// Runs a finite IMU bias and heading trial over the existing acquisition and pure owners.
// Preserves native diagnostics while separating clock admission from immutable evidence.
// Independent D111 scheduling, cancellation, calibration and checkpoint tests cover this path.
#include "imu_heading_bench.h"
#include <cmath>
#include <limits>

namespace imu_heading_bench {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
bool configValid() {
    if constexpr (config::IMU_BENCH_CHECKPOINT_US == 0U) return false;
    else {
        const std::uint64_t trial = config::IMU_BENCH_TRIAL_US;
        const std::uint64_t period = config::IMU_BENCH_CHECKPOINT_US;
        const std::uint64_t minimum = config::IMU_SETUP_DEADLINE_US +
            static_cast<std::uint64_t>(config::CAL_END_MS) * 1000U + trial;
        return config::TICK_US > 0U && config::TICK_US <= config::IMU_HEADING_MAX_GAP_US &&
            config::IMU_HEADING_MAX_GAP_US < HALF_RANGE &&
            period >= config::IMU_HEADING_MAX_GAP_US && trial > 0U && trial % period == 0U &&
            config::IMU_BENCH_CHECKPOINTS == 1U + trial / period &&
            config::IMU_BENCH_DEADLINE_US < HALF_RANGE &&
            config::IMU_BENCH_DEADLINE_US > minimum && config::IMU_BENCH_MAX_POLLS > 0U &&
            config::IMU_BENCH_MAX_POLLS < std::numeric_limits<std::uint32_t>::max();
    }
}
bool knownBus(imu::BusStatus status, imu::BusCleanup cleanup) {
    return static_cast<std::uint8_t>(status) <= static_cast<std::uint8_t>(imu::BusStatus::CANCELLED) &&
        static_cast<std::uint8_t>(cleanup) <= static_cast<std::uint8_t>(imu::BusCleanup::UNCONFIRMED);
}
bool emptyMotion(const imu::CoherentMotion& motion) {
    if (motion.status != imu::DecodeStatus::RESPONSE || motion.temperature_raw != 0 ||
        motion.started_us != 0U || motion.completed_us != 0U || motion.interrupt_status != 0U ||
        motion.rail_mask != 0U || motion.coherent) return false;
    for (unsigned i = 0U; i < 3U; ++i)
        if (motion.accel_raw[i] != 0 || motion.gyro_raw[i] != 0 ||
            motion.accel_g[i] != 0.0F || motion.gyro_dps[i] != 0.0F) return false;
    return true;
}
bool emptyPhase(const imu::Sample& sample) {
    return sample.readiness_completed_us == 0U && sample.motion_started_us == 0U &&
        sample.observation_gap_us == 0U && !sample.had_previous_observation;
}
bool emptySample(const imu::Sample& sample) {
    return sample.state == imu::SampleState::NOT_READY && sample.fault == imu::SampleFault::NONE &&
        sample.bus_status == imu::BusStatus::NOT_INITIALIZED &&
        sample.cleanup == imu::BusCleanup::NOT_ATTEMPTED && sample.error_flags == 0U &&
        sample.sequence == 0U && sample.checked_us == 0U && emptyMotion(sample.motion) &&
        emptyPhase(sample);
}
bool faultSample(const imu::Sample& sample) {
    return sample.state == imu::SampleState::FAULT && sample.fault != imu::SampleFault::NONE &&
        static_cast<std::uint8_t>(sample.fault) <= static_cast<std::uint8_t>(imu::SampleFault::SILENCE) &&
        knownBus(sample.bus_status, sample.cleanup) && emptyMotion(sample.motion) && emptyPhase(sample);
}
bool completeSample(const imu::Sample& sample) {
    if ((sample.state != imu::SampleState::NO_NEW && sample.state != imu::SampleState::OBSERVATION) ||
        sample.fault != imu::SampleFault::NONE || sample.bus_status != imu::BusStatus::OK ||
        sample.cleanup != imu::BusCleanup::NOT_ATTEMPTED || sample.error_flags != 0U) return false;
    return sample.state == imu::SampleState::OBSERVATION ||
        (emptyMotion(sample.motion) && sample.readiness_completed_us == sample.checked_us &&
         sample.motion_started_us == 0U && sample.observation_gap_us == 0U &&
         !sample.had_previous_observation);
}
countdown::GyroPresence presence(imu::Presence observed) {
    if (observed == imu::Presence::VALID) return countdown::GyroPresence::VALID;
    if (observed == imu::Presence::ABSENT) return countdown::GyroPresence::ABSENT;
    return countdown::GyroPresence::INVALID;
}
} // namespace

