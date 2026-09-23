// Checks D107 through frozen public callbacks, literal pixels and actual clocks.
// No private-state seeding or implementation-derived expectations are used.
// The isolated Python harness runs normal, sanitizer and native-binding profiles.
#ifndef D107_TEST_SEPARATE_MAIN
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#endif
#include "doctest.h"
#include "opp_view.h"
#include "config.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <type_traits>
#ifdef TEST_NATIVE_BINDING
#include "opp_view_native.h"
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
using opp_view::Fault;
using opp_view::Phase;
using opp_view::Runner;
using ui::MatrixStatus;
constexpr std::uint32_t HALF = 0x80000000U;
enum Event { CLOCK, OPP_BEGIN, OPP_READ, MATRIX_BEGIN, MATRIX_SUBMIT };
struct Observation { Event event; std::uint32_t time; };

struct Fake {
    std::uint32_t now = 10000U, clock_cost = 0U;
    std::uint32_t setup_cost = 7U, matrix_setup_cost = 11U;
    std::uint32_t read_cost = 20U, submit_cost = 40U;
    unsigned clock_calls = 0U, opp_begins = 0U, reads = 0U;
    unsigned matrix_begins = 0U, submits = 0U;
    unsigned fault_at_clock = 0U, fault_delay_after_read = 0U;
    unsigned fault_delay_after_submit = 0U;
    std::uint32_t fault_delta = 0xffffffffU;
    opp_sensors::InitResult initial{true, 0x7fU, {}};
    opp_sensors::Snapshot value;
    bool automatic_times = true;
    MatrixStatus begin_status = MatrixStatus::INIT_UNCONFIRMED;
    MatrixStatus submit_status = MatrixStatus::SUBMITTED_UNCONFIRMED;
    ui::MatrixGrant grant;
    ui::Frame sent;
    std::uint32_t sent_time = 0U;
    std::array<Observation, 128> trace{};
    std::size_t used = 0U;
    Fake() { levels(0U); }
    void levels(unsigned raw) {
        value.valid = true; value.raw_mask = static_cast<std::uint8_t>(raw);
        value.valid_mask = 0x7fU;
        for (unsigned i = 0U; i < 7U; ++i) value.status[i] = (raw >> i) & 1U;
    }
    void record(Event event) {
        if (used < trace.size()) trace[used++] = {event, now};
    }
    void resetTrace() { used = 0U; }
    opp_view::Port port();
    static std::uint32_t clock(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.clock_calls;
        if (f.clock_calls == f.fault_at_clock) f.now += f.fault_delta;
        f.record(CLOCK); const auto observed = f.now; f.now += f.clock_cost;
        return observed;
    }
    static opp_sensors::InitResult beginOpp(void* context) {
        auto& f = *static_cast<Fake*>(context); f.record(OPP_BEGIN);
        ++f.opp_begins; f.now += f.setup_cost; return f.initial;
    }
    static opp_sensors::Snapshot readOpp(void* context) {
        auto& f = *static_cast<Fake*>(context); f.record(OPP_READ); ++f.reads;
        if (f.automatic_times) f.value.started_us = f.now;
        f.now += f.read_cost;
        if (f.automatic_times) f.value.completed_us = f.now;
        if (f.fault_delay_after_read) f.fault_at_clock = f.clock_calls + f.fault_delay_after_read;
        return f.value;
    }
    static MatrixStatus beginMatrix(void* context, ui::MatrixGrant grant) {
        auto& f = *static_cast<Fake*>(context); f.record(MATRIX_BEGIN);
        ++f.matrix_begins; f.grant = grant; f.now += f.matrix_setup_cost;
        return f.begin_status;
    }
    static MatrixStatus submit(void* context, std::uint32_t time, const ui::Frame& frame) {
        auto& f = *static_cast<Fake*>(context); f.record(MATRIX_SUBMIT);
        ++f.submits; f.sent_time = time; f.sent = frame; f.now += f.submit_cost;
        if (f.fault_delay_after_submit) f.fault_at_clock = f.clock_calls + f.fault_delay_after_submit;
        return f.submit_status;
    }
};
opp_view::Port Fake::port() { return {this, clock, beginOpp, readOpp, beginMatrix, submit}; }

