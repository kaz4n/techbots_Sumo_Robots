// Freezes D126 hold and edge invariants without editing established locked tests.
// Exercises genuine menu, real Transaction/Gate and configured Runtime service isolation.
// Software-only traces distinguish final electrical settings from physical stopping.
#include "../fixtures/stop_trial_fixture.h"
#include <limits>

using namespace stop_test;

TEST_CASE("B3 R1 D126 actual Gate stays low through full release debounce and hold across wrap") {
    for (auto base : {0U, 0xffd00000U}) {
        Rig rig; rig.selectDrive(base); rig.next(1000U, Button::START); rig.next(20000U, Button::START);
        const auto raw = rig.now + 1000U; rig.at(raw);
        const auto before = rig.at(raw + 19999U); CHECK_FALSE(before.robot.lifecycle.gate.start_release);
        drive_test::disabled(before, rig.port); const auto release = raw + 20000U;
        APP_REQUIRE(rig.at(release).robot.lifecycle.gate.start_release);
        for (auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto r = rig.at(release + age); drive_test::disabled(r, rig.port);
            CHECK(r.robot.lifecycle.gate.phase == countdown::Phase::HOLDING);
            CHECK(r.robot.stop_trial.phase == Phase::NOT_STARTED); CHECK_FALSE(r.robot.stop_trial.started);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.at(release + 5100000U); APP_REQUIRE(go.robot.lifecycle.gate.go);
        approach(rig, go, release + 5100000U);
    }
}

TEST_CASE("B3 D126 boot-held START and MODE cancellation cannot launch or replay an approach") {
    Rig boot; boot.at(0U, Button::START); boot.at(20000U, Button::START); boot.at(30000U);
    const auto released = boot.at(50000U); CHECK_FALSE(released.robot.lifecycle.gate.start_release);
    CHECK(released.robot.stop_trial.phase == Phase::NOT_STARTED); drive_test::disabled(released, boot.port);
    Rig rig; const auto release = rig.releaseDrive(); rig.at(release + 5080000U, Button::MODE);
    const auto cancelled = rig.at(release + 5100000U, Button::MODE);
    CHECK_FALSE(cancelled.robot.lifecycle.gate.go); drive_test::disabled(cancelled, rig.port);
    CHECK(cancelled.robot.stop_trial.phase == Phase::NOT_STARTED);
    rig.next(); const auto later = rig.next(6000000U); CHECK_FALSE(later.robot.lifecycle.gate.go);
    CHECK_FALSE(later.robot.lifecycle.gate.start_release); drive_test::disabled(later, rig.port);
}

TEST_CASE("B3 B4 D126 selected service cannot bypass absent raw-only line readiness") {
    Rig rig; rig.source.line.explicit_values = true; rig.source.line.use = core::LineUse::CALIBRATION;
    rig.source.line.presence = core::LinePresence::ABSENT; rig.source.opponent_fresh = true;
    rig.selectDrive(); rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
    const auto later = rig.next(6000000U); drive_test::disabled(later, rig.port);
    CHECK_FALSE(later.robot.lifecycle.gate.go); CHECK(later.robot.stop_trial.phase == Phase::NOT_STARTED);
}

TEST_CASE("B6 B7 D126 actual Gate orders LOW PWM settle HIGH and reports downward quantization") {
    Rig rig; rig.source.vbat_v = 9.0F; const auto go = rig.goDrive(); rig.port.clear(go);
    const auto report = rig.at(go + 50000U); approach(rig, report, go);
    CHECK(report.robot.outputs.duty_l == DUTY); CHECK(report.robot.outputs.duty_r == DUTY);
    const auto left = static_cast<std::uint32_t>(std::floor(static_cast<double>(DUTY) * 1000.0));
    const auto right = static_cast<std::uint32_t>(std::floor(static_cast<double>(DUTY) * 251.0));
    CHECK(rig.port.pulses[0] == (MOTORS_ALLOWED ? left : 0U)); CHECK(rig.port.pulses[1] == 0U);
    CHECK(rig.port.pulses[2] == (MOTORS_ALLOWED ? right : 0U)); CHECK(rig.port.pulses[3] == 0U);
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
    CHECK(report.applied.feedback.duty_l == (MOTORS_ALLOWED ? static_cast<float>(left) / 1000.0F : 0.0F));
    CHECK(report.applied.feedback.duty_r == (MOTORS_ALLOWED ? static_cast<float>(right) / 251.0F : 0.0F));
}

TEST_CASE("B7 D126 no-edge COMPLETE immediately inhibits and can never repeat or become search") {
    Rig rig; const auto go = rig.goDrive(); brake(rig, rig.at(go + 1000000U), go + 1000000U);
    const auto done = rig.at(go + 1500000U); complete(rig, done, go + 1500000U);
    const auto stop = rig.next(); CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    drive_test::disabled(stop, rig.port); rig.next();
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    rig.next(1000U, Button::START); rig.next(20000U, Button::START); rig.next();
    const auto later = rig.next(6000000U); CHECK(later.robot.outputs.ui_state == core::State::STOPPED);
    same(later.robot.stop_trial, done.robot.stop_trial); drive_test::disabled(later, rig.port);
    CHECK(later.robot.stop_trial_stopping); CHECK_FALSE(later.robot.stop_trial.fresh);
}

TEST_CASE("B4 R5 D126 edge at GO prevents approach and three or all white stays reset-only inhibited") {
    for (unsigned mask : {1U, 7U, 15U}) {
        Rig rig; const auto release = rig.releaseDrive(); rig.white(mask);
        const auto r = rig.at(release + 5100000U); CHECK(r.robot.lifecycle.gate.go);
        CHECK(r.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK(r.robot.stop_trial.phase == Phase::NOT_STARTED); CHECK_FALSE(r.robot.stop_trial.started);
        CHECK(r.robot.stop_trial_edge_interrupted); CHECK_FALSE(r.robot.stop_trial_stopping);
        if (mask != 1U) {
            CHECK(r.robot.escape_fault == edge::EscapeFault::WHITE_PATTERN); drive_test::disabled(r, rig.port);
            rig.white(0U); const auto later = rig.next(1000000U); drive_test::disabled(later, rig.port);
            CHECK(later.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK(later.robot.stop_trial.phase == Phase::NOT_STARTED);
        }
    }
}

TEST_CASE("B4 R5 D126 edge GO approach or brake runs full approved escape then stops without resumption") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        Rig rig; rig.source.imu_ok = false; std::uint32_t entered = 0U;
        if (stage == 0U) { const auto release = rig.releaseDrive(); rig.white(1U);
            entered = release + 5100000U; rig.at(entered); }
        else { const auto go = rig.goDrive(); if (stage == 2U) rig.at(go + 1000000U);
            rig.white(1U); entered = rig.now + 1000U; rig.at(entered); }
        const auto interrupted = rig.owner.report().robot.stop_trial;
        CHECK(interrupted.phase == (stage == 0U ? Phase::NOT_STARTED : Phase::INTERRUPTED));
        if (stage != 0U) { CHECK(interrupted.reason == Reason::EDGE); CHECK(interrupted.finished_us == entered); }
        rig.white(0U); bool exited = false, exceeded_trial_cap = false;
        for (unsigned age = 1000U; age <= 2000000U; age += 1000U) {
            const auto r = rig.at(entered + age); same(r.robot.stop_trial, interrupted);
            CHECK(r.robot.stop_trial_edge_interrupted); drive_test::noCombat(r.robot);
            exceeded_trial_cap |= std::fabs(r.robot.outputs.duty_l) > DUTY;
            if (age == 50000U) { CHECK(r.robot.outputs.duty_l == -.8F); CHECK(r.robot.outputs.duty_r == -.8F); }
            if (age == 200000U) { CHECK(r.robot.outputs.duty_l == .8F); CHECK(r.robot.outputs.duty_r == -.8F); }
            if (!r.robot.stop_trial_stopping) { CHECK(r.robot.outputs.ui_state == core::State::EDGE_ESCAPE); continue; }
            CHECK(age == 361000U); // Full 1ms brake, 120ms reverse, 120deg * 2ms/deg pivot.
            drive_test::disabled(r, rig.port); const auto stop = rig.next();
            CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
            CHECK(stop.robot.outputs.ui_state == core::State::STOPPED); drive_test::disabled(stop, rig.port);
            same(stop.robot.stop_trial, interrupted); exited = true; break;
        }
        CHECK(exceeded_trial_cap); CHECK(exited);
    }
}

TEST_CASE("B4 R5 D126 edge wins exact approach and brake completion deadlines") {
    for (bool braking : {false, true}) {
        Rig rig; const auto go = rig.goDrive(); if (braking) rig.at(go + 1000000U);
        rig.white(1U); const auto time = go + (braking ? 1500000U : 1000000U);
        const auto edge = rig.at(time); CHECK(edge.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK(edge.robot.stop_trial.phase == Phase::INTERRUPTED); CHECK(edge.robot.stop_trial.reason == Reason::EDGE);
        CHECK(edge.robot.stop_trial.finished_us == time); CHECK(edge.robot.stop_trial.approach_finished == braking);
        CHECK(edge.robot.stop_trial.approach_status == (braking ? motion::Status::DONE : motion::Status::ACTIVE));
        CHECK_FALSE(edge.robot.stop_trial_stopping);
    }
}

TEST_CASE("B4 R5 D126 persistent white exhausts recovery but never resumes or erases interrupted approach") {
    Rig rig; rig.source.imu_ok = false; rig.goDrive(); rig.white(1U); rig.next();
    const auto interrupted = rig.owner.report().robot.stop_trial; bool faulted = false;
    for (unsigned i = 0U; i < 2500U; ++i) {
        const auto r = rig.next(); same(r.robot.stop_trial, interrupted);
        CHECK(r.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
        CHECK_FALSE(r.robot.stop_trial_stopping); CHECK(r.robot.stop_trial_edge_interrupted);
        if (r.robot.escape_fault == edge::EscapeFault::NONE) continue;
        drive_test::disabled(r, rig.port); faulted = true; break;
    }
    CHECK(faulted); rig.white(0U); drive_test::disabled(rig.next(), rig.port);
    CHECK(rig.owner.report().robot.outputs.ui_state == core::State::EDGE_ESCAPE);
}

TEST_CASE("B4 B5 D126 real centered opponent and applied forward retain pushed-out escape context") {
    Rig rig; rig.source.imu_ok = false; const auto go = rig.goDrive(); rig.opponent(2U);
    rig.at(go + 1000U); rig.at(go + 2000U); rig.at(go + 50000U); rig.white(8U);
    const auto edge = rig.next(); CHECK(edge.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    CHECK(edge.robot.stop_trial.reason == Reason::EDGE); bool pushed = false;
    for (unsigned i = 0U; i < edge.robot.events.count; ++i)
        if (edge.robot.events.entries[i].type == core::Event::EDGE)
            pushed |= (edge.robot.events.entries[i].detail & logframe::PUSHED_OUT) != 0U;
    CHECK(pushed == (MOTORS_ALLOWED != 0)); drive_test::noCombat(edge.robot);
}

TEST_CASE("B3 B4 D126 immediate STOP wins concurrent edge at GO approach and brake") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        Rig rig; std::uint32_t time = 0U;
        if (stage == 0U) time = rig.releaseDrive() + 5100000U;
        else { const auto go = rig.goDrive(); if (stage == 2U) rig.at(go + 1000000U); time = rig.now + 1000U; }
        rig.source.stop_requested = true; rig.white(15U); const auto stop = rig.at(time);
        CHECK(stop.robot.outputs.ui_state == core::State::STOPPED);
        CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED); drive_test::disabled(stop, rig.port);
        CHECK(stop.robot.stop_trial.phase == (stage == 0U ? Phase::NOT_STARTED : Phase::INTERRUPTED));
        if (stage != 0U) { CHECK(stop.robot.stop_trial.reason == Reason::STOP);
            CHECK(stop.robot.stop_trial.finished_us == time); }
    }
}

TEST_CASE("B3 D126 qualified logical BOTH cancels active brake after full debounce and long hold") {
    Rig rig; const auto go = rig.goDrive(); const auto pressed = go + 1000U;
    rig.at(pressed, Button::BOTH); rig.at(pressed + 20000U, Button::BOTH);
    rig.at(go + 1000000U, Button::BOTH);
    const auto before = rig.at(pressed + 1019999U, Button::BOTH);
    CHECK(before.robot.stop_trial.phase == Phase::BRAKE);
    const auto stop = rig.at(pressed + 1020000U, Button::BOTH);
    CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED);
    CHECK(stop.robot.stop_trial.phase == Phase::INTERRUPTED); CHECK(stop.robot.stop_trial.reason == Reason::STOP);
    CHECK(stop.robot.stop_trial.approach_status == motion::Status::DONE); drive_test::disabled(stop, rig.port);
}

