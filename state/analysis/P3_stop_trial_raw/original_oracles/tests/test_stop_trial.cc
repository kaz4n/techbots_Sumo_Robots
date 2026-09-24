// Tests D126 stopping-trial software without claiming measured stopping distance.
// Uses public Robot, Straight and Governor contracts with actual Transaction receipts.
// Frozen M0/M1 cases support every accepted configured duty and isolated overlays.
#include "fixtures/stop_trial_fixture.h"
#include "hal/ui_display.h"
#include <algorithm>
#include <limits>

using namespace stop_test;

TEST_CASE("B1 B13 D126 immutable stopping profile exposes inert report and local service intent") {
    CHECK(SUMOX_P3_STOP_TRIAL == 1); CHECK(SUMOX_P3_TURN_TRIAL == 0);
    CHECK(SUMOX_P3_DRIVE_TEST == 0); CHECK(SUMOX_B4_STAND == 0); CHECK(MATCH == 0);
    CHECK(fsm::RobotResult::STOP_TRIAL_PROFILE); CHECK_FALSE(fsm::RobotResult::TURN_TRIAL_PROFILE);
    CHECK_FALSE(fsm::RobotResult::DRIVE_TEST_PROFILE); CHECK_FALSE(fsm::RobotResult::STAND_PROFILE);
    CHECK((DUTY == .30F || DUTY == .40F || DUTY == .50F || DUTY == .60F || DUTY == .70F));
    CHECK(config::STOP_TRIAL_APPROACH_MS == 1000U); CHECK(config::STOP_TRIAL_BRAKE_MS == 500U);
    CHECK(config::SEARCH_DUTY_MAX == .30F);
    const fsm::RobotResult initial; CHECK(initial.stop_trial.phase == Phase::NOT_STARTED);
    CHECK_FALSE(initial.stop_trial.started); CHECK_FALSE(initial.stop_trial.approach_finished);
    CHECK_FALSE(initial.stop_trial.finished); CHECK_FALSE(initial.stop_trial_stopping);
    CHECK_FALSE(initial.stop_trial_edge_interrupted); bounded(initial.stop_trial);
    Rig rig; rig.selectDrive(); rig.releaseSelected(); const auto release = rig.owner.report();
    CHECK(release.robot.menu.request == countdown::Service::DRIVE_TEST);
    CHECK_FALSE(release.robot.menu.request_unavailable); CHECK(release.robot.lifecycle.gate.start_release);
    CHECK(release.robot.stop_trial.phase == Phase::NOT_STARTED); drive_test::disabled(release, rig.port);
}

TEST_CASE("B3 B13 D126 all match selections and other services cannot start the approach") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        Rig rig; rig.prime(); for (unsigned i = 1U; i < mode; ++i) rig.shortMode();
        rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
        const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
        CHECK(later.robot.stop_trial.phase == Phase::NOT_STARTED);
        CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
    }
    for (unsigned item : {0U, 1U, 3U}) {
        Rig rig; rig.prime(); rig.longMode(); for (unsigned i = 0U; i < item; ++i) rig.shortMode();
        rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
        const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
        CHECK(later.robot.stop_trial.phase == Phase::NOT_STARTED);
    }
}

TEST_CASE("B6 B7 D126 GO starts real straight and final electrical duty obeys cap voltage and slew") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) for (float origin : {0.0F, 170.0F}) {
        Rig rig; rig.source.vbat_v = voltage; rig.source.raw_heading_deg = origin;
        const auto go = rig.goDrive(); approach(rig, rig.owner.report(), go);
        CHECK(rig.owner.report().robot.heading.heading_deg == 0.0F);
        CHECK(rig.owner.report().robot.stop_trial.duty_l == DUTY);
        CHECK(rig.owner.report().robot.stop_trial.duty_r == DUTY);
        CHECK_FALSE(rig.owner.report().robot.stop_trial.imu_fallback);
        const auto first = rig.next(); approach(rig, first, go);
        CHECK(first.robot.outputs.duty_l <= .021F); CHECK(first.robot.outputs.duty_r <= .021F);
        const auto full = rig.at(go + 50000U); approach(rig, full, go);
        const float expected = std::min(DUTY, DUTY * 11.1F / voltage);
        CHECK(full.robot.outputs.duty_l == doctest::Approx(expected));
        CHECK(full.robot.outputs.duty_r == doctest::Approx(expected));
    }
}

