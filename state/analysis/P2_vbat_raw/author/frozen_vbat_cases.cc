// Tests D110 finite voltage capture from adopted public contracts and clocks.
// Keeps native values, skipped releases and immutable publication independently observable.
// Isolated normal, sanitizer and counted-owner profiles execute the actual bench sources.
#ifndef D110_TEST_SEPARATE_MAIN
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#endif
#include "doctest.h"
#include "vbat.h"
#include "config.h"
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <type_traits>
#ifdef TEST_NATIVE_BINDING
#include "vbat_native.h"
void setup();
void loop();
#endif

namespace allocations { bool active = false; unsigned calls = 0U; }
extern "C" {
void* __real_malloc(std::size_t);
void* __real_calloc(std::size_t, std::size_t);
void* __real_realloc(void*, std::size_t);
void __real_free(void*);
void* __wrap_malloc(std::size_t n) {
    if (allocations::active) ++allocations::calls;
    return __real_malloc(n);
}
void* __wrap_calloc(std::size_t n, std::size_t size) {
    if (allocations::active) ++allocations::calls;
    return __real_calloc(n, size);
}
void* __wrap_realloc(void* p, std::size_t n) {
    if (allocations::active) ++allocations::calls;
    return __real_realloc(p, n);
}
void __wrap_free(void* p) {
    if (allocations::active) ++allocations::calls;
    __real_free(p);
}
}
void* operator new(std::size_t size) {
    if (allocations::active) ++allocations::calls;
    if (void* value = __real_malloc(size)) return value;
    std::abort();
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* value) noexcept {
    if (allocations::active) ++allocations::calls;
    __real_free(value);
}
void operator delete[](void* value) noexcept { ::operator delete(value); }
void operator delete(void* value, std::size_t) noexcept { ::operator delete(value); }
void operator delete[](void* value, std::size_t) noexcept { ::operator delete(value); }

namespace {
using power::Status;
using power::Shutdown;
using power::Sample;
using vbat::Runner;
using vbat::Phase;
using vbat::Fault;
constexpr std::uint32_t HALF = 0x80000000U;
enum Event { CLOCK, BEGIN, READ };
std::uint32_t bits(float value) {
    std::uint32_t out = 0U; static_assert(sizeof(out) == sizeof(value));
    std::memcpy(&out, &value, sizeof(out)); return out;
}
float voltage(std::uint16_t raw) {
    return static_cast<float>(raw) / 16383.0F * config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
}
[[maybe_unused]] std::uint32_t expectedMisses(std::uint32_t age) {
    if constexpr (config::VBAT_SAMPLE_PERIOD_US != 0U)
        return age / config::VBAT_SAMPLE_PERIOD_US - 1U;
    else return 0U; // Invalid-config builds execute only admission/passivity cases.
}
Sample good(std::uint32_t start, std::uint32_t end, std::uint16_t raw = 9000U) {
    Sample value; value.status = Status::OK; value.valid = true;
    value.started_us = start; value.completed_us = end; value.raw = raw;
    value.voltage_v = voltage(raw); return value;
}
bool same(const Sample& a, const Sample& b) {
    return a.status == b.status && a.shutdown == b.shutdown && a.valid == b.valid &&
        a.raw == b.raw && a.started_us == b.started_us && a.completed_us == b.completed_us &&
        bits(a.voltage_v) == bits(b.voltage_v);
}
bool same(const power::InitResult& a, const power::InitResult& b) {
    return a.status == b.status && a.shutdown == b.shutdown && a.ready == b.ready;
}
bool same(const vbat::Timing& a, const vbat::Timing& b) {
    return a.calls == b.calls && a.measured_calls == b.measured_calls &&
        a.last_us == b.last_us && a.maximum_us == b.maximum_us && a.last_valid == b.last_valid;
}
bool same(const vbat::Capture& a, const vbat::Capture& b) {
    return same(a.sample, b.sample) && a.call_started_us == b.call_started_us &&
        a.call_returned_us == b.call_returned_us && a.poll_closed_us == b.poll_closed_us &&
        a.source_us == b.source_us && a.read_us == b.read_us && a.poll_us == b.poll_us &&
        a.missed_before == b.missed_before;
}
bool same(const vbat::Report& a, const vbat::Report& b) {
    return a.phase == b.phase && a.fault == b.fault && a.fresh == b.fresh &&
        a.clock_fault == b.clock_fault && a.counter_saturated == b.counter_saturated &&
        a.sample_seen == b.sample_seen && a.last_read_accepted == b.last_read_accepted &&
        same(a.setup, b.setup) && same(a.sample, b.sample) && a.captured_samples == b.captured_samples &&
        a.not_due == b.not_due && a.missed_releases == b.missed_releases &&
        same(a.setup_timing, b.setup_timing) && same(a.read_timing, b.read_timing) &&
        same(a.poll_timing, b.poll_timing);
}
struct Fake {
    std::uint32_t now = 10000U, setup_cost = 7U, read_cost = 20U;
    std::uint32_t source_offset = 2U, source_span = 10U;
    unsigned clocks = 0U, begins = 0U, reads = 0U, used = 0U;
    unsigned jump_at = 0U;
    std::uint32_t jump_delta = HALF;
    bool automatic = true;
    const Runner* observe_runner = nullptr;
    unsigned observe_at = 0U;
    bool observed_seen = false, observed_accepted = true, observed_last_valid = true;
    Sample observed_sample;
    std::uint16_t raw = 9000U;
    power::InitResult setup_result{Status::OK, Shutdown::NOT_ATTEMPTED, true};
    Sample value;
    std::array<Event, 1024> trace{};
    void record(Event event) { if (used < trace.size()) trace[used++] = event; }
    vbat::Port port() { return {this, clock, begin, read}; }
    static std::uint32_t clock(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.clocks;
        if (f.clocks == f.jump_at) f.now += f.jump_delta;
        if (f.observe_runner && f.clocks == f.observe_at) {
            const auto& r = f.observe_runner->report();
            f.observed_seen = r.sample_seen; f.observed_accepted = r.last_read_accepted;
            f.observed_last_valid = r.read_timing.last_valid; f.observed_sample = r.sample;
        }
        f.record(CLOCK); return f.now;
    }
    static power::InitResult begin(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.begins; f.record(BEGIN);
        f.now += f.setup_cost; return f.setup_result;
    }
    static Sample read(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.reads; f.record(READ);
        if (f.automatic) f.value = good(f.now + f.source_offset, f.now + f.source_offset + f.source_span, f.raw);
        f.now += f.read_cost; return f.value;
    }
};
void traceIs(const Fake& f, std::initializer_list<Event> events) {
    REQUIRE(f.used == events.size()); unsigned i = 0U;
    for (const auto event : events) { CHECK(f.trace[i] == event); ++i; }
}
void running(Fake& f, Runner& r) {
    REQUIRE(r.begin({true})); REQUIRE(r.report().phase == Phase::RUNNING);
    CHECK(f.begins == 1U); CHECK(f.clocks == 3U); CHECK(f.reads == 0U);
}
void terminal(Fake& f, Runner& r) {
    auto expected = r.report(); expected.fresh = false; const auto used = f.used;
    CHECK_FALSE(r.poll()); CHECK_FALSE(r.begin({false})); CHECK_FALSE(r.begin({true}));
    CHECK(same(r.report(), expected)); CHECK(f.used == used);
}
void faultIs(Fake& f, Runner& r, Fault fault) {
    CHECK(r.report().phase == Phase::FAULT); CHECK(r.report().fault == fault); terminal(f, r);
}
Fake* stateless = nullptr;
} // namespace

