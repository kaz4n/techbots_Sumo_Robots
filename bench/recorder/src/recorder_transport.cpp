// Owns one bounded synthetic recorder experiment through actual transactions.
// Retains original timing and failures without fabricating application receipts.
// Independent D116 tests cover full-length transport and terminal behavior.
#include "recorder_transport.h"
#include <limits>

namespace recorder_transport {
Runner::Runner(const ClockPort& clock, const app::DumpPort& dump)
    : clock_(clock), dump_port_(dump), transaction_(motorPort(this)), transfer_(dump.output) {}

const Report& Runner::report() const { return report_; }
const app::Transaction& Runner::transaction() const { return transaction_; }
const recorder::AttemptRecorder& Runner::source() const { return transaction_.recording(); }
const recorder::dump::Report& Runner::dump() const { return transfer_.report(); }

void Runner::add(std::uint32_t& counter, std::uint64_t amount) {
    const auto remaining = std::numeric_limits<std::uint32_t>::max() - counter;
    if (amount > remaining) report_.counters_saturated = true;
    counter = recorder::saturatedAdd(counter, amount);
}

bool Runner::terminal() const {
    return report_.phase == Phase::DISABLED || report_.phase == Phase::FAILED ||
        report_.phase == Phase::SENT_UNCONFIRMED;
}

void Runner::fail(Failure failure) {
    if (terminal()) return;
    report_.failure = failure;
    report_.phase = Phase::FAILED;
    if (!initialized_) return;
    // Gate inhibition precedes any potentially active UART cancellation.
    transaction_.abort();
    transfer_.abort();
}

bool Runner::validConfig() const {
    const auto hold = (std::uint64_t{config::COUNTDOWN_MS} + config::COUNTDOWN_MARGIN_MS) * 1000U;
    return config::TICK_US > 0U && DEBOUNCE_US > 0U && LONG_US > 0U &&
        config::APP_CLOCK_STALL_MAX_POLLS > 0U && G_US < LONG_US &&
        RECORD_US >= hold && TOTAL_US < HALF_RANGE;
}

bool Runner::begin(bool enabled, const recorder::dump::SetupGrant& grants) {
    if (attempted_ || terminal()) return false;
    attempted_ = true;
    if (!enabled) { report_.phase = Phase::DISABLED; return false; }
    if (!clock_.now_us || !dump_port_.begin || !dump_port_.ready ||
        !dump_port_.output.write || !dump_port_.output.cancel) {
        fail(Failure::PORT);
        return false;
    }
    if (!recorder::dump::setupGrantAccepted(grants)) { fail(Failure::GRANT); return false; }
    if (!validConfig()) { fail(Failure::CONFIG); return false; }
    session_ = grants.session;
    initialized_ = true; // Cleanup is required after any initialization attempt.
    if (!ownerResult(transaction_.initialize())) return false;
    report_.dump_setup = dump_port_.begin(dump_port_.context, grants);
    if (report_.dump_setup != recorder::dump::NativeStatus::OK) {
        fail(Failure::DUMP_SETUP);
        return false;
    }
    std::uint32_t now = 0U;
    if (!sample(now)) { fail(Failure::CLOCK); return false; }
    report_.setup_completed = true;
    report_.setup_completed_us = previous_poll_us_ = now;
    report_.next_release_us = now + config::TICK_US;
    report_.phase = Phase::STARTING;
    return true;
}

bool Runner::sample(std::uint32_t& now) {
    now = clock_.now_us(clock_.context);
    const auto delta = now - last_clock_us_;
    if (clock_seen_ && delta >= HALF_RANGE) {
        clock_fault_ = true;
        return false;
    }
    if (clock_seen_ && report_.setup_completed) elapsed_us_ += delta;
    last_clock_us_ = now;
    clock_seen_ = true;
    return !clock_fault_;
}

std::uint32_t Runner::ownerClock(void* context) {
    auto& self = *static_cast<Runner*>(context);
    std::uint32_t actual = 0U;
    self.sample(actual); // Latch only: never recursively abort inside Gate's clock.
    return actual;
}

bool Runner::ownerResult(bool success) {
    if (clock_fault_ || transaction_.report().fault == app::Fault::CLOCK) {
        fail(Failure::CLOCK);
        return false;
    }
    if (!success) { fail(Failure::TRANSACTION); return false; }
    return true;
}

void Runner::poll() {
    if (terminal()) return;
    if (!attempted_) { fail(Failure::ORDER); return; }
    std::uint32_t now = 0U;
    const bool accepted = sample(now);
    report_.last_poll_us = now;
    if (!accepted) { fail(Failure::CLOCK); return; }
    if (now == previous_poll_us_) {
        if (equal_polls_ < std::numeric_limits<std::uint32_t>::max()) ++equal_polls_;
    } else equal_polls_ = 0U;
    previous_poll_us_ = now;
    if (equal_polls_ >= config::APP_CLOCK_STALL_MAX_POLLS) { fail(Failure::CLOCK); return; }
    if (elapsed_us_ >= TOTAL_US) { fail(Failure::DEADLINE); return; }
    const auto lateness = now - report_.next_release_us;
    if (lateness >= HALF_RANGE) return;
    if (lateness > report_.maximum_lateness_us) report_.maximum_lateness_us = lateness;
    if constexpr (config::TICK_US > 0U) {
        if (lateness >= config::TICK_US) {
            add(report_.missed_releases, lateness / config::TICK_US);
            fail(Failure::MISSED_RELEASE);
            return;
        }
    }
    report_.next_release_us += config::TICK_US;
    epoch();
}

void Runner::epoch() {
    if (!ownerResult(transaction_.open())) return;
    if (!applyReset()) return;
    const app::DecisionSource source{this, project, projectionClockAccepted};
    if (!ownerResult(transaction_.decideFrom(source))) return;
    if (scenario_fault_) { fail(Failure::SCENARIO); return; }
    if (!receiptValid()) { fail(Failure::TRANSACTION); return; }
    if (!observeDecision()) return;
    std::uint32_t after = 0U;
    if (!transfer(after)) return;
    if (!ownerResult(transaction_.finishAfter(after))) return;
    add(report_.epochs);
    const auto execution = transaction_.report().execution_us;
    if (execution > report_.maximum_execution_us) report_.maximum_execution_us = execution;
    // A real C, including a completed transfer, cannot waive this total deadline.
    if (elapsed_us_ >= TOTAL_US) { fail(Failure::DEADLINE); return; }
    closeEpoch();
}

void Runner::closeEpoch() {
    const auto& tick = transaction_.report();
    if (report_.phase == Phase::STOPPING && tick.robot.token > report_.stop_token) {
        if (!sealed()) { fail(Failure::RECORDING); return; }
        report_.phase = Phase::RESET_GESTURE;
        stage_ = Stage::RESET_NEUTRAL;
        stage_seen_ = false;
    }
    if (transfer_.report().phase == recorder::dump::Phase::SENT_UNCONFIRMED) {
        if (!report_.service_only || report_.request_token == 0U) {
            fail(Failure::SCENARIO);
            return;
        }
        report_.phase = Phase::SENT_UNCONFIRMED;
    }
}
} // namespace recorder_transport
