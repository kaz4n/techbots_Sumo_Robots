// Checks the D104 inert Runtime contract through public owners and real callbacks.
// Keeps the oracle independent of implementation and never seeds private state.
// Built in isolated source copies by test_runtime_bench_runner.py, normal and ASan.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "runtime_bench.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <type_traits>

namespace allocation_probe { bool active = false; std::uint64_t calls = 0U; }
extern "C" {
void* __real_malloc(std::size_t);
void* __real_calloc(std::size_t, std::size_t);
void* __real_realloc(void*, std::size_t);
void __real_free(void*);
void* __wrap_malloc(std::size_t size) {
    if (allocation_probe::active) ++allocation_probe::calls;
    return __real_malloc(size);
}
void* __wrap_calloc(std::size_t count, std::size_t size) {
    if (allocation_probe::active) ++allocation_probe::calls;
    return __real_calloc(count, size);
}
void* __wrap_realloc(void* value, std::size_t size) {
    if (allocation_probe::active) ++allocation_probe::calls;
    return __real_realloc(value, size);
}
void __wrap_free(void* value) {
    if (allocation_probe::active) ++allocation_probe::calls;
    __real_free(value);
}
}

namespace {
using runtime_bench::Failure;
using runtime_bench::Phase;
using runtime_bench::Runner;
constexpr std::uint32_t WINDOW_US = config::LOG_FRAME_WINDOW_MS * 1000U;
constexpr std::uint32_t GUARD_US = config::BTN_LONG_MS * 1000U;
constexpr std::uint32_t HALF = 0x80000000U;
constexpr std::uint32_t MIN_EPOCHS = (WINDOW_US + config::TICK_US - 1U) / config::TICK_US;

struct Clock {
    std::uint32_t now = 12345U, increment = 1U;
    std::uint64_t calls = 0U, inject_call = 0U;
    std::uint32_t inject_delta = 0U;
    std::array<std::uint32_t, 256> observations{};
    std::size_t count = 0U;
    static std::uint32_t read(void* context) {
        auto& self = *static_cast<Clock*>(context);
        ++self.calls;
        if (self.calls == self.inject_call) self.now += self.inject_delta;
        const auto value = self.now;
        if (self.count < self.observations.size()) self.observations[self.count++] = value;
        self.now += self.increment;
        return value;
    }
    runtime_bench::ClockPort port() { return {this, &read}; }
    void trace() { count = 0U; }
    bool observed(std::uint32_t value) const {
        for (std::size_t i = 0U; i < count; ++i) if (observations[i] == value) return true;
        return false;
    }
};

bool begin(Runner& runner) {
    allocation_probe::active = true;
    const bool result = runner.begin();
    allocation_probe::active = false;
    CHECK(allocation_probe::calls == 0U);
    CHECK(result);
    return result;
}
void poll(Runner& runner, Clock& clock) {
    clock.trace();
    const auto before = runner.runtime().report().epochs;
    allocation_probe::active = true;
    runner.poll();
    allocation_probe::active = false;
    CHECK(allocation_probe::calls == 0U);
    CHECK(runner.runtime().report().epochs >= before);
    CHECK(runner.runtime().report().epochs <= before + 1U);
}
void due(Runner& runner, Clock& clock, std::uint32_t late = 0U) {
    const auto target = runner.runtime().report().next_release_us + late;
    if (static_cast<std::uint32_t>(target - clock.now) < HALF) clock.now = target;
    poll(runner, clock);
}
bool running(const Runner& runner) {
    return runner.report().phase == static_cast<std::uint32_t>(Phase::RUNNING);
}
void terminalPassive(Runner& runner, Clock& clock) {
    const auto report = runner.report();
    const auto calls = clock.calls;
    const auto epochs = runner.runtime().report().epochs;
    for (unsigned i = 0U; i < 4U; ++i) {
        runner.poll();
        CHECK_FALSE(runner.begin());
        CHECK(std::memcmp(&report, &runner.report(), sizeof(report)) == 0);
        CHECK(clock.calls == calls);
        CHECK(runner.runtime().report().epochs == epochs);
    }
}
void absentInputs(const Runner& runner) {
    const auto& in = runner.runtime().decisionInput();
    CHECK_FALSE(in.initialization_complete);
    CHECK(in.line.explicit_values);
    CHECK(in.line.contract_valid);
    CHECK(in.line.presence == core::LinePresence::ABSENT);
    CHECK(in.line.use == core::LineUse::CALIBRATION);
    CHECK(in.line.sequence == 0U);
    CHECK(in.line.threshold_version == 0U);
    CHECK(in.imu.explicit_values);
    CHECK(in.imu.contract_valid);
    CHECK(in.imu.gyro == core::ImuPresence::ABSENT);
    CHECK(in.imu.accel == core::ImuPresence::ABSENT);
    CHECK_FALSE(in.imu.heading_available);
    CHECK_FALSE(in.imu.heading_updated);
    CHECK(in.raw_heading_deg == 0.0F);
    CHECK(in.raw_gyro_z_dps == 0.0F);
    CHECK(in.ax_g == 0.0F);
    CHECK(in.ay_g == 0.0F);
    CHECK(in.buttons.explicit_values);
    CHECK(in.buttons.contract_valid);
    CHECK(in.buttons.presence == core::ButtonPresence::ABSENT);
    CHECK(in.buttons.level == core::ButtonLevel::NONE);
    CHECK(in.buttons.sequence == 0U);
    CHECK_FALSE(in.vbat_valid);
    CHECK_FALSE(in.opponent_fresh);
    CHECK_FALSE(in.stop_requested);
}
void checkOwners(const Runner& runner) {
    const auto& runtime = runner.runtime().report();
    const auto& tx = runner.runtime().transaction().report();
    const auto& report = runner.report();
    CHECK(runtime.phase == app::RuntimePhase::RUNNING);
    CHECK(runtime.fault == app::RuntimeFault::NONE);
    CHECK(tx.finished);
    CHECK(tx.timing_valid);
    CHECK(tx.fault == app::Fault::NONE);
    CHECK(tx.robot.token != 0U);
    CHECK(tx.robot.outputs.ui_state == core::State::BOOT);
    CHECK(tx.robot.contract_faults == 0U);
    CHECK(tx.robot.escape_fault == edge::EscapeFault::NONE);
    CHECK_FALSE(tx.robot.lifecycle.gate.start_release);
    CHECK_FALSE(tx.robot.lifecycle.gate.go);
    CHECK_FALSE(tx.robot.lifecycle.gate.motion_permitted);
    CHECK_FALSE(tx.robot.outputs.motors_enabled);
    CHECK(tx.robot.outputs.duty_l == 0.0F);
    CHECK(tx.robot.outputs.duty_r == 0.0F);
    CHECK(tx.applied.fault == motors::Fault::NONE);
    CHECK(tx.applied.consumed);
    CHECK(tx.applied.feedback.applied_valid);
    CHECK(tx.applied.feedback.token == tx.robot.token);
    CHECK_FALSE(tx.applied.feedback.motors_enabled);
    CHECK(tx.applied.feedback.duty_l == 0.0F);
    CHECK(tx.applied.feedback.duty_r == 0.0F);
    CHECK(report.runtime_phase == static_cast<std::uint32_t>(runtime.phase));
    CHECK(report.runtime_fault == static_cast<std::uint32_t>(runtime.fault));
    CHECK(report.transaction_phase == static_cast<std::uint32_t>(tx.phase));
    CHECK(report.transaction_fault == static_cast<std::uint32_t>(tx.fault));
    CHECK(report.robot_state == static_cast<std::uint32_t>(core::State::BOOT));
    CHECK(report.gate_fault == static_cast<std::uint32_t>(tx.applied.fault));
    CHECK(report.contract_faults == 0U);
    CHECK(report.escape_fault == 0U);
    CHECK(report.receipt_flags == 15U);
    CHECK(report.input_absent_mask == 31U);
    CHECK(report.initialization_complete == 0U);
    CHECK(report.epochs == runtime.epochs);
    CHECK(report.missed_releases == runtime.missed_releases);
    CHECK(report.maximum_execution_us == runtime.maximum_execution_us);
    CHECK((static_cast<std::uint64_t>(report.token_hi) << 32U | report.token_lo) == tx.robot.token);
    CHECK(report.enabled_requests == 0U);
    CHECK(report.nonzero_requests == 0U);
    CHECK(report.invalid_requests == 0U);
    for (const auto value : report.reserved) CHECK(value == 0U);
}
void checkTimes(const Runner& runner, const Clock& clock) {
    const auto& tx = runner.runtime().transaction().report();
    const auto& report = runner.report();
    CHECK(clock.observed(tx.started_us));
    CHECK(clock.observed(tx.decision_us));
    CHECK(clock.observed(tx.applied.feedback.applied_us));
    CHECK(clock.observed(tx.completed_us));
    CHECK(static_cast<std::uint32_t>(tx.decision_us - tx.started_us) < HALF);
    CHECK(static_cast<std::uint32_t>(tx.applied.feedback.applied_us - tx.decision_us) < HALF);
    CHECK(static_cast<std::uint32_t>(tx.completed_us - tx.applied.feedback.applied_us) < HALF);
    CHECK(report.last_s_us == tx.started_us);
    CHECK(report.last_d_us == tx.decision_us);
    CHECK(report.last_a_us == tx.applied.feedback.applied_us);
    CHECK(report.last_c_us == tx.completed_us);
    CHECK(tx.execution_us == static_cast<std::uint32_t>(tx.completed_us - tx.started_us));
    CHECK(report.clock_calls == clock.calls);
    CHECK(report.maximum_runner_us >= tx.execution_us);
    CHECK(report.elapsed_us >= static_cast<std::uint32_t>(tx.completed_us - report.boot_us));
    CHECK(report.elapsed_us <= static_cast<std::uint32_t>(clock.now - report.boot_us));
}
void emptyRecorder(const Runner& runner) {
    const auto& recording = runner.runtime().transaction().recording();
    CHECK(recording.phase() == recorder::AttemptPhase::EMPTY);
    CHECK(recording.summary().epoch_token == 0U);
    CHECK(recording.frames().size() == 0U);
    CHECK(recording.events().size() == 0U);
    CHECK_FALSE(recording.summary().go_seen);
    CHECK(runner.report().recorder_phase == static_cast<std::uint32_t>(recording.phase()));
    CHECK(runner.report().frame_count == 0U);
    CHECK(runner.report().event_count == 0U);
}
void setupPort(motors::Port& port) {
    CHECK(port.configureEnableLow(port.context));
    CHECK(port.writeEnable(port.context, false));
    for (std::uint32_t i = 0U; i < 4U; ++i)
        CHECK(port.configurePwm(port.context, static_cast<motors::Channel>(i)));
    for (std::uint32_t i = 0U; i < 4U; ++i)
        CHECK(port.writePwm(port.context, static_cast<motors::Channel>(i), 1U, 0U));
    CHECK(port.settle(port.context));
}
void checkLatch(runtime_bench::InertMotorPort& owner, motors::Port& port) {
    CHECK(owner.counters().fault);
    CHECK_FALSE(port.writeEnable(port.context, false));
    CHECK_FALSE(port.writePwm(port.context, motors::Channel::LEFT_FORWARD, 1U, 0U));
    CHECK_FALSE(port.settle(port.context));
    CHECK_FALSE(port.configureEnableLow(port.context));
    CHECK_FALSE(port.configurePwm(port.context, motors::Channel::RIGHT_FORWARD));
    CHECK(owner.counters().fault);
}
}