TEST_CASE("D110 passive construction defaults bounds and repeated begin") {
    static_assert(!std::is_copy_constructible<Runner>::value);
    static_assert(!std::is_copy_assignable<Runner>::value);
    static_assert(std::is_same<decltype(std::declval<const Runner&>().capture(0U)), const vbat::Capture*>::value);
    Fake f; Runner r(f.port()); const auto initial = r.report();
    CHECK_FALSE(r.poll()); CHECK(same(initial, r.report())); CHECK(f.used == 0U);
    CHECK(r.captureCapacity() == config::VBAT_BENCH_SAMPLES);
    CHECK(r.captureCount() == 0U); CHECK(r.capture(0U) == nullptr); CHECK(r.capture(0xffffffffU) == nullptr);
    CHECK(r.begin({})); CHECK(r.report().phase == Phase::DISABLED); terminal(f, r); CHECK(f.used == 0U);
    Runner no_port({}); CHECK(no_port.begin({})); CHECK(no_port.report().phase == Phase::DISABLED);
    CHECK_FALSE(no_port.poll()); CHECK_FALSE(no_port.begin({true}));
}

TEST_CASE("D110 missing ports precede all config and perform no clock") {
    for (unsigned missing = 0U; missing < 3U; ++missing) {
        CAPTURE(missing); Fake f; auto port = f.port();
        if (missing == 0U) port.clockUs = nullptr;
        if (missing == 1U) port.beginBattery = nullptr;
        if (missing == 2U) port.readBattery = nullptr;
        Runner r(port); CHECK_FALSE(r.begin({true})); faultIs(f, r, Fault::PORT); CHECK(f.used == 0U);
    }
}

TEST_CASE("D110 invalid config is refused before callbacks while disabled remains passive") {
#ifdef TEST_INVALID_CONFIG
    Fake f; Runner r(f.port()); CHECK_FALSE(r.begin({true})); faultIs(f, r, Fault::CONFIG);
    CHECK(f.used == 0U); CHECK(r.captureCapacity() == config::VBAT_BENCH_SAMPLES);
    Runner disabled(f.port()); CHECK(disabled.begin({})); CHECK_FALSE(disabled.poll());
    CHECK(disabled.report().phase == Phase::DISABLED); CHECK(f.used == 0U);
#endif
}

