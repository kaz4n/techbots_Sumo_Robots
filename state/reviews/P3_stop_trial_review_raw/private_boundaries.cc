// Independently checks D126 deadlines, priority and electrical envelopes.
// Uses established actual-owner fixtures and explicit contract expectations.
// Frozen before any C++ execution; host observations are not physical distance.
#include "fixtures/drive_test_fixture.h"
#include "fixtures/app_service_reset/fixture.h"

using Phase = stop_trial::Phase;
using Reason = stop_trial::Reason;

TEST_CASE("B3 B7 D126 private delayed approach completion observes a whole brake across wrap") {
    drive_test::Rig rig;
    const auto go = rig.goDrive(0xFFFFFFFFU - 6800000U);
    const auto observed = go + 1300000U;
    auto report = rig.at(observed);
    CHECK(report.robot.stop_trial.phase == Phase::BRAKE);
    CHECK(report.robot.stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
    CHECK(report.robot.stop_trial.started);
    CHECK(report.robot.stop_trial.started_us == go);
    CHECK(report.robot.stop_trial.approach_finished);
    CHECK(report.robot.stop_trial.approach_finished_us == observed);
    CHECK(report.robot.stop_trial.approach_status == motion::Status::DONE);
    CHECK_FALSE(report.robot.stop_trial.finished);
    CHECK_FALSE(report.robot.stop_trial_stopping);
    report = rig.at(observed + 499999U);
    CHECK(report.robot.stop_trial.phase == Phase::BRAKE);
    CHECK(report.robot.outputs.motors_enabled);
    CHECK(report.robot.outputs.duty_l == 0.0F);
    CHECK(report.robot.outputs.duty_r == 0.0F);
    CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0));
    for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
    report = rig.at(observed + 500000U);
    CHECK(report.robot.stop_trial.phase == Phase::COMPLETE);
    CHECK(report.robot.stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
    CHECK(report.robot.stop_trial.finished);
    CHECK(report.robot.stop_trial.finished_us == observed + 500000U);
    CHECK(report.robot.stop_trial_stopping);
    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
    drive_test::disabled(report, rig.port);
    report = rig.next();
    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(report.robot.stop_trial.phase == Phase::COMPLETE);
    drive_test::disabled(report, rig.port);
}

TEST_CASE("B4 R5 D126 private edge wins either primitive deadline without terminating escape") {
    for (const bool braking : {false, true}) {
        for (const auto white : {1U, 3U, 12U, 15U}) {
            for (const auto offset : {-1, 0, 1}) {
                CAPTURE(braking); CAPTURE(white); CAPTURE(offset);
                drive_test::Rig rig;
                const auto go = rig.goDrive();
                std::uint32_t deadline = go + 1000000U;
                if (braking) {
                    APP_REQUIRE(rig.at(deadline).robot.stop_trial.phase == Phase::BRAKE);
                    deadline += 500000U;
                }
                rig.white(white);
                const auto time = deadline + static_cast<std::uint32_t>(offset);
                auto report = rig.at(time);
                CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
                CHECK(report.robot.stop_trial.phase == Phase::INTERRUPTED);
                CHECK(report.robot.stop_trial.reason == Reason::EDGE);
                CHECK(report.robot.stop_trial.finished);
                CHECK(report.robot.stop_trial.finished_us == time);
                CHECK(report.robot.stop_trial.approach_finished == braking);
                CHECK(report.robot.stop_trial.approach_status ==
                    (braking ? motion::Status::DONE : motion::Status::ACTIVE));
                CHECK(report.robot.stop_trial_edge_interrupted);
                CHECK_FALSE(report.robot.stop_trial_stopping);
                CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
                for (unsigned later = 0U; later < 3U; ++later) {
                    report = rig.next();
                    CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
                    CHECK_FALSE(report.robot.stop_trial_stopping);
                    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
                    if (white == 15U) drive_test::disabled(report, rig.port);
                }
                rig.source.stop_requested = true;
                report = rig.next();
                CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
                CHECK(report.robot.stop_trial.reason == Reason::EDGE);
                drive_test::disabled(report, rig.port);
            }
        }
    }
}

