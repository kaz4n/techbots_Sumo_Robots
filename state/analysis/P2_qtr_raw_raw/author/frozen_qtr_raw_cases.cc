// Tests D109 from public contracts and independently supplied source records.
// Preserves raw acquisition evidence without pretending to qualify optical color.
// The isolated harness executes actual Runner, adapter, Native and default sketch.
#ifndef D109_TEST_SEPARATE_MAIN
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#endif
#include "doctest.h"
#include "qtr_raw.h"
#include "config.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <new>
#include <type_traits>
#ifdef TEST_NATIVE_BINDING
#include "qtr_raw_native.h"
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
using line_qtr::Snapshot;
using line_qtr::Status;
using line_qtr::RawQualification;
using QPhase = line_qtr::Phase;
using qtr_raw::Phase;
using qtr_raw::Fault;
using qtr_raw::Runner;
constexpr std::uint32_t HALF = 0x80000000U;
enum Event { CLOCK, BEGIN, START, REPORT, ADVANCE, CANCEL };

Snapshot idle(std::uint32_t checked) {
    Snapshot value;
    value.phase = QPhase::IDLE; value.status = Status::OK; value.checked_us = checked;
    return value;
}
Snapshot charging(std::uint32_t base, std::uint32_t sequence) {
    Snapshot value;
    value.phase = QPhase::CHARGING; value.status = Status::OK;
    value.sequence = sequence; value.started_us = base;
    value.drive_completed_us = base + 3U; value.checked_us = base + 4U;
    return value;
}
Snapshot complete(std::uint32_t base, std::uint32_t sequence, std::uint32_t advances = 1U) {
    Snapshot value = charging(base, sequence);
    value.phase = QPhase::COMPLETE; value.valid = true; value.advances = advances;
    value.released_mask = 15U; value.high_mask = 15U; value.low_mask = 15U;
    value.checked_us = base + 108U; value.completed_us = value.checked_us;
    value.max_service_gap_us = 81U;
    value.cleanup.attempted_mask = 15U;
    value.cleanup.started_us = base + 104U; value.cleanup.completed_us = base + 108U;
    for (unsigned i = 0U; i < 4U; ++i) {
        auto& pad = value.pad[i];
        pad.release_before_us = base + 16U + 2U * i;
        pad.release_after_us = base + 17U + 2U * i;
        pad.last_high_before_us = pad.release_after_us + 20U + i;
        pad.first_low_after_us = base + 100U + i;
        pad.lower_us = 19U + i; pad.upper_us = 85U - i;
    }
    return value;
}
Snapshot mixed(std::uint32_t base, std::uint32_t sequence) {
    Snapshot value = complete(base, sequence);
    value.low_mask = 5U; value.timeout_mask = 10U;
    value.checked_us = base + 1548U; value.completed_us = value.checked_us;
    value.cleanup.started_us = base + 1540U; value.cleanup.completed_us = base + 1548U;
    for (unsigned i = 0U; i < 4U; ++i) {
        auto& pad = value.pad[i];
        if ((i & 1U) != 0U) {
            pad.last_high_before_us = pad.release_after_us + 1502U + i;
            pad.first_low_after_us = 0U; pad.lower_us = 1501U + i;
            pad.upper_us = 0U; value.status_by_pad[i] = 1;
        } else {
            pad.first_low_after_us = base + 1530U + i;
            pad.upper_us = 1515U - i;
        }
    }
    return value;
}
Snapshot cancelled(const Snapshot& active, std::uint32_t when) {
    Snapshot value = active;
    value.phase = QPhase::FAULT; value.status = Status::CANCELLED; value.valid = false;
    value.cleanup = {}; value.cleanup.attempted_mask = 15U;
    value.cleanup.started_us = when + 1U; value.cleanup.completed_us = when + 5U;
    value.checked_us = when + 5U; value.completed_us = value.checked_us;
    return value;
}
bool same(const Snapshot& a, const Snapshot& b) {
    if (a.phase != b.phase || a.status != b.status || a.valid != b.valid ||
        a.sequence != b.sequence || a.started_us != b.started_us ||
        a.drive_completed_us != b.drive_completed_us || a.checked_us != b.checked_us ||
        a.completed_us != b.completed_us || a.advances != b.advances ||
        a.max_service_gap_us != b.max_service_gap_us || a.released_mask != b.released_mask ||
        a.high_mask != b.high_mask || a.low_mask != b.low_mask || a.timeout_mask != b.timeout_mask)
        return false;
    const auto& x = a.cleanup; const auto& y = b.cleanup;
    if (x.attempted_mask != y.attempted_mask || x.failed_mask != y.failed_mask ||
        x.skipped_mask != y.skipped_mask || x.nonneutral_mask != y.nonneutral_mask ||
        x.started_us != y.started_us || x.completed_us != y.completed_us ||
        x.deadline_exceeded != y.deadline_exceeded) return false;
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto& p = a.pad[i]; const auto& q = b.pad[i];
        if (a.status_by_pad[i] != b.status_by_pad[i] || x.status[i] != y.status[i] ||
            p.release_before_us != q.release_before_us || p.release_after_us != q.release_after_us ||
            p.last_high_before_us != q.last_high_before_us || p.first_low_after_us != q.first_low_after_us ||
            p.lower_us != q.lower_us || p.upper_us != q.upper_us) return false;
    }
    return true;
}
bool same(const qtr_raw::Timing& a, const qtr_raw::Timing& b) {
    return a.calls == b.calls && a.measured_calls == b.measured_calls && a.last_us == b.last_us &&
           a.maximum_us == b.maximum_us && a.last_valid == b.last_valid;
}
bool same(const qtr_raw::Report& a, const qtr_raw::Report& b) {
    return a.phase == b.phase && a.fault == b.fault && a.fresh == b.fresh &&
        a.counter_saturated == b.counter_saturated && a.clock_fault == b.clock_fault &&
        a.cancel_attempted == b.cancel_attempted && a.setup_status == b.setup_status &&
        a.start_status == b.start_status && a.qualification == b.qualification &&
        a.cancel_qualification == b.cancel_qualification && same(a.snapshot, b.snapshot) &&
        same(a.cancellation, b.cancellation) && a.captured_frames == b.captured_frames &&
        a.not_due == b.not_due && same(a.setup, b.setup) && same(a.start, b.start) &&
        same(a.advance, b.advance) && same(a.cancel, b.cancel) && same(a.poll, b.poll);
}

