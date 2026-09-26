// Checks D243's exact entry population and delayed publication boundaries.
// Keeps synthetic wall intervals distinct from physical timing qualification.
// The focused serial runner links actual Runtime fixtures under UBSan.
#include "doctest.h"
#include "app/outer_loop_timing.h"
#include "fixtures/app_runtime_fixture.h"
#include <array>
#include <cstdio>
#include <cstring>
#include <limits>
#include "native_app_runtime/allocation_probe.cc"

using app::outer_loop_timing::Observer;
using app::outer_loop_timing::Context;
using app::outer_loop_timing::Status;
namespace {
constexpr auto WINDOW = config::OUTER_LOOP_WINDOW_US;
Context running(std::uint32_t epochs = 0U) {
    return {app::RuntimePhase::RUNNING, app::RuntimeFault::NONE, epochs, false};
}
void idle(Observer& observer) { observer.result(running(), running(), false); }
void complete(Observer& observer) { observer.result(running(), running(1U), true); }
void poll(Observer& observer, runtime_test::Rig& rig) {
    observer.entry(rig.fake.now);
    const auto before = Context::read(rig.owner.report());
    const bool result = rig.owner.step();
    observer.result(before, Context::read(rig.owner.report()), result);
}
std::array<unsigned char, sizeof(Observer)> bytes(const Observer& observer) {
    std::array<unsigned char, sizeof(Observer)> result{};
    std::memcpy(result.data(), &observer, sizeof observer);
    return result;
}
}

TEST_CASE("P2.2 D243 exact half-open start cohort retains whole straddler and one drain") {
    Observer observer;
    observer.entry(100U); complete(observer);
    observer.entry(100U + WINDOW - 1U); complete(observer);
    observer.entry(100U + WINDOW + 10U);
    REQUIRE(observer.data().status == Status::DRAINING);
    CHECK(observer.summary().population_closed);
    CHECK(observer.data().all.data().samples == 2U);
    CHECK(observer.data().all.data().bins[11U] == 1U);
    CHECK(observer.data().all.data().overflow == 1U);
    CHECK(observer.data().last_population.returned);
    CHECK(observer.data().last_population_entry_us == 100U + WINDOW - 1U);
    CHECK(observer.data().overshoot_us == 10U);
    idle(observer);
    observer.entry(100U + WINDOW + 19U);
    CHECK(observer.data().status == Status::SEALED);
    CHECK(observer.data().drain_us == 9U);
    CHECK(observer.data().last_population_entry_us == 100U + WINDOW - 1U);
    CHECK(observer.data().all.data().last_completed_us == 100U + WINDOW + 10U);
    CHECK(observer.data().all.data().samples == 2U);
    const auto frozen = bytes(observer);
    observer.entry(0U); complete(observer); observer.entry(0x80000000U);
    CHECK(bytes(observer) == frozen);
}

TEST_CASE("P2.2 D243 exact endpoint and unfinished drain never claim another sample") {
    Observer observer;
    observer.entry(0U); idle(observer);
    observer.entry(WINDOW);
    CHECK(observer.data().all.data().samples == 1U);
    CHECK(observer.data().overshoot_us == 0U);
    CHECK(observer.data().status == Status::DRAINING);
    CHECK_FALSE(observer.terminal());
    CHECK_FALSE(observer.data().pending_context);
    idle(observer); // No next entry: the drain duration remains unknown.
    CHECK(observer.data().drain_end_us == 0U);
    CHECK(observer.data().status != Status::SEALED);
}

TEST_CASE("P2.2 D243 pending Runtime result needs next entry to become a duration") {
    Observer observer;
    observer.entry(42U); complete(observer);
    CHECK(observer.data().status == Status::SAMPLING);
    CHECK(observer.data().all.data().samples == 0U);
    CHECK(observer.data().pending_context);
    CHECK(observer.data().pending.returned);
    CHECK_FALSE(observer.summary().population_closed);
}

TEST_CASE("P2.2 D243 ordinary clock wrap and zero quantization preserve raw anchors") {
    Observer observer;
    observer.entry(0xfffffff0U); idle(observer);
    observer.entry(4U); complete(observer);
    observer.entry(4U);
    CHECK(observer.data().all.data().bins[20U] == 1U);
    CHECK(observer.data().all.data().bins[0U] == 1U);
    CHECK(observer.data().elapsed_us == 20U);
    CHECK(observer.data().equal_entries == 1U);
    CHECK(observer.data().completed.data().first_started_us == 4U);
}

TEST_CASE("P2.2 D243 ambiguous reversed and missing clocks preserve first bad prefix") {
    for (const auto next : {99U, 100U + 0x80000000U}) {
        Observer observer;
        observer.entry(100U); complete(observer); observer.entry(next);
        CHECK(observer.data().status == Status::CLOCK_ERROR);
        CHECK(observer.data().bad_entry_us == next);
        CHECK(observer.data().last_entry_us == 100U);
        CHECK(observer.data().pending.returned);
        CHECK(observer.data().all.data().samples == 0U);
        const auto frozen = bytes(observer);
        observer.entry(101U); idle(observer);
        CHECK(bytes(observer) == frozen);
    }
    Observer missing;
    missing.entry(0U); missing.entry(1U);
    CHECK(missing.data().status == Status::MISSING_CONTEXT);
}

TEST_CASE("P2.2 D243 stopped clock has bounded equality evidence not invented elapsed time") {
    Observer observer;
    observer.entry(9U);
    for (unsigned i = 0U; i < config::APP_CLOCK_STALL_MAX_POLLS; ++i) {
        idle(observer); observer.entry(9U);
    }
    CHECK(observer.data().status == Status::CLOCK_STALLED);
    CHECK(observer.data().equal_entries == config::APP_CLOCK_STALL_MAX_POLLS);
    CHECK(observer.data().all.data().samples == config::APP_CLOCK_STALL_MAX_POLLS - 1U);
    CHECK(observer.data().elapsed_us == 0U);
    CHECK(observer.data().bad_entry_us == 9U);
}

