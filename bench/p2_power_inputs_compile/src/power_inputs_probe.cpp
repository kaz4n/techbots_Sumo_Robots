// Retains native Reader and MotorGate beside the new fixed ADC owner.
// Does not execute; this link exercise is neither a scheduler nor board evidence.
// D093 independent tests prove behavior; target ELF checks prove retained paths.
#include <Arduino.h>
#include "power_inputs_probe.h"
namespace power_inputs_probe {
power::Reader reader;
power::InputOwner inputs{power::readerInputPort(reader)};
motors::UnoQPort native_motors;
motors::MotorGate gate{native_motors.port()};
fsm::Robot robot;
recorder::AttemptRecorder recorder;
fsm::PreviousTick previous;
__attribute__((noinline, used)) Result exercise(fsm::RobotInput input,
        bool initialize, bool battery_slot, bool button_slot) {
    Result result;
    if (initialize) {
        inputs.begin();
        gate.begin();
    }
    input.timing = {true, true, static_cast<std::uint32_t>(micros())};
    result.battery = inputs.readBatteryIfDue(battery_slot);
    result.buttons = inputs.readButtons(button_slot);
    input.t_us = micros();
    inputs.applyBattery(input);
    result.qualification = inputs.applyButtons(input, result.buttons);
    result.inputs = inputs.report();
    input.previous = previous;
    // Other sensor readiness remains the caller's obligation in this link probe.
    input.initialization_complete = input.initialization_complete && input.vbat_valid;
    result.robot = robot.step(input);
    result.applied = gate.apply(input.t_us, result.robot);
    recorder.consume(result.robot);
    previous = result.applied.feedback;
    previous.completed_us = micros();
    previous.execution_us = previous.completed_us - input.timing.started_us;
    previous.duration_valid = true;
    return result;
}
} // namespace power_inputs_probe
