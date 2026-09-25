// Tests D186 observation around actual Runtime, Transaction, Robot and MotorGate.
// Derives expected admission, timing and failure order from public contracts.
// Run only through the serial RAM-backed test_app_motor_fault.py driver.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "app_motor_fault.h"
#include <array>
#include <cstdint>

namespace {
using app_motor_fault::Phase;
using app_motor_fault::Reason;
using motor_fault::Operation;
using motor_fault::Stage;

struct Native {
    app_motor_fault::Runner* owner = nullptr;
    std::uint32_t now = 10000U, clocks = 0U, calls = 0U;
    std::uint32_t reverse_call = 0U, reverse_clock = 0U;
    std::uint32_t callback_work = 0U, peripheral_calls = 0U;
    std::array<bool, 128> failure{};
    std::uint32_t finalizing_observations = 0U;
    bool unsafe = false;

    static Native& self(void* p) { return *static_cast<Native*>(p); }
    static std::uint32_t clock(void* p) {
        auto& n = self(p); ++n.clocks;
        return n.clocks == n.reverse_clock ? n.now - 1U : n.now;
    }
    bool callback(Operation operation, bool high = false, std::uint32_t pulse = 0U) {
        ++calls; unsafe = unsafe || high || pulse != 0U;
        if (owner != nullptr) observe(operation);
        if (calls == reverse_call) --now;
        now += callback_work;
        return calls >= failure.size() || !failure[calls];
    }
    void observe(Operation operation) {
        const auto& t = owner->trace();
        REQUIRE(t.has_current);
        CHECK(t.current.operation == operation);
        CHECK(t.current.invoked);
        CHECK_FALSE(t.current.completed);
        const auto& r = owner->report();
        CHECK(r.begin_called);
        if (r.phase == Phase::RUNNING && t.current.stage == Stage::SETUP)
            CHECK_FALSE(r.begin_finished);
        if (r.phase != Phase::FINALIZING) return;
        ++finalizing_observations;
        CHECK(r.before_abort_valid); CHECK(r.abort_called);
        CHECK_FALSE(r.abort_returned); CHECK_FALSE(owner->active());
        CHECK(t.current.stage == Stage::HALT);
        const auto count = calls, read_count = clocks;
        owner->poll(); CHECK_FALSE(owner->begin({true}));
        CHECK(calls == count); CHECK(clocks == read_count);
    }
    static bool configureEnable(void* p) {
        return self(p).callback(Operation::CONFIGURE_ENABLE);
    }
    static bool configurePwm(void* p, motors::Channel) {
        return self(p).callback(Operation::CONFIGURE_PWM);
    }
    static bool enable(void* p, bool high) {
        return self(p).callback(Operation::ENABLE, high);
    }
    static bool pwm(void* p, motors::Channel, std::uint32_t, std::uint32_t pulse) {
        return self(p).callback(Operation::PWM, false, pulse);
    }
    static bool settle(void* p) { return self(p).callback(Operation::SETTLE); }
    motors::Port port() {
        return {this, configureEnable, configurePwm, enable, pwm, settle, clock,
            {1000U, 1001U, 1002U, 1003U}};
    }
    static power::InitResult adcSetup(void* p) { ++self(p).peripheral_calls; return {}; }
    static power::Sample a0(void* p) { ++self(p).peripheral_calls; return {}; }
    static power::ButtonSample a1(void* p) { ++self(p).peripheral_calls; return {}; }
    static std::uint32_t adcClock(void* p) { ++self(p).peripheral_calls; return 0U; }
    power::InputPort adc() { return {this, adcSetup, a0, a1, adcClock}; }
    static opp_sensors::InitResult oppSetup(void* p) { ++self(p).peripheral_calls; return {}; }
    static opp_sensors::Snapshot opponents(void* p) { ++self(p).peripheral_calls; return {}; }
    static line_qtr::Status linesSetup(void* p, bool) { ++self(p).peripheral_calls; return {}; }
    static line_qtr::Status linesStart(void* p) { ++self(p).peripheral_calls; return {}; }
    static line_qtr::Snapshot lines(void* p) { ++self(p).peripheral_calls; return {}; }
    static imu::SetupReport imuSetup(void* p, std::uint32_t, bool) {
        ++self(p).peripheral_calls; return {};
    }
    static imu::SetupReport imuAdvance(void* p, std::uint32_t) {
        ++self(p).peripheral_calls; return {};
    }
    static imu::SampleProgress imuSample(void* p, std::uint32_t) {
        ++self(p).peripheral_calls; return {};
    }
    static imu::Sample imuFailure(void* p, std::uint32_t) {
        ++self(p).peripheral_calls; return {};
    }
    static ui::MatrixStatus matrixSetup(void* p, ui::MatrixGrant) {
        ++self(p).peripheral_calls; return {};
    }
    static ui::MatrixStatus matrix(void* p, std::uint32_t, const ui::Frame&) {
        ++self(p).peripheral_calls; return {};
    }
    app::SourcePort sources() {
        return {this, oppSetup, opponents, linesSetup, linesStart, lines, lines,
            lines, imuSetup, imuAdvance, imuSample, imuSample, imuSample,
            imuFailure, matrixSetup, matrix};
    }
    static recorder::dump::NativeStatus dumpSetup(void* p, const recorder::dump::SetupGrant&) {
        ++self(p).peripheral_calls; return {};
    }
    static bool dumpReady(void* p) { ++self(p).peripheral_calls; return true; }
    app::DumpPort dump() { return {this, dumpSetup, dumpReady, {}}; }
};

struct Rig {
    Native native;
    app_motor_fault::Runner owner{native.port(), native.adc(), native.sources(), native.dump()};
    Rig() { native.owner = &owner; }
    void next() {
        native.now = owner.runtime().report().next_release_us;
        owner.poll();
    }
};

void zeroReceipt(const app::TransactionReport& t) {
    REQUIRE(t.decision_made); CHECK(t.applied.consumed);
    const auto& p = t.applied.feedback;
    CHECK(p.applied_valid); CHECK(p.token == t.robot.token);
    CHECK_FALSE(p.motors_enabled); CHECK(p.duty_l == 0.0F); CHECK(p.duty_r == 0.0F);
}
void samePrevious(const fsm::PreviousTick& a, const fsm::PreviousTick& b) {
    CHECK(a.applied_valid == b.applied_valid); CHECK(a.token == b.token);
    CHECK(a.applied_us == b.applied_us); CHECK(a.motors_enabled == b.motors_enabled);
    CHECK(a.duty_l == b.duty_l); CHECK(a.duty_r == b.duty_r);
    CHECK(a.duration_valid == b.duration_valid); CHECK(a.completed_us == b.completed_us);
    CHECK(a.execution_us == b.execution_us);
}
void sameHalt(const motors::HaltResult& a, const motors::HaltResult& b) {
    CHECK(a.fresh == b.fresh); CHECK(a.attempted == b.attempted);
    CHECK(a.inhibition_confirmed == b.inhibition_confirmed);
    CHECK(a.timing_valid == b.timing_valid); CHECK(a.started_us == b.started_us);
    CHECK(a.completed_us == b.completed_us); CHECK(a.fault == b.fault);
}
void terminal(Rig& r, Reason reason) {
    const auto& report = r.owner.report();
    REQUIRE(report.phase == Phase::FROZEN); CHECK(report.reason == reason);
    CHECK(report.before_abort_valid); CHECK(report.abort_called); CHECK(report.abort_returned);
    CHECK_FALSE(r.owner.active()); CHECK_FALSE(r.native.unsafe);
    const auto count = r.native.calls, clocks = r.native.clocks;
    const auto token = report.before_abort.transaction.robot.token;
    for (unsigned i = 0U; i < 3U; ++i) {
        r.native.now += config::TICK_US; r.owner.poll();
        CHECK_FALSE(r.owner.begin({true})); CHECK_FALSE(r.owner.begin({}));
    }
    CHECK(r.native.calls == count); CHECK(r.native.clocks == clocks);
    CHECK(report.before_abort.transaction.robot.token == token);
    CHECK(r.native.peripheral_calls == 0U);
}
void allLow(const Rig& r) {
    CHECK_FALSE(r.native.unsafe);
    const auto& trace = r.owner.trace();
    REQUIRE(trace.count <= motor_fault::TRACE_CAPACITY);
    for (std::uint32_t i = 0U; i < trace.count; ++i) {
        const auto& call = trace.calls[i];
        CHECK_FALSE(call.requested_high); CHECK(call.pulse_cycles == 0U);
        CHECK(call.invoked); CHECK(call.completed);
    }
}
Reason orderedReason(const app_motor_fault::Runner& owner) {
    const auto& trace = owner.trace();
    if (trace.has_failure) return Reason::CALLBACK_FAILURE;
    if (trace.overflow || trace.timing_fault) return Reason::TRACE_INVALID;
    const auto& snap = owner.report().before_abort;
    const auto& t = snap.transaction;
    const auto& f = t.applied.feedback;
    if (t.decision_made && (!t.applied.consumed || !f.applied_valid ||
        f.token != t.robot.token || f.motors_enabled || f.duty_l != 0.0F || f.duty_r != 0.0F))
        return Reason::APPLICATION_INVALID;
    if (snap.runtime.phase == app::RuntimePhase::FAULT ||
        snap.runtime.phase == app::RuntimePhase::STOPPED) return Reason::RUNTIME_TERMINAL;
    if (snap.runtime.epochs >= app_motor_fault::EPOCH_SAMPLES) return Reason::EPOCH_LIMIT;
    return Reason::NONE;
}
} // namespace

