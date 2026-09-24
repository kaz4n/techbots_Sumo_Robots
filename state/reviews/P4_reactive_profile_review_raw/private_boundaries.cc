// Probes the adopted D128 public contract without deriving outcomes from routing.
// Distinguishes actual Gate writes and post-GO observations from state labels.
// Frozen reviewer-only host cases execute after public freeze, never on hardware.
#include "fixtures/drive_test_fixture.h"
#include "fixtures/app_service_reset/fixture.h"

namespace {
struct ReactiveRig : drive_test::Rig {
    std::uint32_t prepare(unsigned mode = 1U, std::uint32_t base = 0U) {
        prime(base);
        for (unsigned i = 1U; i < mode; ++i) shortMode();
        APP_REQUIRE(!owner.report().robot.menu.selection.service_menu);
        const auto release = releaseSelected();
        APP_REQUIRE(owner.report().robot.lifecycle.gate.start_release);
        at(release + 1500000U); next(); at(release + 4500000U);
        return release;
    }
    std::uint32_t go(unsigned mode = 1U, unsigned target = 0U,
                     std::uint32_t base = 0U) {
        const auto release = prepare(mode, base);
        opponent(target);
        at(release + 5098000U); at(release + 5099000U);
        at(release + 5099999U);
        drive_test::disabled(owner.report(), port);
        at(release + 5100000U);
        APP_REQUIRE(owner.report().robot.lifecycle.gate.go);
        APP_REQUIRE(owner.report().robot.opponent_mask == target);
        return now;
    }
};
void receipt(const ReactiveRig& rig) {
    const auto& r = rig.owner.report();
    CHECK(r.robot.contract_faults == 0U);
    CHECK(r.applied.consumed);
    CHECK(r.applied.feedback.applied_valid);
    CHECK(r.applied.feedback.token == r.robot.token);
    CHECK(r.applied.fault == motors::Fault::NONE);
    CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0));
    CHECK(r.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
    CHECK(std::fabs(r.applied.feedback.duty_l) <= std::fabs(r.robot.outputs.duty_l));
    CHECK(std::fabs(r.applied.feedback.duty_r) <= std::fabs(r.robot.outputs.duty_r));
    if (!MOTORS_ALLOWED) app_test::zero(rig.port);
}
}

TEST_CASE("B3 B8 B9 D128 private every mode and confirmed bearing starts literal SEARCH") {
    static_assert(fsm::RobotResult::REACTIVE_PROFILE);
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        for (unsigned target : {1U, 2U, 4U, 7U, 8U, 64U}) {
            for (std::uint32_t base : {0U, 0xFFF00000U}) {
                CAPTURE(mode); CAPTURE(target); CAPTURE(base);
                ReactiveRig rig;
                rig.go(mode, target, base);
                auto r = rig.owner.report();
                CHECK(r.robot.running_mode == static_cast<core::Mode>(mode));
                CHECK(r.robot.outputs.ui_state == core::State::SEARCH);
                CHECK(r.robot.outputs.duty_l == 0.0F);
                CHECK(r.robot.outputs.duty_r == 0.0F);
                receipt(rig);
                const bool front = (target & 7U) != 0U;
                for (unsigned observation = 1U; observation <= 3U; ++observation) {
                    r = rig.next();
                    const auto expected = !front ? core::State::DEFEND_TURN :
                        (observation == 3U && (target == 2U || target == 7U) ?
                         core::State::ATTACK : core::State::TRACK);
                    CHECK(r.robot.outputs.ui_state == expected);
                    CHECK(r.robot.running_mode == static_cast<core::Mode>(mode));
                    receipt(rig);
                }
            }
        }
    }
}

TEST_CASE("B8 D128 private empty GO preserves entry yaw across first normal observation") {
    ReactiveRig rig;
    const auto release = rig.prepare();
    rig.source.raw_heading_deg = 37.0F;
    const auto go = release + 5100000U;
    APP_REQUIRE(rig.at(go).robot.lifecycle.gate.go);
    APP_REQUIRE(rig.owner.report().robot.outputs.ui_state == core::State::SEARCH);
    CHECK(rig.owner.report().robot.outputs.duty_l > 0.0F);
    CHECK(rig.owner.report().robot.outputs.duty_r < 0.0F);
    rig.source.raw_heading_deg = 100.0F;
    rig.next();
    rig.source.raw_heading_deg = 396.0F;
    for (unsigned i = 0U; i < 20U; ++i) rig.next();
    CHECK(rig.owner.report().robot.outputs.duty_r < 0.0F);
    rig.source.raw_heading_deg = 397.0F;
    for (unsigned i = 0U; i < 20U; ++i) rig.next();
    CHECK(rig.owner.report().robot.outputs.ui_state == core::State::SEARCH);
    CHECK(rig.owner.report().robot.outputs.duty_l > 0.0F);
    CHECK(rig.owner.report().robot.outputs.duty_r > 0.0F);
    CHECK(rig.owner.report().robot.outputs.duty_l <= config::SEARCH_DUTY_MAX);
    CHECK(rig.owner.report().robot.outputs.duty_r <= config::SEARCH_DUTY_MAX);
    receipt(rig);
}