struct Fake {
    std::uint32_t now = 10000U, setup_cost = 3U, start_cost = 6U, report_cost = 2U;
    std::uint32_t advance_cost = 10U, cancel_cost = 6U;
    unsigned clocks = 0U, begins = 0U, starts = 0U, reports = 0U, advances = 0U, cancels = 0U;
    unsigned fault_at = 0U;
    std::uint32_t fault_delta = HALF;
    std::uint32_t clock_increment = 0U;
    bool automatic = true, automatic_cancel = true, grant = false;
    Status setup_status = Status::OK, start_status = Status::OK;
    Snapshot value, next, cancellation;
    std::array<Event, 4096> trace{};
    unsigned used = 0U;
    void record(Event event) { if (used < trace.size()) trace[used++] = event; }
    qtr_raw::Port port() { return {this, clock, begin, start, report, advance, cancel}; }
    static std::uint32_t clock(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.clocks;
        if (f.clocks == f.fault_at) f.now += f.fault_delta;
        f.record(CLOCK); const auto out = f.now; f.now += f.clock_increment; return out;
    }
    static Status begin(void* context, bool grant) {
        auto& f = *static_cast<Fake*>(context); ++f.begins; f.record(BEGIN); f.grant = grant;
        if (f.automatic) f.value = idle(f.now + 2U);
        f.now += f.setup_cost; return f.setup_status;
    }
    static Status start(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.starts; f.record(START);
        if (f.automatic && f.start_status == Status::OK)
            f.value = charging(f.now + 1U, f.value.sequence + 1U);
        f.now += f.start_cost; return f.start_status;
    }
    static Snapshot report(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.reports; f.record(REPORT);
        f.now += f.report_cost; return f.value;
    }
    static Snapshot advance(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.advances; f.record(ADVANCE);
        f.value = f.next; f.now += f.advance_cost; return f.value;
    }
    static Snapshot cancel(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.cancels; f.record(CANCEL);
        if (f.automatic_cancel) f.cancellation = cancelled(f.value, f.now);
        f.now += f.cancel_cost; return f.cancellation;
    }
};
void running(Fake& f, Runner& r) {
    REQUIRE(r.begin({true})); REQUIRE(r.report().phase == Phase::RUNNING);
    CHECK(f.begins == 1U); CHECK(f.reports == 1U); CHECK(f.clocks == 3U);
}
void active(Fake& f, Runner& r) {
    running(f, r); CHECK_FALSE(r.poll()); REQUIRE(r.report().phase == Phase::RUNNING);
    REQUIRE(r.report().snapshot.phase == QPhase::CHARGING);
}
void prepareComplete(Fake& f, bool timeout = false) {
    f.next = timeout ? mixed(f.value.started_us, f.value.sequence) : complete(f.value.started_us, f.value.sequence);
    f.now = f.value.started_us + (timeout ? 1539U : 99U);
}
void traceIs(const Fake& f, std::initializer_list<Event> events) {
    REQUIRE(f.used == events.size()); unsigned index = 0U;
    for (const auto expected : events) { CHECK(f.trace[index] == expected); ++index; }
}
void terminal(Fake& f, Runner& r) {
    auto before = r.report(); before.fresh = false; const auto used = f.used;
    CHECK_FALSE(r.poll()); r.stop(); CHECK_FALSE(r.begin({true}));
    CHECK(same(r.report(), before)); CHECK(f.used == used);
}
void faultIs(Fake& f, Runner& r, Fault fault, unsigned cancels) {
    CHECK(r.report().phase == Phase::FAULT); CHECK(r.report().fault == fault);
    CHECK(f.cancels == cancels); CHECK(r.report().cancel.calls == cancels);
    terminal(f, r);
}
} // namespace

TEST_CASE("D109 fixture raw qualification uses actual shared validator") {
    CHECK(line_qtr::validateRaw(Snapshot{}) == RawQualification::ABSENT);
    CHECK(line_qtr::validateRaw(idle(200U)) == RawQualification::ABSENT);
    CHECK(line_qtr::validateRaw(charging(100U, 1U)) == RawQualification::ABSENT);
    for (auto base : {100U, 0xfffffff0U}) {
        CHECK(line_qtr::validateRaw(complete(base, 1U)) == RawQualification::VALID);
        CHECK(line_qtr::validateRaw(mixed(base, 1U)) == RawQualification::VALID);
    }
    auto value = cancelled(charging(100U, 1U), 130U);
    CHECK(line_qtr::validateRaw(value) == RawQualification::PROVIDER_FAULT);
    value.status = Status::BUSY;
    CHECK(line_qtr::validateRaw(value) == RawQualification::INVALID);
    value = complete(100U, 1U); ++value.pad[2].upper_us;
    CHECK(line_qtr::validateRaw(value) == RawQualification::INVALID);
}