TEST_CASE("B14 B15 D104 public report and diagnostic ABI is fixed and const-only") {
    CHECK(sizeof(runtime_bench::Report) == 192U);
    CHECK(sizeof(runtime_bench::StackSample) == 32U);
    CHECK(sizeof(runtime_bench::Diagnostics) == 232U);
    CHECK(offsetof(runtime_bench::Diagnostics, report) == 4U);
    CHECK(offsetof(runtime_bench::Diagnostics, stack) == 196U);
    CHECK(offsetof(runtime_bench::Diagnostics, sequence_tail) == 228U);
    CHECK(std::is_standard_layout<runtime_bench::Report>::value);
    CHECK(std::is_trivially_copyable<runtime_bench::Report>::value);
    CHECK((std::is_same<decltype(std::declval<const Runner&>().runtime()), const app::Runtime&>::value));
    CHECK((std::is_same<decltype(std::declval<const Runner&>().report()), const runtime_bench::Report&>::value));
}

TEST_CASE("B14 D104 construction and prebegin poll are callback passive") {
    Clock clock;
    Runner runner(clock.port());
    CHECK(clock.calls == 0U);
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::NOT_STARTED));
    runner.poll();
    CHECK(clock.calls == 0U);
    CHECK(runner.runtime().report().epochs == 0U);
    CHECK(runner.report().setup_enable_calls == 0U);
}

