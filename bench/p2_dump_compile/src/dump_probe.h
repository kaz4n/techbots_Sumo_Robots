// Declares an inert retained integration path through actual D090 production APIs.
// Avoids Arduino EMPTY macro collisions while preserving its previous definition.
// Host pipelines and target ELF checks exercise separate evidence boundaries.
#pragma once
#pragma push_macro("EMPTY")
#undef EMPTY
#include "hal/dump_uart_unoq.h"
#include "hal/motors.h"
#pragma pop_macro("EMPTY")
namespace dump_probe {
struct Result {
    recorder::dump::NativeStatus native;
    recorder::dump::Report transfer;
    fsm::RobotResult robot;
};
using Probe = Result (*)(fsm::RobotInput, const recorder::dump::SetupGrant&, bool);
extern Probe volatile entry;
Result exercise(fsm::RobotInput, const recorder::dump::SetupGrant&, bool);
}
