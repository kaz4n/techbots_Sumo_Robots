// Tests D123's public P3 search-only contract through real application owners.
// Derives motion, menu and evidence expectations from B3/B5/B6/B8/B13/B15.
// Independent frozen M0/M1 scenarios precede implementation execution.
#include "fixtures/drive_test_fixture.h"
#include "hal/ui_display.h"
#include <array>

using drive_test::Rig;
using drive_test::Button;

TEST_CASE("B1 B13 D123 immutable profile selects DRIVE_TEST with an available local intent") {
    CHECK(SUMOX_P3_DRIVE_TEST == 1); CHECK(SUMOX_B4_STAND == 0); CHECK(MATCH == 0);
    CHECK(fsm::RobotResult::DRIVE_TEST_PROFILE); CHECK_FALSE(fsm::RobotResult::STAND_PROFILE);
    Rig rig; rig.selectDrive(); const auto release = rig.releaseSelected();
    const auto& result = rig.owner.report().robot;
    CHECK(result.menu.request == countdown::Service::DRIVE_TEST);
    CHECK_FALSE(result.menu.request_unavailable); CHECK(result.lifecycle.gate.start_release);
    CHECK(result.lifecycle.gate.release_us == release);
    CHECK(result.outputs.ui_state == core::State::COUNTDOWN);
    drive_test::disabled(rig.owner.report(), rig.port);
    const auto later = rig.next(); CHECK(later.robot.menu.request == countdown::Service::NONE);
    CHECK_FALSE(later.robot.lifecycle.gate.start_release);
}

TEST_CASE("B3 B13 D123 all six match selections and other services cannot enter countdown") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        Rig rig; rig.prime(); for (unsigned i = 1U; i < mode; ++i) rig.shortMode();
        CHECK(static_cast<unsigned>(rig.owner.report().robot.menu.selection.mode) == mode);
        rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
        drive_test::disabled(rig.next(6000000U), rig.port);
        CHECK(rig.owner.report().robot.outputs.ui_state == core::State::IDLE);
        CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
    }
    for (unsigned item : {0U, 1U, 3U}) {
        Rig rig; rig.prime(); rig.longMode();
        for (unsigned i = 0U; i < item; ++i) rig.shortMode();
        rig.releaseSelected(); const auto request = rig.owner.report().robot;
        CHECK(request.menu.request != countdown::Service::NONE);
        CHECK(request.menu.request != countdown::Service::DRIVE_TEST);
        CHECK_FALSE(request.lifecycle.gate.start_release);
        drive_test::disabled(rig.next(6000000U), rig.port);
        CHECK(rig.owner.report().robot.outputs.ui_state == core::State::IDLE);
    }
}

TEST_CASE("B3 B13 D123 selecting service never replays a previously suppressed release") {
    Rig rig; rig.prime(); rig.releaseSelected();
    CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
    rig.next(20000U); rig.longMode(); rig.shortMode(); rig.shortMode();
    CHECK(rig.owner.report().robot.menu.selection.service == countdown::Service::DRIVE_TEST);
    const auto idle = rig.next(6000000U); CHECK_FALSE(idle.robot.lifecycle.gate.go);
    CHECK_FALSE(idle.robot.lifecycle.gate.start_release); drive_test::disabled(idle, rig.port);
    rig.releaseSelected(); CHECK(rig.owner.report().robot.lifecycle.gate.start_release);
}

TEST_CASE("B5 B8 D123 all 128 opponent masks remain real but cannot select combat") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mask); Rig rig; const auto go = rig.goDrive();
        rig.opponent(mask); rig.source.ax_g = 2.0F; rig.source.ay_g = 2.0F;
        for (unsigned tick = 1U; tick <= 30U; ++tick) {
            const auto report = rig.at(go + tick * 1000U); drive_test::moving(rig, report);
        }
        CHECK(rig.owner.report().robot.opponent_mask == mask);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::CONTACT) == 0U);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::STALL) == 0U);
        CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::REFLANK_PHASE) == 0U);
    }
}

