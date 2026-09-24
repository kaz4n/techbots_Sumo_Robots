// Freezes D128 hold, edge and actual receipt safety for the new reactive profile.
// Preserves established locked oracles while testing ordinary local admission.
// New independent M0/M1 cases use actual Transaction/Gate and configured Runtime.
#include "../fixtures/reactive_profile_fixture.h"
#include <limits>

using namespace reactive_test;

TEST_CASE("B3 R1 D128 ordinary match start preserves full release debounce and5100ms physical hold") {
    for (auto base : {0U, 0xfff00000U}) {
        Rig rig; rig.prime(base); rig.next(1000U, Button::START); rig.next(20000U, Button::START);
        const auto raw = rig.now + 1000U; rig.at(raw);
        const auto before = rig.at(raw + 19999U); CHECK_FALSE(before.robot.lifecycle.gate.start_release);
        drive_test::disabled(before, rig.port); const auto release = raw + 20000U;
        APP_REQUIRE(rig.at(release).robot.lifecycle.gate.start_release);
        for (auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto held = rig.at(release + age); drive_test::disabled(held, rig.port);
            CHECK(held.robot.lifecycle.gate.phase == countdown::Phase::HOLDING); noOpener(held.robot);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.at(release + 5100000U); CHECK(go.robot.lifecycle.gate.go);
        CHECK(go.robot.outputs.ui_state == State::SEARCH); active(rig, go);
    }
}

TEST_CASE("B3 B13 D128 every service remains nonmotion and DRIVE_TEST stays unavailable") {
    for (unsigned item = 0U; item < 4U; ++item) {
        Rig rig; rig.prime(); rig.longMode(); for (unsigned i = 0U; i < item; ++i) rig.shortMode();
        rig.releaseSelected(); const auto release = rig.owner.report();
        CHECK(release.robot.menu.request == static_cast<countdown::Service>(item + 1U));
        CHECK(release.robot.menu.request_unavailable == (item == 2U));
        CHECK_FALSE(release.robot.lifecycle.gate.start_release); drive_test::disabled(release, rig.port);
        const auto later = rig.next(6000000U); CHECK_FALSE(later.robot.lifecycle.gate.go);
        CHECK(later.robot.outputs.ui_state == State::IDLE); drive_test::disabled(later, rig.port);
        CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
    }
}

TEST_CASE("B3 R1 D128 bootheld initialization and MODE cancellation cannot replay starts") {
    Rig boot; boot.at(0U, Button::START); boot.at(20000U, Button::START); boot.at(30000U);
    const auto release = boot.at(50000U); CHECK_FALSE(release.robot.lifecycle.gate.start_release);
    drive_test::disabled(release, boot.port);
    Rig init; init.source.initialization_complete = false; init.at(0U); init.at(21000U);
    init.at(22000U, Button::START); init.at(42000U, Button::START); init.at(43000U);
    init.source.initialization_complete = true; const auto ready = init.at(63000U);
    CHECK_FALSE(ready.robot.lifecycle.gate.start_release); drive_test::disabled(ready, init.port);
    Rig cancel; const auto anchor = cancel.releaseMatch(); cancel.at(anchor + 5080000U, Button::MODE);
    const auto cancelled = cancel.at(anchor + 5100000U, Button::MODE);
    CHECK_FALSE(cancelled.robot.lifecycle.gate.go); drive_test::disabled(cancelled, cancel.port);
    cancel.next(); const auto later = cancel.next(6000000U);
    CHECK_FALSE(later.robot.lifecycle.gate.start_release); CHECK_FALSE(later.robot.lifecycle.gate.go);
    drive_test::disabled(later, cancel.port);
}

TEST_CASE("B3 B4 D128 raw-only absent line evidence cannot enter countdown") {
    Rig rig; rig.source.line.explicit_values = true; rig.source.line.use = core::LineUse::CALIBRATION;
    rig.source.line.presence = core::LinePresence::ABSENT; rig.source.opponent_fresh = true;
    rig.prime(); rig.releaseSelected(); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.start_release);
    drive_test::disabled(rig.next(6000000U), rig.port); CHECK_FALSE(rig.owner.report().robot.lifecycle.gate.go);
}

