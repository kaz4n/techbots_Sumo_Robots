// Prepares a full synthetic recording and optional native inhibited-IDLE dump.
// Keeps every native grant disabled and uses only inert motor callbacks.
// D116 and session tests qualify software; native run admission remains separate.
#include "src/config.h"
#include "src/recorder_transport.h"
#include "src/recorder_run_identity.h"
#include <Arduino.h>

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Recorder bench must remain inert");
namespace {
std::uint32_t clockUs(void*) { return micros(); }
recorder::dump::UnoQDumpPort native_dump{recorder::dump::Buffering::FIFO8};
recorder_transport::Runner runner({nullptr, clockUs}, app::unoQDumpPort(native_dump));
}
void setup() { runner.begin(recorder_run_identity::ENABLED, recorder_run_identity::GRANTS); }
void loop() { runner.poll(); }