TEST_CASE("B8 D123 opponents cannot restart full directed scan or suppress alternating advance") {
    Rig rig; const auto go = rig.goDrive(); rig.opponent(7U); rig.source.ax_g = 3.0F;
    for (unsigned step = 1U; step <= 4U; ++step) {
        rig.source.raw_heading_deg = static_cast<float>(step * 89U);
        const auto report = rig.at(go + step * 25000U); drive_test::moving(rig, report);
        CHECK(report.robot.outputs.duty_l > 0.0F); CHECK(report.robot.outputs.duty_r < 0.0F);
    }
    rig.source.raw_heading_deg = 360.0F; rig.at(go + 101000U);
    const auto forward = rig.at(go + 121000U); drive_test::moving(rig, forward);
    CHECK(forward.robot.outputs.duty_l > 0.0F); CHECK(forward.robot.outputs.duty_r > 0.0F);
    CHECK(forward.robot.outputs.duty_l <= .30F); CHECK(forward.robot.outputs.duty_r <= .30F);
    rig.opponent(127U); rig.at(go + 401000U);
    const auto left = rig.at(go + 426000U); drive_test::moving(rig, left);
    CHECK(left.robot.outputs.duty_l < 0.0F); CHECK(left.robot.outputs.duty_r > 0.0F);
    rig.source.raw_heading_deg = 0.0F; rig.at(go + 427000U);
    const auto second = rig.at(go + 447000U); drive_test::moving(rig, second);
    CHECK(second.robot.outputs.duty_l > 0.0F); CHECK(second.robot.outputs.duty_r > 0.0F);
}

TEST_CASE("B6 B8 D123 timed full scan retains pivot duty and low voltage final forward cap") {
    for (float voltage : {9.0F, 11.1F}) {
        Rig rig; rig.source.imu_ok = false; rig.source.vbat_v = voltage;
        const auto go = rig.goDrive(); rig.opponent(2U);
        const auto pivot = rig.at(go + 40000U); drive_test::moving(rig, pivot);
        CHECK(pivot.robot.outputs.duty_l > .30F); CHECK(pivot.robot.outputs.duty_r < -.30F);
        CHECK(std::fabs(pivot.robot.outputs.duty_l) <= .80F);
        const auto before = rig.at(go + 719999U); drive_test::moving(rig, before);
        CHECK(before.robot.outputs.duty_l > 0.0F); CHECK(before.robot.outputs.duty_r < 0.0F);
        rig.at(go + 720000U); const auto advance = rig.at(go + 740000U);
        drive_test::moving(rig, advance);
        CHECK(advance.robot.outputs.duty_l == doctest::Approx(.30F));
        CHECK(advance.robot.outputs.duty_r == doctest::Approx(.30F));
        rig.at(go + 1020000U); const auto opposite = rig.at(go + 1045000U);
        drive_test::moving(rig, opposite);
        CHECK(opposite.robot.outputs.duty_l < -.30F); CHECK(opposite.robot.outputs.duty_r > .30F);
    }
}

TEST_CASE("B8 D123 IMU recovery cannot restart latched remaining scan fallback") {
    Rig rig; const auto go = rig.goDrive(); rig.source.raw_heading_deg = 90.0F;
    rig.at(go + 100000U); rig.source.imu_ok = false; rig.at(go + 101000U);
    rig.source.imu_ok = true; rig.source.raw_heading_deg = 100.0F;
    rig.at(go + 200000U); const auto before = rig.at(go + 640999U);
    CHECK(before.robot.outputs.duty_r < 0.0F);
    rig.at(go + 641000U); const auto advance = rig.at(go + 661000U);
    drive_test::moving(rig, advance);
    CHECK(advance.robot.outputs.duty_l > 0.0F); CHECK(advance.robot.outputs.duty_r > 0.0F);
}

TEST_CASE("B5 B8 D123 recent left memory creates captured turn before left scan") {
    Rig rig; const auto release = rig.releaseDrive(); rig.opponent(8U);
    rig.at(release + 5098000U); rig.at(release + 5099000U);
    const auto go = release + 5100000U; rig.at(go);
    rig.opponent(16U); const auto turn = rig.at(go + 40000U); drive_test::moving(rig, turn);
    CHECK(turn.robot.outputs.duty_l == doctest::Approx(-.80F));
    CHECK(turn.robot.outputs.duty_r == doctest::Approx(.80F));
    rig.source.raw_heading_deg = -90.0F; const auto scan = rig.at(go + 41000U);
    drive_test::moving(rig, scan);
    CHECK(scan.robot.outputs.duty_l == doctest::Approx(-.45F));
    CHECK(scan.robot.outputs.duty_r == doctest::Approx(.45F));
}