TEST_CASE("B6 R6 D126 private trial cap reduction is immediate after compensated full contact") {
    for (const auto voltage : {0.0F, 1.0F, 8.0F, 11.1F}) {
        CAPTURE(voltage);
        governor::Governor owner;
        governor::Request request;
        request.profile = governor::Profile::ATTACK;
        request.centered = true; request.contact = true; request.inhibited = false;
        request.duty_l = request.duty_r = 1.0F; request.vbat_v = voltage;
        CHECK(owner.step(0U, request).valid);
        APP_REQUIRE(owner.step(1000000U, request).duty_l == 1.0F);
        request.profile = governor::Profile::STOP_TRIAL_FORWARD;
        request.centered = false; request.contact = false;
        auto result = owner.step(1000000U, request);
        CHECK(result.valid);
        CHECK(result.duty_l == config::STOP_TRIAL_DUTY);
        CHECK(result.duty_r == config::STOP_TRIAL_DUTY);
        request.profile = governor::Profile::SEARCH_FORWARD;
        result = owner.step(1000000U, request);
        CHECK(result.duty_l == 0.30F); CHECK(result.duty_r == 0.30F);
        request.profile = governor::Profile::STOP_TRIAL_FORWARD;
        result = owner.step(1001000U, request);
        CHECK(result.duty_l <= 0.30F + config::SLEW_DUTY_PER_MS);
        CHECK(result.duty_r <= 0.30F + config::SLEW_DUTY_PER_MS);
        CHECK(result.duty_l <= config::STOP_TRIAL_DUTY);
        CHECK(result.duty_r <= config::STOP_TRIAL_DUTY);
        request.brake = true;
        result = owner.step(1001000U, request);
        CHECK(result.duty_l == 0.0F); CHECK(result.duty_r == 0.0F);
    }
}

TEST_CASE("B3 B13 D126 private finite Runtime timeout then service reconstruction never rearms") {
    service_reset_test::Rig rig;
    APP_REQUIRE(rig.begin(true, true, false));
    APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.run(30U));
    APP_REQUIRE(rig.robot().line_available && !rig.robot().line_raw_mode);
    APP_REQUIRE(!rig.robot().line_calibration_hold && !rig.robot().line_start_rearming);
    APP_REQUIRE(rig.robot().button_available && rig.robot().button_level == core::ButtonLevel::NONE);
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST));
    APP_REQUIRE(rig.robot().lifecycle.gate.start_release);
    bool completed = false;
    for (unsigned i = 0U; i < 8000U; ++i) {
        APP_REQUIRE(rig.next());
        completed = completed || rig.robot().stop_trial.phase == Phase::COMPLETE;
        if (rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING) break;
    }
    APP_REQUIRE(completed);
    APP_REQUIRE(rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING);
    CHECK(rig.robot().stop_trial.phase == Phase::COMPLETE);
    CHECK(rig.robot().stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
    const auto epoch = rig.owner.transaction().recording().summary().epoch_token;
    const auto highs = rig.fake.highs; const auto nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending()); APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.report().service_only);
    CHECK(rig.robot().stop_trial.phase == Phase::NOT_STARTED);
    CHECK_FALSE(rig.robot().stop_trial.started);
    CHECK_FALSE(rig.robot().stop_trial_stopping);
    CHECK_FALSE(rig.robot().stop_trial_edge_interrupted);
    APP_REQUIRE(rig.run(35U)); APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST));
    CHECK(rig.owner.report().service_action.status == app::ServiceActionStatus::UNAVAILABLE);
    for (unsigned i = 0U; i < 5200U; ++i) {
        APP_REQUIRE(rig.next());
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go);
        CHECK_FALSE(rig.robot().outputs.motors_enabled);
        CHECK(rig.robot().stop_trial.phase == Phase::NOT_STARTED);
    }
    CHECK(rig.owner.transaction().recording().summary().epoch_token == epoch);
    CHECK(rig.fake.highs == highs); CHECK(rig.fake.nonzero == nonzero);
    CHECK_FALSE(rig.fake.enabled);
    for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