TEST_CASE("B6 B8 D128 real Gate scan writes LOW four PWM settle HIGH with downward quantization") {
    Rig rig; const auto go = rig.goMatch(); rig.port.clear(go);
    const auto scan = rig.at(go + 50000U); active(rig, scan);
    CHECK(scan.robot.outputs.duty_l == .45F); CHECK(scan.robot.outputs.duty_r == -.45F);
    const auto left = static_cast<std::uint32_t>(std::floor(static_cast<double>(.45F) * 1000.0));
    const auto right = static_cast<std::uint32_t>(std::floor(static_cast<double>(.45F) * 65535.0));
    CHECK(rig.port.pulses[0] == (MOTORS_ALLOWED ? left : 0U)); CHECK(rig.port.pulses[1] == 0U);
    CHECK(rig.port.pulses[2] == 0U); CHECK(rig.port.pulses[3] == (MOTORS_ALLOWED ? right : 0U));
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
    CHECK(scan.applied.feedback.duty_l == (MOTORS_ALLOWED ? static_cast<float>(left) / 1000.0F : 0.0F));
    CHECK(scan.applied.feedback.duty_r == (MOTORS_ALLOWED ? -static_cast<float>(right) / 65535.0F : 0.0F));
}

TEST_CASE("B4 R5 D128 every nonzero white mask wins GO and moving ATTACK even with centered contact") {
    for (unsigned mask = 1U; mask < 16U; ++mask) for (bool at_go : {true, false}) {
        Rig rig; std::uint32_t time;
        if (at_go) { rig.opponent(7U); rig.source.ax_g = 2.0F; time = rig.releaseMatch() + 5100000U; }
        else time = rig.attack(true) + 1000U;
        rig.white(mask); const auto r = rig.at(time); CHECK(r.robot.outputs.ui_state == State::EDGE_ESCAPE);
        CHECK(r.robot.line_mask == mask); CHECK_FALSE(r.robot.contact); noOpener(r.robot);
        const unsigned bits = ((mask >> 0U) & 1U) + ((mask >> 1U) & 1U) +
                              ((mask >> 2U) & 1U) + ((mask >> 3U) & 1U);
        if (bits >= 3U) { CHECK(r.robot.escape_fault == edge::EscapeFault::WHITE_PATTERN);
            drive_test::disabled(r, rig.port); rig.white(0U);
            const auto later = rig.next(1000000U); drive_test::disabled(later, rig.port);
            CHECK(later.robot.outputs.ui_state == State::EDGE_ESCAPE); }
        else CHECK(r.robot.escape_fault == edge::EscapeFault::NONE);
    }
}

TEST_CASE("B4 D128 complete front escape atGO selects current perception and brakes before any executor") {
    for (unsigned target : {0U, 2U, 8U}) {
        Rig rig; rig.source.imu_ok = false; rig.opponent(target);
        const auto release = rig.releaseMatch(); rig.white(1U); const auto entered = release + 5100000U;
        CHECK(rig.at(entered).robot.outputs.ui_state == State::EDGE_ESCAPE); rig.white(0U);
        rig.next(); const auto back = rig.at(entered + 50000U); active(rig, back);
        CHECK(back.robot.outputs.duty_l == -.8F); CHECK(back.robot.outputs.duty_r == -.8F);
        rig.at(entered + 121000U); const auto pivot = rig.at(entered + 200000U);
        CHECK(pivot.robot.outputs.duty_l == .8F); CHECK(pivot.robot.outputs.duty_r == -.8F);
        CHECK(rig.at(entered + 360999U).robot.outputs.ui_state == State::EDGE_ESCAPE);
        const auto exit = rig.at(entered + 361000U); brake(rig, exit);
        const auto state = target == 0U ? State::SEARCH : (target == 2U ? State::TRACK : State::DEFEND_TURN);
        CHECK(exit.robot.outputs.ui_state == state); CHECK(count(exit.robot, core::Event::EDGE, 8U) == 1U);
        const auto next = rig.next(); active(rig, next); CHECK(next.robot.outputs.ui_state == state);
        if (target == 2U) CHECK(rig.next().robot.outputs.ui_state == State::ATTACK);
    }
}

