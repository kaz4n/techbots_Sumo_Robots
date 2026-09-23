// Owns B15 attempt evidence in fixed frame/event RAM without hardware integration.
// Preserves the last attempt across reset and reports every known evidence loss.
// Independent D-070 host tests cover epoch boundaries, final receipts and tokens.
#pragma once
#include "recorder_frames.h"
#include "../core/fsm.h"
#include <cstdint>
#include <limits>

namespace recorder {
enum class AttemptPhase : std::uint8_t { EMPTY, RECORDING, DRAINING, SEALED, INTERRUPTED };
enum class ConsumeStatus : std::uint8_t { ACCEPTED, IGNORED_DUPLICATE, OUTSIDE_ATTEMPT, REJECTED };
struct AttemptSummary {
    std::uint64_t epoch_token = 0;
    std::uint64_t last_frame_token = 0;
    std::uint32_t release_us = 0;
    core::Mode mode = core::Mode::SIDESTEP_R;
    std::uint32_t observed_results = 0;
    std::uint32_t missing_results = 0;
    std::uint32_t rejected_results = 0;
    std::uint32_t identity_rejected = 0;
    std::uint32_t malformed_batches = 0;
    std::uint32_t event_semantic_rejected = 0;
    std::uint32_t upstream_event_rejected = 0;
    std::uint32_t upstream_event_invalid = 0;
    std::uint32_t source_regressions = 0;
    std::uint32_t skipped_frames = 0;
    logframe::TickStatistics ticks;
    bool upstream_event_overflow = false;
    bool timing_incomplete = false;
    bool recording_incomplete = false;
    bool go_seen = false;
    bool final_frame_missing = false;
    bool interrupted = false;
    bool terminal_exhausted = false;
};
// Pure loss-counter arithmetic exposes UINT64 gaps without billions of iterations.
constexpr std::uint32_t saturatedAdd(std::uint32_t value, std::uint64_t added) {
    const auto remaining = std::numeric_limits<std::uint32_t>::max() - value;
    return added > remaining ? std::numeric_limits<std::uint32_t>::max() :
        value + static_cast<std::uint32_t>(added);
}
class AttemptRecorder {
public:
    AttemptRecorder() = default;
    AttemptRecorder(const AttemptRecorder&) = delete;
    AttemptRecorder& operator=(const AttemptRecorder&) = delete;
    // Exact ingestion/epoch/loss contract: state/analysis/P2_attempt_recorder_contract.md.
    ConsumeStatus consume(const fsm::RobotResult& result);
    // Preserve evidence; notify before reset/end-of-stream, never clear storage.
    void onRobotReset();
    AttemptPhase phase() const;
    const FrameBuffer& frames() const;
    const logframe::EventBuffer& events() const;
    const AttemptSummary& summary() const;
    bool incomplete() const;
private:
    bool active() const;
    ConsumeStatus reject();
    bool startMarker(const fsm::RobotResult& result, std::size_t& index) const;
    void begin(const fsm::RobotResult& result);
    void appendEvents(const logframe::EventBatch& batch, std::size_t first);
    bool appendFrame(const fsm::RobotResult& result, std::uint64_t expected);
    void observeSummary(const fsm::RobotResult& result);
    ConsumeStatus terminal(const fsm::RobotResult& result);
    FrameBuffer frames_;
    logframe::EventBuffer events_;
    AttemptSummary summary_;
    std::uint64_t highest_token_ = 0;
    std::uint64_t stopping_token_ = 0;
    core::State previous_state_ = core::State::BOOT;
    AttemptPhase phase_ = AttemptPhase::EMPTY;
    bool terminal_seen_ = false;
};
} // namespace recorder
