// Supplies explicit synthetic observations and observes the real service lifecycle.
// Preserves full recording, qualified local reset and actual menu authority.
// Independent D116 scenarios compare retained source rows with received output.
#include "recorder_transport.h"

namespace recorder_transport {
void Runner::enterStage(Stage stage, std::uint32_t now) {
    stage_ = stage;
    stage_started_us_ = now;
    stage_seen_ = true;
}

std::uint64_t Runner::stageDuration() const {
    switch (stage_) {
    case Stage::RESET_PRESS: case Stage::MENU_LONG: return G_US + LONG_US;
    case Stage::SELECT_RELEASE: return 2U * G_US;
    default: return G_US;
    }
}

void Runner::advanceStage(std::uint32_t now) {
    if (!stage_seen_) { enterStage(stage_, now); return; }
    if (std::uint64_t{now - stage_started_us_} < stageDuration()) return;
    switch (stage_) {
    case Stage::START_NEUTRAL: enterStage(Stage::START_PRESS, now); break;
    case Stage::START_PRESS: enterStage(Stage::START_RELEASE, now); break;
    case Stage::START_RELEASE: scenario_fault_ = report_.release_token == 0U; break;
    case Stage::RESET_NEUTRAL: enterStage(Stage::RESET_PRESS, now); break;
    case Stage::RESET_PRESS: enterStage(Stage::RESET_RELEASE, now); break;
    case Stage::SERVICE_NEUTRAL:
        if (service_idle_seen_) enterStage(Stage::MENU_LONG, now);
        break;
    case Stage::MENU_LONG: enterStage(Stage::MENU_RELEASE, now); break;
    case Stage::MENU_RELEASE: enterStage(Stage::SELECT_PRESS, now); break;
    case Stage::SELECT_PRESS: enterStage(Stage::SELECT_RELEASE, now); break;
    case Stage::SELECT_RELEASE:
        ++short_pairs_;
        if (short_pairs_ < 3U) enterStage(Stage::SELECT_PRESS, now);
        else {
            scenario_fault_ = !menu_is_log_;
            enterStage(Stage::REQUEST_PRESS, now);
        }
        break;
    case Stage::REQUEST_PRESS: enterStage(Stage::REQUEST_RELEASE, now); break;
    case Stage::REQUEST_RELEASE:
        scenario_fault_ = report_.request_token == 0U;
        enterStage(Stage::WAIT_DUMP, now);
        break;
    default: break;
    }
}

core::ButtonLevel Runner::stageButton() const {
    switch (stage_) {
    case Stage::START_PRESS: case Stage::REQUEST_PRESS: return core::ButtonLevel::START;
    case Stage::RESET_PRESS: case Stage::MENU_LONG: case Stage::SELECT_PRESS:
        return core::ButtonLevel::MODE;
    default: return core::ButtonLevel::NONE;
    }
}

fsm::RobotInput Runner::project(void* context, std::uint32_t decision) {
    return static_cast<Runner*>(context)->input(decision);
}

bool Runner::projectionClockAccepted(void* context) {
    return !static_cast<Runner*>(context)->clock_fault_;
}

fsm::RobotInput Runner::input(std::uint32_t now) {
    advanceStage(now);
    button_ = scenario_fault_ ? core::ButtonLevel::NONE : stageButton();
    fsm::RobotInput value;
    value.t_us = now;
    value.initialization_complete = true;
    value.vbat_v = config::V_NOM_V;
    value.vbat_valid = true;
    value.imu.explicit_values = true;
    value.opponent_fresh = true;
    value.opp_raw_mask = static_cast<std::uint8_t>(config::OPP_ACTIVE_LOW_MASK ^
                                                  (report_.go_seen ? 2U : 0U));
    if (report_.service_only) {
        value.line.explicit_values = true;
        value.line.use = core::LineUse::CALIBRATION;
    } else {
        value.observations_fresh = true;
        for (auto& raw : value.line_raw_us) raw = config::QTR_TIMEOUT_US;
        stop_projected_ = report_.release_token != 0U &&
            std::uint64_t{now - report_.release_us} >= RECORD_US;
        value.stop_requested = stop_projected_;
    }
    ++sequence_;
    value.button = button_;
    value.buttons = {true, true, core::ButtonPresence::VALID, button_, 0U, sequence_, now, now};
    if (service_first_) {
        scenario_fault_ = scenario_fault_ || sequence_ - pending_sequence_ != 1U ||
            now - pending_source_us_ == 0U || now - pending_source_us_ >= HALF_RANGE ||
            now - pending_source_us_ > config::BUTTON_SAMPLE_MAX_AGE_US;
        service_first_ = false;
    }
    return value;
}

bool Runner::observeDecision() {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    if (robot.contract_faults != 0U || robot.escape_fault != edge::EscapeFault::NONE ||
        !robot.button_available || !robot.button_updated || robot.button_sequence != sequence_ ||
        robot.button_source_us != tick.decision_us || robot.button_level != button_ ||
        report_.invalid_motor_calls != 0U || report_.enabled_en != 0U || report_.nonzero_pwm != 0U) {
        fail(Failure::SCENARIO);
        return false;
    }
    if (tick.recorded == recorder::ConsumeStatus::REJECTED || source().incomplete()) {
        fail(Failure::RECORDING);
        return false;
    }
    if (report_.service_only) return observeService();
    if (!observeRecording()) return false;
    if (report_.phase == Phase::RESET_GESTURE) observeResetGesture();
    return true;
}

bool Runner::observeRecording() {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    if (robot.lifecycle.gate.start_release) {
        if (report_.release_token != 0U || stage_ != Stage::START_RELEASE ||
            robot.lifecycle.gate.release_us != tick.decision_us) {
            fail(Failure::SCENARIO);
            return false;
        }
        report_.release_us = tick.decision_us;
        report_.release_token = robot.token;
        report_.phase = Phase::RECORDING;
        enterStage(Stage::RECORD, tick.decision_us);
    }
    if (robot.lifecycle.gate.go) {
        if (report_.release_token == 0U || report_.go_seen) { fail(Failure::SCENARIO); return false; }
        report_.go_seen = true;
    }
    if (robot.outputs.ui_state == core::State::STOPPED) {
        if (!stop_projected_ || !report_.go_seen) { fail(Failure::SCENARIO); return false; }
        if (report_.stop_token == 0U) {
            report_.stop_token = robot.token;
            report_.stop_us = tick.decision_us;
            report_.phase = Phase::STOPPING;
            enterStage(Stage::STOP_TAIL, tick.decision_us);
        }
    } else if (stop_projected_) { fail(Failure::SCENARIO); return false; }
    return true;
}

bool Runner::sealed() const {
    const auto& summary = source().summary();
    return source().phase() == recorder::AttemptPhase::SEALED && !source().incomplete() &&
        summary.go_seen && report_.go_seen && summary.epoch_token == report_.release_token &&
        summary.release_us == report_.release_us && summary.ticks.ticks != 0U &&
        source().frames().size() == config::LOG_FRAME_CAPACITY;
}

void Runner::observeResetGesture() {
    const auto& tick = transaction_.report();
    const auto now = tick.decision_us;
    const auto age = std::uint64_t{now - stage_started_us_};
    if (stage_ == Stage::RESET_NEUTRAL && age >= DEBOUNCE_US) reset_neutral_ = true;
    if (stage_ == Stage::RESET_PRESS && reset_neutral_) {
        if (!reset_mode_ && age >= DEBOUNCE_US) {
            reset_mode_ = true;
            reset_hold_us_ = now; // The actual qualifying decision anchors the hold.
        }
        if (reset_mode_ && std::uint64_t{now - reset_hold_us_} >= LONG_US) reset_held_ = true;
    }
    if (stage_ == Stage::RESET_RELEASE && reset_held_ && age >= DEBOUNCE_US) {
        report_.reset_pending = true;
        pending_source_us_ = now;
        pending_sequence_ = sequence_;
        pending_token_ = tick.robot.token;
    }
}

bool Runner::applyReset() {
    if (!report_.reset_pending) return true;
    report_.reset_pending = false;
    const auto start = transaction_.report().started_us;
    const auto& previous = transaction_.previous();
    if (!previous.applied_valid || !previous.duration_valid || previous.token != pending_token_ ||
        start - previous.completed_us >= HALF_RANGE || start - pending_source_us_ >= HALF_RANGE ||
        start - pending_source_us_ > config::BUTTON_SAMPLE_MAX_AGE_US) {
        fail(Failure::RESET);
        return false;
    }
    transfer_.onRobotReset();
    if (!transaction_.resetStoppedRobotForService()) { fail(Failure::RESET); return false; }
    report_.service_only = report_.reset_done = true;
    report_.reset_epoch_started_us = start;
    report_.reset_from_token = pending_token_;
    stage_ = Stage::SERVICE_NEUTRAL;
    stage_seen_ = false;
    service_first_ = true;
    report_.phase = Phase::SERVICE_MENU;
    return true;
}

bool Runner::observeService() {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    const auto& gate = robot.lifecycle.gate;
    if ((robot.outputs.ui_state != core::State::BOOT && robot.outputs.ui_state != core::State::IDLE) ||
        gate.start_release || gate.go || gate.motion_permitted || robot.outputs.motors_enabled ||
        robot.outputs.duty_l != 0.0F || robot.outputs.duty_r != 0.0F ||
        tick.applied.fault != motors::Fault::STOPPED) {
        fail(Failure::SCENARIO);
        return false;
    }
    if (!service_idle_seen_ && robot.outputs.ui_state == core::State::IDLE) {
        service_idle_seen_ = true;
        stage_started_us_ = tick.decision_us;
    }
    menu_is_log_ = robot.menu.selection.service_menu &&
        robot.menu.selection.service == countdown::Service::LOG_DUMP;
    if (robot.menu.request != countdown::Service::NONE) {
        if (robot.menu.request != countdown::Service::LOG_DUMP || !menu_is_log_ ||
            robot.menu.request_unavailable || report_.request_token != 0U ||
            stage_ != Stage::REQUEST_RELEASE) {
            fail(Failure::SCENARIO);
            return false;
        }
        report_.request_us = tick.decision_us;
        report_.request_token = robot.token;
        report_.phase = Phase::DUMPING;
    }
    return true;
}
} // namespace recorder_transport
