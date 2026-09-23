// Declares an inert retention probe for the actual native battery reader.
// Compiler evidence is separate from permission to acquire a physical sample.
// Independent startup counters and target ELF inspection check this boundary.
#pragma once
#include "hal/power.h"

namespace power_probe {
struct Result {
    power::InitResult init;
    power::Sample sample;
};
using Probe = Result (*)();
extern power::Reader reader;
extern Probe volatile entry;
Result exercise();
} // namespace power_probe
