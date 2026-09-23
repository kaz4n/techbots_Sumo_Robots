// Declares the retained D093 integration exercise, never called by the sketch.
// Keeps native acquisition provenance visible across projection and application.
// Host startup substitutes and target symbol inspection verify this probe ABI.
#pragma once
#pragma push_macro("EMPTY")
#undef EMPTY
#include "hal/power_inputs.h"
#include "hal/motor_port_unoq.h"
#include "hal/recorder.h"
#pragma pop_macro("EMPTY")
namespace power_inputs_probe {
struct Result {
    power::InputReport inputs;
    power::BatteryRead battery;
    power::ButtonRead buttons;
    ui::ButtonQualification qualification;
    fsm::RobotResult robot;
    motors::Result applied;
};
using Probe = Result (*)(fsm::RobotInput, bool, bool, bool);
extern Probe volatile entry;
Result exercise(fsm::RobotInput, bool initialize, bool battery_slot, bool button_slot);
} // namespace power_inputs_probe
