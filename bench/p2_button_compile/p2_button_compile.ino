// Retains the complete button software path without reading or acting on inputs.
// This compile-only probe remains outside every upload allowlist.
// Independent startup tests and target ELF checks verify no native I/O.
#include "src/config.h"
#include "src/button_probe.h"

namespace button_probe {
power::Reader reader;
fsm::Robot controller;
Probe volatile entry = nullptr;
} // namespace button_probe

void setup() {
    button_probe::entry = &button_probe::exercise;
}

void loop() {}
