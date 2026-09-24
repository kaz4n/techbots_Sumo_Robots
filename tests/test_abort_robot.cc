// Tests D135 source-to-handover-to-application evidence through public production owners.
// Distinguishes actual Gate receipts from deliberately altered invalid receipt inputs.
// Isolated draft tests cover timing endpoints, causal negatives, priority and no-retry lifetime.
#include "fixtures/p5_abort_fixture.h"

using namespace p5_abort;
namespace {
void preparePhase(Rig& rig, unsigned mode, unsigned phase) {
    rig.go(static_cast<Mode>(mode));
    if (mode == 6U) {
        if (phase == 4U) return;
        rig.opponent(2U); rig.next(); rig.next(); rig.opponent(3U); rig.next(); rig.next();
        APP_REQUIRE(rig.last.outputs.ui_state == State::OPENER); CHECK(rig.trace_size == 1U);
        rig.opponent(0U); rig.next(); rig.next(30000U);
    }
    if (phase == 1U) return;
    const float sign = mode == 2U || mode == 5U ? -1.0F : 1.0F;
    rig.input.raw_heading_deg = sign * (mode == 4U || mode == 5U ? 80.0F : 50.0F);
    rig.next(); APP_REQUIRE(rig.last.outputs.ui_state == State::OPENER);
    if (phase == 2U) return;
    rig.opponent(sign > 0.0F ? 8U : 16U); rig.next(); rig.next();
    APP_REQUIRE(rig.last.outputs.ui_state == State::OPENER); CHECK(rig.trace_size == 1U);
    rig.opponent(0U); rig.next(); rig.next(30000U);
}
void noRetry(Rig& rig) {
    const auto count_before = rig.trace_size; rig.white(0U); rig.opponent(2U);
    rig.next(); rig.next(); rig.next();
    CHECK(rig.trace_size == count_before); CHECK(count(rig.last) == 0U);
}
void complete(Rig& rig, std::uint32_t a) {
    const auto pending = rig.last; const auto previous = rig.previous;
    const auto done = rig.next(); CHECK(count(done, APPLIED) == 1U);
    CHECK(event(done, APPLIED).t_us == a); CHECK(event(done, APPLIED).value == 1U);
    receiptPrefix(done, APPLIED, pending, previous, rig.now); CHECK(rig.trace_size == 6U);
}
void sameMotion(const fsm::RobotResult& a, const fsm::RobotResult& b) {
    CHECK(a.outputs.ui_state == b.outputs.ui_state);
    CHECK(a.outputs.motors_enabled == b.outputs.motors_enabled);
    CHECK(a.outputs.duty_l == b.outputs.duty_l); CHECK(a.outputs.duty_r == b.outputs.duty_r);
    CHECK(a.contact == b.contact); CHECK(a.contract_faults == b.contract_faults);
}
} // namespace

TEST_CASE("B3 B15 D135 header immediately follows accepted START and uses compiled M variant") {
    Rig rig; const auto release = rig.release(); const auto& r = rig.last;
    CHECK(rig.trace_size == 1U); CHECK(event(r, HEADER).t_us == release);
    CHECK(event(r, HEADER).value == (MOTORS_ALLOWED ? 0x0205U : 0x0201U));
    bool paired = false;
    for (unsigned i = 0U; i + 1U < r.events.count; ++i) if (r.events.entries[i].type == core::Event::START_RELEASE) {
        CHECK(r.events.entries[i + 1U].type == TIMING);
        CHECK(r.events.entries[i + 1U].detail == HEADER);
        CHECK(r.events.entries[i + 1U].t_us == r.events.entries[i].t_us); paired = true;
    }
    CHECK(paired); CHECK(count(rig.next()) == 0U);
}

TEST_CASE("B12 B15 D135 DIRECT current front abort at GO needs no prior OPENER or positive receipt") {
    for (auto base : {0U, 0xffb00000U}) {
        Rig rig; const auto release = rig.release(Mode::DIRECT, base); rig.services(release);
        rig.opponent(2U); rig.step(release + 5099000U);
        CHECK(rig.last.outputs.ui_state == State::COUNTDOWN); app_test::zero(rig.port);
        const auto d = release + 5100000U; auto value = rig.at(d, 200U);
        value.opponent_read = {true, d - 150U, d - 120U}; const auto r = rig.submit(value, 40U, 80U);
        CHECK(r.lifecycle.gate.go);
        qualified(rig, r, 3U, 0U, 1U, 2U, State::TRACK, d - 150U, d - 120U);
        CHECK_FALSE(r.contact); CHECK(r.outputs.duty_l <= 0.30F); CHECK(r.outputs.duty_r <= 0.30F);
        complete(rig, d + 40U); CHECK(rig.last.outputs.ui_state == State::TRACK);
        rig.next(); CHECK(rig.last.outputs.ui_state == State::ATTACK); noRetry(rig);
    }
}

