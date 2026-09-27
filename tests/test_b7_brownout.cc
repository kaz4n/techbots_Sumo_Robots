// Checks the frozen D244 B7 contract independently of its implementation.
// Uses literal endpoint, deadline, safety and one-shot lifetime expectations.
// Dedicated M0/M1 strict host targets and the serialized UBSan runner execute it.
#include "fixtures/b7_fixture.h"
#include "app/configured_setup.h"
#include <limits>

using namespace b7_test;

TEST_CASE("B7 D244 immutable identity and exact original trial constants") {
    CHECK(SUMOX_B7_BROWNOUT == 1); CHECK(MATCH == 0);
    CHECK(fsm::RobotResult::BROWNOUT_PROFILE);
    CHECK(config::BROWNOUT_CYCLES == 20U); CHECK(config::BROWNOUT_FULL_DUTY == 1.0F);
    CHECK(config::BROWNOUT_DWELL_MS == 500U); CHECK(config::BROWNOUT_REACH_MS == 1000U);
    CHECK(config::BROWNOUT_RECEIPT_MAX_GAP_US == 2000U);
    const fsm::RobotResult initial;
    CHECK(initial.brownout.phase == Phase::NOT_STARTED); CHECK_FALSE(initial.brownout.consumed);
    CHECK_FALSE(initial.brownout_stopping); CHECK_FALSE(initial.brownout_edge_interrupted);
}

TEST_CASE("B7 D244 pure sequence requires forty exact signed half-second endpoint dwells") {
    Sequence owner; APP_REQUIRE(owner.start(100U)); std::uint32_t now = 100U;
    std::uint64_t token = 0U;
    for (unsigned leg = 0U; leg < 40U; ++leg) {
        const auto start = now; const float sign = leg % 2U == 0U ? 1.0F : -1.0F;
        CHECK(owner.report().leg_index == leg); CHECK(owner.report().leg_started_us == start);
        CHECK(owner.report().duty_l == sign); CHECK(owner.report().duty_r == sign);
        now += 1000U; auto r = owner.step(now, receipt(++token, leg, now));
        CHECK(r.phase == Phase::DWELL); CHECK(r.endpoint_started_us == now);
        const auto endpoint = now;
        for (unsigned tick = 1U; tick < 500U; ++tick) {
            now += 1000U; r = owner.step(now, receipt(++token, leg, now));
        }
        CHECK(r.completed_legs == leg); CHECK(r.completed_cycles == leg / 2U);
        now += 1000U; r = owner.step(now, receipt(++token, leg, now));
        CHECK(r.completed_legs == leg + 1U); CHECK(r.completed_cycles == (leg + 1U) / 2U);
        CHECK(r.completed_endpoint_started_us == endpoint);
        CHECK(r.completed_endpoint_last_us - endpoint == 500000U);
        CHECK(r.phase == (leg == 39U ? Phase::COMPLETE : Phase::REACH));
    }
    const auto terminal = owner.report(); CHECK(terminal.reason == Reason::NONE);
    CHECK(terminal.terminal_us == now); CHECK(terminal.duty_l == 0.0F); CHECK(terminal.duty_r == 0.0F);
    CHECK_FALSE(owner.start(now + 1000U)); CHECK_FALSE(owner.interrupt(Reason::RESET_REQUEST, now + 1U));
    same(owner.step(now + 1000U, {}), terminal);
}

TEST_CASE("B7 D244 first endpoint strict deadline uses actual applied time before delayed decision") {
    for (std::uint32_t applied : {999999U, 1000000U}) {
        Sequence owner; APP_REQUIRE(owner.start(0U)); std::uint64_t token = 0U;
        for (std::uint32_t now = 1000U; now <= 999000U; now += 1000U)
            owner.step(now, receipt(++token, 0U, now, true, .5F));
        const auto r = owner.step(1001000U, receipt(++token, 0U, applied));
        if (applied == 999999U) {
            CHECK(r.phase == Phase::DWELL); CHECK(r.endpoint_started_us == 999999U);
        } else { aborted(r); CHECK(r.reason == Reason::REACH_TIMEOUT); CHECK_FALSE(r.endpoint_valid); }
        CHECK(r.completed_legs == 0U); CHECK(r.completed_cycles == 0U);
    }
}

