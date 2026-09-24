// Probes D129 contract boundaries independently of the public test author.
// All stimuli and receipts are synthetic host observations from actual owners.
// Frozen before execution; no native board, physical timing or acceptance claim.
#include "private_fixture.h"
#include "fixtures/app_service_reset/fixture.h"

namespace {
void expected(const Rig& rig, Detail detail, unsigned m1_count) {
    CHECK(rig.count(detail) == (MOTORS_ALLOWED ? m1_count : 0U));
}
std::uint32_t timestamp(const Rig& rig, Detail detail) {
    for (const auto& event : rig.events)
        if (event.detail == static_cast<unsigned>(detail)) return event.t_us;
    APP_REQUIRE(false);
    return 0U;
}
}

TEST_CASE("D129 private valid prior brake receipt wins simultaneous current STOP edge and reassertion") {
    for (std::uint32_t base : {0U, std::uint32_t{0xFFFFFF00U - 5223000U}}) {
        Rig rig;
        const auto onset = rig.approach(base) + 60000U;
        rig.input.opp_raw_mask = 0x78U;
        rig.at(onset); rig.at(onset + 29999U);
        CHECK(rig.last.outputs.ui_state == core::State::ATTACK);
        rig.at(onset + 30000U);
        CHECK(rig.last.outputs.ui_state == core::State::SEARCH);
        CHECK(rig.last.outputs.duty_l == 0.0F);
        CHECK(rig.last.outputs.duty_r == 0.0F);
        expected(rig, Detail::LOSS_BRAKE_DECISION, 1U);
        expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
        rig.input.stop_requested = true;
        rig.input.opp_raw_mask = 2U ^ 0x78U;
        for (auto& line : rig.input.line_raw_us) line = 100U;
        rig.at(onset + 31000U);
        CHECK(rig.last.outputs.ui_state == core::State::STOPPED);
        expected(rig, Detail::LOSS_ZERO_APPLIED, 1U);
        expected(rig, Detail::INTERRUPTED_EDGE, 0U);
        expected(rig, Detail::INTERRUPTED_STOP_FAULT, 0U);
        CHECK(rig.events.size() == (MOTORS_ALLOWED ? 5U : 1U));
        if (MOTORS_ALLOWED) {
            CHECK(timestamp(rig, Detail::LOSS_READ_START) == onset - 80U);
            CHECK(timestamp(rig, Detail::LOSS_READ_END) == onset - 60U);
            CHECK(timestamp(rig, Detail::LOSS_BRAKE_DECISION) == onset + 30000U);
            CHECK(timestamp(rig, Detail::LOSS_ZERO_APPLIED) == onset + 30000U);
            CHECK(timestamp(rig, Detail::LOSS_ZERO_APPLIED) - timestamp(rig, Detail::LOSS_READ_START) == 30080U);
        }
    }
}

TEST_CASE("D129 private one unconfirmed raw reassertion closes without selecting a later favorable trial") {
    Rig rig;
    const auto onset = rig.approach() + 60000U;
    rig.input.opp_raw_mask = 0x78U; rig.at(onset);
    rig.input.opp_raw_mask = 4U ^ 0x78U; rig.at(onset + 1000U);
    CHECK(rig.last.opponent_mask == 2U);
    expected(rig, Detail::EXCLUDED_TRANSIENT, 1U);
    rig.input.opp_raw_mask = 0x78U; rig.at(onset + 2000U);
    rig.at(onset + 60000U); rig.at(onset + 61000U);
    expected(rig, Detail::LOSS_READ_START, 1U);
    expected(rig, Detail::LOSS_READ_END, 1U);
    expected(rig, Detail::LOSS_BRAKE_DECISION, 0U);
    expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
    expected(rig, Detail::EXCLUDED_TRANSIENT, 1U);
    CHECK(rig.events.size() == (MOTORS_ALLOWED ? 4U : 1U));
}

TEST_CASE("D129 private malformed source window before onset closes evidence without steering") {
    Rig rig;
    const auto time = rig.approach() + 51000U;
    const auto left = rig.last.outputs.duty_l;
    const auto right = rig.last.outputs.duty_r;
    rig.atWindow(time, time - 100U, time - 60U, time - 80U);
    expected(rig, Detail::INVALID_SOURCE_TIME, 1U);
    expected(rig, Detail::LOSS_READ_START, 0U);
    CHECK(rig.last.contract_faults == 0U);
    CHECK(rig.last.outputs.ui_state == core::State::ATTACK);
    CHECK(rig.last.outputs.duty_l == left);
    CHECK(rig.last.outputs.duty_r == right);
    rig.input.opp_raw_mask = 0x78U;
    rig.at(time + 1000U); rig.at(time + 31000U); rig.at(time + 32000U);
    expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
    CHECK(rig.events.size() == (MOTORS_ALLOWED ? 2U : 1U));
}