TEST_CASE("D110 valid config smoke first sample and exact nominal scale") {
    Fake f; f.source_offset = 0U; f.source_span = 0U; f.read_cost = 0U;
    Runner r(f.port()); running(f, r); REQUIRE(r.poll());
    REQUIRE(r.capture(0U)); CHECK(same(r.capture(0U)->sample, f.value));
    CHECK(r.capture(0U)->sample.voltage_v == voltage(9000U)); CHECK(r.capture(0U)->source_us == 0U);
}

TEST_CASE("D110 null context stateless callbacks and copied port are valid") {
    Fake f; stateless = &f;
    vbat::Port port{nullptr, [](void*) { return Fake::clock(stateless); },
        [](void*) { return Fake::begin(stateless); }, [](void*) { return Fake::read(stateless); }};
    Runner r(port); port = {}; running(f, r); REQUIRE(r.poll());
    CHECK(r.captureCount() == 1U); CHECK(f.reads == 1U); stateless = nullptr;
}

TEST_CASE("D110 exact setup read closure timing and first poll is immediately due") {
    Fake f; Runner r(f.port()); running(f, r); traceIs(f, {CLOCK, BEGIN, CLOCK, CLOCK});
    CHECK(r.report().setup_timing.calls == 1U); CHECK(r.report().setup_timing.measured_calls == 1U);
    CHECK(r.report().setup_timing.last_us == 7U); CHECK(r.report().setup_timing.last_valid);
    CHECK_FALSE(r.report().sample_seen); CHECK_FALSE(r.report().last_read_accepted);
    const auto saved = r.report(); CHECK_FALSE(r.begin({true})); CHECK(same(saved, r.report()));
    const auto s = f.now; f.used = 0U; f.jump_at = f.clocks + 3U; f.jump_delta = 13U;
    REQUIRE(r.poll()); traceIs(f, {CLOCK, READ, CLOCK, CLOCK});
    REQUIRE(r.capture(0U)); const auto& c = *r.capture(0U);
    CHECK(c.call_started_us == s); CHECK(c.call_returned_us == s + 20U); CHECK(c.poll_closed_us == s + 33U);
    CHECK(c.source_us == 10U); CHECK(c.read_us == 20U); CHECK(c.poll_us == 33U); CHECK(c.missed_before == 0U);
    CHECK(r.report().read_timing.last_us == 20U); CHECK(r.report().poll_timing.last_us == 33U);
    CHECK(r.report().sample_seen); CHECK(r.report().last_read_accepted); CHECK(r.report().fresh);
}

TEST_CASE("D110 actual returned sample is visible before closing A callback") {
    Fake f; Runner r(f.port()); running(f, r); f.observe_runner = &r; f.observe_at = f.clocks + 2U;
    REQUIRE(r.poll()); CHECK(f.observed_seen); CHECK_FALSE(f.observed_accepted);
    CHECK_FALSE(f.observed_last_valid); CHECK(same(f.observed_sample, f.value));
}

TEST_CASE("D110 all configured records remain immutable through terminal fresh clearing") {
    Fake f; Runner r(f.port()); running(f, r);
    std::array<vbat::Capture, config::VBAT_BENCH_SAMPLES> expected{};
    std::array<const vbat::Capture*, config::VBAT_BENCH_SAMPLES> pointers{};
    for (std::uint32_t i = 0U; i < config::VBAT_BENCH_SAMPLES; ++i) {
        if (i != 0U) f.now = expected[i - 1U].sample.started_us + config::VBAT_SAMPLE_PERIOD_US;
        f.raw = (i % 3U == 0U) ? 0U : (i % 3U == 1U ? 16383U : 9000U);
        const auto s = f.now; allocations::calls = 0U; allocations::active = true;
        const bool accepted = r.poll(); allocations::active = false;
        REQUIRE(accepted); CHECK(allocations::calls == 0U); CHECK(r.report().fresh);
        expected[i] = {f.value, s, s + 20U, s + 20U, 10U, 20U, 20U, 0U};
        pointers[i] = r.capture(i); REQUIRE(pointers[i]); CHECK(same(*pointers[i], expected[i]));
        CHECK(r.captureCount() == i + 1U); CHECK(r.report().captured_samples == i + 1U);
        CHECK(r.capture(i + 1U) == nullptr); CHECK(r.capture(0xffffffffU) == nullptr);
        const auto used = f.used;
        for (std::uint32_t j = 0U; j <= i; ++j) {
            CHECK(r.capture(j) == pointers[j]); CHECK(same(*r.capture(j), expected[j]));
        }
        CHECK(f.used == used);
    }
    CHECK(r.report().phase == Phase::COMPLETE); CHECK(f.reads == config::VBAT_BENCH_SAMPLES);
    CHECK(r.report().sample.shutdown == Shutdown::NOT_ATTEMPTED);
    CHECK(r.report().read_timing.calls == config::VBAT_BENCH_SAMPLES);
    CHECK(r.report().poll_timing.measured_calls == config::VBAT_BENCH_SAMPLES);
    terminal(f, r);
    for (std::uint32_t i = 0U; i < config::VBAT_BENCH_SAMPLES; ++i)
        CHECK(same(*r.capture(i), expected[i]));
}

