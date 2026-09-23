// Retains one real Robot and recorder for isolated B8 target-memory evidence.
// Publishes addresses only so compilation cannot imply runtime qualification.
// Independent host substitutes and target ELF inspection verify inertness.
#include "src/config.h"
#include "src/memory_probe.h"

static_assert(MATCH == 0, "This memory compile probe cannot be a MATCH build");
static_assert(MOTORS_ALLOWED == 0, "This memory compile probe must remain inert");

namespace memory_probe {
fsm::Robot robot_owner;
recorder::AttemptRecorder recorder_owner;
fsm::Robot* volatile robot_address = nullptr;
recorder::AttemptRecorder* volatile recorder_address = nullptr;
const Abi* volatile abi_address = nullptr;
StepProbe volatile step_address = nullptr;
ConsumeProbe volatile consume_address = nullptr;
QueryProbe volatile query_address = nullptr;
ResetProbe volatile reset_address = nullptr;
} // namespace memory_probe

void setup() {
    memory_probe::robot_address = &memory_probe::robot_owner;
    memory_probe::recorder_address = &memory_probe::recorder_owner;
    memory_probe::abi_address = &memory_probe::abi;
    memory_probe::step_address = &memory_probe::probeStep;
    memory_probe::consume_address = &memory_probe::probeConsume;
    memory_probe::query_address = &memory_probe::probeQuery;
    memory_probe::reset_address = &memory_probe::probeReset;
}

void loop() {
}
