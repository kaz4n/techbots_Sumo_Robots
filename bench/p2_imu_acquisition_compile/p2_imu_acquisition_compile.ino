// Retains owned MPU6050 setup and acquisition without executing sensor work.
// This compile-only probe is outside every firmware upload allowlist.
// Independent startup counters and target ELF inspection check its inertness.
#include "src/config.h"
#include "src/imu_acquisition_probe.h"

namespace imu_acquisition_probe {
imu::Acquirer acquirer;
Probe volatile entry = nullptr;
} // namespace imu_acquisition_probe

void setup() {
    imu_acquisition_probe::entry = &imu_acquisition_probe::exercise;
}

void loop() {}
