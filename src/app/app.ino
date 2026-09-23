// Runs the fixed native acquisition, decision, MotorGate and recorder pipeline.
// Keeps unconfirmed setup grants absent and all physical acceptance explicit.
// D096 actual runtime tests and compile-only target checks verify this entry.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};
}

void setup() {
    // Physical grants are intentionally unconfirmed, never inferred from a build.
    runtime.begin(app::SetupGrants{});
}

void loop() {
    runtime.step();
}
