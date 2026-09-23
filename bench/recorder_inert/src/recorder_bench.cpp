// Runs one clock-paced synthetic attempt through the real core, gate and recorder.
// Collects bounded retention and timing evidence while rejecting every active output.
// Independent host contract tests and a separately reviewed inert target exercise it.
#include "recorder_bench.h"
#include "config.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Recorder bench must remain inert");

namespace recorder_bench {
namespace {
constexpr std::uint32_t START_STAGE_US = config::BTN_DEBOUNCE_MS * 1000U +
                                          4U * config::TICK_US;
constexpr std::uint32_t DEADLINE_US = config::BTN_LONG_MS * 1000U;
constexpr std::uint64_t RECORD_US = static_cast<std::uint64_t>(
    config::LOG_FRAME_WINDOW_MS) * 1000U;
static_assert(config::TICK_US > 0U && START_STAGE_US < 0x80000000U);
static_assert(DEADLINE_US > START_STAGE_US && DEADLINE_US < 0x80000000U);

std::uint32_t low(std::uint64_t value) { return static_cast<std::uint32_t>(value); }
std::uint32_t high(std::uint64_t value) { return static_cast<std::uint32_t>(value >> 32U); }
void increment(std::uint32_t& value) { value = logframe::saturatingIncrement(value); }
} // namespace

Runner::Runner(const ClockPort& clock) : clock_(clock), gate_(motorPort(this)) {
    report_.schema_version = 1U;
    report_.byte_size = sizeof(Report);
    report_.phase = static_cast<std::uint32_t>(Phase::BOOT);
}

motors::Port Runner::motorPort(Runner* runner) {
    // One is an inert integer representation; no timer or physical PWM exists.
    return {runner, configureEnable, configurePwm, writeEnable, writePwm,
            settle, gateClock, {1U, 1U, 1U, 1U}};
}

bool Runner::configureEnable(void* context) {
    auto& runner = *static_cast<Runner*>(context);
    increment(runner.report_.configure_calls);
    return true;
}

bool Runner::configurePwm(void* context, motors::Channel channel) {
    auto& runner = *static_cast<Runner*>(context);
    increment(runner.report_.configure_calls);
    return static_cast<std::uint8_t>(channel) < 4U;
}

bool Runner::writeEnable(void* context, bool enabled) {
    auto& runner = *static_cast<Runner*>(context);
    if (enabled) increment(runner.report_.enabled_en);
    return !enabled;
}

bool Runner::writePwm(void* context, motors::Channel channel,
                      std::uint32_t period, std::uint32_t pulse) {
    auto& runner = *static_cast<Runner*>(context);
    if (pulse != 0U) increment(runner.report_.nonzero_pwm);
    return pulse == 0U && period == 1U && static_cast<std::uint8_t>(channel) < 4U;
}

bool Runner::settle(void*) { return true; }

std::uint32_t Runner::gateClock(void* context) {
    auto& runner = *static_cast<Runner*>(context);
    std::uint32_t now = runner.latest_us_;
    runner.sampleClock(now);
    return now;
}

bool Runner::begin() {
    if (began_ || terminal()) { fail(Failure::REENTRY); return false; }
    began_ = true;
    if (clock_.now_us == nullptr) { fail(Failure::CLOCK); return false; }
    std::uint32_t now = 0U;
    if (!sampleClock(now)) return false;
    report_.boot_us = scheduled_us_ = now;
    if (!gate_.begin()) { fail(Failure::GATE); return false; }
    if (terminal()) return false;
    report_.phase = static_cast<std::uint32_t>(Phase::RUNNING);
    refresh();
    return true;
}

bool Runner::terminal() const {
    return report_.phase == static_cast<std::uint32_t>(Phase::FROZEN) ||
           report_.phase == static_cast<std::uint32_t>(Phase::FAILED);
}

bool Runner::sampleClock(std::uint32_t& now) {
    if (clock_.now_us == nullptr) { fail(Failure::CLOCK); return false; }
    const auto sampled = clock_.now_us(clock_.context);
    const auto delta = static_cast<std::uint32_t>(sampled - latest_us_);
    if (have_clock_ && delta >= 0x80000000U) { fail(Failure::CLOCK); return false; }
    if (have_clock_ && released_) release_age_us_ += delta;
    now = latest_us_ = sampled;
    have_clock_ = true;
    report_.last_us = now;
    report_.elapsed_us = recorder::saturatedAdd(0U, release_age_us_);
    return true;
}

void Runner::fail(Failure reason) {
    if (report_.phase == static_cast<std::uint32_t>(Phase::FAILED)) return;
    report_.phase = static_cast<std::uint32_t>(Phase::FAILED);
    report_.failure = static_cast<std::uint32_t>(reason);
    refresh();
}

bool Runner::deadlines(std::uint32_t now) {
    if (!released_ && button_stage_ == 2U &&
        static_cast<std::uint32_t>(now - stage_started_us_) >= DEADLINE_US) {
        fail(Failure::START_TIMEOUT);
        return false;
    }
    if (report_.phase == static_cast<std::uint32_t>(Phase::FINALIZING) &&
        static_cast<std::uint32_t>(now - report_.stop_us) >= DEADLINE_US) {
        fail(Failure::SEAL_TIMEOUT);
        return false;
    }
    return true;
}

void Runner::poll() {
    if (terminal()) return;
    if (!began_) { fail(Failure::REENTRY); return; }
    const auto preceding = latest_us_;
    std::uint32_t now = 0U;
    if (!sampleClock(now) || now == preceding) return;
    if (report_.phase == static_cast<std::uint32_t>(Phase::CHECKSUM)) {
        checksum();
        return;
    }
    if (!deadlines(now)) return;
    const auto elapsed = static_cast<std::uint32_t>(now - scheduled_us_);
    if (elapsed >= 0x80000000U) { fail(Failure::CLOCK); return; }
    if (elapsed < config::TICK_US) return;
    const auto slots = elapsed / config::TICK_US;
    const auto lateness = elapsed - config::TICK_US;
    report_.missed_slots = recorder::saturatedAdd(report_.missed_slots, slots - 1U);
    if (lateness > report_.max_lateness_us) report_.max_lateness_us = lateness;
    scheduled_us_ += slots * config::TICK_US;
    tick(now);
}

core::ButtonLevel Runner::button(std::uint32_t now) {
    if (!stage_observed_) {
        stage_started_us_ = now;
        stage_observed_ = true;
    } else if (button_stage_ < 2U &&
               static_cast<std::uint32_t>(now - stage_started_us_) >= START_STAGE_US) {
        ++button_stage_;
        stage_started_us_ = now;
    }
    return button_stage_ == 1U ? core::ButtonLevel::START : core::ButtonLevel::NONE;
}

fsm::RobotInput Runner::input(std::uint32_t now) {
    fsm::RobotInput value;
    value.t_us = now;
    value.initialization_complete = true;
    value.observations_fresh = true;
    for (auto& raw : value.line_raw_us) raw = config::QTR_TIMEOUT_US;
    value.opp_raw_mask = static_cast<std::uint8_t>(config::OPP_ACTIVE_LOW_MASK ^
                                                  (go_seen_ ? 2U : 0U));
    value.vbat_v = config::V_NOM_V;
    value.vbat_valid = true;
    value.imu.explicit_values = true; // ABSENT values are explicit, never live I/O.
    value.imu.checked_us = now;
    value.button = button(now);
    value.stop_requested = report_.phase == static_cast<std::uint32_t>(Phase::FINALIZING);
    value.previous = previous_;
    return value;
}

bool Runner::observe(const fsm::RobotResult& result, const motors::Result& applied) {
    report_.robot_faults = result.contract_faults;
    report_.gate_fault = static_cast<std::uint32_t>(applied.fault);
    if (!result.fresh || result.token == 0U || result.contract_faults != 0U ||
        result.escape_fault != edge::EscapeFault::NONE ||
        (result.outputs.ui_state == core::State::STOPPED &&
         report_.phase != static_cast<std::uint32_t>(Phase::FINALIZING))) {
        fail(Failure::ROBOT);
        return false;
    }
    if (!applied.consumed || !applied.feedback.applied_valid ||
        (applied.fault != motors::Fault::NONE && applied.fault != motors::Fault::STOPPED) ||
        report_.nonzero_pwm != 0U || report_.enabled_en != 0U) {
        fail(Failure::GATE);
        return false;
    }
    if (result.lifecycle.gate.start_release) {
        if (released_ || button_stage_ != 2U || source_.phase() != recorder::AttemptPhase::RECORDING) {
            fail(Failure::RECORDER);
            return false;
        }
        released_ = true;
        report_.release_us = result.lifecycle.gate.release_us;
        release_age_us_ = static_cast<std::uint32_t>(latest_us_ - report_.release_us);
        report_.elapsed_us = recorder::saturatedAdd(0U, release_age_us_);
    }
    go_seen_ = go_seen_ || result.lifecycle.gate.go;
    if (source_.phase() == recorder::AttemptPhase::INTERRUPTED ||
        (released_ && source_.phase() == recorder::AttemptPhase::EMPTY)) {
        fail(Failure::RECORDER);
        return false;
    }
    return true;
}

void Runner::tick(std::uint32_t now) {
    if (released_ && release_age_us_ >= RECORD_US &&
        report_.phase == static_cast<std::uint32_t>(Phase::RUNNING)) {
        report_.phase = static_cast<std::uint32_t>(Phase::FINALIZING);
        report_.stop_us = now;
    }
    const auto result = robot_.step(input(now));
    increment(report_.ticks);
    const auto applied = gate_.apply(now, result);
    if (terminal()) return; // A malformed clock observed inside Gate already froze us.
    source_.consume(result);
    if (!observe(result, applied)) return;
    previous_ = applied.feedback;
    refresh();
    std::uint32_t completed = now;
    if (!sampleClock(completed)) return;
    if (static_cast<std::uint32_t>(completed - now) >= 0x80000000U) {
        fail(Failure::CLOCK);
        return;
    }
    previous_.duration_valid = true;
    previous_.completed_us = completed;
    previous_.execution_us = static_cast<std::uint32_t>(completed - now);
    if (previous_.execution_us > report_.max_step_us)
        report_.max_step_us = previous_.execution_us;
    if (source_.phase() == recorder::AttemptPhase::SEALED) {
        if (report_.phase != static_cast<std::uint32_t>(Phase::FINALIZING)) {
            fail(Failure::RECORDER);
            return;
        }
        if (static_cast<std::uint32_t>(completed - report_.stop_us) >= DEADLINE_US) {
            fail(Failure::SEAL_TIMEOUT);
            return;
        }
        report_.phase = static_cast<std::uint32_t>(Phase::CHECKSUM);
    }
}

void Runner::refresh() {
    const auto& summary = source_.summary();
    report_.source_phase = static_cast<std::uint32_t>(source_.phase());
    report_.frame_count = static_cast<std::uint32_t>(source_.frames().size());
    report_.event_count = static_cast<std::uint32_t>(source_.events().size());
    report_.epoch_lo = low(summary.epoch_token);
    report_.epoch_hi = high(summary.epoch_token);
    report_.last_frame_lo = low(summary.last_frame_token);
    report_.last_frame_hi = high(summary.last_frame_token);
    report_.mode = static_cast<std::uint32_t>(summary.mode);
    report_.observed_results = summary.observed_results;
    report_.missing_results = summary.missing_results;
    report_.rejected_results = summary.rejected_results;
    report_.identity_rejected = summary.identity_rejected;
    report_.malformed_batches = summary.malformed_batches;
    report_.event_semantic_rejected = summary.event_semantic_rejected;
    report_.upstream_event_rejected = summary.upstream_event_rejected;
    report_.upstream_event_invalid = summary.upstream_event_invalid;
    report_.source_regressions = summary.source_regressions;
    report_.skipped_frames = summary.skipped_frames;
    report_.timing_ticks_lo = low(summary.ticks.ticks);
    report_.timing_ticks_hi = high(summary.ticks.ticks);
    report_.timing_overruns_lo = low(summary.ticks.overruns);
    report_.timing_overruns_hi = high(summary.ticks.overruns);
    report_.timing_max_us = summary.ticks.max_us;
    report_.timing_saturated = summary.ticks.saturated;
    report_.gate_fault = static_cast<std::uint32_t>(gate_.fault());
    refreshLoss();
}

void Runner::refreshLoss() {
    const auto& summary = source_.summary();
    report_.upstream_event_overflow = summary.upstream_event_overflow;
    report_.timing_incomplete = summary.timing_incomplete;
    report_.recording_incomplete = summary.recording_incomplete;
    report_.go_seen = summary.go_seen;
    report_.final_frame_missing = summary.final_frame_missing;
    report_.interrupted = summary.interrupted;
    report_.terminal_exhausted = summary.terminal_exhausted;
    report_.frame_overwritten = source_.frames().overwrittenCount();
    report_.frame_rejected_status = source_.frames().rejectedStatusCount();
    report_.frame_clamped = source_.frames().clampedCount();
    report_.frame_invalid = source_.frames().invalidCount();
    report_.event_overflow = source_.events().overflowed();
    report_.event_rejected = source_.events().rejectedCount();
    report_.incomplete = source_.incomplete();
}

void Runner::checksumBytes(const std::uint8_t* bytes, std::size_t size) {
    for (std::size_t i = 0U; i < size; ++i) {
        crc_ ^= bytes[i];
        for (unsigned bit = 0U; bit < 8U; ++bit)
            crc_ = (crc_ >> 1U) ^ ((crc_ & 1U) != 0U ? 0xEDB88320U : 0U);
    }
}

void Runner::checksum() {
    if (source_.phase() != recorder::AttemptPhase::SEALED) { fail(Failure::CHECKSUM); return; }
    if (checksum_index_ < source_.frames().size()) {
        recorder::StoredFrame row;
        if (!source_.frames().read(checksum_index_, row)) { fail(Failure::CHECKSUM); return; }
        checksumBytes(row.bytes.data, logframe::FRAME_BYTES);
        const auto status = static_cast<std::uint8_t>(row.status);
        checksumBytes(&status, 1U);
    } else if (checksum_index_ < source_.frames().size() + source_.events().size()) {
        const auto* row = source_.events().at(checksum_index_ - source_.frames().size());
        if (row == nullptr) { fail(Failure::CHECKSUM); return; }
        checksumBytes(row->data, logframe::EVENT_BYTES);
    } else {
        report_.crc32 = crc_ ^ 0xFFFFFFFFU;
        report_.phase = static_cast<std::uint32_t>(Phase::FROZEN);
        return;
    }
    ++checksum_index_;
    increment(report_.checksum_rows);
    if (checksum_index_ == source_.frames().size() + source_.events().size()) {
        report_.crc32 = crc_ ^ 0xFFFFFFFFU;
        report_.phase = static_cast<std::uint32_t>(Phase::FROZEN);
    }
}

const Report& Runner::report() const { return report_; }
const recorder::AttemptRecorder& Runner::source() const { return source_; }
} // namespace recorder_bench
