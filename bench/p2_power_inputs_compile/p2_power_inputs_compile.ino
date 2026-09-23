// Retains the D093 ADC owner and actual Robot/MotorGate/recorder link path.
// Setup only stores a pointer; no backend or sensor/motor operation executes.
// Controlled startup tests and target ELF inspection verify compile-only scope.
#include "src/power_inputs_probe.h"
namespace power_inputs_probe { Probe volatile entry = nullptr; }
void setup() { power_inputs_probe::entry = &power_inputs_probe::exercise; }
void loop() {}
