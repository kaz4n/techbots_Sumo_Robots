// Declares a finite IMU calibration and continuous-heading evidence trial.
// Reuses the actual pure estimator/services and one explicitly granted native source.
// D111 contract: independent lifecycle, chronology and checkpoint tests follow adoption.
#pragma once
#include "hal/imu_heading.h"
#include "core/countdown.h"
#include <cstdint>

namespace imu_heading_bench {
enum class Phase : std::uint8_t {
    NOT_STARTED, DISABLED, SETUP, CALIBRATION, MEASURING, COMPLETE, FAULT
};
enum class Fault : std::uint8_t {
    NONE, GRANT, PORT, CONFIG, SETUP, SOURCE, CONTRACT, SOURCE_ORDER,
    HEADING, CALIBRATION, NUMERIC, CLOCK, DEADLINE, LIMIT
};
struct Port {
    void* context = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
    imu::SetupReport (*startSetup)(void*, std::uint32_t, bool) = nullptr;
    imu::SetupReport (*advanceSetup)(void*, std::uint32_t) = nullptr;
    imu::SampleProgress (*beginRead)(void*, std::uint32_t) = nullptr;
    imu::SampleProgress (*advanceRead)(void*, std::uint32_t) = nullptr;
    imu::SampleProgress (*cancelRead)(void*, std::uint32_t) = nullptr;
};
struct Grants {
    bool enabled = false;
    bool exclusive_i2c = false;
    bool power_confirmed = false;
    bool at_rest_confirmed = false;
    imu::Mounting mounting;
    float initial_bias_dps = 0.0F;
};
struct Timing {
    std::uint32_t calls = 0U, measured_calls = 0U;
    std::uint32_t last_us = 0U, maximum_us = 0U;
    bool last_valid = false;
};
struct Checkpoint {
    imu::Sample sample;
    imu::Estimate estimate;
    std::uint32_t elapsed_source_us = 0U;
    std::uint32_t delivered_us = 0U; // A, not native source time.
    std::uint32_t closed_us = 0U; // C; closing publication is outside the bracket.
};
struct Measurement {
    bool anchored = false;
    std::uint32_t started_us = 0U, ended_us = 0U, elapsed_us = 0U;
    std::uint32_t first_sequence = 0U, last_sequence = 0U, observations = 0U;
    float start_heading_deg = 0.0F, end_heading_deg = 0.0F;
    double delta_deg = 0.0, minimum_delta_deg = 0.0, maximum_delta_deg = 0.0;
    double maximum_absolute_excursion_deg = 0.0;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Fault fault = Fault::NONE;
    bool checkpoint_fresh = false, observation_fresh = false;
    bool clock_fault = false, counter_saturated = false;
    bool bias_applied = false, cancellation_attempted = false;
    imu::SetupReport setup;
    imu::SampleProgress progress; // Actual latest normal native callback result.
    imu::SampleProgress cancellation; // Actual cleanup result, kept separately.
    imu::Estimate estimate; // Actual latest pure result; not a checkpoint claim.
    countdown::ServiceResult calibration;
    std::uint32_t calibration_started_us = 0U;
    float accepted_bias_dps = 0.0F;
    std::uint32_t admitted_polls = 0U, checkpoints = 0U;
    std::uint32_t setup_not_due = 0U, read_not_due = 0U;
    std::uint32_t missed_setup_releases = 0U, missed_read_releases = 0U;
    std::uint32_t pending_results = 0U, completions = 0U;
    std::uint32_t observations = 0U, no_new = 0U;
    std::uint32_t maximum_observation_gap_us = 0U;
    Measurement measurement;
    Timing start_timing, setup_timing, begin_timing, advance_timing;
    Timing cancel_timing, poll_timing;
};
class Runner {
public:
    explicit Runner(const Port& port);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    bool poll(); // True only for one newly published immutable checkpoint.
    const Report& report() const;
    std::uint32_t checkpointCapacity() const;
    std::uint32_t checkpointCount() const;
    const Checkpoint* checkpoint(std::uint32_t index) const;
private:
    enum class Reply : std::uint8_t { INVALID, PENDING, COMPLETE, FAULT };
    bool portsValid() const;
    bool active() const;
    void fail(Fault fault);
    void add(std::uint32_t& counter, std::uint32_t amount = 1U);
    void attempt(Timing& timing);
    void measure(Timing& timing, std::uint32_t elapsed_us);
    bool admitClock(std::uint32_t now_us);
    bool clock(std::uint32_t& now_us);
    bool cancelOnce(std::uint32_t historical_us);
    bool finish(std::uint32_t started_us, bool poll_call, std::uint32_t& closed_us);
    bool due(bool setup);
    void release(bool setup);
    bool setupShape(const imu::SetupReport& previous, std::uint32_t started_us, bool initial);
    bool runSetup(std::uint32_t started_us, bool initial);
    Reply progressShape(bool beginning);
    bool sourceOrder(std::uint32_t started_us, std::uint32_t returned_us);
    void consume(std::uint32_t returned_us);
    void calibrate(std::uint32_t returned_us);
    bool prepareMeasurement(Measurement& candidate, std::uint32_t returned_us);
    void commitRead(Phase entered, const Measurement& candidate, bool checkpoint,
                    std::uint32_t closed_us);
    bool runRead(std::uint32_t started_us);
    Port port_;
    Report report_;
    imu::Estimator estimator_;
    countdown::Services calibration_;
    Checkpoint checkpoints_[config::IMU_BENCH_CHECKPOINTS > 0U ? config::IMU_BENCH_CHECKPOINTS : 1U]{};
    bool attempted_ = false;
    bool clock_seen_ = false;
    bool interval_active_ = false;
    bool grid_active_ = false;
    bool read_started_ = false;
    bool possibly_pending_ = false;
    bool calibration_open_ = false;
    std::uint32_t last_clock_us_ = 0U;
    std::uint32_t lifetime_us_ = 0U;
    std::uint32_t interval_us_ = 0U;
    std::uint32_t grid_age_us_ = 0U;
    std::uint32_t operation_started_us_ = 0U;
};
} // namespace imu_heading_bench
