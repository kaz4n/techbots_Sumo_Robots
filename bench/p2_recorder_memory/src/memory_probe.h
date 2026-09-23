// Declares inert B8 memory-probe addresses and target ABI evidence.
// Separates retained compilation paths from firmware execution and acceptance.
// Tested independently from D-071 and inspected in the final target ELF.
#pragma once
#include "core/fsm.h"
#include "hal/recorder.h"
#include <cstddef>
#include <cstdint>

namespace memory_probe {
enum TypeIndex : std::size_t {
    ROBOT, ATTEMPT_RECORDER, FRAME_BUFFER, STORED_FRAME, EVENT_BUFFER,
    ATTEMPT_SUMMARY, ROBOT_INPUT, ROBOT_RESULT, TYPE_COUNT
};
struct Abi {
    std::uint32_t version, record_bytes, log_hz, window_ms;
    std::uint32_t frame_capacity, event_capacity, pointer_bytes, size_t_bytes;
    std::uint32_t sizes[TYPE_COUNT];
    std::uint32_t alignments[TYPE_COUNT];
};
static_assert(sizeof(Abi) == 96U, "ABI record must be 24 uint32 words");
struct View {
    const recorder::StoredFrame* frame;
    const logframe::EventBytes* event;
    recorder::AttemptSummary summary;
    std::size_t frame_count, event_count;
    recorder::AttemptPhase phase;
    bool incomplete;
};
using StepProbe = void (*)(fsm::Robot&, const fsm::RobotInput&, fsm::RobotResult&);
using ConsumeProbe = recorder::ConsumeStatus (*)(recorder::AttemptRecorder&,
                                                const fsm::RobotResult&);
using QueryProbe = void (*)(const recorder::AttemptRecorder&, std::size_t, View&);
using ResetProbe = void (*)(fsm::Robot&, recorder::AttemptRecorder&);
void probeStep(fsm::Robot&, const fsm::RobotInput&, fsm::RobotResult&);
recorder::ConsumeStatus probeConsume(recorder::AttemptRecorder&, const fsm::RobotResult&);
void probeQuery(const recorder::AttemptRecorder&, std::size_t, View&);
void probeReset(fsm::Robot&, recorder::AttemptRecorder&);
extern fsm::Robot robot_owner;
extern recorder::AttemptRecorder recorder_owner;
extern const Abi abi;
extern fsm::Robot* volatile robot_address;
extern recorder::AttemptRecorder* volatile recorder_address;
extern const Abi* volatile abi_address;
extern StepProbe volatile step_address;
extern ConsumeProbe volatile consume_address;
extern QueryProbe volatile query_address;
extern ResetProbe volatile reset_address;
} // namespace memory_probe
