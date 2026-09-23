// Projects retained sensor evidence at the actual Transaction decision clock.
// Prevents expired samples from reviving and pairs post-work with the same input.
// Independent D096 boundary, lifecycle and calibration tests exercise this seam.
#include "runtime.h"
#include <limits>

namespace app {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
std::uint32_t ageAfter(std::uint32_t age, std::uint32_t elapsed) {
    const auto limit = std::numeric_limits<std::uint32_t>::max();
    return elapsed > limit - age ? limit : age + elapsed;
}
bool calibrationContext(const fsm::RobotResult& robot) {
    return robot.outputs.ui_state == core::State::IDLE &&
        robot.menu.selection.service_menu &&
        robot.menu.selection.service == countdown::Service::QTR_CAL;
}
} // namespace

void Runtime::selectLineMode() {
    const auto state = previous_state_;
    if (report_.service_only)
        report_.raw_lines = state == core::State::BOOT || state == core::State::IDLE;
    else if (state == core::State::BOOT) report_.raw_lines = !confirmed_bank_;
    else if (state == core::State::IDLE)
        report_.raw_lines = previous_calibration_context_ || !confirmed_bank_;
    else report_.raw_lines = false;
}

bool Runtime::opponentsReady() const {
    if (!grants_.opponents || !report_.opponents_setup.ready ||
        report_.opponents_setup.configured_mask != 0x7FU) return false;
    for (const auto status : report_.opponents_setup.status) if (status != 0) return false;
    return true;
}

bool Runtime::opponentsFresh(std::uint32_t now_us) const {
    if (!opponentsReady() || !opponents_.valid || opponents_.valid_mask != 0x7FU ||
        opponents_.raw_mask > 0x7FU) return false;
    for (unsigned i = 0U; i < 7U; ++i) {
        const auto value = opponents_.status[i];
        if ((value != 0 && value != 1) ||
            value != static_cast<std::int32_t>((opponents_.raw_mask >> i) & 1U)) return false;
    }
    const auto start = transaction_.report().started_us;
    const auto duration = now_us - start;
    return duration < HALF_RANGE && opponents_.started_us - start <=
        opponents_.completed_us - start && opponents_.completed_us - start <= duration;
}

void Runtime::projectImu(std::uint32_t now_us, std::uint32_t elapsed_us) {
    if (report_.service_only) {
        decision_input_.imu.explicit_values = true;
        decision_input_.previous_bias_dps = estimator_.report().bias_dps;
        return;
    }
    auto publication = imu_publication_;
    publication.bias_dps = estimator_.report().bias_dps;
    // Validate the genuine publication before considering delivery-time expiry.
    if (!imu::applyEstimate(decision_input_, publication) || !publication.heading_available)
        return;
    if (imu_new_) {
        imu_age_us_ = now_us - publication.observation_us;
        imu_new_ = false;
        if (imu_age_us_ >= HALF_RANGE || now_us - publication.checked_us >= HALF_RANGE) {
            decision_input_.imu.contract_valid = false;
            return;
        }
    } else imu_age_us_ = ageAfter(imu_age_us_, elapsed_us);
    if (imu_age_us_ > config::IMU_HEADING_MAX_GAP_US) report_.imu_expired = true;
    if (!report_.imu_expired) return;
    decision_input_.imu = {};
    decision_input_.imu.explicit_values = true;
    decision_input_.imu.gyro = core::ImuPresence::INVALID;
    decision_input_.imu.accel = core::ImuPresence::INVALID;
    decision_input_.imu_ok = false;
    decision_input_.raw_heading_deg = decision_input_.raw_gyro_z_dps = 0.0F;
    decision_input_.ax_g = decision_input_.ay_g = 0.0F;
    decision_input_.previous_bias_dps = publication.bias_dps;
}

void Runtime::projectLines(std::uint32_t now_us, std::uint32_t elapsed_us) {
    decision_line_ = {};
    if (!report_.service_only && line_current_.phase == line_qtr::Phase::FAULT)
        decision_line_ = line_current_;
    else if (!sources_cancelled_ && line_seen_) {
        const auto qualification = line_qtr::validateRaw(line_mailbox_);
        const bool new_source = line_new_;
        if (new_source) {
            line_age_us_ = now_us - line_mailbox_.started_us;
            line_new_ = false;
        } else line_age_us_ = ageAfter(line_age_us_, elapsed_us);
        const bool future = new_source && (now_us - line_mailbox_.started_us >= HALF_RANGE ||
            now_us - line_mailbox_.completed_us >= HALF_RANGE);
        if (qualification != line_qtr::RawQualification::VALID || future)
            decision_line_ = line_mailbox_;
        else {
            if (line_age_us_ >= config::QTR_SAMPLE_MAX_AGE_US) line_expired_ = true;
            if (!line_expired_) decision_line_ = line_mailbox_;
        }
    }
    if (report_.raw_lines) line_qtr::applyRawSnapshot(decision_input_, decision_line_);
    else line_qtr::applySnapshot(decision_input_, decision_line_, calibration_.thresholds());
}