TEST_CASE("B14 D126 source battery and healthy-yaw failures immediately inhibit and cancel active trial") {
    for (unsigned failure = 0U; failure < 3U; ++failure) {
        Rig rig; rig.goDrive(); rig.next(50000U);
        if (failure == 0U) rig.source.observations_fresh = false;
        if (failure == 1U) rig.source.vbat_v = std::numeric_limits<float>::quiet_NaN();
        if (failure == 2U) rig.source.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        const auto r = rig.next(); CHECK(r.robot.contract_faults != 0U);
        CHECK(r.robot.outputs.ui_state == core::State::STOPPED); drive_test::disabled(r, rig.port);
        CHECK(r.robot.stop_trial.phase == Phase::INTERRUPTED); CHECK(r.robot.stop_trial.reason == Reason::STOP);
    }
}

TEST_CASE("B14 D126 failed actual Gate callback receipt remains invalid and cancels on next owner tick") {
    for (unsigned operation = 1U; operation <= (MOTORS_ALLOWED ? 7U : 6U); ++operation) {
        Rig rig; rig.goDrive(); rig.next(50000U); rig.port.fail_at = rig.port.operations + operation;
        const auto failed = rig.next(); CHECK_FALSE(failed.applied.feedback.applied_valid);
        CHECK(failed.applied.fault == motors::Fault::IO); app_test::zero(rig.port);
        rig.port.fail_at = 0U; const auto stopped = rig.next(); CHECK(stopped.robot.contract_faults != 0U);
        drive_test::disabled(stopped, rig.port); CHECK(stopped.robot.stop_trial.phase == Phase::INTERRUPTED);
        CHECK(stopped.robot.stop_trial.reason == Reason::STOP);
    }
}

