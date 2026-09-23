// Owns bounded B15 attempt evidence with explicit epoch and final-frame identity.
// Preserves loss and interrupted attempts without controlling hardware or cadence.
// Independent D-070 host tests cover lifecycle, tokens, malformed input and loss.
#include "recorder.h"

namespace recorder {
namespace {
bool knownState(core::State state) {
    return static_cast<std::uint8_t>(state) <=
        static_cast<std::uint8_t>(core::State::DRIVE_TEST);
}

bool endsAttempt(const fsm::RobotResult& result, core::State previous) {
    const auto state = result.outputs.ui_state;
    return state == core::State::STOPPED ||
        (state == core::State::EDGE_ESCAPE &&
         result.escape_fault != edge::EscapeFault::NONE) ||
        (previous == core::State::COUNTDOWN && state == core::State::IDLE);
}
} // namespace

ConsumeStatus AttemptRecorder::consume(const fsm::RobotResult& result) {
    if (result.token == 0U) return terminal(result);
    if (result.token == highest_token_) return ConsumeStatus::IGNORED_DUPLICATE;
    if (result.token < highest_token_ || !result.fresh) return reject();

    const auto gap = result.token - highest_token_ - 1U;
    highest_token_ = result.token;
    std::size_t first = 0U;
    const bool starting = result.lifecycle.gate.start_release;
    if (starting && startMarker(result, first)) {
        begin(result);
    } else {
        if (active()) {
            summary_.missing_results = saturatedAdd(summary_.missing_results, gap);
        }
        if (starting) return reject();
        if (!active()) return ConsumeStatus::OUTSIDE_ATTEMPT;
        if (!knownState(result.outputs.ui_state)) return reject();
    }

    const bool draining = phase_ == AttemptPhase::DRAINING;
    appendEvents(result.events, first);
    // START may carry the previous attempt's delayed receipt; it is excluded.
    const bool accepted_frame = !starting && appendFrame(result, result.token - 1U);
    observeSummary(result);
    if (draining) {
        summary_.final_frame_missing = !accepted_frame;
        phase_ = AttemptPhase::SEALED;
    } else if (endsAttempt(result, previous_state_)) {
        stopping_token_ = result.token;
        phase_ = AttemptPhase::DRAINING;
    }
    previous_state_ = result.outputs.ui_state;
    return ConsumeStatus::ACCEPTED;
}

bool AttemptRecorder::active() const {
    return phase_ == AttemptPhase::RECORDING || phase_ == AttemptPhase::DRAINING;
}

ConsumeStatus AttemptRecorder::reject() {
    if (active()) {
        summary_.rejected_results = logframe::saturatingIncrement(summary_.rejected_results);
    }
    return ConsumeStatus::REJECTED;
}

bool AttemptRecorder::startMarker(const fsm::RobotResult& result,
                                  std::size_t& index) const {
    const auto mode = static_cast<std::uint8_t>(result.running_mode);
    if (!knownState(result.outputs.ui_state) ||
        mode < static_cast<std::uint8_t>(core::Mode::SIDESTEP_R) ||
        mode > static_cast<std::uint8_t>(core::Mode::WAIT) ||
        result.events.count > logframe::ROBOT_EVENT_CAPACITY) return false;
    bool found = false;
    for (std::size_t i = 0U; i < result.events.count; ++i) {
        if (result.events.entries[i].type != core::Event::START_RELEASE) continue;
        if (found) return false;
        found = true;
        index = i;
    }
    if (!found) return false;
    const auto& marker = result.events.entries[index];
    return logframe::validEventMetadata(marker) && marker.detail == mode &&
        marker.t_us == result.lifecycle.gate.release_us;
}

void AttemptRecorder::begin(const fsm::RobotResult& result) {
    frames_.reset();
    events_.reset();
    summary_ = AttemptSummary{};
    summary_.epoch_token = result.token;
    summary_.release_us = result.lifecycle.gate.release_us;
    summary_.mode = result.running_mode;
    stopping_token_ = 0U;
    previous_state_ = core::State::COUNTDOWN;
    phase_ = AttemptPhase::RECORDING;
}

void AttemptRecorder::appendEvents(const logframe::EventBatch& batch,
                                   std::size_t first) {
    summary_.upstream_event_rejected = saturatedAdd(
        summary_.upstream_event_rejected, batch.rejected);
    summary_.upstream_event_invalid = saturatedAdd(
        summary_.upstream_event_invalid, batch.invalid_metadata);
    summary_.upstream_event_overflow = summary_.upstream_event_overflow || batch.overflowed;
    if (batch.count > logframe::ROBOT_EVENT_CAPACITY) {
        summary_.malformed_batches = logframe::saturatingIncrement(summary_.malformed_batches);
        return;
    }
    for (std::size_t i = first; i < batch.count; ++i) {
        logframe::EventBytes bytes;
        if (!logframe::validEventMetadata(batch.entries[i]) ||
            logframe::packEvent(batch.entries[i], bytes) != logframe::PackStatus::OK) {
            summary_.event_semantic_rejected = logframe::saturatingIncrement(
                summary_.event_semantic_rejected);
            continue;
        }
        events_.append(bytes);
    }
}

bool AttemptRecorder::appendFrame(const fsm::RobotResult& result,
                                  std::uint64_t expected) {
    if (!result.frame_ready) return false;
    if (result.frame_token != expected || result.frame_token < summary_.epoch_token ||
        result.frame_token <= summary_.last_frame_token ||
        (phase_ == AttemptPhase::DRAINING && result.frame_token != stopping_token_)) {
        summary_.identity_rejected = logframe::saturatingIncrement(summary_.identity_rejected);
        return false;
    }
    if (!frames_.append(result.frame, result.frame_status)) return false;
    summary_.last_frame_token = result.frame_token;
    return true;
}

void AttemptRecorder::observeSummary(const fsm::RobotResult& result) {
    const bool skipped_regressed = result.skipped_frames < summary_.skipped_frames;
    const bool ticks_regressed = result.ticks.ticks < summary_.ticks.ticks ||
        result.ticks.overruns < summary_.ticks.overruns ||
        result.ticks.max_us < summary_.ticks.max_us ||
        result.ticks.overruns > result.ticks.ticks;
    const bool saturated = summary_.ticks.saturated || result.ticks.saturated;
    if (!skipped_regressed) summary_.skipped_frames = result.skipped_frames;
    if (!ticks_regressed) summary_.ticks = result.ticks;
    summary_.ticks.saturated = saturated;
    if (skipped_regressed || ticks_regressed) {
        summary_.source_regressions = logframe::saturatingIncrement(summary_.source_regressions);
    }
    summary_.timing_incomplete = summary_.timing_incomplete ||
        result.timing_incomplete || saturated;
    summary_.recording_incomplete = summary_.recording_incomplete || result.recording_incomplete;
    summary_.go_seen = summary_.go_seen || result.lifecycle.gate.go;
    summary_.observed_results = logframe::saturatingIncrement(summary_.observed_results);
}

ConsumeStatus AttemptRecorder::terminal(const fsm::RobotResult& result) {
    if (highest_token_ != std::numeric_limits<std::uint64_t>::max() || result.fresh ||
        (result.contract_faults & fsm::TOKEN_EXHAUSTED) == 0U ||
        result.outputs.ui_state != core::State::STOPPED ||
        result.lifecycle.gate.start_release) return reject();
    if (terminal_seen_) return ConsumeStatus::IGNORED_DUPLICATE;
    terminal_seen_ = true;
    if (!active()) return ConsumeStatus::OUTSIDE_ATTEMPT;

    const bool draining = phase_ == AttemptPhase::DRAINING;
    appendEvents(result.events, 0U);
    const bool accepted_frame = appendFrame(result, highest_token_);
    observeSummary(result);
    if (draining) summary_.final_frame_missing = !accepted_frame;
    summary_.terminal_exhausted = true;
    onRobotReset();
    return ConsumeStatus::ACCEPTED;
}

void AttemptRecorder::onRobotReset() {
    if (!active()) return;
    phase_ = AttemptPhase::INTERRUPTED;
    summary_.interrupted = true;
    summary_.timing_incomplete = summary_.timing_incomplete || summary_.go_seen;
}

AttemptPhase AttemptRecorder::phase() const {
    return phase_;
}

const FrameBuffer& AttemptRecorder::frames() const {
    return frames_;
}

const logframe::EventBuffer& AttemptRecorder::events() const {
    return events_;
}

const AttemptSummary& AttemptRecorder::summary() const {
    return summary_;
}

bool AttemptRecorder::incomplete() const {
    return frames_.incomplete() || events_.overflowed() || events_.rejectedCount() != 0U ||
        summary_.missing_results != 0U || summary_.rejected_results != 0U ||
        summary_.identity_rejected != 0U || summary_.malformed_batches != 0U ||
        summary_.event_semantic_rejected != 0U || summary_.upstream_event_rejected != 0U ||
        summary_.upstream_event_invalid != 0U || summary_.source_regressions != 0U ||
        summary_.skipped_frames != 0U || summary_.final_frame_missing || summary_.interrupted ||
        summary_.terminal_exhausted || summary_.upstream_event_overflow ||
        summary_.recording_incomplete || summary_.timing_incomplete || summary_.ticks.saturated;
}

} // namespace recorder
