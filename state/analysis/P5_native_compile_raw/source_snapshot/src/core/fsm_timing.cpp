// Records D129's one P4 raw-clear candidate and its matched brake receipt.
// Keeps timing evidence observational so trace failures cannot change motion.
// Independent profile tests cover source windows, exclusions, receipt identity and wrap.
#include "fsm.h"

#if SUMOX_TIMING_EVIDENCE
namespace fsm {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
using Detail = logframe::TimingDetail;
}

void Robot::closeTimingTrace(Detail detail) {
    emit(tick_.t_us, core::Event::TIMING, static_cast<std::uint8_t>(detail), 1U);
    timing_trace_.phase = TimingPhase::CLOSED;
}

void Robot::receiveTimingTrace(const RobotInput& input, bool applied_valid) {
    const auto& receipt = input.previous;
    const bool timed = explicit_tick_timing_ && input.timing.explicit_start &&
        receipt.duration_valid && validTimingReceipt(input);
    tick_.timing_epoch_valid = timed;
    tick_.timing_approach = applied_valid && timed &&
        pending_.after_go && pending_.requested.ui_state == core::State::ATTACK &&
        !pending_.contact && receipt.motors_enabled &&
        receipt.duty_l > 0.0F && receipt.duty_r > 0.0F;
    if (timing_trace_.phase != TimingPhase::RECEIPT) return;
    const auto origin = timing_trace_.anchor_us;
    const std::uint32_t end = timing_trace_.read_end_us - origin;
    const std::uint32_t decision = timing_trace_.decision_us - origin;
    const std::uint32_t applied = receipt.applied_us - origin;
    const std::uint32_t observed = input.t_us - origin;
    const bool ordered = end <= decision && decision <= applied &&
        applied <= observed && observed < HALF_RANGE;
    const bool matched = pending_.token == timing_trace_.expected_token &&
        receipt.token == timing_trace_.expected_token;
    if (!applied_valid || !timed || !matched || !ordered ||
        !receipt.motors_enabled || receipt.duty_l != 0.0F || receipt.duty_r != 0.0F) {
        closeTimingTrace(Detail::INVALID_RECEIPT);
        return;
    }
    emit(receipt.applied_us, core::Event::TIMING,
         static_cast<std::uint8_t>(Detail::LOSS_ZERO_APPLIED), 1U);
    timing_trace_.phase = TimingPhase::CLOSED;
}

bool Robot::validTimingSource(const RobotInput& input) const {
    if (!tick_.sampled || !tick_.timing_epoch_valid || !input.opponent_read.valid || !explicit_tick_timing_ ||
        !input.timing.explicit_start || !validTimingStart(input) ||
        tick_.delta_us >= HALF_RANGE) return false;
    const auto start = input.timing.started_us;
    const std::uint32_t read_start = input.opponent_read.started_us - start;
    const std::uint32_t read_end = input.opponent_read.completed_us - start;
    const std::uint32_t decision = input.t_us - start;
    return read_start <= read_end && read_end <= decision && decision < HALF_RANGE;
}

bool Robot::timingFrontFiltered() const {
    const auto& observed = tick_.observation;
    return (observed.stuck.fault_mask & 7U) != 0U ||
        (observed.stuck.filtered_mask & ~observed.phantom.filtered_mask & 7U) != 0U;
}

bool Robot::timingLossBrake() const {
    const auto state = tick_.selected;
    return tick_.timing_loss_brake && (tick_.observation.confirmed_mask & 7U) == 0U &&
        (state == core::State::SEARCH || state == core::State::DEFEND_TURN) &&
        tick_.request.brake && !tick_.request.inhibited && tick_.permission &&
        faults_ == 0U && result_.outputs.motors_enabled &&
        result_.outputs.duty_l == 0.0F && result_.outputs.duty_r == 0.0F;
}

