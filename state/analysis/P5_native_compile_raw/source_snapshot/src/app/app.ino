// Runs the fixed native acquisition, decision, MotorGate, recorder and dump pipeline.
// Keeps unconfirmed setup grants absent and all physical acceptance explicit.
// D096/D101 actual runtime tests and compile-only target checks verify this entry.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
recorder::dump::UnoQDumpPort dump_port{recorder::dump::Buffering::FIFO8};
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port(),
    app::unoQDumpPort(dump_port)};
}

void setup() {
    // Physical grants are intentionally unconfirmed, never inferred from a build.
    runtime.begin(app::SetupGrants{});
}

void loop() {
    runtime.step();
}
