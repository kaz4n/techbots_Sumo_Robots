// Retains the first configured complete QTR frames through bounded cooperative calls.
// Separates raw evidence, wrapper chronology and one-shot cleanup without classifying color.
// Independent D109 lifecycle, timing, immutable-capture and native-binding tests cover this path.
#include "qtr_raw.h"
#include "config.h"
#include <limits>

namespace qtr_raw {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
bool active(line_qtr::Phase phase) {
    return phase == line_qtr::Phase::CHARGING || phase == line_qtr::Phase::DISCHARGING;
}
bool inside(std::uint32_t time, std::uint32_t before, std::uint32_t after) {
    return time - before <= after - before;
}
bool sameIdentity(const line_qtr::Snapshot& a, const line_qtr::Snapshot& b) {
    return a.sequence == b.sequence && a.started_us == b.started_us &&
        a.drive_completed_us == b.drive_completed_us;
}
bool samePad(const line_qtr::Pad& a, const line_qtr::Pad& b) {
    return a.release_before_us == b.release_before_us && a.release_after_us == b.release_after_us &&
        a.last_high_before_us == b.last_high_before_us && a.first_low_after_us == b.first_low_after_us &&
        a.lower_us == b.lower_us && a.upper_us == b.upper_us;
}
bool sameCleanup(const line_qtr::Cleanup& a, const line_qtr::Cleanup& b) {
    if (a.attempted_mask != b.attempted_mask || a.failed_mask != b.failed_mask ||
        a.skipped_mask != b.skipped_mask || a.nonneutral_mask != b.nonneutral_mask ||
        a.started_us != b.started_us || a.completed_us != b.completed_us ||
        a.deadline_exceeded != b.deadline_exceeded) return false;
    for (unsigned i = 0U; i < 4U; ++i) if (a.status[i] != b.status[i]) return false;
    return true;
}
bool sameSnapshot(const line_qtr::Snapshot& a, const line_qtr::Snapshot& b) {
    if (!sameIdentity(a, b) || a.phase != b.phase || a.status != b.status || a.valid != b.valid ||
        a.checked_us != b.checked_us || a.completed_us != b.completed_us ||
        a.advances != b.advances || a.max_service_gap_us != b.max_service_gap_us ||
        a.released_mask != b.released_mask || a.high_mask != b.high_mask ||
        a.low_mask != b.low_mask || a.timeout_mask != b.timeout_mask ||
        !sameCleanup(a.cleanup, b.cleanup)) return false;
    for (unsigned i = 0U; i < 4U; ++i)
        if (a.status_by_pad[i] != b.status_by_pad[i] || !samePad(a.pad[i], b.pad[i])) return false;
    return true;
}
bool cleanupSuccessful(const line_qtr::Cleanup& cleanup) {
    if (cleanup.attempted_mask != 0x0FU || cleanup.failed_mask != 0U ||
        cleanup.skipped_mask != 0U || cleanup.nonneutral_mask != 0U ||
        cleanup.deadline_exceeded) return false;
    for (const auto status : cleanup.status) if (status != 0) return false;
    return true;
}
} // namespace