TEST_CASE("B0 D186 construction accessors pre-start and denied admission are passive") {
    Rig r;
    CHECK(r.owner.report().phase == Phase::NOT_STARTED);
    CHECK(r.owner.report().reason == Reason::NONE); CHECK_FALSE(r.owner.active());
    r.owner.poll(); CHECK(r.native.calls == 0U); CHECK(r.native.clocks == 0U);
    CHECK(r.owner.begin({})); CHECK(r.owner.report().phase == Phase::DISABLED);
    CHECK_FALSE(r.owner.report().begin_called); CHECK_FALSE(r.owner.report().abort_called);
    CHECK_FALSE(r.owner.begin({true})); r.owner.poll();
    CHECK(r.native.calls == 0U); CHECK(r.native.clocks == 0U);
    CHECK(r.native.peripheral_calls == 0U);
}

TEST_CASE("B0 B14 D186 four actual empty-grant epochs produce exactly 41 safe callbacks") {
    Rig r; REQUIRE(r.owner.begin({true})); CHECK(r.owner.report().begin_finished);
    CHECK(r.owner.report().begin_ok); CHECK(r.native.calls == 11U);
    const auto setup_clocks = r.native.clocks;
    CHECK_FALSE(r.owner.begin({true})); CHECK(r.native.clocks == setup_clocks);
    for (std::uint32_t epoch = 1U; epoch <= 4U; ++epoch) {
        r.next(); CHECK(r.owner.report().last_step_returned);
        const auto& t = epoch == 4U ? r.owner.report().before_abort.transaction :
            r.owner.runtime().transaction().report();
        zeroReceipt(t); CHECK(t.robot.token == epoch);
        CHECK(t.robot.outputs.ui_state == core::State::BOOT);
        CHECK(r.owner.runtime().report().epochs == epoch);
        if (epoch != 4U) CHECK(r.owner.active());
    }
    terminal(r, Reason::EPOCH_LIMIT); REQUIRE(r.native.calls == 41U);
    REQUIRE(r.owner.trace().count == 41U); CHECK_FALSE(r.owner.trace().has_failure);
    CHECK_FALSE(r.owner.trace().timing_fault); CHECK_FALSE(r.owner.trace().overflow);
    CHECK(r.native.finalizing_observations == 6U);
    for (std::uint32_t i = 0U; i < 41U; ++i) {
        const auto& c = r.owner.trace().calls[i]; CHECK(c.returned); CHECK(c.timing_valid);
        const auto stage = i < 11U ? Stage::SETUP : (i < 35U ? Stage::APPLY : Stage::HALT);
        const auto ordinal = i < 11U ? 0U : (i < 35U ? 1U + (i - 11U) / 6U : 4U);
        CHECK(c.stage == stage); CHECK(c.application == ordinal);
    }
    const auto& snap = r.owner.report().before_abort;
    CHECK(snap.runtime.phase == app::RuntimePhase::RUNNING); CHECK(snap.runtime.epochs == 4U);
    CHECK(snap.transaction.finished); CHECK(snap.transaction.timing_valid);
    CHECK(snap.transaction.phase == app::Phase::IDLE);
    CHECK(snap.previous.applied_valid); CHECK(snap.previous.duration_valid);
    auto completed = snap.transaction.applied.feedback;
    completed.duration_valid = true;
    completed.completed_us = snap.transaction.completed_us;
    completed.execution_us = snap.transaction.execution_us;
    samePrevious(snap.previous, completed);
    CHECK_FALSE(r.owner.runtime().transaction().previous().applied_valid);
    CHECK(r.owner.runtime().transaction().report().halt.inhibition_confirmed);
    CHECK_FALSE(r.owner.runtime().report().initialization_complete);
    CHECK(r.owner.runtime().report().raw_lines); allLow(r);
}