TEST_CASE("B14 D104 missing clock fails before any setup and terminal is passive") {
    Clock clock;
    Runner runner({&clock, nullptr});
    CHECK_FALSE(runner.begin());
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::CLOCK));
    CHECK(runner.report().setup_enable_calls == 0U);
    CHECK(runner.report().setup_pwm_calls == 0U);
    terminalPassive(runner, clock);
}

TEST_CASE("B14 D104 begin twice is terminal reentry without inventing an epoch") {
    Clock clock;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    CHECK_FALSE(runner.begin());
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::REENTRY));
    CHECK(runner.runtime().report().epochs == 0U);
    terminalPassive(runner, clock);
}

TEST_CASE("B14 B15 D104 actual first epoch retains absent BOOT EMPTY owners and real S D A C") {
    Clock clock;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    CHECK(runner.report().schema_version != 0U);
    CHECK(runner.report().byte_size == 192U);
    CHECK(clock.observed(runner.report().boot_us));
    due(runner, clock);
    CHECK(running(runner));
    checkOwners(runner);
    checkTimes(runner, clock);
    absentInputs(runner);
    emptyRecorder(runner);
    CHECK(runner.report().first_s_us == runner.report().last_s_us);
    CHECK(runner.report().first_d_us == runner.report().last_d_us);
    CHECK(runner.report().first_c_us == runner.report().last_c_us);
    CHECK(runner.report().setup_enable_calls == 1U);
    CHECK(runner.report().setup_pwm_calls == 4U);
}

