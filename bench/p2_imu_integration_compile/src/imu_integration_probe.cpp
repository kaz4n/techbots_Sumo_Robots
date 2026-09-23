// Retains actual estimator admission, adapter routing, Robot and recording code.
// The disabled receipt is a compile fixture, never evidence of motor application.
// Startup tests and target disassembly verify this callable path remains unused.
#include "imu_integration_probe.h"

namespace imu_integration_probe {
__attribute__((noinline, used)) Result exercise() {
    ++exercise_calls;
    Result result{};
    result.begun = estimator.begin(candidate_mounting, candidate_bias_dps);
    result.estimate = estimator.observe(candidate_sample);
    fsm::RobotInput input = candidate_input;
    result.mapped = imu::applyEstimate(input, result.estimate);
    result.decision = robot.step(input);
    if (result.decision.bias_update_requested)
        result.bias_applied = estimator.applyBias(result.decision.accepted_bias_dps);
    // A bounded memory-only second call retains the matched receipt/recording path.
    input.previous = {};
    input.previous.applied_valid = true;
    input.previous.token = result.decision.token;
    input.previous.applied_us = input.t_us + 1U;
    input.previous.duration_valid = true;
    input.previous.completed_us = input.t_us + 1U;
    input.previous.execution_us = 1U;
    input.t_us += 2U;
    result.completed = robot.step(input);
    result.frame_status = logframe::packFrame(candidate_frame, result.frame);
    return result;
}
} // namespace imu_integration_probe