TEST_CASE("B14 D186 early polls and late releases stay on the real Runtime grid") {
    Rig r; REQUIRE(r.owner.begin({true})); const auto anchor = r.native.now;
    r.next(); REQUIRE(r.owner.runtime().report().epochs == 1U);
    const auto count = r.native.calls;
    r.native.now = anchor + 999U; r.owner.poll();
    CHECK_FALSE(r.owner.report().last_step_returned); CHECK(r.native.calls == count);
    CHECK(r.owner.runtime().report().epochs == 1U);
    r.native.now = anchor + 4500U; r.owner.poll();
    CHECK(r.owner.runtime().report().epochs == 2U);
    CHECK(r.owner.runtime().report().missed_releases == 3U);
    CHECK(r.owner.runtime().report().next_release_us == anchor + 5000U);
    CHECK(r.owner.runtime().transaction().report().started_us == anchor + 4500U);
    CHECK(r.owner.trace().calls[count].application == 2U);
    r.next(); r.next(); terminal(r, Reason::EPOCH_LIMIT); allLow(r);
}

TEST_CASE("B14 D186 natural wrap and callback execution never invent catch-up applications") {
    for (auto origin : {0U, 0xFFFFFF00U}) {
        Rig r; r.native.now = origin; REQUIRE(r.owner.begin({true}));
        r.native.callback_work = 200U; r.next();
        const auto& t = r.owner.runtime().transaction().report();
        CHECK(t.execution_us == 1200U); CHECK(t.completed_us == origin + 1200U);
        CHECK(r.owner.runtime().report().epochs == 1U);
        CHECK(r.owner.runtime().report().missed_releases == 1U);
        CHECK(r.owner.runtime().report().next_release_us == origin + 2000U);
        CHECK(r.owner.active()); r.native.callback_work = 0U;
        r.next(); r.next(); r.next(); terminal(r, Reason::EPOCH_LIMIT); allLow(r);
    }
}

