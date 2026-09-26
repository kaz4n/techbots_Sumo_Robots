// Exercises D197 public native settle exits using the unchanged hardware fixture.
// Records exact native and clock transcripts while independently checking reports.
// Fresh processes keep first-failure tests independent without a probe reset API.
#include "native_fixture.h"
#include "hal/motor_port_unoq.h"
#include "hal/motor_settle_probe.h"
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <type_traits>

namespace {
unsigned long clocks[5000]{};
unsigned clock_count = 0U;
void need(bool condition, int line) {
    if (!condition) { std::fprintf(stderr, "D197 assertion line %d\n", line); std::exit(1); }
}
#define NEED(condition) need(static_cast<bool>(condition), __LINE__)

#if SUMOX_MOTOR_FAULT_PROBE == 1
using motors::SettleProbeReason;
using motors::SettleProbeReport;
using motors::SettleProbeSample;
static_assert(std::is_standard_layout<SettleProbeSample>::value);
static_assert(std::is_standard_layout<SettleProbeReport>::value);
static_assert(sizeof(SettleProbeSample) == 12U && alignof(SettleProbeSample) == 4U);
static_assert(sizeof(SettleProbeReport) == 28U && alignof(SettleProbeReport) == 4U);
static_assert(offsetof(SettleProbeSample, elapsed_us) == 0U);
static_assert(offsetof(SettleProbeSample, poll_index) == 4U);
static_assert(offsetof(SettleProbeSample, reason) == 8U);
static_assert(offsetof(SettleProbeSample, fresh_mask) == 9U);
static_assert(offsetof(SettleProbeSample, valid) == 10U);
static_assert(offsetof(SettleProbeSample, reserved) == 11U);
static_assert(offsetof(SettleProbeReport, current) == 0U);
static_assert(offsetof(SettleProbeReport, first_failure) == 12U);
static_assert(offsetof(SettleProbeReport, has_current) == 24U);
static_assert(offsetof(SettleProbeReport, has_failure) == 25U);
static_assert(offsetof(SettleProbeReport, reserved) == 26U);
static_assert(std::is_same<decltype(motors::settleProbeReport()), const SettleProbeReport&>::value);
static_assert(static_cast<unsigned>(SettleProbeReason::NONE) == 0U);
static_assert(static_cast<unsigned>(SettleProbeReason::SUCCESS) == 1U);
static_assert(static_cast<unsigned>(SettleProbeReason::NULL_CONTEXT) == 2U);
static_assert(static_cast<unsigned>(SettleProbeReason::PRECONDITION) == 3U);
static_assert(static_cast<unsigned>(SettleProbeReason::INITIAL_BANK) == 4U);
static_assert(static_cast<unsigned>(SettleProbeReason::POLL_DEADLINE) == 5U);
static_assert(static_cast<unsigned>(SettleProbeReason::POLL_BANK) == 6U);
static_assert(static_cast<unsigned>(SettleProbeReason::FINAL_DEADLINE) == 7U);
static_assert(static_cast<unsigned>(SettleProbeReason::POLL_LIMIT) == 8U);
static_assert(motors::SETTLE_ELAPSED_VALID == 1U);
static_assert(motors::SETTLE_POLL_VALID == 2U);
static_assert(motors::SETTLE_FRESH_VALID == 4U);
SettleProbeReport expected{};
const SettleProbeReport* identity = nullptr;

void inspect() {
    const auto native_calls = fixture::hw.trace_size;
    const auto clock_calls = clock_count;
    {
        fixture::NoAllocation guard;
        const auto& observed = motors::settleProbeReport();
        if (identity == nullptr) identity = &observed;
        NEED(&observed == identity);
        NEED(std::memcmp(&observed, &expected, sizeof(expected)) == 0);
        NEED(&motors::settleProbeReport() == identity);
    }
    NEED(fixture::hw.trace_size == native_calls && clock_count == clock_calls);
    NEED(fixture::hw.allocations == 0U && fixture::hw.deallocations == 0U);
}

void observe(unsigned reason, std::uint32_t elapsed, std::uint32_t poll, unsigned fresh) {
    SettleProbeSample next{};
    next.reason = static_cast<SettleProbeReason>(reason);
    next.elapsed_us = elapsed;
    next.poll_index = poll;
    next.fresh_mask = static_cast<std::uint8_t>(fresh);
    next.valid = reason >= 5U || reason == 1U ? 7U : 0U;
    expected.current = next;
    expected.has_current = 1U;
    if (reason != 1U && expected.has_failure == 0U) {
        expected.first_failure = next;
        expected.has_failure = 1U;
    }
    inspect();
}
#else
void inspect() {}
void observe(unsigned, std::uint32_t, std::uint32_t, unsigned) {}
#endif

void begin_segment() { fixture::clearTrace(); clock_count = 0U; }

void bytes(const char* name, const void* pointer, std::size_t count) {
    const auto* raw = static_cast<const unsigned char*>(pointer);
    std::printf("%s ", name);
    for (std::size_t i = 0U; i < count; ++i) std::printf("%02x", raw[i]);
    std::printf("\n");
}

void emit(const char* tag, bool returned) {
    const auto& h = fixture::hw;
    unsigned total = 0U;
    for (auto count : h.calls) total += count;
    NEED(total == h.trace_size); // Refuse a truncated fixture transcript.
    NEED(clock_count == h.calls[fixture::CLOCK]);
    NEED(h.allocations == 0U && h.deallocations == 0U);
    NEED(!h.unsafe_high && !h.writes_while_high);
    std::printf("SEGMENT %s %u native_size=%zu\n", tag, returned ? 1U : 0U, sizeof(motors::UnoQPort));
    for (unsigned i = 0U; i < h.trace_size; ++i) {
        const auto& c = h.trace[i];
        std::printf("N %u %u %u %u\n", unsigned(c.kind), c.index, c.a, c.b);
    }
    for (unsigned i = 0U; i < clock_count; ++i) std::printf("C %lu\n", clocks[i]);
    bytes("gpio", GPIOB, sizeof(GPIO_TypeDef));
    for (unsigned i = 0U; i < 3U; ++i) bytes("timer", fixture::timer(i), sizeof(TIM_TypeDef));
    bytes("ready", h.ready, sizeof(h.ready));
    bytes("rates", h.rate, sizeof(h.rate));
    bytes("active", h.active, sizeof(h.active));
    bytes("active_arr", h.active_arr, sizeof(h.active_arr));
    bytes("polls", h.polls, sizeof(h.polls));
    bytes("clears", h.clears, sizeof(h.clears));
    bytes("timer_init", h.timer_init, sizeof(h.timer_init));
    std::printf("STATE %u %u %u %u %u\n", h.now, h.all_write_mask, h.update_mask,
                h.allocations, h.deallocations);
}

struct Native {
    motors::UnoQPort native;
    motors::Port port = native.port();
    void configure() {
        NEED(port.configureEnableLow(port.context));
        NEED(port.writeEnable(port.context, false));
        for (unsigned i = 0U; i < 4U; ++i)
            NEED(port.configurePwm(port.context, static_cast<motors::Channel>(i)));
    }
    void write(unsigned i) {
        NEED(port.writePwm(port.context, static_cast<motors::Channel>(i), port.period_cycles[i], 0U));
    }
    void write_all() { for (unsigned i = 0U; i < 4U; ++i) write(i); }
    void ready() { configure(); write_all(); }
};

void settle(Native& n, const char* tag, unsigned reason, std::uint32_t elapsed = 0U,
            std::uint32_t poll = 0U, unsigned fresh = 0U, bool null_context = false) {
    begin_segment();
    bool returned = false;
    { fixture::NoAllocation guard; returned = n.port.settle(null_context ? nullptr : n.port.context); }
    NEED(returned == (reason == 1U));
    observe(reason, elapsed, poll, fresh);
    emit(tag, returned);
}

void preconditions(const char* scenario) {
    Native n;
    if (std::strcmp(scenario, "null") == 0) {
        settle(n, scenario, 2U, 0U, 0U, 0U, true);
        NEED(fixture::hw.trace_size == 0U);
    } else if (std::strcmp(scenario, "unconfigured") == 0) {
        settle(n, scenario, 3U);
        NEED(fixture::hw.trace_size == 0U);
    } else if (std::strncmp(scenario, "missing", 7U) == 0) {
        n.configure();
        const unsigned missing = static_cast<unsigned>(scenario[7] - '0');
        NEED(missing < 4U);
        for (unsigned i = 0U; i < 4U; ++i) if (i != missing) n.write(i);
        settle(n, scenario, 3U);
        NEED(fixture::hw.trace_size == 0U);
    } else {
        n.ready();
        fixture::hw.read_override = 1;
        settle(n, scenario, 3U);
        NEED(fixture::hw.calls[fixture::READ_GPIO] == 1U);
        NEED(fixture::hw.calls[fixture::CLOCK] == 0U);
    }
}

void initial_bank(bool rate) {
    Native n; n.ready();
    if (rate) fixture::hw.rate[0] = 1U;
    else TIM3->PSC ^= 1U;
    settle(n, rate ? "initial_rate" : "initial_register", 4U);
    NEED(fixture::hw.calls[fixture::CLOCK] == 1U);
    NEED(fixture::hw.calls[fixture::CLEAR] == 0U);
}

void loop_bank(bool ready) {
    Native n; n.ready();
    if (ready) {
        fixture::hw.lose_ready_at_poll = 1U;
        fixture::hw.lose_ready_index = 0U;
    } else {
        fixture::hw.corrupt_reg = &TIM3->DIER;
        fixture::hw.corrupt_value = 1U;
        fixture::hw.corrupt_at_poll = 1U;
    }
    settle(n, ready ? "loop_ready" : "loop_register", 6U, 0U, 0U, 7U);
    NEED(fixture::hw.now == 3U);
    NEED(fixture::hw.calls[fixture::CLOCK] == 2U);
    NEED(fixture::hw.calls[fixture::POLL] == 3U);
}

void final_boundary(unsigned elapsed, bool wrap) {
    Native n; n.ready();
    fixture::hw.now = wrap ? 0xfffffff0U : 100U;
    fixture::hw.use_event_elapsed = true;
    fixture::hw.event_elapsed = fixture::hw.now + elapsed;
    settle(n, wrap ? "wrap_boundary" : "final_boundary", elapsed < 150U ? 1U : 7U,
           elapsed, 0U, 7U);
    NEED(fixture::hw.calls[fixture::CLOCK] == 3U);
    NEED(fixture::hw.calls[fixture::POLL] == 3U);
}

void loop_deadline() {
    Native n; n.ready();
    fixture::hw.ticks_per_poll = 50U;
    fixture::hw.fresh_after[1] = fixture::hw.fresh_after[2] = -1;
    settle(n, "loop_deadline", 5U, 150U, 1U, 1U);
    NEED(fixture::hw.calls[fixture::CLOCK] == 3U);
    NEED(fixture::hw.calls[fixture::POLL] == 3U);
}

void poll_limit(bool partial) {
    Native n; n.ready();
    fixture::hw.now = 42U;
    fixture::hw.ticks_per_poll = 0U;
    for (auto& value : fixture::hw.fresh_after) value = -1;
    if (partial) fixture::hw.fresh_after[0] = 1;
    settle(n, partial ? "limit_partial" : "limit_zero", 8U, 0U, 4095U, partial ? 1U : 0U);
    NEED(fixture::hw.calls[fixture::CLOCK] == 4097U);
    NEED(fixture::hw.calls[fixture::POLL] == 3U * 4096U);
    for (auto count : fixture::hw.polls) NEED(count == 4096U);
}

void first_failure_lifetime() {
    Native n; n.ready();
    settle(n, "initial_success", 1U, 3U, 0U, 7U);
    NEED(n.port.writeEnable(n.port.context, false));
    settle(n, "first_precondition", 3U);
    n.write_all();
    TIM3->PSC ^= 1U;
    settle(n, "later_bank", 4U);
    TIM3->PSC ^= 1U;
    settle(n, "later_success", 1U, 3U, 0U, 7U);
    begin_segment();
    const auto again = n.native.port();
    NEED(again.context == n.port.context);
    inspect();
    emit("factory_and_accessor_are_passive", true);
    NEED(fixture::hw.trace_size == 0U);
}

void actual_gate_cleanup() {
    motors::UnoQPort n;
    motors::MotorGate gate(n.port());
    begin_segment();
    bool began = false;
    { fixture::NoAllocation guard; began = gate.begin(); }
    NEED(began); observe(1U, 3U, 0U, 7U); emit("gate_begin", began);
    fixture::hw.now = 100U;
    fixture::hw.use_event_elapsed = true;
    fixture::hw.event_elapsed = 250U;
    fsm::RobotResult command{};
    command.fresh = true; command.token = 1U; command.outputs.ui_state = core::State::IDLE;
    begin_segment();
    motors::Result result{};
    { fixture::NoAllocation guard; result = gate.apply(100U, command); }
    NEED(result.consumed && !result.feedback.applied_valid && result.fault == motors::Fault::IO);
    // The first settle fails at150; MotorGate's immediate inhibit then succeeds at0.
#if SUMOX_MOTOR_FAULT_PROBE == 1
    expected.first_failure = {150U, 0U, SettleProbeReason::FINAL_DEADLINE, 7U, 7U, 0U};
    expected.has_failure = 1U;
#endif
    observe(1U, 0U, 0U, 7U); emit("gate_failed_apply_with_successful_cleanup", false);
    fixture::hw.use_event_elapsed = false;
    fixture::hw.corrupt_reg = &TIM3->DIER;
    fixture::hw.corrupt_value = 1U;
    fixture::hw.corrupt_at_poll = 1U;
    begin_segment();
    motors::HaltResult halt{};
    { fixture::NoAllocation guard; halt = gate.halt(); }
    NEED(halt.fresh && halt.attempted && !halt.inhibition_confirmed && halt.timing_valid);
    NEED(halt.fault == motors::Fault::IO);
    observe(6U, 0U, 0U, 7U); emit("gate_halt_preserves_first", false);
    begin_segment();
    const auto repeated = gate.halt();
    NEED(!repeated.fresh && !repeated.inhibition_confirmed);
    inspect(); emit("repeated_halt_is_passive", false);
    NEED(fixture::hw.trace_size == 0U);
}
} // namespace

