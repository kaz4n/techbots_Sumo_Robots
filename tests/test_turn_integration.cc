// Tests the D125 isolated turn profile through actual Robot and Transaction APIs.
// Keeps signed angle, primitive outcome and applied evidence independently visible.
// Frozen public-contract scenarios run in M0/M1 and all four config-angle overlays.
#include "fixtures/turn_integration_fixture.h"
#include "hal/ui_display.h"
#include <limits>

using namespace turn_integration;

TEST_CASE("B1 B13 D125 immutable profile admits one available selected local turn trial") {
    CHECK(SUMOX_P3_TURN_TRIAL == 1); CHECK(SUMOX_P3_DRIVE_TEST == 0);
    CHECK(SUMOX_B4_STAND == 0); CHECK(MATCH == 0); CHECK(fsm::RobotResult::TURN_TRIAL_PROFILE);
    CHECK_FALSE(fsm::RobotResult::DRIVE_TEST_PROFILE); CHECK_FALSE(fsm::RobotResult::STAND_PROFILE);
    CHECK((ANGLE == -180.0F || ANGLE == -90.0F || ANGLE == 90.0F || ANGLE == 180.0F));
    const fsm::RobotResult initial; CHECK(initial.turn_trial.phase == Phase::NOT_STARTED);
    CHECK_FALSE(initial.turn_trial_stopping); CHECK_FALSE(initial.turn_trial_edge_interrupted);
    Rig rig; rig.selectDrive(); rig.releaseSelected(); const auto release = rig.owner.report();
    CHECK(release.robot.menu.request == countdown::Service::DRIVE_TEST);
    CHECK_FALSE(release.robot.menu.request_unavailable); CHECK(release.robot.lifecycle.gate.start_release);
    CHECK(release.robot.turn_trial.phase == Phase::NOT_STARTED);
    drive_test::disabled(release, rig.port);
}

TEST_CASE("B3 B13 D125 six match selections and all other services cannot start the trial") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        Rig rig; rig.prime(); for (unsigned i = 1U; i < mode; ++i) rig.shortMode();
        CHECK(static_cast<unsigned>(rig.owner.report().robot.menu.selection.mode) == mode);
        rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
        const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
        CHECK(later.robot.turn_trial.phase == Phase::NOT_STARTED);
        CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
    }
    for (unsigned item : {0U, 1U, 3U}) {
        Rig rig; rig.prime(); rig.longMode(); for (unsigned i = 0U; i < item; ++i) rig.shortMode();
        rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
        const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
        CHECK(later.robot.turn_trial.phase == Phase::NOT_STARTED);
    }
}

TEST_CASE("B6 B7 D125 GO captures configured signed turn after heading reset with governed slew") {
    for (float origin : {0.0F, 170.0F, -720.0F}) for (float voltage : {9.0F, 11.1F}) {
        Rig rig; rig.source.raw_heading_deg = origin; rig.source.vbat_v = voltage;
        const auto go = rig.goDrive(); const auto initial = rig.owner.report(); running(rig, initial);
        CHECK(initial.robot.heading.heading_deg == 0.0F); CHECK(initial.robot.heading.imu_ok);
        CHECK(initial.robot.turn_trial.phase == Phase::TURN); CHECK(initial.robot.turn_trial.started_us == go);
        CHECK(initial.robot.turn_trial.duty_l == SIGN * .8F);
        CHECK(initial.robot.turn_trial.duty_r == -SIGN * .8F); CHECK_FALSE(initial.robot.turn_trial.imu_fallback);
        const auto first = rig.next(); running(rig, first);
        CHECK(std::fabs(first.robot.outputs.duty_l) <= .021F);
        const auto full = rig.at(go + 40000U); running(rig, full);
        CHECK(full.robot.outputs.duty_l == SIGN * .8F); CHECK(full.robot.outputs.duty_r == -SIGN * .8F);
    }
}

