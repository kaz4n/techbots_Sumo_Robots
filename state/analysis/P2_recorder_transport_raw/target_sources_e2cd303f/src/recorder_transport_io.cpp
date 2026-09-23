// Binds inert checked motor callbacks and brackets the existing dump Transfer.
// Keeps native writes conditional on real inhibited-IDLE transaction evidence.
// Independent D116 traces verify clocks, cancellation order and unchanged bytes.
#include "recorder_transport.h"

namespace recorder_transport {
motors::Port Runner::motorPort(Runner* owner) {
    return {owner, configureEnable, configurePwm, writeEnable, writePwm, settle,
            ownerClock, {1U, 1U, 1U, 1U}};
}

bool Runner::configureEnable(void* context) {
    auto& self = *static_cast<Runner*>(context);
    self.add(self.report_.configure_enable_calls);
    return true;
}

bool Runner::configurePwm(void* context, motors::Channel channel) {
    auto& self = *static_cast<Runner*>(context);
    self.add(self.report_.configure_pwm_calls);
    const bool valid = static_cast<unsigned>(channel) < 4U;
    if (!valid) self.add(self.report_.invalid_motor_calls);
    return valid;
}

bool Runner::writeEnable(void* context, bool enabled) {
    auto& self = *static_cast<Runner*>(context);
    self.add(self.report_.write_enable_calls);
    if (enabled) {
        self.add(self.report_.enabled_en);
        self.add(self.report_.invalid_motor_calls);
    }
    return !enabled;
}

bool Runner::writePwm(void* context, motors::Channel channel,
                     std::uint32_t period, std::uint32_t pulse) {
    auto& self = *static_cast<Runner*>(context);
    self.add(self.report_.write_pwm_calls);
    if (pulse != 0U) self.add(self.report_.nonzero_pwm);
    const bool valid = static_cast<unsigned>(channel) < 4U && period == 1U && pulse == 0U;
    if (!valid) self.add(self.report_.invalid_motor_calls);
    return valid;
}

bool Runner::settle(void* context) {
    auto& self = *static_cast<Runner*>(context);
    self.add(self.report_.settle_calls);
    return true;
}

bool Runner::receiptValid() const {
    const auto& tick = transaction_.report();
    const auto& applied = tick.applied;
    const auto& receipt = applied.feedback;
    return tick.phase == app::Phase::DECIDED && tick.decision_made &&
        tick.robot.fresh && tick.robot.token != 0U && applied.consumed &&
        receipt.applied_valid && receipt.token == tick.robot.token &&
        receipt.applied_us - tick.decision_us < HALF_RANGE &&
        !receipt.motors_enabled && receipt.duty_l == 0.0F && receipt.duty_r == 0.0F &&
        (applied.fault == motors::Fault::NONE || applied.fault == motors::Fault::STOPPED);
}

bool Runner::inhibitedIdle(std::uint32_t now) const {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    const auto& gate = robot.lifecycle.gate;
    return receiptValid() && now - tick.decision_us < config::TICK_US &&
        robot.outputs.ui_state == core::State::IDLE && gate.phase == countdown::Phase::IDLE &&
        !gate.start_release && !gate.go && !gate.motion_permitted &&
        !robot.outputs.motors_enabled && robot.outputs.duty_l == 0.0F &&
        robot.outputs.duty_r == 0.0F;
}

bool Runner::transfer(std::uint32_t& after) {
    std::uint32_t before = 0U, now = 0U;
    if (!sample(before)) { fail(Failure::CLOCK); return false; }
    const bool ready = inhibitedIdle(before) && dump_port_.ready(dump_port_.context);
    if (!sample(now)) { fail(Failure::CLOCK); return false; }
    const auto decision = transaction_.report().decision_us;
    if (now - decision >= config::TICK_US) { fail(Failure::DEADLINE); return false; }
    transfer_.step({now, decision, ready, recorder::dump::Origin::SYNTHETIC},
                   transaction_.report().robot, source());
    if (!sample(after)) { fail(Failure::CLOCK); return false; }
    if (after - decision >= config::TICK_US) { fail(Failure::DEADLINE); return false; }
    const auto phase = transfer_.report().phase;
    if (phase == recorder::dump::Phase::REFUSED || phase == recorder::dump::Phase::FAILED ||
        phase == recorder::dump::Phase::CANCELLED) {
        fail(Failure::DUMP);
        return false;
    }
    return true;
}
} // namespace recorder_transport