TEST_CASE("B6 B7 D126 bounded real heading correction precedes compensation and final selected cap") {
    for (float voltage : {9.0F, 11.1F}) for (float yaw : {-20.0F, 20.0F}) {
        Rig rig; rig.source.vbat_v = voltage; const auto go = rig.goDrive(); rig.at(go + 50000U);
        rig.source.raw_heading_deg = yaw; const auto corrected = rig.at(go + 100000U);
        approach(rig, corrected, go); const float adjustment = yaw > 0.0F ? -.25F : .25F;
        CHECK(corrected.robot.stop_trial.duty_l == doctest::Approx(DUTY + adjustment));
        CHECK(corrected.robot.stop_trial.duty_r == doctest::Approx(DUTY - adjustment));
        const float expected_l = std::min(DUTY, (DUTY + adjustment) * 11.1F / voltage);
        const float expected_r = std::min(DUTY, (DUTY - adjustment) * 11.1F / voltage);
        CHECK(corrected.robot.outputs.duty_l == doctest::Approx(expected_l));
        CHECK(corrected.robot.outputs.duty_r == doctest::Approx(expected_r));
        CHECK(corrected.robot.outputs.duty_l > 0.0F); CHECK(corrected.robot.outputs.duty_r > 0.0F);
    }
}

TEST_CASE("B6 D126 trial Governor profile preserves production search cap and immediate reductions") {
    CHECK(static_cast<unsigned>(governor::Profile::SEARCH_FORWARD) == 0U);
    CHECK(static_cast<unsigned>(governor::Profile::EDGE_FORWARD) == 7U);
    CHECK(static_cast<unsigned>(governor::Profile::STOP_TRIAL_FORWARD) == 8U);
    governor::Governor governor; governor::Request request;
    request.profile = governor::Profile::STOP_TRIAL_FORWARD; request.inhibited = false;
    request.vbat_v = 9.0F; request.duty_l = request.duty_r = 1.0F;
    const auto initial = governor.step(0U, request); CHECK(initial.duty_l == 0.0F);
    CHECK(governor.step(1000U, request).duty_l == doctest::Approx(.02F));
    const auto trial = governor.step(50000U, request);
    CHECK(trial.valid); CHECK(trial.duty_l == DUTY); CHECK(trial.duty_r == DUTY);
    request.profile = governor::Profile::SEARCH_FORWARD; const auto search = governor.step(50001U, request);
    CHECK(search.duty_l == .30F); CHECK(search.duty_r == .30F);
    request.profile = governor::Profile::STOP_TRIAL_FORWARD;
    const auto rise = governor.step(51001U, request);
    CHECK(rise.duty_l == doctest::Approx(std::min(DUTY, .32F)));
    request.brake = true; const auto braking = governor.step(51002U, request);
    CHECK(braking.duty_l == 0.0F); CHECK(braking.duty_r == 0.0F);
}

TEST_CASE("B7 D126 no-edge deadline reports DONE timeout then full observed brake and final STOP") {
    for (auto base : {0U, 0xffa00000U}) {
        Rig rig; const auto go = rig.goDrive(base); approach(rig, rig.at(go + 999999U), go);
        brake(rig, rig.at(go + 1000000U), go + 1000000U);
        brake(rig, rig.at(go + 1499999U), go + 1000000U);
        const auto done = rig.at(go + 1500000U); complete(rig, done, go + 1500000U);
        const auto stop = rig.next(1U); CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
        CHECK(stop.robot.outputs.ui_state == core::State::STOPPED); drive_test::disabled(stop, rig.port);
        same(stop.robot.stop_trial, done.robot.stop_trial);
        CHECK_FALSE(stop.robot.stop_trial.fresh); CHECK_FALSE(stop.robot.stop_trial.phase_changed);
    }
}

