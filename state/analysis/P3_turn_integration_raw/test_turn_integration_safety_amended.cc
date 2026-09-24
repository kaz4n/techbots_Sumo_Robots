// Freezes new D125 safety cases without changing any accepted locked oracle.
// Drives genuine local selection and actual Gate callbacks across hold and preemption.
// Host M0/M1 and configured Runtime checks establish no physical run authority.
#include "../fixtures/turn_integration_fixture.h"
#include <limits>

using namespace turn_integration;

TEST_CASE("B3 R1 D125 full release debounce and 5100ms hold inhibit actual Gate across wrap") {
    for (auto base : {0U, 0xffd00000U}) {
        Rig rig; rig.selectDrive(base); rig.next(1000U, Button::START); rig.next(20000U, Button::START);
        const auto raw = rig.now + 1000U; rig.at(raw);
        const auto before = rig.at(raw + 19999U); CHECK_FALSE(before.robot.lifecycle.gate.start_release);
        drive_test::disabled(before, rig.port); const auto release = raw + 20000U;
        APP_REQUIRE(rig.at(release).robot.lifecycle.gate.start_release);
        for (auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto report = rig.at(release + age); drive_test::disabled(report, rig.port);
            CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::HOLDING);
            CHECK(report.robot.turn_trial.phase == Phase::NOT_STARTED);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.at(release + 5100000U); APP_REQUIRE(go.robot.lifecycle.gate.go);
        running(rig, go); CHECK(go.robot.turn_trial.phase == Phase::TURN);
        CHECK(go.robot.turn_trial.started_us == release + 5100000U);
    }
}

TEST_CASE("B3 R1 D125 boot-held START and MODE cancellation cannot launch or replay a trial") {
    Rig boot; boot.at(0U, Button::START); boot.at(20000U, Button::START);
    boot.at(30000U); const auto released = boot.at(50000U);
    CHECK_FALSE(released.robot.lifecycle.gate.start_release); drive_test::disabled(released, boot.port);
    CHECK(released.robot.turn_trial.phase == Phase::NOT_STARTED);
    Rig rig; const auto release = rig.releaseDrive(); rig.at(release + 5080000U, Button::MODE);
    const auto cancelled = rig.at(release + 5100000U, Button::MODE);
    CHECK_FALSE(cancelled.robot.lifecycle.gate.go); drive_test::disabled(cancelled, rig.port);
    CHECK(cancelled.robot.turn_trial.phase == Phase::NOT_STARTED);
    rig.next(); const auto idle = rig.next(6000000U);
    CHECK_FALSE(idle.robot.lifecycle.gate.start_release); CHECK_FALSE(idle.robot.lifecycle.gate.go);
    drive_test::disabled(idle, rig.port);
}

TEST_CASE("B3 B4 D125 selected service cannot bypass raw-only absent line readiness") {
    Rig rig; rig.source.line.explicit_values = true;
    rig.source.line.use = core::LineUse::CALIBRATION; rig.source.line.presence = core::LinePresence::ABSENT;
    rig.source.opponent_fresh = true; rig.selectDrive(); rig.releaseSelected();
    CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
    const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
    CHECK_FALSE(later.robot.lifecycle.gate.go); CHECK(later.robot.turn_trial.phase == Phase::NOT_STARTED);
}

TEST_CASE("B6 B7 D125 actual Gate applies pivot PWM after LOW and settle with truthful quantization") {
    Rig rig; rig.source.vbat_v = 9.0F; const auto go = rig.goDrive(); rig.port.clear(go);
    const auto report = rig.at(go + 40000U); running(rig, report);
    CHECK(report.robot.outputs.duty_l == SIGN * .8F); CHECK(report.robot.outputs.duty_r == -SIGN * .8F);
    const std::uint32_t right[] = {800U, 0U, 0U, 52428U};
    const std::uint32_t left[] = {0U, 797U, 200U, 0U};
    for (unsigned i = 0U; i < 4U; ++i)
        CHECK(rig.port.pulses[i] == (MOTORS_ALLOWED ? (SIGN > 0.0F ? right[i] : left[i]) : 0U));
    unsigned operation = 0U;
    for (unsigned i = 0U; i < rig.port.count; ++i) {
        APP_REQUIRE(i < rig.port.calls.size()); const auto& call = rig.port.calls[i];
        if (call.kind == app_test::Kind::CLOCK) continue;
        if (operation == 0U) { CHECK(call.kind == app_test::Kind::ENABLE); CHECK_FALSE(call.high); }
        else if (operation <= 4U) { CHECK(call.kind == app_test::Kind::PWM); CHECK(call.channel == operation - 1U); }
        else if (operation == 5U) CHECK(call.kind == app_test::Kind::SETTLE);
        else { CHECK(call.kind == app_test::Kind::ENABLE); CHECK(call.high); CHECK(MOTORS_ALLOWED == 1); }
        ++operation;
    }
    CHECK(operation == (MOTORS_ALLOWED ? 7U : 6U));
    const auto& actual = report.applied.feedback;
    const float expected_l = SIGN > 0.0F ? 800.0F / 1000.0F : -797.0F / 997.0F;
    const float expected_r = SIGN > 0.0F ? -52428.0F / 65535.0F : 200.0F / 251.0F;
    CHECK(actual.duty_l == (MOTORS_ALLOWED ? expected_l : 0.0F));
    CHECK(actual.duty_r == (MOTORS_ALLOWED ? expected_r : 0.0F));
}

