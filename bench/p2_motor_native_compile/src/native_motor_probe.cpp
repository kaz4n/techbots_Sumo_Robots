// Retains real native MotorGate setup, transaction and cleanup code for compilation.
// No caller invokes this probe in the sketch, including during global startup.
// Host startup tests and MCU ELF inspection verify that distinction.
#include "native_motor_probe.h"

namespace native_motor_probe {
__attribute__((noinline, used)) Result exercise(
    std::uint32_t now, const fsm::RobotResult& command) {
    Result result;
    result.began = gate.begin();
    result.applied = gate.apply(now, command);
    result.reset = gate.reset();
    return result;
}
} // namespace native_motor_probe