TEST_CASE("B12 B15 D135 actual Robot phase and mask govern qualified abort independent of final state") {
    for (unsigned mode : {1U, 2U, 4U, 5U, 6U}) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        for (unsigned phase = 1U; phase <= (mode == 6U ? 4U : 3U); ++phase) {
            for (unsigned mask : {2U, 8U, 16U, 32U, 64U, 10U, 18U}) {
                unsigned cause = permittedCue(mode, phase, 1U, mask, false) ? 1U :
                                 permittedCue(mode, phase, 2U, mask, false) ? 2U : 0U;
                if (cause == 0U) continue;
                Rig rig; preparePhase(rig, mode, phase); auto value = rig.frontCandidate(mask);
                const auto d = value.t_us; const auto r = rig.submit(value, 40U, 80U);
                const auto state = mask & 7U ? State::TRACK : State::DEFEND_TURN;
                qualified(rig, r, mode, phase, cause, mask, state, d - 150U, d - 120U);
                CHECK_FALSE(r.contact); complete(rig, d + 40U); noRetry(rig);
            }
        }
    }
}

TEST_CASE("B12 D135 phase advancement can qualify a persistent front on the same observation") {
    for (unsigned mode : {1U, 2U, 4U, 5U}) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        Rig rig; preparePhase(rig, mode, 1U); rig.opponent(2U); rig.next(); rig.next();
        CHECK(rig.last.outputs.ui_state == State::OPENER); CHECK(rig.trace_size == 1U);
        const float sign = mode == 2U || mode == 5U ? -1.0F : 1.0F;
        rig.input.raw_heading_deg = sign * (mode >= 4U ? 80.0F : 50.0F);
        auto value = rig.at(rig.now + 1000U, 200U); const auto d = value.t_us;
        const auto r = rig.submit(value);
        qualified(rig, r, mode, 2U, 1U, 2U, State::TRACK, d - 200U, d);
    }
}

TEST_CASE("B5 B12 D135 held effective front remains eligible after fresh raw electrical deassertion") {
    for (unsigned mode : {1U, 2U}) {
        Rig rig; preparePhase(rig, mode, 1U); rig.opponent(2U); rig.next(); rig.next();
        APP_REQUIRE(rig.last.opponent_mask == 2U); CHECK(rig.trace_size == 1U);
        rig.opponent(0U); rig.input.raw_heading_deg = mode == 1U ? 50.0F : -50.0F;
        const auto d = rig.now + 1000U; const auto r = rig.step(d);
        CHECK(rig.input.opp_raw_mask == 0x78U); CHECK(r.opponent_mask == 2U);
        qualified(rig, r, mode, 2U, 1U, 2U, State::TRACK, d, d); complete(rig, d);
    }
}

TEST_CASE("B12 D135 DIRECT snapshot-only is NOT_ABORT even when current perception routes side") {
    for (unsigned current : {0U, 8U}) {
        Rig rig; const auto release = rig.release(); rig.services(release);
        rig.opponent(2U); rig.step(release + 5000000U); rig.next();
        APP_REQUIRE(rig.last.lifecycle.services.opponent_snapshot == 2U);
        rig.opponent(current); rig.step(release + 5060000U);
        APP_REQUIRE(rig.last.lifecycle.services.opponent_snapshot == 2U);
        const auto r = rig.step(release + 5100000U);
        CHECK(r.opponent_mask == current); CHECK(r.lifecycle.gate.go);
        CHECK(r.outputs.ui_state == (current ? State::DEFEND_TURN : State::SEARCH));
        terminal(r, NOT_ABORT, 1U, rig.now); CHECK(rig.trace_size == 2U); noRetry(rig);
    }
}

