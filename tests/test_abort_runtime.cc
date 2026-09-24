// Observes D135 through actual Runtime acquisition, Transaction and recorder owners.
// Uses existing synthetic callback grants without claiming native or physical timing.
// Configured draft cases compare emitted read bounds with callback clocks and receipts.
#include "fixtures/p5_abort_fixture.h"
#include "fixtures/app_service_reset/fixture.h"

using namespace p5_abort;
namespace {
void runtimeZero(const service_reset_test::Rig& rig) {
    CHECK_FALSE(rig.fake.enabled); for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
#ifdef APP_TEST_CONFIGURED_BUTTONS
void go(service_reset_test::Rig& rig, Mode mode) {
    APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.robot().button_available && rig.robot().line_available);
    for (unsigned i = 0U; i < 6U && rig.robot().menu.selection.mode != mode; ++i) {
        APP_REQUIRE(rig.run(30U, service_reset_test::MODE)); APP_REQUIRE(rig.run(30U));
    }
    APP_REQUIRE(rig.robot().menu.selection.mode == mode);
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); rig.fake.button_raw = service_reset_test::NONE;
    bool released = false, went = false;
    for (unsigned i = 0U; i < 5150U; ++i) {
        APP_REQUIRE(rig.next()); released |= rig.robot().lifecycle.gate.start_release;
        if (rig.robot().lifecycle.gate.go) { went = true; break; }
        runtimeZero(rig);
    }
    APP_REQUIRE(released && went); APP_REQUIRE(rig.robot().outputs.ui_state == State::OPENER);
    CHECK(stored(rig.owner.transaction().recording(), HEADER) == 1U);
    CHECK(stored(rig.owner.transaction().recording(), QUALIFIED) == 0U);
}
std::uint32_t readStart(const service_reset_test::Rig& rig) {
    APP_REQUIRE(rig.fake.seen(runtime_test::Call::OPP) == 1U);
    for (unsigned i = 0U; i < rig.fake.count && i < rig.fake.trace.size(); ++i)
        if (rig.fake.trace[i].kind == runtime_test::Call::OPP) return rig.fake.trace[i].at;
    APP_REQUIRE(false); return 0U;
}
void noEventLoss(const recorder::AttemptRecorder& owner) {
    CHECK(owner.summary().upstream_event_rejected == 0U);
    CHECK(owner.summary().upstream_event_invalid == 0U);
    CHECK(owner.summary().event_semantic_rejected == 0U);
    CHECK(owner.summary().malformed_batches == 0U);
    CHECK(owner.events().rejectedCount() == 0U); CHECK_FALSE(owner.events().overflowed());
}
#endif
} // namespace

