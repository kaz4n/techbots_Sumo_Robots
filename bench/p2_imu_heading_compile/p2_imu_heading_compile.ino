// Retains the continuous-heading estimator without consuming any observation.
// Unconfirmed candidate inputs select no physical mounting or runtime operation.
// Independent startup counters and target ELF inspection check this inert probe.
#include "src/config.h"
#include "src/imu_heading_probe.h"

namespace imu_heading_probe {
imu::Estimator estimator;
imu::Mounting candidate_mounting;
imu::Sample candidate_sample;
float candidate_bias_dps = 0.0F;
Probe volatile entry = nullptr;
} // namespace imu_heading_probe

void setup() {
    imu_heading_probe::entry = &imu_heading_probe::exercise;
}

void loop() {}
