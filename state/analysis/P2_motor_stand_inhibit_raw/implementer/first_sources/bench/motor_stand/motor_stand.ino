// Prepares a one-shot motor setup and inhibition diagnostic with permission false.
// Keeps every native motor and clock callback inactive in the ordinary sketch.
// Independent default-wrapper tests and target startup inspection check passivity.
#include "src/config.h"
#include "src/motor_stand_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Motor inhibition bench requires inert flags");
namespace {
motor_stand::Native native;
motor_stand::Runner runner(native.port());
}
void setup() { runner.begin(motor_stand::Grants{}); }
void loop() { runner.poll(); }
