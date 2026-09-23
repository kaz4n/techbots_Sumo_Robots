// Runs bounded native source work inside actual Robot and MotorGate epochs.
// Keeps release-grid scheduling, exclusive charge service and cleanup truthful.
// Independent D096 source fixtures and native compilation verify this owner.
#include "runtime.h"
#include <limits>

namespace app {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
std::uint32_t added(std::uint32_t value, std::uint32_t delta) {
    const auto limit = std::numeric_limits<std::uint32_t>::max();
    return delta > limit - value ? limit : value + delta;
}
} // namespace

Runtime::Runtime(const motors::Port& motors, const power::InputPort& adc,
                 const SourcePort& sources, const DumpPort& dump)
    : motor_port_(motors), adc_port_(adc), source_(sources), dump_port_(dump),
      transaction_(motors), dump_(dump.output), adc_(adc) {}

bool Runtime::validPorts() const {
    if (grants_.adc_pair && (!adc_port_.beginWithButtons || !adc_port_.readA0 ||
        !adc_port_.readA1 || !adc_port_.clockUs)) return false;
    if (grants_.opponents && (!source_.beginOpponents || !source_.readOpponents)) return false;
    if (grants_.qtr_exclusive_pads && (!source_.beginLines || !source_.startLines ||
        !source_.advanceLines || !source_.cancelLines || !source_.lines)) return false;
    if (grants_.imu_enabled && (!source_.startImu || !source_.advanceImuSetup ||
        !source_.beginImu || !source_.advanceImu || !source_.cancelImu ||
        !source_.imuSetupFailure)) return false;
    return !grants_.matrix_enabled || (source_.beginMatrix && source_.submitMatrix);
}

bool Runtime::acceptClock(std::uint32_t now_us) {
    const auto elapsed = now_us - last_clock_us_;
    if (clock_seen_ && elapsed >= HALF_RANGE) return false;
    clock_equal_ = clock_seen_ && elapsed == 0U;
    if (!clock_equal_) idle_polls_ = 0U;
    last_clock_us_ = now_us;
    clock_seen_ = true;
    return true;
}

bool Runtime::clock(std::uint32_t& now_us) {
    now_us = motor_port_.clockUs(motor_port_.context);
    if (acceptClock(now_us)) return true;
    fail(RuntimeFault::CLOCK);
    return false;
}

bool Runtime::initializeSources() {
    std::uint32_t now = 0U;
    if (grants_.matrix_enabled)
        report_.matrix_status = source_.beginMatrix(source_.context, grants_.matrix);
    if (!clock(now)) return false;
    if (grants_.adc_pair) adc_.begin();
    if (!clock(now)) return false;
    if (grants_.opponents) report_.opponents_setup = source_.beginOpponents(source_.context);
    if (!clock(now)) return false;
    if (grants_.qtr_exclusive_pads) {
        report_.line_setup = source_.beginLines(source_.context, true);
        rememberLines(source_.lines(source_.context));
    }
    if (!clock(now)) return false;
    if (grants_.imu_enabled) {
        estimator_ready_ = estimator_.begin(grants_.mounting, 0.0F);
        imu_publication_ = estimator_.report();
        report_.imu_setup = source_.startImu(source_.context, now, grants_.imu_power_confirmed);
        if (!clock(now)) return false;
        setupImuFault(now);
    }
    return clock(now);
}

bool Runtime::begin(const SetupGrants& grants) {
    if (attempted_ || report_.phase == RuntimePhase::FAULT) return false;
    attempted_ = true;
    grants_ = grants;
    if (!transaction_.initialize()) { fail(RuntimeFault::TRANSACTION); return false; }
    if (!validPorts()) { fail(RuntimeFault::PORT); return false; }
    confirmed_bank_ = grants.default_line_thresholds_confirmed;
    report_.raw_lines = !confirmed_bank_;
    if (!initializeSources()) return false;
    initializeDump();
    std::uint32_t anchor = 0U;
    if (!clock(anchor)) return false;
    report_.next_release_us = anchor;
    report_.phase = RuntimePhase::RUNNING;
    return true;
}

bool Runtime::linesActive() const {
    return line_current_.phase == line_qtr::Phase::CHARGING ||
        line_current_.phase == line_qtr::Phase::DISCHARGING;
}

void Runtime::rememberLines(const line_qtr::Snapshot& snapshot) {
    line_current_ = snapshot;
    if (snapshot.phase != line_qtr::Phase::COMPLETE) return;
    if (!line_seen_ || snapshot.sequence != line_mailbox_.sequence ||
        snapshot.started_us != line_mailbox_.started_us ||
        snapshot.completed_us != line_mailbox_.completed_us) {
        line_new_ = true;
        line_expired_ = false;
    }
    line_mailbox_ = snapshot;
    line_seen_ = true;
}

