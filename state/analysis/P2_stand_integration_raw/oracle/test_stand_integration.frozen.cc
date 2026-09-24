// Tests D120 bench identity, real application receipts and additive cancellation.
// Derives expectations from the public integration contract, never implementation.
// Dedicated profile1 M0/M1 targets execute the actual Transaction and MotorGate.
#include "fixtures/app_transaction_fixture.h"
#include "fixtures/app_service_reset/fixture.h"
#include "core/stand_sequence.h"
#include <cmath>

namespace {
using stand_sequence::Phase;
using stand_sequence::Reason;
constexpr std::uint32_t SEGMENT_US = 500000U;
struct Row { Phase phase; float l; float r; };
constexpr Row ROWS[] = {{Phase::DRIVE,.25F,0}, {Phase::BRAKE,0,0}, {Phase::COAST,0,0},
    {Phase::DRIVE,-.25F,0}, {Phase::BRAKE,0,0}, {Phase::COAST,0,0},
    {Phase::DRIVE,0,.25F}, {Phase::BRAKE,0,0}, {Phase::COAST,0,0},
    {Phase::DRIVE,0,-.25F}, {Phase::BRAKE,0,0}, {Phase::COAST,0,0}};

void same(const stand_sequence::Report& a, const stand_sequence::Report& b) {
    CHECK(a.phase == b.phase); CHECK(a.reason == b.reason); CHECK(a.segment == b.segment);
    CHECK(a.duty_l == b.duty_l); CHECK(a.duty_r == b.duty_r);
    CHECK(a.fresh == b.fresh); CHECK(a.phase_changed == b.phase_changed);
}
void noCombat(const fsm::RobotResult& result) {
    CHECK(result.outputs.ui_state == core::State::OPENER);
    CHECK_FALSE(result.contact); CHECK_FALSE(result.all_in);
    for (unsigned i = 0U; i < result.events.count; ++i) {
        CHECK(result.events.entries[i].type != core::Event::CONTACT);
        CHECK(result.events.entries[i].type != core::Event::STALL);
        CHECK(result.events.entries[i].type != core::Event::REFLANK_PHASE);
    }
}
void actualRow(app_test::Rig& rig, const app::TransactionReport& report, unsigned row) {
    APP_REQUIRE(row < 12U);
    const auto& result = report.robot; const auto& expected = ROWS[row];
    CHECK(result.stand.segment == row); CHECK(result.stand.phase == expected.phase);
    CHECK(result.stand.reason == Reason::NONE);
    CHECK(result.stand.duty_l == expected.l); CHECK(result.stand.duty_r == expected.r);
    CHECK_FALSE(result.stand_stopping); CHECK(result.contract_faults == 0U);
    noCombat(result);
    const bool enabled = expected.phase != Phase::COAST;
    CHECK(result.outputs.motors_enabled == enabled);
    CHECK(report.applied.consumed); CHECK(report.applied.feedback.applied_valid);
    CHECK(report.applied.feedback.token == result.token);
    CHECK(report.applied.feedback.motors_enabled == (enabled && MOTORS_ALLOWED != 0));
    CHECK(rig.port.enabled == (enabled && MOTORS_ALLOWED != 0));
    CHECK(std::isfinite(result.outputs.duty_l)); CHECK(std::isfinite(result.outputs.duty_r));
    CHECK(std::fabs(result.outputs.duty_l) <= .25F);
    CHECK(std::fabs(result.outputs.duty_r) <= .25F);
    if (expected.l == 0.0F) CHECK(result.outputs.duty_l == 0.0F);
    if (expected.r == 0.0F) CHECK(result.outputs.duty_r == 0.0F);
    CHECK(std::fabs(report.applied.feedback.duty_l) <= std::fabs(result.outputs.duty_l));
    CHECK(std::fabs(report.applied.feedback.duty_r) <= std::fabs(result.outputs.duty_r));
    if (!MOTORS_ALLOWED || expected.phase != Phase::DRIVE) {
        CHECK(report.applied.feedback.duty_l == 0.0F);
        CHECK(report.applied.feedback.duty_r == 0.0F);
        for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
    } else {
        const unsigned channel = row == 0U ? 0U : row == 3U ? 1U : row == 6U ? 2U : 3U;
        const std::uint32_t periods[] = {1000U, 997U, 251U, 65535U};
        CHECK(rig.port.pulses[channel] == periods[channel] / 4U);
        for (unsigned i = 0U; i < 4U; ++i) if (i != channel) CHECK(rig.port.pulses[i] == 0U);
    }
}
}

