// Captures finite unchanged battery evidence when ADC ownership is explicitly granted.
// Ships disabled and constructs no motor, transport, button or unrelated sensor owner.
// Independent default-sketch tests and exact checked target audits verify this boundary.
#include "src/config.h"
#include "src/vbat_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Battery bench requires inert flags");
namespace {
vbat::Native native;
vbat::Runner runner(native.port());
}
void setup() { runner.begin(vbat::Grants{}); }
void loop() { runner.poll(); }