TEST_CASE("B4 D128 persistent white exhausts bounded recovery and never falls back to Search") {
    Rig rig; rig.source.imu_ok = false; rig.goMatch(); rig.white(1U); rig.next(); bool faulted = false;
    for (unsigned i = 0U; i < 2500U; ++i) {
        const auto r = rig.next(); CHECK(r.robot.outputs.ui_state == State::EDGE_ESCAPE); noOpener(r.robot);
        if (r.robot.escape_fault == edge::EscapeFault::NONE) continue;
        CHECK(r.robot.escape_fault == edge::EscapeFault::REPLAN_LIMIT);
        drive_test::disabled(r, rig.port); faulted = true; break;
    }
    CHECK(faulted); rig.white(0U); drive_test::disabled(rig.next(), rig.port);
    CHECK(rig.owner.report().robot.outputs.ui_state == State::EDGE_ESCAPE);
}

TEST_CASE("B4 B5 D128 real centered push context uses actual positive Gate feedback and clears contact") {
    Rig rig; rig.attack(true); rig.white(8U); const auto r = rig.next();
    CHECK(r.robot.outputs.ui_state == State::EDGE_ESCAPE); CHECK_FALSE(r.robot.contact);
    bool pushed = false;
    for (unsigned i = 0U; i < r.robot.events.count; ++i)
        if (r.robot.events.entries[i].type == core::Event::EDGE)
            pushed |= (r.robot.events.entries[i].detail & logframe::PUSHED_OUT) != 0U;
    CHECK(pushed == (MOTORS_ALLOWED != 0));
}

TEST_CASE("B3 B4 D128 immediate STOP beats simultaneous edge during GO Search TRACK ATTACK and DEFEND") {
    for (unsigned stage = 0U; stage < 5U; ++stage) {
        Rig rig; std::uint32_t time;
        if (stage == 0U) time = rig.releaseMatch() + 5100000U;
        else if (stage == 3U) time = rig.attack(true) + 1000U;
        else { if (stage == 2U) rig.opponent(1U); if (stage == 4U) rig.opponent(8U);
            rig.goMatch(); rig.next(); time = rig.now + 1000U; }
        rig.source.stop_requested = true; rig.white(15U); const auto stop = rig.at(time);
        CHECK(stop.robot.outputs.ui_state == State::STOPPED); CHECK_FALSE(stop.robot.contact);
        CHECK(stop.robot.lifecycle.gate.phase == countdown::Phase::STOPPED); drive_test::disabled(stop, rig.port);
        rig.source.stop_requested = false; rig.white(0U); rig.next(6000000U);
        CHECK(rig.owner.report().robot.outputs.ui_state == State::STOPPED);
    }
}

TEST_CASE("B3 D128 logical BOTH still requires20ms qualification and full1000ms hold") {
    Rig rig; rig.goMatch(); const auto raw = rig.now + 1000U;
    rig.at(raw, Button::BOTH); rig.at(raw + 20000U, Button::BOTH);
    const auto before = rig.at(raw + 1019999U, Button::BOTH); active(rig, before);
    const auto stop = rig.at(raw + 1020000U, Button::BOTH);
    CHECK(stop.robot.outputs.ui_state == State::STOPPED); drive_test::disabled(stop, rig.port);
}

TEST_CASE("B14 D128 stale sources invalid battery and healthy invalid yaw latch actual inhibition") {
    for (unsigned failure = 0U; failure < 3U; ++failure) for (bool holding : {true, false}) {
        Rig rig; if (holding) rig.releaseMatch(); else rig.attack(true);
        if (failure == 0U) rig.source.observations_fresh = false;
        if (failure == 1U) rig.source.vbat_v = std::numeric_limits<float>::quiet_NaN();
        if (failure == 2U) rig.source.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        const auto r = rig.next(); CHECK(r.robot.contract_faults != 0U);
        CHECK(r.robot.outputs.ui_state == State::STOPPED); drive_test::disabled(r, rig.port);
    }
}

TEST_CASE("B14 D128 all actual Gate callback failures invalidate receipts and stop the next decision") {
    for (unsigned operation = 1U; operation <= (MOTORS_ALLOWED ? 7U : 6U); ++operation) {
        Rig rig; rig.attack(true); rig.port.fail_at = rig.port.operations + operation;
        const auto failed = rig.next(); CHECK_FALSE(failed.applied.feedback.applied_valid);
        CHECK(failed.applied.fault == motors::Fault::IO); app_test::zero(rig.port);
        rig.port.fail_at = 0U; const auto stopped = rig.next(); CHECK(stopped.robot.contract_faults != 0U);
        CHECK(stopped.robot.outputs.ui_state == State::STOPPED); drive_test::disabled(stopped, rig.port);
    }
}