TEST_CASE("B7 D244 half-second dwell closes at500000us and never499999us") {
    Sequence owner; APP_REQUIRE(owner.start(0U)); std::uint64_t token = 0U;
    for (std::uint32_t now = 1000U; now <= 500000U; now += 1000U)
        owner.step(now, receipt(++token, 0U, now));
    const auto before = owner.step(500999U, receipt(++token, 0U, 500999U));
    CHECK(before.phase == Phase::DWELL); CHECK(before.completed_legs == 0U);
    const auto closed = owner.step(501000U, receipt(++token, 0U, 501000U));
    CHECK(closed.completed_legs == 1U); CHECK(closed.completed_cycles == 0U);
    CHECK(closed.phase == Phase::REACH); CHECK(closed.leg_index == 1U);
}

TEST_CASE("B7 D244 endpoint loss is immediate and cannot restart dwell") {
    for (unsigned fault = 0U; fault < 5U; ++fault) {
        Sequence owner; APP_REQUIRE(owner.start(0U)); owner.step(1000U, receipt(1U, 0U, 1000U));
        auto lost = receipt(2U, 0U, 2000U);
        if (fault == 0U) lost.enabled = false;
        if (fault == 1U) lost.duty_l = std::nextafter(1.0F, 0.0F);
        if (fault == 2U) lost.duty_r = .999F;
        if (fault == 3U) lost.duty_l = -1.0F;
        if (fault == 4U) lost.duty_l = lost.duty_r = 0.0F;
        const auto terminal = owner.step(2000U, lost); aborted(terminal);
        CHECK(terminal.reason == Reason::ENDPOINT_LOST); CHECK(terminal.endpoint_valid);
        CHECK(terminal.endpoint_started_us == 1000U); CHECK(terminal.last_endpoint_us == 1000U);
        same(owner.step(3000U, receipt(3U, 0U, 3000U)), terminal);
    }
}

TEST_CASE("B7 D244 independent decision and applied gap limits admit2000 and reject2001") {
    for (bool decision_gap : {false, true}) for (std::uint32_t gap : {2000U, 2001U}) {
        Sequence owner; APP_REQUIRE(owner.start(0U));
        const auto first = decision_gap ? 1000U : 2000U;
        owner.step(first, receipt(1U, 0U, 1000U));
        const auto decision = decision_gap ? 1000U + gap : 4000U;
        const auto applied = decision_gap ? 2000U : 1000U + gap;
        const auto r = owner.step(decision, receipt(2U, 0U, applied));
        if (gap == 2000U) CHECK(r.phase == Phase::DWELL);
        else { aborted(r); CHECK(r.reason == Reason::RECEIPT_GAP); }
    }
}

TEST_CASE("B7 D244 duplicate decision is passive while replay on a new decision faults") {
    Sequence owner; APP_REQUIRE(owner.start(0U));
    const auto first = owner.step(1000U, receipt(1U, 0U, 1000U));
    same(owner.step(1000U, receipt(99U, 12U, 500000U)), first);
    const auto bad = owner.step(2000U, receipt(1U, 0U, 1000U)); aborted(bad);
    CHECK(bad.completed_legs == 0U); CHECK(bad.last_endpoint_us == 1000U);
}

TEST_CASE("B7 D244 invalid receipt wrong leg nonfinite and reverse chronology fail closed") {
    for (unsigned fault = 0U; fault < 8U; ++fault) {
        Sequence owner; APP_REQUIRE(owner.start(0U)); owner.step(1000U, receipt(1U, 0U, 1000U));
        auto input = receipt(2U, 0U, 2000U); auto decision = 2000U;
        if (fault == 0U) input.valid = false;
        if (fault == 1U) input.leg_index = 1U;
        if (fault == 2U) input.duty_l = std::numeric_limits<float>::quiet_NaN();
        if (fault == 3U) input.duty_r = std::numeric_limits<float>::infinity();
        if (fault == 4U) input.applied_us = 999U;
        if (fault == 5U) decision = 999U;
        if (fault == 6U) decision = 1000U + 0x80000000U;
        if (fault == 7U) input.applied_us = 2001U;
        const auto terminal = owner.step(decision, input); aborted(terminal);
        CHECK(terminal.completed_legs == 0U); CHECK(terminal.completed_cycles == 0U);
    }
}

