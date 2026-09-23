// Retains actual A1 acquisition, classification and Robot admission methods.
// The sketch never invokes this path, including during global startup.
// Host startup tests and target ELF inspection check this retained-only path.
#include "button_probe.h"

namespace button_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result;
    result.init = reader.beginWithButtons();
    result.raw = reader.readButtons();
    fsm::RobotInput input;
    input.t_us = result.raw.completed_us;
    result.qualification = ui::applyButtons(input, result.raw);
    result.robot = controller.step(input);
    return result;
}
} // namespace button_probe