TEST_CASE("D110 setup preserves every known nonOK result as SETUP without synthetic shutdown") {
    for (unsigned status = 1U; status <= 14U; ++status)
        for (unsigned shutdown = 0U; shutdown <= 2U; ++shutdown) for (bool ready : {false, true}) {
            CAPTURE(status); CAPTURE(shutdown); CAPTURE(ready); Fake f;
            f.setup_result = {static_cast<Status>(status), static_cast<Shutdown>(shutdown), ready};
            Runner r(f.port()); CHECK_FALSE(r.begin({true}));
            CHECK(same(r.report().setup, f.setup_result)); CHECK(f.reads == 0U);
            CHECK(r.report().setup_timing.last_valid); CHECK(r.report().setup_timing.last_us == 7U);
            faultIs(f, r, Fault::SETUP);
        }
}

TEST_CASE("D110 setup unknown or contradictory success shape is CONTRACT before bad A") {
    for (unsigned mode = 0U; mode < 6U; ++mode) for (bool bad_a : {false, true}) {
        CAPTURE(mode); CAPTURE(bad_a); Fake f;
        if (mode == 0U) f.setup_result.status = static_cast<Status>(255U);
        if (mode == 1U) f.setup_result.shutdown = static_cast<Shutdown>(255U);
        if (mode == 2U) f.setup_result.ready = false;
        if (mode == 3U) f.setup_result.shutdown = Shutdown::DISABLED;
        if (mode == 4U) f.setup_result.shutdown = Shutdown::UNCONFIRMED;
        if (mode == 5U) { f.setup_result.status = Status::NOT_ENABLED;
            f.setup_result.shutdown = static_cast<Shutdown>(255U); }
        if (bad_a) f.jump_at = 2U;
        Runner r(f.port()); CHECK_FALSE(r.begin({true})); CHECK(same(r.report().setup, f.setup_result));
        CHECK(r.report().clock_fault == bad_a); CHECK(f.clocks == (bad_a ? 2U : 3U));
        CHECK(r.report().setup_timing.last_valid == !bad_a); faultIs(f, r, Fault::CONTRACT);
    }
}

TEST_CASE("D110 native read failures retain all fields and cleanup inclusive timing") {
    for (unsigned status = 1U; status <= 14U; ++status) for (unsigned shutdown = 0U; shutdown <= 2U; ++shutdown) {
        CAPTURE(status); CAPTURE(shutdown); Fake f; Runner r(f.port()); running(f, r);
        f.automatic = false; f.read_cost = 180U;
        f.value = good(f.now - 100U, f.now - 200U, 65535U); f.value.valid = false;
        f.value.status = static_cast<Status>(status); f.value.shutdown = static_cast<Shutdown>(shutdown);
        f.value.voltage_v = std::numeric_limits<float>::quiet_NaN(); const auto actual = f.value;
        CHECK_FALSE(r.poll()); CHECK(same(r.report().sample, actual)); CHECK(r.report().sample_seen);
        CHECK_FALSE(r.report().last_read_accepted); CHECK(r.captureCount() == 0U);
        CHECK(r.report().read_timing.last_us == 180U); CHECK(r.report().poll_timing.last_us == 180U);
        CHECK(r.report().read_timing.last_valid); CHECK(r.report().poll_timing.last_valid);
        faultIs(f, r, Fault::ADC);
    }
}

TEST_CASE("D110 sample semantic failures precede bad A and preserve actual fields") {
    for (unsigned mode = 0U; mode < 10U; ++mode) for (bool bad_a : {false, true}) {
        CAPTURE(mode); CAPTURE(bad_a); Fake f; Runner r(f.port()); running(f, r); f.automatic = false;
        f.value = good(f.now + 2U, f.now + 12U);
        if (mode == 0U) f.value.status = static_cast<Status>(255U);
        if (mode == 1U) f.value.shutdown = static_cast<Shutdown>(255U);
        if (mode == 2U) f.value.status = Status::CONVERSION_TIMEOUT;
        if (mode == 3U) f.value.valid = false;
        if (mode == 4U) f.value.shutdown = Shutdown::DISABLED;
        if (mode == 5U) f.value.shutdown = Shutdown::UNCONFIRMED;
        if (mode == 6U) f.value.raw = 16384U;
        if (mode == 7U) f.value.voltage_v = std::numeric_limits<float>::infinity();
        if (mode == 8U) f.value.voltage_v = std::numeric_limits<float>::quiet_NaN();
        if (mode == 9U) f.value.voltage_v = std::nextafter(f.value.voltage_v, 0.0F);
        if (bad_a) f.jump_at = f.clocks + 2U;
        const auto actual = f.value; const auto clocks = f.clocks;
        CHECK_FALSE(r.poll()); CHECK(same(r.report().sample, actual));
        CHECK(r.report().clock_fault == bad_a); CHECK(f.clocks == clocks + (bad_a ? 2U : 3U));
        CHECK(r.report().read_timing.last_valid == !bad_a); CHECK(r.report().poll_timing.last_valid == !bad_a);
        faultIs(f, r, Fault::CONTRACT);
    }
}

