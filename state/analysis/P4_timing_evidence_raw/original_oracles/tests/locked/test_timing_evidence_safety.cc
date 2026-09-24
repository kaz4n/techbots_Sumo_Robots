// Freezes D129 evidence exclusions without changing prior motion safety oracles.
// Distinguishes actual Transaction/Gate callbacks from labeled synthetic faults.
// New independent M0/M1 cases exercise hold, priority, receipts and Runtime reset.
#include "../p4_timing_fixture.h"

using namespace p4_time;

TEST_CASE("B3 R1 D129 actual Gate stays electrically zero through full hold including wrap") {
    for (auto base : {0U, 0xfff00000U}) {
        TxRig rig; rig.opponent(2U); const auto release = rig.release(base);
        CHECK(event(rig.owner.report().robot, Detail::HEADER).t_us == release);
        for (auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto r = rig.at(release + age); CHECK_FALSE(r.robot.outputs.motors_enabled);
            CHECK(r.robot.outputs.duty_l == 0.0F); CHECK(r.robot.outputs.duty_r == 0.0F);
            CHECK(count(r.robot) == 0U); app_test::zero(rig.port);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.at(release + 5100000U); CHECK(go.robot.lifecycle.gate.go);
        CHECK(go.robot.outputs.ui_state == State::SEARCH); CHECK(count(go.robot) == 0U);
        CHECK(go.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
        CHECK(go.applied.feedback.duty_l == 0.0F); CHECK(go.applied.feedback.duty_r == 0.0F);
    }
}

TEST_CASE("B6 B9 B15 D129 actual Transaction and Gate timestamps complete only real M1 applied approach") {
    TxRig rig; const auto loss = rig.approach() + 1000U; rig.opponent(0U);
    rig.source.opponent_read = {true, loss - 150U, loss - 120U};
    const auto onset = rig.cycle(loss - 200U, loss, loss + 80U);
    if (MOTORS_ALLOWED) pair(onset.robot, loss - 150U, loss - 120U);
    else CHECK(count(onset.robot) == 0U);
    const auto d = loss + 30000U; rig.source.opponent_read = {true, d, d};
    rig.port.clear(d); rig.port.work_us = 2U;
    const auto brake = rig.cycle(d, d, d + 80U);
    CHECK(brake.robot.outputs.ui_state == State::SEARCH); CHECK(brake.robot.outputs.motors_enabled);
    CHECK(brake.robot.outputs.duty_l == 0.0F); CHECK(brake.robot.outputs.duty_r == 0.0F);
    CHECK(brake.applied.feedback.applied_us == d + (MOTORS_ALLOWED ? 14U : 12U));
    CHECK(brake.applied.feedback.token == brake.robot.token); CHECK(brake.applied.feedback.applied_valid);
    for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
    CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0)); rig.port.work_us = 0U;
    const auto tail = rig.at(d + 1000U);
    if (MOTORS_ALLOWED) {
        CHECK(event(brake.robot, Detail::LOSS_BRAKE_DECISION).t_us == d);
        CHECK(event(tail.robot, Detail::LOSS_ZERO_APPLIED).t_us == d + 14U);
        CHECK(stored(rig.owner.recording(), Detail::LOSS_ZERO_APPLIED) == 1U);
    } else {
        CHECK(count(brake.robot) == 0U); CHECK(count(tail.robot) == 0U);
        CHECK(stored(rig.owner.recording(), Detail::LOSS_READ_START) == 0U);
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
    }
    CHECK_FALSE(tail.robot.timing_incomplete); CHECK(tail.robot.contract_faults == 0U);
}