TEST_CASE("B5 B8 D128 private raw onset at GO is not fabricated effective perception") {
    ReactiveRig rig;
    const auto release = rig.prepare();
    rig.at(release + 5099999U);
    rig.opponent(2U);
    APP_REQUIRE(rig.at(release + 5100000U).robot.lifecycle.gate.go);
    CHECK(rig.owner.report().robot.opponent_mask == 0U);
    CHECK(rig.owner.report().robot.outputs.ui_state == core::State::SEARCH);
    CHECK(rig.owner.report().robot.outputs.duty_l > 0.0F);
    CHECK(rig.owner.report().robot.outputs.duty_r < 0.0F);
    for (unsigned i = 1U; i <= 3U; ++i) {
        const auto r = rig.next();
        CHECK(r.robot.opponent_mask == 2U);
        CHECK(r.robot.outputs.ui_state == (i == 3U ? core::State::ATTACK : core::State::TRACK));
    }
    receipt(rig);
}

TEST_CASE("B3 B4 D128 private white GO outranks reactive entry and explicit STOP outranks escape") {
    for (unsigned white : {1U, 3U, 12U, 15U}) {
        ReactiveRig rig;
        const auto release = rig.prepare(6U);
        rig.opponent(1U);
        rig.at(release + 5098000U); rig.at(release + 5099000U);
        rig.white(white);
        const auto r = rig.at(release + 5100000U);
        APP_REQUIRE(r.robot.lifecycle.gate.go);
        CHECK(r.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        for (unsigned i = 0U; i < 5U; ++i) {
            const auto next = rig.next();
            CHECK(next.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK(next.robot.lifecycle.gate.phase == countdown::Phase::READY);
        }
        rig.source.stop_requested = true;
        CHECK(rig.next().robot.outputs.ui_state == core::State::STOPPED);
        drive_test::disabled(rig.owner.report(), rig.port);
    }
}

#if defined(APP_TEST_CONFIGURED_BUTTONS)
TEST_CASE("B3 B13 D103 D128 private real Runtime hold and retained attempt after service-only reset") {
    service_reset_test::Rig rig;
    APP_REQUIRE(rig.begin(true, true, false));
    APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.run(30U, service_reset_test::START));
    rig.fake.button_raw = service_reset_test::NONE;
    bool released = false;
    for (unsigned i = 0U; i < 40U && !released; ++i) {
        APP_REQUIRE(rig.next());
        released = rig.robot().lifecycle.gate.start_release;
    }
    APP_REQUIRE(released);
    const auto release = rig.robot().lifecycle.gate.release_us;
    bool go = false;
    for (unsigned i = 0U; i < 5200U && !go; ++i) {
        APP_REQUIRE(rig.next());
        go = rig.robot().lifecycle.gate.go;
        if (!go) {
            CHECK_FALSE(rig.fake.enabled);
            for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
        }
    }
    APP_REQUIRE(go);
    CHECK(rig.robot().outputs.ui_state == core::State::SEARCH);
    CHECK(static_cast<std::uint32_t>(rig.owner.decisionInput().t_us - release) >= 5100000U);
    CHECK(rig.fake.enabled == (MOTORS_ALLOWED != 0));
    APP_REQUIRE(rig.firstStop());
    APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING);
    const auto epoch = rig.owner.transaction().recording().summary().epoch_token;
    const auto highs = rig.fake.highs;
    const auto nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending());
    APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.report().service_only);
    APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(!rig.robot().menu.selection.service_menu);
    APP_REQUIRE(rig.run(30U, service_reset_test::START));
    rig.fake.button_raw = service_reset_test::NONE;
    for (unsigned i = 0U; i < 5300U; ++i) {
        APP_REQUIRE(rig.next());
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go);
        CHECK_FALSE(rig.robot().outputs.motors_enabled);
    }
    CHECK(rig.owner.transaction().recording().summary().epoch_token == epoch);
    CHECK(rig.fake.highs == highs);
    CHECK(rig.fake.nonzero == nonzero);
    CHECK_FALSE(rig.fake.enabled);
    for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
#endif