Runner::Runner(const Port& port) : port_(port) {}
const Report& Runner::report() const { return report_; }
std::uint32_t Runner::captureCapacity() const { return config::QTR_BENCH_FRAMES; }
std::uint32_t Runner::captureCount() const { return report_.captured_frames; }
const line_qtr::Snapshot* Runner::capture(std::uint32_t index) const {
    return index < report_.captured_frames ? &frames_[index] : nullptr;
}
bool Runner::portsValid() const {
    return port_.clockUs && port_.begin && port_.start && port_.report &&
        port_.advance && port_.cancel;
}
void Runner::fail(Fault fault) {
    if (report_.fault == Fault::NONE) report_.fault = fault;
    report_.phase = Phase::FAULT;
    report_.fresh = false;
}
void Runner::add(std::uint32_t& counter) {
    if (counter == std::numeric_limits<std::uint32_t>::max()) report_.counter_saturated = true;
    else ++counter;
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
bool Runner::open(std::uint32_t& started_us) {
    if (!clock(started_us)) return false;
    interval_elapsed_us_ = 0U;
    interval_active_ = true;
    return true;
}
bool Runner::close(std::uint32_t started_us, Timing& timing) {
    if (report_.fault != Fault::NONE) cancelOnce();
    std::uint32_t completed = 0U;
    const bool accepted = clock(completed);
    if (!accepted) cancelOnce();
    interval_active_ = false;
    if (accepted) measure(timing, completed - started_us);
    return accepted && report_.fault == Fault::NONE;
}

void Runner::invoke(Command command) {
    possibly_active_ = true;
    if (command == Command::BEGIN) {
        attempt(report_.setup);
        report_.setup_status = port_.begin(port_.context, true);
        report_.snapshot = port_.report(port_.context);
    } else if (command == Command::START) {
        attempt(report_.start);
        report_.start_status = port_.start(port_.context);
        if (report_.start_status == line_qtr::Status::NOT_DUE) add(report_.not_due);
        report_.snapshot = port_.report(port_.context);
    } else {
        attempt(report_.advance);
        report_.snapshot = port_.advance(port_.context);
    }
}
void Runner::examineStart(const line_qtr::Snapshot& previous,
                          std::uint32_t source_age_at_start) {
    const auto& current = report_.snapshot;
    if (report_.start_status == line_qtr::Status::NOT_DUE) {
        if (!source_seen_ || source_age_at_start >= config::QTR_START_PERIOD_US ||
            current.phase != previous.phase) { fail(Fault::CONTRACT); return; }
        if (!sameIdentity(current, previous) || current.completed_us != previous.completed_us ||
            current.advances != previous.advances) { fail(Fault::SOURCE_ORDER); return; }
        if (!sameSnapshot(current, previous)) fail(Fault::CONTRACT);
        return;
    }
    if (report_.start_status != line_qtr::Status::OK ||
        current.phase != line_qtr::Phase::CHARGING) { fail(Fault::CONTRACT); return; }
    const auto expected = source_seen_ ? previous.sequence + 1U : 1U;
    if (current.sequence != expected || current.advances != 0U) fail(Fault::SOURCE_ORDER);
}
void Runner::examineAdvance(const line_qtr::Snapshot& previous) {
    const auto& current = report_.snapshot;
    const bool allowed = current.phase == line_qtr::Phase::DISCHARGING ||
        current.phase == line_qtr::Phase::COMPLETE ||
        (previous.phase == line_qtr::Phase::CHARGING && current.phase == line_qtr::Phase::CHARGING);
    if (!allowed) { fail(Fault::CONTRACT); return; }
    if (!sameIdentity(current, previous) || current.advances != previous.advances + 1U)
        fail(Fault::SOURCE_ORDER);
}
void Runner::examine(Command command, const line_qtr::Snapshot& previous,
                     std::uint32_t source_age_at_start) {
    report_.qualification = line_qtr::validateRaw(report_.snapshot);
    if (report_.qualification == line_qtr::RawQualification::INVALID) {
        fail(Fault::CONTRACT);
        return;
    }
    if (report_.qualification == line_qtr::RawQualification::PROVIDER_FAULT) {
        possibly_active_ = false;
        fail(Fault::PROVIDER);
        return;
    }
    if (command == Command::BEGIN) {
        if (report_.setup_status != line_qtr::Status::OK ||
            report_.snapshot.phase != line_qtr::Phase::IDLE) fail(Fault::CONTRACT);
    } else if (command == Command::START) examineStart(previous, source_age_at_start);
    else examineAdvance(previous);
}
void Runner::startSource(const line_qtr::Snapshot& previous, std::uint32_t after_us) {
    const auto age = after_us - report_.snapshot.started_us;
    if (source_seen_) {
        if (age > source_age_us_) { fail(Fault::SOURCE_ORDER); return; }
        const auto spacing = source_age_us_ - age;
        if (spacing < config::QTR_START_PERIOD_US ||
            spacing < previous.completed_us - previous.started_us) {
            fail(Fault::SOURCE_ORDER);
            return;
        }
    }
    source_seen_ = true;
    source_age_us_ = age;
}
void Runner::sourceBracket(Command command, const line_qtr::Snapshot& previous,
                           std::uint32_t started_us, std::uint32_t after_us) {
    const auto& current = report_.snapshot;
    if (command == Command::START && report_.start_status == line_qtr::Status::NOT_DUE) {
        possibly_active_ = false;
        return;
    }
    if (!inside(current.checked_us, started_us, after_us)) {
        fail(Fault::SOURCE_ORDER);
        return;
    }
    if (command == Command::START) {
        if (!inside(current.started_us, started_us, after_us) ||
            !inside(current.drive_completed_us, current.started_us, after_us)) {
            fail(Fault::SOURCE_ORDER);
            return;
        }
        startSource(previous, after_us);
    } else if (current.phase == line_qtr::Phase::COMPLETE &&
               !inside(current.completed_us, started_us, after_us)) {
        fail(Fault::SOURCE_ORDER);
        return;
    }
    if (report_.fault == Fault::NONE &&
        (current.phase == line_qtr::Phase::IDLE || current.phase == line_qtr::Phase::COMPLETE))
        possibly_active_ = false;
}

void Runner::examineCancellation() {
    const auto& current = report_.cancellation;
    if (report_.cancel_qualification != line_qtr::RawQualification::PROVIDER_FAULT ||
        current.phase != line_qtr::Phase::FAULT) { fail(Fault::CONTRACT); return; }
    if (!sameIdentity(current, report_.snapshot)) { fail(Fault::SOURCE_ORDER); return; }
    if (current.status == line_qtr::Status::CLEANUP || !cleanupSuccessful(current.cleanup)) {
        fail(Fault::CLEANUP);
        return;
    }
    if (current.status != line_qtr::Status::CANCELLED) fail(Fault::CONTRACT);
}
void Runner::cancellationBracket(std::uint32_t before_us, std::uint32_t after_us) {
    const auto& current = report_.cancellation;
    const auto& cleanup = current.cleanup;
    if (!inside(cleanup.started_us, before_us, after_us) ||
        !inside(cleanup.completed_us, cleanup.started_us, after_us) ||
        cleanup.completed_us - cleanup.started_us >= config::QTR_CLEANUP_MAX_US ||
        current.checked_us != cleanup.completed_us || current.completed_us != cleanup.completed_us)
        fail(Fault::SOURCE_ORDER);
}
void Runner::cancelOnce(bool stopping) {
    if (!possibly_active_ || report_.cancel_attempted) return;
    report_.cancel_attempted = true;
    std::uint32_t before = 0U;
    if (!report_.clock_fault) clock(before);
    attempt(report_.cancel);
    report_.cancellation = port_.cancel(port_.context);
    const bool can_close = !report_.clock_fault;
    const auto after = can_close ? port_.clockUs(port_.context) : 0U;
    report_.cancel_qualification = line_qtr::validateRaw(report_.cancellation);
    if (stopping) examineCancellation();
    if (can_close && admitClock(after)) {
        measure(report_.cancel, after - before);
        if (stopping) cancellationBracket(before, after);
    }
}

bool Runner::begin(const Grants& grants) {
    if (attempted_) return false;
    attempted_ = true;
    if (!grants.exclusive_pads) { report_.phase = Phase::DISABLED; return true; }
    if (!portsValid()) { fail(Fault::PORT); return false; }
    if (config::QTR_BENCH_FRAMES == 0U) { fail(Fault::CONFIG); return false; }
    std::uint32_t started = 0U;
    if (!open(started)) return false;
    const auto previous = report_.snapshot;
    invoke(Command::BEGIN);
    const auto after = port_.clockUs(port_.context);
    examine(Command::BEGIN, previous, 0U);
    if (admitClock(after) && report_.fault == Fault::NONE)
        sourceBracket(Command::BEGIN, previous, started, after);
    if (!close(started, report_.setup)) return false;
    report_.phase = Phase::RUNNING;
    return true;
}
bool Runner::poll() {
    report_.fresh = false;
    if (report_.phase != Phase::RUNNING) return false;
    attempt(report_.poll);
    std::uint32_t started = 0U;
    if (!open(started)) { cancelOnce(); return false; }
    const auto age_at_start = source_age_us_;
    const auto previous = report_.snapshot;
    const auto command = active(previous.phase) ? Command::ADVANCE : Command::START;
    invoke(command);
    const auto after = port_.clockUs(port_.context);
    examine(command, previous, age_at_start);
    if (admitClock(after)) {
        measure(command == Command::START ? report_.start : report_.advance, after - started);
        if (report_.fault == Fault::NONE) sourceBracket(command, previous, started, after);
    }
    const bool complete = report_.fault == Fault::NONE && command == Command::ADVANCE &&
        report_.snapshot.phase == line_qtr::Phase::COMPLETE;
    if (complete) frames_[report_.captured_frames] = report_.snapshot;
    if (!close(started, report_.poll)) return false;
    if (complete) {
        ++report_.captured_frames;
        report_.fresh = true;
        if (report_.captured_frames == config::QTR_BENCH_FRAMES) report_.phase = Phase::COMPLETE;
    }
    return report_.fresh;
}
void Runner::stop() {
    report_.fresh = false;
    if (report_.phase != Phase::RUNNING) return;
    cancelOnce(true);
    if (report_.fault == Fault::NONE) report_.phase = Phase::STOPPED;
}
} // namespace qtr_raw
