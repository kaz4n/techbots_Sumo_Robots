// Runs actual Gate begin and one terminal halt only when explicitly granted.
// Retains each real outcome without inventing motion, cleanup or timing evidence.
// Independent D115 success, failure, clock and passive-repeat tests cover this path.
#include "motor_stand.h"

namespace motor_stand {
Runner::Runner(const motors::Port& port) : gate_(port) {}

bool Runner::begin(const Grants& grants) {
    if (attempted_) return false;
    attempted_ = true;
    if (!grants.exclusive_motor_outputs) {
        report_.phase = Phase::DISABLED;
        return true;
    }
    report_.phase = Phase::ACTIVE;
    report_.begin_called = true;
    report_.begin_ok = gate_.begin();
    report_.begin_fault = gate_.fault();
    report_.halt_called = true;
    report_.halt = gate_.halt();
    const auto& halt = report_.halt;
    const bool complete = report_.begin_ok && report_.begin_fault == motors::Fault::NONE &&
        halt.fresh && halt.attempted && halt.inhibition_confirmed && halt.timing_valid &&
        halt.fault == motors::Fault::STOPPED;
    report_.phase = complete ? Phase::COMPLETE : Phase::FAULT;
    return complete;
}

void Runner::poll() {}
const Report& Runner::report() const { return report_; }
} // namespace motor_stand
