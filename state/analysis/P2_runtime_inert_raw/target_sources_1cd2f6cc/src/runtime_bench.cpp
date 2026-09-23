// Observes the real Runtime with absent sources and an entirely inert motor port.
// Freezes truthful BOOT evidence without creating a match, STOP or native I/O.
// Independent D104 boundary tests verify chronology, receipts and terminal lifetime.
#include "runtime_bench.h"
#include <limits>

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Runtime probe must remain inert");

namespace runtime_bench {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
constexpr std::uint64_t WINDOW_US = std::uint64_t(config::LOG_FRAME_WINDOW_MS) * 1000U;
constexpr std::uint64_t GRACE_US = std::uint64_t(config::BTN_LONG_MS) * 1000U;
constexpr std::uint64_t DEADLINE_US = WINDOW_US + GRACE_US;
constexpr std::uint64_t REQUIRED_EPOCHS = (WINDOW_US + config::TICK_US - 1U) / config::TICK_US;
constexpr auto COUNTER_MAX = std::numeric_limits<std::uint32_t>::max();
static_assert(config::TICK_US > 0U && WINDOW_US > 0U && GRACE_US > 0U);
static_assert(DEADLINE_US < HALF_RANGE && REQUIRED_EPOCHS < COUNTER_MAX);
static_assert(config::APP_CLOCK_STALL_MAX_POLLS > 0U);

bool inhibited(const core::Outputs& output) {
    return !output.motors_enabled && output.duty_l == 0.0F && output.duty_r == 0.0F;
}
bool inhibited(const fsm::PreviousTick& output) {
    return !output.motors_enabled && output.duty_l == 0.0F && output.duty_r == 0.0F;
}
std::uint32_t absentMask(const fsm::RobotInput& input) {
    const auto& line = input.line;
    const auto& imu = input.imu;
    const auto& buttons = input.buttons;
    const bool raw = line.explicit_values && line.contract_valid &&
        line.presence == core::LinePresence::ABSENT && line.use == core::LineUse::CALIBRATION &&
        line.sequence == 0U && line.started_us == 0U && line.completed_us == 0U &&
        line.white_candidates == 0U && line.threshold_version == 0U;
    const bool inert_imu = imu.explicit_values && imu.contract_valid &&
        imu.gyro == core::ImuPresence::ABSENT && imu.accel == core::ImuPresence::ABSENT &&
        !imu.heading_available && !imu.heading_updated && imu.checked_us == 0U &&
        imu.observation_us == 0U && imu.sequence == 0U && !input.imu_ok &&
        input.raw_heading_deg == 0.0F && input.raw_gyro_z_dps == 0.0F &&
        input.ax_g == 0.0F && input.ay_g == 0.0F && input.previous_bias_dps == 0.0F;
    const bool inert_buttons = buttons.explicit_values && buttons.contract_valid &&
        buttons.presence == core::ButtonPresence::ABSENT &&
        buttons.level == core::ButtonLevel::NONE && buttons.raw == 0U &&
        buttons.sequence == 0U && buttons.started_us == 0U && buttons.completed_us == 0U &&
        input.button == core::ButtonLevel::NONE;
    return (raw ? 1U : 0U) | (inert_imu ? 2U : 0U) | (inert_buttons ? 4U : 0U) |
        (!input.vbat_valid && input.vbat_v == 0.0F ? 8U : 0U) |
        (!input.opponent_fresh && input.opp_raw_mask == 0U ? 16U : 0U);
}
} // namespace

InertMotorPort::InertMotorPort(const ClockPort& clock) : clock_(clock) {}

motors::Port InertMotorPort::port() {
    // Unit periods represent inert integers, never a physical PWM frequency.
    return {this, configureEnable, configurePwm, writeEnable, writePwm,
            settle, clockUs, {1U, 1U, 1U, 1U}};
}
const Counters& InertMotorPort::counters() const { return counters_; }

bool InertMotorPort::count(std::uint32_t& value) {
    if (value < COUNTER_MAX) ++value;
    if (value == COUNTER_MAX) counters_.saturated = counters_.fault = true;
    return !counters_.fault;
}

bool InertMotorPort::accept(bool valid) {
    if (!valid) {
        count(counters_.invalid);
        counters_.fault = true;
    }
    return valid && !counters_.fault;
}