TEST_CASE("B14 D104 early poll clocks admission only and does not duplicate a transaction") {
    Clock clock;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    due(runner, clock);
    const auto before = runner.report();
    poll(runner, clock);
    CHECK(running(runner));
    CHECK(runner.report().epochs == before.epochs);
    CHECK(runner.report().token_lo == before.token_lo);
    CHECK(runner.report().token_hi == before.token_hi);
    CHECK(runner.report().enable_low_calls == before.enable_low_calls);
    CHECK(runner.report().pwm_zero_calls == before.pwm_zero_calls);
    CHECK(runner.report().settle_calls == before.settle_calls);
    CHECK(runner.report().clock_calls > before.clock_calls);
}

TEST_CASE("B14 B15 D104 200 second genuine Runtime window freezes with no manufactured STOP") {
    for (const auto start : {12345U, std::numeric_limits<std::uint32_t>::max() - 1500U}) {
        Clock clock;
        clock.now = start;
        Runner runner(clock.port());
        if (!begin(runner)) continue;
        std::uint64_t previous_token = 0U;
        std::uint32_t first_s = 0U, first_d = 0U, first_c = 0U;
        for (std::uint32_t i = 0U; i < MIN_EPOCHS + 5U && running(runner); ++i) {
            due(runner, clock, i % 17U);
            const auto& tx = runner.runtime().transaction().report();
            CHECK(tx.robot.token > previous_token);
            previous_token = tx.robot.token;
            CHECK(runner.report().epochs == i + 1U);
            CHECK(runner.report().missed_releases == 0U);
            CHECK(tx.finished);
            CHECK(tx.timing_valid);
            CHECK(tx.robot.outputs.ui_state == core::State::BOOT);
            CHECK_FALSE(tx.applied.feedback.motors_enabled);
            CHECK(tx.applied.feedback.duty_l == 0.0F);
            CHECK(tx.applied.feedback.duty_r == 0.0F);
            if (i == 0U) {
                first_s = tx.started_us; first_d = tx.decision_us; first_c = tx.completed_us;
            }
            if (i % 10000U == 0U) {
                checkOwners(runner); checkTimes(runner, clock); absentInputs(runner); emptyRecorder(runner);
            }
            if (static_cast<std::uint32_t>(tx.completed_us - runner.report().boot_us) < WINDOW_US)
                CHECK(running(runner));
        }
        CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FROZEN));
        CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::NONE));
        CHECK(runner.report().elapsed_us >= WINDOW_US);
        CHECK(runner.report().elapsed_us < WINDOW_US + GUARD_US);
        CHECK(runner.report().epochs >= MIN_EPOCHS);
        CHECK(runner.report().first_s_us == first_s);
        CHECK(runner.report().first_d_us == first_d);
        CHECK(runner.report().first_c_us == first_c);
        checkOwners(runner); checkTimes(runner, clock); absentInputs(runner); emptyRecorder(runner);
        terminalPassive(runner, clock);
    }
}

