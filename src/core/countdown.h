// Defines B3 button qualification, hold timer and their approved composition.
// Separates a testable logical interlock from ADC decoding and hardware MotorGate.
// Locked host tests cover qualified events, debounce, boot-held START and wraparound.
#pragma once
#include "types.h"

namespace countdown {
enum class Phase : std::uint8_t { IDLE, HOLDING, READY, STOPPED };
struct Commands {
    bool start_release = false; // Qualified logical event, not a raw button level.
    bool mode_press = false;
    bool stop_requested = false;
};
struct Result {
    Phase phase = Phase::IDLE;
    bool motion_permitted = false;
    bool start_release = false; // One step pulse at the debounced release.
    bool go = false; // One step pulse at the end of the full hold.
    std::uint32_t release_us = 0;
};
class Gate {
public:
    // An accepted release starts the hold at the supplied event time t_us.
    // Caller supplies qualified commands. Controller uses D-019's completed
    // release-qualification tick; direct Gate users must supply that event time.
    // STOP is latched until reset. MODE cancels a hold; neither can grant motion.
    Result step(std::uint32_t t_us, Commands commands = {});
    void reset();
private:
    Phase phase_ = Phase::IDLE;
    std::uint32_t release_us_ = 0;
};
struct ButtonEvents {
    bool start_release = false;
    bool mode_press = false;
    std::uint32_t edge_us = 0; // First sample of the now-qualified transition.
    std::uint32_t qualified_us = 0;
};
class Buttons {
public:
    // Qualifies stable logical levels for BTN_DEBOUNCE_MS. The first sample
    // establishes the boot level; a boot-held START is not a valid press.
    // A qualified NONE -> START -> NONE sequence emits one start-release pulse.
    // Both timestamps are exposed; Controller anchors Gate at qualified_us (D-019).
    // MODE includes BOTH. B13 both-held STOP and ADC decoding remain separate.
    ButtonEvents step(std::uint32_t t_us, core::ButtonLevel level);
    void reset();
private:
    core::ButtonLevel candidate_ = core::ButtonLevel::NONE;
    core::ButtonLevel stable_ = core::ButtonLevel::NONE;
    std::uint32_t candidate_since_us_ = 0;
    bool initialized_ = false;
    bool armed_ = false;
    bool pressed_ = false;
};

class StopHold {
public:
    // D-035: an observed logical BOTH begins debounce, including if held at boot.
    // Once BTN_DEBOUNCE_MS has elapsed, start the full BTN_LONG_MS at that call;
    // never backdate a delayed qualification. A non-BOTH observation cancels any
    // pending stage, including a release on its deadline. After a true result,
    // retain true regardless of releases/other inputs until reset.
    // Invalid button enums count as non-BOTH, never as an assumed press.
    // Successive calls must be <one uint32 micros wrap. No clock or hardware I/O.
    bool step(std::uint32_t t_us, core::ButtonLevel level);
    void reset();
private:
    enum class Stage : std::uint8_t { IDLE, DEBOUNCE, HOLDING, STOPPED };
    Stage stage_ = Stage::IDLE;
    std::uint32_t last_us_ = 0;
    std::uint32_t age_us_ = 0;
};

class Controller {
public:
    // Update Buttons before Gate on every tick, including while inhibited
    // (D-018). D-019 anchors the full hold at completed release qualification,
    // with no backdating after a delayed tick. Returns Gate's one-step pulses.
    // D-035 logical StopHold updates each call; it ORs with an external qualified
    // immediate STOP before Gate. STOP remains latched until reset; physical ADC
    // decoding is separate. This never writes motors/duty. Reset clears all three
    // components; START held at reset is still ignored until a new press/release.
    Result step(const core::Inputs& inputs, bool stop_requested = false);
    void reset();
private:
    StopHold stop_;
    Buttons buttons_;
    Gate gate_;
};

struct ServiceSample {
    std::uint32_t t_us = 0;
    float raw_gyro_z_dps = 0.0F; // Before bias subtraction; one new logical reading/tick.
    bool imu_ok = false;
    std::uint8_t line_mask = 0;
    std::uint8_t confirmed_opp_mask = 0;
};
struct ServiceResult {
    float bias_dps = 0.0F;
    std::uint32_t calibration_samples = 0;
    bool calibration_finished = false;
    bool calibration_rejected = false;
    bool line_warning = false;
    std::uint8_t opponent_snapshot = 0;
    bool active = false;
    bool finished = false;
};

class Services {
public:
    // Caller starts at Controller's qualified release tick (D-019); previous
    // bias must be finite. Invalid start returns false, idle with rejection flag.
    // A successful start clears the prior attempt's flags/snapshot/sample state.
    bool start(std::uint32_t release_us, float previous_bias_dps);
    // D-024: samples in [CAL_START_MS,CAL_END_MS), raw finite gyro with imu_ok;
    // any invalid window sample rejects. At CAL_END_MS or the next call, finish
    // once: accept mean iff sample count>=CAL_MIN_SAMPLES and max-min<=spread.
    // Invalid/too-few/high-spread keeps prior bias. A duplicate timestamp adds
    // no observation. Caller must supply new samples; this does not prove HAL
    // freshness. Gaps do not fabricate readings; consecutive calls <uint32 wrap.
    // Final warning/snapshot windows are [hold-window,hold), excluding GO.
    // Warning latches; snapshot takes latest low seven bits (including zero).
    // At/after hold, freeze results, active=false/finished=true. No motor gate.
    ServiceResult step(const ServiceSample& sample);
    // Cancel clears attempt state but preserves its current bias; reset clears
    // all state to defaults. Neither enables motors or changes Controller.
    void cancel();
    void reset();
private:
    void finishCalibration();
    void observeCalibration(const ServiceSample& sample);
    ServiceResult result_;
    std::uint32_t last_us_ = 0;
    std::uint64_t elapsed_us_ = 0;
    double sum_dps_ = 0.0;
    double minimum_dps_ = 0.0;
    double maximum_dps_ = 0.0;
    bool invalid_sample_ = false;
};

struct LifecycleResult {
    Result gate;
    ServiceResult services;
    bool service_start_failed = false; // Diagnostic, never a new motion policy.
    bool heading_reset_requested = false; // Exactly the Controller GO pulse.
};
class Lifecycle {
public:
    // D-018/D-019/D-024/D-035 production composition: update Controller first.
    // On accepted release, start Services at gate.release_us with this call's
    // previous bias only. ServiceSample is the single time/raw-observation source;
    // use gyro before bias subtraction and genuinely new confirmed sensor data.
    // IDLE/STOPPED cancels a pending attempt BEFORE its sample is processed.
    // Cancellation clears attempt diagnostics, retaining Services' current bias.
    // Step Services, then return; Controller alone controls GO/permission. A
    // service start failure remains explicit until cancellation, restart or reset;
    // do not reinterpret it as accepted calibration or infer a new motor veto.
    // At GO the attempt stops being pending; keep completed service evidence on
    // later STOP. This diagnostic lifetime never overrides latched STOP inhibition.
    // New accepted release replaces prior service evidence. Previous bias values
    // on all other ticks are ignored. heading_reset_requested is one GO pulse,
    // not a board reset. Caller applies bias/heading change through HAL/app.
    // Existing Gate timing is authoritative even for sparse wrapped call streams;
    // finished services alone cannot authorize motion. No clock, I/O or allocation.
    LifecycleResult step(const ServiceSample& sample, core::ButtonLevel button,
                         float previous_bias_dps, bool stop_requested = false);
    void reset();
private:
    Controller controller_;
    Services services_;
    bool pending_ = false;
    bool service_start_failed_ = false;
};
} // namespace countdown