TEST_CASE("D109 passive constructors disabled precedence and repeat attempt") {
    STATIC_REQUIRE_FALSE(std::is_copy_constructible<Runner>::value);
    STATIC_REQUIRE_FALSE(std::is_copy_assignable<Runner>::value);
    STATIC_REQUIRE(std::is_same<decltype(std::declval<const Runner&>().capture(0U)), const Snapshot*>::value);
    Fake f; Runner r(f.port()); const auto initial = r.report();
    CHECK(r.captureCapacity() == config::QTR_BENCH_FRAMES);
    CHECK(r.captureCount() == 0U); CHECK(r.capture(0U) == nullptr); CHECK(r.capture(0xffffffffU) == nullptr);
    CHECK_FALSE(r.poll()); r.stop(); CHECK(same(initial, r.report())); CHECK(f.used == 0U);
    CHECK(r.begin({})); CHECK(r.report().phase == Phase::DISABLED);
    terminal(f, r); CHECK(f.used == 0U);
    Runner absent({}); CHECK(absent.begin({})); CHECK(absent.report().phase == Phase::DISABLED);
    CHECK_FALSE(absent.poll()); CHECK_FALSE(absent.begin({true}));
}

TEST_CASE("D109 every missing callback fails before any callback") {
    for (unsigned missing = 0U; missing < 6U; ++missing) {
        CAPTURE(missing); Fake f; auto port = f.port();
        if (missing == 0U) port.clockUs = nullptr;
        if (missing == 1U) port.begin = nullptr;
        if (missing == 2U) port.start = nullptr;
        if (missing == 3U) port.report = nullptr;
        if (missing == 4U) port.advance = nullptr;
        if (missing == 5U) port.cancel = nullptr;
        Runner r(port); CHECK_FALSE(r.begin({true})); faultIs(f, r, Fault::PORT, 0U);
        CHECK(f.used == 0U);
    }
}

TEST_CASE("D109 zero capacity refuses enabled begin and preserves default silence") {
    if constexpr (config::QTR_BENCH_FRAMES == 0U) {
        Fake f; Runner r(f.port()); CHECK_FALSE(r.begin({true}));
        CHECK(r.captureCapacity() == 0U); CHECK(r.captureCount() == 0U);
        faultIs(f, r, Fault::CONFIG, 0U); CHECK(f.used == 0U);
        Runner disabled(f.port()); CHECK(disabled.begin({})); CHECK_FALSE(disabled.poll());
        CHECK(disabled.report().phase == Phase::DISABLED); CHECK(f.used == 0U);
    }
}

TEST_CASE("D109 exact command order timings and no repeated initialization") {
    Fake f; auto copied = f.port(); Runner r(copied); copied = {};
    running(f, r); traceIs(f, {CLOCK, BEGIN, REPORT, CLOCK, CLOCK}); CHECK(f.grant);
    CHECK(r.report().setup.calls == 1U); CHECK(r.report().setup.measured_calls == 1U);
    CHECK(r.report().setup.last_valid); CHECK(r.report().setup.last_us == 5U);
    const auto retained = r.report(); CHECK_FALSE(r.begin({false})); CHECK(same(retained, r.report()));
    f.used = 0U; CHECK_FALSE(r.poll()); traceIs(f, {CLOCK, START, REPORT, CLOCK, CLOCK});
    CHECK(r.report().start.calls == 1U); CHECK(r.report().start.last_us == 8U);
    CHECK(r.report().poll.calls == 1U); CHECK(r.report().poll.last_us == 8U);
    f.used = 0U; prepareComplete(f); const auto source = f.next; REQUIRE(r.poll());
    traceIs(f, {CLOCK, ADVANCE, CLOCK, CLOCK}); CHECK(r.report().advance.last_us == 10U);
    CHECK(r.report().poll.measured_calls == 2U); CHECK(r.report().poll.maximum_us == 10U);
    CHECK(same(r.report().snapshot, source)); REQUIRE(r.capture(0U)); CHECK(same(*r.capture(0U), source));
    CHECK(r.report().qualification == RawQualification::VALID);
    CHECK(f.reports == 2U); CHECK_FALSE(r.report().counter_saturated);
}

TEST_CASE("D109 finite complete capture preserves all records pointers and final pulse") {
    Fake f; Runner r(f.port()); running(f, r);
    std::array<Snapshot, config::QTR_BENCH_FRAMES> expected{};
    std::array<const Snapshot*, config::QTR_BENCH_FRAMES> address{};
    for (std::uint32_t i = 0U; i < config::QTR_BENCH_FRAMES; ++i) {
        if (i != 0U) f.now = expected[i - 1U].started_us + 1999U;
        CHECK_FALSE(r.poll()); REQUIRE(r.report().phase == Phase::RUNNING);
        prepareComplete(f, (i & 1U) != 0U); expected[i] = f.next;
        allocations::calls = 0U; allocations::active = true;
        const bool appended = r.poll(); allocations::active = false;
        REQUIRE(appended); CHECK(allocations::calls == 0U); CHECK(r.report().fresh);
        CHECK(r.captureCount() == i + 1U); CHECK(r.report().captured_frames == i + 1U);
        address[i] = r.capture(i); REQUIRE(address[i]); CHECK(same(*address[i], expected[i]));
        CHECK(r.capture(i + 1U) == nullptr); CHECK(r.capture(0xffffffffU) == nullptr);
        const auto used = f.used;
        for (std::uint32_t j = 0U; j <= i; ++j) {
            CHECK(r.capture(j) == address[j]); CHECK(same(*r.capture(j), expected[j]));
        }
        CHECK(f.used == used);
    }
    CHECK(r.report().phase == Phase::COMPLETE); CHECK(f.starts == config::QTR_BENCH_FRAMES);
    CHECK(f.advances == config::QTR_BENCH_FRAMES); CHECK(f.cancels == 0U);
    terminal(f, r);
    for (std::uint32_t i = 0U; i < config::QTR_BENCH_FRAMES; ++i)
        CHECK(same(*r.capture(i), expected[i]));
}

