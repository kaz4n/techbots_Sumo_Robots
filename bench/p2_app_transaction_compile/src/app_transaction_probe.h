// Declares a retained transaction exercise which the sketch never invokes.
// Exposes the real lifecycle for compilation without claiming sensor acquisition.
// Host startup and exact target-symbol checks validate this probe ABI.
#pragma once
#pragma push_macro("EMPTY")
#undef EMPTY
#include "app/transaction.h"
#include "hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")
namespace app_transaction_probe {
enum class Action : std::uint8_t { INITIALIZE, OPEN, DECIDE, FINISH, ABORT };
using Probe = bool (*)(Action, fsm::RobotInput);
extern Probe volatile entry;
bool exercise(Action action, fsm::RobotInput input);
} // namespace app_transaction_probe
