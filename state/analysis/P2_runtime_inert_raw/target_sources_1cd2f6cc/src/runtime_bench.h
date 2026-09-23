// Runs the actual Runtime with absent sources and checked inert motor callbacks.
// Exposes fixed truthful diagnostics for a no-pin bare-board load experiment.
// Independent D104 host and exact-target capture tests verify this contract.
#pragma once
#include "app/runtime.h"
#include <cstddef>
#include <cstdint>

namespace runtime_bench {
enum class Phase : std::uint32_t { NOT_STARTED, RUNNING, FROZEN, FAILED };
enum class Failure : std::uint32_t {
    NONE, CLOCK, REENTRY, SETUP, PORT, RUNTIME, CHRONOLOGY, RECEIPT,
    INPUTS, RECORDER, MISSED_RELEASE, DEADLINE, SATURATION
};
struct ClockPort { void* context = nullptr; std::uint32_t (*now_us)(void*) = nullptr; };
struct Counters {
    std::uint32_t setup_enable = 0U, setup_pwm = 0U, enable_low = 0U, pwm_zero = 0U;
    std::uint32_t settle = 0U, clock = 0U, enabled = 0U, nonzero = 0U, invalid = 0U;
    bool fault = false, saturated = false;
};
struct Report {
    std::uint32_t schema_version = 0U, byte_size = 0U, phase = 0U, failure = 0U;
    std::uint32_t boot_us = 0U, first_s_us = 0U, first_d_us = 0U, first_c_us = 0U;
    std::uint32_t last_s_us = 0U, last_d_us = 0U, last_a_us = 0U, last_c_us = 0U;
    std::uint32_t elapsed_us = 0U, epochs = 0U, missed_releases = 0U;
    std::uint32_t maximum_execution_us = 0U, maximum_runner_us = 0U;
    std::uint32_t token_lo = 0U, token_hi = 0U;
    std::uint32_t runtime_phase = 0U, runtime_fault = 0U;
    std::uint32_t transaction_phase = 0U, transaction_fault = 0U;
    std::uint32_t robot_state = 0U, contract_faults = 0U, escape_fault = 0U, gate_fault = 0U;
    std::uint32_t receipt_flags = 0U, input_absent_mask = 0U, initialization_complete = 0U;
    std::uint32_t recorder_phase = 0U, frame_count = 0U, event_count = 0U;
    std::uint32_t setup_enable_calls = 0U, setup_pwm_calls = 0U;
    std::uint32_t enable_low_calls = 0U, pwm_zero_calls = 0U, settle_calls = 0U, clock_calls = 0U;
    std::uint32_t enabled_requests = 0U, nonzero_requests = 0U, invalid_requests = 0U;
    std::uint32_t reserved[6] = {};
};
static_assert(sizeof(Report) == 192U, "D104 report ABI");
struct StackSample {
    std::uint32_t valid = 0U, region_start = 0U, region_size = 0U, region_delta = 0U;
    std::uint32_t minimum_sp = 0U, samples = 0U, sampled_headroom_bytes = 0U, fault = 0U;
};
struct Diagnostics {
    std::uint32_t sequence_front = 0U;
    Report report;
    StackSample stack;
    std::uint32_t sequence_tail = 0U;
};
static_assert(sizeof(Diagnostics) == 232U, "D104 diagnostic ABI");
static_assert(offsetof(Diagnostics, sequence_tail) == 228U, "D104 tail offset");
class InertMotorPort {
public:
    explicit InertMotorPort(const ClockPort& clock);
    motors::Port port();
    const Counters& counters() const;
private:
    friend class Runner;
    bool count(std::uint32_t& value);
    bool accept(bool valid);
    static bool configureEnable(void* context);
    static bool configurePwm(void* context, motors::Channel channel);
    static bool writeEnable(void* context, bool enabled);
    static bool writePwm(void* context, motors::Channel channel,
                         std::uint32_t period, std::uint32_t pulse);
    static bool settle(void* context);
    static std::uint32_t clockUs(void* context);
    ClockPort clock_;
    Counters counters_;
    bool enable_configured_ = false;
    std::uint8_t pwm_configured_ = 0U;
};
class Runner {
public:
    explicit Runner(const ClockPort& clock);
    bool begin();
    void poll();
    const Report& report() const;
    const app::Runtime& runtime() const;
private:
    static std::uint32_t observeClock(void* context);
    std::uint32_t clock();
    bool terminal() const;
    void fail(Failure reason);
    bool deadlines(std::uint32_t now_us);
    void refresh();
    void refreshCounters();
    void checkEpoch(std::uint32_t previous_epochs);
    void checkOwners();
    void finishPoll(std::uint32_t started_us);
    ClockPort clock_;
    InertMotorPort motor_;
    app::Runtime runtime_;
    Report report_;
    std::uint64_t last_token_ = 0U;
    std::uint32_t latest_us_ = 0U;
    std::uint32_t equal_observations_ = 0U;
    std::uint32_t previous_c_us_ = 0U;
    bool began_ = false;
    bool clock_seen_ = false;
    bool epoch_seen_ = false;
};
} // namespace runtime_bench
