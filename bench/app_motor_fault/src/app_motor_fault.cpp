// Observes real application epochs through the unchanged native callback trace.
// Freezes pre-abort evidence without granting peripherals or inventing receipts.
// Independent D186 contract tests verify stop ordering and passive terminal states.
#include "app_motor_fault.h"

namespace app_motor_fault {
Runner::Runner(const motors::Port& motor, const power::InputPort& adc,
               const app::SourcePort& sources, const app::DumpPort& dump)
    : trace_(motor), runtime_(trace_.port(), adc, sources, dump) {}

bool Runner::begin(const motor_fault::Grants& grant) {
    if (attempted_) return false;
    attempted_ = true;
    if (!grant.exclusive_motor_outputs) {
        report_.phase = Phase::DISABLED;
        return true;
    }
    report_.phase = Phase::RUNNING;
    report_.begin_called = true;
    trace_.context(motor_fault::Stage::SETUP, 0U);
    report_.begin_ok = runtime_.begin(app::SetupGrants{});
    report_.begin_finished = true;
    if (!report_.begin_ok) {
        freeze(Reason::SETUP_FAILED);
        return false;
    }
    const auto reason = stopReason();
    if (reason != Reason::NONE) freeze(reason);
    return active();
}

bool Runner::applicationValid() const {
    const auto& tick = runtime_.transaction().report();
    if (!tick.decision_made) return true;
    const auto& applied = tick.applied;
    const auto& feedback = applied.feedback;
    return applied.consumed && feedback.applied_valid &&
        feedback.token == tick.robot.token && !feedback.motors_enabled &&
        feedback.duty_l == 0.0F && feedback.duty_r == 0.0F;
}

Reason Runner::stopReason() const {
    const auto& trace = trace_.report();
    if (trace.has_failure) return Reason::CALLBACK_FAILURE;
    if (trace.overflow || trace.timing_fault) return Reason::TRACE_INVALID;
    if (!applicationValid()) return Reason::APPLICATION_INVALID;
    const auto& runtime = runtime_.report();
    if (runtime.phase == app::RuntimePhase::FAULT ||
        runtime.phase == app::RuntimePhase::STOPPED) return Reason::RUNTIME_TERMINAL;
    if (runtime.epochs >= EPOCH_SAMPLES) return Reason::EPOCH_LIMIT;
    return Reason::NONE;
}

void Runner::freeze(Reason reason) {
    if (!active()) return;
    report_.phase = Phase::FINALIZING;
    report_.reason = reason;
    report_.before_abort.runtime = runtime_.report();
    report_.before_abort.transaction = runtime_.transaction().report();
    report_.before_abort.previous = runtime_.transaction().previous();
    report_.before_abort_valid = true;
    trace_.context(motor_fault::Stage::HALT, runtime_.report().epochs);
    report_.abort_called = true;
    runtime_.abort();
    report_.abort_returned = true;
    report_.phase = Phase::FROZEN;
}

void Runner::poll() {
    if (!active()) return;
    trace_.context(motor_fault::Stage::APPLY, runtime_.report().epochs + 1U);
    report_.last_step_returned = runtime_.step();
    const auto reason = stopReason();
    if (reason != Reason::NONE) freeze(reason);
}
} // namespace app_motor_fault
