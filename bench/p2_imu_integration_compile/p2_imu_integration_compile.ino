// Retains the actual estimator, Robot adapter and recording path for compilation.
// Startup stores an unused entry address; no observation or hardware is consumed.
// Independent startup counters and target ELF review verify this inert boundary.
#include "src/config.h"
#include "src/imu_integration_probe.h"

namespace imu_integration_probe {
imu::Estimator estimator;
fsm::Robot robot;
imu::Mounting candidate_mounting;
imu::Sample candidate_sample;
fsm::RobotInput candidate_input;
logframe::FrameInput candidate_frame;
float candidate_bias_dps = 0.0F;
unsigned exercise_calls = 0U;
Probe volatile entry = nullptr;
} // namespace imu_integration_probe

void setup() { imu_integration_probe::entry = &imu_integration_probe::exercise; }
void loop() {}