opp_view::Grants grants(bool opponents = true, bool matrix = true) {
    return {opponents, matrix, {true, true}};
}
bool begin(Runner& runner, const opp_view::Grants& selected = grants()) {
    allocations::active = true; const bool result = runner.begin(selected);
    allocations::active = false; CHECK(allocations::calls == 0U); return result;
}
bool poll(Runner& runner, Fake& fake) {
    fake.resetTrace(); allocations::active = true; const bool result = runner.poll();
    allocations::active = false; CHECK(allocations::calls == 0U); return result;
}
[[maybe_unused]] void due(Runner& runner, Fake& fake) { fake.now = runner.report().next_release_us; }
[[maybe_unused]] void snapshotEqual(const opp_sensors::Snapshot& a, const opp_sensors::Snapshot& b) {
    CHECK(a.valid == b.valid); CHECK(a.raw_mask == b.raw_mask); CHECK(a.valid_mask == b.valid_mask);
    CHECK(a.started_us == b.started_us); CHECK(a.completed_us == b.completed_us);
    for (unsigned i = 0U; i < 7U; ++i) CHECK(a.status[i] == b.status[i]);
}
[[maybe_unused]] void pixels(const ui::Frame& frame, bool available, unsigned mask, bool error) {
    for (unsigned row = 0U; row < 8U; ++row) {
        for (unsigned col = 0U; col < 13U; ++col) {
            unsigned expected = 0U;
            if (row == 0U && error) expected = 7U;
            if ((row == 2U || row == 3U) && col % 2U == 0U)
                expected = available ? (((mask >> (col / 2U)) & 1U) ? 7U : 0U) : 3U;
            CHECK(frame.pixels[row * 13U + col] == expected);
        }
    }
}
void faultPassive(Runner& runner, Fake& fake, Fault expected) {
    const auto before = runner.report(); const auto calls = fake.clock_calls;
    const auto reads = fake.reads, submits = fake.submits;
    CHECK(before.phase == Phase::FAULT); CHECK(before.fault == expected);
    CHECK_FALSE(before.fresh); CHECK_FALSE(before.current_available); CHECK(before.detection_mask == 0U);
    for (unsigned i = 0U; i < 3U; ++i) CHECK_FALSE(poll(runner, fake));
    CHECK(fake.clock_calls == calls); CHECK(fake.reads == reads); CHECK(fake.submits == submits);
    CHECK_FALSE(begin(runner)); CHECK(runner.report().fault == expected);
    CHECK(runner.report().completed_polls == before.completed_polls);
}

#ifdef TEST_BAD_CONFIG
TEST_CASE("D107 config rejects enabled work before any callback and disabled remains silent") {
    Fake f; Runner runner(f.port()); CHECK_FALSE(begin(runner));
    CHECK(f.clock_calls == 0U); CHECK(f.opp_begins == 0U); CHECK(f.matrix_begins == 0U);
    faultPassive(runner, f, Fault::CONFIG);
    Runner disabled(f.port()); REQUIRE(begin(disabled, {}));
    CHECK(disabled.report().phase == Phase::DISABLED); CHECK_FALSE(poll(disabled, f));
    CHECK(f.clock_calls == 0U);
}
#else
TEST_CASE("D107 construction prebegin and all false grants are completely passive") {
    static_assert(!std::is_copy_constructible<Runner>::value);
    static_assert(!std::is_copy_assignable<Runner>::value);
    Fake f; Runner runner(f.port()); CHECK(f.clock_calls == 0U);
    CHECK(runner.report().phase == Phase::NOT_STARTED); CHECK_FALSE(poll(runner, f));
    REQUIRE(begin(runner, {})); CHECK(runner.report().phase == Phase::DISABLED);
    CHECK(runner.report().fault == Fault::NONE); CHECK_FALSE(begin(runner));
    for (unsigned i = 0U; i < 5U; ++i) CHECK_FALSE(poll(runner, f));
    CHECK(f.clock_calls == 0U); CHECK(f.opp_begins == 0U); CHECK(f.matrix_begins == 0U);
    CHECK(f.reads == 0U); CHECK(f.submits == 0U);
    Runner empty({}); REQUIRE(begin(empty, {})); CHECK_FALSE(empty.poll());
    Runner ignored(f.port()); REQUIRE(begin(ignored, grants(false, false)));
    CHECK(ignored.report().phase == Phase::DISABLED); CHECK(f.clock_calls == 0U);
}

