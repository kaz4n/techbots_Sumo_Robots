// Defines the fixed startup-only ADC timing record for passive P0 readout.
// Keeps raw API returns and first-use cost separate from production timing claims.
// Independently tested against D-063; target layout is checked before capture.
#pragma once
#include "config.h"
#include <cstdint>

namespace p0 {
struct AdcSample {
    std::uint32_t overhead_us;
    std::uint32_t elapsed_us;
    std::int32_t value;
};
struct AdcCapture {
    std::uint32_t version;
    std::uint32_t complete;
    std::uint32_t completed;
    std::uint32_t start_us;
    std::uint32_t end_us;
    AdcSample samples[config::P0_ADC_SAMPLES];
};
static_assert(sizeof(AdcSample) == 12, "ADC sample layout changed");
static_assert(sizeof(AdcCapture) == 12020, "ADC capture layout changed");
} // namespace p0

extern volatile p0::AdcCapture p0Adc;