TEST_CASE("B0 D186 every setup callback failure retains setup precedence and first failure") {
    for (std::uint32_t failed = 1U; failed <= 11U; ++failed) {
        CAPTURE(failed); Rig r; r.native.failure[failed] = true;
        CHECK_FALSE(r.owner.begin({true})); terminal(r, Reason::SETUP_FAILED);
        CHECK(r.owner.report().begin_called); CHECK(r.owner.report().begin_finished);
        CHECK_FALSE(r.owner.report().begin_ok); REQUIRE(r.owner.trace().has_failure);
        const auto& first = r.owner.trace().first_failure;
        CHECK(first.stage == Stage::SETUP); CHECK(first.application == 0U);
        CHECK_FALSE(first.returned); CHECK(first.completed);
        CHECK(first.operation == r.owner.trace().calls[failed - 1U].operation);
        sameHalt(r.owner.report().before_abort.transaction.halt,
            r.owner.runtime().transaction().report().halt);
        CHECK(r.native.finalizing_observations == 0U); allLow(r);
    }
}

TEST_CASE("B0 D186 every callback position of each actual application retains first failure") {
    for (std::uint32_t epoch = 1U; epoch <= 4U; ++epoch) {
        for (std::uint32_t offset = 0U; offset < 6U; ++offset) {
            CAPTURE(epoch); CAPTURE(offset); Rig r; REQUIRE(r.owner.begin({true}));
            for (std::uint32_t i = 1U; i < epoch; ++i) r.next();
            const auto failed = r.native.calls + offset + 1U;
            r.native.failure[failed] = true; r.next();
            terminal(r, Reason::CALLBACK_FAILURE); REQUIRE(r.owner.trace().has_failure);
            const auto& f = r.owner.trace().first_failure;
            CHECK(f.stage == Stage::APPLY); CHECK(f.application == epoch);
            CHECK_FALSE(f.returned); CHECK(f.completed);
            CHECK(f.operation == r.owner.trace().calls[failed - 1U].operation);
            CHECK_FALSE(r.owner.report().before_abort.transaction.applied.feedback.applied_valid);
            allLow(r);
        }
    }
}