TEST_CASE("D107 grant truth setup brackets matrix grant and copied ports") {
    for (unsigned bits = 1U; bits < 4U; ++bits) {
        Fake f; auto port = f.port(); Runner runner(port); port = {};
        const auto selected = grants((bits & 1U) != 0U, (bits & 2U) != 0U);
        REQUIRE(begin(runner, selected)); REQUIRE(f.used == (bits == 3U ? 6U : 3U));
        CHECK(f.trace[0].event == CLOCK); CHECK(f.trace[2].event == CLOCK);
        CHECK(f.trace[1].event == (selected.opponents ? OPP_BEGIN : MATRIX_BEGIN));
        if (bits == 3U) {
            CHECK(f.trace[3].event == CLOCK); CHECK(f.trace[4].event == MATRIX_BEGIN);
            CHECK(f.trace[5].event == CLOCK);
        }
        CHECK(runner.report().next_release_us == f.trace[f.used - 1U].time);
        CHECK(f.opp_begins == static_cast<unsigned>(selected.opponents));
        CHECK(f.matrix_begins == static_cast<unsigned>(selected.matrix));
        const auto calls = f.clock_calls; CHECK_FALSE(begin(runner, {})); CHECK(f.clock_calls == calls);
        REQUIRE(poll(runner, f)); CHECK(f.reads == static_cast<unsigned>(selected.opponents));
        CHECK(f.submits == static_cast<unsigned>(selected.matrix));
        CHECK(runner.report().current_available == selected.opponents);
        CHECK_FALSE(runner.report().sensor_error);
    }
    for (unsigned bits = 0U; bits < 4U; ++bits) {
        Fake f; Runner runner(f.port()); auto selected = grants(false, true);
        selected.matrix_grant = {(bits & 1U) != 0U, (bits & 2U) != 0U};
        REQUIRE(begin(runner, selected)); CHECK(f.grant.normal_startup == selected.matrix_grant.normal_startup);
        CHECK(f.grant.exclusive_boot_owner == selected.matrix_grant.exclusive_boot_owner);
    }
}

TEST_CASE("D107 missing required callbacks fail before any setup IO") {
    for (unsigned missing = 0U; missing < 5U; ++missing) {
        Fake f; auto p = f.port();
        if (missing == 0U) p.clockUs = nullptr;
        if (missing == 1U) p.beginOpponents = nullptr;
        if (missing == 2U) p.readOpponents = nullptr;
        if (missing == 3U) p.beginMatrix = nullptr;
        if (missing == 4U) p.submitMatrix = nullptr;
        Runner runner(p); CHECK_FALSE(begin(runner));
        CHECK(f.clock_calls == 0U); CHECK(f.opp_begins == 0U); CHECK(f.matrix_begins == 0U);
        faultPassive(runner, f, Fault::PORT);
    }
    Fake f; auto p = f.port(); p.beginOpponents = nullptr; p.readOpponents = nullptr;
    Runner matrix(p); REQUIRE(begin(matrix, grants(false, true))); REQUIRE(poll(matrix, f));
    p = f.port(); p.beginMatrix = nullptr; p.submitMatrix = nullptr;
    Runner sensors(p); REQUIRE(begin(sensors, grants(true, false))); REQUIRE(poll(sensors, f));
}

TEST_CASE("D107 all 128 masks have literal full overwrite and polarity exactly once") {
    Fake f; Runner runner(f.port()); REQUIRE(begin(runner));
    for (unsigned raw = 0U; raw < 128U; ++raw) {
        f.levels(raw); due(runner, f); REQUIRE(poll(runner, f)); const auto& r = runner.report();
        const auto expected = (raw ^ config::OPP_ACTIVE_LOW_MASK) & 0x7fU;
        CHECK(r.current_available); CHECK(r.fresh); CHECK(r.detection_mask == expected);
        CHECK(r.valid_reads == raw + 1U); CHECK(r.read_attempts == raw + 1U);
        CHECK(r.invalid_reads == 0U); CHECK_FALSE(r.sensor_error); snapshotEqual(r.snapshot, f.value);
        pixels(r.frame, true, expected, false);
    }
}

TEST_CASE("D107 every setup status and malformed setup stays unknown without read retry") {
    const std::int32_t errors[] = {-2147483647 - 1, -19, -1, 1, 2147483647};
    for (unsigned index = 0U; index < 7U; ++index) for (auto error : errors) {
        Fake f; f.initial.status[index] = error; Runner runner(f.port()); REQUIRE(begin(runner));
        CHECK(runner.report().setup.status[index] == error); REQUIRE(poll(runner, f));
        CHECK(f.reads == 0U); CHECK(f.submits == 1U); CHECK(runner.report().sensor_error);
        pixels(runner.report().frame, false, 0U, true);
        f.initial.status[index] = 0; due(runner, f); REQUIRE(poll(runner, f)); CHECK(f.reads == 0U);
    }
    for (unsigned kind = 0U; kind < 3U; ++kind) {
        Fake f; if (kind == 0U) f.initial.ready = false;
        if (kind == 1U) f.initial.configured_mask = 0x3fU;
        if (kind == 2U) f.initial.configured_mask = 0xffU;
        Runner runner(f.port()); REQUIRE(begin(runner)); REQUIRE(poll(runner, f));
        CHECK(f.reads == 0U); CHECK(runner.report().sensor_error);
        CHECK(runner.report().setup.ready == f.initial.ready);
        CHECK(runner.report().setup.configured_mask == f.initial.configured_mask);
    }
}

