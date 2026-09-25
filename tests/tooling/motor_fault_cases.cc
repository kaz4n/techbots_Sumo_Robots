// Tests D162 inert callback diagnostics from their public contract.
// Preserves independent expectations around the real MotorGate write boundary.
// Run through test_motor_fault.py, including the sanitizer build.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "motor_fault.h"
#include <cstdlib>
#include <new>

namespace {
bool watch_allocations = false;
std::uint32_t allocation_count = 0U;
}
void* operator new(std::size_t size) {
    if (watch_allocations) ++allocation_count;
    void* pointer = std::malloc(size == 0U ? 1U : size);
    if (pointer == nullptr) std::abort();
    return pointer;
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* pointer) noexcept { std::free(pointer); }
void operator delete[](void* pointer) noexcept { std::free(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { std::free(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { std::free(pointer); }

namespace {
using motor_fault::Call;
using motor_fault::Failure;
using motor_fault::Operation;
using motor_fault::Phase;
using motor_fault::Stage;
using motors::Channel;

struct NativeCall {
    Operation operation = Operation::CONFIG_ENABLE;
    Channel channel = Channel::LEFT_FORWARD;
    bool high = false;
    std::uint32_t period = 0U, pulse = 0U;
};
struct Fake {
    NativeCall calls[256];
    std::uint32_t count = 0U, clock_reads = 0U, now = 100U, last_clock = 0U;
    std::uint32_t clock_step = 1U, fail_at = 0U, fail_from = 0U;
    bool inside_observed = false, inside_correct = true;
    bool false_pending = false, false_seen_before_trailing_clock = false;
    motor_fault::Trace* inspect = nullptr;

    bool record(Operation op, Channel channel = Channel::LEFT_FORWARD,
                bool high = false, std::uint32_t period = 0U,
                std::uint32_t pulse = 0U) {
        if (count >= 256U) std::abort();
        calls[count++] = {op, channel, high, period, pulse};
        if (inspect != nullptr) {
            const auto& current = inspect->report().current;
            inside_observed = true;
            inside_correct = inside_correct && inspect->report().has_current && !current.completed &&
                current.operation == op && current.channel == channel &&
                current.requested_high == high && current.period_cycles == period &&
                current.pulse_cycles == pulse;
        }
        const bool okay = count != fail_at && (fail_from == 0U || count < fail_from);
        false_pending = !okay;
        return okay;
    }
    static bool configureEnable(void* p) {
        return static_cast<Fake*>(p)->record(Operation::CONFIG_ENABLE);
    }
    static bool configurePwm(void* p, Channel channel) {
        return static_cast<Fake*>(p)->record(Operation::CONFIG_PWM, channel);
    }
    static bool enable(void* p, bool high) {
        return static_cast<Fake*>(p)->record(Operation::ENABLE, Channel::LEFT_FORWARD, high);
    }
    static bool pwm(void* p, Channel channel, std::uint32_t period, std::uint32_t pulse) {
        return static_cast<Fake*>(p)->record(Operation::PWM, channel, false, period, pulse);
    }
    static bool settle(void* p) {
        return static_cast<Fake*>(p)->record(Operation::SETTLE);
    }
    static std::uint32_t clock(void* p) {
        auto& f = *static_cast<Fake*>(p);
        if (f.false_pending && f.inspect != nullptr) {
            const auto& r = f.inspect->report();
            f.false_seen_before_trailing_clock = r.has_failure && !r.first_failure.returned;
            f.false_pending = false;
        }
        ++f.clock_reads;
        f.last_clock = f.now;
        f.now += f.clock_step;
        return f.last_clock;
    }
    motors::Port port() {
        motors::Port p;
        p.context = this;
        p.configureEnableLow = configureEnable;
        p.configurePwm = configurePwm;
        p.writeEnable = enable;
        p.writePwm = pwm;
        p.settle = settle;
        p.clockUs = clock;
        for (std::uint32_t i = 0U; i < 4U; ++i) p.period_cycles[i] = 101U + i;
        return p;
    }
};

void checkCall(const Call& actual, const NativeCall& expected) {
    CHECK(actual.operation == expected.operation);
    CHECK(actual.channel == expected.channel);
    CHECK(actual.requested_high == expected.high);
    CHECK(actual.period_cycles == expected.period);
    CHECK(actual.pulse_cycles == expected.pulse);
    CHECK(actual.invoked);
    CHECK(actual.completed);
}
bool invoke(const motors::Port& port, std::uint32_t operation) {
    switch (operation) {
    case 0U: return port.configureEnableLow(port.context);
    case 1U: return port.configurePwm(port.context, Channel::RIGHT_REVERSE);
    case 2U: return port.writeEnable(port.context, false);
    case 3U: return port.writePwm(port.context, Channel::RIGHT_FORWARD, 937U, 0U);
    default: return port.settle(port.context);
    }
}
void checkInert(const Fake& fake) {
    for (std::uint32_t i = 0U; i < fake.count; ++i) {
        CHECK_FALSE(fake.calls[i].high);
        CHECK(fake.calls[i].pulse == 0U);
    }
}
void complete(motor_fault::Runner& runner, Fake& fake) {
    for (std::uint32_t i = 0U; i < motor_fault::APPLY_SAMPLES && runner.active(); ++i) {
        fake.now = runner.report().next_release_us;
        runner.poll(fake.now);
    }
}
void checkTerminalPassive(motor_fault::Runner& runner, Fake& fake) {
    const auto phase = runner.report().phase;
    const auto reason = runner.report().failure;
    const auto applications = runner.report().applications;
    const auto count = fake.count;
    const auto clock_reads = fake.clock_reads;
    CHECK_FALSE(runner.active());
    CHECK_FALSE(runner.begin({true}));
    runner.poll(0U);
    runner.poll(0xffffffffU);
    CHECK(runner.report().phase == phase);
    CHECK(runner.report().failure == reason);
    CHECK(runner.report().applications == applications);
    CHECK(fake.count == count);
    CHECK(fake.clock_reads == clock_reads);
}
} // namespace

TEST_CASE("D162 B4 construction and denied begin are wholly passive") {
    Fake fake;
    motor_fault::Trace trace(fake.port());
    const auto port = trace.port();
    CHECK(port.context != nullptr);
    CHECK(trace.report().count == 0U);
    CHECK_FALSE(trace.report().has_current);
    motor_fault::Runner runner(fake.port());
    CHECK(runner.report().phase == Phase::NOT_STARTED);
    CHECK_FALSE(runner.active());
    runner.poll(1234U);
    CHECK(runner.begin({}));
    CHECK(runner.report().phase == Phase::DISABLED);
    CHECK_FALSE(runner.report().begin_called);
    CHECK_FALSE(runner.report().halt_called);
    CHECK(fake.count == 0U);
    CHECK(fake.clock_reads == 0U);
    checkTerminalPassive(runner, fake);
}

TEST_CASE("D162 B4 Trace preserves missing callbacks and native periods") {
    Fake fake;
    auto native = fake.port();
    native.configureEnableLow = nullptr;
    native.configurePwm = nullptr;
    native.writeEnable = nullptr;
    native.writePwm = nullptr;
    native.settle = nullptr;
    native.clockUs = nullptr;
    native.period_cycles[3] = 0U;
    motor_fault::Trace trace(native);
    const auto wrapped = trace.port();
    CHECK(wrapped.configureEnableLow == nullptr);
    CHECK(wrapped.configurePwm == nullptr);
    CHECK(wrapped.writeEnable == nullptr);
    CHECK(wrapped.writePwm == nullptr);
    CHECK(wrapped.settle == nullptr);
    CHECK(wrapped.clockUs == nullptr);
    for (unsigned i = 0U; i < 4U; ++i) CHECK(wrapped.period_cycles[i] == native.period_cycles[i]);
    CHECK(fake.count == 0U);
    CHECK(fake.clock_reads == 0U);
}

TEST_CASE("D162 B4 every callback forwards native context arguments and true outcome once") {
    Fake fake;
    motor_fault::Trace trace(fake.port());
    fake.inspect = &trace;
    trace.context(Stage::APPLY, 3U);
    const auto port = trace.port();
    for (std::uint32_t op = 0U; op < 5U; ++op) CHECK(invoke(port, op));
    REQUIRE(fake.count == 5U);
    REQUIRE(trace.report().count == 5U);
    for (std::uint32_t i = 0U; i < 5U; ++i) {
        const auto& call = trace.report().calls[i];
        checkCall(call, fake.calls[i]);
        CHECK(call.stage == Stage::APPLY);
        CHECK(call.application == 3U);
        CHECK(call.returned);
        CHECK(call.timing_valid);
        CHECK(call.completed_us - call.started_us == 1U);
    }
    CHECK(fake.inside_observed);
    CHECK(fake.inside_correct);
    CHECK(trace.report().has_current);
    CHECK_FALSE(trace.report().has_failure);
    CHECK(trace.report().clock_reads == fake.clock_reads);
    const auto before = fake.clock_reads;
    const auto actual = fake.now;
    CHECK(port.clockUs(port.context) == actual);
    CHECK(fake.clock_reads == before + 1U);
    CHECK(trace.report().clock_reads == fake.clock_reads);
}

TEST_CASE("D162 B4 every false native result precedes diagnostic trailing clock") {
    for (std::uint32_t operation = 0U; operation < 5U; ++operation) {
        Fake fake;
        fake.fail_at = 1U;
        motor_fault::Trace trace(fake.port());
        fake.inspect = &trace;
        const auto port = trace.port();
        CHECK_FALSE(invoke(port, operation));
        REQUIRE(trace.report().has_failure);
        const auto failed = trace.report().first_failure;
        checkCall(failed, fake.calls[0]);
        CHECK_FALSE(failed.returned);
        CHECK(failed.timing_valid);
        CHECK(failed.completed_us - failed.started_us == 1U);
        CHECK(fake.false_seen_before_trailing_clock);
        fake.fail_from = 2U;
        trace.context(Stage::HALT);
        CHECK_FALSE(port.settle(port.context));
        CHECK(trace.report().first_failure.operation == failed.operation);
        CHECK(trace.report().first_failure.started_us == failed.started_us);
        CHECK(trace.report().first_failure.stage == Stage::SETUP);
        CHECK(fake.count == 2U);
    }
}

TEST_CASE("D162 B4 local guard rejects HIGH and nonzero pulses without backend I O") {
    Fake fake;
    motor_fault::Trace trace(fake.port());
    const auto port = trace.port();
    CHECK_FALSE(port.writeEnable(port.context, true));
    for (std::uint32_t channel = 0U; channel < 4U; ++channel) {
        CHECK_FALSE(port.writePwm(port.context, static_cast<Channel>(channel), 234U, 1U));
    }
    CHECK(fake.count == 0U);
    REQUIRE(trace.report().count == 5U);
    for (std::uint32_t i = 0U; i < 5U; ++i) {
        CHECK_FALSE(trace.report().calls[i].invoked);
        CHECK_FALSE(trace.report().calls[i].returned);
        CHECK(trace.report().calls[i].completed);
    }
    CHECK(trace.report().first_failure.operation == Operation::ENABLE);
    CHECK(trace.report().first_failure.requested_high);
    CHECK(port.writeEnable(port.context, false));
    CHECK(port.writePwm(port.context, Channel::LEFT_FORWARD, 0U, 0U));
    CHECK(fake.calls[1].period == 0U);
}

TEST_CASE("D162 B4 trace timing permits same time and wrap but latches ambiguous or absent clock") {
    for (const std::uint32_t step : {0U, 7U, 0x80000000U, 0xffffffffU}) {
        Fake fake;
        fake.now = 0xfffffffcU;
        fake.clock_step = step;
        motor_fault::Trace trace(fake.port());
        const auto port = trace.port();
        CHECK(port.settle(port.context));
        REQUIRE(trace.report().count == 1U);
        CHECK(trace.report().calls[0].timing_valid == (step < 0x80000000U));
        CHECK(trace.report().timing_fault == (step >= 0x80000000U));
        CHECK(trace.report().calls[0].completed_us - trace.report().calls[0].started_us == step);
        fake.clock_step = 0U;
        CHECK(port.settle(port.context));
        CHECK(trace.report().timing_fault == (step >= 0x80000000U));
    }
    Fake fake;
    auto native = fake.port();
    native.clockUs = nullptr;
    motor_fault::Trace trace(native);
    const auto port = trace.port();
    CHECK(port.settle(port.context));
    CHECK(trace.report().timing_fault);
    CHECK_FALSE(trace.report().calls[0].timing_valid);
    CHECK(fake.clock_reads == 0U);
}

TEST_CASE("D162 B4 trace overflow retains first64 current and a later first false") {
    Fake fake;
    fake.fail_at = 67U;
    motor_fault::Trace trace(fake.port());
    const auto port = trace.port();
    for (std::uint32_t i = 1U; i <= 70U; ++i) {
        trace.context(Stage::APPLY, i);
        CHECK(port.settle(port.context) == (i != 67U));
    }
    REQUIRE(trace.report().count == 64U);
    CHECK(trace.report().overflow);
    CHECK(trace.report().rejected == 6U);
    for (std::uint32_t i = 0U; i < 64U; ++i) CHECK(trace.report().calls[i].application == i + 1U);
    CHECK(trace.report().current.application == 70U);
    CHECK(trace.report().current.completed);
    CHECK(trace.report().first_failure.application == 67U);
    CHECK_FALSE(trace.report().first_failure.returned);
    CHECK(fake.count == 70U);
    CHECK(trace.report().clock_reads == fake.clock_reads);
}

TEST_CASE("D162 B4 real Gate accepts exactly four zero samples then acknowledged halt") {
    Fake fake;
    motor_fault::Runner runner(fake.port());
    REQUIRE(runner.begin({true}));
    CHECK(runner.report().begin_called);
    CHECK(runner.report().begin_ok);
    CHECK(runner.report().begin_fault == motors::Fault::NONE);
    CHECK(runner.report().next_release_us == fake.last_clock);
    CHECK(runner.report().applications == 0U);
    CHECK(runner.active());
    complete(runner, fake);
    REQUIRE(runner.report().applications == 4U);
    CHECK(runner.report().phase == Phase::COMPLETE);
    CHECK(runner.report().failure == Failure::NONE);
    for (std::uint32_t i = 0U; i < 4U; ++i) {
        const auto& result = runner.report().applied[i];
        CHECK(result.consumed);
        CHECK(result.fault == motors::Fault::NONE);
        CHECK(result.feedback.applied_valid);
        CHECK(result.feedback.token == i + 1U);
        CHECK_FALSE(result.feedback.motors_enabled);
        CHECK(result.feedback.duty_l == 0.0F);
        CHECK(result.feedback.duty_r == 0.0F);
        CHECK_FALSE(result.feedback.duration_valid);
        CHECK(result.feedback.execution_us == 0U);
        const auto& last_write = runner.trace().calls[16U + 6U * i];
        CHECK(result.feedback.applied_us == last_write.completed_us + 1U);
    }
    CHECK(runner.report().halt_called);
    CHECK(runner.report().halt.fresh);
    CHECK(runner.report().halt.attempted);
    CHECK(runner.report().halt.inhibition_confirmed);
    CHECK(runner.report().halt.timing_valid);
    CHECK(runner.report().halt.fault == motors::Fault::STOPPED);
    REQUIRE(runner.trace().count == 41U);
    for (std::uint32_t i = 0U; i < 41U; ++i) {
        const auto& call = runner.trace().calls[i];
        CHECK(call.stage == (i < 11U ? Stage::SETUP : i < 35U ? Stage::APPLY : Stage::HALT));
        CHECK(call.application == (i >= 11U && i < 35U ? (i - 11U) / 6U + 1U : 0U));
    }
    checkInert(fake);
    checkTerminalPassive(runner, fake);
}

TEST_CASE("D162 B4 missing native callback or invalid period fails real Gate setup") {
    for (std::uint32_t field = 0U; field < 8U; ++field) {
        Fake fake;
        auto port = fake.port();
        switch (field) {
        case 0U: port.configureEnableLow = nullptr; break;
        case 1U: port.configurePwm = nullptr; break;
        case 2U: port.writeEnable = nullptr; break;
        case 3U: port.writePwm = nullptr; break;
        case 4U: port.settle = nullptr; break;
        case 5U: port.clockUs = nullptr; break;
        case 6U: port.period_cycles[1] = 0U; break;
        default: port.period_cycles[3] = 16777217U; break;
        }
        motor_fault::Runner runner(port);
        CHECK_FALSE(runner.begin({true}));
        CHECK(runner.report().phase == Phase::FAULT);
        CHECK(runner.report().failure == Failure::SETUP);
        CHECK(runner.report().begin_fault == motors::Fault::PORT);
        CHECK(runner.report().applications == 0U);
        CHECK(runner.report().halt_called);
        checkInert(fake);
        checkTerminalPassive(runner, fake);
    }
}

TEST_CASE("D162 B4 forward clock movement resets consecutive equal poll count") {
    Fake fake;
    motor_fault::Runner runner(fake.port());
    REQUIRE(runner.begin({true}));
    const auto first = runner.report().next_release_us;
    for (std::uint32_t i = 1U; i < config::APP_CLOCK_STALL_MAX_POLLS; ++i) runner.poll(first);
    runner.poll(first + 1U);
    CHECK(runner.active());
    for (std::uint32_t i = 1U; i < config::APP_CLOCK_STALL_MAX_POLLS; ++i) runner.poll(first + 1U);
    CHECK(runner.active());
    CHECK(runner.report().applications == 1U);
    runner.poll(first + 1U);
    CHECK(runner.report().failure == Failure::CLOCK);
}

TEST_CASE("D162 B4 scheduling applies once at deadline and skips whole releases") {
    Fake fake;
    motor_fault::Runner runner(fake.port());
    REQUIRE(runner.begin({true}));
    const auto first = runner.report().next_release_us;
    fake.now = first;
    runner.poll(first);
    REQUIRE(runner.report().applications == 1U);
    const auto next = runner.report().next_release_us;
    CHECK(next == first + config::TICK_US);
    const auto calls = fake.count;
    const auto reads = fake.clock_reads;
    runner.poll(next - 1U);
    CHECK(runner.report().applications == 1U);
    CHECK(fake.count == calls);
    CHECK(fake.clock_reads == reads);
    fake.now = next + 3U * config::TICK_US + 1U;
    runner.poll(fake.now);
    CHECK(runner.report().applications == 2U);
    CHECK(runner.report().missed_releases == 3U);
    CHECK(runner.report().next_release_us == next + 4U * config::TICK_US);
    complete(runner, fake);
    CHECK(runner.report().phase == Phase::COMPLETE);
}

TEST_CASE("D162 B4 scheduling crosses uint32 wrap and rejects backward half range") {
    Fake fake;
    fake.now = 0xffffff80U;
    motor_fault::Runner runner(fake.port());
    REQUIRE(runner.begin({true}));
    complete(runner, fake);
    CHECK(runner.report().phase == Phase::COMPLETE);
    CHECK(runner.report().missed_releases == 0U);
    for (const std::uint32_t delta : {0xffffffffU, 0x80000000U}) {
        Fake reversed;
        motor_fault::Runner rejected(reversed.port());
        REQUIRE(rejected.begin({true}));
        rejected.poll(rejected.report().next_release_us + delta);
        CHECK(rejected.report().failure == Failure::CLOCK);
        CHECK(rejected.report().phase == Phase::FAULT);
        CHECK(rejected.report().applications == 0U);
        CHECK(rejected.report().halt_called);
        checkTerminalPassive(rejected, reversed);
    }
}

TEST_CASE("D162 B4 equal-time polling faults exactly at existing stall bound") {
    Fake fake;
    motor_fault::Runner runner(fake.port());
    REQUIRE(runner.begin({true}));
    const auto now = runner.report().next_release_us;
    for (std::uint32_t i = 1U; i < config::APP_CLOCK_STALL_MAX_POLLS; ++i) runner.poll(now);
    CHECK(runner.active());
    CHECK(runner.report().applications == 1U);
    runner.poll(now);
    CHECK(runner.report().phase == Phase::FAULT);
    CHECK(runner.report().failure == Failure::CLOCK);
    CHECK(runner.report().applications == 1U);
    checkTerminalPassive(runner, fake);
}

TEST_CASE("D162 B4 every real Gate setup callback failure remains first after failed cleanup") {
    for (std::uint32_t fail = 1U; fail <= 11U; ++fail) {
        Fake fake;
        fake.fail_from = fail;
        motor_fault::Runner runner(fake.port());
        CHECK_FALSE(runner.begin({true}));
        CHECK(runner.report().phase == Phase::FAULT);
        CHECK(runner.report().failure == Failure::SETUP);
        CHECK_FALSE(runner.report().begin_ok);
        CHECK(runner.report().begin_fault == motors::Fault::IO);
        CHECK(runner.report().halt_called);
        CHECK_FALSE(runner.report().halt.inhibition_confirmed);
        REQUIRE(runner.trace().has_failure);
        CHECK(runner.trace().first_failure.stage == Stage::SETUP);
        checkCall(runner.trace().first_failure, fake.calls[fail - 1U]);
        CHECK(runner.report().applications == 0U);
        checkInert(fake);
        checkTerminalPassive(runner, fake);
    }
}

TEST_CASE("D162 B4 every disabled application callback failure preserves invalid receipt") {
    for (std::uint32_t fail = 1U; fail <= 6U; ++fail) {
        Fake fake;
        motor_fault::Runner runner(fake.port());
        REQUIRE(runner.begin({true}));
        fake.fail_from = fake.count + fail;
        runner.poll(runner.report().next_release_us);
        CHECK(runner.report().phase == Phase::FAULT);
        CHECK(runner.report().failure == Failure::APPLICATION);
        REQUIRE(runner.report().applications == 1U);
        CHECK(runner.report().applied[0].consumed);
        CHECK(runner.report().applied[0].feedback.token == 1U);
        CHECK_FALSE(runner.report().applied[0].feedback.applied_valid);
        CHECK(runner.report().applied[0].fault == motors::Fault::IO);
        CHECK(runner.trace().first_failure.stage == Stage::APPLY);
        CHECK(runner.trace().first_failure.application == 1U);
        CHECK(runner.report().halt_called);
        CHECK_FALSE(runner.report().halt.inhibition_confirmed);
        checkInert(fake);
        checkTerminalPassive(runner, fake);
    }
}

TEST_CASE("D162 B4 every cleanup callback failure prevents complete") {
    for (std::uint32_t fail = 1U; fail <= 6U; ++fail) {
        Fake fake;
        fake.fail_at = 35U + fail;
        motor_fault::Runner runner(fake.port());
        REQUIRE(runner.begin({true}));
        complete(runner, fake);
        CHECK(runner.report().applications == 4U);
        CHECK(runner.report().phase == Phase::FAULT);
        CHECK(runner.report().failure == Failure::HALT);
        CHECK(runner.report().halt_called);
        CHECK_FALSE(runner.report().halt.inhibition_confirmed);
        CHECK(runner.report().halt.fault == motors::Fault::IO);
        REQUIRE(runner.trace().has_failure);
        CHECK(runner.trace().first_failure.stage == Stage::HALT);
        CHECK(runner.trace().first_failure.application == 0U);
        checkInert(fake);
        checkTerminalPassive(runner, fake);
    }
}

TEST_CASE("D162 B4 invalid trace clock during setup or apply forces trace fault") {
    Fake setup;
    setup.clock_step = 0x80000000U;
    motor_fault::Runner first(setup.port());
    CHECK_FALSE(first.begin({true}));
    CHECK(first.report().begin_ok);
    CHECK(first.report().failure == Failure::TRACE);
    CHECK(first.report().halt_called);
    CHECK(first.trace().timing_fault);
    Fake apply;
    motor_fault::Runner second(apply.port());
    REQUIRE(second.begin({true}));
    apply.clock_step = 0x80000000U;
    second.poll(second.report().next_release_us);
    CHECK(second.report().applications == 1U);
    CHECK(second.report().failure == Failure::TRACE);
    CHECK(second.report().halt_called);
    checkTerminalPassive(second, apply);
}

TEST_CASE("D162 B4 construction trace and whole real Gate run allocate no heap") {
    allocation_count = 0U;
    watch_allocations = true;
    Fake fake;
    motor_fault::Runner runner(fake.port());
    const bool began = runner.begin({true});
    complete(runner, fake);
    const auto phase = runner.report().phase;
    runner.poll(0U);
    const bool restarted = runner.begin({true});
    watch_allocations = false;
    CHECK(began);
    CHECK(phase == Phase::COMPLETE);
    CHECK_FALSE(restarted);
    CHECK(allocation_count == 0U);
}
