// Declares an inert retention probe for the native adapter and actual MotorGate.
// Keeps compiler compatibility evidence separate from authorization to operate pins.
// Independent startup counters and target ELF inspection check this boundary.
#pragma once
#pragma push_macro("EMPTY")
#ifdef EMPTY
#undef EMPTY
#endif
#include "hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")

namespace native_motor_probe {
struct Result {
    bool began;
    motors::Result applied;
    bool reset;
};
using Probe = Result (*)(std::uint32_t, const fsm::RobotResult&);
extern motors::UnoQPort native;
extern motors::MotorGate gate;
extern Probe volatile address;
Result exercise(std::uint32_t now, const fsm::RobotResult& command);
} // namespace native_motor_probe
