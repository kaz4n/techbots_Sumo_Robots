// Retains the concrete native motor backend without executing its callbacks.
// Both compile configurations remain outside the upload allowlist.
// Independent startup tests and final target ELF checks verify no user pin I/O.
#include "src/config.h"
#include "src/native_motor_probe.h"

namespace native_motor_probe {
motors::UnoQPort native;
motors::MotorGate gate{native.port()};
Probe volatile address = nullptr;
} // namespace native_motor_probe

void setup() {
    native_motor_probe::address = &native_motor_probe::exercise;
}

void loop() {}
