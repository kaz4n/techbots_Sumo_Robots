// Defines the frozen internal LED GPIO timing record for passive P0 readout.
// Preserves raw costs and readbacks without claiming recovered native error codes.
// Independent D-064 tests and final target layout checks verify this contract.
#pragma once
#include "config.h"
#include <cstdint>

namespace p0 {
struct GpioSample {
    std::uint32_t overhead_us;
    std::uint32_t pin_mode_us;
    std::uint32_t write_high_us;
    std::uint32_t read_low_us;
    std::uint32_t read_high_us;
    std::uint32_t pair_us;
    std::int32_t low_level;
    std::int32_t high_level;
    std::int32_t pair_level;
};
struct GpioCapture {
    std::uint32_t version;
    std::uint32_t ready;
    std::uint32_t complete;
    std::uint32_t completed;
    std::uint32_t start_us;
    std::uint32_t end_us;
    std::int32_t final_level;
    GpioSample samples[config::P0_GPIO_SAMPLES];
};
bool gpioReady();
static_assert(sizeof(GpioSample) == 36, "GPIO sample layout changed");
static_assert(sizeof(GpioCapture) == 14428, "GPIO capture layout changed");
} // namespace p0

extern volatile p0::GpioCapture p0Gpio;
