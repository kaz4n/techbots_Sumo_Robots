// Defines the standalone B3 release-to-GO permission timer.
// Separates a testable logical interlock from ADC decoding and hardware MotorGate.
// Locked host tests cover release debounce, boot-held START, hold and wraparound.
#pragma once
#include "types.h"

namespace countdown {
enum class Phase : std::uint8_t { IDLE, HOLDING, READY, STOPPED };
struct Result {
    Phase phase = Phase::IDLE;
    bool motion_permitted = false;
    bool start_release = false; // One step pulse at the debounced release.
    bool go = false; // One step pulse at the end of the full hold.
    std::uint32_t release_us = 0;
};
class Gate {
public:
    // Call once per tick, including inhibited states; no clock or I/O is read here.
    // First sample establishes the boot level. Boot-held START is not a press.
    // Only a debounced NONE -> START -> NONE sequence starts a countdown.
    // MODE (including BOTH) cancels a hold when debounced. A stop request is
    // immediate and latched until reset; its B13 button decoder is not implemented.
    Result step(std::uint32_t t_us, core::ButtonLevel level,
                bool stop_requested = false);
    void reset();
private:
    void updateButton(std::uint32_t t_us, core::ButtonLevel level);
    void onButtonChange(std::uint32_t t_us);
    Phase phase_ = Phase::IDLE;
    core::ButtonLevel candidate_ = core::ButtonLevel::NONE;
    core::ButtonLevel stable_ = core::ButtonLevel::NONE;
    std::uint32_t candidate_since_us_ = 0;
    std::uint32_t release_us_ = 0;
    bool initialized_ = false;
    bool armed_ = false;
    bool pressed_ = false;
    bool released_this_step_ = false;
};
} // namespace countdown