bool InertMotorPort::configureEnable(void* context) {
    auto& self = *static_cast<InertMotorPort*>(context);
    self.count(self.counters_.setup_enable);
    if (!self.accept(!self.enable_configured_ && self.pwm_configured_ == 0U)) return false;
    self.enable_configured_ = true;
    return true;
}

bool InertMotorPort::configurePwm(void* context, motors::Channel channel) {
    auto& self = *static_cast<InertMotorPort*>(context);
    self.count(self.counters_.setup_pwm);
    const auto index = static_cast<unsigned>(channel);
    const bool valid = self.enable_configured_ && index < 4U &&
        (self.pwm_configured_ & (1U << index)) == 0U;
    if (!self.accept(valid)) return false;
    self.pwm_configured_ |= static_cast<std::uint8_t>(1U << index);
    return true;
}

bool InertMotorPort::writeEnable(void* context, bool enabled) {
    auto& self = *static_cast<InertMotorPort*>(context);
    self.count(enabled ? self.counters_.enabled : self.counters_.enable_low);
    if (enabled) self.counters_.fault = true;
    return self.accept(self.enable_configured_);
}

bool InertMotorPort::writePwm(void* context, motors::Channel channel,
                               std::uint32_t period, std::uint32_t pulse) {
    auto& self = *static_cast<InertMotorPort*>(context);
    self.count(pulse == 0U ? self.counters_.pwm_zero : self.counters_.nonzero);
    if (pulse != 0U) self.counters_.fault = true;
    return self.accept(self.enable_configured_ && self.pwm_configured_ == 15U &&
        static_cast<unsigned>(channel) < 4U && period == 1U);
}

bool InertMotorPort::settle(void* context) {
    auto& self = *static_cast<InertMotorPort*>(context);
    self.count(self.counters_.settle);
    return self.accept(self.enable_configured_ && self.pwm_configured_ == 15U);
}

std::uint32_t InertMotorPort::clockUs(void* context) {
    auto& self = *static_cast<InertMotorPort*>(context);
    self.count(self.counters_.clock);
    if (!self.clock_.now_us) { self.accept(false); return 0U; }
    return self.clock_.now_us(self.clock_.context);
}

Runner::Runner(const ClockPort& clock)
    : clock_(clock), motor_({this, observeClock}), runtime_(motor_.port(), {}, {}) {
    report_.schema_version = 1U;
    report_.byte_size = sizeof(Report);
}
const Report& Runner::report() const { return report_; }
const app::Runtime& Runner::runtime() const { return runtime_; }

bool Runner::terminal() const {
    return report_.phase == static_cast<std::uint32_t>(Phase::FROZEN) ||
        report_.phase == static_cast<std::uint32_t>(Phase::FAILED);
}

void Runner::fail(Failure reason) {
    if (report_.failure != static_cast<std::uint32_t>(Failure::NONE)) return;
    report_.failure = static_cast<std::uint32_t>(reason);
    report_.phase = static_cast<std::uint32_t>(Phase::FAILED);
}

std::uint32_t Runner::observeClock(void* context) {
    auto& self = *static_cast<Runner*>(context);
    const auto now = self.clock_.now_us(self.clock_.context);
    const auto delta = now - self.latest_us_;
    if (!self.clock_seen_) self.report_.boot_us = now;
    else if (delta >= HALF_RANGE) self.fail(Failure::CLOCK);
    else if (delta != 0U) self.equal_observations_ = 0U;
    else {
        if (self.equal_observations_ < COUNTER_MAX) ++self.equal_observations_;
        if (self.equal_observations_ >= config::APP_CLOCK_STALL_MAX_POLLS)
            self.fail(Failure::CLOCK);
    }
    self.latest_us_ = now;
    self.clock_seen_ = true;
    self.report_.elapsed_us = now - self.report_.boot_us;
    if (self.report_.elapsed_us >= HALF_RANGE) self.fail(Failure::CLOCK);
    if (self.motor_.counters().saturated) self.fail(Failure::SATURATION);
    return now;
}

std::uint32_t Runner::clock() { return InertMotorPort::clockUs(&motor_); }