Runner::Runner(const Port& port) : port_(port) {}
const Report& Runner::report() const { return report_; }
std::uint32_t Runner::checkpointCapacity() const { return config::IMU_BENCH_CHECKPOINTS; }
std::uint32_t Runner::checkpointCount() const { return report_.checkpoints; }
const Checkpoint* Runner::checkpoint(std::uint32_t index) const {
    return index < report_.checkpoints ? &checkpoints_[index] : nullptr;
}
bool Runner::portsValid() const {
    return port_.clockUs && port_.startSetup && port_.advanceSetup &&
        port_.beginRead && port_.advanceRead && port_.cancelRead;
}
bool Runner::active() const {
    return report_.phase == Phase::SETUP || report_.phase == Phase::CALIBRATION ||
        report_.phase == Phase::MEASURING;
}
void Runner::fail(Fault fault) {
    if (report_.fault == Fault::NONE) report_.fault = fault;
    report_.phase = Phase::FAULT;
    report_.checkpoint_fresh = report_.observation_fresh = false;
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
    if (elapsed >= HALF_RANGE || elapsed >= HALF_RANGE - lifetime_us_ ||
        (interval_active_ && elapsed >= HALF_RANGE - interval_us_) ||
        (grid_active_ && elapsed >= HALF_RANGE - grid_age_us_)) {
        report_.clock_fault = true;
        fail(Fault::CLOCK);
        return false;
    }
    lifetime_us_ += elapsed;
    if (interval_active_) interval_us_ += elapsed;
    if (grid_active_) grid_age_us_ += elapsed;
    clock_seen_ = true;
    last_clock_us_ = now_us;
    if (lifetime_us_ >= config::IMU_BENCH_DEADLINE_US) fail(Fault::DEADLINE);
    return true;
}
bool Runner::clock(std::uint32_t& now_us) {
    if (report_.clock_fault) return false;
    now_us = port_.clockUs(port_.context);
    return admitClock(now_us);
}
bool Runner::cancelOnce(std::uint32_t historical_us) {
    if (!possibly_pending_ || report_.cancellation_attempted) return false;
    possibly_pending_ = false;
    report_.cancellation_attempted = true;
    attempt(report_.cancel_timing);
    report_.cancellation = port_.cancelRead(port_.context, historical_us);
    return true;
}
bool Runner::finish(std::uint32_t started_us, bool poll_call, std::uint32_t& closed_us) {
    const auto trigger = last_clock_us_;
    const bool cancelled = report_.fault != Fault::NONE && cancelOnce(trigger);
    const bool accepted = clock(closed_us);
    interval_active_ = false;
    if (accepted && poll_call) measure(report_.poll_timing, closed_us - started_us);
    if (accepted && cancelled) measure(report_.cancel_timing, closed_us - trigger);
    // A failure first observed at C permits cleanup, but cannot measure its later duration.
    if (report_.fault != Fault::NONE) cancelOnce(last_clock_us_);
    return accepted && report_.fault == Fault::NONE;
}
bool Runner::due(bool setup) {
    if (!setup && !read_started_) return true;
    if (grid_age_us_ >= config::TICK_US) return true;
    add(setup ? report_.setup_not_due : report_.read_not_due);
    return false;
}
void Runner::release(bool setup) {
    if (!setup && !read_started_) {
        read_started_ = grid_active_ = true;
        grid_age_us_ = 0U;
        return;
    }
    if constexpr (config::TICK_US > 0U) {
        const auto slots = grid_age_us_ / config::TICK_US;
        add(setup ? report_.missed_setup_releases : report_.missed_read_releases, slots - 1U);
        grid_age_us_ -= slots * config::TICK_US;
    }
}
bool Runner::setupShape(const imu::SetupReport& previous, std::uint32_t started_us, bool initial) {
    const auto& setup = report_.setup;
    if (static_cast<std::uint8_t>(setup.state) > static_cast<std::uint8_t>(imu::SetupState::FAULT) ||
        static_cast<std::uint8_t>(setup.fault) > static_cast<std::uint8_t>(imu::SetupFault::STATUS) ||
        !knownBus(setup.bus_status, setup.cleanup)) { fail(Fault::CONTRACT); return false; }
    if (setup.state == imu::SetupState::FAULT) {
        fail(setup.fault == imu::SetupFault::NONE ? Fault::CONTRACT : Fault::SETUP);
        return false;
    }
    bool valid = setup.fault == imu::SetupFault::NONE &&
        setup.cleanup == imu::BusCleanup::NOT_ATTEMPTED && setup.error_flags == 0U;
    if (initial) valid = valid && setup.state == imu::SetupState::IN_PROGRESS &&
        setup.started_us == started_us && setup.observed_us == started_us &&
        setup.advances == 0U && setup.requests == 0U && setup.bus_status == imu::BusStatus::NOT_INITIALIZED;
    else valid = valid && (setup.state == imu::SetupState::IN_PROGRESS ||
        setup.state == imu::SetupState::PROFILE_READY) && setup.started_us == previous.started_us &&
        static_cast<std::uint64_t>(setup.advances) == static_cast<std::uint64_t>(previous.advances) + 1U &&
        setup.advances <= config::IMU_SETUP_MAX_ADVANCES && setup.requests >= previous.requests &&
        static_cast<std::uint64_t>(setup.requests) <= static_cast<std::uint64_t>(previous.requests) + 1U &&
        setup.requests <= config::IMU_SETUP_MAX_REQUESTS &&
        setup.bus_status == (setup.requests == 0U ? imu::BusStatus::NOT_INITIALIZED : imu::BusStatus::OK) &&
        (setup.state != imu::SetupState::PROFILE_READY || setup.requests > 0U);
    if (!valid) fail(Fault::CONTRACT);
    return valid;
}
bool Runner::runSetup(std::uint32_t started_us, bool initial) {
    const auto previous = report_.setup;
    auto& timing = initial ? report_.start_timing : report_.setup_timing;
    attempt(timing);
    report_.setup = initial ? port_.startSetup(port_.context, started_us, true) :
        port_.advanceSetup(port_.context, started_us);
    const auto returned = port_.clockUs(port_.context);
    const bool healthy = setupShape(previous, started_us, initial);
    if (admitClock(returned)) {
        measure(timing, returned - started_us);
        if (healthy && report_.setup.observed_us - started_us > returned - started_us)
            fail(Fault::SOURCE_ORDER);
    }
    std::uint32_t closed = 0U;
    if (!finish(started_us, !initial, closed)) return false;
    report_.phase = Phase::SETUP;
    if (report_.setup.state == imu::SetupState::PROFILE_READY) {
        report_.calibration_started_us = closed;
        if (!calibration_.start(closed, report_.estimate.bias_dps)) { fail(Fault::CALIBRATION); return false; }
        calibration_open_ = true;
        grid_active_ = false;
        grid_age_us_ = 0U;
        report_.phase = Phase::CALIBRATION;
    }
    return true;
}
Runner::Reply Runner::progressShape(bool beginning) {
    const auto& progress = report_.progress;
    if (progress.state == imu::AsyncState::PENDING && progress.started == beginning &&
        !progress.completed && emptySample(progress.sample)) {
        add(report_.pending_results);
        return Reply::PENDING;
    }
    if (progress.started || !progress.completed) { fail(Fault::CONTRACT); return Reply::INVALID; }
    if (progress.state == imu::AsyncState::FAULT && faultSample(progress.sample)) {
        possibly_pending_ = false;
        add(report_.completions);
        fail(Fault::SOURCE);
        return Reply::FAULT;
    }
    if (!beginning && progress.state == imu::AsyncState::COMPLETE && completeSample(progress.sample)) {
        add(report_.completions);
        return Reply::COMPLETE;
    }
    fail(Fault::CONTRACT);
    return Reply::INVALID;
}
bool Runner::sourceOrder(std::uint32_t started_us, std::uint32_t returned_us) {
    const auto& sample = report_.progress.sample;
    bool valid = sample.checked_us - started_us <= returned_us - started_us;
    if (sample.state == imu::SampleState::OBSERVATION) {
        const auto origin = sample.motion.started_us - operation_started_us_;
        const auto ready = sample.readiness_completed_us - operation_started_us_;
        const auto motion = sample.motion_started_us - operation_started_us_;
        const auto complete = sample.checked_us - operation_started_us_;
        valid = valid && sample.motion.completed_us == sample.checked_us && origin <= ready &&
            ready <= motion && motion <= complete && complete <= returned_us - operation_started_us_ &&
            sample.motion.completed_us - sample.motion.started_us < config::IMU_I2C_TRANSFER_US;
    }
    if (!valid) fail(Fault::SOURCE_ORDER);
    return valid;
}
void Runner::calibrate(std::uint32_t returned_us) {
    countdown::ServiceSample sample{};
    sample.t_us = returned_us;
    sample.raw_gyro_z_dps = report_.estimate.raw_gyro_z_dps;
    sample.gyro_presence = presence(report_.estimate.gyro_observation);
    sample.gyro_observation_us = report_.estimate.observation_us;
    sample.gyro_sequence = report_.estimate.sequence;
    sample.explicit_line = true;
    report_.calibration = calibration_.step(sample);
    if (!report_.calibration.calibration_finished) return;
    calibration_open_ = false;
    if (report_.calibration.calibration_rejected) { fail(Fault::CALIBRATION); return; }
    const bool applied = estimator_.applyBias(report_.calibration.bias_dps);
    report_.estimate = estimator_.report();
    if (!applied) { fail(Fault::HEADING); return; }
    report_.bias_applied = true;
    report_.accepted_bias_dps = report_.calibration.bias_dps;
}
void Runner::consume(std::uint32_t returned_us) {
    report_.estimate = estimator_.observe(report_.progress.sample);
    if (report_.estimate.state == imu::HeadingState::FAULT) fail(Fault::HEADING);
    if (calibration_open_) calibrate(returned_us);
}
bool Runner::prepareMeasurement(Measurement& candidate, std::uint32_t returned_us) {
    candidate = report_.measurement;
    const auto& estimate = report_.estimate;
    if (!candidate.anchored) {
        candidate.anchored = true;
        candidate.started_us = estimate.observation_us;
        candidate.first_sequence = estimate.sequence;
        candidate.start_heading_deg = estimate.heading_deg;
    }
    candidate.ended_us = estimate.observation_us;
    candidate.elapsed_us = estimate.observation_us - candidate.started_us;
    candidate.last_sequence = estimate.sequence;
    candidate.end_heading_deg = estimate.heading_deg;
    candidate.delta_deg = static_cast<double>(estimate.heading_deg) - candidate.start_heading_deg;
    if (!std::isfinite(candidate.delta_deg)) { fail(Fault::NUMERIC); return false; }
    if (candidate.delta_deg < candidate.minimum_delta_deg) candidate.minimum_delta_deg = candidate.delta_deg;
    if (candidate.delta_deg > candidate.maximum_delta_deg) candidate.maximum_delta_deg = candidate.delta_deg;
    const auto absolute = std::fabs(candidate.delta_deg);
    if (absolute > candidate.maximum_absolute_excursion_deg) candidate.maximum_absolute_excursion_deg = absolute;
    const auto next = static_cast<std::uint64_t>(report_.checkpoints) * config::IMU_BENCH_CHECKPOINT_US;
    if (candidate.elapsed_us < next) return false;
    if (report_.checkpoints >= config::IMU_BENCH_CHECKPOINTS ||
        (report_.checkpoints + 1U < config::IMU_BENCH_CHECKPOINTS &&
         candidate.elapsed_us >= next + config::IMU_BENCH_CHECKPOINT_US)) {
        fail(Fault::CONTRACT);
        return false;
    }
    auto& checkpoint = checkpoints_[report_.checkpoints];
    checkpoint.sample = report_.progress.sample;
    checkpoint.estimate = estimate;
    checkpoint.elapsed_source_us = candidate.elapsed_us;
    checkpoint.delivered_us = returned_us;
    return true;
}
void Runner::commitRead(Phase entered, const Measurement& candidate, bool checkpoint,
                        std::uint32_t closed_us) {
    if (report_.progress.sample.state == imu::SampleState::NO_NEW) add(report_.no_new);
    if (report_.estimate.heading_updated) {
        add(report_.observations);
        report_.observation_fresh = true;
        const auto gap = report_.progress.sample.observation_gap_us;
        if (gap > report_.maximum_observation_gap_us) report_.maximum_observation_gap_us = gap;
        if (entered == Phase::MEASURING) {
            report_.measurement = candidate;
            add(report_.measurement.observations);
        }
    }
    if (entered == Phase::CALIBRATION && report_.bias_applied && !calibration_open_)
        report_.phase = Phase::MEASURING;
    if (!checkpoint) return;
    checkpoints_[report_.checkpoints].closed_us = closed_us;
    ++report_.checkpoints;
    report_.checkpoint_fresh = true;
    if (report_.checkpoints == config::IMU_BENCH_CHECKPOINTS) report_.phase = Phase::COMPLETE;
}
bool Runner::runRead(std::uint32_t started_us) {
    const auto entered = report_.phase;
    const bool beginning = !possibly_pending_;
    auto& timing = beginning ? report_.begin_timing : report_.advance_timing;
    attempt(timing);
    if (beginning) { possibly_pending_ = true; operation_started_us_ = started_us; }
    report_.progress = beginning ? port_.beginRead(port_.context, started_us) :
        port_.advanceRead(port_.context, started_us);
    const auto returned = port_.clockUs(port_.context);
    const auto reply = progressShape(beginning);
    if (admitClock(returned)) {
        measure(timing, returned - started_us);
        if (reply == Reply::COMPLETE && sourceOrder(started_us, returned)) {
            possibly_pending_ = false;
            consume(returned);
        } else if (reply == Reply::FAULT) consume(returned);
    }
    Measurement candidate{};
    const bool checkpoint = report_.fault == Fault::NONE && entered == Phase::MEASURING &&
        reply == Reply::COMPLETE && report_.estimate.heading_updated && prepareMeasurement(candidate, returned);
    std::uint32_t closed = 0U;
    if (!finish(started_us, true, closed)) return false;
    if (reply == Reply::COMPLETE) commitRead(entered, candidate, checkpoint, closed);
    return report_.checkpoint_fresh;
}
bool Runner::begin(const Grants& grants) {
    if (attempted_) return false;
    attempted_ = true;
    if (!grants.enabled) { report_.phase = Phase::DISABLED; return true; }
    if (!grants.exclusive_i2c || !grants.power_confirmed || !grants.at_rest_confirmed) {
        fail(Fault::GRANT); return false;
    }
    if (!portsValid()) { fail(Fault::PORT); return false; }
    if (!configValid()) { fail(Fault::CONFIG); return false; }
    const bool ready = estimator_.begin(grants.mounting, grants.initial_bias_dps);
    report_.estimate = estimator_.report();
    if (!ready) { fail(Fault::HEADING); return false; }
    std::uint32_t started = 0U;
    if (!clock(started)) return false;
    interval_active_ = grid_active_ = true;
    interval_us_ = grid_age_us_ = 0U;
    return runSetup(started, true);
}
bool Runner::poll() {
    report_.checkpoint_fresh = report_.observation_fresh = false;
    if (!active()) return false;
    attempt(report_.poll_timing);
    if (report_.admitted_polls >= config::IMU_BENCH_MAX_POLLS) {
        fail(Fault::LIMIT); cancelOnce(last_clock_us_); return false;
    }
    ++report_.admitted_polls;
    std::uint32_t started = 0U, closed = 0U;
    if (!clock(started)) { cancelOnce(last_clock_us_); return false; }
    interval_active_ = true;
    interval_us_ = 0U;
    if (report_.fault != Fault::NONE) { finish(started, true, closed); return false; }
    const bool setup = report_.phase == Phase::SETUP;
    if (!possibly_pending_) {
        if (!due(setup)) { interval_active_ = false; return false; }
        release(setup);
    }
    if (setup) { runSetup(started, false); return false; }
    return runRead(started);
}
} // namespace imu_heading_bench
