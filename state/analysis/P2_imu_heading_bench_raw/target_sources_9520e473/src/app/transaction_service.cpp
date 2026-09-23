// Proves a real stopped tail before one local Robot-only service reset.
// Preserves the inhibited MotorGate, actual epoch clocks and retained evidence.
// Independent D103 transaction histories exercise eligibility and passivity.
#include "transaction.h"
#include <limits>

namespace app {
void Transaction::rememberStoppedCompletion() {
    const auto& robot = report_.robot;
    const auto& permission = robot.lifecycle.gate;
    const auto& applied = report_.applied;
    const auto& feedback = applied.feedback;
    const bool stopped = report_.finished && report_.timing_valid && report_.decision_made &&
        robot.fresh && robot.token != 0U &&
        robot.token != std::numeric_limits<std::uint64_t>::max() &&
        robot.outputs.ui_state == core::State::STOPPED &&
        permission.phase == countdown::Phase::STOPPED && !permission.start_release &&
        !permission.go && !permission.motion_permitted && !robot.outputs.motors_enabled &&
        robot.outputs.duty_l == 0.0F && robot.outputs.duty_r == 0.0F &&
        applied.consumed && applied.fault == motors::Fault::STOPPED &&
        feedback.applied_valid && feedback.token == robot.token &&
        !feedback.motors_enabled && feedback.duty_l == 0.0F && feedback.duty_r == 0.0F &&
        (report_.recorded == recorder::ConsumeStatus::ACCEPTED ||
         report_.recorded == recorder::ConsumeStatus::OUTSIDE_ATTEMPT);
    if (!stopped) stopped_completions_ = 0U;
    else if (stopped_completions_ < 2U) ++stopped_completions_;
}

bool Transaction::resetStoppedRobotForService() {
    const auto phase = recorder_.phase();
    if (report_.phase != Phase::ACQUIRING || service_reset_used_ || stopped_completions_ < 2U ||
        gate_.fault() != motors::Fault::STOPPED || recorder_.summary().terminal_exhausted ||
        (phase != recorder::AttemptPhase::EMPTY && phase != recorder::AttemptPhase::SEALED))
        return false;
    recorder_.onRobotReset();
    robot_.reset();
    previous_ = {};
    service_reset_used_ = true;
    stopped_completions_ = 0U;
    return true;
}
} // namespace app
