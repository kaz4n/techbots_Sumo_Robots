// Verifies D229 observes real Runtime completions once using the existing fixture.
// Keeps failed/idle/stale work out of the S..C population without physical claims.
// Focused host execution covers exact boundaries and actual completion-clock failure.
#include "doctest.h"
#include "fixtures/app_runtime_fixture.h"
#include <cstdio>
#include <type_traits>

using app::epoch_timing::Status;
using runtime_test::Rig;
static_assert(std::is_same_v<decltype(std::declval<const app::Runtime&>().epochTiming()),
                            const app::epoch_timing::Distribution&>);
namespace {
app::SetupGrants matrixGrants() {
    app::SetupGrants grants;
    grants.matrix_enabled = true;
    grants.matrix = {true, true};
    return grants;
}
ui::MatrixStatus reverseCompletion(void* context, std::uint32_t now, const ui::Frame& frame) {
    const auto result = runtime_test::Fake::matrix(context, now, frame);
    // First read admits matrix completion; the second is Transaction's actual C.
    runtime_test::Fake::self(context).clock_reversal_countdown = 2U;
    return result;
}
}

TEST_CASE("B14 P2.2 D229 actual Runtime counts every admitted completion exactly once") {
    Rig rig;
    CHECK(rig.owner.epochTiming().summary().status == Status::EMPTY);
    REQUIRE(rig.owner.begin(matrixGrants()));
    unsigned count = 0U, overflow = 0U, maximum = 0U;
    for (const unsigned duration : {0U, 1U, 799U, 800U, 1400U, 2U}) {
        rig.fake.matrix_work = duration;
        REQUIRE(rig.next());
        const auto& tick = rig.owner.transaction().report();
        const auto result = rig.owner.epochTiming().summary();
        ++count;
        if (duration >= 800U) ++overflow;
        if (duration > maximum) maximum = duration;
        CHECK(tick.finished);
        CHECK(tick.timing_valid);
        CHECK(tick.execution_us == duration);
        CHECK(result.samples == count);
        CHECK(result.samples == rig.owner.report().epochs);
        CHECK(result.overflow == overflow);
        CHECK(result.maximum_us == maximum);
        CHECK(result.maximum_us == rig.owner.report().maximum_execution_us);
        CHECK(result.last_completed_us == tick.completed_us);
        if (duration < 800U) CHECK(rig.owner.epochTiming().data().bins[duration] == 1U);
        // Same-time early calls clear freshness but cannot recount the stale transaction.
        const auto endpoint = result.last_completed_us;
        CHECK_FALSE(rig.owner.step());
        CHECK_FALSE(rig.owner.report().fresh);
        CHECK(rig.owner.epochTiming().summary().samples == count);
        CHECK(rig.owner.epochTiming().summary().last_completed_us == endpoint);
    }
    CHECK(rig.owner.epochTiming().summary().status == Status::RANGE_OVERFLOW);
    rig.owner.abort();
    CHECK_FALSE(rig.owner.step());
    CHECK_FALSE(rig.owner.begin(matrixGrants()));
    CHECK(rig.owner.epochTiming().summary().samples == count);
}

TEST_CASE("B14 P2.2 D229 real sensor acquisition is included in S to C distribution") {
    Rig rig;
    REQUIRE(rig.begin(false, true));
    for (unsigned count = 1U; count <= 4U; ++count) {
        REQUIRE(rig.next());
        const auto& tick = rig.owner.transaction().report();
        CHECK(rig.owner.epochTiming().summary().samples == count);
        CHECK(tick.execution_us > 0U);
        CHECK(rig.fake.opponents == count);
        CHECK(rig.fake.imu_begins == count);
        REQUIRE(tick.execution_us < config::TICK_DISTRIBUTION_LIMIT_US);
        CHECK(rig.owner.epochTiming().data().bins[tick.execution_us] > 0U);
    }
}

TEST_CASE("B14 P2.2 D229 failed service or decision never produces a duration") {
    for (unsigned failure = 0U; failure < 2U; ++failure) {
        CAPTURE(failure);
        Rig rig;
        REQUIRE(rig.begin());
        REQUIRE(rig.next());
        const auto previous = rig.owner.epochTiming().summary();
        if (failure == 0U) {
            rig.fake.qtr_never_release = true;
            rig.fake.line_work = 0U;
        } else rig.fake.reverse_decision_clock = true;
        // Existing fake frames are due only every 2000 us; make the failure real.
        rig.fake.now = rig.owner.report().next_release_us + 1000U;
        REQUIRE_FALSE(rig.owner.step());
        REQUIRE(rig.owner.report().phase == app::RuntimePhase::FAULT);
        CHECK(rig.owner.epochTiming().summary().samples == 1U);
        CHECK(rig.owner.epochTiming().summary().maximum_us == previous.maximum_us);
        CHECK(rig.owner.epochTiming().summary().last_completed_us == previous.last_completed_us);
        CHECK_FALSE(rig.owner.step());
        CHECK(rig.owner.epochTiming().summary().samples == 1U);
    }
}

TEST_CASE("B14 P2.2 D229 failed actual completion clock never enters histogram") {
    runtime_test::Fake fake;
    auto source = fake.sourcePort();
    source.submitMatrix = reverseCompletion;
    app::Runtime owner(fake.motorPort(), fake.adcPort(), source);
    REQUIRE(owner.begin(matrixGrants()));
    CHECK_FALSE(owner.step());
    CHECK(owner.transaction().report().decision_made);
    CHECK(owner.transaction().report().fault == app::Fault::CLOCK);
    CHECK_FALSE(owner.transaction().report().finished);
    CHECK(owner.epochTiming().summary().status == Status::EMPTY);
}

TEST_CASE("B14 P2.2 D229 actual completion preserves natural clock wrap anchors") {
    Rig rig;
    rig.fake.now = 0xFFFFFF00U;
    REQUIRE(rig.owner.begin(matrixGrants()));
    rig.fake.matrix_work = 400U;
    REQUIRE(rig.next());
    const auto report = rig.owner.epochTiming().summary();
    CHECK(report.first_started_us == 0xFFFFFF00U);
    CHECK(report.last_completed_us == 144U);
    CHECK(report.p99_us == 400U);
    CHECK(report.maximum_us == 400U);
    std::printf("D229 host Runtime size=%zu MATCH=%d MOTORS_ALLOWED=%d\n",
                sizeof(app::Runtime), MATCH, MOTORS_ALLOWED);
}
