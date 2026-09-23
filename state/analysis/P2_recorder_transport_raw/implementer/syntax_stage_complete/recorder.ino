// Prepares a full synthetic recording and optional native inhibited-IDLE dump.
// Keeps every native grant disabled and uses only inert motor callbacks.
// D116 host, target and independent review qualify software; no upload is allowed.
#include "src/config.h"
#include "src/recorder_transport.h"
#include <Arduino.h>

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Recorder bench must remain inert");
namespace {
std::uint32_t clockUs(void*) { return micros(); }
recorder::dump::UnoQDumpPort native_dump;
recorder_transport::Runner runner({nullptr, clockUs}, app::unoQDumpPort(native_dump));
}
void setup() { runner.begin(false, {}); }
void loop() { runner.poll(); }