TEST_CASE("B0 D186 abort failures cannot replace epoch-limit reason or pre-abort receipt") {
    for (std::uint32_t offset = 0U; offset < 6U; ++offset) {
        Rig r; REQUIRE(r.owner.begin({true}));
        r.native.failure[36U + offset] = true;
        for (unsigned i = 0U; i < 4U; ++i) r.next();
        terminal(r, Reason::EPOCH_LIMIT); zeroReceipt(r.owner.report().before_abort.transaction);
        CHECK(r.owner.report().before_abort.previous.applied_valid);
        REQUIRE(r.owner.trace().has_failure); CHECK(r.owner.trace().first_failure.stage == Stage::HALT);
        CHECK(r.owner.trace().first_failure.application == 4U);
        CHECK_FALSE(r.owner.runtime().transaction().report().halt.inhibition_confirmed);
        CHECK(r.native.calls == 41U); allLow(r);
    }
}

TEST_CASE("B0 D186 repeated cleanup failures and clock faults preserve first callback reason") {
    Rig r; REQUIRE(r.owner.begin({true}));
    for (unsigned i = 12U; i < r.native.failure.size(); ++i) r.native.failure[i] = true;
    r.native.reverse_call = 12U; r.next();
    terminal(r, Reason::CALLBACK_FAILURE); REQUIRE(r.owner.trace().has_failure);
    CHECK(r.owner.trace().timing_fault); CHECK(r.owner.trace().first_failure.operation == Operation::ENABLE);
    CHECK(r.owner.trace().first_failure.stage == Stage::APPLY);
    CHECK(r.owner.trace().first_failure.application == 1U); allLow(r);
}

TEST_CASE("B14 D186 callback time reversal uses trace-invalid priority without invented command") {
    Rig r; REQUIRE(r.owner.begin({true})); r.native.reverse_call = 12U; r.next();
    terminal(r, Reason::TRACE_INVALID); CHECK(r.owner.trace().timing_fault);
    CHECK_FALSE(r.owner.trace().has_failure); allLow(r);
}

TEST_CASE("B14 D186 outer backward and half-range clocks preserve Runtime terminal evidence") {
    for (auto elapsed : {0xFFFFFFFFU, 0x80000000U}) {
        Rig r; REQUIRE(r.owner.begin({true})); r.native.now += elapsed; r.owner.poll();
        terminal(r, Reason::RUNTIME_TERMINAL); CHECK_FALSE(r.owner.report().last_step_returned);
        CHECK(r.owner.report().before_abort.runtime.fault == app::RuntimeFault::CLOCK);
        CHECK(r.owner.report().before_abort.runtime.epochs == 0U);
        CHECK_FALSE(r.owner.report().before_abort.transaction.decision_made);
        sameHalt(r.owner.report().before_abort.transaction.halt,
            r.owner.runtime().transaction().report().halt);
        CHECK(r.native.finalizing_observations == 0U);
        for (std::uint32_t i = 11U; i < r.owner.trace().count; ++i)
            CHECK(r.owner.trace().calls[i].stage == Stage::APPLY);
        allLow(r);
    }
}