TEST_CASE("D107 every bad channel preserves first evidence and permits real recovery") {
    const std::int32_t errors[] = {-2147483647 - 1, -19, -1, 2, 7, 2147483647};
    for (unsigned index = 0U; index < 7U; ++index) for (auto error : errors) {
        Fake f; Runner runner(f.port()); REQUIRE(begin(runner)); REQUIRE(poll(runner, f));
        f.value.status[index] = error; due(runner, f); REQUIRE(poll(runner, f));
        const auto first = f.value; const auto& bad = runner.report();
        CHECK_FALSE(bad.current_available); CHECK(bad.detection_mask == 0U);
        CHECK(bad.invalid_reads == 1U); CHECK(bad.first_read_error_saved); CHECK(bad.sensor_error);
        snapshotEqual(bad.snapshot, first); snapshotEqual(bad.first_read_error, first);
        pixels(bad.frame, false, 0U, true);
        f.value.valid = false; due(runner, f); REQUIRE(poll(runner, f));
        CHECK(runner.report().invalid_reads == 2U); snapshotEqual(runner.report().first_read_error, first);
        f.levels(0x55U); due(runner, f); REQUIRE(poll(runner, f));
        CHECK(runner.report().current_available); CHECK(runner.report().sensor_error);
        CHECK(runner.report().valid_reads == 2U); CHECK(runner.report().read_attempts == 4U);
        pixels(runner.report().frame, true, (0x55U ^ config::OPP_ACTIVE_LOW_MASK) & 0x7fU, true);
    }
}

TEST_CASE("D107 malformed flags masks and status bit mismatches never present live bits") {
    for (unsigned kind = 0U; kind < 12U; ++kind) {
        Fake f; Runner runner(f.port()); REQUIRE(begin(runner));
        if (kind == 0U) f.value.valid = false;
        if (kind == 1U) f.value.valid_mask = 0U;
        if (kind == 2U) f.value.valid_mask = 0x3fU;
        if (kind == 3U) f.value.valid_mask = 0xffU;
        if (kind == 4U) f.value.raw_mask = 0x80U;
        if (kind >= 5U) f.value.status[kind - 5U] = 1;
        REQUIRE(poll(runner, f)); CHECK_FALSE(runner.report().current_available);
        CHECK(runner.report().invalid_reads == 1U); CHECK(runner.report().valid_reads == 0U);
        CHECK(runner.report().last_read_us == 0U); CHECK(runner.report().maximum_read_us == 0U);
        snapshotEqual(runner.report().snapshot, f.value); pixels(runner.report().frame, false, 0U, true);
    }
}

TEST_CASE("D107 source timestamps must fit the current actual read bracket") {
    for (unsigned kind = 0U; kind < 6U; ++kind) {
        Fake f; Runner runner(f.port()); REQUIRE(begin(runner, grants(true, false)));
        f.automatic_times = false; const auto start = f.now;
        f.value.started_us = start; f.value.completed_us = start + f.read_cost;
        if (kind == 0U) f.value.started_us = start - 1U;
        if (kind == 1U) f.value.completed_us = start + f.read_cost + 1U;
        if (kind == 2U) { f.value.started_us = start + 10U; f.value.completed_us = start + 9U; }
        if (kind == 3U) f.value.completed_us = start + HALF;
        if (kind == 4U) { f.value.started_us = start - 2U; f.value.completed_us = start - 1U; }
        if (kind == 5U) f.value.completed_us = f.value.started_us;
        REQUIRE(poll(runner, f)); CHECK(runner.report().current_available == (kind == 5U));
        CHECK(runner.report().invalid_reads == (kind == 5U ? 0U : 1U));
        snapshotEqual(runner.report().snapshot, f.value);
    }
}

