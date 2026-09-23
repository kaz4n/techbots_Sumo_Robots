// Returns the existing UNO Q port unchanged for its single MotorGate owner.
// Preserves native context, callbacks and periods without touching hardware.
// Independent binding tests and exact target inspection check this forwarding.
#include "motor_stand_native.h"

namespace motor_stand {
motors::Port Native::port() { return native_.port(); }
} // namespace motor_stand
