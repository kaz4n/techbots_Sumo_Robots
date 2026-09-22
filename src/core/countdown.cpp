// Implements B3 logical button qualification and the separate release hold timer.
// Keeps raw-release anchoring, integrated arbitration and all hardware writes out.
// Verified by independent locked host boundary, wraparound and seeded stream tests.
#include "countdown.h"
#include "../config.h"

namespace countdown {
Result Gate::step(std::uint32_t t_us, Commands commands) {
    Result result;
    if (commands.stop_requested) {
        phase_ = Phase::STOPPED;
    } else if (phase_ == Phase::HOLDING && commands.mode_press) {
        phase_ = Phase::IDLE;
    } else if (phase_ == Phase::IDLE && commands.start_release &&
               !commands.mode_press) {
        release_us_ = t_us;
        phase_ = Phase::HOLDING;
        result.start_release = true;
    }
    const std::uint32_t hold_us =
        (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
    if (phase_ == Phase::HOLDING && t_us - release_us_ >= hold_us) {
        phase_ = Phase::READY;
        result.go = true;
    }
    result.phase = phase_;
    result.release_us = release_us_;
    result.motion_permitted = phase_ == Phase::READY;
    return result;
}

void Gate::reset() {
    *this = Gate{};
}

ButtonEvents Buttons::step(std::uint32_t t_us, core::ButtonLevel level) {
    ButtonEvents result;
    if (!initialized_) {
        initialized_ = true;
        candidate_ = stable_ = level;
        candidate_since_us_ = t_us;
        armed_ = level == core::ButtonLevel::NONE;
        return result;
    }
    if (level != candidate_) {
        candidate_ = level;
        candidate_since_us_ = t_us;
    }
    if (candidate_ == stable_ ||
        t_us - candidate_since_us_ < config::BTN_DEBOUNCE_MS * 1000U) {
        return result;
    }
    const bool was_mode = stable_ == core::ButtonLevel::MODE ||
                          stable_ == core::ButtonLevel::BOTH;
    stable_ = candidate_;
    result.edge_us = candidate_since_us_;
    result.qualified_us = t_us;
    if (stable_ == core::ButtonLevel::NONE) {
        result.start_release = pressed_;
        pressed_ = false;
        armed_ = true;
    } else if (stable_ == core::ButtonLevel::START) {
        pressed_ = armed_;
        armed_ = false;
    } else {
        result.mode_press = !was_mode;
        pressed_ = false;
        armed_ = false;
    }
    return result;
}

void Buttons::reset() {
    *this = Buttons{};
}
} // namespace countdown