TEST_CASE("D107 early polls are single clock observations and freeze does not reread") {
    Fake f; Runner runner(f.port()); REQUIRE(begin(runner)); REQUIRE(poll(runner, f));
    const auto completed = runner.report().completed_polls; const auto reads = f.reads;
    const auto submits = f.submits; const auto saved = runner.report().snapshot;
    for (unsigned i = 0U; i < 100U; ++i) {
        const auto calls = f.clock_calls; CHECK_FALSE(poll(runner, f));
        CHECK(f.clock_calls == calls + 1U); REQUIRE(f.used == 1U); CHECK(f.trace[0].event == CLOCK);
        CHECK_FALSE(runner.report().fresh); CHECK(runner.report().completed_polls == completed);
        CHECK(f.reads == reads); CHECK(f.submits == submits); snapshotEqual(runner.report().snapshot, saved);
    }
    f.now = runner.report().next_release_us - 1U; CHECK_FALSE(poll(runner, f));
    ++f.now; REQUIRE(poll(runner, f)); CHECK(f.reads == reads + 1U);
}

TEST_CASE("D107 latest released slot and strict completion skips retain original grid") {
    for (unsigned cost : {0U, 999U, 1000U, 1001U, 2999U, 3000U, 3001U}) {
        Fake f; f.read_cost = cost; Runner runner(f.port()); REQUIRE(begin(runner, grants(true, false)));
        const auto anchor = runner.report().next_release_us;
        f.now = anchor + 2500U; REQUIRE(poll(runner, f));
        const auto c_offset = 2500U + cost;
        const auto next_slot = c_offset <= 3000U ? 3U : (c_offset + 999U) / 1000U;
        CHECK(runner.report().next_release_us == anchor + next_slot * 1000U);
        CHECK(runner.report().missed_releases == next_slot - 1U);
        CHECK(f.reads == 1U); CHECK(runner.report().completed_polls == 1U);
        CHECK(runner.report().last_poll_us == cost);
    }
    Fake f; f.read_cost = 1000U; Runner runner(f.port()); REQUIRE(begin(runner, grants(true, false)));
    const auto anchor = runner.report().next_release_us; REQUIRE(poll(runner, f));
    CHECK(runner.report().next_release_us == anchor + 1000U); CHECK(runner.report().missed_releases == 0U);
    REQUIRE(poll(runner, f)); CHECK(f.reads == 2U); CHECK(runner.report().missed_releases == 0U);
}

TEST_CASE("D107 read and complete poll durations include actual callback costs") {
    Fake f; f.clock_cost = 1U; f.read_cost = 37U; f.submit_cost = 127U;
    Runner runner(f.port()); REQUIRE(begin(runner)); REQUIRE(poll(runner, f));
    REQUIRE(f.used >= 7U); const auto s = f.trace[0].time; const auto c = f.trace[f.used - 1U].time;
    CHECK(f.trace[0].event == CLOCK); CHECK(f.trace[f.used - 1U].event == CLOCK);
    CHECK(runner.report().last_read_us == 37U); CHECK(runner.report().maximum_read_us == 37U);
    CHECK(runner.report().last_poll_us == c - s); CHECK(c - s >= 164U);
    CHECK(runner.report().maximum_poll_us == c - s);
    for (std::size_t i = 0U; i < f.used; ++i) if (f.trace[i].event == MATRIX_SUBMIT) {
        REQUIRE(i > 0U); CHECK(f.trace[i - 1U].event == CLOCK); CHECK(f.sent_time == f.trace[i - 1U].time);
    }
    f.read_cost = 4U; due(runner, f); REQUIRE(poll(runner, f));
    CHECK(runner.report().last_read_us == 4U); CHECK(runner.report().maximum_read_us == 37U);
    CHECK(runner.report().maximum_poll_us == c - s);
}

TEST_CASE("D107 matrix cadence remembers throttled attempt and never catches up") {
    Fake f; f.read_cost = 0U; f.submit_cost = 0U; Runner runner(f.port()); REQUIRE(begin(runner));
    const auto anchor = f.now; f.submit_status = MatrixStatus::THROTTLED;
    REQUIRE(poll(runner, f)); CHECK(f.submits == 1U); CHECK(runner.report().throttles == 1U);
    f.now = anchor + 39000U; REQUIRE(poll(runner, f)); CHECK(f.submits == 1U);
    f.now = anchor + 40000U; REQUIRE(poll(runner, f)); CHECK(f.submits == 2U);
    CHECK(runner.report().throttles == 2U); CHECK(runner.report().submissions == 0U);
    f.submit_status = MatrixStatus::SUBMITTED_UNCONFIRMED;
    f.now = anchor + 79000U; REQUIRE(poll(runner, f)); CHECK(f.submits == 2U);
    f.now = anchor + 80000U; REQUIRE(poll(runner, f)); CHECK(f.submits == 3U);
    f.now = anchor + 400000U; REQUIRE(poll(runner, f)); CHECK(f.submits == 4U);
    CHECK(runner.report().submissions == 2U); CHECK(runner.report().display_attempts == 4U);
}

