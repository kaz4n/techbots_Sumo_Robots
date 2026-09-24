// Freezes D123 safety expectations without altering any existing locked tests.
// Checks genuine local admission, full hold, edge priority and real applied receipts.
// Dedicated profile1 M0/M1 executions provide host evidence only, never motor authority.
#include "../fixtures/drive_test_fixture.h"
#include "../fixtures/app_service_reset/fixture.h"

using drive_test::Rig;
using drive_test::Button;

TEST_CASE("B3 R1 D123 actual Gate remains low until exact full qualified release hold across wrap") {
    for (auto base : {0U, 0xffd00000U}) {
        Rig rig; rig.selectDrive(base); rig.next(1000U, Button::START);
        rig.next(20000U, Button::START); const auto raw = rig.now + 1000U;
        rig.at(raw); const auto before_release = rig.at(raw + 19999U);
        CHECK_FALSE(before_release.robot.lifecycle.gate.start_release);
        drive_test::disabled(before_release, rig.port);
        const auto release = raw + 20000U; const auto accepted = rig.at(release);
        APP_REQUIRE(accepted.robot.lifecycle.gate.start_release);
        CHECK(accepted.robot.lifecycle.gate.release_us == release);
        for (auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto report = rig.at(release + age);
            CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::HOLDING);
            drive_test::disabled(report, rig.port);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.at(release + 5100000U);
        CHECK(go.robot.lifecycle.gate.go); drive_test::moving(rig, go);
        CHECK(go.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
        drive_test::moving(rig, rig.next());
    }
}

TEST_CASE("B3 R1 D123 boot-held START and unqualified bounce never create a release") {
    Rig boot; boot.at(0U, Button::START); boot.at(20000U, Button::START);
    boot.at(30000U); const auto boot_release = boot.at(50000U);
    CHECK_FALSE(boot_release.robot.lifecycle.gate.start_release);
    drive_test::disabled(boot_release, boot.port);
    Rig rig; rig.selectDrive(); rig.next(1000U, Button::START);
    rig.next(19999U, Button::START); rig.next(); rig.next(20000U);
    CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
    drive_test::disabled(rig.next(6000000U), rig.port);
    rig.releaseSelected(); CHECK(rig.owner.report().robot.lifecycle.gate.start_release);
}

TEST_CASE("B3 R1 D123 MODE cancellation at GO deadline wins and later NONE cannot replay") {
    Rig rig; const auto release = rig.releaseDrive();
    rig.at(release + 5080000U, Button::MODE);
    const auto cancelled = rig.at(release + 5100000U, Button::MODE);
    CHECK_FALSE(cancelled.robot.lifecycle.gate.go);
    CHECK(cancelled.robot.lifecycle.gate.phase == countdown::Phase::IDLE);
    drive_test::disabled(cancelled, rig.port);
    rig.next(); const auto idle = rig.next(6000000U);
    CHECK_FALSE(idle.robot.lifecycle.gate.start_release); CHECK_FALSE(idle.robot.lifecycle.gate.go);
    drive_test::disabled(idle, rig.port);
}

TEST_CASE("B3 B4 D123 raw-only absent line preparation cannot admit selected DRIVE_TEST") {
    Rig rig; rig.source.line.explicit_values = true;
    rig.source.line.use = core::LineUse::CALIBRATION;
    rig.source.line.presence = core::LinePresence::ABSENT;
    rig.source.opponent_fresh = true; rig.selectDrive(); rig.releaseSelected();
    CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
    drive_test::disabled(rig.owner.report(), rig.port);
    const auto later = rig.next(6000000U);
    CHECK_FALSE(later.robot.lifecycle.gate.go); drive_test::disabled(later, rig.port);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
}

TEST_CASE("B3 B15 D123 FIRST_NONZERO records actual Gate receipt once and never prehold") {
    Rig rig; const auto release = rig.releaseDrive(); const auto go = release + 5100000U;
    const auto initial = rig.at(go).applied.feedback;
    bool have_first = initial.duty_l != 0.0F || initial.duty_r != 0.0F;
    std::uint32_t first = have_first ? initial.applied_us : 0U;
    for (unsigned i = 1U; i <= 50U; ++i) {
        const auto report = rig.at(go + i * 1000U); drive_test::moving(rig, report);
        const auto& actual = report.applied.feedback;
        if (!have_first && (actual.duty_l != 0.0F || actual.duty_r != 0.0F)) {
            first = actual.applied_us; have_first = true;
        }
    }
    std::uint32_t logged = 0U;
    CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::START_RELEASE) == 1U);
    CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::GO) == 1U);
    CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::FIRST_NONZERO_DUTY, &logged)
        == (MOTORS_ALLOWED ? 1U : 0U));
    CHECK(have_first == (MOTORS_ALLOWED != 0));
    if (MOTORS_ALLOWED) { CHECK(logged == first); CHECK(first - release >= 5100000U); }
    else { CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U); }
}

