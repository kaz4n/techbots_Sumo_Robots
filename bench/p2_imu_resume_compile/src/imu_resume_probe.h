// Declares the retained D094 integration exercise, never called by the sketch.
// Separates acquisition progress from completed sensor and estimator evidence.
// Host startup substitutes and target symbol inspection verify this probe ABI.
#pragma once
#pragma push_macro("EMPTY")
#undef EMPTY
#include "hal/imu_acquisition.h"
#include "hal/imu_adapter.h"
#include "hal/motor_port_unoq.h"
#include "hal/recorder.h"
#pragma pop_macro("EMPTY")
namespace imu_resume_probe {
enum class Action : std::uint8_t { INITIALIZE, SETUP, BEGIN, ADVANCE, CANCEL, LEGACY };
struct Result {
    imu::SetupReport setup;
    imu::SampleProgress progress;
    imu::Estimate estimate;
    bool admitted = false;
    fsm::RobotResult robot;
    motors::Result applied;
};
using Probe = Result (*)(fsm::RobotInput, Action, const imu::Mounting&, bool);
extern Probe volatile entry;
Result exercise(fsm::RobotInput, Action, const imu::Mounting&, bool power_confirmed);
} // namespace imu_resume_probe