TEST_CASE("D107 all nonaccepted matrix setup statuses terminate once") {
    for (unsigned status = 0U; status <= 10U; ++status) {
        if (status == static_cast<unsigned>(MatrixStatus::INIT_UNCONFIRMED)) continue;
        Fake f; f.begin_status = static_cast<MatrixStatus>(status); Runner runner(f.port());
        CHECK_FALSE(begin(runner)); CHECK(runner.report().matrix_setup == f.begin_status);
        CHECK(f.matrix_begins == 1U); CHECK(f.reads == 0U); CHECK(f.submits == 0U);
        faultPassive(runner, f, Fault::MATRIX);
    }
}

TEST_CASE("D107 matrix submit faults retain actual status and completed duration") {
    for (unsigned status = 0U; status <= 10U; ++status) {
        if (status == static_cast<unsigned>(MatrixStatus::SUBMITTED_UNCONFIRMED) ||
            status == static_cast<unsigned>(MatrixStatus::THROTTLED)) continue;
        Fake f; f.submit_cost = 1700U; f.submit_status = static_cast<MatrixStatus>(status);
        Runner runner(f.port()); REQUIRE(begin(runner)); CHECK_FALSE(poll(runner, f));
        CHECK(runner.report().matrix_status == f.submit_status); CHECK(runner.report().display_attempts == 1U);
        CHECK(runner.report().completed_polls == 1U); CHECK(runner.report().last_poll_us == 1720U);
        CHECK(runner.report().maximum_poll_us == 1720U); CHECK(runner.report().valid_reads == 1U);
        faultPassive(runner, f, Fault::MATRIX);
    }
}

TEST_CASE("D107 backwards and half range clocks reject setup admission and pre read") {
    for (auto delta : {0xffffffffU, HALF}) for (unsigned where = 0U; where < 3U; ++where) {
        Fake f; f.setup_cost = 0U; f.matrix_setup_cost = 0U; f.fault_delta = delta;
        Runner runner(f.port());
        if (where == 0U) { f.fault_at_clock = 2U; CHECK_FALSE(begin(runner)); CHECK(f.matrix_begins == 0U); }
        else {
            REQUIRE(begin(runner)); f.fault_at_clock = f.clock_calls + (where == 1U ? 1U : 2U);
            CHECK_FALSE(poll(runner, f)); CHECK(f.reads == 0U); CHECK(runner.report().read_attempts == 0U);
        }
        CHECK(runner.report().completed_polls == 0U); faultPassive(runner, f, Fault::CLOCK);
    }
}

TEST_CASE("D107 post read clock failure saves attempted evidence without fake C") {
    Fake f; f.read_cost = 0U; Runner runner(f.port()); REQUIRE(begin(runner));
    f.fault_delay_after_read = 1U; CHECK_FALSE(poll(runner, f)); const auto& r = runner.report();
    CHECK(r.read_attempts == 1U); CHECK(r.invalid_reads == 1U); CHECK(r.valid_reads == 0U);
    CHECK(r.sensor_error); CHECK(r.first_read_error_saved); snapshotEqual(r.first_read_error, f.value);
    CHECK(r.completed_polls == 0U); CHECK(r.last_poll_us == 0U); CHECK(r.last_read_us == 0U);
    CHECK(f.submits == 0U); faultPassive(runner, f, Fault::CLOCK);
}

TEST_CASE("D107 invalid slow read preserves prior qualified duration metrics") {
    Fake f; Runner runner(f.port()); REQUIRE(begin(runner, grants(true, false)));
    REQUIRE(poll(runner, f)); CHECK(runner.report().last_read_us == 20U);
    f.value.valid = false; f.read_cost = 80U; due(runner, f); REQUIRE(poll(runner, f));
    CHECK(runner.report().last_read_us == 20U); CHECK(runner.report().maximum_read_us == 20U);
    CHECK(runner.report().last_poll_us == 80U); CHECK(runner.report().maximum_poll_us == 80U);
}