TEST_CASE("B12 D135 genuine current front beats a simultaneous saved-front-only classification") {
    Rig rig; const auto release = rig.release(); rig.services(release);
    rig.opponent(2U); rig.step(release + 5000000U); rig.next();
    APP_REQUIRE(rig.last.lifecycle.services.opponent_snapshot == 2U);
    const auto d = release + 5100000U; const auto r = rig.step(d);
    qualified(rig, r, 3U, 0U, 1U, 2U, State::TRACK, d, d, true);
    complete(rig, d);
}

TEST_CASE("B12 D135 natural DIRECT and front-present WAIT expiry never masquerade as aborts") {
    for (auto mode : {Mode::DIRECT, Mode::WAIT}) {
        if (!core::modeAvailable(mode)) continue;
        Rig rig; const auto go = rig.go(mode);
        if (mode == Mode::WAIT) { rig.opponent(2U); rig.next(); rig.next(); }
        const auto duration = mode == Mode::DIRECT ? 400000U : 2000000U;
        CHECK(count(rig.step(go + duration - 1U)) == 0U);
        const auto end = rig.step(go + duration);
        CHECK(end.outputs.ui_state == (mode == Mode::WAIT ? State::TRACK : State::SEARCH));
        terminal(end, NOT_ABORT, 2U, rig.now); CHECK(rig.trace_size == 2U); noRetry(rig);
    }
}

TEST_CASE("B12 D055 D135 WAIT cue continues the attempt and delegated abort preserves mode6") {
    if (!core::modeAvailable(Mode::WAIT)) return;
    Rig rig; rig.go(Mode::WAIT); rig.opponent(2U); rig.next(); rig.next();
    rig.opponent(3U); rig.next(); rig.next(); CHECK(rig.trace_size == 1U);
    CHECK(rig.last.outputs.ui_state == State::OPENER);
    CHECK(rig.last.outputs.duty_l > 0.0F); CHECK(rig.last.outputs.duty_r < 0.0F);
    rig.input.raw_heading_deg = 50.0F; const auto d = rig.now + 1000U; const auto r = rig.step(d);
    qualified(rig, r, 6U, 2U, 1U, 3U, State::TRACK, d, d); complete(rig, d);
}

