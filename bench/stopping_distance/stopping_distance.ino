// Runs one D126 stopping trial through real acquisition, Runtime and MotorGate.
// Leaves every unconfirmed setup grant absent and electrical outputs inhibited.
// Independent M0/M1 profile tests and checked compile-only builds verify the route.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

static_assert(SUMOX_P3_STOP_TRIAL == 1 && MATCH == 0 && MOTORS_ALLOWED == 0 &&
              SUMOX_P3_DRIVE_TEST == 0 && SUMOX_P3_TURN_TRIAL == 0 && SUMOX_B4_STAND == 0,
              "Stopping distance requires its exclusive compiler-wide inert P3 profile");

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};
}

void setup() { runtime.begin(app::SetupGrants{}); }
void loop() { runtime.step(); }