TEST_CASE("B6 D129 real downward PWM quantization cannot substitute requested positive duty for evidence") {
    Rig rig(true, true); rig.approach();
    APP_REQUIRE(rig.last.outputs.duty_l > 0.0F && rig.last.outputs.duty_r > 0.0F);
    CHECK(rig.previous.duty_l == 0.0F); CHECK(rig.previous.duty_r == 0.0F);
    CHECK(rig.previous.motors_enabled == (MOTORS_ALLOWED != 0)); CHECK(rig.port.nonzero == 0U);
    const auto loss = rig.onset(); CHECK(count(rig.last) == 0U);
    const auto d = rig.brake(loss); CHECK(count(rig.step(d + 1000U)) == 0U);
    CHECK(rig.trace_size == 1U);
}

TEST_CASE("B4 R5 D129 synthetic edge preemption excludes every white mask without a false brake completion") {
    for (unsigned mask = 1U; mask < 16U; ++mask) for (bool observing : {false, true}) {
        Rig rig; rig.approach(); if (observing) rig.onset();
        const auto t = rig.now + 1000U; rig.opponent(0U); rig.white(mask);
        const auto r = rig.step(t); CHECK(r.outputs.ui_state == State::EDGE_ESCAPE);
        terminal(r, Detail::INTERRUPTED_EDGE, t); CHECK(count(r, Detail::LOSS_READ_START) == 0U);
        CHECK(count(r, Detail::LOSS_BRAKE_DECISION) == 0U);
        const auto size = rig.trace_size; rig.white(0U); rig.step(t + 1000U);
        CHECK(rig.trace_size == size);
    }
}

TEST_CASE("B3 B5 B14 D129 current STOP contact and stale source exclude before first clear pair") {
    for (unsigned scenario = 0U; scenario < 4U; ++scenario) for (bool observing : {false, true}) {
        Rig rig; rig.approach(); if (observing) rig.onset();
        const auto t = rig.now + 1000U; rig.opponent(0U); auto value = rig.at(t);
        Detail expected = Detail::INTERRUPTED_STOP_FAULT;
        if (scenario == 0U) value.stop_requested = true;
        if (scenario == 1U) { value.ax_g = 2.0F; expected = Detail::EXCLUDED_CONTACT_ROUTE; }
        if (scenario == 2U) { value.observations_fresh = false; value.stop_requested = true;
            value.line_raw_us[0] = 100U; expected = Detail::INVALID_SOURCE_TIME; }
        if (scenario == 3U) value.previous.token ^= (1ULL << 32U);
        const auto r = rig.submit(value); terminal(r, expected, t);
        CHECK(count(r, Detail::LOSS_READ_START) == 0U); CHECK(count(r, Detail::LOSS_BRAKE_DECISION) == 0U);
        if (scenario == 1U) CHECK(r.contact);
        else { CHECK(r.outputs.ui_state == State::STOPPED); CHECK_FALSE(r.outputs.motors_enabled); }
    }
}

TEST_CASE("B9 B14 D129 pending synthetic brake receipt requires exact full token duty permission and timing") {
    for (unsigned scenario = 0U; scenario < 11U; ++scenario) {
        CAPTURE(scenario); Rig rig; rig.approach(); const auto loss = rig.onset(); const auto d = rig.brake(loss);
        auto value = rig.at(d + 1000U);
        if (scenario == 0U) value.previous.token ^= (1ULL << 32U);
        if (scenario == 1U) value.previous.applied_valid = false;
        if (scenario == 2U) value.previous.motors_enabled = false;
        if (scenario == 3U) value.previous.duty_l = .001F;
        if (scenario == 4U) value.previous.duty_r = std::numeric_limits<float>::quiet_NaN();
        if (scenario == 5U) value.previous.duration_valid = false;
        if (scenario == 6U) ++value.previous.execution_us;
        if (scenario == 7U) value.previous.applied_us = d - 1U;
        if (scenario == 8U) value.previous.completed_us = d - 1U;
        if (scenario == 9U) value.timing.started_us = d - 1U;
        if (scenario == 10U) value.timing.start_valid = false;
        const auto rejected = rig.submit(value); CHECK(count(rejected) == 1U);
        CHECK(event(rejected, Detail::INVALID_RECEIPT).t_us == d + 1000U);
        CHECK(count(rejected, Detail::LOSS_ZERO_APPLIED) == 0U); CHECK(rig.trace_size == 5U);
        CHECK(count(rig.step(d + 2000U)) == 0U); CHECK(rig.trace_size == 5U);
    }
}