TEST_CASE("B7 D244 phase ownership forbids previous forward receipt entering reverse dwell") {
    Sequence owner; APP_REQUIRE(owner.start(0U));
    for (std::uint32_t now = 1000U; now <= 501000U; now += 1000U)
        owner.step(now, receipt(now / 1000U, 0U, now));
    CHECK(owner.report().phase == Phase::REACH); CHECK(owner.report().completed_legs == 1U);
    const auto r = owner.step(502000U, receipt(502U, 0U, 502000U));
    aborted(r); CHECK(r.completed_legs == 1U); CHECK(r.completed_cycles == 0U);
}

TEST_CASE("B7 D244 unsigned clock wrap preserves one full dwell and exact anchors") {
    Sequence owner; constexpr std::uint32_t start = 0xfffffff0U; APP_REQUIRE(owner.start(start));
    for (std::uint32_t tick = 1U; tick <= 501U; ++tick)
        owner.step(start + tick * 1000U, receipt(tick, 0U, start + tick * 1000U));
    const auto r = owner.report(); CHECK(r.completed_legs == 1U); CHECK(r.phase == Phase::REACH);
    CHECK(r.started_us == start); CHECK(r.completed_endpoint_started_us == start + 1000U);
    CHECK(r.completed_endpoint_last_us - r.completed_endpoint_started_us == 500000U);
}

TEST_CASE("B7 D244 reset before start consumes instance and first terminal report is immutable") {
    Sequence owner; CHECK_FALSE(owner.interrupt(Reason::STOP, 1U));
    APP_REQUIRE(owner.interrupt(Reason::RESET_REQUEST, 2U)); const auto terminal = owner.report();
    aborted(terminal); CHECK_FALSE(terminal.started); CHECK(terminal.reason == Reason::RESET_REQUEST);
    CHECK_FALSE(owner.start(3U)); CHECK_FALSE(owner.interrupt(Reason::EDGE, 4U));
    same(owner.step(5U, receipt(1U, 0U, 5U)), terminal);
}

TEST_CASE("B3 B7 D244 real MotorGate remains zero for the full qualified5100ms hold") {
    Rig rig; const auto release = rig.release();
    for (const auto offset : {0U, 1U, 4999999U, 5000000U, 5099999U}) {
        if (offset != 0U) rig.tick(release + offset);
        zero(rig.owner.report(), rig.port); CHECK(rig.owner.report().robot.brownout.phase == Phase::NOT_STARTED);
    }
    const auto go = rig.tick(release + 5100000U);
    CHECK(go.robot.lifecycle.gate.go); CHECK(go.robot.brownout.started);
    CHECK(go.robot.brownout.phase == Phase::REACH); CHECK(go.robot.brownout.started_us == release + 5100000U);
    CHECK(go.robot.outputs.ui_state == core::State::OPENER);
}

TEST_CASE("B6 B7 D244 real Robot Governor Gate reaches full electrical endpoints at low and high voltage") {
    for (float voltage : {9.0F, 12.6F}) {
        Rig rig; rig.source.vbat_v = voltage; rig.begin(); float previous = 0.0F;
        bool full = false;
        for (unsigned tick = 1U; tick <= 1000U; ++tick) {
            const auto& r = rig.next(); CHECK_FALSE(r.robot.contact);
            CHECK(r.robot.outputs.ui_state == core::State::OPENER);
            CHECK(r.robot.outputs.duty_l == r.robot.outputs.duty_r);
            CHECK(r.robot.outputs.duty_l - previous <= .02001F); previous = r.robot.outputs.duty_l;
            CHECK(r.applied.feedback.applied_valid);
            if (r.applied.feedback.duty_l == 1.0F && r.applied.feedback.duty_r == 1.0F) {
                full = true; CHECK(r.applied.feedback.motors_enabled); break;
            }
            if (!MOTORS_ALLOWED && r.robot.brownout.phase == Phase::ABORTED) break;
        }
        CHECK(full == (MOTORS_ALLOWED != 0));
        if (!MOTORS_ALLOWED) { CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U); }
    }
}

