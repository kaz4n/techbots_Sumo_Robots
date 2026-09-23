// Retains the native QTR Reader-to-Robot path for compile-only target inspection.
// Startup publishes an address; ungranted candidate state never accesses pads.
// Independent startup counters and target disassembly verify inert execution.
#include "src/config.h"
#include "src/qtr_native_probe.h"

namespace qtr_native_probe {
line_qtr::Reader reader;
bool exclusive_pads = false;
fsm::Robot robot;
fsm::RobotInput candidate_input;
line_qtr::Qualification qualification = line_qtr::Qualification::ABSENT;
fsm::RobotResult decision;
fsm::RobotResult completed;
logframe::FrameInput candidate_frame;
logframe::FrameBytes frame;
logframe::PackStatus frame_status = logframe::PackStatus::INVALID;
unsigned exercise_calls = 0U;
Probe volatile entry = nullptr;
} // namespace qtr_native_probe

void setup() { qtr_native_probe::entry = &qtr_native_probe::exercise; }
void loop() {}