TEST_CASE("B14 D186 finitely stalled equal clock freezes without a second real epoch") {
    Rig r; REQUIRE(r.owner.begin({true})); r.next();
    for (std::uint32_t i = 0U; i < config::APP_CLOCK_STALL_MAX_POLLS + 1U && r.owner.active(); ++i)
        r.owner.poll();
    terminal(r, Reason::RUNTIME_TERMINAL);
    CHECK(r.owner.report().before_abort.runtime.fault == app::RuntimeFault::CLOCK);
    CHECK(r.owner.report().before_abort.runtime.epochs == 1U);
    CHECK(r.owner.report().before_abort.transaction.robot.token == 1U); allLow(r);
}

TEST_CASE("B14 D186 single clock glitches preserve ordered evidence across real pipeline") {
    Rig baseline; REQUIRE(baseline.owner.begin({true}));
    const auto setup_reads = baseline.native.clocks; baseline.next();
    const auto epoch_reads = baseline.native.clocks - setup_reads;
    REQUIRE(epoch_reads > 0U);
    for (std::uint32_t read = 1U; read <= epoch_reads; ++read) {
        CAPTURE(read); Rig r; REQUIRE(r.owner.begin({true}));
        r.native.reverse_clock = r.native.clocks + read; r.next();
        if (r.owner.active()) {
            r.native.reverse_clock = 0U;
            for (unsigned i = 0U; i < 4U && r.owner.active(); ++i) r.next();
        }
        REQUIRE(r.owner.report().phase == Phase::FROZEN);
        CHECK(r.owner.report().reason == orderedReason(r.owner)); allLow(r);
    }
}

TEST_CASE("B0 D186 missing native callbacks clock and invalid periods are terminal setup evidence") {
    for (unsigned missing = 0U; missing < 8U; ++missing) {
        CAPTURE(missing); Native n; auto p = n.port();
        if (missing == 0U) p.configureEnableLow = nullptr;
        if (missing == 1U) p.configurePwm = nullptr;
        if (missing == 2U) p.writeEnable = nullptr;
        if (missing == 3U) p.writePwm = nullptr;
        if (missing == 4U) p.settle = nullptr;
        if (missing == 5U) p.clockUs = nullptr;
        if (missing == 6U) p.period_cycles[0] = 0U;
        if (missing == 7U) p.period_cycles[3] = 16777217U;
        app_motor_fault::Runner owner{p, {}, {}}; n.owner = &owner;
        CHECK_FALSE(owner.begin({true})); CHECK(owner.report().phase == Phase::FROZEN);
        CHECK(owner.report().reason == Reason::SETUP_FAILED); CHECK(owner.report().before_abort_valid);
        const auto calls = n.calls, clocks = n.clocks; owner.poll(); CHECK_FALSE(owner.begin({true}));
        CHECK(n.calls == calls); CHECK(n.clocks == clocks); CHECK_FALSE(n.unsafe);
    }
}

TEST_CASE("B0 D186 absent peripheral ports remain absent through full diagnostic") {
    Native n; app_motor_fault::Runner owner{n.port(), {}, {}}; n.owner = &owner;
    REQUIRE(owner.begin({true}));
    for (unsigned i = 0U; i < 4U; ++i) { n.now = owner.runtime().report().next_release_us; owner.poll(); }
    CHECK(owner.report().phase == Phase::FROZEN); CHECK(owner.report().reason == Reason::EPOCH_LIMIT);
    CHECK(n.calls == 41U); CHECK_FALSE(n.unsafe);
}