TEST_CASE("B7 D244 disabled actual M0 receipts receive no endpoint credit and timeout exactly") {
    if (MOTORS_ALLOWED) return;
    Rig rig; const auto go = rig.begin();
    for (unsigned tick = 1U; tick < 1000U; ++tick) {
        const auto& r = rig.next(); CHECK(r.robot.brownout.phase == Phase::REACH);
        CHECK(r.applied.feedback.applied_valid); CHECK_FALSE(r.applied.feedback.motors_enabled);
        CHECK(r.applied.feedback.duty_l == 0.0F); CHECK(r.applied.feedback.duty_r == 0.0F);
    }
    const auto r = rig.next(); aborted(r.robot.brownout);
    CHECK(r.robot.brownout.reason == Reason::REACH_TIMEOUT); CHECK(r.robot.brownout.terminal_us == go + 1000000U);
    CHECK_FALSE(r.robot.brownout.endpoint_valid); CHECK(r.robot.brownout.completed_legs == 0U);
    CHECK(r.robot.brownout.completed_cycles == 0U); zero(r, rig.port);
    CHECK(rig.next().robot.outputs.ui_state == core::State::STOPPED);
    CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
}

TEST_CASE("B6 B7 D244 actual twenty pairs use zero-before-reversal and retain complete evidence") {
    if (!MOTORS_ALLOWED) return;
    Rig rig; rig.begin(); unsigned completed = 0U, reversals = 0U;
    float previous = 0.0F; int last_sign = 0; bool zero_seen = true;
    bool finished = false;
    for (unsigned tick = 0U; tick < 35000U; ++tick) {
        const auto r = rig.next(); const auto& b = r.robot.brownout;
        APP_REQUIRE(r.applied.feedback.applied_valid); APP_REQUIRE(r.robot.contract_faults == 0U);
        const float applied = r.applied.feedback.duty_l;
        CHECK(r.robot.outputs.duty_l == r.robot.outputs.duty_r);
        if (applied == 0.0F) zero_seen = true;
        else {
            const int sign = applied > 0.0F ? 1 : -1;
            if (last_sign != 0 && sign != last_sign) { CHECK(zero_seen); ++reversals; }
            zero_seen = false; last_sign = sign;
        }
        if (std::fabs(r.robot.outputs.duty_l) > std::fabs(previous))
            CHECK(std::fabs(r.robot.outputs.duty_l) - std::fabs(previous) <= .02001F);
        previous = r.robot.outputs.duty_l;
        if (b.completed_legs != completed) {
            CHECK(b.completed_legs == completed + 1U); ++completed;
            CHECK(b.completed_endpoint_last_us - b.completed_endpoint_started_us == 500000U);
            CHECK(b.completed_cycles == completed / 2U);
        }
        if (b.phase != Phase::COMPLETE) { APP_REQUIRE(b.phase != Phase::ABORTED); continue; }
        CHECK(completed == 40U); CHECK(b.completed_cycles == 20U); CHECK(reversals == 39U);
        CHECK(r.robot.brownout_stopping); zero(r, rig.port); const auto terminal = b;
        CHECK(rig.next().robot.outputs.ui_state == core::State::STOPPED);
        same(rig.owner.report().robot.brownout, terminal); finished = true; break;
    }
    CHECK(finished);
}

