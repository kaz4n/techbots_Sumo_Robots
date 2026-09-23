// Retains the native two-channel reader without acquiring either input.
// This compile-only probe remains outside every upload allowlist.
// Independent startup tests and target ELF checks verify no native I/O.
#include "src/config.h"
#include "src/adc_pair_probe.h"

namespace adc_pair_probe {
power::Reader reader;
Probe volatile entry = nullptr;
} // namespace adc_pair_probe

void setup() {
    adc_pair_probe::entry = &adc_pair_probe::exercise;
}

void loop() {}