TEST_CASE("P2 B4 D120 immutable bench identity appends governor profile without renumbering") {
    CHECK(SUMOX_B4_STAND == 1); CHECK(MATCH == 0); CHECK(fsm::RobotResult::STAND_PROFILE);
    CHECK(static_cast<unsigned>(governor::Profile::SEARCH_FORWARD) == 0U);
    CHECK(static_cast<unsigned>(governor::Profile::ATTACK) == 3U);
    CHECK(static_cast<unsigned>(governor::Profile::EDGE_FORWARD) == 7U);
    CHECK(static_cast<unsigned>(governor::Profile::STAND) == 8U);
    const fsm::RobotResult initial;
    CHECK(initial.stand.phase == Phase::NOT_STARTED); CHECK_FALSE(initial.stand_stopping);
}

TEST_CASE("P2 B4 D120 all twelve real Gate phases respect low voltage cap and shared enable") {
    for (const float voltage : {9.0F, 11.1F}) {
        for (const auto base : {0U, 0xffb00000U}) {
            app_test::Rig rig; rig.source.vbat_v = voltage;
            const auto go = rig.go(base);
            for (unsigned row = 0U; row < 12U; ++row) {
                CAPTURE(row); CAPTURE(voltage); CAPTURE(base);
                const auto entered = go + row * SEGMENT_US;
                if (row != 0U) rig.tick(entered);
                actualRow(rig, rig.tick(entered + 25000U), row);
                actualRow(rig, rig.tick(entered + SEGMENT_US - 1U), row);
            }
            const auto complete = rig.tick(go + 6000000U);
            CHECK(complete.robot.stand.phase == Phase::COMPLETE);
            CHECK(complete.robot.stand.segment == 12U); CHECK(complete.robot.stand_stopping);
            CHECK(complete.robot.outputs.ui_state == core::State::OPENER);
            CHECK_FALSE(complete.robot.outputs.motors_enabled); app_test::zero(rig.port);
            const auto stop = rig.tick(go + 6000001U);
            CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
            CHECK(stop.robot.outputs.ui_state == core::State::STOPPED);
            CHECK(stop.robot.stand.phase == Phase::COMPLETE); CHECK_FALSE(stop.robot.stand.fresh);
            CHECK_FALSE(stop.robot.stand.phase_changed); app_test::zero(rig.port);
        }
    }
}

TEST_CASE("P2 B4 D120 opponents and contact cues never route the bench into combat") {
    app_test::Rig rig; const auto go = rig.go();
    for (std::uint32_t elapsed = 1000U; elapsed < 6000000U; elapsed += 1000U) {
        const std::uint8_t masks[] = {0U, 2U, 7U, 8U, 16U, 32U, 64U, 127U};
        rig.source.opp_raw_mask = static_cast<std::uint8_t>(masks[(elapsed / 1000U) % 8U] ^ 0x78U);
        rig.source.ax_g = 2.0F; rig.source.ay_g = 2.0F;
        const auto report = rig.tick(go + elapsed);
        noCombat(report.robot); CHECK(report.robot.contract_faults == 0U);
        CHECK(std::fabs(report.robot.outputs.duty_l) <= .25F);
        CHECK(std::fabs(report.robot.outputs.duty_r) <= .25F);
    }
}

TEST_CASE("P2 B4 D120 stand governor caps after compensation and retains slew reversal braking") {
    governor::Governor governor; governor::Request request;
    request.profile = governor::Profile::STAND; request.inhibited = false;
    request.vbat_v = 9.0F; request.duty_l = 1.0F; request.duty_r = -1.0F;
    const auto first = governor.step(0U, request);
    CHECK(first.duty_l == 0.0F); CHECK(first.duty_r == 0.0F);
    const auto ramp = governor.step(1000U, request);
    CHECK(ramp.duty_l == doctest::Approx(.02F)); CHECK(ramp.duty_r == doctest::Approx(-.02F));
    const auto full = governor.step(100000U, request);
    CHECK(full.duty_l == .25F); CHECK(full.duty_r == -.25F);
    request.duty_l = -1.0F; request.duty_r = 1.0F;
    const auto reverse = governor.step(101000U, request);
    CHECK(reverse.duty_l == 0.0F); CHECK(reverse.duty_r == 0.0F);
    governor.step(200000U, request); request.brake = true;
    const auto brake = governor.step(200001U, request);
    CHECK(brake.duty_l == 0.0F); CHECK(brake.duty_r == 0.0F);
}