TEST_CASE("B5 B15 D123 stuck evidence remains real and frames identify DRIVE_TEST and opponent") {
    Rig rig; const auto go = rig.goDrive(); rig.opponent(2U);
    for (unsigned tick = 1U; tick <= 5105U; ++tick) {
        rig.source.raw_heading_deg = static_cast<float>(tick) * .1F;
        drive_test::moving(rig, rig.at(go + tick * 1000U));
    }
    CHECK((rig.owner.report().robot.opponent_fault_mask & 2U) != 0U);
    CHECK((rig.owner.report().robot.opponent_mask & 2U) == 0U);
    bool observed_real_mask = false;
    for (std::size_t i = 0U; i < rig.owner.recording().frames().size(); ++i) {
        recorder::StoredFrame frame; APP_REQUIRE(rig.owner.recording().frames().read(i, frame));
        if (frame.bytes.data[4] != static_cast<unsigned>(core::State::DRIVE_TEST)) continue;
        observed_real_mask |= frame.bytes.data[7] == 2U;
        CHECK(frame.bytes.data[5] == static_cast<unsigned>(core::Mode::SIDESTEP_R));
        CHECK(frame.status != logframe::PackStatus::INVALID);
    }
    CHECK(observed_real_mask);
}

TEST_CASE("B4 B8 D123 fresh search preserves real inward heading after a successful escape") {
    Rig rig; rig.goDrive(); rig.white(8U); const auto began = rig.now + 1000U; rig.at(began);
    rig.white(0U); bool exited = false;
    for (unsigned age = 1000U; age <= 500000U; age += 1000U) {
        const auto report = rig.at(began + age);
        if (report.robot.outputs.ui_state != core::State::DRIVE_TEST) continue;
        CHECK(report.robot.outputs.duty_l == 0.0F); CHECK(report.robot.outputs.duty_r == 0.0F);
        exited = true; break;
    }
    APP_REQUIRE(exited); rig.next(); rig.source.raw_heading_deg = 370.0F;
    rig.next(40000U); const auto advance = rig.next(25000U); drive_test::moving(rig, advance);
    CHECK(advance.robot.outputs.duty_l >= 0.0F); CHECK(advance.robot.outputs.duty_r > 0.0F);
    CHECK(advance.robot.outputs.duty_l < advance.robot.outputs.duty_r);
    CHECK(advance.robot.outputs.duty_l <= .30F); CHECK(advance.robot.outputs.duty_r <= .30F);
}

TEST_CASE("B13 D123 selected and active DRIVE_TEST show D with blank available icon") {
    for (auto state : {core::State::IDLE, core::State::DRIVE_TEST}) {
        ui::DisplaySample sample; sample.state = state; sample.service_menu = true;
        sample.service = countdown::Service::DRIVE_TEST; ui::Frame frame;
        APP_REQUIRE(ui::render(sample, frame) == ui::RenderStatus::OK);
        constexpr unsigned D[] = {6U, 5U, 5U, 5U, 6U};
        for (unsigned y = 0U; y < 5U; ++y) {
            for (unsigned x = 0U; x < 3U; ++x)
                CHECK(frame.pixels[(y + 1U) * 13U + x] == ((D[y] & (4U >> x)) ? 7U : 0U));
            for (unsigned x = 4U; x < 9U; ++x) CHECK(frame.pixels[(y + 1U) * 13U + x] == 0U);
        }
    }
    ui::DisplaySample sample; sample.state = core::State::IDLE; sample.service_menu = true;
    sample.service = countdown::Service::DRIVE_TEST; sample.service_unavailable = true;
    ui::Frame frame; APP_REQUIRE(ui::render(sample, frame) == ui::RenderStatus::OK);
    constexpr unsigned CROSS[] = {17U, 10U, 4U, 10U, 17U};
    for (unsigned y = 0U; y < 5U; ++y) for (unsigned x = 0U; x < 5U; ++x)
        CHECK(frame.pixels[(y + 1U) * 13U + x + 4U] == ((CROSS[y] & (16U >> x)) ? 7U : 0U));
}