TEST_CASE("B3 B7 D125 natural complete cannot repeat and final stopped recording seals") {
    Rig rig; const auto go = rig.goDrive(); rig.source.raw_heading_deg = ANGLE;
    const auto began = go + 1000U; rig.at(began); const auto done = rig.at(began + 500000U);
    completed(rig, done, motion::Status::DONE, began + 500000U);
    const auto stop = rig.next(); CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    drive_test::disabled(stop, rig.port); rig.next();
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    rig.next(1000U, Button::START); rig.next(20000U, Button::START); rig.next();
    const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
    CHECK(later.robot.outputs.ui_state == core::State::STOPPED);
    sameTrial(later.robot.turn_trial, done.robot.turn_trial);
    CHECK_FALSE(later.robot.turn_trial.fresh); CHECK_FALSE(later.robot.turn_trial.phase_changed);
    CHECK(later.robot.turn_trial_stopping);
}

TEST_CASE("B4 R5 D125 edge at GO prevents trial start and three or all white stays fault-inhibited") {
    for (unsigned mask : {1U, 7U, 15U}) {
        Rig rig; const auto release = rig.releaseDrive(); rig.white(mask);
        const auto report = rig.at(release + 5100000U);
        CHECK(report.robot.lifecycle.gate.go); CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK(report.robot.turn_trial.phase == Phase::NOT_STARTED);
        CHECK(report.robot.turn_trial_edge_interrupted); CHECK_FALSE(report.robot.turn_trial_stopping);
        drive_test::noCombat(report.robot);
        if (mask != 1U) {
            CHECK(report.robot.escape_fault == edge::EscapeFault::WHITE_PATTERN);
            drive_test::disabled(report, rig.port); rig.white(0U);
            const auto later = rig.next(1000000U); drive_test::disabled(later, rig.port);
            CHECK(later.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK(later.robot.turn_trial.phase == Phase::NOT_STARTED);
        }
    }
}

TEST_CASE("B4 R5 D125 edge during TURN or BRAKE permanently cancels before full escape and STOP") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        Rig rig; rig.source.imu_ok = false; std::uint32_t edge_time = 0U;
        if (stage == 0U) {
            const auto release = rig.releaseDrive(); rig.white(1U);
            edge_time = release + 5100000U; rig.at(edge_time);
        } else {
            const auto go = rig.goDrive();
            if (stage == 2U) rig.at(go + FALLBACK_US);
            rig.white(1U); edge_time = rig.now + 1000U; rig.at(edge_time);
        }
        const auto interrupted = rig.owner.report().robot.turn_trial;
        CHECK(interrupted.phase == (stage == 0U ? Phase::NOT_STARTED : Phase::INTERRUPTED));
        if (stage != 0U) { CHECK(interrupted.reason == Reason::EDGE); CHECK(interrupted.finished_us == edge_time); }
        rig.white(0U); bool exited = false, escape_moved = false;
        for (std::uint32_t age = 1000U; age <= 2000000U; age += 1000U) {
            const auto report = rig.at(edge_time + age); sameTrial(report.robot.turn_trial, interrupted);
            CHECK(report.robot.turn_trial_edge_interrupted); drive_test::noCombat(report.robot);
            escape_moved |= std::fabs(report.robot.outputs.duty_l) > .3F;
            if (!report.robot.turn_trial_stopping) { CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE); continue; }
            drive_test::disabled(report, rig.port); const auto stopped = rig.next();
            CHECK(stopped.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
            CHECK(stopped.robot.outputs.ui_state == core::State::STOPPED); drive_test::disabled(stopped, rig.port);
            sameTrial(stopped.robot.turn_trial, interrupted); exited = true; break;
        }
        CHECK(escape_moved); CHECK(exited);
    }
}

