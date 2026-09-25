// Prepares a default-disabled trace around the real inhibited application.
// Keeps all peripheral grants absent and native ownership explicitly admitted.
// Independent D186 sketch checks and inert-only builds verify this binding.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#include "src/app_motor_fault.h"
#pragma pop_macro("EMPTY")

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
recorder::dump::UnoQDumpPort dump_port{recorder::dump::Buffering::FIFO8};
app_motor_fault::Runner diagnostic{motor_port.port(), sources.adcPort(), sources.port(),
    app::unoQDumpPort(dump_port)};
}

void setup() {
    diagnostic.begin(motor_fault::Grants{SUMOX_MOTOR_FAULT_PROBE == 1});
}

void loop() {
    if (diagnostic.active()) diagnostic.poll();
}
