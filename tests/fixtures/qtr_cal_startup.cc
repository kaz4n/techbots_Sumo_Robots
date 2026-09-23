// Checks the actual retained D089 probe startup through its public ABI.
// Setup and repeated loops must leave pure owner histories untouched.
// This host executable has no native GPIO or physical motor backend.
#include "qtr_cal_probe.h"

void setup();
void loop();

int main() {
    if (qtr_cal_probe::entry != nullptr || qtr_cal_probe::calibration.thresholds().version != 0U) return 1;
    setup();
    if (qtr_cal_probe::entry != &qtr_cal_probe::exercise) return 2;
    for (unsigned i = 0U; i < 10000U; ++i) loop();
    fsm::RobotInput input;
    input.t_us = 100U;
    const auto result = qtr_cal_probe::robot.step(input);
    if (!result.fresh || result.token != 1U) return 3;
    auto eligible = result;
    eligible.outputs = {};
    eligible.outputs.ui_state = core::State::IDLE;
    eligible.line_raw_mode = eligible.line_calibration_hold = true;
    eligible.menu.selection.service_menu = true;
    eligible.menu.selection.service = eligible.menu.request = countdown::Service::QTR_CAL;
    const auto report = qtr_cal_probe::calibration.step(100U, eligible, {});
    if (report.phase != qtr_cal::Phase::COLLECTING || report.samples != 0U) return 4;
    return qtr_cal_probe::calibration.thresholds().version == 0U ? 0 : 5;
}