TEST_CASE("P2 B4 D120 interrupt is additive finite active-only and preserves terminal snapshots") {
    for (const auto reason : {Reason::STOP, Reason::EDGE}) {
        for (unsigned row = 0U; row < 12U; ++row) {
            stand_sequence::Sequence sequence; const auto initial = sequence.report();
            CHECK_FALSE(sequence.interrupt(reason)); same(sequence.report(), initial);
            APP_REQUIRE(sequence.start(0U));
            for (unsigned n = 1U; n <= row; ++n) {
                sequence.step(n * SEGMENT_US - 1U); sequence.step(n * SEGMENT_US);
            }
            const auto active = sequence.report();
            for (const auto invalid : {Reason::NONE, Reason::CLOCK_ORDER, Reason::CLOCK_GAP,
                                       static_cast<Reason>(255U)}) {
                CHECK_FALSE(sequence.interrupt(invalid)); same(sequence.report(), active);
            }
            CHECK(sequence.interrupt(reason)); const auto terminal = sequence.report();
            CHECK(terminal.phase == Phase::INTERRUPTED); CHECK(terminal.reason == reason);
            CHECK(terminal.segment == row); CHECK(terminal.fresh); CHECK(terminal.phase_changed);
            CHECK(terminal.duty_l == 0.0F); CHECK(terminal.duty_r == 0.0F);
            CHECK_FALSE(sequence.interrupt(Reason::STOP)); same(sequence.report(), terminal);
            CHECK_FALSE(sequence.interrupt(Reason::EDGE)); same(sequence.report(), terminal);
            const auto passive = sequence.step(row * SEGMENT_US, true, true);
            CHECK(passive.reason == reason); CHECK_FALSE(passive.fresh);
            CHECK_FALSE(passive.phase_changed); CHECK_FALSE(sequence.start(42U));
        }
    }
}

TEST_CASE("P2 B4 D120 genuine stopped Transaction cannot perform D103 service reset") {
    app_test::Rig rig; const auto go = rig.go(); rig.source.stop_requested = true;
    rig.tick(go + 1000U); rig.tick(go + 2000U);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    rig.port.now = go + 3000U; APP_REQUIRE(rig.owner.open());
    const auto before = rig.owner.report(); const auto previous = rig.owner.previous();
    const auto calls = rig.port.count;
    CHECK_FALSE(rig.owner.resetStoppedRobotForService());
    CHECK(rig.owner.report().phase == before.phase); CHECK(rig.port.count == calls);
    CHECK(rig.owner.report().robot.token == before.robot.token);
    CHECK(rig.owner.previous().token == previous.token);
    CHECK(rig.owner.previous().applied_valid == previous.applied_valid);
    APP_REQUIRE(rig.owner.decide(rig.source)); APP_REQUIRE(rig.owner.finish());
    CHECK(rig.owner.report().robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
}

TEST_CASE("P2 B4 D120 interrupt cannot replace completed or faulted sequence evidence") {
    for (const bool completed : {false, true}) {
        stand_sequence::Sequence sequence; APP_REQUIRE(sequence.start(0U));
        if (completed) {
            for (unsigned row = 1U; row <= 12U; ++row) {
                sequence.step(row * SEGMENT_US - 1U); sequence.step(row * SEGMENT_US);
            }
        } else sequence.step(SEGMENT_US);
        const auto before = sequence.report();
        CHECK(before.phase == (completed ? Phase::COMPLETE : Phase::FAULT));
        for (const auto reason : {Reason::STOP, Reason::EDGE, Reason::NONE}) {
            CHECK_FALSE(sequence.interrupt(reason)); same(sequence.report(), before);
        }
    }
}

TEST_CASE("P2 B4 D120 Runtime grant alone never publishes service reset or service-only mode") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.begin(true));
    for (unsigned i = 0U; i < 50U; ++i) {
        APP_REQUIRE(rig.next());
        CHECK_FALSE(rig.owner.report().service_reset_pending);
        CHECK_FALSE(rig.owner.report().service_reset_fresh);
        CHECK_FALSE(rig.owner.report().service_only);
    }
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("P2 B4 D120 configured Runtime refuses genuine post-STOP MODE reset gesture") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.stopped(false, false, true));
    const auto token = rig.robot().token;
    for (unsigned i = 0U; i < 1150U; ++i) {
        rig.fake.button_raw = i < 30U || i >= 1100U ? service_reset_test::NONE : service_reset_test::MODE;
        rig.next();
        CHECK_FALSE(rig.owner.report().service_reset_pending);
        CHECK_FALSE(rig.owner.report().service_reset_fresh);
        CHECK_FALSE(rig.owner.report().service_only);
        CHECK(rig.robot().outputs.ui_state == core::State::STOPPED);
        CHECK(rig.robot().token >= token); CHECK_FALSE(rig.fake.enabled);
    }
}
#endif