TEST_CASE("B15 D135 actual Transaction Gate recorder preserve early exact and late application times") {
    for (auto delay : {0U, 999U, 1000U, 1001U, 50000U}) {
        TxRig rig; rig.go(); rig.opponent(2U); rig.next(); const auto d = rig.now + 1000U;
        rig.source.opponent_read = {true, d - 150U, d - 120U}; rig.port.settle_us = delay;
        const auto candidate = rig.cycle(d - 200U, d, d + delay + 80U);
        CHECK(candidate.applied.feedback.applied_us == d + delay);
        CHECK(candidate.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
        suffix(candidate.robot, {READ_START, READ_END, QUALIFIED, HANDOVER});
        CHECK(stored(rig.owner.recording(), QUALIFIED) == 1U);
        CHECK(stored(rig.owner.recording(), APPLIED) == 0U);
        rig.port.settle_us = 0U; const auto done = rig.at(d + delay + 1000U);
        const auto applied = event(done.robot, APPLIED); CHECK(applied.t_us == d + delay);
        const auto elapsed = static_cast<std::uint32_t>(applied.t_us - event(candidate.robot, QUALIFIED).t_us);
        CHECK(elapsed == delay); CHECK((elapsed <= 1000U) == (delay <= 1000U));
        CHECK(stored(rig.owner.recording(), APPLIED) == 1U);
        // Sparse host epochs intentionally skip frames; event integrity is independent.
        CHECK(rig.owner.recording().incomplete());
        CHECK(rig.owner.recording().summary().skipped_frames > 0U);
        CHECK(rig.owner.recording().summary().upstream_event_rejected == 0U);
        CHECK(rig.owner.recording().summary().event_semantic_rejected == 0U);
        if (!MOTORS_ALLOWED) app_test::zero(rig.port);
    }
}

TEST_CASE("B15 D135 valid common-anchor source and receipt chronology survives numerical clock wrap") {
    Rig anchor; anchor.go(); const auto prefix = anchor.frontCandidate().t_us;
    Rig rig; rig.go(Mode::DIRECT, 0U - prefix);
    auto value = rig.frontCandidate(); const auto d = value.t_us;
    CHECK(d == 0U); CHECK(value.opponent_read.started_us > d);
    const auto r = rig.submit(value, 40U, 80U);
    qualified(rig, r, 3U, 0U, 1U, 2U, State::TRACK, d - 150U, d - 120U);
    complete(rig, d + 40U); CHECK_FALSE(rig.last.timing_incomplete);
}

TEST_CASE("B15 D135 bad read metadata closes INVALID_SOURCE without altering admitted motion") {
    for (unsigned scenario = 0U; scenario < 7U; ++scenario) {
        Rig honest, changed; honest.go(); changed.go();
        const auto good_input = honest.frontCandidate(); auto bad_input = changed.frontCandidate();
        const auto d = bad_input.t_us;
        if (scenario == 0U) bad_input.opponent_read.valid = false;
        if (scenario == 1U) bad_input.opponent_read.started_us = d - 201U;
        if (scenario == 2U) bad_input.opponent_read.completed_us = d + 1U;
        if (scenario == 3U) bad_input.opponent_read.started_us = d - 119U;
        if (scenario == 4U) bad_input.timing.start_valid = false;
        if (scenario == 5U) bad_input.timing.explicit_start = false;
        if (scenario == 6U) bad_input.opponent_read.started_us = d + 0x80000000U;
        const auto good = honest.submit(good_input), bad = changed.submit(bad_input);
        sameMotion(good, bad); terminal(bad, INVALID_SOURCE, 1U, d);
        CHECK(changed.trace_size == 2U); noRetry(changed);
    }
}

TEST_CASE("B15 D135 altered immediate receipt rejects whole token chronology duty and M1 disabled EN") {
    for (unsigned scenario = 0U; scenario < 10U; ++scenario) {
        if (scenario == 9U && !MOTORS_ALLOWED) continue;
        Rig rig; rig.go(); const auto r = rig.submit(rig.frontCandidate(), 40U, 80U);
        APP_REQUIRE(count(r, HANDOVER) == 1U); auto value = rig.at(rig.now + 1000U);
        if (scenario == 0U) value.previous.token ^= (1ULL << 32U);
        if (scenario == 1U) value.previous.applied_valid = false;
        if (scenario == 2U) value.previous.duration_valid = false;
        if (scenario == 3U) ++value.previous.execution_us;
        if (scenario == 4U) value.previous.applied_us = rig.now - 1U;
        if (scenario == 5U) value.previous.completed_us = value.previous.applied_us - 1U;
        if (scenario == 6U) value.timing.started_us = rig.now + 79U;
        if (scenario == 7U) value.previous.duty_l = 1.0F;
        if (scenario == 8U) value.previous.duty_l = -1.0F;
        if (scenario == 9U) {
            value.previous.motors_enabled = false; value.previous.duty_l = value.previous.duty_r = 0.0F;
        }
        const auto rejected = rig.submit(value);
        CHECK(count(rejected, INVALID_RECEIPT) == 1U); CHECK(count(rejected, APPLIED) == 0U);
        CHECK(event(rejected, INVALID_RECEIPT).t_us == value.t_us); CHECK(rig.trace_size == 6U);
        receiptPrefix(rejected, INVALID_RECEIPT, r, value.previous, value.t_us); noRetry(rig);
    }
}

TEST_CASE("B15 D135 duplicate decision cannot consume receipt or replay qualified suffix") {
    Rig rig; rig.go(); auto value = rig.frontCandidate(); rig.submit(value);
    const auto size = rig.trace_size, operations = rig.port.operations;
    auto duplicate = rig.at(rig.now); duplicate.stop_requested = true;
    const auto r = rig.robot.step(duplicate);
    CHECK_FALSE(r.fresh); CHECK(r.events.count == 0U); CHECK(rig.port.operations == operations);
    CHECK(rig.trace_size == size); complete(rig, value.t_us);
}

TEST_CASE("B15 D135 reset and missing Transaction tail cannot manufacture applied acknowledgement") {
    Rig rig; rig.go(); rig.submit(rig.frontCandidate()); APP_REQUIRE(rig.trace_size == 5U);
    rig.reset(); rig.go(); CHECK(rig.trace_size == 1U);
    rig.submit(rig.frontCandidate()); complete(rig, rig.now);
    TxRig tx; tx.go(); tx.opponent(2U); tx.next(); tx.next();
    CHECK(stored(tx.owner.recording(), HANDOVER) == 1U);
    CHECK(stored(tx.owner.recording(), APPLIED) == 0U);
    tx.owner.abort(); CHECK(tx.owner.recording().incomplete());
    CHECK(stored(tx.owner.recording(), APPLIED) == 0U); app_test::zero(tx.port);
}