TEST_CASE("B14 D104 first skipped release fails promptly and retains actual miss count") {
    Clock clock;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    due(runner, clock);
    const auto before = runner.runtime().report().epochs;
    due(runner, clock, 3U * config::TICK_US);
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::MISSED_RELEASE));
    CHECK(runner.report().missed_releases > 0U);
    CHECK(runner.report().missed_releases == runner.runtime().report().missed_releases);
    CHECK(runner.runtime().report().epochs <= before + 1U);
    CHECK(runner.runtime().report().phase == app::RuntimePhase::RUNNING);
    CHECK(runner.runtime().transaction().report().fault == app::Fault::NONE);
    terminalPassive(runner, clock);
}

TEST_CASE("B14 D104 jumping to duration cannot manufacture sufficient completed epochs") {
    Clock clock;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    due(runner, clock);
    clock.now = runner.report().boot_us + WINDOW_US;
    poll(runner, clock);
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.report().epochs < MIN_EPOCHS);
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::MISSED_RELEASE));
    terminalPassive(runner, clock);
}

TEST_CASE("B14 D104 first-epoch deadline exact and later fails before Runtime work") {
    for (const auto excess : {0U, 1U}) {
        Clock clock;
        Runner runner(clock.port());
        if (!begin(runner)) continue;
        const auto before = runner.report();
        clock.now = before.boot_us + GUARD_US + excess;
        poll(runner, clock);
        CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
        CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::DEADLINE));
        CHECK(runner.runtime().report().epochs == 0U);
        CHECK(runner.report().enable_low_calls == before.enable_low_calls);
        CHECK(runner.report().pwm_zero_calls == before.pwm_zero_calls);
        terminalPassive(runner, clock);
    }
}

TEST_CASE("B14 D104 overall deadline exact and later preserves previous real transaction") {
    for (const auto excess : {0U, 1U}) {
        Clock clock;
        Runner runner(clock.port());
        if (!begin(runner)) continue;
        due(runner, clock);
        const auto before = runner.report();
        clock.now = before.boot_us + WINDOW_US + GUARD_US + excess;
        poll(runner, clock);
        CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
        CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::DEADLINE));
        CHECK(runner.report().epochs == before.epochs);
        CHECK(runner.report().token_lo == before.token_lo);
        CHECK(runner.report().last_c_us == before.last_c_us);
        CHECK(runner.runtime().report().phase == app::RuntimePhase::RUNNING);
        terminalPassive(runner, clock);
    }
}

TEST_CASE("B14 D104 equal observations have a bounded consecutive stall failure") {
    Clock clock;
    clock.increment = 0U;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    for (std::uint32_t i = 0U; i <= config::APP_CLOCK_STALL_MAX_POLLS && running(runner); ++i)
        poll(runner, clock);
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.report().failure != static_cast<std::uint32_t>(Failure::NONE));
    CHECK(clock.calls >= config::APP_CLOCK_STALL_MAX_POLLS + 1U);
    CHECK(clock.calls <= config::APP_CLOCK_STALL_MAX_POLLS + 16U);
    CHECK(runner.report().epochs <= 1U);
    terminalPassive(runner, clock);
}

TEST_CASE("B14 D104 natural equal clocks within epochs are valid and progress clears stall") {
    Clock clock;
    clock.increment = 0U;
    Runner runner(clock.port());
    if (!begin(runner)) return;
    for (std::uint32_t i = 0U; i < 20U; ++i) {
        due(runner, clock);
        CHECK(running(runner));
        CHECK(runner.runtime().transaction().report().timing_valid);
    }
    CHECK(runner.report().epochs == 20U);
    CHECK(runner.report().maximum_execution_us == 0U);
}

TEST_CASE("B14 D104 every observed callback position rejects regression and half-range") {
    Clock baseline_clock;
    Runner baseline(baseline_clock.port());
    if (!begin(baseline)) return;
    const auto before = baseline_clock.calls;
    due(baseline, baseline_clock);
    const auto observations = baseline_clock.calls - before;
    CHECK(observations > 3U);
    for (const auto delta : {0xfffffffeU, HALF}) {
        for (std::uint64_t index = 1U; index <= observations; ++index) {
            Clock clock;
            Runner runner(clock.port());
            if (!begin(runner)) continue;
            due(runner, clock);
            clock.inject_call = clock.calls + index;
            clock.inject_delta = delta;
            // Keep the first injected observation adjacent, avoiding a scheduler-gap mask.
            if (index == 1U) clock.now -= 1U;
            else clock.now = runner.runtime().report().next_release_us;
            poll(runner, clock);
            CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
            CHECK(runner.report().failure != static_cast<std::uint32_t>(Failure::NONE));
            terminalPassive(runner, clock);
        }
    }
}

