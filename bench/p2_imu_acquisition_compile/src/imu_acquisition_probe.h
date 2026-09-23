// Declares retained owned-setup and qualified-acquisition probe results.
// Compilation cannot establish sensor freshness, clock or runtime acceptance.
// Host startup counters and target ELF inspection verify this unused boundary.
#pragma once
#include "hal/imu_acquisition.h"

namespace imu_acquisition_probe {
struct Result {
    imu::SetupReport started;
    imu::SetupReport advanced;
    imu::Sample sample;
};
using Probe = Result (*)();
extern imu::Acquirer acquirer;
extern Probe volatile entry;
Result exercise();
} // namespace imu_acquisition_probe
