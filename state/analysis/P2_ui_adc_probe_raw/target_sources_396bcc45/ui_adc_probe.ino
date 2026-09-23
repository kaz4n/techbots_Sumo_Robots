// Observes actual native A1 initialization and raw conversions on a bare UNO Q.
// Reuses the tested finite bench without granting motion or button qualification.
// D114 requires independent wrapper, exact target and readout review before a run.
#include "src/config.h"
#include "src/ui_bench_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Bare ADC diagnostic requires inert flags");
namespace {
ui_bench::Native native;
ui_bench::Runner runner(native.port());
}
void setup() { runner.begin(ui_bench::Grants{true}); }
void loop() { runner.poll(); }
