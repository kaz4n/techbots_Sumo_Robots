// Declares a retained-only integration path for the D089 target compiler.
// No probe function is called by the inert compile sketch.
// Target symbol/source inspection and host tests supply distinct evidence.
#pragma once
#include "hal/ui_display.h"
namespace qtr_cal_probe {
struct Result {
    fsm::RobotResult robot;
    qtr_cal::Report calibration;
    ui::Frame frame;
    char snippet[80] = {};
    std::size_t written = 0U;
    qtr_cal::FormatStatus format;
    ui::RenderStatus render;
};
extern fsm::Robot robot;
extern qtr_cal::Calibration calibration;
using Probe = Result (*)(fsm::RobotInput, const line_qtr::Snapshot&, bool);
extern Probe volatile entry;
Result exercise(fsm::RobotInput input, const line_qtr::Snapshot& raw, bool calibrating);
}
