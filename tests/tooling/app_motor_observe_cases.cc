// Tests D192 observation around actual Runtime, Transaction, Robot and MotorGate.
// Derives expected admission, timing and failure order from public contracts.
// Run only through the serial RAM-backed test_app_motor_observe.py driver.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "app_motor_observe.h"
#include <array>
#include <cstdint>
#include <type_traits>

static_assert(!std::is_copy_constructible_v<app_motor_observe::Runner>);
static_assert(!std::is_copy_assignable_v<app_motor_observe::Runner>);
static_assert(static_cast<unsigned>(app_motor_observe::Reason::POLL_LIMIT) == 7U);

namespace {
using app_motor_observe::Phase;
using app_motor_observe::Reason;
using motor_fault::Operation;
using motor_fault::Stage;

struct Native {
    app_motor_observe::Runner* owner = nullptr;
    std::uint32_t now = 10000U, clocks = 0U, calls = 0U;
    std::uint32_t reverse_call = 0U, reverse_clock = 0U;
    std::uint32_t callback_work = 0U, peripheral_calls = 0U;
    std::array<bool, 128> failure{};
    std::uint32_t fail_at = 0U, fail_from = 0U;
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
        return calls != fail_at && (fail_from == 0U || calls < fail_from) &&
            (calls >= failure.size() || !failure[calls]);
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
        if (r.phase == Phase::RUNNING && t.current.stage == Stage::APPLY)
            CHECK(r.polls > 0U);
        if (r.phase != Phase::FINALIZING) return;
        ++finalizing_observations;
        CHECK(r.before_abort_valid); CHECK(r.abort_called);
        CHECK(r.reason != Reason::NONE);
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
    app_motor_observe::Runner owner{native.port(), native.adc(), native.sources(), native.dump()};
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
[[maybe_unused]] void sameHalt(const motors::HaltResult& a, const motors::HaltResult& b) {
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
    const auto count = r.native.calls, clocks = r.native.clocks, polls = report.polls;
    const auto token = report.before_abort.transaction.robot.token;
    for (unsigned i = 0U; i < 3U; ++i) {
        r.native.now += config::TICK_US; r.owner.poll();
        CHECK_FALSE(r.owner.begin({true})); CHECK_FALSE(r.owner.begin({}));
    }
    CHECK(r.native.calls == count); CHECK(r.native.clocks == clocks);
    CHECK(report.polls == polls);
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
[[maybe_unused]] Reason orderedReason(const app_motor_observe::Runner& owner) {
    const auto& trace = owner.trace();
    if (trace.has_failure) return Reason::CALLBACK_FAILURE;
    if (trace.timing_fault) return Reason::TRACE_INVALID;
    const auto& snap = owner.report().before_abort;
    const auto& t = snap.transaction;
    const auto& f = t.applied.feedback;
    if (t.decision_made && (!t.applied.consumed || !f.applied_valid ||
        f.token != t.robot.token || f.motors_enabled || f.duty_l != 0.0F || f.duty_r != 0.0F))
        return Reason::APPLICATION_INVALID;
    if (snap.runtime.phase == app::RuntimePhase::FAULT ||
        snap.runtime.phase == app::RuntimePhase::STOPPED) return Reason::RUNTIME_TERMINAL;
    if (snap.runtime.epochs >= config::APP_MOTOR_OBSERVE_EPOCHS) return Reason::EPOCH_LIMIT;
    if (owner.report().polls >= config::APP_MOTOR_OBSERVE_MAX_POLLS) return Reason::POLL_LIMIT;
    return Reason::NONE;
}
} // namespace

namespace {
void finish(Rig& r) {
    for (std::uint32_t i = 0U; i < config::APP_MOTOR_OBSERVE_EPOCHS && r.owner.active(); ++i)
        r.next();
    REQUIRE_FALSE(r.owner.active());
}
[[maybe_unused]] void sameCall(const motor_fault::Call& a, const motor_fault::Call& b) {
    CHECK(a.stage == b.stage); CHECK(a.operation == b.operation);
    CHECK(a.channel == b.channel); CHECK(a.application == b.application);
    CHECK(a.requested_high == b.requested_high); CHECK(a.period_cycles == b.period_cycles);
    CHECK(a.pulse_cycles == b.pulse_cycles); CHECK(a.invoked == b.invoked);
    CHECK(a.completed == b.completed); CHECK(a.returned == b.returned);
    CHECK(a.timing_valid == b.timing_valid); CHECK(a.started_us == b.started_us);
    CHECK(a.completed_us == b.completed_us);
}
Operation applicationOperation(std::uint32_t offset) {
    return offset == 0U ? Operation::ENABLE : (offset == 5U ? Operation::SETTLE : Operation::PWM);
}
[[maybe_unused]] void prefixCall(const motor_fault::Call& c, std::uint32_t index, std::uint32_t anchor) {
    const bool setup = index < 11U;
    const auto offset = setup ? index : (index - 11U) % 6U;
    const auto epoch = setup ? 0U : 1U + (index - 11U) / 6U;
    auto operation = applicationOperation(offset);
    if (setup) operation = index == 0U ? Operation::CONFIGURE_ENABLE :
        (index == 1U ? Operation::ENABLE : (index < 6U ? Operation::CONFIGURE_PWM :
        (index < 10U ? Operation::PWM : Operation::SETTLE)));
    CHECK(c.stage == (setup ? Stage::SETUP : Stage::APPLY));
    CHECK(c.application == epoch); CHECK(c.operation == operation);
    if (operation == Operation::PWM || operation == Operation::CONFIGURE_PWM) {
        const auto channel = setup ? (index < 6U ? index - 2U : index - 6U) : offset - 1U;
        CHECK(c.channel == static_cast<motors::Channel>(channel));
        CHECK(c.period_cycles == (operation == Operation::PWM ? 1000U + channel : 0U));
    }
    CHECK_FALSE(c.requested_high); CHECK(c.pulse_cycles == 0U);
    CHECK(c.invoked); CHECK(c.completed); CHECK(c.returned); CHECK(c.timing_valid);
    CHECK(c.started_us == anchor + (setup ? 0U : (epoch - 1U) * config::TICK_US));
    CHECK(c.completed_us == c.started_us);
}
void frozenReceipt(Rig& r, std::uint32_t epochs) {
    const auto& snap = r.owner.report().before_abort;
    CHECK(snap.runtime.phase == app::RuntimePhase::RUNNING);
    CHECK(snap.runtime.fault == app::RuntimeFault::NONE);
    CHECK(snap.runtime.epochs == epochs); CHECK(snap.runtime.missed_releases == 0U);
    CHECK(snap.transaction.finished); CHECK(snap.transaction.timing_valid);
    CHECK(snap.transaction.phase == app::Phase::IDLE);
    CHECK(snap.transaction.fault == app::Fault::NONE);
    zeroReceipt(snap.transaction); CHECK(snap.transaction.robot.token == epochs);
    CHECK(snap.previous.applied_valid); CHECK(snap.previous.duration_valid);
    auto completed = snap.transaction.applied.feedback;
    completed.duration_valid = true;
    completed.completed_us = snap.transaction.completed_us;
    completed.execution_us = snap.transaction.execution_us;
    samePrevious(snap.previous, completed);
    CHECK_FALSE(r.owner.runtime().transaction().previous().applied_valid);
    CHECK_FALSE(r.owner.runtime().report().initialization_complete);
    CHECK(r.owner.runtime().report().raw_lines);
}
} // namespace

TEST_CASE("B0 D192 constructors accessors denied grant and repeats are passive") {
    Rig r;
    const auto& report = r.owner.report();
    CHECK(report.phase == Phase::NOT_STARTED); CHECK(report.reason == Reason::NONE);
    CHECK_FALSE(report.begin_called); CHECK_FALSE(report.begin_finished);
    CHECK_FALSE(report.begin_ok); CHECK_FALSE(report.before_abort_valid);
    CHECK_FALSE(report.abort_called); CHECK_FALSE(report.abort_returned);
    CHECK_FALSE(report.last_step_returned); CHECK(report.polls == 0U);
    CHECK_FALSE(r.owner.active()); CHECK(r.owner.trace().count == 0U);
    CHECK(r.owner.runtime().report().epochs == 0U);
    r.owner.poll(); CHECK(r.native.calls == 0U); CHECK(r.native.clocks == 0U);
    CHECK(r.owner.begin({})); CHECK(report.phase == Phase::DISABLED);
    CHECK_FALSE(r.owner.begin({true})); CHECK_FALSE(r.owner.begin({})); r.owner.poll();
    CHECK_FALSE(report.begin_called); CHECK_FALSE(report.abort_called);
    CHECK(report.polls == 0U); CHECK(r.native.calls == 0U); CHECK(r.native.clocks == 0U);
    CHECK(r.native.peripheral_calls == 0U);
}

#ifndef OBSERVE_BOUNDARY_FIXTURE
TEST_CASE("B0 B14 D192 10000 real epochs preserve first 64 calls and report 59953 rejected") {
    REQUIRE(config::APP_MOTOR_OBSERVE_EPOCHS == 10000U);
    REQUIRE(config::APP_MOTOR_OBSERVE_MAX_POLLS == 10000000U);
    Rig r; const auto anchor = r.native.now; REQUIRE(r.owner.begin({true}));
    CHECK(r.owner.report().begin_finished); CHECK(r.owner.report().begin_ok);
    CHECK(r.native.calls == 11U); CHECK(r.owner.report().polls == 0U);
    const auto clocks = r.native.clocks; CHECK_FALSE(r.owner.begin({true}));
    CHECK(r.native.clocks == clocks); CHECK(r.native.calls == 11U);
    std::array<motor_fault::Call, motor_fault::TRACE_CAPACITY> prefix{};
    for (std::uint32_t epoch = 1U; epoch <= 10000U; ++epoch) {
        r.next(); CHECK(r.owner.report().polls == epoch);
        CHECK(r.owner.report().last_step_returned);
        CHECK(r.owner.runtime().report().epochs == epoch);
        const auto& t = epoch == 10000U ? r.owner.report().before_abort.transaction :
            r.owner.runtime().transaction().report();
        zeroReceipt(t); CHECK(t.robot.token == epoch);
        CHECK(t.robot.outputs.ui_state == core::State::BOOT);
        if (epoch != 10000U) CHECK(r.owner.active());
        if (epoch == 4U) CHECK(r.native.calls == 35U);
        if (epoch == 8U) CHECK_FALSE(r.owner.trace().overflow);
        if (epoch == 9U) {
            REQUIRE(r.owner.trace().count == 64U); CHECK(r.owner.trace().overflow);
            CHECK(r.owner.trace().rejected == 1U);
            for (std::uint32_t i = 0U; i < prefix.size(); ++i) prefix[i] = r.owner.trace().calls[i];
        }
    }
    terminal(r, Reason::EPOCH_LIMIT); REQUIRE(r.native.calls == 60017U);
    const auto& trace = r.owner.trace();
    REQUIRE(trace.count == 64U); CHECK(trace.rejected == 59953U); CHECK(trace.overflow);
    CHECK_FALSE(trace.has_failure); CHECK_FALSE(trace.timing_fault);
    CHECK(trace.clock_reads == r.native.clocks); CHECK(r.native.finalizing_observations == 6U);
    for (std::uint32_t i = 0U; i < trace.count; ++i) {
        prefixCall(trace.calls[i], i, anchor); sameCall(trace.calls[i], prefix[i]);
    }
    CHECK(trace.has_current); CHECK(trace.current.stage == Stage::HALT);
    CHECK(trace.current.application == 10000U); CHECK(trace.current.operation == Operation::SETTLE);
    CHECK(trace.current.completed); CHECK(trace.current.returned); CHECK(trace.current.timing_valid);
    frozenReceipt(r, 10000U);
    CHECK(r.owner.runtime().transaction().report().halt.inhibition_confirmed); allLow(r);
}

TEST_CASE("B14 D192 early polls skipped releases and one step per poll stay on Runtime grid") {
    Rig r; REQUIRE(r.owner.begin({true})); const auto anchor = r.native.now;
    r.next(); REQUIRE(r.owner.runtime().report().epochs == 1U);
    const auto count = r.native.calls;
    r.native.now = anchor + 999U; r.owner.poll();
    CHECK(r.owner.report().polls == 2U); CHECK_FALSE(r.owner.report().last_step_returned);
    CHECK(r.native.calls == count); CHECK(r.owner.runtime().report().epochs == 1U);
    r.native.now = anchor + 4500U; r.owner.poll();
    CHECK(r.owner.report().polls == 3U); CHECK(r.owner.runtime().report().epochs == 2U);
    CHECK(r.owner.runtime().report().missed_releases == 3U);
    CHECK(r.owner.runtime().report().next_release_us == anchor + 5000U);
    CHECK(r.owner.runtime().transaction().report().started_us == anchor + 4500U);
    CHECK(r.owner.trace().calls[count].application == 2U);
    finish(r); terminal(r, Reason::EPOCH_LIMIT);
    CHECK(r.owner.report().polls == 10001U); allLow(r);
}

TEST_CASE("B14 D192 natural wrap and callback work never invent catch-up epochs") {
    for (auto origin : {0U, 0xFFFFFF00U}) {
        Rig r; r.native.now = origin; REQUIRE(r.owner.begin({true}));
        r.native.callback_work = 200U; r.next();
        const auto& t = r.owner.runtime().transaction().report();
        CHECK(t.execution_us == 1200U); CHECK(t.completed_us == origin + 1200U);
        CHECK(r.owner.runtime().report().epochs == 1U);
        CHECK(r.owner.runtime().report().missed_releases == 1U);
        CHECK(r.owner.runtime().report().next_release_us == origin + 2000U);
        CHECK(r.owner.active()); r.native.callback_work = 0U;
        finish(r); terminal(r, Reason::EPOCH_LIMIT); allLow(r);
    }
}

TEST_CASE("B0 D192 each setup failure keeps setup reason and exact first failure") {
    for (std::uint32_t failed = 1U; failed <= 11U; ++failed) {
        CAPTURE(failed); Rig r; r.native.failure[failed] = true;
        CHECK_FALSE(r.owner.begin({true})); terminal(r, Reason::SETUP_FAILED);
        CHECK(r.owner.report().begin_called); CHECK(r.owner.report().begin_finished);
        CHECK_FALSE(r.owner.report().begin_ok); CHECK(r.owner.report().polls == 0U);
        REQUIRE(r.owner.trace().has_failure); const auto& first = r.owner.trace().first_failure;
        CHECK(first.stage == Stage::SETUP); CHECK(first.application == 0U);
        CHECK_FALSE(first.returned); CHECK(first.completed);
        sameCall(first, r.owner.trace().calls[failed - 1U]);
        sameHalt(r.owner.report().before_abort.transaction.halt,
            r.owner.runtime().transaction().report().halt);
        CHECK(r.native.finalizing_observations == 0U); allLow(r);
    }
}

TEST_CASE("B0 D192 each native application operation fails before and beyond trace prefix") {
    for (auto epoch : {1U, 8U, 9U, 10U, 12U, 10000U}) {
        for (std::uint32_t offset = 0U; offset < 6U; ++offset) {
            CAPTURE(epoch); CAPTURE(offset); Rig r; REQUIRE(r.owner.begin({true}));
            for (std::uint32_t i = 1U; i < epoch; ++i) r.next();
            r.native.fail_at = 11U + (epoch - 1U) * 6U + offset + 1U; r.next();
            terminal(r, Reason::CALLBACK_FAILURE); REQUIRE(r.owner.trace().has_failure);
            const auto& f = r.owner.trace().first_failure;
            CHECK(f.stage == Stage::APPLY); CHECK(f.application == epoch);
            CHECK(f.operation == applicationOperation(offset));
            if (offset > 0U && offset < 5U)
                CHECK(f.channel == static_cast<motors::Channel>(offset - 1U));
            CHECK_FALSE(f.returned); CHECK(f.completed); CHECK(f.timing_valid);
            CHECK(r.owner.report().polls == epoch);
            CHECK_FALSE(r.owner.report().before_abort.transaction.applied.feedback.applied_valid);
            if (r.native.fail_at <= 64U) sameCall(f, r.owner.trace().calls[r.native.fail_at - 1U]);
            if (r.native.fail_at > 64U) {
                CHECK(r.owner.trace().overflow); CHECK(r.owner.trace().count == 64U);
                CHECK(r.owner.trace().rejected == r.native.calls - 64U);
                for (const auto& c : r.owner.trace().calls) CHECK(c.returned);
            }
            allLow(r);
        }
    }
}

TEST_CASE("B0 D192 final cleanup failure leaves epoch reason but never implies successful halt") {
    for (std::uint32_t offset = 0U; offset < 6U; ++offset) {
        Rig r; REQUIRE(r.owner.begin({true}));
        r.native.fail_at = 60012U + offset; finish(r);
        terminal(r, Reason::EPOCH_LIMIT); frozenReceipt(r, 10000U);
        REQUIRE(r.owner.trace().has_failure); CHECK(r.owner.trace().first_failure.stage == Stage::HALT);
        CHECK(r.owner.trace().first_failure.application == 10000U);
        CHECK(r.owner.trace().first_failure.operation == applicationOperation(offset));
        CHECK_FALSE(r.owner.runtime().transaction().report().halt.inhibition_confirmed);
        CHECK(r.native.calls == 60017U); CHECK(r.owner.trace().rejected == 59953U); allLow(r);
    }
}

TEST_CASE("B0 B14 D192 late failure outranks timing bounds and repeated cleanup failures") {
    Rig r; REQUIRE(r.owner.begin({true}));
    for (unsigned i = 0U; i < 9999U; ++i) r.next();
    r.native.fail_from = r.native.calls + 1U; r.native.reverse_call = r.native.fail_from;
    r.next(); terminal(r, Reason::CALLBACK_FAILURE);
    CHECK(r.owner.trace().has_failure); CHECK(r.owner.trace().timing_fault);
    CHECK(r.owner.trace().first_failure.stage == Stage::APPLY);
    CHECK(r.owner.trace().first_failure.application == 10000U);
    CHECK(r.owner.trace().first_failure.operation == Operation::ENABLE); allLow(r);
}

TEST_CASE("B14 D192 trace time reversal after prefix outranks runtime and bounds") {
    for (auto epoch : {1U, 12U, 10000U}) {
        Rig r; REQUIRE(r.owner.begin({true}));
        for (std::uint32_t i = 1U; i < epoch; ++i) r.next();
        r.native.reverse_call = r.native.calls + 1U; r.next();
        terminal(r, Reason::TRACE_INVALID); CHECK(r.owner.trace().timing_fault);
        CHECK_FALSE(r.owner.trace().has_failure); allLow(r);
    }
}

TEST_CASE("B14 D192 outer backward and half-range clocks retain Runtime terminal evidence") {
    for (auto elapsed : {0xFFFFFFFFU, 0x80000000U}) {
        Rig r; REQUIRE(r.owner.begin({true})); r.native.now += elapsed; r.owner.poll();
        terminal(r, Reason::RUNTIME_TERMINAL); CHECK_FALSE(r.owner.report().last_step_returned);
        CHECK(r.owner.report().polls == 1U);
        CHECK(r.owner.report().before_abort.runtime.fault == app::RuntimeFault::CLOCK);
        CHECK(r.owner.report().before_abort.runtime.epochs == 0U);
        CHECK_FALSE(r.owner.report().before_abort.transaction.decision_made);
        sameHalt(r.owner.report().before_abort.transaction.halt,
            r.owner.runtime().transaction().report().halt);
        CHECK(r.native.finalizing_observations == 0U); allLow(r);
    }
}

TEST_CASE("B14 D192 equal clock stops on real Runtime stall before observer poll cap") {
    Rig r; REQUIRE(r.owner.begin({true})); r.next();
    for (std::uint32_t i = 0U; i <= config::APP_CLOCK_STALL_MAX_POLLS && r.owner.active(); ++i)
        r.owner.poll();
    terminal(r, Reason::APPLICATION_INVALID);
    CHECK(r.owner.report().before_abort.transaction.decision_made);
    CHECK_FALSE(r.owner.report().before_abort.transaction.applied.feedback.applied_valid);
    CHECK(r.owner.report().before_abort.runtime.fault == app::RuntimeFault::CLOCK);
    CHECK(r.owner.report().before_abort.runtime.epochs == 1U);
    CHECK(r.owner.report().before_abort.transaction.robot.token == 1U);
    CHECK(r.owner.report().polls < config::APP_MOTOR_OBSERVE_MAX_POLLS); allLow(r);
}

TEST_CASE("B14 D192 individual clock glitches keep ordered evidence through real pipeline") {
    Rig baseline; REQUIRE(baseline.owner.begin({true}));
    const auto setup_reads = baseline.native.clocks; baseline.next();
    const auto epoch_reads = baseline.native.clocks - setup_reads; REQUIRE(epoch_reads > 0U);
    for (std::uint32_t read = 1U; read <= epoch_reads; ++read) {
        CAPTURE(read); Rig r; REQUIRE(r.owner.begin({true}));
        r.native.reverse_clock = r.native.clocks + read; r.next();
        if (r.owner.active()) { r.native.reverse_clock = 0U; finish(r); }
        REQUIRE(r.owner.report().phase == Phase::FROZEN);
        CHECK(r.owner.report().reason == orderedReason(r.owner)); allLow(r);
    }
}

TEST_CASE("B0 D192 missing callbacks clock and invalid periods fail setup and remain passive") {
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
        app_motor_observe::Runner owner{p, {}, {}}; n.owner = &owner;
        CHECK_FALSE(owner.begin({true})); CHECK(owner.report().phase == Phase::FROZEN);
        CHECK(owner.report().reason == Reason::SETUP_FAILED); CHECK(owner.report().before_abort_valid);
        CHECK(owner.report().polls == 0U);
        const auto calls = n.calls, clocks = n.clocks; owner.poll(); CHECK_FALSE(owner.begin({true}));
        CHECK(n.calls == calls); CHECK(n.clocks == clocks); CHECK_FALSE(n.unsafe);
    }
}

TEST_CASE("B0 D192 absent peripheral ports stay absent across every long observation epoch") {
    Native n; app_motor_observe::Runner owner{n.port(), {}, {}}; n.owner = &owner;
    REQUIRE(owner.begin({true}));
    for (unsigned i = 0U; i < 10000U; ++i) {
        n.now = owner.runtime().report().next_release_us; owner.poll();
    }
    CHECK(owner.report().phase == Phase::FROZEN); CHECK(owner.report().reason == Reason::EPOCH_LIMIT);
    CHECK(n.calls == 60017U); CHECK(n.peripheral_calls == 0U); CHECK_FALSE(n.unsafe);
}
#else
TEST_CASE("B14 D192 copied bounds stop finite advancing early polls without a fake epoch") {
    REQUIRE(config::APP_MOTOR_OBSERVE_EPOCHS == 12U);
    REQUIRE(config::APP_MOTOR_OBSERVE_MAX_POLLS == 12U);
    Rig r; REQUIRE(r.owner.begin({true})); r.next();
    for (std::uint32_t i = 2U; i <= 12U; ++i) {
        ++r.native.now; r.owner.poll(); CHECK(r.owner.report().polls == i);
        CHECK_FALSE(r.owner.report().last_step_returned);
        CHECK(r.owner.runtime().report().epochs == 1U);
        if (i < 12U) CHECK(r.owner.active());
    }
    terminal(r, Reason::POLL_LIMIT); frozenReceipt(r, 1U);
    CHECK(r.native.calls == 23U); CHECK(r.native.finalizing_observations == 6U); allLow(r);
}

TEST_CASE("B14 D192 exact epoch and poll tie selects epoch without an extra poll") {
    Rig r; REQUIRE(r.owner.begin({true})); finish(r);
    terminal(r, Reason::EPOCH_LIMIT); frozenReceipt(r, 12U);
    CHECK(r.owner.report().polls == 12U); CHECK(r.native.calls == 89U);
    CHECK(r.owner.trace().count == 64U); CHECK(r.owner.trace().rejected == 25U);
    CHECK(r.owner.trace().overflow); CHECK_FALSE(r.owner.trace().has_failure); allLow(r);
}

TEST_CASE("B0 B14 D192 late callback and timing faults each outrank exact bound tie") {
    for (bool failed : {false, true}) {
        Rig r; REQUIRE(r.owner.begin({true}));
        for (unsigned i = 0U; i < 11U; ++i) r.next();
        r.native.reverse_call = r.native.calls + 1U;
        if (failed) r.native.fail_from = r.native.reverse_call;
        r.next(); terminal(r, failed ? Reason::CALLBACK_FAILURE : Reason::TRACE_INVALID);
        CHECK(r.owner.report().polls == 12U); CHECK(r.owner.trace().timing_fault);
        CHECK(r.owner.trace().has_failure == failed); allLow(r);
    }
}
#endif
