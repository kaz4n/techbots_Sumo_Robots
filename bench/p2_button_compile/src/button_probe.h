// Declares an inert retention probe for ADC, classifier and actual Robot routing.
// Compile evidence cannot approve button voltages or permit motor operation.
// Independent startup counters and target ELF inspection verify this boundary.
#pragma once
#include "hal/ui.h"

namespace button_probe {
struct Result {
    power::InitResult init;
    power::ButtonSample raw;
    ui::ButtonQualification qualification = ui::ButtonQualification::ABSENT;
    fsm::RobotResult robot;
};
using Probe = Result (*)();
extern power::Reader reader;
extern fsm::Robot controller;
extern Probe volatile entry;
Result exercise();
} // namespace button_probe