fsm::RobotInput Runtime::projectThunk(void* context, std::uint32_t now_us) {
    return static_cast<Runtime*>(context)->project(now_us);
}

bool Runtime::clockAcceptedThunk(void* context) {
    return !static_cast<Runtime*>(context)->projection_failed_;
}

fsm::RobotInput Runtime::project(std::uint32_t now_us) {
    decision_input_ = {};
    decision_input_.t_us = now_us;
    decision_input_.timing = {true, true, transaction_.report().started_us};
    decision_input_.previous = transaction_.previous();
    const auto elapsed = decision_seen_ ? now_us - last_decision_us_ : 0U;
    projection_failed_ = !acceptClock(now_us) || elapsed >= HALF_RANGE;
    decision_seen_ = true;
    last_decision_us_ = now_us;
    adc_.applyBattery(decision_input_);
    adc_.applyButtons(decision_input_, buttons_);
    checkServiceContinuity(now_us);
    projectImu(now_us, elapsed);
    projectLines(now_us, elapsed);
    decision_input_.opponent_fresh = opponentsFresh(now_us);
    if (decision_input_.opponent_fresh) decision_input_.opp_raw_mask = opponents_.raw_mask;
    const auto& buttons = decision_input_.buttons;
    const bool current_buttons = buttons.contract_valid &&
        buttons.presence == core::ButtonPresence::VALID &&
        now_us - buttons.started_us <= config::BUTTON_SAMPLE_MAX_AGE_US &&
        now_us - buttons.completed_us < HALF_RANGE;
    const bool line_ready = report_.service_only || (grants_.qtr_exclusive_pads &&
        report_.line_setup == line_qtr::Status::OK);
    const bool ready = opponentsReady() && line_ready && grants_.adc_pair &&
        adc_.report().ready && decision_input_.vbat_valid && current_buttons &&
        decision_input_.opponent_fresh && (report_.raw_lines ||
        (decision_input_.line.contract_valid &&
            decision_input_.line.presence == core::LinePresence::VALID &&
            now_us - decision_input_.line.started_us < config::QTR_SAMPLE_MAX_AGE_US &&
            now_us - decision_input_.line.completed_us < HALF_RANGE));
    report_.initialization_complete = report_.initialization_complete || ready;
    decision_input_.initialization_complete = report_.initialization_complete;
    return decision_input_;
}

bool Runtime::display() {
    if (!grants_.matrix_enabled) return true;
    auto sample = ui::displaySample(decision_input_, transaction_.report().robot);
    ui::applyCalibration(sample, report_.calibration);
    sample.service_unavailable = report_.service_only && sample.service_menu &&
        (sample.service == countdown::Service::QTR_CAL ||
         sample.service == countdown::Service::DRIVE_TEST);
    ui::Frame frame;
    if (ui::render(sample, frame) != ui::RenderStatus::OK) {
        report_.matrix_status = ui::MatrixStatus::INVALID_FRAME;
        return true;
    }
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    report_.matrix_status = source_.submitMatrix(source_.context, now, frame);
    return clock(now);
}

bool Runtime::postDecision() {
    const auto& robot = transaction_.report().robot;
    // Only these two facts cross Transaction::open; its full result stays owned there.
    previous_state_ = robot.outputs.ui_state;
    previous_calibration_context_ = calibrationContext(robot);
    if (!report_.service_only && robot.bias_update_requested) {
        if (!estimator_.applyBias(robot.accepted_bias_dps))
            imu_publication_ = estimator_.report();
    }
    if (!report_.service_only) {
        report_.calibration = calibration_.step(decision_input_.t_us, robot, decision_line_);
        if (report_.calibration.committed) confirmed_bank_ = true;
    }
    observeServiceReset();
    serviceAction();
    if (!stop_tail_ && robot.outputs.ui_state == core::State::STOPPED) cancelSources();
#if !MATCH
    if (!prepareCalibrationOutput(!report_.service_only && report_.calibration.committed))
        return false;
#endif
    if (!display()) return false;
    if (!serviceDump()) return false;
#if !MATCH
    return serviceCalibrationOutput();
#else
    return true;
#endif
}
} // namespace app
