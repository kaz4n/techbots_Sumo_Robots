// Applies governed motor outputs through bounded, acknowledged port transactions.
// Keeps enable LOW across direction changes and independently enforces the hold.
// Independent port-trace tests check countdown, quantization and every I/O failure.
#include "motors.h"
#include <cmath>

namespace motors {
namespace {
bool validPeriod(std::uint32_t period_cycles) {
    // Above 2^24 the adapter's integer period cannot be represented exactly as float.
    return period_cycles != 0U && period_cycles <= 16777216U;
}

bool validOutput(const core::Outputs& output) {
    if (static_cast<std::uint8_t>(output.ui_state) >
        static_cast<std::uint8_t>(core::State::DRIVE_TEST)) return false;
    if (!std::isfinite(output.duty_l) || !std::isfinite(output.duty_r) ||
        std::fabs(output.duty_l) > 1.0F || std::fabs(output.duty_r) > 1.0F) return false;
    if (!output.motors_enabled && (output.duty_l != 0.0F || output.duty_r != 0.0F))
        return false;
    switch (output.ui_state) {
    case core::State::BOOT:
    case core::State::IDLE:
    case core::State::COUNTDOWN:
    case core::State::STOPPED:
    case core::State::DRIVE_TEST: return !output.motors_enabled;
    default: return true;
    }
}

float wheelPulses(float duty, std::uint32_t first, const Port& port,
                  std::uint32_t (&pulses)[4]) {
    const std::uint32_t channel = first + (duty < 0.0F ? 1U : 0U);
    const auto period = port.period_cycles[channel];
    // Multiplication in double avoids rounding a sub-cycle request up to a pulse.
    pulses[channel] = static_cast<std::uint32_t>(std::fabs(static_cast<double>(duty)) * period);
    const float applied = static_cast<float>(pulses[channel]) / static_cast<float>(period);
    return duty < 0.0F ? -applied : applied;
}
} // namespace

MotorGate::MotorGate(const Port& port) : port_(port) {}

bool MotorGate::validPort() const {
    if (port_.configureEnableLow == nullptr || port_.configurePwm == nullptr ||
        port_.writeEnable == nullptr || port_.writePwm == nullptr ||
        port_.settle == nullptr || port_.clockUs == nullptr) return false;
    for (std::uint32_t period : port_.period_cycles)
        if (!validPeriod(period)) return false;
    return true;
}

bool MotorGate::zeroPwm() {
    for (std::uint32_t index = 0; index < 4U; ++index)
        if (!port_.writePwm(port_.context, static_cast<Channel>(index),
                            port_.period_cycles[index], 0U)) return false;
    return true;
}

bool MotorGate::inhibit() {
    const bool enable_present = port_.writeEnable != nullptr;
    bool success = enable_present && port_.writeEnable(port_.context, false);
    bool io_failed = enable_present && !success;
    for (std::uint32_t index = 0; index < 4U; ++index) {
        // A failed callback must not short-circuit cleanup of the other channels.
        const bool writable = port_.writePwm != nullptr && validPeriod(port_.period_cycles[index]);
        const bool written = writable &&
            port_.writePwm(port_.context, static_cast<Channel>(index), port_.period_cycles[index], 0U);
        io_failed = (writable && !written) || io_failed;
        success = written && success;
    }
    const bool settled = port_.settle != nullptr && port_.settle(port_.context);
    io_failed = (port_.settle != nullptr && !settled) || io_failed;
    if (io_failed) fault_ = Fault::IO;
    else if ((!settled || !success) && fault_ == Fault::NONE) fault_ = Fault::PORT;
    return settled && success;
}

bool MotorGate::begin() {
    if (initialized_ || began_ || fault_ != Fault::NONE) return false;
    began_ = true;
    if (!validPort()) {
        fault_ = Fault::PORT;
        return false;
    }
    bool success = port_.configureEnableLow(port_.context) &&
                   port_.writeEnable(port_.context, false);
    for (std::uint32_t index = 0; index < 4U && success; ++index)
        success = port_.configurePwm(port_.context, static_cast<Channel>(index));
    if (success) success = zeroPwm();
    if (success) success = port_.settle(port_.context);
    if (!success) {
        fault_ = Fault::IO;
        inhibit();
        return false;
    }
    initialized_ = true;
    return true;
}

void MotorGate::disarm() {
    armed_ = false;
    hold_complete_ = false;
    release_us_ = 0U;
}

bool MotorGate::validCommand(std::uint32_t now, const fsm::RobotResult& command) {
    const auto& output = command.outputs;
    const auto& gate = command.lifecycle.gate;
    if (!validOutput(output) || static_cast<std::uint8_t>(gate.phase) >
        static_cast<std::uint8_t>(countdown::Phase::STOPPED)) return false;
    if (output.ui_state == core::State::BOOT || output.ui_state == core::State::IDLE ||
        output.ui_state == core::State::STOPPED || gate.phase == countdown::Phase::IDLE ||
        gate.phase == countdown::Phase::STOPPED) {
        disarm();
        return !gate.start_release && !output.motors_enabled;
    }
    if (gate.start_release) {
        if (armed_ || gate.phase != countdown::Phase::HOLDING ||
            output.ui_state != core::State::COUNTDOWN || gate.motion_permitted ||
            output.motors_enabled || gate.release_us != now) return false;
        armed_ = true;
        release_us_ = now;
        hold_complete_ = false;
    }
    if (!armed_ || gate.release_us != release_us_) return false;
    if (gate.phase == countdown::Phase::HOLDING &&
        (gate.motion_permitted || output.motors_enabled)) return false;
    const std::uint32_t hold_us = (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
    if (!hold_complete_ && static_cast<std::uint32_t>(now - release_us_) >= hold_us)
        hold_complete_ = true;
    if (!output.motors_enabled) return true;
    if (gate.phase != countdown::Phase::READY || !gate.motion_permitted || !hold_complete_ ||
        command.contract_faults != 0U || command.escape_fault != edge::EscapeFault::NONE)
        return false;
    if (std::fabs(output.duty_l) == 1.0F || std::fabs(output.duty_r) == 1.0F)
        return output.ui_state == core::State::ATTACK && command.contact &&
               opp_fusion::frontView(command.opponent_mask).centered;
    return true;
}

bool MotorGate::transact(const core::Outputs& output, fsm::PreviousTick& feedback) {
    const bool enabled = output.motors_enabled && MOTORS_ALLOWED != 0;
    std::uint32_t pulses[4] = {};
    const float duty_l = enabled ? wheelPulses(output.duty_l, 0U, port_, pulses) : 0.0F;
    const float duty_r = enabled ? wheelPulses(output.duty_r, 2U, port_, pulses) : 0.0F;
    bool success = port_.writeEnable(port_.context, false);
    for (std::uint32_t index = 0; index < 4U && success; ++index)
        success = port_.writePwm(port_.context, static_cast<Channel>(index),
                                 port_.period_cycles[index], pulses[index]);
    if (success) success = port_.settle(port_.context);
    if (success && enabled) success = port_.writeEnable(port_.context, true);
    if (!success) {
        fault_ = Fault::IO;
        inhibit();
        return false;
    }
    feedback.applied_valid = true;
    feedback.motors_enabled = enabled;
    feedback.duty_l = duty_l;
    feedback.duty_r = duty_r;
    return true;
}

Result MotorGate::apply(std::uint32_t decision_us, const fsm::RobotResult& command) {
    Result result;
    result.fault = fault_;
    if (!command.fresh) return result;
    if (command.token == 0U || command.token <= last_token_) {
        if (fault_ == Fault::NONE) fault_ = Fault::TOKEN;
        inhibit();
        result.fault = fault_;
        return result;
    }
    last_token_ = command.token;
    result.consumed = true;
    result.feedback.token = command.token;
    if (!initialized_) {
        if (fault_ == Fault::NONE) fault_ = Fault::NOT_INITIALIZED;
        inhibit();
    } else if (fault_ != Fault::NONE && fault_ != Fault::STOPPED) {
        inhibit();
    } else if (!validCommand(decision_us, command)) {
        if (fault_ == Fault::NONE) fault_ = Fault::COMMAND;
        inhibit();
    } else if (fault_ == Fault::STOPPED || command.outputs.ui_state == core::State::STOPPED ||
               command.lifecycle.gate.phase == countdown::Phase::STOPPED) {
        fault_ = Fault::STOPPED;
        disarm();
        const bool inhibited = inhibit();
        result.feedback.applied_valid = inhibited && !command.outputs.motors_enabled;
    } else {
        transact(command.outputs, result.feedback);
    }
    if (port_.clockUs != nullptr) result.feedback.applied_us = port_.clockUs(port_.context);
    result.fault = fault_;
    return result;
}

bool MotorGate::reset() {
    if (!inhibit()) return false;
    disarm();
    fault_ = Fault::NONE;
    began_ = initialized_;
    return true;
}

Fault MotorGate::fault() const { return fault_; }
} // namespace motors
