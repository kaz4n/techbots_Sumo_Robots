// Runs the D123 first-drive profile through real acquisition and MotorGate.
// Leaves all unconfirmed setup grants absent and electrical outputs inhibited.
// Dedicated host M0/M1 scenarios and checked compile-only builds verify it.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

static_assert(SUMOX_P3_DRIVE_TEST == 1 && MATCH == 0 && MOTORS_ALLOWED == 0,
              "Drive test requires its compiler-wide inert P3 profile");

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};
}

void setup() { runtime.begin(app::SetupGrants{}); }
void loop() { runtime.step(); }