TEST_CASE("B14 D104 valid inert setup and zero writes count actual acknowledged callbacks") {
    Clock clock;
    runtime_bench::InertMotorPort owner(clock.port());
    auto port = owner.port();
    CHECK(clock.calls == 0U);
    for (const auto period : port.period_cycles) CHECK(period == 1U);
    setupPort(port);
    CHECK(owner.counters().setup_enable == 1U);
    CHECK(owner.counters().setup_pwm == 4U);
    CHECK(owner.counters().enable_low == 1U);
    CHECK(owner.counters().pwm_zero == 4U);
    CHECK(owner.counters().settle == 1U);
    CHECK_FALSE(owner.counters().fault);
    CHECK_FALSE(owner.counters().saturated);
    for (unsigned i = 0U; i < 10000U; ++i) {
        CHECK(port.writeEnable(port.context, false));
        CHECK(port.writePwm(port.context, static_cast<motors::Channel>(i % 4U), 1U, 0U));
        CHECK(port.settle(port.context));
    }
    CHECK(owner.counters().enable_low == 10001U);
    CHECK(owner.counters().pwm_zero == 10004U);
    CHECK(owner.counters().settle == 10001U);
    CHECK(port.clockUs(port.context) == 12345U);
    CHECK(owner.counters().clock == 1U);
    CHECK(clock.calls == 1U);
}

TEST_CASE("B14 D104 active enable and each nonzero PWM channel latch refusal") {
    for (unsigned which = 0U; which < 5U; ++which) {
        Clock clock;
        runtime_bench::InertMotorPort owner(clock.port());
        auto port = owner.port();
        setupPort(port);
        if (which == 0U) {
            CHECK_FALSE(port.writeEnable(port.context, true));
            CHECK(owner.counters().enabled == 1U);
        } else {
            CHECK_FALSE(port.writePwm(port.context, static_cast<motors::Channel>(which - 1U), 1U, 1U));
            CHECK(owner.counters().nonzero == 1U);
        }
        checkLatch(owner, port);
    }
}

TEST_CASE("B14 D104 invalid channel and wrong period cannot return a zero success") {
    for (unsigned which = 0U; which < 6U; ++which) {
        Clock clock;
        runtime_bench::InertMotorPort owner(clock.port());
        auto port = owner.port();
        setupPort(port);
        if (which < 2U)
            CHECK_FALSE(port.configurePwm(port.context, static_cast<motors::Channel>(4U + 251U * which)));
        else if (which < 4U)
            CHECK_FALSE(port.writePwm(port.context, static_cast<motors::Channel>(4U + 251U * (which - 2U)), 1U, 0U));
        else
            CHECK_FALSE(port.writePwm(port.context, motors::Channel::LEFT_FORWARD, which == 4U ? 0U : 2U, 0U));
        CHECK(owner.counters().invalid >= 1U);
        checkLatch(owner, port);
    }
}

TEST_CASE("B14 D104 missing duplicated or premature setup latches invalid order") {
    for (unsigned which = 0U; which < 8U; ++which) {
        Clock clock;
        runtime_bench::InertMotorPort owner(clock.port());
        auto port = owner.port();
        if (which == 0U) CHECK_FALSE(port.configurePwm(port.context, motors::Channel::LEFT_FORWARD));
        if (which == 1U) CHECK_FALSE(port.writeEnable(port.context, false));
        if (which == 2U) CHECK_FALSE(port.writePwm(port.context, motors::Channel::LEFT_FORWARD, 1U, 0U));
        if (which == 3U) CHECK_FALSE(port.settle(port.context));
        if (which >= 4U) CHECK(port.configureEnableLow(port.context));
        if (which == 4U) CHECK_FALSE(port.configureEnableLow(port.context));
        if (which == 5U) CHECK_FALSE(port.settle(port.context));
        if (which == 6U) {
            CHECK(port.writeEnable(port.context, false));
            CHECK(port.configurePwm(port.context, motors::Channel::LEFT_FORWARD));
            CHECK_FALSE(port.configurePwm(port.context, motors::Channel::LEFT_FORWARD));
        }
        if (which == 7U) {
            CHECK(port.writeEnable(port.context, false));
            CHECK(port.configurePwm(port.context, motors::Channel::LEFT_FORWARD));
            CHECK_FALSE(port.settle(port.context));
        }
        CHECK(owner.counters().invalid >= 1U);
        checkLatch(owner, port);
    }
}
