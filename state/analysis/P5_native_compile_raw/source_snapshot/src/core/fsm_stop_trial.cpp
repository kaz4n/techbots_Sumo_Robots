// Routes one D126 stopping trial through actual Straight, Brake and edge controllers.
// Preserves governed motor authority and separates trial requests from distance evidence.
// Independent profile tests cover hold, timing, correction, cancellation and Gate writes.
#include "fsm.h"

#if SUMOX_P3_STOP_TRIAL
namespace fsm {
namespace {
bool trialActive(stop_trial::Phase phase) {
    return phase == stop_trial::Phase::APPROACH || phase == stop_trial::Phase::BRAKE;
}

void finishTrial(stop_trial::Report& report, stop_trial::Phase phase,
                 stop_trial::Reason reason, std::uint32_t t_us) {
    report.phase = phase;
    report.reason = reason;
    report.duty_l = report.duty_r = 0.0F;
    report.finished = true;
    report.finished_us = t_us;
    report.fresh = report.phase_changed = true;
}
} // namespace

void Robot::cancelStopTrial(stop_trial::Reason reason) {
    if (!trialActive(result_.stop_trial.phase)) return;
    if (reason != stop_trial::Reason::STOP && reason != stop_trial::Reason::EDGE) return;
    finishTrial(result_.stop_trial, stop_trial::Phase::INTERRUPTED, reason, tick_.t_us);
}

void Robot::faultStopTrial(bool start_failure) {
    faults_ |= start_failure ? SCRIPT_START : SCRIPT_RESULT;
    finishTrial(result_.stop_trial, stop_trial::Phase::FAULT,
                stop_trial::Reason::INVALID_MOTION, tick_.t_us);
    stop_trial_stopping_ = stop_trial_inhibited_ = true;
}

void Robot::runStopTrial() {
    auto& trial = result_.stop_trial;
    if (trial.phase == stop_trial::Phase::NOT_STARTED) {
        if (!result_.lifecycle.gate.go) { faultStopTrial(true); return; }
        if (!stop_approach_.start(tick_.t_us, result_.heading.heading_deg,
                                  config::STOP_TRIAL_DUTY, config::STOP_TRIAL_APPROACH_MS)) {
            trial.approach_status = motion::Status::INVALID;
            faultStopTrial(true);
            return;
        }
        trial.phase = stop_trial::Phase::APPROACH;
        trial.started = true;
        trial.started_us = tick_.t_us;
        trial.phase_changed = true;
    }
    if (trial.phase == stop_trial::Phase::APPROACH) {
        const auto approach = stop_approach_.step(tick_.t_us, result_.heading.heading_deg,
                                                  result_.heading.imu_ok);
        trial.approach_status = approach.status;
        trial.imu_fallback = approach.imu_fallback;
        trial.duty_l = approach.duty_l;
        trial.duty_r = approach.duty_r;
        trial.fresh = true;
        if (approach.status == motion::Status::ACTIVE) return;
        if (approach.status != motion::Status::DONE) { faultStopTrial(false); return; }
        trial.phase = stop_trial::Phase::BRAKE;
        trial.reason = stop_trial::Reason::NO_EDGE_TIMEOUT;
        trial.approach_finished = true;
        trial.approach_finished_us = tick_.t_us;
        trial.phase_changed = true;
        // Anchor actual Brake here; a delayed approach observation cannot consume it.
        if (!stop_brake_.start(tick_.t_us, config::STOP_TRIAL_BRAKE_MS))
            faultStopTrial(true);
        return;
    }
    if (trial.phase != stop_trial::Phase::BRAKE) return;
    const auto brake = stop_brake_.step(tick_.t_us);
    trial.fresh = true;
    trial.duty_l = trial.duty_r = 0.0F;
    if (brake.status == motion::Status::DONE) {
        finishTrial(trial, stop_trial::Phase::COMPLETE,
                    stop_trial::Reason::NO_EDGE_TIMEOUT, tick_.t_us);
    } else if (brake.status != motion::Status::ACTIVE) {
        faultStopTrial(false);
    }
}

void Robot::routeStopTrial() {
    stop_trial_inhibited_ = false;
    if (!tick_.permission) {
        cancelStopTrial(stop_trial::Reason::STOP);
        cancelMotion();
        if (result_.stop_trial.phase != stop_trial::Phase::NOT_STARTED ||
            result_.lifecycle.gate.phase == countdown::Phase::STOPPED)
            stop_trial_stopping_ = true;
        return;
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        stop_trial_edge_interrupted_ = true;
        cancelStopTrial(stop_trial::Reason::EDGE);
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        if (tick_.escape.fault == edge::EscapeFault::NONE)
            acceptMotion(tick_.escape.row.motion, tick_.escape.row.profile, tick_.escape.row.brake);
        if (tick_.escape.row.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 1U);
        return;
    }
    if (tick_.escape.exited || stop_trial_edge_interrupted_) {
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        stop_trial_stopping_ = stop_trial_inhibited_ = true;
        return;
    }
    tick_.selected = core::State::DRIVE_TEST;
    runStopTrial();
    const auto& trial = result_.stop_trial;
    stop_trial_inhibited_ = !trialActive(trial.phase);
    if (!stop_trial_inhibited_)
        acceptMotion({trial.duty_l, trial.duty_r, trial.approach_status, trial.imu_fallback},
                     governor::Profile::STOP_TRIAL_FORWARD, trial.phase == stop_trial::Phase::BRAKE);
    if (stop_trial_inhibited_ || faults_ != 0U) stop_trial_stopping_ = true;
}

void Robot::publishStopTrial() {
    if (faults_ != 0U) {
        stop_trial_stopping_ = stop_trial_inhibited_ = true;
        result_.outputs = {};
        result_.outputs.ui_state = tick_.selected = core::State::STOPPED;
    }
    if (faults_ != 0U || !tick_.permission) cancelStopTrial(stop_trial::Reason::STOP);
    result_.stop_trial_stopping = stop_trial_stopping_;
    result_.stop_trial_edge_interrupted = stop_trial_edge_interrupted_;
}
} // namespace fsm
#endif