bool Robot::excludeTimingTrace(const RobotInput& input) {
    const auto origin = timing_trace_.anchor_us;
    const std::uint32_t start = input.opponent_read.started_us - origin;
    const std::uint32_t end = input.opponent_read.completed_us - origin;
    const std::uint32_t decision = input.t_us - origin;
    if (!validTimingSource(input) || start > end || end > decision || decision >= HALF_RANGE)
        closeTimingTrace(Detail::INVALID_SOURCE_TIME);
    else if ((config::EDGE_PUSH_THROUGH_MS > 0U && result_.line_mask != 0U) ||
             tick_.escape.escape_required ||
             tick_.escape.fault != edge::EscapeFault::NONE)
        closeTimingTrace(Detail::INTERRUPTED_EDGE);
    else if (!tick_.permission || faults_ != 0U || tick_.selected == core::State::STOPPED)
        closeTimingTrace(Detail::INTERRUPTED_STOP_FAULT);
    else if (timingFrontFiltered())
        closeTimingTrace(Detail::EXCLUDED_FILTER);
    else if (result_.contact ||
        (tick_.selected != core::State::ATTACK && tick_.selected != core::State::TRACK &&
         !timingLossBrake()))
        closeTimingTrace(Detail::EXCLUDED_CONTACT_ROUTE);
    return timing_trace_.phase == TimingPhase::CLOSED;
}

void Robot::publishTimingCandidate(const RobotInput& input) {
    const auto raw_front = (input.opp_raw_mask ^ config::OPP_ACTIVE_LOW_MASK) & 7U;
    if (timing_trace_.phase == TimingPhase::ARMED) {
        if (raw_front != 0U) return;
        timing_trace_.anchor_us = input.opponent_read.started_us;
        timing_trace_.read_end_us = input.opponent_read.completed_us;
        emit(timing_trace_.anchor_us, core::Event::TIMING,
             static_cast<std::uint8_t>(Detail::LOSS_READ_START), 1U);
        emit(timing_trace_.read_end_us, core::Event::TIMING,
             static_cast<std::uint8_t>(Detail::LOSS_READ_END), 1U);
        timing_trace_.phase = TimingPhase::OBSERVING;
        if (!tick_.timing_approach) {
            closeTimingTrace(Detail::EXCLUDED_NO_APPROACH);
            return;
        }
    } else if (raw_front != 0U) {
        closeTimingTrace(Detail::EXCLUDED_TRANSIENT);
        return;
    }
    if (!timingLossBrake()) return;
    timing_trace_.decision_us = tick_.t_us;
    timing_trace_.expected_token = result_.token;
    timing_trace_.phase = TimingPhase::RECEIPT;
    emit(tick_.t_us, core::Event::TIMING,
         static_cast<std::uint8_t>(Detail::LOSS_BRAKE_DECISION), 1U);
}

void Robot::publishTimingTrace(const RobotInput& input) {
    if (!attempt_go_ || timing_trace_.phase == TimingPhase::CLOSED ||
        timing_trace_.phase == TimingPhase::RECEIPT) return;
    if (timing_trace_.phase == TimingPhase::IDLE) {
        const auto raw_front = (input.opp_raw_mask ^ config::OPP_ACTIVE_LOW_MASK) & 7U;
        if (validTimingSource(input) && tick_.timing_approach &&
            tick_.selected == core::State::ATTACK && !result_.contact &&
            result_.outputs.motors_enabled && raw_front != 0U &&
            (result_.opponent_mask & 7U) != 0U && !timingFrontFiltered()) {
            timing_trace_.anchor_us = tick_.t_us;
            timing_trace_.phase = TimingPhase::ARMED;
            // D131 excludes edge-context approaches even while motion is deferred.
            if (config::EDGE_PUSH_THROUGH_MS > 0U && result_.line_mask != 0U)
                closeTimingTrace(Detail::INTERRUPTED_EDGE);
        }
        return;
    }
    if (!excludeTimingTrace(input)) publishTimingCandidate(input);
}
} // namespace fsm
#endif
