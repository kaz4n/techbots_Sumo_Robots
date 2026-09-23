// Admits one genuine local stopped gesture into an inhibited service lifetime.
// Retains native owners and proves the reset against actual source and epoch time.
// Independent D103 gesture, lifecycle, unavailable-action and dump tests verify it.
#include "runtime.h"
#include <limits>

namespace app {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
} // namespace

bool Runtime::admitApplication() {
    if (!acceptClock(transaction_.report().applied.feedback.applied_us)) {
        fail(RuntimeFault::CLOCK);
        return false;
    }
    if ((report_.phase == RuntimePhase::STOP_OBSERVING || report_.service_only) &&
        !serviceReceiptValid()) {
        fail(RuntimeFault::TRANSACTION);
        return false;
    }
    const auto& robot = transaction_.report().robot;
    // Switching the second STOP tail back to CONTROL honestly exposes absent QTR.
    const auto expected = stop_tail_ ? static_cast<std::uint16_t>(fsm::LINE_CONTRACT) : 0U;
    if (report_.service_only && (service_source_failed_ ||
        adc_.report().fault != power::InputFault::NONE ||
        (robot.contract_faults & ~expected) != 0U || robot.escape_fault != edge::EscapeFault::NONE)) {
        fail(RuntimeFault::TRANSACTION);
        return false;
    }
    if (grants_.dump_enabled && !dumpReceiptValid()) {
        dump_.abort();
        report_.dump = dump_.report();
    }
    return true;
}

bool Runtime::serviceReceiptValid() const {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    const auto& gate = robot.lifecycle.gate;
    const auto& applied = tick.applied.feedback;
    return dumpReceiptValid() && robot.fresh && robot.token != 0U &&
        robot.token != std::numeric_limits<std::uint64_t>::max() &&
        tick.applied.fault == motors::Fault::STOPPED &&
        !gate.start_release && !gate.go && !gate.motion_permitted &&
        !robot.outputs.motors_enabled && robot.outputs.duty_l == 0.0F &&
        robot.outputs.duty_r == 0.0F && !applied.motors_enabled &&
        applied.duty_l == 0.0F && applied.duty_r == 0.0F;
}

bool Runtime::serviceButtonsValid() const {
    const auto& robot = transaction_.report().robot;
    const auto& value = decision_input_.buttons;
    const auto now = decision_input_.t_us;
    return serviceReceiptValid() && grants_.adc_pair && adc_.report().ready &&
        adc_.report().fault == power::InputFault::NONE && buttons_.attempted && buttons_.accepted &&
        robot.button_available && robot.button_updated &&
        (robot.contract_faults & fsm::BUTTON_CONTRACT) == 0U &&
        robot.outputs.ui_state == core::State::STOPPED &&
        robot.lifecycle.gate.phase == countdown::Phase::STOPPED &&
        value.explicit_values && value.contract_valid &&
        value.presence == core::ButtonPresence::VALID &&
        value.completed_us - value.started_us < config::VBAT_ADC_CONVERSION_US &&
        now - value.started_us <= config::BUTTON_SAMPLE_MAX_AGE_US &&
        now - value.completed_us < HALF_RANGE &&
        robot.button_source_us == value.started_us && robot.button_sequence == value.sequence &&
        robot.button_level == value.level && !transaction_.recording().summary().terminal_exhausted;
}

void Runtime::pendServiceReset() {
    const auto& robot = transaction_.report().robot;
    pending_source_us_ = decision_input_.buttons.started_us;
    pending_completed_us_ = decision_input_.buttons.completed_us;
    pending_sequence_ = decision_input_.buttons.sequence;
    pending_decision_us_ = decision_input_.t_us;
    pending_token_ = robot.token;
    pending_contract_faults_ = robot.contract_faults;
    pending_escape_fault_ = robot.escape_fault;
    report_.service_reset_pending = true;
    reset_gesture_ = ResetGesture::DISARMED;
}

void Runtime::serviceNone(std::uint32_t source_us) {
    switch (reset_gesture_) {
    case ResetGesture::DISARMED:
        reset_gesture_ = ResetGesture::NEUTRAL;
        gesture_anchor_us_ = source_us;
        break;
    case ResetGesture::NEUTRAL:
        if (source_us - gesture_anchor_us_ >= config::BTN_DEBOUNCE_MS * 1000U)
            reset_gesture_ = ResetGesture::READY;
        break;
    case ResetGesture::READY: break;
    case ResetGesture::HELD:
        reset_gesture_ = ResetGesture::RELEASE;
        gesture_anchor_us_ = source_us;
        break;
    case ResetGesture::RELEASE:
        if (source_us - gesture_anchor_us_ >= config::BTN_DEBOUNCE_MS * 1000U)
            pendServiceReset();
        break;
    default: reset_gesture_ = ResetGesture::DISARMED; break;
    }
}

