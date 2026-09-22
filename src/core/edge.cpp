// Classifies B4.1 white levels and applies the D-020 persistent edge guard.
// Prevents all-white motion guesses while preserving the countdown's precedence.
// Locked host tests cover masks, confirmation, fault latching and reset.
#include "edge.h"
#include "../config.h"

namespace edge {
std::uint8_t Classifier::observe(const std::uint32_t (&raw_us)[4]) {
    std::uint8_t white_mask = 0U;
    for (std::uint32_t i = 0U; i < 4U; ++i) {
        if (raw_us[i] >= config::QTR_WHITE_US[i]) {
            consecutive_[i] = 0U;
            continue;
        }
        // Saturation lets a continuously white corner remain confirmed forever.
        if (consecutive_[i] < config::QTR_CONFIRM_TICKS) {
            ++consecutive_[i];
        }
        if (consecutive_[i] >= config::QTR_CONFIRM_TICKS) {
            white_mask |= static_cast<std::uint8_t>(1U << i);
        }
    }
    return white_mask;
}

void Classifier::reset() {
    for (auto& count : consecutive_) {
        count = 0U;
    }
}

GuardResult Guard::step(std::uint8_t line_mask, bool motion_permitted,
                        bool script_finished) {
    static_assert(config::EDGE_PUSH_THROUGH_MS == 0U,
                  "Implement and test bounded push-through before enabling it");
    if (!motion_permitted) {
        return {false, fault_latched_, true};
    }
    const std::uint8_t white = line_mask & 0x0FU;
    if (white == 0x0FU) {
        fault_latched_ = true;
    }
    if (fault_latched_) {
        escaping_ = true;
        return {true, true, true};
    }
    if (white != 0U) {
        escaping_ = true;
    } else if (script_finished) {
        escaping_ = false;
    }
    return {escaping_, false, false};
}

void Guard::reset() {
    *this = Guard{};
}
} // namespace edge
