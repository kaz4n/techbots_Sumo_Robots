// Declares an inert trace around the unchanged native MotorGate callbacks.
// Retains the first failed callback across later cleanup without granting motion.
// Independent D162 public-contract traces and real Gate tests verify this probe.
#pragma once
#include "config.h"
#include "hal/motors.h"
#include <cstdint>

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Motor fault diagnostic requires inert flags");

namespace motor_fault {
inline constexpr std::uint32_t TRACE_CAPACITY = 64U; // Fixed evidence ABI extent.
inline constexpr std::uint32_t APPLY_SAMPLES = 4U; // Fixed receipt ABI extent.
enum class Stage : std::uint8_t { SETUP, APPLY, HALT };
enum class Operation : std::uint8_t { CONFIG_ENABLE, CONFIG_PWM, ENABLE, PWM, SETTLE };
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, COMPLETE, FAULT };
enum class Failure : std::uint8_t { NONE, SETUP, CLOCK, APPLICATION, TRACE, HALT };
struct Call {
    Stage stage = Stage::SETUP;
    Operation operation = Operation::CONFIG_ENABLE;
    motors::Channel channel = motors::Channel::LEFT_FORWARD;
    std::uint32_t application = 0U;
    bool requested_high = false;
    std::uint32_t period_cycles = 0U, pulse_cycles = 0U;
    bool invoked = false, completed = false, returned = false, timing_valid = false;
    std::uint32_t started_us = 0U, completed_us = 0U;
};
struct TraceReport {
    Call calls[TRACE_CAPACITY];
    std::uint32_t count = 0U, rejected = 0U, clock_reads = 0U;
    bool overflow = false, timing_fault = false, has_failure = false, has_current = false;
    Call current, first_failure;
};
class Trace {
public:
    explicit Trace(const motors::Port& native);
    Trace(const Trace&) = delete;
    Trace& operator=(const Trace&) = delete;
    motors::Port port();
    void context(Stage stage, std::uint32_t application = 0U);
    const TraceReport& report() const;
private:
    static bool configureEnable(void* context);
    static bool configurePwm(void* context, motors::Channel channel);
    static bool enable(void* context, bool high);
    static bool pwm(void* context, motors::Channel channel, std::uint32_t period,
                    std::uint32_t pulse);
    static bool settle(void* context);
    static std::uint32_t clock(void* context);
    void start(Operation operation, motors::Channel channel = motors::Channel::LEFT_FORWARD,
               bool high = false, std::uint32_t period = 0U, std::uint32_t pulse = 0U);
    bool finish(bool result);
    motors::Port native_;
    TraceReport report_;
    Stage stage_ = Stage::SETUP;
    std::uint32_t application_ = 0U;
};
struct Grants { bool exclusive_motor_outputs = false; };
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Failure failure = Failure::NONE;
    bool begin_called = false, begin_ok = false, halt_called = false;
    motors::Fault begin_fault = motors::Fault::NONE;
    std::uint32_t applications = 0U, next_release_us = 0U, missed_releases = 0U;
    motors::Result applied[APPLY_SAMPLES];
    motors::HaltResult halt;
};
class Runner {
public:
    explicit Runner(const motors::Port& native);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    void poll(std::uint32_t now_us);
    bool active() const;
    const Report& report() const;
    const TraceReport& trace() const;
private:
    bool traceValid() const;
    void stop(Failure reason);
    Trace trace_;
    motors::Port port_;
    motors::MotorGate gate_;
    Report report_;
    bool attempted_ = false;
    std::uint32_t last_us_ = 0U, equal_polls_ = 0U;
};
} // namespace motor_fault