TEST_CASE("B4 R5 D125 white at brake completion wins over natural COMPLETE") {
    Rig rig; const auto go = rig.goDrive(); rig.source.raw_heading_deg = ANGLE;
    const auto entered = go + 1000U; rig.at(entered); rig.white(1U);
    const auto edge = rig.at(entered + 500000U);
    CHECK(edge.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    CHECK(edge.robot.turn_trial.phase == Phase::INTERRUPTED); CHECK(edge.robot.turn_trial.reason == Reason::EDGE);
    CHECK(edge.robot.turn_trial.turn_status == motion::Status::DONE);
    CHECK(edge.robot.turn_trial.turn_finished_us == entered); CHECK_FALSE(edge.robot.turn_trial_stopping);
}

TEST_CASE("B4 R5 D125 persistent edge exhausts recovery while retaining interrupted trial evidence") {
    Rig rig; rig.source.imu_ok = false; rig.goDrive(); rig.white(1U); rig.next();
    const auto interrupted = rig.owner.report().robot.turn_trial; bool faulted = false;
    for (unsigned i = 0U; i < 2500U; ++i) {
        const auto report = rig.next(); sameTrial(report.robot.turn_trial, interrupted);
        CHECK(report.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK(report.robot.turn_trial_edge_interrupted); CHECK_FALSE(report.robot.turn_trial_stopping);
        if (report.robot.escape_fault == edge::EscapeFault::NONE) continue;
        drive_test::disabled(report, rig.port); faulted = true; break;
    }
    CHECK(faulted); rig.white(0U); drive_test::disabled(rig.next(), rig.port);
    CHECK(rig.owner.report().robot.outputs.ui_state == core::State::EDGE_ESCAPE);
}

TEST_CASE("B3 B4 D125 local STOP wins concurrent edge during TURN BRAKE and GO") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        Rig rig; std::uint32_t when = 0U;
        if (stage == 0U) when = rig.releaseDrive() + 5100000U;
        else {
            const auto go = rig.goDrive();
            if (stage == 2U) { rig.source.raw_heading_deg = ANGLE; rig.at(go + 1000U); }
            when = rig.now + 1000U;
        }
        rig.source.stop_requested = true; rig.white(15U); const auto stop = rig.at(when);
        CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
        CHECK(stop.robot.outputs.ui_state == core::State::STOPPED); drive_test::disabled(stop, rig.port);
        CHECK(stop.robot.turn_trial.phase == (stage == 0U ? Phase::NOT_STARTED : Phase::INTERRUPTED));
        if (stage != 0U) { CHECK(stop.robot.turn_trial.reason == Reason::STOP);
            CHECK(stop.robot.turn_trial.finished_us == when); }
    }
}

TEST_CASE("B14 D125 stale sources invalid battery and healthy invalid heading inhibit and cancel") {
    for (unsigned fault = 0U; fault < 3U; ++fault) {
        Rig rig; rig.goDrive(); rig.next(30000U);
        if (fault == 0U) rig.source.observations_fresh = false;
        if (fault == 1U) rig.source.vbat_v = std::numeric_limits<float>::quiet_NaN();
        if (fault == 2U) rig.source.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        const auto stopped = rig.next(); CHECK(stopped.robot.contract_faults != 0U);
        CHECK(stopped.robot.outputs.ui_state == core::State::STOPPED); drive_test::disabled(stopped, rig.port);
        CHECK(stopped.robot.turn_trial.phase == Phase::INTERRUPTED);
        CHECK(stopped.robot.turn_trial.reason == Reason::STOP);
    }
}