TEST_CASE("D109 pending phase progression and native-owned acquisition guards") {
    Fake f; Runner r(f.port()); active(f, r); const auto original = f.value;
    f.next = original; f.next.advances = 1U; f.next.checked_us = f.now + 5U;
    CHECK_FALSE(r.poll()); CHECK(r.report().qualification == RawQualification::ABSENT);
    f.next = f.value; f.next.phase = QPhase::DISCHARGING; f.next.released_mask = 15U;
    f.next.advances = 2U; f.next.checked_us = f.now + 5U; CHECK_FALSE(r.poll());
    f.now += 100000U; f.next = f.value; ++f.next.advances; f.next.checked_us = f.now + 5U;
    CHECK_FALSE(r.poll()); CHECK(r.report().phase == Phase::RUNNING);
    CHECK(r.captureCount() == 0U); CHECK(f.starts == 1U); CHECK(f.reports == 2U);
    r.stop(); CHECK(r.report().phase == Phase::STOPPED); CHECK(f.cancels == 1U);
}

TEST_CASE("D109 setup status shape source and provider failures remain distinct") {
    for (unsigned mode = 0U; mode < 5U; ++mode) {
        CAPTURE(mode); Fake f; f.automatic = false; f.value = idle(f.now + 2U);
        Fault expected = Fault::CONTRACT; unsigned cancels = 1U;
        if (mode == 0U) f.setup_status = Status::BUSY;
        if (mode == 1U) f.value.phase = QPhase::CHARGING;
        if (mode == 2U) { f.value.checked_us = f.now - 1U; expected = Fault::SOURCE_ORDER; }
        if (mode == 3U) f.value.valid = true;
        if (mode == 4U) {
            f.value = cancelled({}, f.now); f.value.status = Status::OWNERSHIP;
            f.setup_status = Status::OWNERSHIP; expected = Fault::PROVIDER; cancels = 0U;
        }
        const auto primary = f.value; Runner r(f.port()); CHECK_FALSE(r.begin({true}));
        CHECK(same(r.report().snapshot, primary)); faultIs(f, r, expected, cancels);
    }
}

TEST_CASE("D109 first start requires sequence one advances zero and admitted bracket") {
    for (unsigned mode = 0U; mode < 8U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); running(f, r); f.automatic = false;
        f.value = charging(f.now + 1U, 1U); Fault expected = Fault::SOURCE_ORDER;
        if (mode == 0U) f.value.sequence = 0U;
        if (mode == 1U) f.value.sequence = 2U;
        if (mode == 2U) f.value.advances = 1U;
        if (mode == 3U) f.value.started_us = f.now - 1U;
        if (mode == 4U) f.value.drive_completed_us = f.now;
        if (mode == 5U) f.value.checked_us = f.now + 9U;
        if (mode == 6U) { f.start_status = Status::BUSY; expected = Fault::CONTRACT; }
        if (mode == 7U) { f.value.phase = QPhase::IDLE; f.value = idle(f.now); expected = Fault::CONTRACT; }
        const auto primary = f.value; CHECK_FALSE(r.poll());
        CHECK(same(r.report().snapshot, primary)); faultIs(f, r, expected, 1U);
    }
}

TEST_CASE("D109 advancing source identity count and checked bracket cannot be replayed") {
    for (unsigned mode = 0U; mode < 7U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r);
        f.next = f.value; f.next.advances = 1U; f.next.checked_us = f.now + 5U;
        if (mode == 0U) ++f.next.sequence;
        if (mode == 1U) ++f.next.started_us;
        if (mode == 2U) ++f.next.drive_completed_us;
        if (mode == 3U) f.next.advances = 0U;
        if (mode == 4U) f.next.advances = 2U;
        if (mode == 5U) f.next.checked_us = f.now - 1U;
        if (mode == 6U) f.next.checked_us = f.now + 11U;
        CHECK_FALSE(r.poll()); faultIs(f, r, Fault::SOURCE_ORDER, 1U);
    }
}

TEST_CASE("D109 illegal return phases statuses and malformed raw fail contract") {
    for (unsigned mode = 0U; mode < 8U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r);
        f.next = f.value; f.next.advances = 1U; f.next.checked_us = f.now + 5U;
        if (mode == 0U) f.next = idle(f.now);
        if (mode == 1U) f.next.status = Status::BUSY;
        if (mode == 2U) f.next.phase = static_cast<QPhase>(255U);
        if (mode == 3U) f.next.status = static_cast<Status>(255U);
        if (mode == 4U) f.next.valid = true;
        if (mode == 5U) f.next.released_mask = 16U;
        if (mode == 6U) { prepareComplete(f); ++f.next.pad[1].upper_us; }
        if (mode == 7U) { f.next.phase = QPhase::FAULT; f.next.status = Status::FAULT_LATCHED; }
        CHECK_FALSE(r.poll()); CHECK(r.captureCount() == 0U);
        faultIs(f, r, Fault::CONTRACT, 1U);
    }
}