TEST_CASE("B3 B4 B7 D244 current STOP edge and stale source preempt final twentieth cycle") {
    if (!MOTORS_ALLOWED) return;
    for (unsigned safety = 0U; safety < 3U; ++safety) {
        Rig rig; rig.source.imu_ok = false; rig.begin(); APP_REQUIRE(rig.beforeFinal());
        if (safety == 0U) rig.source.stop_requested = true;
        if (safety == 1U) rig.source.line_raw_us[0] = 100U;
        if (safety == 2U) rig.source.observations_fresh = false;
        const auto r = rig.next(); aborted(r.robot.brownout);
        CHECK(r.robot.brownout.completed_legs == 39U); CHECK(r.robot.brownout.completed_cycles == 19U);
        if (safety != 1U) { zero(r, rig.port); CHECK(r.robot.outputs.ui_state == core::State::STOPPED); }
        else {
            CHECK(r.robot.brownout.reason == Reason::EDGE); CHECK(r.robot.brownout_edge_interrupted);
            CHECK(r.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
            CHECK_FALSE(r.robot.brownout_stopping); const auto terminal = r.robot.brownout;
            rig.source.line_raw_us[0] = 1000U; bool ended = false, escaped = false;
            for (unsigned tick = 0U; tick < 2000U; ++tick) {
                const auto e = rig.next(); same(e.robot.brownout, terminal);
                CHECK(std::fabs(e.robot.outputs.duty_l) <= .8F); CHECK(std::fabs(e.robot.outputs.duty_r) <= .8F);
                escaped |= e.applied.feedback.duty_l != 0.0F;
                if (!e.robot.brownout_stopping) continue;
                zero(e, rig.port); CHECK(rig.next().robot.outputs.ui_state == core::State::STOPPED);
                ended = true; break;
            }
            CHECK(escaped); CHECK(ended);
        }
    }
}

TEST_CASE("B14 B7 D244 invalid previous applied receipt preempts final cycle before progress") {
    if (!MOTORS_ALLOWED) return;
    ActualRobot rig; rig.go(); APP_REQUIRE(rig.beforeFinal());
    rig.input.previous.applied_valid = false; const auto r = rig.next();
    aborted(r.brownout); CHECK(r.brownout.completed_legs == 39U); CHECK(r.brownout.completed_cycles == 19U);
    CHECK(r.contract_faults != 0U); CHECK(r.outputs.ui_state == core::State::STOPPED); app_test::zero(rig.port);
}

TEST_CASE("B6 B7 D244 MotorGate independently rejects malformed full-duty B7 identity") {
    if (!MOTORS_ALLOWED) return;
    for (unsigned fault = 0U; fault < 6U; ++fault) {
        ActualRobot rig; rig.go(); for (unsigned i = 0U; i < 100U; ++i) rig.next();
        auto forged = rig.result; APP_REQUIRE(forged.outputs.duty_l == 1.0F);
        ++forged.token; rig.port.now = rig.now + 1000U;
        if (fault == 0U) forged.outputs.duty_r = -1.0F;
        if (fault == 1U) forged.brownout.leg_index = 1U;
        if (fault == 2U) forged.brownout.phase = Phase::NOT_STARTED;
        if (fault == 3U) forged.brownout_stopping = true;
        if (fault == 4U) forged.brownout_edge_interrupted = true;
        if (fault == 5U) forged.outputs.ui_state = core::State::ATTACK;
        const auto r = rig.gate.apply(rig.port.now, forged);
        CHECK_FALSE(r.feedback.applied_valid); CHECK(r.fault == motors::Fault::COMMAND);
        app_test::zero(rig.port);
    }
}

TEST_CASE("B14 B7 D244 actual failed motor callback produces no endpoint credit") {
    Rig rig; rig.begin(); for (unsigned i = 0U; i < 100U; ++i) rig.next();
    rig.port.fail_at = rig.port.operations + 1U;
    const auto failed = rig.next(); CHECK_FALSE(failed.applied.feedback.applied_valid);
    CHECK(failed.applied.fault == motors::Fault::IO); app_test::zero(rig.port);
    rig.port.fail_at = 0U; const auto stop = rig.next(); aborted(stop.robot.brownout);
    CHECK(stop.robot.brownout.completed_legs == 0U); CHECK(stop.robot.brownout.completed_cycles == 0U);
    CHECK(stop.robot.outputs.ui_state == core::State::STOPPED); zero(stop, rig.port);
}

TEST_CASE("B7 D244 public Robot reset preserves tokens evidence and defers actual STOP to distinct tick") {
    for (bool active : {false, true}) {
        ActualRobot rig; if (active) { rig.go(); for (unsigned i = 0; i < 100U; ++i) rig.next(); }
        else rig.at(0U);
        const auto before = rig.result; const auto calls = rig.port.count;
        rig.robot.reset(); CHECK(rig.port.count == calls);
        const auto duplicate = rig.at(rig.now); CHECK_FALSE(duplicate.fresh);
        CHECK(duplicate.token == before.token); CHECK(rig.port.count == calls);
        const auto stop = rig.next(); CHECK(stop.token == before.token + 1U);
        CHECK(stop.outputs.ui_state == core::State::STOPPED); CHECK(stop.brownout_stopping);
        aborted(stop.brownout); CHECK(stop.brownout.reason == Reason::RESET_REQUEST);
        CHECK(stop.brownout.started == active); CHECK(stop.brownout.completed_legs == before.brownout.completed_legs);
        app_test::zero(rig.port); const auto terminal = stop.brownout; rig.robot.reset();
        same(rig.next().brownout, terminal);
    }
}

TEST_CASE("B7 D244 real Transaction service reset refuses after completed inhibited STOP epochs") {
    Rig rig; rig.begin(); rig.source.stop_requested = true; rig.next(); rig.next();
    const auto before = rig.owner.report().robot.brownout;
    rig.port.now = rig.now + 1000U; APP_REQUIRE(rig.owner.open());
    const auto calls = rig.port.count; CHECK_FALSE(rig.owner.resetStoppedRobotForService());
    CHECK(rig.port.count == calls); APP_REQUIRE(rig.owner.decide(rig.source)); APP_REQUIRE(rig.owner.finish());
    CHECK(rig.owner.report().robot.outputs.ui_state == core::State::STOPPED);
    same(rig.owner.report().robot.brownout, before); zero(rig.owner.report(), rig.port);
}

TEST_CASE("B7 D244 Robot reset after full completion cannot erase or rearm the trial") {
    if (!MOTORS_ALLOWED) return;
    ActualRobot rig; rig.go(); APP_REQUIRE(rig.beforeFinal());
    const auto complete = rig.next(); APP_REQUIRE(complete.brownout.phase == Phase::COMPLETE);
    const auto calls = rig.port.count; rig.robot.reset(); CHECK(rig.port.count == calls);
    same(rig.at(rig.now).brownout, complete.brownout); CHECK(rig.port.count == calls);
    const auto stop = rig.next(); CHECK(stop.token == complete.token + 1U);
    same(stop.brownout, complete.brownout); CHECK(stop.outputs.ui_state == core::State::STOPPED);
    app_test::zero(rig.port);
}

TEST_CASE("B0 B3 B7 D244 actual Runtime has no fabricated production grants or start") {
    const auto grants = app::configuredSetupGrants(); CHECK_FALSE(grants.opponents);
    CHECK_FALSE(grants.adc_pair); CHECK_FALSE(grants.qtr_exclusive_pads);
    CHECK_FALSE(grants.default_line_thresholds_confirmed); CHECK_FALSE(grants.imu_enabled);
    CHECK_FALSE(grants.local_service_reset);
    service_reset_test::Rig rig; APP_REQUIRE(rig.owner.begin(grants));
    APP_REQUIRE(rig.run(35U)); APP_REQUIRE(rig.run(30U, service_reset_test::START));
    APP_REQUIRE(rig.run(5200U)); CHECK_FALSE(rig.owner.report().initialization_complete);
    CHECK(rig.robot().brownout.phase == Phase::NOT_STARTED); CHECK_FALSE(rig.robot().brownout.started);
    CHECK(rig.fake.highs == 0U); CHECK(rig.fake.nonzero == 0U); CHECK_FALSE(rig.fake.enabled);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 B7 D244 actual configured Runtime qualifies sources holds and refuses service rearm") {
    service_reset_test::Rig rig; APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.owner.report().initialization_complete); APP_REQUIRE(rig.robot().line_available);
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); rig.fake.button_raw = service_reset_test::NONE;
    std::uint32_t release = 0U; bool released = false, go = false;
    for (unsigned tick = 0U; tick < 5200U; ++tick) {
        APP_REQUIRE(rig.next()); const auto& r = rig.robot();
        if (r.lifecycle.gate.start_release) { released = true; release = r.lifecycle.gate.release_us; }
        if (r.lifecycle.gate.go) { go = true; CHECK(rig.owner.transaction().report().decision_us - release >= 5100000U); break; }
        CHECK_FALSE(rig.fake.enabled); CHECK(rig.fake.nonzero == 0U);
    }
    CHECK(released); APP_REQUIRE(go); CHECK(rig.robot().brownout.phase == Phase::REACH);
    CHECK(rig.robot().outputs.ui_state == core::State::OPENER);
    APP_REQUIRE(rig.firstStop()); rig.next(); const auto terminal = rig.robot().brownout;
    aborted(terminal); const auto setups = rig.fake.enable_setups;
    rig.run(30U); rig.run(1040U, service_reset_test::MODE); rig.run(40U);
    CHECK_FALSE(rig.owner.report().service_reset_pending); CHECK_FALSE(rig.owner.report().service_only);
    CHECK_FALSE(rig.owner.report().service_reset_fresh); CHECK(rig.fake.enable_setups == setups);
    same(rig.robot().brownout, terminal); CHECK_FALSE(rig.fake.enabled);
}
#endif