TEST_CASE("B4 B9 B15 D129 valid prior synthetic zero completes before current edge STOP or raw reassertion") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        Rig rig; rig.approach(); const auto loss = rig.onset(); const auto d = rig.brake(loss, 7U, 9U);
        if (scenario == 0U) rig.white(1U);
        if (scenario == 1U) rig.input.stop_requested = true;
        if (scenario == 2U) rig.opponent(2U);
        const auto r = rig.step(d + 1000U); CHECK(count(r) == 1U);
        CHECK(event(r, Detail::LOSS_ZERO_APPLIED).t_us == d + 7U);
        APP_REQUIRE(r.events.count > 0U); CHECK(r.events.entries[0].type == core::Event::TIMING);
        CHECK(r.events.entries[0].detail == 4U); CHECK(rig.trace_size == 5U);
        if (scenario == 0U) CHECK(r.outputs.ui_state == State::EDGE_ESCAPE);
        if (scenario == 1U) { CHECK(r.outputs.ui_state == State::STOPPED); CHECK_FALSE(r.outputs.motors_enabled); }
    }
}

TEST_CASE("B15 D095 D129 actual Transaction abort after brake cannot fabricate the missing receipt tail") {
    TxRig rig; const auto loss = rig.approach() + 1000U; rig.opponent(0U); rig.at(loss);
    rig.at(loss + 30000U);
    CHECK(stored(rig.owner.recording(), Detail::LOSS_BRAKE_DECISION) == (MOTORS_ALLOWED ? 1U : 0U));
    const auto retained = rig.owner.recording().events().size(); rig.owner.abort();
    CHECK(rig.owner.report().phase == app::Phase::FAULT); CHECK(rig.owner.report().fault == app::Fault::ABORTED);
    app_test::zero(rig.port); CHECK(rig.owner.recording().events().size() == retained);
    CHECK(stored(rig.owner.recording(), Detail::LOSS_ZERO_APPLIED) == 0U);
    CHECK(stored(rig.owner.recording(), Detail::INVALID_RECEIPT) == 0U);
}