TEST_CASE("P2.2 D243 failed drain preserves already closed population") {
    Observer observer;
    observer.entry(0U); complete(observer); observer.entry(WINDOW); idle(observer);
    observer.entry(WINDOW - 1U);
    CHECK(observer.data().status == Status::CLOCK_ERROR);
    CHECK(observer.summary().population_closed);
    CHECK(observer.data().all.data().samples == 1U);
    CHECK(observer.data().drain_us == 0U);
}

TEST_CASE("P2.2 D243 completed-labelled percentile cannot be diluted by idle polls") {
    Observer observer;
    observer.entry(0U); complete(observer); observer.entry(800U);
    for (unsigned i = 1U; i <= 200U; ++i) { idle(observer); observer.entry(800U + i); }
    const auto summary = observer.summary();
    CHECK(summary.all.p99_us == 1U);
    CHECK(summary.all.maximum_us == 800U);
    CHECK(summary.completed.samples == 1U);
    CHECK(summary.completed.status == app::epoch_timing::Status::RANGE_OVERFLOW);
    CHECK(observer.data().idle.polls == 200U);
}

TEST_CASE("P2.2 D243 completion failure overlap and uncertain epochs stay explicit") {
    Observer observer;
    observer.entry(0U);
    const Context failure{app::RuntimePhase::FAULT, app::RuntimeFault::TRANSACTION, 1U, false};
    observer.result(running(), failure, false); observer.entry(7U);
    CHECK(observer.data().completed.data().samples == 1U);
    CHECK(observer.data().failed.polls == 1U);
    CHECK(observer.data().first_failure.after.fault == app::RuntimeFault::TRANSACTION);
    observer.result(failure, failure, false); observer.entry(9U);
    CHECK(observer.data().terminal.polls == 1U);
    const auto limit = std::numeric_limits<std::uint32_t>::max();
    observer.result(running(limit), running(limit), true); observer.entry(13U);
    CHECK(observer.data().completed.data().samples == 2U);
    CHECK(observer.data().uncertain.polls == 1U);
    CHECK_FALSE(observer.summary().classification_certain);
    observer.result(running(9U), running(8U), false); observer.entry(15U);
    CHECK(observer.data().uncertain.polls == 2U);
    CHECK(observer.data().first_uncertain.before.epochs == limit);
}

TEST_CASE("P2.2 D243 saturated retained population cannot become a five-minute pass") {
    Observer observer;
    observer.entry(0U); idle(observer);
    auto& seeded = const_cast<app::epoch_timing::Data&>(observer.data().all.data());
    seeded.samples = seeded.bins[0] = std::numeric_limits<std::uint32_t>::max();
    observer.entry(1U);
    CHECK(observer.data().status == Status::SATURATED);
    CHECK(observer.data().all.data().rejected == 1U);
    CHECK(observer.data().idle.polls == 0U);
    CHECK_FALSE(observer.summary().population_closed);
    const auto frozen = bytes(observer);
    observer.entry(WINDOW); complete(observer);
    CHECK(bytes(observer) == frozen);
}

TEST_CASE("P2.2 D243 actual Runtime completion idle failure and terminal wall intervals") {
    runtime_test::Rig rig;
    Observer observer;
    REQUIRE(rig.begin());
    poll(observer, rig);
    REQUIRE(rig.owner.report().fresh);
    const auto finish = rig.fake.now;
    rig.fake.now += 3U; poll(observer, rig); // Framework gap belongs to prior interval.
    CHECK(observer.data().completed.data().samples == 1U);
    CHECK(observer.data().all.data().maximum_us == finish + 3U - observer.data().anchor_us);
    REQUIRE_FALSE(rig.owner.report().fresh);
    rig.fake.now = rig.owner.report().next_release_us + 1000U;
    rig.fake.qtr_never_release = true; rig.fake.line_work = 0U;
    poll(observer, rig);
    REQUIRE(rig.owner.report().phase == app::RuntimePhase::FAULT);
    rig.fake.now += 3U; poll(observer, rig);
    CHECK(observer.data().failed.polls == 1U);
    CHECK(observer.data().idle.polls == 1U);
    rig.fake.now += 2U; poll(observer, rig);
    CHECK(observer.data().terminal.polls == 1U);
    CHECK(observer.data().first_failure.before.phase == app::RuntimePhase::RUNNING);
    CHECK(observer.data().first_failure.after.phase == app::RuntimePhase::FAULT);
    std::printf("D243 host Observer=%zu Data=%zu Summary=%zu Runtime=%zu\n",
        sizeof(Observer), sizeof(app::outer_loop_timing::Data),
        sizeof(app::outer_loop_timing::Summary), sizeof(app::Runtime));
}

TEST_CASE("P2.2 D243 actual Runtime and observer complete without heap operations") {
    allocations = deallocations = 0U;
    counting = true;
    runtime_test::Rig rig;
    Observer observer;
    bool good = rig.begin();
    for (unsigned i = 0U; i < 20U; ++i) {
        rig.fake.now = rig.owner.report().next_release_us;
        poll(observer, rig);
        good = good && rig.owner.report().fresh;
    }
    rig.fake.now = observer.data().anchor_us + WINDOW;
    poll(observer, rig);
    rig.fake.now += 3U; poll(observer, rig);
    const auto summary = observer.summary();
    counting = false;
    CHECK(good);
    CHECK(summary.status == Status::SEALED);
    CHECK(allocations == 0U);
    CHECK(deallocations == 0U);
}
