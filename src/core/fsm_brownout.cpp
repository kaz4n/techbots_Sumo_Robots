// Routes the isolated D244 B7 sequence through real safety and motor authority.
// Consumes phase-owned feedback only after current STOP, fault and edge arbitration.
// Independent Robot/Gate histories verify dwell counts, interruption and no rearm.
#include "fsm.h"

#if SUMOX_B7_BROWNOUT
namespace fsm {
namespace {
bool brownoutActive(brownout_sequence::Phase phase) {
    return phase == brownout_sequence::Phase::REACH || phase == brownout_sequence::Phase::DWELL;
}
} // namespace

void Robot::receiveBrownout(const RobotInput& input, bool applied_valid) {
    const auto& prior = input.previous;
    const auto& trial = brownout_.report();
    const bool owned = applied_valid && brownoutActive(pending_.brownout_phase) &&
        pending_.brownout_phase == trial.phase && pending_.brownout_leg_index == trial.leg_index &&
        pending_.requested.ui_state == core::State::OPENER;
    tick_.brownout_receipt = {owned, prior.token, pending_.brownout_leg_index,
        prior.applied_us, prior.motors_enabled, prior.duty_l, prior.duty_r};
}

void Robot::runBrownout(const RobotInput& input) {
    if (result_.lifecycle.gate.go) {
        if (!brownout_.start(input.t_us)) faults_ |= SCRIPT_START;
    } else if (brownout_.report().phase == brownout_sequence::Phase::NOT_STARTED) {
        faults_ |= SCRIPT_START;
    } else {
        brownout_.step(input.t_us, tick_.brownout_receipt);
    }
    const auto& trial = brownout_.report();
    tick_.request.profile = governor::Profile::B7_ELECTRICAL;
    tick_.request.duty_l = trial.duty_l;
    tick_.request.duty_r = trial.duty_r;
    brownout_inhibited_ = !brownoutActive(trial.phase);
    tick_.request.brake = brownout_inhibited_;
    if (trial.phase == brownout_sequence::Phase::ABORTED) faults_ |= SCRIPT_RESULT;
    if (brownout_inhibited_ || faults_ != 0U) brownout_stopping_ = true;
}

void Robot::routeBrownout(const RobotInput& input) {
    using Reason = brownout_sequence::Reason;
    brownout_inhibited_ = false;
    if (!tick_.permission) {
        const auto reason = (faults_ & APPLICATION_CONTRACT) != 0U ? Reason::APPLICATION :
            faults_ != 0U ? Reason::FAULT : Reason::STOP;
        brownout_.interrupt(reason, input.t_us);
        cancelMotion();
        if (brownout_.report().consumed || result_.lifecycle.gate.phase == countdown::Phase::STOPPED)
            brownout_stopping_ = true;
        return;
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        if (result_.lifecycle.gate.go && !brownout_.report().consumed) brownout_.start(input.t_us);
        brownout_edge_interrupted_ = true;
        brownout_.interrupt(Reason::EDGE, input.t_us);
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        if (tick_.escape.fault == edge::EscapeFault::NONE)
            acceptMotion(tick_.escape.row.motion, tick_.escape.row.profile, tick_.escape.row.brake);
        if (tick_.escape.row.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 1U);
        return;
    }
    if (tick_.escape.exited || brownout_edge_interrupted_) {
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        brownout_stopping_ = brownout_inhibited_ = true;
        return;
    }
    tick_.selected = core::State::OPENER;
    runBrownout(input);
}

void Robot::publishBrownout() {
    if (faults_ != 0U) {
        brownout_.interrupt(brownout_sequence::Reason::FAULT, tick_.t_us);
        brownout_stopping_ = brownout_inhibited_ = true;
        result_.outputs = {};
        result_.outputs.ui_state = tick_.selected = core::State::STOPPED;
    }
    result_.brownout = brownout_.report();
    result_.brownout_stopping = brownout_stopping_;
    result_.brownout_edge_interrupted = brownout_edge_interrupted_;
}

void Robot::resetBrownout() {
    brownout_.interrupt(brownout_sequence::Reason::RESET_REQUEST, last_us_);
    brownout_stopping_ = true;
    result_.brownout = brownout_.report();
    result_.brownout_stopping = true;
}
} // namespace fsm
#endif