TEST_CASE("B15 D095 D129 actual Transaction clock rejection does not create a new Robot timing event") {
    TxRig rig; rig.approach(); const auto last = rig.owner.report().robot;
    const auto receipt_token = rig.owner.previous().token; const auto retained = rig.owner.recording().events().size();
    rig.port.now = rig.now; APP_REQUIRE(rig.owner.open()); CHECK_FALSE(rig.owner.decide(rig.source));
    CHECK(rig.owner.report().fault == app::Fault::CLOCK); CHECK_FALSE(rig.owner.report().decision_made);
    CHECK(rig.owner.report().robot.token == 0U); CHECK(rig.owner.previous().token == receipt_token);
    CHECK(receipt_token == last.token); CHECK(count(rig.owner.report().robot) == 0U);
    CHECK(rig.owner.recording().events().size() == retained); app_test::zero(rig.port);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 B5 D129 configured Runtime projects the one actual complete opponent acquisition interval") {
    service_reset_test::Rig rig; rig.fake.opponent_mask = 2U ^ 0x78U;
    APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.robot().line_available && !rig.robot().line_raw_mode);
    APP_REQUIRE(!rig.robot().line_start_rearming && !rig.robot().line_calibration_hold);
    APP_REQUIRE(rig.robot().button_available && rig.robot().button_level == Button::NONE);
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); APP_REQUIRE(rig.run(5150U));
    APP_REQUIRE(rig.robot().outputs.ui_state == State::ATTACK); APP_REQUIRE(!rig.robot().contact);
    rig.fake.count = 0U; const auto reads = rig.fake.opponents;
    rig.fake.opponent_work = 13U; rig.fake.opponent_mask = 0x78U; APP_REQUIRE(rig.next());
    CHECK(rig.fake.opponents == reads + 1U); CHECK(rig.fake.seen(runtime_test::Call::OPP) == 1U);
    std::uint32_t start = 0U; bool found = false;
    for (unsigned i = 0U; i < rig.fake.count && i < rig.fake.trace.size(); ++i)
        if (rig.fake.trace[i].kind == runtime_test::Call::OPP) { start = rig.fake.trace[i].at; found = true; }
    APP_REQUIRE(found); const auto& input = rig.owner.decisionInput();
    CHECK(input.opponent_read.valid); CHECK(input.opponent_read.started_us == start);
    CHECK(input.opponent_read.completed_us == start + 13U);
    if (MOTORS_ALLOWED) pair(rig.robot(), start, start + 13U); else CHECK(count(rig.robot()) == 0U);
    bool decision_seen = false, completion_seen = false; std::uint32_t applied = 0U;
    for (unsigned i = 0U; i < 50U; ++i) {
        APP_REQUIRE(rig.next());
        if (count(rig.robot(), Detail::LOSS_BRAKE_DECISION)) {
            decision_seen = true; applied = rig.owner.transaction().report().applied.feedback.applied_us;
        }
        if (count(rig.robot(), Detail::LOSS_ZERO_APPLIED)) {
            CHECK(decision_seen); CHECK(event(rig.robot(), Detail::LOSS_ZERO_APPLIED).t_us == applied);
            completion_seen = true;
        }
    }
    CHECK(decision_seen == (MOTORS_ALLOWED != 0)); CHECK(completion_seen == (MOTORS_ALLOWED != 0));
}

TEST_CASE("B14 D129 configured Runtime rejects incomplete acquisition evidence and cannot rearm after D103") {
    service_reset_test::Rig rig; rig.fake.opponent_mask = 2U ^ 0x78U;
    APP_REQUIRE(rig.begin(true, true, false)); APP_REQUIRE(rig.run(35U));
    APP_REQUIRE(rig.run(30U, service_reset_test::START)); APP_REQUIRE(rig.run(5150U));
    APP_REQUIRE(rig.robot().outputs.ui_state == State::ATTACK); rig.fake.opponent_error = 2U;
    APP_REQUIRE(rig.next()); CHECK_FALSE(rig.owner.decisionInput().opponent_read.valid);
    CHECK_FALSE(rig.robot().outputs.motors_enabled); CHECK_FALSE(rig.fake.enabled);
    if (MOTORS_ALLOWED) CHECK(count(rig.robot(), Detail::INVALID_SOURCE_TIME) == 1U);
    else CHECK(count(rig.robot()) == 0U);
    rig.fake.opponent_error = 0U; APP_REQUIRE(rig.next());
    const auto retained = rig.owner.transaction().recording().events().size();
    const auto highs = rig.fake.highs, nonzero = rig.fake.nonzero;
    APP_REQUIRE(rig.pending()); APP_REQUIRE(rig.next()); APP_REQUIRE(rig.owner.report().service_only);
    APP_REQUIRE(rig.run(30U)); APP_REQUIRE(rig.run(30U, service_reset_test::START));
    rig.fake.button_raw = service_reset_test::NONE;
    for (unsigned i = 0U; i < 5150U; ++i) {
        APP_REQUIRE(rig.next()); CHECK_FALSE(rig.robot().lifecycle.gate.start_release);
        CHECK_FALSE(rig.robot().lifecycle.gate.go); CHECK(count(rig.robot()) == 0U);
        CHECK_FALSE(rig.fake.enabled); CHECK(rig.fake.highs == highs); CHECK(rig.fake.nonzero == nonzero);
    }
    CHECK(rig.owner.transaction().recording().events().size() == retained);
    CHECK(stored(rig.owner.transaction().recording(), Detail::HEADER) == 1U);
}
#endif