TEST_CASE("B4 R5 D123 white at GO preempts DRIVE_TEST including three and all white faults") {
    for (auto mask : {1U, 7U, 15U}) {
        Rig rig; const auto release = rig.releaseDrive(); rig.white(mask);
        const auto report = rig.at(release + 5100000U);
        CHECK(report.robot.lifecycle.gate.go);
        CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        drive_test::noCombat(report.robot); CHECK(report.robot.line_mask == mask);
        if (mask == 1U) {
            CHECK(report.robot.escape_fault == edge::EscapeFault::NONE);
            CHECK(report.robot.outputs.duty_l == 0.0F); CHECK(report.robot.outputs.duty_r == 0.0F);
        } else {
            CHECK(report.robot.escape_fault == edge::EscapeFault::WHITE_PATTERN);
            drive_test::disabled(report, rig.port); rig.white(0U);
            drive_test::disabled(rig.next(1000000U), rig.port);
            CHECK(rig.owner.report().robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        }
    }
}

TEST_CASE("B4 R5 D123 later white always preempts scan and edge keeps its approved duty cap") {
    Rig rig; rig.source.imu_ok = false; const auto go = rig.goDrive(); rig.at(go + 30000U);
    rig.white(1U); const auto entry = rig.next();
    CHECK(entry.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    CHECK(entry.robot.outputs.duty_l == 0.0F); CHECK(entry.robot.outputs.duty_r == 0.0F);
    rig.next(); const auto reverse = rig.next(50000U);
    CHECK(reverse.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    CHECK(reverse.robot.outputs.duty_l < -.30F); CHECK(reverse.robot.outputs.duty_r < -.30F);
    CHECK(std::fabs(reverse.robot.outputs.duty_l) <= .80F);
    CHECK(std::fabs(reverse.robot.outputs.duty_r) <= .80F); drive_test::noCombat(reverse.robot);
}

TEST_CASE("B4 B8 D123 successful escape brakes into DRIVE_TEST then starts fresh search next tick") {
    for (bool edge_at_go : {false, true}) {
        Rig rig; rig.source.imu_ok = false; std::uint32_t began = 0U;
        if (edge_at_go) {
            const auto release = rig.releaseDrive(); rig.white(1U);
            began = release + 5100000U; rig.at(began);
        } else { rig.goDrive(); rig.white(1U); began = rig.now + 1000U; rig.at(began); }
        rig.white(0U); bool exited = false;
        for (unsigned age = 1000U; age <= 2000000U; age += 1000U) {
            const auto report = rig.at(began + age); drive_test::noCombat(report.robot);
            if (report.robot.outputs.ui_state == core::State::EDGE_ESCAPE) continue;
            APP_REQUIRE(report.robot.outputs.ui_state == core::State::DRIVE_TEST);
            CHECK(report.robot.outputs.duty_l == 0.0F); CHECK(report.robot.outputs.duty_r == 0.0F);
            CHECK(report.applied.feedback.duty_l == 0.0F); CHECK(report.applied.feedback.duty_r == 0.0F);
            const auto next = rig.next(); drive_test::moving(rig, next);
            const auto scan = rig.next(25000U); drive_test::moving(rig, scan);
            CHECK(scan.robot.outputs.duty_l * scan.robot.outputs.duty_r < 0.0F);
            exited = true; break;
        }
        CHECK(exited);
    }
}

TEST_CASE("B4 R5 D123 persistent white never exits to search and exhausts bounded replacements") {
    Rig rig; rig.source.imu_ok = false; rig.goDrive(); rig.white(1U); rig.next();
    bool faulted = false;
    for (unsigned i = 0U; i < 2500U; ++i) {
        const auto report = rig.next(); CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        drive_test::noCombat(report.robot);
        if (report.robot.escape_fault != edge::EscapeFault::NONE) {
            drive_test::disabled(report, rig.port); faulted = true; break;
        }
    }
    CHECK(faulted); rig.white(0U); drive_test::disabled(rig.next(), rig.port);
}

TEST_CASE("B4 B5 D123 real centered perception and applied forward retain pushed-out edge context") {
    Rig rig; rig.source.imu_ok = false; const auto go = rig.goDrive(); rig.opponent(2U);
    rig.at(go + 1000U); rig.at(go + 2000U); rig.at(go + 720000U); rig.at(go + 750000U);
    rig.white(8U); const auto edge = rig.next();
    CHECK(edge.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    bool pushed = false;
    for (unsigned i = 0U; i < edge.robot.events.count; ++i)
        if (edge.robot.events.entries[i].type == core::Event::EDGE)
            pushed |= (edge.robot.events.entries[i].detail & logframe::PUSHED_OUT) != 0U;
    CHECK(pushed == (MOTORS_ALLOWED != 0)); drive_test::noCombat(edge.robot);
}

TEST_CASE("B3 B14 D123 local STOP and stale observations immediately inhibit active search") {
    for (bool stale : {false, true}) {
        Rig rig; rig.goDrive(); rig.next(30000U);
        if (stale) rig.source.observations_fresh = false; else rig.source.stop_requested = true;
        const auto stop = rig.next(); CHECK(stop.robot.outputs.ui_state == core::State::STOPPED);
        if (stale) CHECK(stop.robot.contract_faults != 0U);
        drive_test::disabled(stop, rig.port);
        rig.source.observations_fresh = true; rig.source.stop_requested = false;
        rig.next(1000U, Button::START); rig.next(20000U, Button::START);
        rig.next(); drive_test::disabled(rig.next(6000000U), rig.port);
        CHECK(rig.owner.report().robot.outputs.ui_state == core::State::STOPPED);
    }
}

TEST_CASE("B3 D123 qualified BOTH stop honors full debounce and hold during drive") {
    Rig rig; rig.goDrive(); const auto pressed = rig.now + 1000U;
    rig.at(pressed, Button::BOTH); rig.at(pressed + 20000U, Button::BOTH);
    const auto before = rig.at(pressed + 1019999U, Button::BOTH);
    CHECK(before.robot.outputs.ui_state == core::State::DRIVE_TEST);
    const auto stop = rig.at(pressed + 1020000U, Button::BOTH);
    CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    drive_test::disabled(stop, rig.port);
}

TEST_CASE("B14 D123 every initial Gate callback failure produces invalid receipt then stopped Robot") {
    for (unsigned operation = 1U; operation <= 6U; ++operation) {
        CAPTURE(operation); Rig rig; rig.goDrive(); rig.next(30000U);
        rig.port.fail_at = rig.port.operations + operation;
        const auto failed = rig.next(); CHECK(failed.applied.fault == motors::Fault::IO);
        CHECK_FALSE(failed.applied.feedback.applied_valid); app_test::zero(rig.port);
        rig.port.fail_at = 0U; const auto stopped = rig.next();
        CHECK(stopped.robot.contract_faults != 0U);
        CHECK(stopped.robot.outputs.ui_state == core::State::STOPPED);
        drive_test::disabled(stopped, rig.port);
    }
}

TEST_CASE("B14 D123 actual Transaction duplicate decision inhibits without another Robot result") {
    Rig rig; rig.goDrive(); rig.next(30000U); const auto before = rig.owner.report().robot;
    rig.port.now = rig.now; APP_REQUIRE(rig.owner.open());
    rig.source.stop_requested = true; rig.white(15U);
    CHECK_FALSE(rig.owner.decide(rig.source));
    CHECK(rig.owner.report().fault == app::Fault::CLOCK);
    CHECK(rig.owner.report().robot.token == before.token);
    CHECK_FALSE(rig.owner.report().decision_made); app_test::zero(rig.port);
}

TEST_CASE("B3 B4 D123 duplicate Robot observation suppresses changed edge STOP and Gate reapplication") {
    app_test::Port port; motors::MotorGate gate(port.port()); fsm::Robot robot;
    APP_REQUIRE(gate.begin()); auto input = app_test::input();
    auto observe = [&](std::uint32_t time, Button button = Button::NONE) {
        port.now = time; input.t_us = time; input.button = button;
        const auto result = robot.step(input);
        if (result.fresh) input.previous = gate.apply(time, result).feedback;
        return result;
    };
    struct Observation { std::uint32_t time; Button button; };
    const Observation sequence[] = {{0U,Button::NONE},{1000U,Button::NONE},{21000U,Button::NONE},
        {22000U,Button::MODE},{42000U,Button::MODE},{1042000U,Button::MODE},
        {1043000U,Button::NONE},{1063000U,Button::NONE},{1064000U,Button::MODE},
        {1084000U,Button::MODE},{1085000U,Button::NONE},{1105000U,Button::NONE},
        {1106000U,Button::MODE},{1126000U,Button::MODE},{1127000U,Button::NONE},
        {1147000U,Button::NONE},{1148000U,Button::START},{1168000U,Button::START},
        {1169000U,Button::NONE},{1189000U,Button::NONE}};
    for (const auto& sample : sequence) observe(sample.time, sample.button);
    APP_REQUIRE(observe(6289000U).lifecycle.gate.go);
    const auto before = observe(6319000U); APP_REQUIRE(before.outputs.ui_state == core::State::DRIVE_TEST);
    const auto calls = port.count; input.stop_requested = true; input.line_raw_us[0] = 100U;
    const auto duplicate = observe(6319000U); CHECK_FALSE(duplicate.fresh);
    CHECK(duplicate.token == before.token); CHECK(duplicate.events.count == 0U);
    CHECK_FALSE(duplicate.frame_ready); CHECK(port.count == calls);
    CHECK(duplicate.outputs.ui_state == before.outputs.ui_state);
    const auto stopped = observe(6319001U); CHECK(stopped.outputs.ui_state == core::State::STOPPED);
    app_test::zero(port);
}

TEST_CASE("B3 D123 Gate profile allowance cannot bypass independent release hold or full-duty rules") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        app_test::Port port; motors::MotorGate gate(port.port()); APP_REQUIRE(gate.begin());
        fsm::RobotResult release; release.fresh = true; release.token = 1U;
        release.outputs.ui_state = core::State::COUNTDOWN;
        release.lifecycle.gate.phase = countdown::Phase::HOLDING;
        release.lifecycle.gate.start_release = true; release.lifecycle.gate.release_us = 1000U;
        if (scenario != 0U) { port.now = 1000U; APP_REQUIRE(gate.apply(1000U, release).feedback.applied_valid); }
        auto moving = release; moving.token = 2U; moving.outputs.ui_state = core::State::DRIVE_TEST;
        moving.outputs.motors_enabled = true; moving.outputs.duty_l = scenario == 2U ? 1.0F : .3F;
        moving.outputs.duty_r = .3F; moving.lifecycle.gate.start_release = false;
        moving.contact = true; moving.opponent_mask = 7U;
        moving.lifecycle.gate.phase = countdown::Phase::READY; moving.lifecycle.gate.motion_permitted = true;
        const auto time = scenario == 1U ? 5100999U : 5101000U; port.now = time;
        const auto rejected = gate.apply(time, moving);
        CHECK(rejected.fault == motors::Fault::COMMAND); CHECK_FALSE(rejected.feedback.applied_valid);
        CHECK(port.highs == 0U); CHECK(port.nonzero == 0U); app_test::zero(port);
    }
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 B13 D103 D123 genuine service-only reset remains permanently inhibited for DRIVE_TEST") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.reset(false, true));
    APP_REQUIRE(rig.owner.report().service_only); APP_REQUIRE(rig.select(2U));
    CHECK(rig.robot().menu.selection.service == countdown::Service::DRIVE_TEST);
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); bool unavailable = false;
    for (unsigned i = 0U; i < 5150U; ++i) {
        rig.fake.button_raw = service_reset_test::NONE; APP_REQUIRE(rig.next());
        CHECK(rig.owner.report().service_only);
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release); CHECK_FALSE(rig.robot().lifecycle.gate.go);
        CHECK_FALSE(rig.robot().outputs.motors_enabled); CHECK_FALSE(rig.fake.enabled);
        CHECK(rig.fake.highs == 0U); CHECK(rig.fake.nonzero == 0U);
        const auto action = rig.owner.report().service_action;
        unavailable |= action.fresh && action.status == app::ServiceActionStatus::UNAVAILABLE;
    }
    CHECK(unavailable);
}
#endif