void Runtime::publishImu(const imu::Sample& sample) {
    const auto estimate = estimator_.observe(sample);
    if (estimate.state == imu::HeadingState::FAULT || estimate.heading_updated ||
        !imu_publication_.heading_updated) {
        imu_publication_ = estimate;
        if (estimate.heading_updated) {
            imu_new_ = true;
            report_.imu_expired = false;
        }
    }
}

void Runtime::consumeImu(const imu::SampleProgress& progress) {
    imu_progress_ = progress;
    if (progress.completed) publishImu(progress.sample);
}

void Runtime::setupImuFault(std::uint32_t now_us) {
    if (!estimator_ready_ || setup_fault_observed_ ||
        report_.imu_setup.state != imu::SetupState::FAULT) return;
    setup_fault_observed_ = true;
    publishImu(source_.imuSetupFailure(source_.context, now_us));
}

bool Runtime::serviceImu() {
    if (!grants_.imu_enabled || sources_cancelled_) return true;
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    if (report_.imu_setup.state == imu::SetupState::IN_PROGRESS) {
        report_.imu_setup = source_.advanceImuSetup(source_.context, now);
        if (!clock(now)) return false;
        setupImuFault(now);
    } else if (report_.imu_setup.state == imu::SetupState::PROFILE_READY &&
        estimator_ready_ && estimator_.report().state != imu::HeadingState::FAULT &&
        imu_progress_.state != imu::AsyncState::FAULT) {
        consumeImu(source_.beginImu(source_.context, now));
    }
    return clock(now);
}

bool Runtime::countPass() {
    if (epoch_passes_ >= config::APP_SERVICE_MAX_PASSES) {
        fail(RuntimeFault::SERVICE_LIMIT);
        return false;
    }
    ++epoch_passes_;
    report_.service_passes = added(report_.service_passes, 1U);
    return true;
}

bool Runtime::releaseCharge() {
    for (std::uint32_t pass = 0U; pass < config::APP_SERVICE_MAX_PASSES; ++pass) {
        if (line_current_.phase != line_qtr::Phase::CHARGING) return true;
        if (!countPass()) return false;
        rememberLines(source_.advanceLines(source_.context));
        std::uint32_t now = 0U;
        if (!clock(now)) return false;
    }
    if (line_current_.phase != line_qtr::Phase::CHARGING) return true;
    fail(RuntimeFault::SERVICE_LIMIT);
    return false;
}

bool Runtime::linesUseful(std::uint32_t now_us) const {
    if (!linesActive()) return false;
    if (line_current_.phase == line_qtr::Phase::CHARGING ||
        imu_progress_.state == imu::AsyncState::PENDING) return true;
    if (now_us - pump_started_us_ >= config::APP_QTR_SERVICE_US) return false;
    if (report_.raw_lines) return true;
    const auto done = line_current_.low_mask | line_current_.timeout_mask;
    for (unsigned i = 0U; i < 4U; ++i)
        if ((done & (1U << i)) == 0U &&
            line_current_.pad[i].lower_us < calibration_.thresholds().white_us[i]) return true;
    return false;
}

bool Runtime::servicePass() {
    if (!countPass()) return false;
    const bool charging = line_current_.phase == line_qtr::Phase::CHARGING;
    if (linesActive()) rememberLines(source_.advanceLines(source_.context));
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    if (!charging && imu_progress_.state == imu::AsyncState::PENDING) {
        consumeImu(source_.advanceImu(source_.context, now));
        if (!clock(now)) return false;
    }
    return true;
}

bool Runtime::pump() {
    if (!clock(pump_started_us_)) return false;
    for (std::uint32_t pass = 0U; pass < config::APP_SERVICE_MAX_PASSES; ++pass) {
        std::uint32_t now = 0U;
        if (!clock(now)) return false;
        // A prior epoch's threshold crossing cannot substitute for this frame's
        // next real service: completion and native gap/deadline checks still matter.
        const bool first_line_service = pass == 0U && linesActive();
        if (!first_line_service && !linesUseful(now) &&
            imu_progress_.state != imu::AsyncState::PENDING) return true;
        if (!servicePass()) return false;
    }
    if (!linesUseful(last_clock_us_) && imu_progress_.state != imu::AsyncState::PENDING)
        return true;
    fail(RuntimeFault::SERVICE_LIMIT);
    return false;
}

bool Runtime::acquire() {
    if (!sources_cancelled_ && !releaseCharge()) return false;
    buttons_ = {};
    if (grants_.adc_pair) {
        buttons_ = adc_.readButtons(true);
        adc_.readBatteryIfDue(true);
    }
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    if (!sources_cancelled_) {
        if (!serviceImu()) return false;
        if (grants_.qtr_exclusive_pads && report_.line_setup == line_qtr::Status::OK &&
            line_current_.phase != line_qtr::Phase::FAULT) {
            rememberLines(source_.lines(source_.context));
            source_.startLines(source_.context);
            rememberLines(source_.lines(source_.context));
        }
        if (!clock(now) || !pump()) return false;
    }
    opponents_ = {};
    if (grants_.opponents) opponents_ = source_.readOpponents(source_.context);
    return clock(now);
}