bool Runner::begin() {
    if (terminal()) return false;
    if (began_) { fail(Failure::REENTRY); refresh(); return false; }
    began_ = true;
    report_.phase = static_cast<std::uint32_t>(Phase::RUNNING);
    if (!clock_.now_us) { fail(Failure::CLOCK); refresh(); return false; }
    clock();
    if (!terminal() && !runtime_.begin(app::SetupGrants{})) fail(Failure::SETUP);
    refresh();
    if (motor_.counters().saturated) fail(Failure::SATURATION);
    else if (motor_.counters().fault) fail(Failure::PORT);
    return !terminal();
}

bool Runner::deadlines(std::uint32_t now_us) {
    const auto elapsed = now_us - report_.boot_us;
    if ((!epoch_seen_ && elapsed >= GRACE_US) || elapsed >= DEADLINE_US)
        fail(Failure::DEADLINE);
    return !terminal();
}

void Runner::refreshCounters() {
    const auto& counters = motor_.counters();
    report_.setup_enable_calls = counters.setup_enable;
    report_.setup_pwm_calls = counters.setup_pwm;
    report_.enable_low_calls = counters.enable_low;
    report_.pwm_zero_calls = counters.pwm_zero;
    report_.settle_calls = counters.settle;
    report_.clock_calls = counters.clock;
    report_.enabled_requests = counters.enabled;
    report_.nonzero_requests = counters.nonzero;
    report_.invalid_requests = counters.invalid;
}

void Runner::refresh() {
    const auto& owner = runtime_.report();
    const auto& tick = runtime_.transaction().report();
    const auto& recording = runtime_.transaction().recording();
    report_.runtime_phase = static_cast<std::uint32_t>(owner.phase);
    report_.runtime_fault = static_cast<std::uint32_t>(owner.fault);
    report_.epochs = owner.epochs;
    report_.missed_releases = owner.missed_releases;
    report_.maximum_execution_us = owner.maximum_execution_us;
    report_.transaction_phase = static_cast<std::uint32_t>(tick.phase);
    report_.transaction_fault = static_cast<std::uint32_t>(tick.fault);
    report_.last_s_us = tick.started_us;
    report_.last_d_us = tick.decision_us;
    report_.last_a_us = tick.applied.feedback.applied_us;
    report_.last_c_us = tick.completed_us;
    report_.token_lo = static_cast<std::uint32_t>(tick.robot.token);
    report_.token_hi = static_cast<std::uint32_t>(tick.robot.token >> 32U);
    report_.robot_state = static_cast<std::uint32_t>(tick.robot.outputs.ui_state);
    report_.contract_faults = tick.robot.contract_faults;
    report_.escape_fault = static_cast<std::uint32_t>(tick.robot.escape_fault);
    // An actual terminal halt is newer evidence than the preceding application.
    report_.gate_fault = static_cast<std::uint32_t>(
        tick.halt.fresh ? tick.halt.fault : tick.applied.fault);
    report_.receipt_flags = (tick.applied.consumed ? 1U : 0U) |
        (tick.applied.feedback.applied_valid ? 2U : 0U) |
        (inhibited(tick.robot.outputs) ? 4U : 0U) |
        (inhibited(tick.applied.feedback) ? 8U : 0U);
    report_.input_absent_mask = absentMask(runtime_.decisionInput());
    report_.initialization_complete = owner.initialization_complete ? 1U : 0U;
    report_.recorder_phase = static_cast<std::uint32_t>(recording.phase());
    report_.frame_count = static_cast<std::uint32_t>(recording.frames().size());
    report_.event_count = static_cast<std::uint32_t>(recording.events().size());
    refreshCounters();
}

void Runner::checkOwners() {
    const auto& owner = runtime_.report();
    const auto& tick = runtime_.transaction().report();
    const auto& recording = runtime_.transaction().recording();
    const auto& counters = motor_.counters();
    if (counters.saturated || owner.epochs == COUNTER_MAX ||
        owner.missed_releases == COUNTER_MAX || owner.service_passes == COUNTER_MAX)
        fail(Failure::SATURATION);
    if (counters.fault) fail(Failure::PORT);
    if (owner.missed_releases != 0U) fail(Failure::MISSED_RELEASE);
    if (owner.phase != app::RuntimePhase::RUNNING || owner.fault != app::RuntimeFault::NONE ||
        tick.fault != app::Fault::NONE || tick.robot.contract_faults != 0U ||
        tick.robot.escape_fault != edge::EscapeFault::NONE) fail(Failure::RUNTIME);
    if (recording.phase() != recorder::AttemptPhase::EMPTY || recording.frames().size() != 0U ||
        recording.events().size() != 0U || recording.summary().epoch_token != 0U ||
        recording.incomplete()) fail(Failure::RECORDER);
}