TEST_CASE("B14 D128 duplicate Robot GO cannot reenter Search advance centering or replay Gate writes") {
    for (bool target : {false, true}) {
        ActualRobot rig; if (target) rig.input.opp_raw_mask = static_cast<std::uint8_t>(2U ^ 0x78U);
        const auto go = rig.go(); const auto calls = rig.port.count;
        const auto first = rig.at(go); CHECK_FALSE(first.fresh); CHECK(first.outputs.ui_state == State::SEARCH);
        rig.input.stop_requested = true; rig.input.line_raw_us[0] = 100U;
        rig.input.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        for (unsigned i = 0U; i < 5U; ++i) {
            const auto duplicate = rig.at(go); CHECK_FALSE(duplicate.fresh); CHECK(duplicate.token == first.token);
            CHECK_FALSE(duplicate.lifecycle.gate.go); CHECK(duplicate.events.count == 0U);
            CHECK_FALSE(duplicate.frame_ready); CHECK(duplicate.contract_faults == 0U);
            CHECK(duplicate.outputs.duty_l == first.outputs.duty_l); CHECK(rig.port.count == calls);
        }
        rig.input.stop_requested = false; rig.input.line_raw_us[0] = 1000U; rig.input.raw_heading_deg = 0.0F;
        const auto next = rig.at(go + 1000U); CHECK(next.outputs.ui_state == (target ? State::TRACK : State::SEARCH));
        if (target) { CHECK(rig.at(go + 2000U).outputs.ui_state == State::TRACK);
            CHECK(rig.at(go + 3000U).outputs.ui_state == State::ATTACK); }
    }
}

TEST_CASE("B14 D128 Transaction duplicate clock creates no Robot result and performs terminal halt") {
    Rig rig; rig.goMatch(); rig.next(50000U); const auto token = rig.owner.previous().token;
    rig.port.now = rig.now; APP_REQUIRE(rig.owner.open()); CHECK_FALSE(rig.owner.decide(rig.source));
    CHECK(rig.owner.report().fault == app::Fault::CLOCK); CHECK_FALSE(rig.owner.report().decision_made);
    CHECK(rig.owner.report().robot.token == 0U); CHECK(rig.owner.previous().token == token);
    CHECK(rig.owner.report().halt.inhibition_confirmed); app_test::zero(rig.port);
}

TEST_CASE("B11 R5 D128 actual reflank BACK and SWING remain interruptible by edge and STOP") {
    if (!MOTORS_ALLOWED) { Rig rig; rig.attack(true); rig.next(2000000U);
        CHECK(rig.owner.report().robot.outputs.ui_state == State::ATTACK); return; }
    for (bool swing : {false, true}) for (bool stop : {false, true}) {
        Rig rig; rig.attack(true); rig.next(); const auto qualified = rig.now;
        APP_REQUIRE(rig.at(qualified + 1000000U).robot.outputs.ui_state == State::REFLANK);
        if (swing) APP_REQUIRE(rig.next(150000U).robot.outputs.ui_state == State::REFLANK);
        rig.white(15U); rig.source.stop_requested = stop; const auto r = rig.next();
        CHECK(r.robot.outputs.ui_state == (stop ? State::STOPPED : State::EDGE_ESCAPE));
        CHECK_FALSE(r.robot.contact); drive_test::disabled(r, rig.port);
    }
}

