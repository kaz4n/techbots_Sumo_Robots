// Retains concrete map validation, sample admission, integration and bias methods.
// Sketch startup only stores this function's address and never executes it.
// Host startup tests and target disassembly check the complete unused call path.
#include "imu_heading_probe.h"

namespace imu_heading_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result{};
    result.begun = estimator.begin(candidate_mounting, candidate_bias_dps);
    result.observation = estimator.observe(candidate_sample);
    result.bias_applied = estimator.applyBias(candidate_bias_dps);
    result.snapshot = estimator.report();
    return result;
}
} // namespace imu_heading_probe