TEST_CASE("B7 D125 strict adjacent five-degree samples and overshoot use actual current heading") {
    const float boundary = ANGLE - SIGN * 5.0F;
    for (float heading : {std::nextafter(boundary, 0.0F), boundary, std::nextafter(boundary, ANGLE)}) {
        Rig rig; const auto go = rig.goDrive(); rig.source.raw_heading_deg = heading;
        const auto result = rig.at(go + 1000U);
        if (heading == std::nextafter(boundary, ANGLE)) braking(rig, result, motion::Status::DONE, go + 1000U);
        else { running(rig, result); CHECK(result.robot.turn_trial.phase == Phase::TURN);
            CHECK(result.robot.turn_trial.duty_l == SIGN * .25F); }
    }
    Rig rig; const auto go = rig.goDrive(); rig.at(go + 40000U);
    rig.source.raw_heading_deg = ANGLE + SIGN * 10.0F; const auto reverse = rig.next();
    CHECK(reverse.robot.turn_trial.phase == Phase::TURN);
    CHECK(reverse.robot.turn_trial.duty_l == -SIGN * .25F);
    CHECK(reverse.robot.outputs.duty_l == 0.0F); CHECK(reverse.robot.outputs.duty_r == 0.0F);
    const auto corrected = rig.next(20000U); running(rig, corrected);
    CHECK(corrected.robot.outputs.duty_l == -SIGN * .25F);
    CHECK(corrected.robot.outputs.duty_r == SIGN * .25F);
}

TEST_CASE("B7 D125 healthy completion keeps full observed brake then immediately inhibits and stops") {
    for (auto base : {0U, 0xffa00000U}) {
        Rig rig; const auto go = rig.goDrive(base); rig.at(go + 30000U);
        rig.source.raw_heading_deg = ANGLE; const auto entered = go + 31000U;
        braking(rig, rig.at(entered), motion::Status::DONE, entered);
        braking(rig, rig.at(entered + 499999U), motion::Status::DONE, entered);
        const auto done = rig.at(entered + 500000U); completed(rig, done, motion::Status::DONE, entered + 500000U);
        const auto stop = rig.next(1U); CHECK(stop.robot.outputs.ui_state == core::State::STOPPED);
        CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
        sameTrial(stop.robot.turn_trial, done.robot.turn_trial); CHECK_FALSE(stop.robot.turn_trial.fresh);
        CHECK_FALSE(stop.robot.turn_trial.phase_changed); drive_test::disabled(stop, rig.port);
    }
}

TEST_CASE("B7 B15 D125 actual timeout is distinct from success and emits one bench-origin event") {
    Rig rig; const auto go = rig.goDrive(); running(rig, rig.at(go + 699999U));
    rig.source.raw_heading_deg = ANGLE;
    const auto timed = rig.at(go + 700000U); braking(rig, timed, motion::Status::TIMED_OUT, go + 700000U);
    CHECK(timed.robot.contract_faults == 0U); CHECK_FALSE(timed.robot.events.overflowed);
    CHECK(timeoutCount(rig.owner.recording(), go + 700000U) == 1U);
    braking(rig, rig.at(go + 1199999U), motion::Status::TIMED_OUT, go + 700000U);
    completed(rig, rig.at(go + 1200000U), motion::Status::TIMED_OUT, go + 1200000U);
    rig.next(); rig.next(); CHECK(timeoutCount(rig.owner.recording(), go + 700000U) == 1U);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK(rig.owner.recording().summary().event_semantic_rejected == 0U);
}

TEST_CASE("B7 D125 real initial IMU absence and recovery retain full angle fallback deadline") {
    Rig rig; rig.source.imu_ok = false; const auto go = rig.goDrive();
    CHECK(rig.owner.report().robot.turn_trial.imu_fallback);
    rig.source.imu_ok = true; rig.source.raw_heading_deg = ANGLE;
    const auto recovered = rig.at(go + 1000U); running(rig, recovered);
    CHECK(recovered.robot.turn_trial.imu_fallback); CHECK(recovered.robot.turn_trial.phase == Phase::TURN);
    running(rig, rig.at(go + FALLBACK_US - 1U));
    braking(rig, rig.at(go + FALLBACK_US), motion::Status::DONE, go + FALLBACK_US);
    completed(rig, rig.at(go + FALLBACK_US + 500000U), motion::Status::DONE, go + FALLBACK_US + 500000U);
    CHECK(timeoutCount(rig.owner.recording(), go + 700000U) == 0U);
}

TEST_CASE("B7 D125 delayed timeout starts the full brake at its observed application tick") {
    Rig rig; const auto go = rig.goDrive(); const auto observed = go + 2000000U;
    braking(rig, rig.at(observed), motion::Status::TIMED_OUT, observed);
    braking(rig, rig.at(observed + 499999U), motion::Status::TIMED_OUT, observed);
    completed(rig, rig.at(observed + 500000U), motion::Status::TIMED_OUT, observed + 500000U);
    CHECK(timeoutCount(rig.owner.recording(), observed) == 1U);
}

