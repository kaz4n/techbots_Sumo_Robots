// Establishes new D120 safety expectations without changing prior locked tests.
// Exercises actual MotorGate callbacks and receipts with independently timed inputs.
// Dedicated profile1 M0/M1 targets prove hold, preemption and immediate inhibition.
#include "../fixtures/app_transaction_fixture.h"
#include "core/stand_sequence.h"
#include <cmath>

namespace {
using stand_sequence::Phase;
using stand_sequence::Reason;
void white(app_test::Rig& rig, std::uint8_t mask) {
    for (unsigned i = 0U; i < 4U; ++i) rig.source.line_raw_us[i] = mask & (1U << i) ? 100U : 1000U;
}
void disabled(const app::TransactionReport& report, const app_test::Port& port) {
    CHECK_FALSE(report.robot.outputs.motors_enabled);
    CHECK(report.robot.outputs.duty_l == 0.0F); CHECK(report.robot.outputs.duty_r == 0.0F);
    CHECK_FALSE(report.applied.feedback.motors_enabled);
    CHECK(report.applied.feedback.duty_l == 0.0F); CHECK(report.applied.feedback.duty_r == 0.0F);
    app_test::zero(port);
}
void advance(app_test::Rig& rig, std::uint32_t go, std::uint32_t end) {
    for (std::uint32_t age = 1000U; age <= end; age += 1000U) rig.tick(go + age);
}
struct ActualRobot {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    ActualRobot() { APP_REQUIRE(gate.begin()); }
    fsm::RobotResult tick(std::uint32_t time, core::ButtonLevel button = core::ButtonLevel::NONE) {
        port.now = time; input.t_us = time; input.button = button;
        const auto report = robot.step(input);
        if (report.fresh) input.previous = gate.apply(time, report).feedback;
        return report;
    }
    std::uint32_t go() {
        tick(0U); tick(1000U); tick(21000U); tick(22000U, core::ButtonLevel::START);
        tick(42000U, core::ButtonLevel::START); tick(43000U); tick(63000U);
        tick(1563000U); tick(1564000U); tick(4563000U); tick(5162999U);
        APP_REQUIRE(tick(5163000U).lifecycle.gate.go); return 5163000U;
    }
};
}

