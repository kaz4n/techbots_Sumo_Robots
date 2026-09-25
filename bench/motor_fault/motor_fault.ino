// Prepares a default-disabled trace of four zero-output MotorGate applications.
// Keeps native pad ownership behind an explicit separately reviewed run grant.
// Independent default-sketch checks and inert-only builds verify this entry.
#include <Arduino.h>
#include "src/motor_fault.h"
#include "src/hal/motor_port_unoq.h"

namespace {
motors::UnoQPort native;
motor_fault::Runner diagnostic(native.port());
}
void setup() { diagnostic.begin(motor_fault::Grants{}); }
void loop() { if (diagnostic.active()) diagnostic.poll(static_cast<std::uint32_t>(micros())); }
