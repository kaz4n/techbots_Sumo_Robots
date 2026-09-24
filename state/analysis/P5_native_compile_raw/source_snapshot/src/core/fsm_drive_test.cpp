// Routes the isolated P3 profile through SEARCH and the actual edge controller.
// Reuses the full lifecycle, perception, governor and physical receipt boundaries.
// Independent profile tests exercise local start, no combat and real Gate safety.
#include "fsm.h"

#if SUMOX_P3_DRIVE_TEST
namespace fsm {
void Robot::routeDriveTest() {
    if (!tick_.permission) {
        cancelMotion();
        return;
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        if (tick_.escape.fault == edge::EscapeFault::NONE)
            acceptMotion(tick_.escape.row.motion, tick_.escape.row.profile, tick_.escape.row.brake);
        if (tick_.escape.row.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 1U);
        return;
    }
    tick_.selected = core::State::DRIVE_TEST;
    if (tick_.escape.exited) {
        // The exit observation brakes; a later distinct tick starts fresh SEARCH.
        cancelMotion();
        tick_.forced_brake = true;
        return;
    }
    runSearch();
}
} // namespace fsm
#endif