TEST_CASE("B7 D126 late approach completion starts a full brake at the actual observation") {
    Rig rig; const auto go = rig.goDrive(); const auto observed = go + 2000000U;
    brake(rig, rig.at(observed), observed); brake(rig, rig.at(observed + 499999U), observed);
    complete(rig, rig.at(observed + 500000U), observed + 500000U);
    CHECK(rig.owner.report().robot.stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
}

TEST_CASE("B7 D126 actual IMU loss uses equal requests and recovery resumes captured heading") {
    Rig rig; const auto go = rig.goDrive(); rig.source.raw_heading_deg = 10.0F;
    auto r = rig.at(go + 50000U); approach(rig, r, go);
    CHECK(r.robot.stop_trial.duty_l == doctest::Approx(DUTY - .2F));
    CHECK(r.robot.stop_trial.duty_r == doctest::Approx(DUTY + .2F));
    rig.source.imu_ok = false; rig.source.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
    r = rig.at(go + 100000U); approach(rig, r, go); CHECK(r.robot.stop_trial.imu_fallback);
    CHECK(r.robot.stop_trial.duty_l == DUTY); CHECK(r.robot.stop_trial.duty_r == DUTY);
    rig.source.imu_ok = true; rig.source.raw_heading_deg = 10.0F;
    r = rig.at(go + 150000U); approach(rig, r, go); CHECK_FALSE(r.robot.stop_trial.imu_fallback);
    CHECK(r.robot.stop_trial.duty_l == doctest::Approx(DUTY - .2F));
    CHECK(r.robot.stop_trial.duty_r == doctest::Approx(DUTY + .2F));
    brake(rig, rig.at(go + 1000000U), go + 1000000U);
}

TEST_CASE("B7 D126 missing-at-GO IMU stays real and recovery cannot restart the approach clock") {
    Rig rig; rig.source.imu_ok = false; const auto go = rig.goDrive();
    CHECK(rig.owner.report().robot.stop_trial.imu_fallback);
    rig.source.raw_heading_deg = std::numeric_limits<float>::infinity();
    approach(rig, rig.at(go + 400000U), go);
    rig.source.imu_ok = true; rig.source.raw_heading_deg = 90.0F;
    const auto recovered = rig.at(go + 500000U); approach(rig, recovered, go);
    CHECK_FALSE(recovered.robot.stop_trial.imu_fallback);
    CHECK(recovered.robot.stop_trial.duty_l == DUTY); CHECK(recovered.robot.stop_trial.duty_r == DUTY);
    brake(rig, rig.at(go + 1000000U), go + 1000000U);
}

TEST_CASE("B5 B7 D126 all128 opponent masks remain real but cannot select combat or restart approach") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mask); Rig rig; rig.opponent(mask); rig.source.ax_g = 3.0F; const auto go = rig.goDrive();
        for (unsigned i = 1U; i <= 30U; ++i) {
            const auto r = rig.at(go + i * 1000U); approach(rig, r, go);
            CHECK(r.robot.opponent_mask == mask); CHECK(r.robot.stop_trial.duty_l == DUTY);
            CHECK(r.robot.stop_trial.duty_r == DUTY);
        }
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::CONTACT) == 0U);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::STALL) == 0U);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::REFLANK_PHASE) == 0U);
    }
}

TEST_CASE("B7 D126 presence flags distinguish real zero start completion and finished timestamps") {
    for (auto base : {0U - 6289000U, 0U - 7289000U, 0U - 7789000U}) {
        Rig rig; const auto go = rig.goDrive(base); const auto started = rig.owner.report().robot.stop_trial;
        CHECK(started.started); CHECK(started.started_us == go);
        brake(rig, rig.at(go + 1000000U), go + 1000000U);
        complete(rig, rig.at(go + 1500000U), go + 1500000U);
        CHECK(rig.owner.report().robot.stop_trial.approach_finished);
    }
}

TEST_CASE("B15 D126 recorder keeps actual first nonzero and DRIVE_TEST perception with no fake distance") {
    Rig rig; const auto release = rig.releaseDrive(); const auto go = release + 5100000U;
    const auto first_report = rig.at(go).applied.feedback;
    bool seen = first_report.duty_l != 0.0F || first_report.duty_r != 0.0F;
    std::uint32_t first = seen ? first_report.applied_us : 0U; rig.opponent(2U);
    for (unsigned i = 1U; i <= 50U; ++i) {
        const auto r = rig.at(go + i * 1000U);
        if (!seen && (r.applied.feedback.duty_l != 0.0F || r.applied.feedback.duty_r != 0.0F)) {
            seen = true; first = r.applied.feedback.applied_us;
        }
    }
    rig.at(go + 1000000U); rig.at(go + 1500000U); rig.next(); rig.next();
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK(rig.owner.report().robot.stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
    std::uint32_t logged = 0U;
    CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::FIRST_NONZERO_DUTY, &logged)
        == (MOTORS_ALLOWED ? 1U : 0U));
    if (MOTORS_ALLOWED) { CHECK(seen); CHECK(logged == first); CHECK(first - release >= 5100000U); }
    else { CHECK_FALSE(seen); CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U); }
    bool found = false;
    for (std::size_t i = 0U; i < rig.owner.recording().frames().size(); ++i) {
        recorder::StoredFrame frame; APP_REQUIRE(rig.owner.recording().frames().read(i, frame));
        if (frame.bytes.data[4] == static_cast<unsigned>(core::State::DRIVE_TEST)) {
            CHECK(frame.status != logframe::PackStatus::INVALID); found |= frame.bytes.data[7] == 2U;
        }
    }
    CHECK(found);
}

TEST_CASE("B13 D126 selected and active stopping service is visibly available as D without cross") {
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
