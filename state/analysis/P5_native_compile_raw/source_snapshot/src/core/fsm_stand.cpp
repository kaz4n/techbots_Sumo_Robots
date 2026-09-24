// Routes the explicitly identified D120 B4 profile through the actual Robot.
// Retains lifecycle, escape, governor and application-receipt motor authority.
// Independent profile tests cover hold, phases, cancellation and terminal STOP.
#include "fsm.h"

#if SUMOX_B4_STAND
namespace fsm {
void Robot::cancelStand(stand_sequence::Reason reason) {
    if (stand_.interrupt(reason)) result_.stand = stand_.report();
}

void Robot::routeStand(const RobotInput& input) {
    stand_inhibited_ = false;
    if (!tick_.permission) {
        cancelStand(stand_sequence::Reason::STOP);
        cancelMotion();
        return;
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        stand_edge_interrupted_ = true;
        cancelStand(stand_sequence::Reason::EDGE);
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        if (tick_.escape.fault == edge::EscapeFault::NONE)
            acceptMotion(tick_.escape.row.motion, tick_.escape.row.profile, tick_.escape.row.brake);
        if (tick_.escape.row.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 1U);
        return;
    }
    if (tick_.escape.exited || stand_edge_interrupted_) {
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        stand_stopping_ = stand_inhibited_ = true;
        return;
    }
    tick_.selected = core::State::OPENER;
    if (result_.lifecycle.gate.go) {
        if (!stand_.start(input.t_us)) faults_ |= SCRIPT_START;
        else result_.stand = stand_.report();
    } else {
        result_.stand = stand_.step(input.t_us);
    }
    const auto& sequence = stand_.report();
    tick_.request.profile = governor::Profile::STAND;
    tick_.request.duty_l = sequence.duty_l;
    tick_.request.duty_r = sequence.duty_r;
    tick_.request.brake = sequence.phase != stand_sequence::Phase::DRIVE;
    stand_inhibited_ = sequence.phase != stand_sequence::Phase::DRIVE &&
        sequence.phase != stand_sequence::Phase::BRAKE;
    if (sequence.phase == stand_sequence::Phase::FAULT) faults_ |= SCRIPT_RESULT;
    if (sequence.phase == stand_sequence::Phase::NOT_STARTED) faults_ |= SCRIPT_START;
    if (sequence.phase == stand_sequence::Phase::COMPLETE || faults_ != 0U)
        stand_stopping_ = true;
}

void Robot::publishStand() {
    if (faults_ != 0U || !tick_.permission)
        cancelStand(stand_sequence::Reason::STOP);
    const bool fresh = result_.stand.fresh;
    const bool changed = result_.stand.phase_changed;
    result_.stand = stand_.report();
    // Rejected interruptions are passive and may retain old helper pulses.
    result_.stand.fresh = fresh;
    result_.stand.phase_changed = changed;
    result_.stand_stopping = stand_stopping_;
}
} // namespace fsm
#endif