TEST_CASE("B11 D025 D128 real third stall enters ALL_IN but edge and STOP retain absolute priority") {
    Rig rig; auto full = rig.attack(true);
    if (!MOTORS_ALLOWED) { const auto later = rig.next(7000000U);
        CHECK_FALSE(later.robot.all_in); CHECK(later.robot.outputs.ui_state == State::ATTACK); return; }
    for (unsigned attempt = 0U; attempt < 2U; ++attempt) {
        rig.at(full + 1000U); const auto start = full + 1001000U;
        APP_REQUIRE(rig.at(start).robot.outputs.ui_state == State::REFLANK);
        full = fullAfterReflank(rig, start);
    }
    rig.at(full + 1000U); const auto all_in = rig.at(full + 1001000U); active(rig, all_in);
    CHECK(all_in.robot.outputs.ui_state == State::ATTACK); CHECK(all_in.robot.all_in); CHECK(all_in.robot.contact);
    rig.white(3U); const auto edge = rig.next(); CHECK(edge.robot.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK_FALSE(edge.robot.contact); CHECK(edge.robot.outputs.duty_l == 0.0F);
    CHECK(edge.robot.outputs.duty_r == 0.0F); rig.source.stop_requested = true;
    const auto stop = rig.next(); CHECK(stop.robot.outputs.ui_state == State::STOPPED); drive_test::disabled(stop, rig.port);
}

TEST_CASE("B3 R6 D128 Gate cannot arm from forged permission or full SEARCH contact flags") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        app_test::Port port; motors::MotorGate gate(port.port()); APP_REQUIRE(gate.begin());
        fsm::RobotResult release; release.fresh = true; release.token = 1U;
        release.outputs.ui_state = State::COUNTDOWN; release.lifecycle.gate.phase = countdown::Phase::HOLDING;
        release.lifecycle.gate.start_release = true; release.lifecycle.gate.release_us = 1000U;
        if (scenario != 0U) { port.now = 1000U; APP_REQUIRE(gate.apply(1000U, release).feedback.applied_valid); }
        auto command = release; command.token = 2U; command.outputs.ui_state = State::SEARCH;
        command.outputs.motors_enabled = true; command.outputs.duty_l = scenario == 2U ? 1.0F : .3F;
        command.outputs.duty_r = .3F; command.contact = true; command.opponent_mask = 7U;
        command.lifecycle.gate.start_release = false; command.lifecycle.gate.motion_permitted = true;
        command.lifecycle.gate.phase = countdown::Phase::READY; port.now = scenario == 1U ? 5100999U : 5101000U;
        const auto rejected = gate.apply(port.now, command); CHECK(rejected.fault == motors::Fault::COMMAND);
        CHECK_FALSE(rejected.feedback.applied_valid); CHECK(port.highs == 0U); CHECK(port.nonzero == 0U);
        app_test::zero(port);
    }
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 D103 D128 configured Runtime ordinary start works once but service-only reset cannot rearm") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.robot().line_available); APP_REQUIRE(!rig.robot().line_raw_mode);
    APP_REQUIRE(!rig.robot().line_calibration_hold); APP_REQUIRE(!rig.robot().line_start_rearming);
    APP_REQUIRE(rig.robot().button_available && rig.robot().button_level == Button::NONE);
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); rig.fake.button_raw = service_reset_test::NONE;
    bool released = false, go = false; std::uint32_t release = 0U;
    for (unsigned i = 0U; i < 5200U; ++i) {
        APP_REQUIRE(rig.next()); const auto& r = rig.robot(); noOpener(r);
        if (r.lifecycle.gate.start_release) { released = true; release = r.lifecycle.gate.release_us; }
        if (r.lifecycle.gate.go) { CHECK(released); CHECK(r.heading.origin_t_us - release >= 5100000U);
            CHECK(r.outputs.ui_state == State::SEARCH); go = true; break; }
        CHECK(rig.fake.highs == 0U); CHECK(rig.fake.nonzero == 0U);
    }
    APP_REQUIRE(go); APP_REQUIRE(rig.run(50U)); CHECK(rig.robot().outputs.ui_state == State::SEARCH);
    CHECK(rig.fake.enabled == (MOTORS_ALLOWED != 0)); APP_REQUIRE(rig.firstStop()); APP_REQUIRE(rig.next());
    APP_REQUIRE(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED);
    const auto frames = rig.owner.transaction().recording().frames().size();
    const auto events = rig.owner.transaction().recording().events().size();
    const auto highs = rig.fake.highs, nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending()); APP_REQUIRE(rig.next()); APP_REQUIRE(rig.owner.report().service_only);
    APP_REQUIRE(rig.run(30U)); APP_REQUIRE(rig.run(30U, service_reset_test::START));
    rig.fake.button_raw = service_reset_test::NONE;
    for (unsigned i = 0U; i < 5150U; ++i) {
        APP_REQUIRE(rig.next()); CHECK(rig.owner.report().service_only);
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release); CHECK_FALSE(rig.robot().lifecycle.gate.go);
        CHECK_FALSE(rig.robot().outputs.motors_enabled); CHECK_FALSE(rig.fake.enabled);
        CHECK(rig.fake.highs == highs); CHECK(rig.fake.nonzero == nonzero); noOpener(rig.robot());
    }
    CHECK(rig.owner.transaction().recording().frames().size() == frames);
    CHECK(rig.owner.transaction().recording().events().size() == events);
}
#endif