TEST_CASE("D107 individually forward clocks cannot conceal half range aggregate poll") {
    Fake f; f.read_cost = 0x40000000U; f.submit_cost = 0x40000000U;
    Runner runner(f.port()); REQUIRE(begin(runner)); CHECK_FALSE(poll(runner, f));
    CHECK(runner.report().completed_polls == 0U); CHECK(runner.report().last_poll_us == 0U);
    faultPassive(runner, f, Fault::CLOCK);
}

TEST_CASE("D107 individually forward setup clocks cannot conceal half range aggregate") {
    Fake f; f.setup_cost = 0x40000000U; f.matrix_setup_cost = 0x40000000U;
    Runner runner(f.port()); CHECK_FALSE(begin(runner));
    CHECK(runner.report().completed_polls == 0U); CHECK(runner.report().last_poll_us == 0U);
    faultPassive(runner, f, Fault::CLOCK);
}

TEST_CASE("D107 matrix attempt elapsed half range rejects before any further submission") {
    for (auto elapsed : {HALF - 1U, HALF, HALF + 1U}) {
        Fake f; f.matrix_setup_cost = 0U; f.submit_cost = 0U;
        Runner runner(f.port()); REQUIRE(begin(runner, grants(false, true)));
        const auto anchor = f.now; REQUIRE(poll(runner, f)); CHECK(f.submits == 1U);
        f.now = anchor + 39999U; REQUIRE(poll(runner, f)); CHECK(f.submits == 1U);
        f.now = anchor + elapsed;
        if (elapsed < HALF) { REQUIRE(poll(runner, f)); CHECK(f.submits == 2U); }
        else { CHECK_FALSE(poll(runner, f)); CHECK(f.submits == 1U); faultPassive(runner, f, Fault::CLOCK); }
    }
}

TEST_CASE("D107 failed closing clock does not publish synthetic complete metrics") {
    Fake f; f.read_cost = 0U; f.submit_cost = 0U; Runner runner(f.port()); REQUIRE(begin(runner));
    REQUIRE(poll(runner, f)); const auto last = runner.report().last_poll_us;
    const auto complete = runner.report().completed_polls;
    f.now = f.sent_time + 40000U; f.fault_delay_after_submit = 2U;
    CHECK_FALSE(poll(runner, f)); CHECK(f.submits == 2U);
    CHECK(runner.report().completed_polls == complete); CHECK(runner.report().last_poll_us == last);
    faultPassive(runner, f, Fault::CLOCK);
}

TEST_CASE("D107 first matrix fault wins a later post submit clock fault") {
    Fake f; f.read_cost = 0U; f.submit_cost = 0U; Runner runner(f.port()); REQUIRE(begin(runner));
    f.submit_status = MatrixStatus::INVALID_FRAME; f.fault_delay_after_submit = 1U;
    CHECK_FALSE(poll(runner, f)); CHECK(runner.report().matrix_status == MatrixStatus::INVALID_FRAME);
    CHECK(runner.report().display_attempts == 1U); CHECK(runner.report().completed_polls == 0U);
    faultPassive(runner, f, Fault::MATRIX);
}

TEST_CASE("D107 natural wrap preserves source bracket grid and display cadence") {
    Fake f; f.now = 0xfffffff0U; f.setup_cost = 0U; f.matrix_setup_cost = 0U;
    f.read_cost = 32U; f.submit_cost = 0U; Runner runner(f.port()); REQUIRE(begin(runner));
    REQUIRE(poll(runner, f)); CHECK(runner.report().current_available);
    CHECK(runner.report().last_read_us == 32U); CHECK(runner.report().last_poll_us == 32U);
    CHECK(runner.report().snapshot.started_us == 0xfffffff0U); CHECK(runner.report().snapshot.completed_us == 16U);
    CHECK(runner.report().next_release_us == 984U); CHECK(runner.report().missed_releases == 0U);
    const auto first = f.sent_time; f.now = first + 40000U; REQUIRE(poll(runner, f));
    CHECK(f.submits == 2U); CHECK(runner.report().phase == Phase::RUNNING);
}

TEST_CASE("D107 missed counter saturates through actual forward polls without private state") {
    Fake f; f.matrix_setup_cost = 0U; f.submit_cost = 0U;
    Runner runner(f.port()); REQUIRE(begin(runner, grants(false, true))); REQUIRE(poll(runner, f));
    for (unsigned i = 0U; i < 2002U; ++i) { f.now += 0x7ffff000U; REQUIRE(poll(runner, f)); }
    CHECK(runner.report().missed_releases == std::numeric_limits<std::uint32_t>::max());
    CHECK(runner.report().counter_saturated); CHECK(runner.report().completed_polls == 2003U);
    CHECK(f.reads == 0U); CHECK(runner.report().phase == Phase::RUNNING);
}
#endif
} // namespace