TEST_CASE("B7 D125 real mid-turn IMU loss latches remaining angle and recovery cannot retarget") {
    Rig rig; const auto go = rig.goDrive(); rig.source.raw_heading_deg = ANGLE - SIGN * 30.0F;
    rig.at(go + 20000U); rig.source.imu_ok = false;
    rig.source.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
    const auto lost = rig.at(go + 30000U); running(rig, lost);
    CHECK(lost.robot.turn_trial.imu_fallback); CHECK(lost.robot.turn_trial.duty_l == SIGN * .8F);
    rig.source.imu_ok = true; rig.source.raw_heading_deg = ANGLE;
    running(rig, rig.at(go + 89999U));
    braking(rig, rig.at(go + 90000U), motion::Status::DONE, go + 90000U);
}

TEST_CASE("B5 B7 D125 every opponent mask and contact cue stays real without combat or trial restart") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mask); Rig rig; rig.opponent(mask); rig.source.ax_g = 3.0F;
        const auto go = rig.goDrive();
        for (unsigned i = 1U; i <= 30U; ++i) {
            const auto report = rig.at(go + i * 1000U); running(rig, report);
            CHECK(report.robot.turn_trial.phase == Phase::TURN);
            CHECK(report.robot.turn_trial.started_us == go); CHECK(report.robot.opponent_mask == mask);
        }
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::CONTACT) == 0U);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::STALL) == 0U);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::REFLANK_PHASE) == 0U);
    }
}

TEST_CASE("B15 D125 completed attempt retains DRIVE_TEST frames and actual one-time nonzero receipt") {
    Rig rig; const auto release = rig.releaseDrive(); const auto go = release + 5100000U;
    const auto initial = rig.at(go).applied.feedback;
    bool seen = initial.duty_l != 0.0F || initial.duty_r != 0.0F;
    std::uint32_t first = seen ? initial.applied_us : 0U;
    rig.opponent(2U);
    for (unsigned i = 1U; i <= 50U; ++i) {
        const auto r = rig.at(go + i * 1000U);
        if (!seen && (r.applied.feedback.duty_l != 0.0F || r.applied.feedback.duty_r != 0.0F)) {
            seen = true; first = r.applied.feedback.applied_us;
        }
    }
    rig.source.raw_heading_deg = ANGLE; rig.next(); const auto brake_time = rig.now;
    rig.at(brake_time + 500000U); rig.next(); rig.next();
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    std::uint32_t logged = 0U;
    CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::FIRST_NONZERO_DUTY, &logged)
        == (MOTORS_ALLOWED ? 1U : 0U));
    if (MOTORS_ALLOWED) { CHECK(seen); CHECK(logged == first); CHECK(first - release >= 5100000U); }
    else { CHECK_FALSE(seen); CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U); }
    bool recorded_turn = false;
    for (std::size_t i = 0U; i < rig.owner.recording().frames().size(); ++i) {
        recorder::StoredFrame frame; APP_REQUIRE(rig.owner.recording().frames().read(i, frame));
        if (frame.bytes.data[4] != static_cast<unsigned>(core::State::DRIVE_TEST)) continue;
        CHECK(frame.status != logframe::PackStatus::INVALID);
        recorded_turn |= frame.bytes.data[7] == 2U;
    }
    CHECK(recorded_turn);
}

TEST_CASE("B13 D125 available selected and active turn profile displays D without unavailable cross") {
    constexpr unsigned D[] = {6U, 5U, 5U, 5U, 6U};
    for (auto state : {core::State::IDLE, core::State::DRIVE_TEST}) {
        ui::DisplaySample sample; sample.state = state; sample.service_menu = true;
        sample.service = countdown::Service::DRIVE_TEST; ui::Frame frame;
        APP_REQUIRE(ui::render(sample, frame) == ui::RenderStatus::OK);
        for (unsigned y = 0U; y < 5U; ++y) {
            for (unsigned x = 0U; x < 3U; ++x)
                CHECK(frame.pixels[(y + 1U) * 13U + x] == ((D[y] & (4U >> x)) ? 7U : 0U));
            for (unsigned x = 4U; x < 9U; ++x) CHECK(frame.pixels[(y + 1U) * 13U + x] == 0U);
        }
    }
}