void Runner::checkEpoch(std::uint32_t previous_epochs) {
    const auto& owner = runtime_.report();
    const auto& tick = runtime_.transaction().report();
    if (!owner.fresh || !tick.finished || !tick.timing_valid || !tick.decision_made ||
        tick.phase != app::Phase::IDLE || owner.epochs != previous_epochs + 1U) {
        fail(Failure::RUNTIME);
        return;
    }
    const auto duration = tick.completed_us - tick.started_us;
    const auto decision = tick.decision_us - tick.started_us;
    const auto applied = tick.applied.feedback.applied_us - tick.started_us;
    if (duration >= HALF_RANGE || decision > applied || applied > duration ||
        tick.execution_us != duration || (epoch_seen_ &&
        tick.started_us - previous_c_us_ >= HALF_RANGE)) fail(Failure::CHRONOLOGY);
    if (!epoch_seen_) {
        report_.first_s_us = tick.started_us;
        report_.first_d_us = tick.decision_us;
        report_.first_c_us = tick.completed_us;
    }
    epoch_seen_ = true;
    previous_c_us_ = tick.completed_us;
    const auto& gate = tick.robot.lifecycle.gate;
    if (!tick.robot.fresh || tick.robot.token == 0U || tick.robot.token <= last_token_ ||
        tick.applied.feedback.token != tick.robot.token || report_.receipt_flags != 15U ||
        tick.applied.fault != motors::Fault::NONE) fail(Failure::RECEIPT);
    last_token_ = tick.robot.token;
    if (tick.robot.outputs.ui_state != core::State::BOOT || gate.phase != countdown::Phase::IDLE ||
        gate.start_release || gate.go || gate.motion_permitted || gate.release_us != 0U ||
        tick.robot.heading.match_started || tick.robot.frame_ready) fail(Failure::RUNTIME);
    if (report_.input_absent_mask != 31U || owner.initialization_complete ||
        runtime_.decisionInput().initialization_complete || !owner.raw_lines ||
        runtime_.decisionInput().stop_requested) fail(Failure::INPUTS);
    const auto expected = std::uint64_t(owner.epochs) + 1U;
    const auto& counts = motor_.counters();
    if (counts.setup_enable != 1U || counts.setup_pwm != 4U ||
        counts.enable_low != expected || counts.pwm_zero != 4U * expected ||
        counts.settle != expected) fail(Failure::PORT);
    const auto elapsed = tick.completed_us - report_.boot_us;
    if (elapsed >= DEADLINE_US) fail(Failure::DEADLINE);
    if (!terminal() && elapsed >= WINDOW_US && owner.epochs >= REQUIRED_EPOCHS)
        report_.phase = static_cast<std::uint32_t>(Phase::FROZEN);
}

void Runner::finishPoll(std::uint32_t started_us) {
    // Substantive owner checks/report preparation precede this closing sample.
    // Endpoint validation/counters/elapsed and duration assignment follow it;
    // these unavoidable endpoint operations and native publication are excluded.
    const auto ended_us = clock();
    refreshCounters();
    const auto duration = ended_us - started_us;
    if (duration >= HALF_RANGE) fail(Failure::CLOCK);
    else if (duration > report_.maximum_runner_us) report_.maximum_runner_us = duration;
}

void Runner::poll() {
    if (terminal()) return;
    if (!began_) { fail(Failure::REENTRY); refresh(); return; }
    const auto started_us = clock();
    if (!terminal() && deadlines(started_us)) {
        const auto epochs = runtime_.report().epochs;
        const bool completed = runtime_.step();
        refresh();
        checkOwners();
        if (completed) checkEpoch(epochs);
        else if (runtime_.report().fresh || runtime_.report().epochs != epochs)
            fail(Failure::RUNTIME);
    } else refresh();
    finishPoll(started_us);
}
} // namespace runtime_bench
