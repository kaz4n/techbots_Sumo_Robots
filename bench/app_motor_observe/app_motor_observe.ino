// Prepares a default-disabled longer observation of the inhibited application.
// Keeps peripheral grants absent and preserves explicit native output ownership.
// Independent D192 sketch checks verify wiring and inert-only admission.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#include "src/app_motor_observe.h"
#pragma pop_macro("EMPTY")

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
recorder::dump::UnoQDumpPort dump_port{recorder::dump::Buffering::FIFO8};
app_motor_observe::Runner diagnostic{motor_port.port(), sources.adcPort(), sources.port(),
    app::unoQDumpPort(dump_port)};
}

void setup() {
    diagnostic.begin(motor_fault::Grants{SUMOX_MOTOR_FAULT_PROBE == 1});
}

void loop() {
    if (diagnostic.active()) diagnostic.poll();
}
