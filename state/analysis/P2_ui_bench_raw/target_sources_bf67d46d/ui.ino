// Captures finite A1 raw and decoder evidence only under explicit ADC ownership.
// Ships disabled with no motor, transport, matrix or unrelated sensor owner.
// Independent default-sketch tests and checked target audits verify the inert boundary.
#include "src/config.h"
#include "src/ui_bench_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "UI evidence bench requires inert flags");
namespace {
ui_bench::Native native;
ui_bench::Runner runner(native.port());
}
void setup() { runner.begin(ui_bench::Grants{}); }
void loop() { runner.poll(); }
