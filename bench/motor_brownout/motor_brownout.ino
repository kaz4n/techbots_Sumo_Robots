// Binds the D244 B7 profile to the actual app Runtime with every setup grant absent.
// Keeps this source wrapper motor-inhibited and separate from qualified bench runs.
// Independent wrapper and Runtime fixtures check the fixed profile and empty grants.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

static_assert(SUMOX_B7_BROWNOUT == 1 && MATCH == 0 && MOTORS_ALLOWED == 0,
              "Brownout wrapper requires the compiler-wide B7 profile and motor inhibition");
namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
recorder::dump::UnoQDumpPort dump_port{recorder::dump::Buffering::FIFO8};
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port(),
    app::unoQDumpPort(dump_port)};
}
void setup() { runtime.begin(app::SetupGrants{}); }
void loop() { runtime.step(); }