TEST_CASE("D110 ADC or SETUP remains first cause when closing clocks fail") {
    for (bool setup : {false, true}) for (unsigned observation : {2U, 3U}) {
        CAPTURE(setup); CAPTURE(observation); Fake f; Runner r(f.port());
        if (setup) {
            f.setup_result = {Status::OWNERSHIP, Shutdown::UNCONFIRMED, false};
            f.jump_at = observation; CHECK_FALSE(r.begin({true}));
        } else {
            running(f, r); f.automatic = false; f.value.status = Status::OVERRUN;
            f.value.shutdown = Shutdown::DISABLED; f.jump_at = f.clocks + observation; CHECK_FALSE(r.poll());
            CHECK(r.report().read_timing.last_valid == (observation == 3U));
        }
        CHECK(r.report().clock_fault); faultIs(f, r, setup ? Fault::SETUP : Fault::ADC);
    }
}

TEST_CASE("D110 source envelope and strict native conversion deadline") {
    for (unsigned mode = 0U; mode < 6U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); running(f, r); f.automatic = false;
        f.value = good(f.now + 2U, f.now + 12U);
        if (mode == 0U) f.value.started_us = f.now - 1U;
        if (mode == 1U) f.value.started_us = f.now + 21U;
        if (mode == 2U) f.value.completed_us = f.now + 21U;
        if (mode == 3U) f.value.completed_us = f.value.started_us - 1U;
        if (mode == 4U) { f.read_cost = 105U; f.value.completed_us = f.value.started_us + 100U; }
        if (mode == 5U) { f.read_cost = 106U; f.value.completed_us = f.value.started_us + 101U; }
        CHECK_FALSE(r.poll()); CHECK(r.captureCount() == 0U); CHECK(r.report().read_timing.last_valid);
        CHECK(r.report().poll_timing.last_valid); faultIs(f, r, Fault::SOURCE_ORDER);
    }
}

TEST_CASE("D110 zero and deadline minus one source spans are accepted") {
    for (auto span : {0U, 99U}) {
        CAPTURE(span); Fake f; f.source_offset = 0U; f.source_span = span; f.read_cost = span;
        Runner r(f.port()); running(f, r); REQUIRE(r.poll()); REQUIRE(r.capture(0U));
        CHECK(r.capture(0U)->source_us == span); CHECK(r.capture(0U)->read_us == span);
        CHECK(r.report().read_timing.last_us == span); CHECK_FALSE(r.report().clock_fault);
    }
}

TEST_CASE("D110 raw endpoints and negative zero are preserved without voltage clamp") {
    for (auto raw : {0U, 16383U}) {
        CAPTURE(raw); Fake f; f.raw = static_cast<std::uint16_t>(raw); Runner r(f.port()); running(f, r);
        REQUIRE(r.poll()); CHECK(r.report().sample.raw == raw);
        CHECK(r.capture(0U)->sample.voltage_v == voltage(static_cast<std::uint16_t>(raw)));
    }
    Fake f; Runner r(f.port()); running(f, r); f.automatic = false;
    f.value = good(f.now, f.now, 0U); f.value.voltage_v = -0.0F;
    REQUIRE(r.poll()); CHECK(std::signbit(r.capture(0U)->sample.voltage_v));
    CHECK(bits(r.report().sample.voltage_v) == bits(-0.0F));
}

TEST_CASE("D110 bad S prevents read and preserves unattempted default sample") {
    for (auto delta : {HALF, 0xffffffffU}) {
        Fake f; Runner r(f.port()); running(f, r); const auto prior = r.report();
        f.used = 0U; f.jump_at = f.clocks + 1U; f.jump_delta = delta; CHECK_FALSE(r.poll());
        traceIs(f, {CLOCK}); CHECK(f.reads == 0U); CHECK_FALSE(r.report().sample_seen);
        CHECK(same(prior.sample, r.report().sample)); CHECK(same(prior.read_timing, r.report().read_timing));
        CHECK(r.report().poll_timing.calls == 1U); faultIs(f, r, Fault::CLOCK);
    }
}

