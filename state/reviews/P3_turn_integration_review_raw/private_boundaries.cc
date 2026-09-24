// Independently probes D125 owner boundaries using existing public fixtures.
// Distinguishes actual MotorGate inhibition from helper status and physical motion.
// Reviewer-only host checks run after the public oracle and source are frozen.
#include "fixtures/drive_test_fixture.h"
#include "fixtures/app_service_reset/fixture.h"

using Phase = turn_trial::Phase;
using Reason = turn_trial::Reason;

TEST_CASE("B3 B7 D125 private delayed timeout never spends its observed brake interval") {
    drive_test::Rig rig;
    const auto go = rig.goDrive();
    auto report = rig.at(go + 710000U);
    CHECK(report.robot.turn_trial.phase == Phase::BRAKE);
    CHECK(report.robot.turn_trial.turn_status == motion::Status::TIMED_OUT);
    CHECK(report.robot.turn_trial.turn_finished_us == go + 710000U);
    CHECK_FALSE(report.robot.turn_trial_stopping);
    report = rig.at(go + 1209999U);
    CHECK(report.robot.turn_trial.phase == Phase::BRAKE);
    CHECK(report.robot.outputs.motors_enabled);
    CHECK(report.robot.outputs.duty_l == 0.0F);
    CHECK(report.robot.outputs.duty_r == 0.0F);
    report = rig.at(go + 1210000U);
    CHECK(report.robot.turn_trial.phase == Phase::COMPLETE);
    CHECK(report.robot.turn_trial_stopping);
    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
    drive_test::disabled(report, rig.port);
    report = rig.next();
    CHECK(report.robot.outputs.ui_state == core::State::STOPPED);
    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(report.robot.turn_trial.phase == Phase::COMPLETE);
    drive_test::disabled(report, rig.port);
}

TEST_CASE("B4 R5 D125 private white at observed brake deadline wins and never prematurely stops escape") {
    for (const auto white : {1U, 3U, 12U, 15U}) {
        for (const auto elapsed : {499999U, 500000U, 500001U}) {
            CAPTURE(white); CAPTURE(elapsed);
            drive_test::Rig rig;
            const auto go = rig.goDrive();
            rig.source.raw_heading_deg = config::TURN_TRIAL_DEG;
            const auto brake = go + 1000U;
            APP_REQUIRE(rig.at(brake).robot.turn_trial.phase == Phase::BRAKE);
            rig.white(white);
            auto report = rig.at(brake + elapsed);
            CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK(report.robot.turn_trial.phase == Phase::INTERRUPTED);
            CHECK(report.robot.turn_trial.reason == Reason::EDGE);
            CHECK(report.robot.turn_trial_edge_interrupted);
            CHECK_FALSE(report.robot.turn_trial_stopping);
            CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
            for (unsigned later = 0U; later < 3U; ++later) {
                report = rig.next();
                CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
                CHECK_FALSE(report.robot.turn_trial_stopping);
                CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
                if (white == 15U) drive_test::disabled(report, rig.port);
            }
            rig.source.stop_requested = true;
            report = rig.next();
            CHECK(report.robot.outputs.ui_state == core::State::STOPPED);
            drive_test::disabled(report, rig.port);
        }
    }
}

#if defined(APP_TEST_CONFIGURED_BUTTONS)
TEST_CASE("B3 B13 D125 private complete actual Runtime then service reset clears report without rearm") {
    service_reset_test::Rig rig;
    APP_REQUIRE(rig.begin(true, true, false));
    APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.robot().line_start_rearming);
    APP_REQUIRE(rig.run(30U));
    APP_REQUIRE(!rig.robot().line_start_rearming);
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST));
    APP_REQUIRE(rig.robot().lifecycle.gate.start_release);
    bool completed = false;
    for (unsigned i = 0U; i < 7000U; ++i) {
        APP_REQUIRE(rig.next());
        completed = completed || rig.robot().turn_trial.phase == Phase::COMPLETE;
        if (rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING) break;
    }
    APP_REQUIRE(completed);
    APP_REQUIRE(rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING);
    CHECK(rig.robot().turn_trial.phase == Phase::COMPLETE);
    const auto epoch = rig.owner.transaction().recording().summary().epoch_token;
    const auto highs = rig.fake.highs;
    const auto nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending());
    APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.report().service_only);
    CHECK(rig.robot().turn_trial.phase == Phase::NOT_STARTED);
    CHECK_FALSE(rig.robot().turn_trial_stopping);
    CHECK_FALSE(rig.robot().turn_trial_edge_interrupted);
    APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST));
    CHECK(rig.owner.report().service_action.status == app::ServiceActionStatus::UNAVAILABLE);
    CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
    for (unsigned i = 0U; i < 5200U; ++i) {
        APP_REQUIRE(rig.next());
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go);
        CHECK_FALSE(rig.robot().outputs.motors_enabled);
        CHECK(rig.robot().turn_trial.phase == Phase::NOT_STARTED);
    }
    CHECK(rig.owner.transaction().recording().summary().epoch_token == epoch);
    CHECK(rig.fake.highs == highs);
    CHECK(rig.fake.nonzero == nonzero);
    CHECK_FALSE(rig.fake.enabled);
    for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}

TEST_CASE("B3 D089 D125 private premature START during classified line rearm is consumed without replay") {
    service_reset_test::Rig rig;
    APP_REQUIRE(rig.begin(true, true, false));
    APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.robot().line_start_rearming);
    CHECK_FALSE(rig.request(countdown::Service::DRIVE_TEST));
    for (unsigned i = 0U; i < 5200U; ++i) {
        APP_REQUIRE(rig.next());
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go);
        CHECK(rig.robot().turn_trial.phase == Phase::NOT_STARTED);
        CHECK_FALSE(rig.fake.enabled);
    }
    CHECK(rig.fake.highs == 0U);
    CHECK(rig.fake.nonzero == 0U);
    APP_REQUIRE(!rig.robot().line_start_rearming);
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST));
    CHECK(rig.robot().lifecycle.gate.start_release);
}
#endif