// The wrapper forwards exactly one original fixture clock read and records its value.
extern "C" unsigned long __real__Z6microsv();
extern "C" unsigned long __wrap__Z6microsv() {
    const auto result = __real__Z6microsv();
    NEED(clock_count < sizeof(clocks) / sizeof(clocks[0]));
    clocks[clock_count++] = result;
    return result;
}

int main(int argc, char** argv) {
    NEED(argc == 2);
    fixture::reset(); inspect();
    const char* name = argv[1];
    if (std::strcmp(name, "null") == 0 || std::strcmp(name, "unconfigured") == 0 ||
        std::strncmp(name, "missing", 7U) == 0 || std::strcmp(name, "enable_readback") == 0)
        preconditions(name);
    else if (std::strcmp(name, "initial_rate") == 0) initial_bank(true);
    else if (std::strcmp(name, "initial_register") == 0) initial_bank(false);
    else if (std::strcmp(name, "loop_ready") == 0) loop_bank(true);
    else if (std::strcmp(name, "loop_register") == 0) loop_bank(false);
    else if (std::strcmp(name, "final149") == 0) final_boundary(149U, false);
    else if (std::strcmp(name, "final150") == 0) final_boundary(150U, false);
    else if (std::strcmp(name, "final151") == 0) final_boundary(151U, false);
    else if (std::strcmp(name, "wrap149") == 0) final_boundary(149U, true);
    else if (std::strcmp(name, "wrap150") == 0) final_boundary(150U, true);
    else if (std::strcmp(name, "loop_deadline") == 0) loop_deadline();
    else if (std::strcmp(name, "limit_zero") == 0) poll_limit(false);
    else if (std::strcmp(name, "limit_partial") == 0) poll_limit(true);
    else if (std::strcmp(name, "first_failure") == 0) first_failure_lifetime();
    else if (std::strcmp(name, "gate_cleanup") == 0) actual_gate_cleanup();
    else NEED(false);
    inspect();
    return 0;
}
