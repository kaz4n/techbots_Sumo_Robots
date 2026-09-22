// Defines the B4.1 classification of completed four-channel RC observations.
// Keeps the unresolved acquisition timing and escape policy outside this module.
// Locked host tests cover exact thresholds, mask order and independent channels.
#pragma once
#include <cstdint>

namespace edge {
class Classifier {
public:
    // Each call represents one NEW complete observation. Repeated/stale samples
    // must not be passed as fresh. This API does not implement or validate a HAL.
    // Returns confirmed white levels (not rising edges), so white persists.
    std::uint8_t observe(const std::uint32_t (&raw_us)[4]);
    void reset();
private:
    std::uint32_t consecutive_[4] = {};
};
} // namespace edge