void Runtime::serviceMode(std::uint32_t source_us) {
    switch (reset_gesture_) {
    case ResetGesture::READY:
        reset_gesture_ = ResetGesture::MODE;
        gesture_anchor_us_ = source_us;
        break;
    case ResetGesture::MODE:
        if (source_us - gesture_anchor_us_ >= config::BTN_DEBOUNCE_MS * 1000U) {
            reset_gesture_ = ResetGesture::HOLD;
            gesture_anchor_us_ = decision_input_.t_us;
        }
        break;
    case ResetGesture::HOLD: {
        const auto held = source_us - gesture_anchor_us_;
        if (held < HALF_RANGE && held >= config::BTN_LONG_MS * 1000U)
            reset_gesture_ = ResetGesture::HELD;
        break;
    }
    case ResetGesture::HELD: break;
    default: reset_gesture_ = ResetGesture::DISARMED; break;
    }
}

void Runtime::observeServiceReset() {
    if (report_.phase != RuntimePhase::STOP_OBSERVING || report_.service_only) return;
    if (!serviceButtonsValid()) {
        reset_gesture_ = ResetGesture::DISARMED;
        report_.service_reset_pending = false;
        return;
    }
    const auto& value = decision_input_.buttons;
    if (value.level == core::ButtonLevel::NONE) serviceNone(value.completed_us);
    else if (value.level == core::ButtonLevel::MODE) serviceMode(value.completed_us);
    else reset_gesture_ = ResetGesture::DISARMED;
}

bool Runtime::applyServiceReset() {
    if (!report_.service_reset_pending) return true;
    report_.service_reset_pending = false;
    reset_gesture_ = ResetGesture::DISARMED;
    const auto start = transaction_.report().started_us;
    if (start - pending_source_us_ > config::BUTTON_SAMPLE_MAX_AGE_US ||
        start - pending_decision_us_ >= HALF_RANGE) return true;
    dump_.onRobotReset();
    report_.dump = dump_.report();
    if (!transaction_.resetStoppedRobotForService()) {
        fail(RuntimeFault::TRANSACTION);
        return false;
    }
    report_.service_only = true;
    report_.service_reset_fresh = true;
    report_.reset_from_token = pending_token_;
    report_.pre_service_contract_faults = pending_contract_faults_;
    report_.pre_service_escape_fault = pending_escape_fault_;
    report_.initialization_complete = false;
    report_.phase = RuntimePhase::RUNNING;
    previous_state_ = core::State::BOOT;
    previous_calibration_context_ = false;
    stop_tail_ = false;
    service_first_source_ = true;
    std::uint32_t now = 0U;
    return clock(now);
}

void Runtime::checkServiceContinuity(std::uint32_t now_us) {
    if (!service_first_source_) return;
    service_first_source_ = false;
    const auto& value = decision_input_.buttons;
    const auto sequence = value.sequence - pending_sequence_;
    const auto completion = value.completed_us - pending_completed_us_;
    service_source_failed_ = !value.explicit_values || !value.contract_valid ||
        value.presence != core::ButtonPresence::VALID || sequence == 0U ||
        sequence >= HALF_RANGE || completion == 0U || completion >= HALF_RANGE ||
        value.started_us - pending_completed_us_ >= HALF_RANGE ||
        value.started_us - pending_source_us_ > config::BUTTON_SAMPLE_MAX_AGE_US ||
        now_us - pending_decision_us_ > config::BUTTON_SAMPLE_MAX_AGE_US;
}

void Runtime::serviceAction() {
    if (!report_.service_only) return;
    const auto& robot = transaction_.report().robot;
    const auto request = robot.menu.request;
    if (robot.fresh && robot.outputs.ui_state == core::State::IDLE &&
        (request == countdown::Service::QTR_CAL || request == countdown::Service::DRIVE_TEST))
        report_.service_action = {true, request, robot.token, ServiceActionStatus::UNAVAILABLE};
}
} // namespace app
