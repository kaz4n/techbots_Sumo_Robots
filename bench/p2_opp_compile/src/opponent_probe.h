// Declares the retained native opponent-driver compatibility probe.
// Separates executable method retention from authorization to run GPIO operations.
// Host startup counters and actual target symbol checks prove the probe stays inert.
#pragma once
#include "hal/opp_sensors.h"

namespace opponent_probe {
struct Result {
    opp_sensors::InitResult initialization;
    opp_sensors::Snapshot sample;
};
using Probe = Result (*)();
extern opp_sensors::Sensors sensors;
extern Probe volatile address;
Result exercise();
} // namespace opponent_probe