TEST_CASE("D129 private onset after permitted TRACK retains the first pair then excludes missing ATTACK receipt") {
    Rig rig;
    const auto time = rig.approach() + 60000U;
    rig.input.opp_raw_mask = 1U ^ 0x78U;
    rig.at(time); rig.at(time + 1000U); rig.at(time + 30000U);
    APP_REQUIRE(rig.last.outputs.ui_state == core::State::TRACK);
    APP_REQUIRE(rig.last.opponent_mask == 1U);
    rig.input.opp_raw_mask = 0x78U; rig.at(time + 31000U);
    expected(rig, Detail::LOSS_READ_START, 1U);
    expected(rig, Detail::LOSS_READ_END, 1U);
    expected(rig, Detail::EXCLUDED_NO_APPROACH, 1U);
    expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
    if (MOTORS_ALLOWED) {
        CHECK(rig.events[1].detail == static_cast<unsigned>(Detail::LOSS_READ_START));
        CHECK(rig.events[2].detail == static_cast<unsigned>(Detail::LOSS_READ_END));
        CHECK(rig.events[3].detail == static_cast<unsigned>(Detail::EXCLUDED_NO_APPROACH));
    }
}

TEST_CASE("D129 private decision needs a later distinct receipt and duplicate cannot manufacture closure") {
    Rig rig;
    const auto onset = rig.approach() + 60000U;
    rig.input.opp_raw_mask = 0x78U; rig.at(onset); rig.at(onset + 30000U);
    expected(rig, Detail::LOSS_BRAKE_DECISION, 1U);
    expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
    const auto count = rig.events.size();
    rig.input.stop_requested = true;
    rig.at(onset + 30000U);
    CHECK_FALSE(rig.last.fresh);
    CHECK(rig.last.events.count == 0U);
    CHECK(rig.events.size() == count);
    expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
}

TEST_CASE("D129 private candidate common-anchor half range is invalid even with a locally ordered source window") {
    Rig rig;
    const auto onset = rig.approach() + 60000U;
    rig.input.opp_raw_mask = 0x78U; rig.at(onset);
    const auto ambiguous = onset - 80U + 0x80000000U;
    rig.at(ambiguous);
    expected(rig, Detail::INVALID_SOURCE_TIME, 1U);
    expected(rig, Detail::LOSS_BRAKE_DECISION, 0U);
    expected(rig, Detail::LOSS_ZERO_APPLIED, 0U);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("D129 private actual Runtime copies only the complete current source interval") {
    for (unsigned failure = 0U; failure <= 4U; ++failure) {
        service_reset_test::Rig rig;
        APP_REQUIRE(rig.begin(true, true, false));
        APP_REQUIRE(rig.run(35U));
        rig.fake.opponent_work = 17U;
        rig.fake.opponent_error = failure;
        const auto first = rig.fake.count;
        APP_REQUIRE(rig.next());
        const auto& input = rig.owner.decisionInput();
        unsigned calls = 0U;
        std::uint32_t source_start = 0U;
        for (unsigned i = first; i < rig.fake.count; ++i) {
            APP_REQUIRE(i < rig.fake.trace.size());
            if (rig.fake.trace[i].kind == runtime_test::Call::OPP) {
                ++calls; source_start = rig.fake.trace[i].at;
            }
        }
        APP_REQUIRE(calls == 1U);
        CHECK(input.opponent_read.valid == (failure == 0U));
        CHECK(input.opponent_fresh == (failure == 0U));
        CHECK(input.opponent_read.started_us == (failure == 0U ? source_start : 0U));
        CHECK(input.opponent_read.completed_us == (failure == 0U ? source_start + 17U : 0U));
    }
}
#endif

TEST_CASE("D129 private bounded batch preserves first26 and separates metadata rejection") {
    static_assert(logframe::ROBOT_EVENT_CAPACITY == 26U);
    logframe::EventBatch batch;
    for (unsigned i = 0U; i < 26U; ++i)
        APP_REQUIRE(logframe::appendEvent(batch, {i, core::Event::TIMING, 1U, 1U}));
    CHECK_FALSE(logframe::appendEvent(batch, {27U, core::Event::TIMING, 1U, 1U}));
    CHECK(batch.count == 26U); CHECK(batch.rejected == 1U); CHECK(batch.overflowed);
    CHECK_FALSE(logframe::appendEvent(batch, {28U, core::Event::TIMING, 13U, 1U}));
    CHECK(batch.invalid_metadata == 1U); CHECK(batch.rejected == 1U);
    for (unsigned i = 0U; i < 26U; ++i) CHECK(batch.entries[i].t_us == i);
}
