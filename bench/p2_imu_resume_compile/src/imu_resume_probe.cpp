// Retains the actual resumable source, estimator, Robot, MotorGate and recorder.
// Never executes at startup; this is a link exercise, not an app scheduler.
// Independent D094 tests prove behavior; target ELF checks prove retained paths.
#include <Arduino.h>
#include "imu_resume_probe.h"
namespace imu_resume_probe {
imu::Acquirer source;
imu::Estimator estimator;
motors::UnoQPort native_motors;
motors::MotorGate gate{native_motors.port()};
fsm::Robot robot;
recorder::AttemptRecorder recorder;
fsm::PreviousTick previous;
__attribute__((noinline, used)) Result exercise(fsm::RobotInput input,
        Action action, const imu::Mounting& mounting, bool power_confirmed) {
    Result result;
    input.timing = {true, true, static_cast<std::uint32_t>(micros())};
    const auto now = input.timing.started_us;
    switch (action) {
    case Action::INITIALIZE:
        source.start(now, power_confirmed);
        estimator.begin(mounting, input.previous_bias_dps);
        gate.begin();
        break;
    case Action::SETUP: source.advanceSetup(now); break;
    case Action::BEGIN: result.progress = source.beginRead(now); break;
    case Action::ADVANCE: result.progress = source.advanceRead(now); break;
    case Action::CANCEL: result.progress = source.cancelRead(now); break;
    case Action::LEGACY:
        result.estimate = estimator.observe(source.read(now));
        break;
    }
    if (result.progress.completed)
        result.estimate = estimator.observe(result.progress.sample);
    result.setup = source.setupReport();
    input.t_us = micros();
    // Pending uses an absent estimate, never a replay with a new checked time.
    result.admitted = imu::applyEstimate(input, result.estimate);
    input.previous = previous;
    result.robot = robot.step(input);
    result.applied = gate.apply(input.t_us, result.robot);
    recorder.consume(result.robot);
    previous = result.applied.feedback;
    previous.completed_us = micros();
    previous.execution_us = previous.completed_us - input.timing.started_us;
    previous.duration_valid = true;
    return result;
}
} // namespace imu_resume_probe