TEST_CASE("B0 B3 D135 Runtime empty grants remain inert with no invented timing attempt") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.owner.begin({}));
    APP_REQUIRE(rig.run(35U)); APP_REQUIRE(rig.run(30U, service_reset_test::START));
    APP_REQUIRE(rig.run(5150U)); runtimeZero(rig);
    CHECK(rig.robot().outputs.ui_state == State::BOOT);
    CHECK_FALSE(rig.robot().lifecycle.gate.start_release); CHECK_FALSE(rig.robot().lifecycle.gate.go);
    CHECK_FALSE(rig.owner.decisionInput().opponent_read.valid);
    CHECK(rig.fake.opponents == 0U); CHECK(rig.fake.buttons == 0U);
    CHECK(stored(rig.owner.transaction().recording(), HEADER) == 0U);
    CHECK(stored(rig.owner.transaction().recording(), APPLIED) == 0U);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B12 B15 D135 actual Runtime projects one complete source interval and stores matching Gate time") {
    for (auto mode : {Mode::DIRECT, Mode::WAIT}) {
        if (!core::modeAvailable(mode)) continue;
        service_reset_test::Rig rig; go(rig, mode);
        if (mode == Mode::WAIT) {
            CHECK(rig.robot().outputs.duty_l == 0.0F); CHECK(rig.robot().outputs.duty_r == 0.0F);
            for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
        }
        const unsigned mask = mode == Mode::DIRECT ? 2U : 8U;
        rig.fake.opponent_mask = static_cast<std::uint8_t>(mask ^ 0x78U); APP_REQUIRE(rig.next());
        rig.fake.count = 0U; rig.fake.opponent_work = 13U; const auto reads = rig.fake.opponents;
        APP_REQUIRE(rig.next()); const auto candidate = rig.owner.transaction().report();
        const auto start = readStart(rig); CHECK(rig.fake.opponents == reads + 1U);
        const auto input = rig.owner.decisionInput(); CHECK(input.opponent_read.valid);
        CHECK(input.opponent_read.started_us == start); CHECK(input.opponent_read.completed_us == start + 13U);
        suffix(candidate.robot, {READ_START, READ_END, QUALIFIED, HANDOVER});
        CHECK(event(candidate.robot, READ_START).t_us == start);
        CHECK(event(candidate.robot, READ_END).t_us == start + 13U);
        CHECK(event(candidate.robot, QUALIFIED).t_us == candidate.decision_us);
        CHECK(event(candidate.robot, QUALIFIED).value == cue(static_cast<unsigned>(mode),
            mode == Mode::DIRECT ? 0U : 4U, mode == Mode::DIRECT ? 1U : 2U, mask));
        CHECK(candidate.robot.outputs.ui_state == (mode == Mode::DIRECT ? State::TRACK : State::DEFEND_TURN));
        CHECK(candidate.applied.feedback.token == candidate.robot.token);
        CHECK(candidate.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
        APP_REQUIRE(candidate.timing_valid); const auto receipt = rig.owner.transaction().previous();
        CHECK(receipt.duration_valid); CHECK(receipt.completed_us == candidate.completed_us);
        APP_REQUIRE(rig.next()); CHECK(event(rig.robot(), APPLIED).t_us == receipt.applied_us);
        CHECK(rig.robot().events.entries[0].detail == APPLIED);
        const auto& recording = rig.owner.transaction().recording();
        CHECK(stored(recording, QUALIFIED) == 1U); CHECK(stored(recording, HANDOVER) == 1U);
        CHECK(stored(recording, APPLIED) == 1U); noEventLoss(recording);
        CHECK(recording.summary().skipped_frames == 0U); CHECK_FALSE(recording.incomplete());
        if (!MOTORS_ALLOWED) runtimeZero(rig);
    }
}

TEST_CASE("B2 B15 D135 actual Runtime rejects partial stale and contradictory opponent reads without retry") {
    for (unsigned scenario = 0U; scenario < 5U; ++scenario) {
        service_reset_test::Rig rig; go(rig, Mode::DIRECT);
        rig.fake.opponent_mask = 2U ^ 0x78U; APP_REQUIRE(rig.next());
        if (scenario < 3U) rig.fake.opponent_error = scenario + 1U;
        if (scenario == 3U) rig.fake.opponent_shift = 0U - 1000U;
        if (scenario == 4U) rig.fake.opponent_shift = 1000U;
        APP_REQUIRE(rig.next()); CHECK_FALSE(rig.owner.decisionInput().opponent_read.valid);
        terminal(rig.robot(), INVALID_SOURCE, 1U, rig.owner.transaction().report().decision_us);
        CHECK(rig.robot().outputs.ui_state == State::STOPPED); runtimeZero(rig);
        rig.fake.opponent_error = 0U; rig.fake.opponent_shift = 0U;
        for (unsigned i = 0U; i < 5U; ++i) { APP_REQUIRE(rig.next()); CHECK(count(rig.robot()) == 0U); }
        CHECK(stored(rig.owner.transaction().recording(), INVALID_SOURCE) == 1U);
        CHECK(stored(rig.owner.transaction().recording(), QUALIFIED) == 0U);
        CHECK(stored(rig.owner.transaction().recording(), APPLIED) == 0U); runtimeZero(rig);
    }
}
#endif
