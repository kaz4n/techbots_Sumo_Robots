// Projects the actual IMU estimator report into the pure Robot input contract.
// Carries observation provenance without sampling clocks or granting motion.
// Independent host integration tests and an inert target probe exercise this map.
#pragma once
#include "imu_heading.h"
#include "../core/fsm.h"

namespace imu {
// Copies IMU fields/bias only; preserves caller decision time and other inputs.
// Invalid report metadata yields false and explicit contract_valid=false, never
// legacy fallback. Caller applies accepted Robot bias only to future increments.
bool applyEstimate(fsm::RobotInput& input, const Estimate& estimate);
} // namespace imu
