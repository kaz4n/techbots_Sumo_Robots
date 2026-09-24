// Runs D129 timing evidence through actual acquisition, Runtime and MotorGate.
// Keeps the P4 trace observational and every unconfirmed setup grant absent.
// Independent profile tests and checked inert compile-only builds verify this route.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

static_assert(SUMOX_TIMING_EVIDENCE == 1 && MATCH == 0 && MOTORS_ALLOWED == 0 &&
              SUMOX_P4_REACTIVE == 1 && SUMOX_B4_STAND == 0 &&
              SUMOX_P3_DRIVE_TEST == 0 && SUMOX_P3_TURN_TRIAL == 0 &&
              SUMOX_P3_STOP_TRIAL == 0,
              "Reactive timing requires its exclusive compiler-wide inert P4 profile");

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};
}

void setup() { runtime.begin(app::SetupGrants{}); }
void loop() { runtime.step(); }