TEST_CASE("D109 discharging cannot return charging") {
    Fake f; Runner r(f.port()); active(f, r);
    f.next = f.value; f.next.phase = QPhase::DISCHARGING; f.next.released_mask = 15U;
    f.next.advances = 1U; f.next.checked_us = f.now + 5U; CHECK_FALSE(r.poll());
    f.next = charging(f.value.started_us, 1U); f.next.advances = 2U; f.next.checked_us = f.now + 5U;
    CHECK_FALSE(r.poll()); faultIs(f, r, Fault::CONTRACT, 1U);
}

TEST_CASE("D109 uint32 clock wrap retains exact native source intervals") {
    Fake f; f.now = 0xffffffd0U; Runner r(f.port()); active(f, r);
    prepareComplete(f); const auto value = f.next; REQUIRE(r.poll());
    CHECK(r.report().fault == Fault::NONE); CHECK_FALSE(r.report().clock_fault);
    CHECK(same(*r.capture(0U), value)); CHECK(r.report().poll.last_us == 10U);
}

TEST_CASE("D109 closing clock failure never exposes tentative complete slot") {
    Fake f; Runner r(f.port()); active(f, r); prepareComplete(f);
    f.fault_at = f.clocks + 3U; CHECK_FALSE(r.poll());
    CHECK(r.captureCount() == 0U); CHECK(r.capture(0U) == nullptr); CHECK_FALSE(r.report().fresh);
    CHECK(r.report().advance.last_valid); CHECK(r.report().advance.last_us == 10U);
    CHECK_FALSE(r.report().poll.last_valid); CHECK(r.report().poll.last_us == 8U);
    CHECK(r.report().poll.measured_calls == 1U); CHECK(r.report().clock_fault);
    faultIs(f, r, Fault::CLOCK, 0U);
}

TEST_CASE("D109 bad A on complete keeps active uncertainty and cancels without clocks") {
    Fake f; Runner r(f.port()); active(f, r); prepareComplete(f);
    f.used = 0U; f.fault_at = f.clocks + 2U; CHECK_FALSE(r.poll());
    traceIs(f, {CLOCK, ADVANCE, CLOCK, CANCEL}); CHECK(r.captureCount() == 0U);
    CHECK_FALSE(r.report().advance.last_valid); CHECK_FALSE(r.report().cancel.last_valid);
    faultIs(f, r, Fault::CLOCK, 1U);
}

TEST_CASE("D109 bad S prevents command but cancels previously active owner") {
    for (bool already_active : {false, true}) for (bool reverse : {false, true}) {
        CAPTURE(already_active); CAPTURE(reverse); Fake f; Runner r(f.port());
        if (reverse) f.fault_delta = 0xffffffffU;
        if (already_active) active(f, r); else running(f, r);
        const auto saved_start = r.report().start; f.used = 0U;
        f.fault_at = f.clocks + 1U; CHECK_FALSE(r.poll());
        CHECK(same(saved_start, r.report().start)); CHECK(f.advances == 0U);
        if (already_active) traceIs(f, {CLOCK, CANCEL}); else traceIs(f, {CLOCK});
        CHECK(r.report().poll.calls == (already_active ? 2U : 1U));
        faultIs(f, r, Fault::CLOCK, already_active ? 1U : 0U);
    }
}

TEST_CASE("D109 semantic primary fault precedes independent bad A evidence") {
    for (unsigned mode = 0U; mode < 3U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r);
        f.next = f.value; f.next.advances = 1U; f.next.checked_us = f.now + 5U;
        Fault expected = Fault::CONTRACT; unsigned cancellations = 1U;
        if (mode == 0U) f.next.valid = true;
        if (mode == 1U) { ++f.next.sequence; expected = Fault::SOURCE_ORDER; }
        if (mode == 2U) { f.next = cancelled(f.value, f.now); f.next.status = Status::CLEANUP;
            f.next.cleanup.failed_mask = 1U; expected = Fault::PROVIDER; cancellations = 0U; }
        f.fault_at = f.clocks + 2U; const auto primary = f.next;
        CHECK_FALSE(r.poll()); CHECK(r.report().clock_fault); CHECK(same(primary, r.report().snapshot));
        CHECK_FALSE(r.report().advance.last_valid); faultIs(f, r, expected, cancellations);
    }
}

TEST_CASE("D109 nonclock fault includes cleanup in poll timing and preserves primary snapshot") {
    Fake f; Runner r(f.port()); active(f, r); f.used = 0U;
    f.next = f.value; f.next.valid = true; const auto primary = f.next;
    CHECK_FALSE(r.poll()); traceIs(f, {CLOCK, ADVANCE, CLOCK, CLOCK, CANCEL, CLOCK, CLOCK});
    CHECK(same(primary, r.report().snapshot)); CHECK(same(f.cancellation, r.report().cancellation));
    CHECK(r.report().qualification == RawQualification::INVALID);
    CHECK(r.report().cancel_qualification == RawQualification::PROVIDER_FAULT);
    CHECK(r.report().advance.last_us == 10U); CHECK(r.report().advance.last_valid);
    CHECK(r.report().cancel.last_us == 6U); CHECK(r.report().cancel.last_valid);
    CHECK(r.report().poll.last_us == 16U); CHECK(r.report().poll.last_valid);
    faultIs(f, r, Fault::CONTRACT, 1U);
}

TEST_CASE("D109 setup closing neutral failure and active start closing failure differ") {
    for (bool during_start : {false, true}) {
        CAPTURE(during_start); Fake f; Runner r(f.port());
        if (during_start) {
            running(f, r); f.fault_at = f.clocks + 3U; CHECK_FALSE(r.poll());
            CHECK(r.report().start.last_valid); CHECK(r.report().start.last_us == 8U);
        } else {
            f.fault_at = 3U; CHECK_FALSE(r.begin({true})); CHECK_FALSE(r.report().setup.last_valid);
            CHECK(r.report().setup.measured_calls == 0U);
        }
        faultIs(f, r, Fault::CLOCK, during_start ? 1U : 0U);
    }
}

