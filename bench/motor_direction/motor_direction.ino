// Runs the D120 finite B4 profile through real acquisition and MotorGate.
// Keeps every unconfirmed setup grant absent and electrical outputs inhibited.
// Dedicated host M0/M1 scenarios and checked compile-only target builds verify it.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

static_assert(SUMOX_B4_STAND == 1 && MATCH == 0 && MOTORS_ALLOWED == 0,
              "Directional bench requires its compiler-wide inert B4 profile");

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};
}

void setup() { runtime.begin(app::SetupGrants{}); }
void loop() { runtime.step(); }
