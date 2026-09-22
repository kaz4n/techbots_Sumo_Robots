// Classifies completed RC observations into B4.1 confirmed white levels.
// Keeps each corner independent and preserves white until a black observation.
// Locked host tests cover thresholds, confirmation, channel order and reset.
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
} // namespace edge
