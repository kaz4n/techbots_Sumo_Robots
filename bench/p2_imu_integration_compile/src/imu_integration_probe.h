// Declares the retained estimator-to-Robot and frame-codec compile probe.
// Candidate state is memory only and asserts no physical mounting or application.
// Independent host startup checks and target ELF inspection test non-execution.
#pragma once
#include "hal/imu_adapter.h"

namespace imu_integration_probe {
struct Result {
    bool begun = false;
    imu::Estimate estimate;
    bool mapped = false;
    fsm::RobotResult decision;
    bool bias_applied = false;
    fsm::RobotResult completed;
    logframe::FrameBytes frame;
    logframe::PackStatus frame_status = logframe::PackStatus::INVALID;
};
using Probe = Result (*)();
extern imu::Estimator estimator;
extern fsm::Robot robot;
extern imu::Mounting candidate_mounting;
extern imu::Sample candidate_sample;
extern fsm::RobotInput candidate_input;
extern logframe::FrameInput candidate_frame;
extern float candidate_bias_dps;
extern unsigned exercise_calls;
extern Probe volatile entry;
Result exercise();
} // namespace imu_integration_probe
