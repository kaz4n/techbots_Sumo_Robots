// Declares an inert retention probe for the fixed native A0/A1 ADC owner.
// Compile evidence cannot authorize acquisition or resolve button voltages.
// Independent startup counters and target ELF inspection verify this boundary.
#pragma once
#include "hal/power.h"

namespace adc_pair_probe {
struct Result {
    power::InitResult init;
    power::Sample battery_first;
    power::ButtonSample buttons_first;
    power::Sample battery_second;
    power::ButtonSample buttons_second;
};
using Probe = Result (*)();
extern power::Reader reader;
extern Probe volatile entry;
Result exercise();
} // namespace adc_pair_probe
