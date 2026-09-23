// Declares retained estimator lifecycle, bias and observation probe results.
// Candidate inputs are unconfirmed memory values, never a physical axis claim.
// Independent host startup tests and target ELF review verify this unused path.
#pragma once
#include "hal/imu_heading.h"

namespace imu_heading_probe {
struct Result {
    bool begun = false;
    imu::Estimate observation;
    bool bias_applied = false;
    imu::Estimate snapshot;
};
using Probe = Result (*)();
extern imu::Estimator estimator;
extern imu::Mounting candidate_mounting;
extern imu::Sample candidate_sample;
extern float candidate_bias_dps;
extern Probe volatile entry;
Result exercise();
} // namespace imu_heading_probe