void Runtime::cancelSources() {
    if (sources_cancelled_) return;
    sources_cancelled_ = true;
    if (grants_.qtr_exclusive_pads && linesActive())
        report_.line_shutdown = source_.cancelLines(source_.context);
    if (grants_.imu_enabled && imu_progress_.state == imu::AsyncState::PENDING)
        report_.imu_shutdown = source_.cancelImu(source_.context,
            motor_port_.clockUs(motor_port_.context));
    if (report_.calibration.phase == qtr_cal::Phase::WAITING ||
        report_.calibration.phase == qtr_cal::Phase::COLLECTING)
        report_.calibration_interrupted = true;
}

void Runtime::fail(RuntimeFault fault) {
    if (report_.phase == RuntimePhase::FAULT || report_.phase == RuntimePhase::STOPPED) return;
    transaction_.abort();
    report_.fault = fault;
    report_.phase = RuntimePhase::FAULT;
    report_.fresh = false;
    report_.service_reset_pending = false;
    reset_gesture_ = ResetGesture::DISARMED;
    dump_.abort();
    report_.dump = dump_.report();
    cancelSources();
}

void Runtime::abort() { fail(RuntimeFault::TRANSACTION); }

void Runtime::skipBefore(std::uint32_t completed_us) {
    const auto late = completed_us - report_.next_release_us;
    if (late == 0U || late >= HALF_RANGE) return;
    const auto skipped = 1U + (late - 1U) / config::TICK_US;
    report_.missed_releases = added(report_.missed_releases, skipped);
    report_.next_release_us += skipped * config::TICK_US;
}

bool Runtime::completeEpoch() {
    if (!transaction_.finishAfter(last_clock_us_)) {
        fail(transaction_.report().fault == Fault::CLOCK ?
            RuntimeFault::CLOCK : RuntimeFault::TRANSACTION);
        return false;
    }
    const auto& tick = transaction_.report();
    if (!acceptClock(tick.completed_us)) { fail(RuntimeFault::CLOCK); return false; }
    report_.epochs = added(report_.epochs, 1U);
    if (tick.execution_us > report_.maximum_execution_us)
        report_.maximum_execution_us = tick.execution_us;
    report_.fresh = true;
    idle_polls_ = 0U;
    skipBefore(tick.completed_us);
    if (report_.phase == RuntimePhase::STOP_OBSERVING) return true;
    if (stop_tail_) {
        const auto recording = transaction_.recording().phase();
        if (recording == recorder::AttemptPhase::RECORDING ||
            recording == recorder::AttemptPhase::DRAINING) {
            fail(RuntimeFault::TRANSACTION);
            return false;
        }
        if (grants_.local_service_reset && !report_.service_only) {
            if (recording != recorder::AttemptPhase::EMPTY &&
                recording != recorder::AttemptPhase::SEALED) {
                fail(RuntimeFault::TRANSACTION);
                return false;
            }
            stop_tail_ = false;
            report_.phase = RuntimePhase::STOP_OBSERVING;
        } else report_.phase = RuntimePhase::STOPPED;
    } else if (tick.robot.outputs.ui_state == core::State::STOPPED) stop_tail_ = true;
    return true;
}

bool Runtime::step() {
    report_.fresh = false;
    report_.service_reset_fresh = false;
    report_.service_action.fresh = false;
    if (report_.phase != RuntimePhase::RUNNING &&
        report_.phase != RuntimePhase::STOP_OBSERVING) return false;
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    const auto released = now - report_.next_release_us;
    if (released >= HALF_RANGE) {
        if (clock_equal_ && ++idle_polls_ >= config::APP_CLOCK_STALL_MAX_POLLS)
            fail(RuntimeFault::CLOCK);
        return false;
    }
    const auto missed = released / config::TICK_US;
    report_.missed_releases = added(report_.missed_releases, missed);
    report_.next_release_us += (missed + 1U) * config::TICK_US;
    if (!transaction_.open()) { fail(RuntimeFault::TRANSACTION); return false; }
    if (!acceptClock(transaction_.report().started_us)) { fail(RuntimeFault::CLOCK); return false; }
    if (!applyServiceReset()) return false;
    epoch_passes_ = 0U;
    selectLineMode();
    if (!acquire()) return false;
    const DecisionSource projection{this, projectThunk, clockAcceptedThunk};
    if (!transaction_.decideFrom(projection)) {
        fail(projection_failed_ ? RuntimeFault::CLOCK : RuntimeFault::TRANSACTION);
        return false;
    }
    if (projection_failed_) { fail(RuntimeFault::PROJECTION); return false; }
    if (!admitApplication()) return false;
    if (!postDecision()) return false;
    return completeEpoch();
}
} // namespace app
