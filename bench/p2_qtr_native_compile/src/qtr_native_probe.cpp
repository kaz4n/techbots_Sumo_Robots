// Retains actual QTR setup/acquisition, adapter, Robot consumers and frame encoding.
// This callable exercise remains unused by startup and has no physical grant.
// Independent native startup tests and target ELF review inspect non-execution.
#include "qtr_native_probe.h"

namespace qtr_native_probe {
__attribute__((noinline, used)) line_qtr::Snapshot exercise() {
    ++exercise_calls;
    reader.begin(exclusive_pads);
    reader.start();
    const auto snapshot = reader.advance();
    reader.cancel();
    fsm::RobotInput input = candidate_input;
    qualification = line_qtr::applySnapshot(input, snapshot);
    decision = robot.step(input);
    // This unused disabled receipt retains the actual next-tick recording path.
    input.previous = {};
    input.previous.applied_valid = true;
    input.previous.token = decision.token;
    input.previous.applied_us = input.t_us + 1U;
    input.previous.duration_valid = true;
    input.previous.completed_us = input.t_us + 1U;
    input.previous.execution_us = 1U;
    input.t_us += 2U;
    completed = robot.step(input);
    auto record = candidate_frame;
    record.state = decision.outputs.ui_state;
    record.line_mask = decision.line_mask;
    record.opp_mask = decision.opponent_mask;
    frame_status = logframe::packFrame(record, frame);
    return reader.report();
}
} // namespace qtr_native_probe
