// Records D135's qualified opener cue, actual routing and matched application.
// Keeps evidence observational and reuses the existing Pending transaction owner.
// Independent profile tests cover predicates, chronology, loss and MotorGate receipts.
#include "fsm.h"

#if SUMOX_P5_ABORT_TIMING
namespace fsm {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
using Detail = logframe::OpenerTimingDetail;
using Cause = openers::AbortCause;
}

void Robot::closeOpenerTiming(Detail detail, std::uint16_t value) {
    emit(tick_.t_us, core::Event::TIMING, static_cast<std::uint8_t>(detail), value);
    abort_trace_phase_ = AbortTracePhase::CLOSED;
}

void Robot::captureOpenerAbort(const openers::AbortEvidence& evidence) {
    if (evidence.cause == Cause::NONE) return;
    tick_.abort = evidence;
    tick_.abort_token = result_.token;
}

void Robot::markOpenerHandover() {
    // Called only after the existing opener branch actually invokes normal routing.
    tick_.abort_routed = tick_.abort_token != 0U && tick_.abort_token == result_.token;
}

void Robot::receiveOpenerTiming(const RobotInput& input, bool applied_valid) {
    const auto& receipt = input.previous;
    const bool timed = pending_.valid && explicit_tick_timing_ &&
        input.timing.explicit_start && receipt.duration_valid && validTimingReceipt(input);
    tick_.abort_epoch_valid = timed;
    const bool tagged = pending_.valid && pending_.abort_handover;
    if (abort_trace_phase_ != AbortTracePhase::RECEIPT && !tagged) return;
    const bool coupled = tagged && abort_trace_phase_ == AbortTracePhase::RECEIPT;
    pending_.abort_handover = false;
    if (!coupled || !applied_valid || !timed ||
        receipt.token != pending_.token || (MOTORS_ALLOWED != 0 && !receipt.motors_enabled)) {
        closeOpenerTiming(Detail::INVALID_RECEIPT);
        return;
    }
    emit(receipt.applied_us, core::Event::TIMING, static_cast<std::uint8_t>(Detail::APPLIED), 1U);
    abort_trace_phase_ = AbortTracePhase::CLOSED;
}

bool Robot::validOpenerSource(const RobotInput& input) const {
    if (!tick_.sampled || !tick_.abort_epoch_valid || !input.opponent_read.valid ||
        !explicit_tick_timing_ || !input.timing.explicit_start || !validTimingStart(input) ||
        tick_.delta_us >= HALF_RANGE) return false;
    const auto start = input.timing.started_us;
    const std::uint32_t read_start = input.opponent_read.started_us - start;
    const std::uint32_t read_end = input.opponent_read.completed_us - start;
    const std::uint32_t decision = input.t_us - start;
    return read_start <= read_end && read_end <= decision && decision < HALF_RANGE;
}

std::uint16_t Robot::openerCueValue() const {
    return static_cast<std::uint16_t>(static_cast<std::uint8_t>(running_mode_) |
        (static_cast<std::uint8_t>(tick_.abort.phase) << 3U) |
        (static_cast<std::uint8_t>(tick_.abort.cause) << 6U) |
        (static_cast<std::uint16_t>(tick_.abort.effective_mask) << 8U) |
        (tick_.abort.snapshot_front_present ? 0x8000U : 0U));
}

bool Robot::validOpenerHandover() const {
    if (!tick_.abort_routed || tick_.abort_token != result_.token) return false;
    if ((tick_.abort.effective_mask & 7U) == 0U)
        return tick_.selected == core::State::DEFEND_TURN;
    const bool first_attack = config::ATTACK_ENTER_TICKS == 1U &&
        tick_.observation.bearing.centered;
    return tick_.selected == (first_attack ? core::State::ATTACK : core::State::TRACK);
}

void Robot::publishOpenerTiming(const RobotInput& input) {
    if (!attempt_go_ || abort_trace_phase_ != AbortTracePhase::WAITING) return;
    if (!validOpenerSource(input)) { closeOpenerTiming(Detail::INVALID_SOURCE); return; }
    const bool qualified = tick_.abort.cause == Cause::CURRENT_FRONT ||
        tick_.abort.cause == Cause::CURRENT_SIDE_OR_REAR;
    if (qualified) {
        emit(input.opponent_read.started_us, core::Event::TIMING,
             static_cast<std::uint8_t>(Detail::READ_START), 1U);
        emit(input.opponent_read.completed_us, core::Event::TIMING,
             static_cast<std::uint8_t>(Detail::READ_END), 1U);
        emit(tick_.t_us, core::Event::TIMING,
             static_cast<std::uint8_t>(Detail::QUALIFIED), openerCueValue());
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        closeOpenerTiming(Detail::INTERRUPTED, 1U); return;
    }
    if (!tick_.permission || faults_ != 0U || tick_.selected == core::State::STOPPED) {
        closeOpenerTiming(Detail::INTERRUPTED, 2U); return;
    }
    if (tick_.abort.cause == Cause::SNAPSHOT_ONLY || tick_.abort.cause == Cause::NATURAL_END) {
        closeOpenerTiming(Detail::NOT_ABORT,
            tick_.abort.cause == Cause::SNAPSHOT_ONLY ? 1U : 2U);
        return;
    }
    if (!qualified) return;
    const logframe::EventInput cue{tick_.t_us, core::Event::TIMING,
        static_cast<std::uint8_t>(Detail::QUALIFIED), openerCueValue()};
    if (!logframe::validEventMetadata(cue) || !validOpenerHandover()) {
        closeOpenerTiming(Detail::HANDOVER_FAILED, static_cast<std::uint16_t>(tick_.selected));
        return;
    }
    emit(tick_.t_us, core::Event::TIMING, static_cast<std::uint8_t>(Detail::HANDOVER),
         static_cast<std::uint16_t>(tick_.selected));
    abort_trace_phase_ = AbortTracePhase::RECEIPT;
}
} // namespace fsm
#endif
