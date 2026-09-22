// Defines the B5.1 polarity correction and hysteresis stage.
// Makes raw digital input filtering testable before higher fusion policies exist.
// Host tests cover each bit, consecutive samples, clear intervals and wraparound.
#pragma once
#include <cstdint>

namespace opp_fusion {
class Debouncer {
public:
    // One newly sampled raw electrical seven-bit mask per call/tick.
    // Assertion counts detected samples; deassertion measures elapsed clear time.
    // The first clear sample starts that interval; high unused bits are ignored.
    std::uint8_t step(std::uint32_t t_us, std::uint8_t raw_mask);
    void reset();
private:
    std::uint32_t detected_ticks_[7] = {};
    std::uint32_t clear_since_us_[7] = {};
    std::uint8_t clearing_mask_ = 0;
    std::uint8_t confirmed_mask_ = 0;
};
} // namespace opp_fusion