TEST_CASE("B3 R1 D120 actual Gate stays low through full qualified hold including adjacent wrap ticks") {
    for (const auto base : {0U, 0xfff00000U}) {
        app_test::Rig rig; const auto release = rig.release(base); rig.port.clear();
        for (const auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto report = rig.tick(release + age);
            CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::HOLDING);
            CHECK(report.robot.stand.phase == Phase::NOT_STARTED); disabled(report, rig.port);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.tick(release + 5100000U);
        CHECK(go.robot.lifecycle.gate.go); CHECK(go.robot.stand.phase == Phase::DRIVE);
        CHECK(go.robot.stand.segment == 0U);
        CHECK(go.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
    }
}

TEST_CASE("B3 R1 D120 boot-held START and cancelled countdown cannot start the sequence") {
    app_test::Rig rig;
    rig.tick(0U, core::ButtonLevel::START); rig.tick(20000U, core::ButtonLevel::START);
    rig.tick(30000U); const auto boot_release = rig.tick(50000U);
    CHECK_FALSE(boot_release.robot.lifecycle.gate.start_release);
    CHECK(boot_release.robot.stand.phase == Phase::NOT_STARTED); disabled(boot_release, rig.port);
    app_test::Rig cancelled; const auto release = cancelled.release();
    cancelled.tick(release + 1000U, core::ButtonLevel::MODE);
    const auto stopped = cancelled.tick(release + 21000U, core::ButtonLevel::MODE);
    CHECK(stopped.robot.lifecycle.gate.phase == countdown::Phase::IDLE);
    CHECK(stopped.robot.stand.phase == Phase::NOT_STARTED); disabled(stopped, cancelled.port);
}

TEST_CASE("B3 D120 qualified logical STOP wins exactly at natural completion") {
    app_test::Rig rig; const auto go = rig.go();
    for (std::uint32_t age = 1000U; age <= 6000000U; age += 1000U) {
        rig.tick(go + age, age >= 4980000U ? core::ButtonLevel::BOTH : core::ButtonLevel::NONE);
    }
    const auto report = rig.owner.report();
    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(report.robot.stand.phase == Phase::INTERRUPTED);
    CHECK(report.robot.stand.reason == Reason::STOP); CHECK(report.robot.stand.segment == 11U);
    disabled(report, rig.port);
}

TEST_CASE("B3 D120 local STOP immediately inhibits every segment and cannot restart") {
    for (unsigned row = 0U; row < 12U; ++row) {
        app_test::Rig rig; const auto go = rig.go(); advance(rig, go, row * 500000U);
        rig.source.stop_requested = true;
        const auto report = rig.tick(go + row * 500000U + 1000U);
        CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
        CHECK(report.robot.stand.phase == Phase::INTERRUPTED);
        CHECK(report.robot.stand.reason == Reason::STOP); CHECK(report.robot.stand.segment == row);
        disabled(report, rig.port); rig.source.stop_requested = false;
        const auto later = rig.tick(go + row * 500000U + 2000U, core::ButtonLevel::START);
        CHECK(later.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
        CHECK_FALSE(later.robot.stand.fresh); CHECK_FALSE(later.robot.stand.phase_changed);
        disabled(later, rig.port);
    }
}

TEST_CASE("B4 R5 D120 edge at GO prevents start and faults never auto-stop active escape") {
    for (const auto mask : {1U, 15U}) {
        app_test::Rig rig; const auto release = rig.release(); white(rig, static_cast<std::uint8_t>(mask));
        const auto go = rig.tick(release + 5100000U);
        CHECK(go.robot.lifecycle.gate.go); CHECK(go.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK(go.robot.stand.phase == Phase::NOT_STARTED); CHECK_FALSE(go.robot.stand_stopping);
        if (mask == 15U) {
            CHECK(go.robot.escape_fault == edge::EscapeFault::WHITE_PATTERN); disabled(go, rig.port);
            const auto later = rig.tick(release + 5600000U);
            CHECK(later.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK(later.robot.lifecycle.gate.phase == countdown::Phase::READY);
            CHECK_FALSE(later.robot.stand_stopping); disabled(later, rig.port);
        }
    }
}

TEST_CASE("B4 R5 D120 edge wins natural final boundary and otherwise fatal sequence gap") {
    for (const bool final_boundary : {false, true}) {
        app_test::Rig rig; const auto go = rig.go();
        if (final_boundary) advance(rig, go, 5999000U);
        white(rig, 1U);
        const auto report = rig.tick(go + (final_boundary ? 6000000U : 500000U));
        CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK(report.robot.stand.phase == Phase::INTERRUPTED);
        CHECK(report.robot.stand.reason == Reason::EDGE);
        CHECK(report.robot.stand.segment == (final_boundary ? 11U : 0U));
        CHECK(report.robot.contract_faults == 0U); CHECK_FALSE(report.robot.stand_stopping);
    }
}

TEST_CASE("B4 R5 D120 completed escape inhibits on exit and actual STOP follows next tick") {
    for (const bool edge_at_go : {false, true}) {
        app_test::Rig rig; rig.source.imu_ok = false; std::uint32_t began = 0U;
        if (edge_at_go) {
            const auto release = rig.release(); white(rig, 1U); began = release + 5100000U;
            rig.tick(began);
        } else {
            const auto go = rig.go(); white(rig, 1U); began = go + 1000U; rig.tick(began);
        }
        white(rig, 0U); bool exited = false; bool exceeded_stand = false;
        for (std::uint32_t age = 1000U; age <= 2000000U; age += 1000U) {
            const auto report = rig.tick(began + age);
            CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK_FALSE(report.robot.stand.fresh); CHECK_FALSE(report.robot.stand.phase_changed);
            exceeded_stand |= std::fabs(report.robot.outputs.duty_l) > .25F;
            if (!report.robot.stand_stopping) continue;
            disabled(report, rig.port); CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
            const auto stop = rig.tick(began + age + 1000U);
            CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
            CHECK(stop.robot.outputs.ui_state == core::State::STOPPED); disabled(stop, rig.port);
            CHECK(stop.robot.stand.phase == (edge_at_go ? Phase::NOT_STARTED : Phase::INTERRUPTED));
            exited = true; break;
        }
        CHECK(exceeded_stand); CHECK(exited);
    }
}

TEST_CASE("B14 D120 source loss and actual failed MotorGate receipt cancel active sequence") {
    for (const bool failed_receipt : {false, true}) {
        app_test::Rig rig; const auto go = rig.go();
        if (failed_receipt) {
            rig.port.fail_at = rig.port.operations + 1U;
            const auto failure = rig.tick(go + 1000U);
            CHECK_FALSE(failure.applied.feedback.applied_valid);
            CHECK(failure.applied.fault == motors::Fault::IO);
            rig.port.fail_at = 0U;
        } else rig.source.observations_fresh = false;
        const auto report = rig.tick(go + 2000U);
        CHECK(report.robot.contract_faults != 0U); CHECK(report.robot.outputs.ui_state == core::State::STOPPED);
        CHECK(report.robot.stand.phase == Phase::INTERRUPTED); CHECK(report.robot.stand.reason == Reason::STOP);
        disabled(report, rig.port);
    }
}

TEST_CASE("B14 D120 sequence gap fault immediately inhibits then requests real Lifecycle STOP") {
    app_test::Rig rig; const auto go = rig.go(); const auto fault = rig.tick(go + 500000U);
    CHECK(fault.robot.stand.phase == Phase::FAULT); CHECK(fault.robot.stand.reason == Reason::CLOCK_GAP);
    CHECK((fault.robot.contract_faults & fsm::SCRIPT_RESULT) != 0U);
    CHECK(fault.robot.stand_stopping); CHECK(fault.robot.outputs.ui_state == core::State::STOPPED);
    disabled(fault, rig.port);
    const auto stop = rig.tick(go + 500001U);
    CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(stop.robot.stand.reason == Reason::CLOCK_GAP); CHECK_FALSE(stop.robot.stand.fresh);
    disabled(stop, rig.port);
}

TEST_CASE("B3 D120 duplicate real Robot observation ignores changed STOP and edge without reapplication") {
    ActualRobot rig; const auto go = rig.go(); const auto before = rig.tick(go + 1000U);
    const auto calls = rig.port.count; rig.input.stop_requested = true;
    rig.input.line_raw_us[0] = 100U; const auto duplicate = rig.tick(go + 1000U);
    CHECK_FALSE(duplicate.fresh); CHECK(duplicate.token == before.token); CHECK(rig.port.count == calls);
    CHECK(duplicate.stand.phase == before.stand.phase); CHECK_FALSE(duplicate.stand.fresh);
    CHECK_FALSE(duplicate.stand.phase_changed); CHECK(duplicate.events.count == 0U);
    const auto stop = rig.tick(go + 1001U);
    CHECK(stop.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(stop.stand.reason == Reason::STOP); CHECK_FALSE(rig.port.enabled);
}