TEST_CASE("D109 aggregate operation and source era reject half range without alias") {
    SUBCASE("setup aggregate") {
        Fake f; f.setup_cost = HALF - 20U; f.report_cost = 0U;
        f.automatic = false; f.value = idle(f.now + 1U);
        f.clock_increment = 10U; Runner r(f.port()); CHECK_FALSE(r.begin({true}));
        CHECK(r.report().clock_fault); faultIs(f, r, Fault::CLOCK, 0U);
    }
    SUBCASE("source era includes A minus actual start") {
        Fake f; Runner r(f.port()); active(f, r); const auto base = f.value.started_us;
        f.now = base + HALF; f.used = 0U; CHECK_FALSE(r.poll());
        traceIs(f, {CLOCK, CANCEL}); CHECK(f.advances == 0U); faultIs(f, r, Fault::CLOCK, 1U);
    }
    SUBCASE("half range minus one is still admitted with equal A C") {
        Fake f; Runner r(f.port()); active(f, r); f.advance_cost = 0U;
        f.now = f.value.started_us + HALF - 1U;
        f.next = f.value; f.next.advances = 1U; f.next.checked_us = f.now;
        CHECK_FALSE(r.poll()); CHECK(r.report().phase == Phase::RUNNING);
        CHECK_FALSE(r.report().clock_fault); CHECK(r.report().advance.last_valid);
        CHECK(r.report().advance.last_us == 0U); CHECK(r.report().poll.last_us == 0U);
    }
    SUBCASE("two valid inter-poll increments cannot resurrect old source") {
        Fake f; Runner r(f.port()); active(f, r);
        f.now += HALF / 2U; f.next = f.value; f.next.advances = 1U; f.next.checked_us = f.now + 1U;
        CHECK_FALSE(r.poll()); REQUIRE(r.report().phase == Phase::RUNNING);
        f.now += HALF / 2U; f.used = 0U; CHECK_FALSE(r.poll());
        traceIs(f, {CLOCK, CANCEL}); faultIs(f, r, Fault::CLOCK, 1U);
    }
}

TEST_CASE("D109 stop neutral active and cleanup record semantics") {
    SUBCASE("neutral IDLE is passive") {
        Fake f; Runner r(f.port()); running(f, r); f.used = 0U; r.stop();
        CHECK(r.report().phase == Phase::STOPPED); CHECK(f.used == 0U); terminal(f, r);
    }
    SUBCASE("active cleanup timed and primary retained") {
        Fake f; Runner r(f.port()); active(f, r); const auto primary = r.report().snapshot;
        f.used = 0U; r.stop(); traceIs(f, {CLOCK, CANCEL, CLOCK});
        CHECK(r.report().phase == Phase::STOPPED); CHECK(r.report().fault == Fault::NONE);
        CHECK(same(r.report().snapshot, primary)); CHECK(same(r.report().cancellation, f.cancellation));
        CHECK(r.report().cancel.last_us == 6U); CHECK(r.report().cancel.measured_calls == 1U);
        CHECK(r.captureCount() == 0U); terminal(f, r);
    }
}

TEST_CASE("D109 stop cleanup failures shape identity statuses and brackets") {
    for (unsigned mode = 0U; mode < 13U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r); f.automatic_cancel = false;
        f.cancellation = cancelled(f.value, f.now); Fault expected = Fault::CLEANUP;
        if (mode == 0U) f.cancellation.cleanup.failed_mask = 1U;
        if (mode == 1U) f.cancellation.cleanup.skipped_mask = 1U;
        if (mode == 2U) f.cancellation.cleanup.nonneutral_mask = 1U;
        if (mode == 3U) f.cancellation.cleanup.status[2] = -5;
        if (mode == 4U) f.cancellation.cleanup.deadline_exceeded = true;
        if (mode == 5U) f.cancellation.status = Status::CLEANUP;
        if (mode == 6U) { ++f.cancellation.sequence; expected = Fault::SOURCE_ORDER; }
        if (mode == 7U) { f.cancellation.status = Status::NATIVE_ERROR; expected = Fault::CONTRACT; }
        if (mode == 8U) { f.cancellation.valid = true; expected = Fault::CONTRACT; }
        if (mode == 9U) { f.cancellation.cleanup.started_us = f.now - 1U; expected = Fault::SOURCE_ORDER; }
        if (mode == 10U) { ++f.cancellation.checked_us; expected = Fault::SOURCE_ORDER; }
        if (mode == 11U) { f.cancellation.cleanup.completed_us = f.now + 7U; expected = Fault::SOURCE_ORDER; }
        if (mode == 12U) f.cancellation.cleanup.attempted_mask = 7U;
        const auto actual = f.cancellation; r.stop(); CHECK(same(actual, r.report().cancellation));
        CHECK(r.report().cancel.last_valid); faultIs(f, r, expected, 1U);
    }
}

TEST_CASE("D109 bad cancellation clocks forbid all later wrapper observations") {
    for (bool stopping : {false, true}) for (unsigned which = 1U; which <= 2U; ++which) {
        CAPTURE(stopping); CAPTURE(which); Fake f; Runner r(f.port()); active(f, r);
        f.used = 0U;
        if (stopping) { f.fault_at = f.clocks + which; r.stop(); }
        else {
            f.next = f.value; f.next.valid = true; f.fault_at = f.clocks + which + 2U;
            CHECK_FALSE(r.poll());
        }
        CHECK(r.report().clock_fault); CHECK_FALSE(r.report().cancel.last_valid);
        CHECK(f.trace[f.used - 1U] == (which == 1U ? CANCEL : CLOCK));
        const unsigned expected = stopping ? which + 1U : which + 4U;
        CHECK(f.used == expected); faultIs(f, r, stopping ? Fault::CLOCK : Fault::CONTRACT, 1U);
    }
}

