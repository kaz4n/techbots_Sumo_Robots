// Declares the inert native QTR-to-Robot exercise and its ungranted owner.
// The saved address retains acquisition and consumers without initialization.
// Native startup tests and target import/disassembly checks verify this boundary.
#pragma once
#include "hal/line_qtr_adapter.h"

namespace qtr_native_probe {
using Probe = line_qtr::Snapshot (*)();
extern line_qtr::Reader reader;
extern bool exclusive_pads;
extern fsm::Robot robot;
extern fsm::RobotInput candidate_input;
extern line_qtr::Qualification qualification;
extern fsm::RobotResult decision;
extern fsm::RobotResult completed;
extern logframe::FrameInput candidate_frame;
extern logframe::FrameBytes frame;
extern logframe::PackStatus frame_status;
extern unsigned exercise_calls;
extern Probe volatile entry;
line_qtr::Snapshot exercise();
} // namespace qtr_native_probe