TEST_CASE("D110 bad A or C cannot expose a tentative sample") {
    for (unsigned observation : {2U, 3U}) {
        CAPTURE(observation); Fake f; Runner r(f.port()); running(f, r);
        f.used = 0U; f.jump_at = f.clocks + observation; CHECK_FALSE(r.poll());
        if (observation == 2U) traceIs(f, {CLOCK, READ, CLOCK});
        else traceIs(f, {CLOCK, READ, CLOCK, CLOCK});
        CHECK(r.captureCount() == 0U); CHECK(r.capture(0U) == nullptr); CHECK_FALSE(r.report().fresh);
        CHECK(r.report().sample_seen); CHECK_FALSE(r.report().last_read_accepted);
        CHECK(same(r.report().sample, f.value)); CHECK_FALSE(r.report().poll_timing.last_valid);
        CHECK(r.report().read_timing.last_valid == (observation == 3U)); faultIs(f, r, Fault::CLOCK);
    }
}

TEST_CASE("D110 setup aggregate half range rejects closing C") {
    Fake f; f.setup_cost = HALF - 10U; f.jump_at = 3U; f.jump_delta = 10U;
    Runner r(f.port()); CHECK_FALSE(r.begin({true})); CHECK(f.clocks == 3U);
    CHECK(r.report().clock_fault); CHECK_FALSE(r.report().setup_timing.last_valid);
    CHECK(r.report().setup_timing.calls == 1U); CHECK(r.report().setup_timing.measured_calls == 0U);
    faultIs(f, r, Fault::CLOCK);
}

TEST_CASE("D110 first due poll aggregate half range does not fabricate closure") {
    Fake f; Runner r(f.port()); running(f, r); f.read_cost = HALF - 10U;
    f.jump_at = f.clocks + 3U; f.jump_delta = 10U; CHECK_FALSE(r.poll());
    CHECK(r.report().read_timing.last_valid); CHECK(r.report().read_timing.last_us == HALF - 10U);
    CHECK_FALSE(r.report().poll_timing.last_valid); CHECK(r.captureCount() == 0U);
    faultIs(f, r, Fault::CLOCK);
}

TEST_CASE("D110 natural uint32 wrap keeps source and wrapper durations exact") {
    Fake f; f.now = 0xfffffff0U; Runner r(f.port()); running(f, r); const auto s = f.now;
    REQUIRE(r.poll()); REQUIRE(r.capture(0U)); const auto& c = *r.capture(0U);
    CHECK(c.call_started_us == s); CHECK(c.call_returned_us == s + 20U);
    CHECK(c.source_us == 10U); CHECK(c.read_us == 20U); CHECK(c.poll_us == 20U);
    CHECK_FALSE(r.report().clock_fault); CHECK(same(c.sample, f.value));
}

TEST_CASE("D110 creation setup read and destruction have no heap operations") {
    Fake f; bool began = false, read = false; allocations::calls = 0U; allocations::active = true;
    { Runner r(f.port()); began = r.begin({true}); read = r.poll(); }
    allocations::active = false; CHECK(began); CHECK(read); CHECK(allocations::calls == 0U);
    CHECK(f.begins == 1U); CHECK(f.reads == 1U); CHECK(f.clocks == 6U);
}

#ifndef TEST_CAPACITY_ONE
TEST_CASE("D110 early equal and late polls count only exact unserved source periods") {
    const auto p = config::VBAT_SAMPLE_PERIOD_US;
    for (auto age : {p - 1U, p, 2U * p - 1U, 2U * p, 3U * p + 1U}) {
        CAPTURE(age); Fake f; Runner r(f.port()); running(f, r); REQUIRE(r.poll());
        const auto prior = r.report(); const auto first = *r.capture(0U);
        f.now = first.sample.started_us + age; f.used = 0U;
        const bool appended = r.poll(); CHECK(appended == (age >= p));
        if (age < p) {
            traceIs(f, {CLOCK}); CHECK(r.report().not_due == 1U); CHECK_FALSE(r.report().fresh);
            CHECK(same(prior.sample, r.report().sample)); CHECK(same(prior.read_timing, r.report().read_timing));
            CHECK(r.report().last_read_accepted); CHECK_FALSE(r.report().poll_timing.last_valid);
            CHECK(r.report().poll_timing.last_us == prior.poll_timing.last_us);
        } else {
            traceIs(f, {CLOCK, READ, CLOCK, CLOCK}); REQUIRE(r.capture(1U));
            CHECK(r.capture(1U)->missed_before == expectedMisses(age));
            CHECK(r.report().missed_releases == expectedMisses(age)); CHECK(f.reads == 2U);
        }
        CHECK(same(*r.capture(0U), first));
    }
}

TEST_CASE("D110 repeated identical numerical values remain distinct admitted captures") {
    Fake f; Runner r(f.port()); running(f, r); REQUIRE(r.poll()); const auto first = *r.capture(0U);
    f.now = first.sample.started_us + config::VBAT_SAMPLE_PERIOD_US; REQUIRE(r.poll());
    CHECK(r.capture(1U)->sample.raw == first.sample.raw);
    CHECK(bits(r.capture(1U)->sample.voltage_v) == bits(first.sample.voltage_v));
    CHECK(r.capture(1U)->sample.started_us != first.sample.started_us);
    CHECK(r.captureCount() == 2U); CHECK(r.report().fresh);
}

