// Retains recorder and Robot code paths and their actual target ABI sizes.
// Makes compiler memory costs observable without invoking the probes on hardware.
// Independent host substitutes and final ELF inspection check D-071 evidence.
#include "memory_probe.h"

namespace memory_probe {
const Abi abi = {
    1U, sizeof(Abi), config::LOG_HZ, config::LOG_FRAME_WINDOW_MS,
    static_cast<std::uint32_t>(config::LOG_FRAME_CAPACITY),
    config::LOG_EVENT_CAPACITY, sizeof(void*), sizeof(std::size_t),
    {sizeof(fsm::Robot), sizeof(recorder::AttemptRecorder),
     sizeof(recorder::FrameBuffer), sizeof(recorder::StoredFrame),
     sizeof(logframe::EventBuffer), sizeof(recorder::AttemptSummary),
     sizeof(fsm::RobotInput), sizeof(fsm::RobotResult)},
    {alignof(fsm::Robot), alignof(recorder::AttemptRecorder),
     alignof(recorder::FrameBuffer), alignof(recorder::StoredFrame),
     alignof(logframe::EventBuffer), alignof(recorder::AttemptSummary),
     alignof(fsm::RobotInput), alignof(fsm::RobotResult)}
};

__attribute__((noinline))
void probeStep(fsm::Robot& robot, const fsm::RobotInput& input,
               fsm::RobotResult& result) {
    result = robot.step(input);
}

__attribute__((noinline))
recorder::ConsumeStatus probeConsume(recorder::AttemptRecorder& owner,
                                     const fsm::RobotResult& result) {
    return owner.consume(result);
}

__attribute__((noinline))
void probeQuery(const recorder::AttemptRecorder& owner, std::size_t index,
                View& view) {
    view.frame = owner.frames().at(index);
    view.event = owner.events().at(index);
    view.summary = owner.summary();
    view.frame_count = owner.frames().size();
    view.event_count = owner.events().size();
    view.phase = owner.phase();
    view.incomplete = owner.incomplete();
}

__attribute__((noinline))
void probeReset(fsm::Robot& robot, recorder::AttemptRecorder& owner) {
    owner.onRobotReset();
    robot.reset();
}
} // namespace memory_probe
