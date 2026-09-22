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

class Controller {
public:
    // Update Buttons before Gate on every tick, including while inhibited
    // (D-018). D-019 anchors the full hold at completed release qualification,
    // with no backdating after a delayed tick. Returns Gate's one-step pulses.
    // External qualified STOP is immediate and latched until reset; ADC and B13
    // both-held timing/recovery remain separate. This never writes motors/duty.
    Result step(const core::Inputs& inputs, bool stop_requested = false);
    void reset();
private:
    Buttons buttons_;
    Gate gate_;
};
} // namespace countdown
