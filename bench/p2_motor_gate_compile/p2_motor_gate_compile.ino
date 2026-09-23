// Retains production MotorGate methods for target compilation without execution.
// Checks the MCU ABI while no real pin adapter or physical acceptance exists.
// Board-side compile-only and a separate source/symbol audit validate this probe.
#include "src/config.h"
#pragma push_macro("EMPTY")
#ifdef EMPTY
#undef EMPTY
#endif
#include "src/hal/motors.h"
#pragma pop_macro("EMPTY")

// Null callbacks are deliberately unusable; no successful fake backend exists.
motors::MotorGate p2_motor_gate{motors::Port{}};
using GateProbe = motors::Result (*)(std::uint32_t, const fsm::RobotResult&);
volatile GateProbe p2_motor_gate_probe = nullptr;

__attribute__((noinline, used)) motors::Result motorGateProbe(
    std::uint32_t now, const fsm::RobotResult& command) {
    p2_motor_gate.begin();
    const auto result = p2_motor_gate.apply(now, command);
    p2_motor_gate.reset();
    return result;
}

void setup() {
    // Never invoke the probe or a motor method. Tooling rejects this sketch's upload.
    p2_motor_gate_probe = &motorGateProbe;
}

void loop() {}
