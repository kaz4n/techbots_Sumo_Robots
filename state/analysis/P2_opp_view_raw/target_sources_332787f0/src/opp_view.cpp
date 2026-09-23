// Samples and displays seven opponent channels through bounded explicit grants.
// Retains invalid evidence and truthful complete-poll timing without motor logic.
// Independent literal-mask, chronology, callback and pixel tests verify D107.
#include "opp_view.h"
#include "config.h"
#include <limits>

namespace opp_view {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool validConfig() {
    return config::TICK_US > 0U && config::TICK_US < HALF_RANGE &&
        config::UI_FRAME_PERIOD_US > 0U && config::UI_FRAME_PERIOD_US < HALF_RANGE &&
        config::OPP_ACTIVE_LOW_MASK <= 0x7FU;
}
} // namespace

Runner::Runner(const Port& port) : port_(port) {}

bool Runner::validPorts() const {
    return port_.clockUs && (!grants_.opponents ||
        (port_.beginOpponents && port_.readOpponents)) &&
        (!grants_.matrix || (port_.beginMatrix && port_.submitMatrix));
}

void Runner::fail(Fault fault) {
    if (report_.fault == Fault::NONE) report_.fault = fault;
    report_.phase = Phase::FAULT;
    report_.fresh = false;
    report_.current_available = false;
    report_.detection_mask = 0U;
}

bool Runner::clock(std::uint32_t& now_us) {
    now_us = port_.clockUs(port_.context);
    if (clock_seen_) {
        const auto delta = now_us - last_clock_us_;
        if (delta >= HALF_RANGE || (interval_active_ &&
            delta >= HALF_RANGE - interval_elapsed_us_)) {
            fail(Fault::CLOCK);
            return false;
        }
        if (interval_active_) interval_elapsed_us_ += delta;
        if (display_attempted_)
            display_age_us_ = delta >= HALF_RANGE - display_age_us_ ?
                HALF_RANGE : display_age_us_ + delta;
    }
    clock_seen_ = true;
    last_clock_us_ = now_us;
    return true;
}

void Runner::add(std::uint32_t& counter, std::uint32_t amount) {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    if (amount > maximum - counter) {
        counter = maximum;
        report_.counter_saturated = true;
    } else counter += amount;
}

bool Runner::setupUsable() const {
    if (!report_.setup.ready || report_.setup.configured_mask != 0x7FU) return false;
    for (const auto status : report_.setup.status) if (status != 0) return false;
    return true;
}

bool Runner::initialize() {
    std::uint32_t now = 0U;
    if (grants_.opponents) {
        if (!clock(now)) return false;
        report_.setup = port_.beginOpponents(port_.context);
        sensors_ready_ = setupUsable();
        report_.sensor_error = !sensors_ready_;
        if (!clock(now)) return false;
    }
    if (grants_.matrix) {
        if (!clock(now)) return false;
        report_.matrix_setup = port_.beginMatrix(port_.context, grants_.matrix_grant);
        matrix_ready_ = report_.matrix_setup == ui::MatrixStatus::INIT_UNCONFIRMED;
        if (!matrix_ready_) fail(Fault::MATRIX);
        if (!clock(now) || !matrix_ready_) return false;
    }
    interval_active_ = false;
    report_.next_release_us = now;
    report_.phase = Phase::RUNNING;
    return true;
}

bool Runner::begin(const Grants& grants) {
    if (attempted_) return false;
    attempted_ = true;
    grants_ = grants;
    if (!grants.opponents && !grants.matrix) {
        report_.phase = Phase::DISABLED;
        return true;
    }
    if (!validPorts()) { fail(Fault::PORT); return false; }
    if (!validConfig()) { fail(Fault::CONFIG); return false; }
    interval_active_ = true;
    return initialize();
}

bool Runner::snapshotUsable(std::uint32_t before_us, std::uint32_t after_us) const {
    const auto& sample = report_.snapshot;
    if (!sample.valid || sample.valid_mask != 0x7FU || sample.raw_mask > 0x7FU)
        return false;
    for (unsigned bit = 0U; bit < 7U; ++bit)
        if (sample.status[bit] != static_cast<std::int32_t>((sample.raw_mask >> bit) & 1U))
            return false;
    const auto duration = after_us - before_us;
    const auto start = sample.started_us - before_us;
    const auto end = sample.completed_us - before_us;
    return duration < HALF_RANGE && start <= end && end <= duration;
}