TEST_CASE("B3 D125 actual logical BOTH retains full qualified hold and cancels an active brake") {
    Rig rig; const auto go = rig.goDrive(); const auto pressed = go + 1000U;
    rig.at(pressed, Button::BOTH); rig.at(pressed + 20000U, Button::BOTH);
    rig.at(go + 700000U, Button::BOTH);
    const auto before = rig.at(pressed + 1019999U, Button::BOTH);
    CHECK(before.robot.turn_trial.phase == Phase::BRAKE);
    CHECK(before.robot.lifecycle.gate.phase == countdown::Phase::READY);
    const auto stop = rig.at(pressed + 1020000U, Button::BOTH);
    CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(stop.robot.turn_trial.phase == Phase::INTERRUPTED); CHECK(stop.robot.turn_trial.reason == Reason::STOP);
    CHECK(stop.robot.turn_trial.turn_status == motion::Status::TIMED_OUT); drive_test::disabled(stop, rig.port);
}

TEST_CASE("B14 D125 failed actual Gate callbacks stay invalid and next receipt cancels the turn") {
    for (unsigned operation = 1U; operation <= 6U; ++operation) {
        Rig rig; rig.goDrive(); rig.next(30000U); rig.port.fail_at = rig.port.operations + operation;
        const auto failed = rig.next(); CHECK_FALSE(failed.applied.feedback.applied_valid);
        CHECK(failed.applied.fault == motors::Fault::IO); app_test::zero(rig.port);
        rig.port.fail_at = 0U; const auto stopped = rig.next();
        CHECK(stopped.robot.contract_faults != 0U); drive_test::disabled(stopped, rig.port);
        CHECK(stopped.robot.turn_trial.phase == Phase::INTERRUPTED);
        CHECK(stopped.robot.turn_trial.reason == Reason::STOP);
    }
}

TEST_CASE("B14 D125 duplicate owner timestamps clear trial pulses and cannot reapply changed inputs") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        ActualRobot rig; const auto go = rig.go(); std::uint32_t when = go + 30000U;
        if (stage != 0U) { rig.input.raw_heading_deg = ANGLE; rig.at(go + 1000U);
            when = go + (stage == 1U ? 2000U : 501000U); }
        const auto before = rig.at(when); const auto calls = rig.port.count;
        rig.input.stop_requested = true; rig.input.line_raw_us[0] = 100U;
        const auto duplicate = rig.at(when); CHECK_FALSE(duplicate.fresh);
        CHECK(duplicate.token == before.token); CHECK(duplicate.events.count == 0U);
        CHECK_FALSE(duplicate.frame_ready); CHECK(rig.port.count == calls);
        sameTrial(duplicate.turn_trial, before.turn_trial);
        CHECK_FALSE(duplicate.turn_trial.fresh); CHECK_FALSE(duplicate.turn_trial.phase_changed);
        CHECK(duplicate.turn_trial_stopping == before.turn_trial_stopping);
        CHECK(duplicate.turn_trial_edge_interrupted == before.turn_trial_edge_interrupted);
        const auto stop = rig.at(when + 1U); CHECK(stop.outputs.ui_state == core::State::STOPPED);
        app_test::zero(rig.port);
    }
}

TEST_CASE("B14 D125 real Transaction rejects duplicate clock with no new Robot result and actual halt") {
    Rig rig; rig.goDrive(); rig.next(30000U); const auto token = rig.owner.previous().token;
    rig.port.now = rig.now; APP_REQUIRE(rig.owner.open()); CHECK_FALSE(rig.owner.decide(rig.source));
    CHECK(rig.owner.report().fault == app::Fault::CLOCK); CHECK(rig.owner.report().phase == app::Phase::FAULT);
    CHECK(rig.owner.report().robot.token == 0U); CHECK(rig.owner.previous().token == token);
    CHECK_FALSE(rig.owner.report().decision_made); CHECK(rig.owner.report().halt.attempted);
    CHECK(rig.owner.report().halt.inhibition_confirmed); app_test::zero(rig.port);
}

