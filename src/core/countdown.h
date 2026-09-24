// Defines B3 button qualification, hold timer and their approved composition.
// Separates a testable logical interlock from ADC decoding and hardware MotorGate.
// Locked host tests cover qualified events, debounce, boot-held START and wraparound.
#pragma once
#include "types.h"
#include "../config.h"

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
// D087 admission result: source time advances gestures only on distinct samples.
// restart discards pending qualification, never Gate STOP or menu selection.
struct ButtonTiming {
    std::uint32_t observation_us = 0U;
    bool fresh = false;
    bool restart = false;
    bool start_ready = false; // Fresh NONE has spanned debounce after boot/restart.
};
class Buttons {
public:
    // Qualifies stable logical levels for BTN_DEBOUNCE_MS. The first sample
    // establishes the boot level; a boot-held START is not a valid press.
    // A qualified NONE -> START -> NONE sequence emits one start-release pulse.
    // Both timestamps are exposed; Controller anchors Gate at qualified_us (D-019).
    // MODE includes BOTH. B13 both-held STOP and ADC decoding remain separate.
    ButtonEvents step(std::uint32_t t_us, core::ButtonLevel level);
    ButtonEvents stepObserved(std::uint32_t decision_us, std::uint32_t source_us,
                              core::ButtonLevel level);
    // D138 observation only: actual qualified NONE can arm the next START.
    bool neutralStartArmed() const;
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
    bool stepObserved(std::uint32_t decision_us, std::uint32_t source_us,
                      core::ButtonLevel level);
    void interrupt(); // Discards an unfinished hold, preserves latched STOP.
    void reset();
private:
    enum class Stage : std::uint8_t { IDLE, DEBOUNCE, HOLDING, STOPPED };
    Stage stage_ = Stage::IDLE;
    std::uint32_t last_us_ = 0;
    std::uint32_t age_us_ = 0;
    bool source_before_anchor_ = false;
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
    // D-057: allow_match_start filters ONLY the qualified START release supplied
    // to Gate. Default true preserves existing behavior. False still advances
    // Buttons, StopHold, MODE cancellation and Gate time; it neither cancels an
    // existing countdown nor revokes READY permission. It is routing, not an
    // emergency inhibit. A suppressed release is consumed, never queued/replayed
    // when true returns. To start later requires a new qualified press/release.
    Result step(const core::Inputs& inputs, bool stop_requested = false,
                bool allow_match_start = true);
    Result stepObserved(const core::Inputs& inputs, const ButtonTiming& timing,
                        bool stop_requested = false, bool allow_match_start = true);
    // Snapshot from the most recent step, including a suppressed qualified START
    // release. Read-only/repeated reads do not advance input or grant permission.
    // Result.start_release remains the Gate's ACCEPTED match-release pulse.
    // Before first step/after reset this snapshot is empty. Caller publishes a
    // service action at most once and only if final IDLE/fault/STOP policy allows;
    // the raw snapshot may still contain a pulse on a STOP-priority observation.
    ButtonEvents buttonEvents() const;
    // Forwards Buttons state; does not include Gate phase or grant permission.
    bool neutralStartArmed() const;
    void reset();
private:
    StopHold stop_;
    Buttons buttons_;
    Gate gate_;
    ButtonEvents events_;
    bool logical_stop_ = false;
};

