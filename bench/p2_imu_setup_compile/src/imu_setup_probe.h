// Declares retained checked-setup and coherent-decoder probe results.
// Source retention establishes compilation, not sensor or runtime acceptance.
// Independent host startup tests and target ELF inspection check this boundary.
#pragma once
#include "hal/imu.h"

namespace imu_setup_probe {
struct Result {
    imu::SetupReport started;
    imu::SetupReport advanced;
    imu::CoherentMotion decoded;
};
using Probe = Result (*)();
extern imu::Bus bus;
extern imu::Setup setup_driver;
extern Probe volatile entry;
Result exercise();
} // namespace imu_setup_probe