TEST_CASE("B14 D126 duplicate Robot observations clear pulses without reapplying changed edge or STOP") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        ActualRobot rig; const auto go = rig.go(); std::uint32_t time = go + 50000U;
        if (stage != 0U) { rig.at(go + 1000000U); time = go + (stage == 1U ? 1001000U : 1500000U); }
        const auto before = rig.at(time); const auto calls = rig.port.count;
        rig.input.stop_requested = true; rig.input.line_raw_us[0] = 100U;
        const auto duplicate = rig.at(time); CHECK_FALSE(duplicate.fresh); CHECK(duplicate.token == before.token);
        CHECK(duplicate.events.count == 0U); CHECK_FALSE(duplicate.frame_ready); CHECK(rig.port.count == calls);
        same(duplicate.stop_trial, before.stop_trial); CHECK_FALSE(duplicate.stop_trial.fresh);
        CHECK_FALSE(duplicate.stop_trial.phase_changed);
        CHECK(duplicate.stop_trial_stopping == before.stop_trial_stopping);
        CHECK(duplicate.stop_trial_edge_interrupted == before.stop_trial_edge_interrupted);
        const auto stop = rig.at(time + 1U); CHECK(stop.outputs.ui_state == core::State::STOPPED);
        app_test::zero(rig.port);
    }
}

