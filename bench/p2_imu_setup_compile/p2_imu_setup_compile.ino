// Retains checked sensor setup and decoding without starting any operation.
// This compile-only probe is outside every firmware upload allowlist.
// Independent startup counters and target ELF inspection check its inertness.
#include "src/config.h"
#include "src/imu_setup_probe.h"

namespace imu_setup_probe {
imu::Bus bus;
imu::Setup setup_driver{bus};
Probe volatile entry = nullptr;
} // namespace imu_setup_probe

void setup() {
    imu_setup_probe::entry = &imu_setup_probe::exercise;
}

void loop() {}