TEST_CASE("D110 closing time reanchors source age without retroactive missed additions") {
    Fake f; Runner r(f.port()); running(f, r); f.jump_at = f.clocks + 3U;
    f.jump_delta = 3U * config::VBAT_SAMPLE_PERIOD_US; REQUIRE(r.poll());
    const auto first = *r.capture(0U); CHECK(first.missed_before == 0U);
    CHECK(r.report().missed_releases == 0U); CHECK(first.poll_us == 20U + f.jump_delta);
    f.jump_at = 0U; const auto age = f.now - first.sample.started_us; REQUIRE(r.poll());
    REQUIRE(r.capture(1U)); CHECK(r.capture(1U)->missed_before == expectedMisses(age));
    CHECK(r.report().missed_releases == 2U); CHECK(f.reads == 2U);
    CHECK_FALSE(r.poll()); CHECK(f.reads == 2U); CHECK(r.report().not_due == 1U);
}

TEST_CASE("D110 actual late invocation counts skips even when result or closure fails") {
    for (unsigned mode = 0U; mode < 3U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); running(f, r); REQUIRE(r.poll());
        const auto first = *r.capture(0U); f.now = first.sample.started_us + 3U * config::VBAT_SAMPLE_PERIOD_US;
        if (mode == 0U) { f.automatic = false; f.value = {}; f.value.status = Status::OVERRUN; }
        if (mode != 0U) f.jump_at = f.clocks + mode + 1U;
        CHECK_FALSE(r.poll()); CHECK(r.report().missed_releases == 2U); CHECK(f.reads == 2U);
        CHECK(r.captureCount() == 1U); CHECK(same(*r.capture(0U), first)); CHECK(r.capture(1U) == nullptr);
        CHECK_FALSE(r.report().last_read_accepted); faultIs(f, r, mode == 0U ? Fault::ADC : Fault::CLOCK);
    }
}

TEST_CASE("D110 bad later S preserves historical accepted sample timing and prior capture") {
    Fake f; Runner r(f.port()); running(f, r); REQUIRE(r.poll()); const auto prior = r.report();
    const auto first = *r.capture(0U); f.jump_at = f.clocks + 1U; CHECK_FALSE(r.poll());
    CHECK(r.report().sample_seen); CHECK(r.report().last_read_accepted); CHECK_FALSE(r.report().fresh);
    CHECK(same(r.report().sample, prior.sample)); CHECK(same(r.report().read_timing, prior.read_timing));
    CHECK(same(*r.capture(0U), first)); CHECK(r.report().missed_releases == 0U); CHECK(f.reads == 1U);
    faultIs(f, r, Fault::CLOCK);
}

TEST_CASE("D110 previous source era must survive A and C before replacement") {
    for (unsigned endpoint : {1U, 2U, 3U}) {
        CAPTURE(endpoint); Fake f; Runner r(f.port()); running(f, r); REQUIRE(r.poll());
        const auto first = *r.capture(0U); const auto count = f.reads;
        f.now = first.sample.started_us + HALF - (endpoint == 1U ? 0U : 10U);
        if (endpoint == 3U) { f.read_cost = 5U; f.source_offset = 0U; f.source_span = 1U;
            f.jump_at = f.clocks + 3U; f.jump_delta = 5U; }
        CHECK_FALSE(r.poll()); CHECK(f.reads == count + (endpoint == 1U ? 0U : 1U));
        CHECK(r.captureCount() == 1U); CHECK(same(*r.capture(0U), first));
        if (endpoint == 3U) CHECK(r.report().read_timing.last_valid);
        faultIs(f, r, Fault::CLOCK);
    }
}

TEST_CASE("D110 early polling accumulates source age and does not refresh history") {
    Fake f; Runner r(f.port()); running(f, r); REQUIRE(r.poll()); const auto first = *r.capture(0U);
    const auto p = config::VBAT_SAMPLE_PERIOD_US;
    for (unsigned i = 1U; i < 10U; ++i) {
        f.now = first.sample.started_us + p * i / 10U; CHECK_FALSE(r.poll());
        CHECK(f.reads == 1U); CHECK(r.report().last_read_accepted); CHECK(same(r.report().sample, first.sample));
    }
    f.now = first.sample.started_us + p; REQUIRE(r.poll());
    CHECK(r.report().not_due == 9U); CHECK(r.report().poll_timing.calls == 11U);
    CHECK(r.report().poll_timing.measured_calls == 2U); CHECK(r.report().missed_releases == 0U);
}

