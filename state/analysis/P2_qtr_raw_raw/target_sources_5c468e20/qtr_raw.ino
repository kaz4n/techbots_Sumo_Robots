// Captures a finite bank of native QTR evidence when ownership is explicitly granted.
// Ships disabled and never constructs a motor, transport or unrelated sensor owner.
// Independent default-sketch tests and exact checked target audits verify the boundary.
#include "src/config.h"
#include "src/qtr_raw_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "QTR raw bench requires inert flags");
namespace {
qtr_raw::Native native;
qtr_raw::Runner runner(native.port());
}
void setup() { runner.begin(qtr_raw::Grants{}); }
void loop() { runner.poll(); }