TEST_CASE("B3 R6 D125 permitting DRIVE_TEST never bypasses independent Gate hold or ATTACK-only full duty") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        app_test::Port port; motors::MotorGate gate(port.port()); APP_REQUIRE(gate.begin());
        fsm::RobotResult release; release.fresh = true; release.token = 1U;
        release.outputs.ui_state = core::State::COUNTDOWN;
        release.lifecycle.gate.phase = countdown::Phase::HOLDING;
        release.lifecycle.gate.start_release = true; release.lifecycle.gate.release_us = 1000U;
        if (scenario != 0U) { port.now = 1000U; APP_REQUIRE(gate.apply(1000U, release).feedback.applied_valid); }
        auto command = release; command.token = 2U; command.outputs.ui_state = core::State::DRIVE_TEST;
        command.outputs.motors_enabled = true; command.outputs.duty_l = scenario == 2U ? 1.0F : .8F;
        command.outputs.duty_r = -.8F; command.contact = true; command.opponent_mask = 7U;
        command.lifecycle.gate.start_release = false; command.lifecycle.gate.motion_permitted = true;
        command.lifecycle.gate.phase = countdown::Phase::READY;
        port.now = scenario == 1U ? 5100999U : 5101000U;
        const auto rejected = gate.apply(port.now, command); CHECK(rejected.fault == motors::Fault::COMMAND);
        CHECK_FALSE(rejected.feedback.applied_valid); CHECK(port.highs == 0U); CHECK(port.nonzero == 0U);
        app_test::zero(port);
    }
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 B7 D103 D125 actual Runtime completes once then service-only reset cannot rearm") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.select(2U));
    // Traversing QTR_CAL requires fresh CONTROL frames and a new neutral span.
    APP_REQUIRE(rig.run(30U, service_reset_test::NONE));
    APP_REQUIRE(rig.robot().line_available); APP_REQUIRE(!rig.robot().line_raw_mode);
    APP_REQUIRE(!rig.robot().line_calibration_hold); APP_REQUIRE(!rig.robot().line_start_rearming);
    APP_REQUIRE(rig.robot().button_available && rig.robot().button_level == Button::NONE);
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST));
    APP_REQUIRE(rig.robot().lifecycle.gate.start_release); const auto release = rig.robot().lifecycle.gate.release_us;
    bool saw_go = false, saw_brake = false, completed_once = false, stopped = false;
    for (unsigned i = 0U; i < 7000U; ++i) {
        APP_REQUIRE(rig.next()); const auto& r = rig.robot(); drive_test::noCombat(r);
        if (r.lifecycle.gate.go) { CHECK(r.turn_trial.started_us - release >= 5100000U); saw_go = true; }
        if (!saw_go) { CHECK(rig.fake.highs == 0U); CHECK(rig.fake.nonzero == 0U); }
        if (r.turn_trial.phase == Phase::BRAKE) { saw_brake = true;
            CHECK(r.turn_trial.turn_finished_us - r.turn_trial.started_us >= FALLBACK_US);
            CHECK(rig.fake.enabled == (MOTORS_ALLOWED != 0)); for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U); }
        if (r.turn_trial.phase == Phase::COMPLETE) { completed_once = true; CHECK(r.turn_trial_stopping);
            CHECK(r.turn_trial.finished_us - r.turn_trial.turn_finished_us >= 500000U); CHECK_FALSE(rig.fake.enabled); }
        if (r.outputs.ui_state == core::State::STOPPED) { stopped = true; break; }
    }
    CHECK(saw_go); CHECK(saw_brake); CHECK(completed_once); APP_REQUIRE(stopped); APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED);
    const auto frames = rig.owner.transaction().recording().frames().size();
    const auto events = rig.owner.transaction().recording().events().size();
    const auto highs = rig.fake.highs, nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending()); APP_REQUIRE(rig.next()); APP_REQUIRE(rig.owner.report().service_only);
    CHECK(rig.robot().turn_trial.phase == Phase::NOT_STARTED); CHECK_FALSE(rig.robot().turn_trial_stopping);
    CHECK_FALSE(rig.robot().turn_trial_edge_interrupted); APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); bool unavailable = false;
    for (unsigned i = 0U; i < 5150U; ++i) {
        rig.fake.button_raw = service_reset_test::NONE; APP_REQUIRE(rig.next());
        CHECK(rig.owner.report().service_only); CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go); CHECK_FALSE(rig.robot().outputs.motors_enabled);
        CHECK_FALSE(rig.fake.enabled); CHECK(rig.fake.highs == highs); CHECK(rig.fake.nonzero == nonzero);
        CHECK(rig.robot().turn_trial.phase == Phase::NOT_STARTED);
        const auto action = rig.owner.report().service_action;
        unavailable |= action.fresh && action.service == countdown::Service::DRIVE_TEST &&
                       action.status == app::ServiceActionStatus::UNAVAILABLE;
    }
    CHECK(unavailable); CHECK(rig.owner.transaction().recording().frames().size() == frames);
    CHECK(rig.owner.transaction().recording().events().size() == events);
}
#endif