enum class GyroPresence : std::uint8_t { LEGACY, ABSENT, VALID, INVALID };
struct ServiceSample {
    std::uint32_t t_us = 0;
    float raw_gyro_z_dps = 0.0F; // Before bias subtraction; one new logical reading/tick.
    bool imu_ok = false;
    std::uint8_t line_mask = 0;
    std::uint8_t confirmed_opp_mask = 0;
    // D083: append-only compatibility. LEGACY retains imu_ok/tick-time semantics.
    GyroPresence gyro_presence = GyroPresence::LEGACY;
    std::uint32_t gyro_observation_us = 0; // Actual completion, never delivery time.
    std::uint32_t gyro_sequence = 0; // Source identity; zero is valid after wrap.
    bool explicit_line = false;
    bool line_updated = false;
    std::uint32_t line_source_us = 0U; // Both source/delivery must be in warning window.
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
    // D083 explicit mode: ABSENT skips only gyro aggregation; INVALID rejects.
    // VALID ignores imu_ok, requires finite raw gyro, delivery age <= the D082
    // heading gap, forward source time/sequence, and both source and decision
    // inside the calibration window. An identical last observation is ignored;
    // conflicting/reversed identity rejects. Delivery at CAL_END is too late.
    // First in-window call selects legacy/explicit; mixing rejects the attempt.
    // All other services and original hold/STOP/cancellation timing still advance.
    // Full admission details: state/analysis/P2_calibration_presence_contract.md.
    ServiceResult step(const ServiceSample& sample);
    // Cancel clears attempt state but preserves its current bias; reset clears
    // all state to defaults. Neither enables motors or changes Controller.
    void cancel();
    void reset();
private:
    void finishCalibration();
    void observeCalibration(const ServiceSample& sample);
    bool admitGyro(const ServiceSample& sample);
    bool admitExplicitGyro(const ServiceSample& sample);
    ServiceResult result_;
    std::uint32_t last_us_ = 0;
    std::uint64_t elapsed_us_ = 0;
    double sum_dps_ = 0.0;
    double minimum_dps_ = 0.0;
    double maximum_dps_ = 0.0;
    bool invalid_sample_ = false;
    bool gyro_mode_selected_ = false;
    bool explicit_gyro_mode_ = false;
    bool have_gyro_observation_ = false;
    std::uint32_t last_gyro_observation_us_ = 0;
    std::uint32_t last_gyro_sequence_ = 0;
    float last_raw_gyro_dps_ = 0.0F;
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
    // not a board reset. D-059: caller establishes its logical match-yaw origin
    // before same-tick motion; never reset the continuous HAL yaw/Fusion history.
    // Accepted gyro bias affects subsequent integration increments only.
    // Existing Gate timing is authoritative even for sparse wrapped call streams;
    // finished services alone cannot authorize motion. No clock, I/O or allocation.
    // D-057 forwards the same START-only routing selector to Controller. A
    // suppressed release cannot start Services, consume previous_bias_dps or
    // request heading reset. Existing attempts still progress/cancel normally.
    // This additive argument defaults true; it does not implement the menu.
    LifecycleResult step(const ServiceSample& sample, core::ButtonLevel button,
                         float previous_bias_dps, bool stop_requested = false,
                         bool allow_match_start = true);
    LifecycleResult stepObserved(const ServiceSample& sample, core::ButtonLevel button,
        const ButtonTiming& timing, float previous_bias_dps,
        bool stop_requested = false, bool allow_match_start = true);
    // Same last-step snapshot as Controller, without sampling Buttons again.
    ButtonEvents buttonEvents() const;
    bool neutralStartArmed() const;
    void reset();
private:
    Controller controller_;
    Services services_;
    bool pending_ = false;
    bool service_start_failed_ = false;
};
enum class Service : std::uint8_t { NONE, SENSOR_VIEW, QTR_CAL, DRIVE_TEST, LOG_DUMP };
struct MenuSelection {
    core::Mode mode = static_cast<core::Mode>(config::MODE_DEFAULT);
    bool service_menu = false;
    Service service = Service::SENSOR_VIEW;
};
struct MenuSample {
    std::uint32_t t_us = 0;
    core::ButtonLevel button = core::ButtonLevel::NONE;
    core::State state_at_entry = core::State::BOOT;
    bool inhibited_fault = false; // Includes final STOP/fault outcome from this tick.
    bool qualified_start_release = false; // This tick's Controller snapshot only.
};
struct MenuResult {
    MenuSelection selection;
    bool selection_changed = false; // Any mode/item/view change by this step.
    bool menu_toggled = false;
    Service request = Service::NONE; // One-call intent, never actual execution.
    bool request_unavailable = false; // DRIVE_TEST unavailable outside D123 profile.
};
class Menu {
public:
    // D134: match cycling skips disabled ARC/WAIT with at most six probes.
    // MODE_DEFAULT must be available; service order and captured mode are unchanged.
    // B13/D-058: only IDLE-at-entry and no final inhibited fault admit gestures
    // or service requests. Other/invalid states cancel the gesture and retain
    // selection. Caller includes final STOP in inhibited_fault; a countdown MODE
    // cancellation still supplies COUNTDOWN-at-entry, not newly reached IDLE.
    // Boot/reset/contamination require NONE observed for BTN_DEBOUNCE_MS before
    // arming. Exclusive MODE then qualifies for that duration; its actual
    // qualification call starts the hold clock, never a backdated raw edge.
    // A first NONE freezes hold age. After NONE qualifies, age<MODE_SHORT_MS
    // cycles the selected item once; [MODE_SHORT_MS,BTN_LONG_MS] and later ages
    // do nothing. NONE at the exact long deadline wins over a pending toggle.
    // Continuous MODE at age>=BTN_LONG_MS toggles services once; release cannot
    // also cycle. Interrupted release cancels the entire gesture and requires
    // new qualified NONE. Any START/BOTH/invalid button immediately disarms MODE.
    // NONE interrupting an unqualified press also requires fresh NONE arming.
    // Match modes cycle1..6; service items cycle SENSOR_VIEW/QTR_CAL/DRIVE_TEST/
    // LOG_DUMP. Entering services selects SENSOR_VIEW; exiting preserves match
    // mode and the inactive service item. No mode can be injected by a setter.
    //
    // A genuine current qualified_start_release from Controller, with raw NONE,
    // services selected and eligible state, returns the selected request once
    // and cancels any MODE gesture. That observation begins a fresh NONE arming
    // interval before another MODE gesture. It is not accepted match START. DRIVE_TEST
    // sets request_unavailable outside the D123 profile; other requests need a bounded
    // consumer, and false does not certify installed/physical availability.
    // Requests are not queued; no consumer response can enable a match or motor.
    // Caller derives D-057 allow_match_start from ENTRY state/selection, steps
    // Lifecycle once, then steps Menu using its ButtonEvents and final inhibition.
    // Capture running match mode only on the Gate's accepted release, preserving
    // that mode through countdown/moving states. No duplicated Buttons sampling.
    //
    // Immediate duplicate timestamp ignores changed data and returns selection
    // with all pulses/request cleared. Distinct calls must be <one uint32 wrap
    // apart; bounded accumulated ages prevent long holds retriggering after wrap.
    // No duties, clocks, I/O, allocation, Gate mutation or actual service actions.
    MenuResult step(const MenuSample& sample);
    MenuResult stepObserved(const MenuSample& sample, const ButtonTiming& timing);
    MenuSelection selection() const;
    // MODE_DEFAULT/match view/SENSOR_VIEW, no armed gesture or retained request.
    void reset();
private:
    enum class Stage : std::uint8_t { DISARMED, REARM, READY, PRESS, HELD, RELEASE, CONSUMED };
    void advanceAge(std::uint32_t delta_us, std::uint32_t limit_us);
    void disarm();
    void observeMode(std::uint32_t delta_us, MenuResult& result);
    void observeNone(std::uint32_t delta_us, MenuResult& result);
    void cycle(MenuResult& result);
    void toggle(MenuResult& result);
    MenuSelection selection_;
    Stage stage_ = Stage::DISARMED;
    std::uint32_t last_us_ = 0;
    std::uint32_t age_us_ = 0;
    bool observed_ = false;
    bool short_release_ = false;
    std::uint32_t last_source_us_ = 0U;
    std::uint32_t hold_source_us_ = 0U;
    bool source_observed_ = false;
    bool source_before_anchor_ = false;
};
} // namespace countdown
