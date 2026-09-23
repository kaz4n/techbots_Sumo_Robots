// Retains native I2C4 transport without starting or using the bus.
// This compile-only probe is outside all firmware upload allowlists.
// Independent host startup counters and target ELF review check the boundary.
#include "src/config.h"
#include "src/imu_bus_probe.h"

namespace imu_bus_probe {
imu::Bus bus;
Probe volatile entry = nullptr;
} // namespace imu_bus_probe

void setup() {
    imu_bus_probe::entry = &imu_bus_probe::exercise;
}

void loop() {}