#ifdef TEST_NATIVE_BINDING
namespace native_fixture {
unsigned clocks = 0U, begins = 0U, reads = 0U, matrix_begins = 0U, submits = 0U;
const void* opponent = nullptr; const void* matrix = nullptr;
opp_sensors::InitResult initial{false, 0x35U, {-1, 2, -3, 4, -5, 6, -7}};
opp_sensors::Snapshot value{false, 0x65U, 0x31U, {-1, 1, 0, 2, -3, 1, 0}, 123U, 456U};
ui::MatrixGrant grant; ui::Frame frame; std::uint32_t time = 0U;
void reset() { clocks = begins = reads = matrix_begins = submits = 0U; opponent = matrix = nullptr; }
unsigned calls() { return clocks + begins + reads + matrix_begins + submits; }
}
unsigned long micros() { ++native_fixture::clocks; return 0xfedcba98UL; }
namespace opp_sensors {
InitResult Sensors::begin() { ++native_fixture::begins; native_fixture::opponent = this; return native_fixture::initial; }
Snapshot Sensors::read() const { ++native_fixture::reads; native_fixture::opponent = this; return native_fixture::value; }
}
namespace ui {
MatrixStatus UnoQMatrix::begin(MatrixGrant grant) {
    ++native_fixture::matrix_begins; native_fixture::matrix = this; native_fixture::grant = grant;
    return MatrixStatus::DEVICE_UNAVAILABLE;
}
MatrixStatus UnoQMatrix::submit(std::uint32_t time, const Frame& frame) {
    ++native_fixture::submits; native_fixture::matrix = this; native_fixture::time = time; native_fixture::frame = frame;
    return MatrixStatus::INVALID_FRAME;
}
}
TEST_CASE("D107 Native port directly forwards exactly one stable owner and truthful fields") {
    using namespace native_fixture; CHECK(calls() == 0U); reset();
    static_assert(!std::is_copy_constructible<opp_view::Native>::value);
    static_assert(!std::is_copy_assignable<opp_view::Native>::value);
    opp_view::Native first, second; auto a = first.port(); auto b = second.port();
    CHECK(calls() == 0U); REQUIRE(a.context != nullptr); REQUIRE(b.context != nullptr);
    CHECK(a.context != b.context); CHECK(first.port().context == a.context);
    REQUIRE(a.clockUs); REQUIRE(a.beginOpponents); REQUIRE(a.readOpponents);
    REQUIRE(a.beginMatrix); REQUIRE(a.submitMatrix);
    CHECK(a.clockUs(a.context) == 0xfedcba98U); CHECK(clocks == 1U);
    const auto init = a.beginOpponents(a.context); const auto* first_opp = opponent;
    CHECK(begins == 1U); CHECK(init.ready == initial.ready); CHECK(init.configured_mask == initial.configured_mask);
    for (unsigned i = 0U; i < 7U; ++i) CHECK(init.status[i] == initial.status[i]);
    snapshotEqual(a.readOpponents(a.context), value); CHECK(reads == 1U); CHECK(opponent == first_opp);
    b.beginOpponents(b.context); CHECK(opponent != first_opp);
    CHECK(a.beginMatrix(a.context, {false, true}) == MatrixStatus::DEVICE_UNAVAILABLE);
    const auto* first_matrix = matrix; CHECK_FALSE(grant.normal_startup); CHECK(grant.exclusive_boot_owner);
    ui::Frame sent; for (unsigned i = 0U; i < 104U; ++i) sent.pixels[i] = static_cast<std::uint8_t>(i % 8U);
    CHECK(a.submitMatrix(a.context, 0xabcdefU, sent) == MatrixStatus::INVALID_FRAME);
    CHECK(matrix == first_matrix); CHECK(time == 0xabcdefU); CHECK(submits == 1U);
    CHECK(std::memcmp(sent.pixels, frame.pixels, sizeof sent.pixels) == 0);
    b.beginMatrix(b.context, {true, false}); CHECK(matrix != first_matrix);
    CHECK(grant.normal_startup); CHECK_FALSE(grant.exclusive_boot_owner);
}
TEST_CASE("D107 default sketch construction setup and loops are silent") {
    native_fixture::reset(); allocations::active = true;
    setup(); for (unsigned i = 0U; i < 100U; ++i) loop(); setup(); loop();
    allocations::active = false; CHECK(allocations::calls == 0U); CHECK(native_fixture::calls() == 0U);
}
#endif