TEST_CASE("D109 stop primary semantic failure wins bad Q and has no recursion") {
    Fake f; Runner r(f.port()); active(f, r); f.automatic_cancel = false;
    f.cancellation = cancelled(f.value, f.now); ++f.cancellation.sequence;
    f.cancellation.cleanup.failed_mask = 1U; f.fault_at = f.clocks + 2U;
    r.stop(); CHECK(r.report().clock_fault); faultIs(f, r, Fault::SOURCE_ORDER, 1U);
}

TEST_CASE("D109 known provider failure is measured and never cancelled again") {
    for (Status status : {Status::OWNERSHIP, Status::NATIVE_ERROR, Status::READBACK,
         Status::CHARGE_LOW, Status::TIME_ORDER, Status::CALL_DEADLINE, Status::CHARGE_DEADLINE,
         Status::FRAME_DEADLINE, Status::ADVANCE_LIMIT, Status::CLEANUP, Status::CANCELLED}) {
        CAPTURE(static_cast<unsigned>(status)); Fake f; Runner r(f.port()); active(f, r);
        f.next = cancelled(f.value, f.now); f.next.status = status;
        f.next.cleanup.failed_mask = 2U; f.next.cleanup.status[1] = -5;
        CHECK_FALSE(r.poll()); CHECK(r.report().qualification == RawQualification::PROVIDER_FAULT);
        CHECK(same(r.report().snapshot, f.next)); CHECK(r.report().advance.last_valid);
        CHECK(r.report().advance.last_us == 10U); CHECK(r.report().poll.last_us == 10U);
        CHECK_FALSE(r.report().cancel_attempted); faultIs(f, r, Fault::PROVIDER, 0U);
    }
}

TEST_CASE("D109 complete source outside actual advance bracket is never published") {
    for (bool before : {false, true}) {
        Fake f; Runner r(f.port()); active(f, r); prepareComplete(f);
        f.now = f.value.started_us + (before ? 109U : 80U);
        CHECK_FALSE(r.poll()); CHECK(r.report().qualification == RawQualification::VALID);
        CHECK(r.captureCount() == 0U); faultIs(f, r, Fault::SOURCE_ORDER, 1U);
    }
}

TEST_CASE("D109 every invoked acquisition path remains heap free") {
    Fake f; Runner r(f.port()); allocations::calls = 0U; allocations::active = true;
    const bool began = r.begin({true}); const bool first = r.poll();
    f.next = f.value; f.next.advances = 1U; f.next.checked_us = f.now + 5U;
    const bool pending = r.poll(); r.stop(); allocations::active = false;
    CHECK(began); CHECK_FALSE(first); CHECK_FALSE(pending); CHECK(allocations::calls == 0U);
    CHECK(r.report().phase == Phase::STOPPED); CHECK(f.cancels == 1U);
}

#ifndef TEST_CAPACITY_ONE
TEST_CASE("D109 NOT_DUE preserves complete record and permits S A boundary straddle") {
    for (unsigned mode = 0U; mode < 4U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r); prepareComplete(f); REQUIRE(r.poll());
        const auto captured = *r.capture(0U); f.start_status = Status::NOT_DUE;
        f.now = captured.started_us + (mode == 2U ? 2000U : 1999U);
        if (mode == 1U) ++f.value.max_service_gap_us;
        if (mode == 3U) f.fault_at = f.clocks + 2U;
        CHECK_FALSE(r.poll()); CHECK(r.report().not_due == 1U); CHECK(r.captureCount() == 1U);
        CHECK(same(*r.capture(0U), captured)); CHECK_FALSE(r.report().fresh);
        if (mode == 0U) { CHECK(r.report().phase == Phase::RUNNING); r.stop(); CHECK(f.cancels == 0U); }
        else faultIs(f, r, mode == 3U ? Fault::CLOCK : Fault::CONTRACT, 1U);
    }
}

TEST_CASE("D109 first NOT_DUE and incompatible unchanged command fail contract") {
    Fake f; Runner r(f.port()); running(f, r); f.start_status = Status::NOT_DUE;
    CHECK_FALSE(r.poll()); CHECK(r.report().not_due == 1U);
    faultIs(f, r, Fault::CONTRACT, 1U);
}

TEST_CASE("D109 NOT_DUE identity changes precede A clocks and bad C preserves neutral evidence") {
    for (unsigned mode = 0U; mode < 7U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r); prepareComplete(f); REQUIRE(r.poll());
        f.start_status = Status::NOT_DUE; f.now = f.value.started_us + 500U;
        if (mode == 0U) ++f.value.sequence;
        if (mode == 1U) { ++f.value.started_us; ++f.value.drive_completed_us; }
        if (mode == 2U) ++f.value.drive_completed_us;
        if (mode == 3U) ++f.value.advances;
        if (mode == 4U) { ++f.value.completed_us; ++f.value.checked_us; ++f.value.cleanup.completed_us; }
        if (mode == 5U) { ++f.value.sequence; f.fault_at = f.clocks + 2U; }
        if (mode == 6U) f.fault_at = f.clocks + 3U;
        CHECK_FALSE(r.poll()); CHECK(r.report().not_due == 1U); CHECK(r.captureCount() == 1U);
        if (mode == 6U) CHECK(r.report().start.last_valid);
        faultIs(f, r, mode == 6U ? Fault::CLOCK : Fault::SOURCE_ORDER, mode == 6U ? 0U : 1U);
    }
}

