// Links the real raw/control adapter, Robot, owner, bank and display composition.
// The probe is retained through a pointer and is never executed by the sketch.
// Host pipelines test behavior; target builds establish compilation only.
#include "qtr_cal_probe.h"
namespace qtr_cal_probe {
__attribute__((noinline, used)) Result exercise(fsm::RobotInput input,
        const line_qtr::Snapshot& raw, bool calibrating) {
    Result result;
    if (calibrating) line_qtr::applyRawSnapshot(input, raw);
    else line_qtr::applySnapshot(input, raw, calibration.thresholds());
    result.robot = robot.step(input);
    result.calibration = calibration.step(input.t_us, result.robot, raw);
    auto display = ui::displaySample(input, result.robot);
    ui::applyCalibration(display, result.calibration);
    result.render = ui::render(display, result.frame);
    result.format = qtr_cal::formatConfig(result.calibration, result.snippet,
                                         sizeof(result.snippet), result.written);
    return result;
}
}