TEST_CASE("B14 D126 actual Transaction duplicate clock halts without fabricating a new Robot result") {
    Rig rig; rig.goDrive(); rig.next(50000U); const auto token = rig.owner.previous().token;
    rig.port.now = rig.now; APP_REQUIRE(rig.owner.open()); CHECK_FALSE(rig.owner.decide(rig.source));
    CHECK(rig.owner.report().fault == app::Fault::CLOCK); CHECK(rig.owner.report().phase == app::Phase::FAULT);
    CHECK(rig.owner.report().robot.token == 0U); CHECK(rig.owner.previous().token == token);
    CHECK_FALSE(rig.owner.report().decision_made); CHECK(rig.owner.report().halt.inhibition_confirmed);
    app_test::zero(rig.port);
}

TEST_CASE("B3 R6 D126 allowed state still cannot bypass Gate anchor full hold or ATTACK-only full duty") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        app_test::Port port; motors::MotorGate gate(port.port()); APP_REQUIRE(gate.begin());
        fsm::RobotResult release; release.fresh = true; release.token = 1U;
        release.outputs.ui_state = core::State::COUNTDOWN; release.lifecycle.gate.phase = countdown::Phase::HOLDING;
        release.lifecycle.gate.start_release = true; release.lifecycle.gate.release_us = 1000U;
        if (scenario != 0U) { port.now = 1000U; APP_REQUIRE(gate.apply(1000U, release).feedback.applied_valid); }
        auto command = release; command.token = 2U; command.outputs.ui_state = core::State::DRIVE_TEST;
        command.outputs.motors_enabled = true; command.outputs.duty_l = scenario == 2U ? 1.0F : DUTY;
        command.outputs.duty_r = DUTY; command.contact = true; command.opponent_mask = 7U;
        command.lifecycle.gate.start_release = false; command.lifecycle.gate.motion_permitted = true;
        command.lifecycle.gate.phase = countdown::Phase::READY; port.now = scenario == 1U ? 5100999U : 5101000U;
        const auto rejected = gate.apply(port.now, command); CHECK(rejected.fault == motors::Fault::COMMAND);
        CHECK_FALSE(rejected.feedback.applied_valid); CHECK(port.highs == 0U); CHECK(port.nonzero == 0U);
        app_test::zero(port);
    }
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 B7 D103 D126 actual ready Runtime finishes once and service-only reset cannot rearm") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.select(2U)); APP_REQUIRE(rig.run(30U, service_reset_test::NONE));
    APP_REQUIRE(rig.robot().line_available); APP_REQUIRE(!rig.robot().line_raw_mode);
    APP_REQUIRE(!rig.robot().line_calibration_hold); APP_REQUIRE(!rig.robot().line_start_rearming);
    APP_REQUIRE(rig.robot().button_available && rig.robot().button_level == Button::NONE);
    APP_REQUIRE(rig.request(countdown::Service::DRIVE_TEST)); APP_REQUIRE(rig.robot().lifecycle.gate.start_release);
    const auto release = rig.robot().lifecycle.gate.release_us;
    bool saw_go = false, saw_brake = false, saw_complete = false, stopped = false;
    for (unsigned i = 0U; i < 8000U; ++i) {
        APP_REQUIRE(rig.next()); const auto& r = rig.robot(); drive_test::noCombat(r);
        if (r.lifecycle.gate.go) { CHECK(r.stop_trial.started_us - release >= 5100000U); saw_go = true; }
        if (!saw_go) { CHECK(rig.fake.highs == 0U); CHECK(rig.fake.nonzero == 0U); }
        if (r.stop_trial.phase == Phase::BRAKE) { saw_brake = true;
            CHECK(r.stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
            CHECK(r.stop_trial.approach_finished_us - r.stop_trial.started_us >= 1000000U);
            CHECK(rig.fake.enabled == (MOTORS_ALLOWED != 0)); for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U); }
        if (r.stop_trial.phase == Phase::COMPLETE) { saw_complete = true; CHECK(r.stop_trial_stopping);
            CHECK(r.stop_trial.finished_us - r.stop_trial.approach_finished_us >= 500000U); CHECK_FALSE(rig.fake.enabled); }
        if (r.outputs.ui_state == core::State::STOPPED) { stopped = true; break; }
    }
    CHECK(saw_go); CHECK(saw_brake); CHECK(saw_complete); APP_REQUIRE(stopped); APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED);
    const auto frames = rig.owner.transaction().recording().frames().size();
    const auto events = rig.owner.transaction().recording().events().size();
    const auto highs = rig.fake.highs, nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending()); APP_REQUIRE(rig.next()); APP_REQUIRE(rig.owner.report().service_only);
    CHECK(rig.robot().stop_trial.phase == Phase::NOT_STARTED); CHECK_FALSE(rig.robot().stop_trial_stopping);
    CHECK_FALSE(rig.robot().stop_trial_edge_interrupted); APP_REQUIRE(rig.select(2U));
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); bool unavailable = false;
    for (unsigned i = 0U; i < 5150U; ++i) {
        rig.fake.button_raw = service_reset_test::NONE; APP_REQUIRE(rig.next());
        CHECK(rig.owner.report().service_only); CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go); CHECK_FALSE(rig.robot().outputs.motors_enabled);
        CHECK_FALSE(rig.fake.enabled); CHECK(rig.fake.highs == highs); CHECK(rig.fake.nonzero == nonzero);
        CHECK(rig.robot().stop_trial.phase == Phase::NOT_STARTED);
        const auto action = rig.owner.report().service_action;
        unavailable |= action.fresh && action.service == countdown::Service::DRIVE_TEST &&
                       action.status == app::ServiceActionStatus::UNAVAILABLE;
    }
    CHECK(unavailable); CHECK(rig.owner.transaction().recording().frames().size() == frames);
    CHECK(rig.owner.transaction().recording().events().size() == events);
}
#endif
