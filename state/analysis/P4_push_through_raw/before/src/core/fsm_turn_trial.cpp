// Routes the isolated D125 turn trial through the actual Robot and edge controller.
// Retains lifecycle, governor and MotorGate authority for every turn and brake request.
// Independent profile tests cover admission, cancellation, receipts and final inhibition.
#include "fsm.h"

#if SUMOX_P3_TURN_TRIAL
namespace fsm {
void Robot::cancelTurnTrial(turn_trial::Reason reason) {
    const auto phase = turn_trial_.report().phase;
    if (phase != turn_trial::Phase::TURN && phase != turn_trial::Phase::BRAKE) return;
    if (reason != turn_trial::Reason::STOP && reason != turn_trial::Reason::EDGE) return;
    const bool fresh = result_.turn_trial.fresh;
    const bool changed = result_.turn_trial.phase_changed;
    result_.turn_trial = turn_trial_.step({tick_.t_us, result_.heading.heading_deg,
        result_.heading.imu_ok, reason == turn_trial::Reason::EDGE,
        reason == turn_trial::Reason::STOP});
    // A late duplicate cannot cancel yet or erase an action observed this tick.
    result_.turn_trial.fresh = result_.turn_trial.fresh || fresh;
    result_.turn_trial.phase_changed = result_.turn_trial.phase_changed || changed;
}

void Robot::routeTurnTrial() {
    turn_trial_inhibited_ = false;
    if (!tick_.permission) {
        cancelTurnTrial(turn_trial::Reason::STOP);
        cancelMotion();
        if (turn_trial_.report().phase != turn_trial::Phase::NOT_STARTED ||
            result_.lifecycle.gate.phase == countdown::Phase::STOPPED)
            turn_trial_stopping_ = true;
        return;
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        turn_trial_edge_interrupted_ = true;
        cancelTurnTrial(turn_trial::Reason::EDGE);
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        if (tick_.escape.fault == edge::EscapeFault::NONE)
            acceptMotion(tick_.escape.row.motion, tick_.escape.row.profile, tick_.escape.row.brake);
        if (tick_.escape.row.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 1U);
        return;
    }
    if (tick_.escape.exited || turn_trial_edge_interrupted_) {
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        turn_trial_stopping_ = turn_trial_inhibited_ = true;
        return;
    }
    tick_.selected = core::State::DRIVE_TEST;
    if (result_.lifecycle.gate.go) {
        turn_trial_.start(tick_.t_us, result_.heading.heading_deg,
                          config::TURN_TRIAL_DEG, result_.heading.imu_ok);
        result_.turn_trial = turn_trial_.report();
    } else {
        result_.turn_trial = turn_trial_.step({tick_.t_us, result_.heading.heading_deg,
                                             result_.heading.imu_ok, false, false});
    }
    const auto& trial = result_.turn_trial;
    if (trial.phase_changed && trial.phase == turn_trial::Phase::BRAKE &&
        trial.turn_status == motion::Status::TIMED_OUT)
        markFault(logframe::FaultCode::TURN_TIMEOUT, 16U);
    if (trial.phase == turn_trial::Phase::FAULT) faults_ |= SCRIPT_RESULT;
    if (trial.phase == turn_trial::Phase::NOT_STARTED) faults_ |= SCRIPT_START;
    turn_trial_inhibited_ = trial.phase != turn_trial::Phase::TURN &&
        trial.phase != turn_trial::Phase::BRAKE;
    if (!turn_trial_inhibited_)
        acceptMotion({trial.duty_l, trial.duty_r, trial.turn_status, trial.imu_fallback},
                     governor::Profile::PIVOT, trial.phase == turn_trial::Phase::BRAKE);
    if (turn_trial_inhibited_ || faults_ != 0U) turn_trial_stopping_ = true;
}

void Robot::publishTurnTrial() {
    if (faults_ != 0U) {
        turn_trial_stopping_ = turn_trial_inhibited_ = true;
        result_.outputs = {};
        result_.outputs.ui_state = tick_.selected = core::State::STOPPED;
    }
    if (faults_ != 0U || !tick_.permission)
        cancelTurnTrial(turn_trial::Reason::STOP);
    const bool fresh = result_.turn_trial.fresh;
    const bool changed = result_.turn_trial.phase_changed;
    result_.turn_trial = turn_trial_.report();
    // Terminal helpers retain history; owner pulses belong only to this observation.
    result_.turn_trial.fresh = fresh;
    result_.turn_trial.phase_changed = changed;
    result_.turn_trial_stopping = turn_trial_stopping_;
    result_.turn_trial_edge_interrupted = turn_trial_edge_interrupted_;
}
} // namespace fsm
#endif
