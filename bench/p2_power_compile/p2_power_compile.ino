// Retains the concrete native battery reader without calling its methods.
// The probe is compile-only and remains outside every upload allowlist.
// Independent startup tests and final target ELF checks verify no native I/O.
#include "src/config.h"
#include "src/power_probe.h"

namespace power_probe {
power::Reader reader;
Probe volatile entry = nullptr;
} // namespace power_probe

void setup() {
    power_probe::entry = &power_probe::exercise;
}

void loop() {}
