// Applies B5.1 polarity correction and independent per-sensor hysteresis.
// Rejects brief detections and clear flicker before later opponent fusion.
// Host tests cover seven channels, interval boundaries, wraparound and reset.
#include "opp_fusion.h"
#include "../config.h"

namespace opp_fusion {
FrontView frontView(std::uint8_t confirmed_mask) {
    switch (confirmed_mask & 0x07U) {
    case 0x01U: return {true, false, false, -15.0F};
    case 0x02U: return {true, true, false, 0.0F};
    case 0x03U: return {true, true, false, -6.0F};
    case 0x04U: return {true, false, false, 15.0F};
    case 0x05U: return {true, true, true, 0.0F};
    case 0x06U: return {true, true, false, 6.0F};
    case 0x07U: return {true, true, true, 0.0F};
    default: return {};
    }
}

std::uint8_t Debouncer::step(std::uint32_t t_us, std::uint8_t raw_mask) {
    const auto detected_mask = static_cast<std::uint8_t>(
        (raw_mask ^ config::OPP_ACTIVE_LOW_MASK) & 0x7FU);
    for (std::uint32_t i = 0U; i < 7U; ++i) {
        const auto bit = static_cast<std::uint8_t>(1U << i);
        const auto other_bits = static_cast<std::uint8_t>(~bit);
        if ((detected_mask & bit) != 0U) {
            if (detected_ticks_[i] < config::OPP_SET_TICKS) {
                ++detected_ticks_[i];
            }
            if (detected_ticks_[i] >= config::OPP_SET_TICKS) {
                confirmed_mask_ |= bit;
            }
            clearing_mask_ &= other_bits;
            continue;
        }
        detected_ticks_[i] = 0U;
        // A separate active bit keeps timestamp zero valid, including at wrap.
        if ((clearing_mask_ & bit) == 0U) {
            clear_since_us_[i] = t_us;
            clearing_mask_ |= bit;
        }
        const std::uint32_t clear_elapsed_us = t_us - clear_since_us_[i];
        if (clear_elapsed_us >= config::OPP_CLEAR_MS * 1000U) {
            confirmed_mask_ &= other_bits;
        }
    }
    return confirmed_mask_;
}

void Debouncer::reset() {
    for (std::uint32_t i = 0U; i < 7U; ++i) {
        detected_ticks_[i] = 0U;
        clear_since_us_[i] = 0U;
    }
    clearing_mask_ = 0U;
    confirmed_mask_ = 0U;
}
} // namespace opp_fusion