TEST_CASE("D109 later start spacing sequence and previously published records survive fault") {
    for (unsigned mode = 0U; mode < 4U; ++mode) {
        CAPTURE(mode); Fake f; Runner r(f.port()); active(f, r); prepareComplete(f); REQUIRE(r.poll());
        const auto first = *r.capture(0U); f.now = first.started_us + (mode == 0U ? 1998U : 1999U);
        f.automatic = false; f.value = charging(f.now + 1U, mode == 1U ? 1U : 2U);
        if (mode == 2U) f.value.sequence = 3U;
        if (mode == 3U) f.value.started_us = first.completed_us - 1U;
        CHECK_FALSE(r.poll()); faultIs(f, r, Fault::SOURCE_ORDER, 1U);
        CHECK(r.captureCount() == 1U); CHECK(same(*r.capture(0U), first)); CHECK(r.capture(1U) == nullptr);
    }
}

TEST_CASE("D109 second frame active stop retains first capture without appending partial") {
    Fake f; Runner r(f.port()); active(f, r); prepareComplete(f); REQUIRE(r.poll());
    const auto first = *r.capture(0U); f.now = first.started_us + 1999U;
    CHECK_FALSE(r.poll()); r.stop(); CHECK(r.report().phase == Phase::STOPPED);
    CHECK(r.captureCount() == 1U); CHECK(same(*r.capture(0U), first)); CHECK(r.capture(1U) == nullptr);
    terminal(f, r);
}
#endif

#ifdef TEST_NATIVE_BINDING
namespace native_fake {
unsigned clocks = 0U, begins = 0U, starts = 0U, advances = 0U, cancels = 0U;
bool grant = false; const line_qtr::Reader* first = nullptr; bool same_owner = true;
std::uint32_t now = 20000U;
void owner(const line_qtr::Reader* value) {
    if (!first) first = value;
    same_owner = same_owner && value == first;
}
void reset() { clocks = begins = starts = advances = cancels = 0U; first = nullptr; same_owner = true; }
}
unsigned long micros() { ++native_fake::clocks; return native_fake::now; }
namespace line_qtr {
Status Reader::begin(bool grant) {
    native_fake::owner(this); ++native_fake::begins; native_fake::grant = grant;
    result_ = idle(native_fake::now); return Status::OK;
}
Status Reader::start() {
    native_fake::owner(this); ++native_fake::starts;
    result_ = charging(native_fake::now + 1U, result_.sequence + 1U); native_fake::now += 8U;
    return Status::OK;
}
Snapshot Reader::advance() {
    native_fake::owner(this); ++native_fake::advances;
    result_ = complete(result_.started_us, result_.sequence); native_fake::now = result_.completed_us;
    return result_;
}
Snapshot Reader::cancel() {
    native_fake::owner(this); ++native_fake::cancels;
    result_ = cancelled(result_, native_fake::now); native_fake::now += 6U; return result_;
}
}
TEST_CASE("D109 default sketch actual setup loop make no callbacks") {
    CHECK(native_fake::clocks == 0U); CHECK(native_fake::begins == 0U);
    CHECK(native_fake::starts == 0U); CHECK(native_fake::advances == 0U); CHECK(native_fake::cancels == 0U);
    setup(); for (unsigned i = 0U; i < 100U; ++i) loop();
    CHECK(native_fake::clocks == 0U); CHECK(native_fake::begins == 0U);
    CHECK(native_fake::starts == 0U); CHECK(native_fake::advances == 0U); CHECK(native_fake::cancels == 0U);
}
TEST_CASE("D109 Native actual binding is passive and delegates one stable Reader") {
    STATIC_REQUIRE_FALSE(std::is_copy_constructible<qtr_raw::Native>::value);
    STATIC_REQUIRE_FALSE(std::is_copy_assignable<qtr_raw::Native>::value);
    native_fake::reset();
    {
        qtr_raw::Native native; const auto port = native.port(); const auto again = native.port();
        CHECK(port.context == again.context); CHECK(native_fake::begins == 0U); CHECK(native_fake::clocks == 0U);
        REQUIRE(port.clockUs); REQUIRE(port.begin); REQUIRE(port.start); REQUIRE(port.report);
        REQUIRE(port.advance); REQUIRE(port.cancel);
        CHECK(port.clockUs(port.context) == native_fake::now); CHECK(native_fake::clocks == 1U);
        CHECK(port.begin(port.context, false) == Status::OK); CHECK_FALSE(native_fake::grant);
        CHECK(port.report(port.context).phase == QPhase::IDLE);
        CHECK(port.begin(port.context, true) == Status::OK); CHECK(native_fake::grant);
        CHECK(port.start(port.context) == Status::OK); const auto active = port.report(port.context);
        CHECK(active.phase == QPhase::CHARGING); CHECK(active.sequence == 1U);
        const auto done = port.advance(port.context); CHECK(same(done, port.report(port.context)));
        CHECK(done.phase == QPhase::COMPLETE);
        const auto ended = port.cancel(port.context); CHECK(same(ended, port.report(port.context)));
        CHECK(ended.status == Status::CANCELLED); CHECK(native_fake::same_owner);
    }
    CHECK(native_fake::begins == 2U); CHECK(native_fake::starts == 1U);
    CHECK(native_fake::advances == 1U); CHECK(native_fake::cancels == 1U); CHECK(native_fake::clocks == 1U);
}
#endif