void Runner::invalidRead() {
    add(report_.invalid_reads);
    report_.sensor_error = true;
    report_.current_available = false;
    report_.detection_mask = 0U;
    if (report_.first_read_error_saved) return;
    report_.first_read_error = report_.snapshot;
    report_.first_read_error_saved = true;
}

bool Runner::read() {
    report_.current_available = false;
    report_.detection_mask = 0U;
    if (!sensors_ready_) return true;
    std::uint32_t before = 0U, after = 0U;
    if (!clock(before)) return false;
    add(report_.read_attempts);
    report_.snapshot = port_.readOpponents(port_.context);
    if (!clock(after)) { invalidRead(); return false; }
    if (!snapshotUsable(before, after)) { invalidRead(); return true; }
    add(report_.valid_reads);
    report_.current_available = true;
    report_.detection_mask = static_cast<std::uint8_t>(
        (report_.snapshot.raw_mask ^ config::OPP_ACTIVE_LOW_MASK) & 0x7FU);
    report_.last_read_us = report_.snapshot.completed_us - report_.snapshot.started_us;
    if (report_.last_read_us > report_.maximum_read_us)
        report_.maximum_read_us = report_.last_read_us;
    return true;
}

void Runner::render() {
    report_.frame = {};
    for (unsigned bit = 0U; bit < 7U; ++bit) {
        const auto value = !report_.current_available ? 3U :
            (report_.detection_mask & (1U << bit)) != 0U ? 7U : 0U;
        report_.frame.pixels[2U * ui::FRAME_COLS + 2U * bit] = static_cast<std::uint8_t>(value);
        report_.frame.pixels[3U * ui::FRAME_COLS + 2U * bit] = static_cast<std::uint8_t>(value);
    }
    if (report_.sensor_error)
        for (unsigned column = 0U; column < ui::FRAME_COLS; ++column)
            report_.frame.pixels[column] = 7U;
}

bool Runner::display() {
    if (!matrix_ready_) return true;
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    if (display_attempted_ && display_age_us_ >= HALF_RANGE) {
        fail(Fault::CLOCK);
        return false;
    }
    if (display_attempted_ && now - last_display_us_ < config::UI_FRAME_PERIOD_US)
        return true;
    display_attempted_ = true;
    last_display_us_ = now;
    display_age_us_ = 0U;
    add(report_.display_attempts);
    report_.matrix_status = port_.submitMatrix(port_.context, now, report_.frame);
    if (report_.matrix_status == ui::MatrixStatus::SUBMITTED_UNCONFIRMED)
        add(report_.submissions);
    else if (report_.matrix_status == ui::MatrixStatus::THROTTLED)
        add(report_.throttles);
    else fail(Fault::MATRIX);
    return clock(now);
}

bool Runner::finish(std::uint32_t started_us, std::uint32_t next_release_us,
                    std::uint32_t missed) {
    if constexpr (config::TICK_US == 0U) {
        fail(Fault::CONFIG);
        return false;
    } else {
        std::uint32_t completed = 0U;
        if (!clock(completed)) return false;
        interval_active_ = false;
        report_.last_poll_us = completed - started_us;
        if (report_.last_poll_us > report_.maximum_poll_us)
            report_.maximum_poll_us = report_.last_poll_us;
        add(report_.completed_polls);
        add(report_.missed_releases, missed);
        const auto late = completed - next_release_us;
        if (late != 0U && late < HALF_RANGE) {
            const auto skipped = 1U + (late - 1U) / config::TICK_US;
            next_release_us += skipped * config::TICK_US;
            add(report_.missed_releases, skipped);
        }
        report_.next_release_us = next_release_us;
        report_.fresh = report_.phase == Phase::RUNNING;
        return report_.fresh;
    }
}

bool Runner::poll() {
    report_.fresh = false;
    if (report_.phase != Phase::RUNNING) return false;
    if constexpr (config::TICK_US == 0U) {
        fail(Fault::CONFIG);
        return false;
    } else {
        std::uint32_t started = 0U;
        if (!clock(started)) return false;
        const auto due = started - report_.next_release_us;
        if (due >= HALF_RANGE) return false;
        const auto missed = due / config::TICK_US;
        const auto next = report_.next_release_us + (missed + 1U) * config::TICK_US;
        interval_elapsed_us_ = 0U;
        interval_active_ = true;
        if (!read()) return false;
        render();
        if (!display()) return false;
        return finish(started, next, missed);
    }
}
} // namespace opp_view
