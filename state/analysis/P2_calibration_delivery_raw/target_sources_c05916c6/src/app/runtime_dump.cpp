// Services the retained recorder only under the actual post-MotorGate authority.
// Includes readiness, bounded transfer and cancellation in the real S..C lifetime.
// Independent D101 Runtime scenarios verify setup, receipts, timing and preemption.
#include "runtime.h"

namespace app {
void Runtime::initializeDump() {
    if (!grants_.dump_enabled) return;
    if (!dump_port_.begin || !dump_port_.ready || !dump_port_.output.write ||
        !dump_port_.output.cancel) {
        report_.dump_setup = recorder::dump::NativeStatus::CONTEXT;
        return;
    }
    report_.dump_setup = dump_port_.begin(dump_port_.context, grants_.dump);
}

bool Runtime::dumpReceiptValid() const {
    const auto& tick = transaction_.report();
    const auto& applied = tick.applied;
    return tick.phase == Phase::DECIDED && tick.decision_made &&
        applied.consumed && applied.feedback.applied_valid &&
        applied.feedback.token == tick.robot.token &&
        applied.feedback.applied_us - tick.decision_us < 0x80000000U &&
        (applied.fault == motors::Fault::NONE || applied.fault == motors::Fault::STOPPED);
}

bool Runtime::inhibitedIdle(std::uint32_t now_us) const {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    const auto& gate = robot.lifecycle.gate;
    const auto& applied = tick.applied.feedback;
    return robot.fresh && now_us - tick.decision_us < config::TICK_US &&
        robot.outputs.ui_state == core::State::IDLE &&
        gate.phase == countdown::Phase::IDLE && !gate.start_release && !gate.go &&
        !gate.motion_permitted && !robot.outputs.motors_enabled &&
        robot.outputs.duty_l == 0.0F && robot.outputs.duty_r == 0.0F &&
        !applied.motors_enabled && applied.duty_l == 0.0F && applied.duty_r == 0.0F;
}

bool Runtime::dumpReadyContext(std::uint32_t now_us) const {
    return report_.dump_setup == recorder::dump::NativeStatus::OK &&
        dumpReceiptValid() && transaction_.report().robot.token != 0U && inhibitedIdle(now_us);
}

bool Runtime::serviceDump() {
    if (!grants_.dump_enabled) return true;
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    // A failed real receipt was already cancelled immediately after application.
    // It cannot authorize readiness or consume a new service intent.
    if (!dumpReceiptValid()) return true;
    const bool ready = dumpReadyContext(now) && dump_port_.ready(dump_port_.context);
    if (!clock(now)) return false;
    const auto& tick = transaction_.report();
    const recorder::dump::Context context{now, tick.decision_us, ready, grants_.dump_origin};
    report_.dump = dump_.step(context, tick.robot, transaction_.recording());
    return clock(now);
}
} // namespace app