TEST_CASE("D110 five public samples reach exact missed counter maximum then saturate") {
#ifdef TEST_SATURATION
    static_assert(config::VBAT_SAMPLE_PERIOD_US == 1U && config::VBAT_ADC_CONVERSION_US == 1U);
    Fake f; f.source_offset = 0U; f.source_span = 0U; f.read_cost = 0U;
    Runner r(f.port()); running(f, r); REQUIRE(r.poll());
    const std::array<std::uint32_t, 4> ages{HALF - 1U, HALF - 1U, 4U, 2U};
    const std::array<std::uint32_t, 4> skips{2147483646U, 2147483646U, 3U, 1U};
    const std::array<std::uint32_t, 4> sums{2147483646U, 4294967292U, 4294967295U, 4294967295U};
    for (unsigned i = 0U; i < ages.size(); ++i) {
        f.now = r.capture(i)->sample.started_us + ages[i]; REQUIRE(r.poll()); REQUIRE(r.capture(i + 1U));
        CHECK(r.capture(i + 1U)->missed_before == skips[i]); CHECK(r.report().missed_releases == sums[i]);
        CHECK(r.report().counter_saturated == (i == 3U)); CHECK_FALSE(r.report().clock_fault);
        CHECK(r.captureCount() == i + 2U); CHECK(f.reads == i + 2U);
    }
#endif
}
TEST_CASE("D110 accumulated source half range cannot alias across early polls") {
#ifdef TEST_LONG_PERIOD
    static_assert(config::VBAT_SAMPLE_PERIOD_US == HALF - 1U);
    Fake f; f.source_offset = 0U; f.source_span = 0U; f.read_cost = 0U;
    Runner r(f.port()); running(f, r); REQUIRE(r.poll()); const auto first = *r.capture(0U);
    f.now = first.sample.started_us + HALF / 2U; CHECK_FALSE(r.poll());
    CHECK(r.report().phase == Phase::RUNNING); CHECK(r.report().not_due == 1U); CHECK(f.reads == 1U);
    f.now = first.sample.started_us + HALF; f.used = 0U; CHECK_FALSE(r.poll());
    traceIs(f, {CLOCK}); CHECK(f.reads == 1U); CHECK(r.report().not_due == 1U);
    CHECK(same(*r.capture(0U), first)); CHECK(r.report().last_read_accepted); faultIs(f, r, Fault::CLOCK);
#endif
}
#endif

#ifdef TEST_NATIVE_BINDING
namespace native_fake {
unsigned clocks = 0U, begins = 0U, reads = 0U, pair_begins = 0U, buttons = 0U;
const power::Reader* first = nullptr; bool same_owner = true;
std::uint32_t now = 30000U;
void owner(const power::Reader* value) { if (!first) first = value; same_owner = same_owner && first == value; }
void reset() { clocks = begins = reads = pair_begins = buttons = 0U; first = nullptr; same_owner = true; }
}
unsigned long micros() { ++native_fake::clocks; return native_fake::now; }
namespace power {
InitResult Reader::begin() {
    native_fake::owner(this); ++native_fake::begins;
    return {Status::OK, Shutdown::NOT_ATTEMPTED, true};
}
Sample Reader::read() {
    native_fake::owner(this); ++native_fake::reads;
    return good(native_fake::now, native_fake::now + 12U, 12345U);
}
InitResult Reader::beginWithButtons() { ++native_fake::pair_begins; return {}; }
ButtonSample Reader::readButtons() { ++native_fake::buttons; return {}; }
}
TEST_CASE("D110 default sketch startup and 10000 loops perform zero callbacks") {
    CHECK(native_fake::clocks == 0U); CHECK(native_fake::begins == 0U); CHECK(native_fake::reads == 0U);
    CHECK(native_fake::pair_begins == 0U); CHECK(native_fake::buttons == 0U);
    setup(); for (unsigned i = 0U; i < 10000U; ++i) loop();
    CHECK(native_fake::clocks == 0U); CHECK(native_fake::begins == 0U); CHECK(native_fake::reads == 0U);
    CHECK(native_fake::pair_begins == 0U); CHECK(native_fake::buttons == 0U);
}
TEST_CASE("D110 Native actual binding owns one stable battery only Reader") {
    static_assert(!std::is_copy_constructible<vbat::Native>::value);
    static_assert(!std::is_copy_assignable<vbat::Native>::value);
    native_fake::reset();
    {
        vbat::Native native; const auto port = native.port(); const auto second = native.port();
        CHECK(port.context == second.context); CHECK(native_fake::clocks == 0U); CHECK(native_fake::begins == 0U);
        REQUIRE(port.clockUs); REQUIRE(port.beginBattery); REQUIRE(port.readBattery);
        CHECK(port.clockUs(port.context) == native_fake::now); CHECK(native_fake::clocks == 1U);
        CHECK(port.beginBattery(port.context).ready); CHECK(native_fake::begins == 1U);
        const auto one = port.readBattery(port.context); const auto two = port.readBattery(port.context);
        CHECK(same(one, good(native_fake::now, native_fake::now + 12U, 12345U)));
        CHECK(same(one, two)); CHECK(native_fake::reads == 2U); CHECK(native_fake::same_owner);
    }
    CHECK(native_fake::begins == 1U); CHECK(native_fake::reads == 2U); CHECK(native_fake::clocks == 1U);
    CHECK(native_fake::pair_begins == 0U); CHECK(native_fake::buttons == 0U);
}
#endif

