// Retains the actual countdown calibration path for compile-only inspection.
// Setup stores an unused entry address; no observations or hardware are consumed.
// Independent startup counters and target disassembly verify this inert boundary.
#include "src/config.h"
#include "src/core/countdown.h"

namespace calibration_probe {
countdown::Lifecycle lifecycle;
countdown::ServiceSample sample;
countdown::LifecycleResult result;
core::ButtonLevel button = core::ButtonLevel::NONE;
float previous_bias_dps = 0.0F;
bool stop_requested = false;
unsigned exercise_calls = 0U;
using Probe = void (*)();
Probe volatile entry = nullptr;

__attribute__((noinline, used)) void exercise() {
    ++exercise_calls;
    result = lifecycle.step(sample, button, previous_bias_dps, stop_requested);
}
} // namespace calibration_probe

void setup() { calibration_probe::entry = &calibration_probe::exercise; }
void loop() {}
