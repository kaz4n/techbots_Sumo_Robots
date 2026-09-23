// Declares a retained probe for the actual native MPU6050 transport.
// Bus transaction compilation does not establish sensor or runtime acceptance.
// Host startup counters and target ELF review verify this inert boundary.
#pragma once
#include "hal/imu_bus_unoq.h"

namespace imu_bus_probe {
struct Result {
    imu::BusInit init;
    imu::BusTransfer identity;
    imu::BusTransfer configuration;
    imu::BusTransfer motion;
};
using Probe = Result (*)();
extern imu::Bus bus;
extern Probe volatile entry;
Result exercise();
} // namespace imu_bus_probe
