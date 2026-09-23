// Captures finite A1 raw evidence and the existing decoder's unchanged diagnostics.
// Separates source admission, decoder provenance and immutable publication without ADC cleanup.
// Independent D112 cadence, chronology, decoder and capture tests exercise this owner.
#include "ui_bench.h"
#include <limits>

namespace ui_bench {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
bool configValid() {
    return config::UI_BENCH_SAMPLES > 0U && config::VBAT_ADC_CONVERSION_US > 0U &&
        config::VBAT_ADC_CONVERSION_US <= config::TICK_US && config::TICK_US < HALF_RANGE;
}
bool known(power::Status status, power::Shutdown shutdown) {
    return static_cast<std::uint8_t>(status) <= static_cast<std::uint8_t>(power::Status::NOT_ENABLED) &&
        static_cast<std::uint8_t>(shutdown) <= static_cast<std::uint8_t>(power::Shutdown::UNCONFIRMED);
}
std::uint32_t missedAt(std::uint32_t age_us) {
    if constexpr (config::TICK_US > 0U) return age_us / config::TICK_US - 1U;
    // Invalid configuration cannot reach a read; no fallback period is substituted.
    return 0U;
}
} // namespace

Runner::Runner(const Port& port) : port_(port) {}
const Report& Runner::report() const { return report_; }
std::uint32_t Runner::captureCapacity() const { return config::UI_BENCH_SAMPLES; }
std::uint32_t Runner::captureCount() const { return report_.captured_samples; }
const Capture* Runner::capture(std::uint32_t index) const {
    return index < report_.captured_samples ? &captures_[index] : nullptr;
}
bool Runner::portsValid() const {
    return port_.clockUs && port_.beginButtons && port_.readButtons;
}
void Runner::fail(Fault fault) {
    if (report_.fault == Fault::NONE) report_.fault = fault;
    report_.phase = Phase::FAULT;
    report_.fresh = false;
}
void Runner::add(std::uint32_t& counter, std::uint32_t amount) {
    const auto remaining = std::numeric_limits<std::uint32_t>::max() - counter;
    if (amount > remaining) {
        counter = std::numeric_limits<std::uint32_t>::max();
        report_.counter_saturated = true;
    } else counter += amount;
}
void Runner::attempt(Timing& timing) {
    timing.last_valid = false;
    add(timing.calls);
}
void Runner::measure(Timing& timing, std::uint32_t elapsed_us) {
    add(timing.measured_calls);
    timing.last_us = elapsed_us;
    if (elapsed_us > timing.maximum_us) timing.maximum_us = elapsed_us;
    timing.last_valid = true;
}
bool Runner::admitClock(std::uint32_t now_us) {
    const auto elapsed = clock_seen_ ? now_us - last_clock_us_ : 0U;
    if (elapsed >= HALF_RANGE ||
        (interval_active_ && elapsed >= HALF_RANGE - interval_elapsed_us_) ||
        (source_seen_ && elapsed >= HALF_RANGE - source_age_us_)) {
        report_.clock_fault = true;
        fail(Fault::CLOCK);
        return false;
    }
    if (interval_active_) interval_elapsed_us_ += elapsed;
    if (source_seen_) source_age_us_ += elapsed;
    last_clock_us_ = now_us;
    clock_seen_ = true;
    return true;
}
bool Runner::clock(std::uint32_t& now_us) {
    if (report_.clock_fault) return false;
    now_us = port_.clockUs(port_.context);
    return admitClock(now_us);
}
bool Runner::close(std::uint32_t started_us, Timing& timing, std::uint32_t& closed_us) {
    const bool accepted = clock(closed_us);
    interval_active_ = false;
    if (accepted) measure(timing, closed_us - started_us);
    return accepted && report_.fault == Fault::NONE;
}
void Runner::examineSetup() {
    const auto& setup = report_.setup;
    if (!known(setup.status, setup.shutdown)) fail(Fault::CONTRACT);
    else if (setup.status != power::Status::OK) fail(Fault::SETUP);
    else if (!setup.ready || setup.shutdown != power::Shutdown::NOT_ATTEMPTED)
        fail(Fault::CONTRACT);
}
void Runner::examineSample() {
    const auto& sample = report_.sample;
    if (!known(sample.status, sample.shutdown) || sample.valid != (sample.status == power::Status::OK) ||
        (sample.status != power::Status::OK && (sample.raw != 0U || sample.sequence != 0U))) {
        fail(Fault::CONTRACT);
        return;
    }
    if (sample.status != power::Status::OK) { fail(Fault::ADC); return; }
    if (sample.shutdown != power::Shutdown::NOT_ATTEMPTED || sample.raw > 16383U)
        fail(Fault::CONTRACT);
}
void Runner::examineSource(std::uint32_t started_us, std::uint32_t returned_us) {
    const auto& sample = report_.sample;
    const auto source_start = sample.started_us - started_us;
    const auto source_end = sample.completed_us - started_us;
    const auto expected = source_seen_ ? captures_[report_.captured_samples - 1U].sample.sequence + 1U : 1U;
    if (source_start > source_end || source_end > returned_us - started_us ||
        sample.completed_us - sample.started_us >= config::VBAT_ADC_CONVERSION_US ||
        sample.sequence != expected) fail(Fault::SOURCE_ORDER);
}
bool Runner::begin(const Grants& grants) {
    if (attempted_) return false;
    attempted_ = true;
    if (!grants.exclusive_adc) { report_.phase = Phase::DISABLED; return true; }
    if (!portsValid()) { fail(Fault::PORT); return false; }
    if (!configValid()) { fail(Fault::CONFIG); return false; }
    std::uint32_t started = 0U, closed = 0U;
    if (!clock(started)) return false;
    interval_active_ = true;
    interval_elapsed_us_ = 0U;
    attempt(report_.setup_timing);
    report_.setup = port_.beginButtons(port_.context);
    const auto returned = port_.clockUs(port_.context);
    examineSetup();
    admitClock(returned);
    if (!close(started, report_.setup_timing, closed)) return false;
    report_.phase = Phase::RUNNING;
    return true;
}
void Runner::stage(std::uint32_t started_us, std::uint32_t returned_us, std::uint32_t missed) {
    auto& record = captures_[report_.captured_samples];
    record.sample = report_.sample;
    record.decoded = report_.decoded;
    record.call_started_us = started_us;
    record.call_returned_us = returned_us;
    record.source_us = report_.sample.completed_us - report_.sample.started_us;
    record.read_us = returned_us - started_us;
    record.missed_before = missed;
}
void Runner::publish(std::uint32_t closed_us) {
    auto& record = captures_[report_.captured_samples];
    record.poll_closed_us = closed_us;
    record.poll_us = closed_us - record.call_started_us;
    source_age_us_ = closed_us - record.sample.started_us;
    source_seen_ = true;
    ++report_.captured_samples;
    report_.last_read_accepted = true;
    report_.fresh = true;
    if (report_.captured_samples == config::UI_BENCH_SAMPLES) report_.phase = Phase::COMPLETE;
}
bool Runner::read(std::uint32_t started_us, std::uint32_t missed) {
    interval_active_ = true;
    interval_elapsed_us_ = 0U;
    add(report_.missed_releases, missed);
    attempt(report_.read_timing);
    report_.last_read_accepted = false;
    report_.decode_matches_sample = false;
    report_.sample = port_.readButtons(port_.context);
    const auto returned = port_.clockUs(port_.context);
    report_.sample_seen = true;
    examineSample();
    if (admitClock(returned)) {
        measure(report_.read_timing, returned - started_us);
        report_.decoded = ui::decodeButtons(report_.sample);
        report_.decode_matches_sample = true;
        if (report_.fault == Fault::NONE) examineSource(started_us, returned);
    }
    if (report_.fault == Fault::NONE) stage(started_us, returned, missed);
    std::uint32_t closed = 0U;
    if (!close(started_us, report_.poll_timing, closed)) return false;
    publish(closed);
    return true;
}
bool Runner::poll() {
    report_.fresh = false;
    if (report_.phase != Phase::RUNNING) return false;
    attempt(report_.poll_timing);
    std::uint32_t started = 0U;
    if (!clock(started)) return false;
    if (source_seen_ && source_age_us_ < config::TICK_US) {
        add(report_.not_due);
        return false;
    }
    const auto missed = source_seen_ ? missedAt(source_age_us_) : 0U;
    return read(started, missed);
}
} // namespace ui_bench
