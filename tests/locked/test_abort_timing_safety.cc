// Drafts D135 safety expectations at the actual Robot and MotorGate boundary.
// Keeps evidence disposition separate from B2 motion priority and real port receipts.
// Unaccepted locked candidates cover hold, edge, STOP, source faults and no retry.
#include "fixtures/p5_abort_fixture.h"

using namespace p5_abort;
namespace {
void physical(const Rig& rig) {
    CHECK(rig.applied.fault == motors::Fault::NONE);
    CHECK(rig.applied.feedback.token == rig.last.token);
    const bool enabled = rig.last.outputs.motors_enabled && MOTORS_ALLOWED != 0;
    CHECK(rig.applied.feedback.motors_enabled == enabled); CHECK(rig.port.enabled == enabled);
    constexpr std::uint32_t periods[] = {1000U, 997U, 251U, 65535U};
    const float demand[] = {rig.last.outputs.duty_l, rig.last.outputs.duty_r};
    for (unsigned side = 0U; side < 2U; ++side) {
        const unsigned channel = 2U * side + (demand[side] < 0.0F ? 1U : 0U);
        const auto pulse = enabled ? static_cast<std::uint32_t>(std::floor(
            std::fabs(static_cast<double>(demand[side])) * periods[channel])) : 0U;
        CHECK(rig.port.pulses[channel] == pulse); CHECK(rig.port.pulses[channel ^ 1U] == 0U);
        const float expected = std::copysign(static_cast<float>(pulse) / periods[channel], demand[side]);
        const float actual = side == 0U ? rig.applied.feedback.duty_l : rig.applied.feedback.duty_r;
        CHECK(actual == doctest::Approx(expected));
    }
    if (!enabled) app_test::zero(rig.port);
}
void noLaterTrace(Rig& rig) {
    const auto before = rig.trace_size; rig.opponent(2U); rig.white(0U);
    rig.input.stop_requested = false; rig.input.observations_fresh = true;
    for (unsigned i = 0U; i < 5U; ++i) { rig.next(); CHECK(count(rig.last) == 0U); }
    CHECK(rig.trace_size == before);
}
std::uint32_t random(std::uint32_t& seed) { return seed = 1664525U * seed + 1013904223U; }
} // namespace

TEST_CASE("B3 R1 D135 every available opener keeps physical zero through exact5100ms hold") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        for (auto base : {0U, 0xffff0000U}) {
            Rig rig; const auto release = rig.release(static_cast<Mode>(mode), base);
            for (auto elapsed : {1U, 1500000U, 1501000U, 4500000U, 5000000U, 5099999U}) {
                rig.step(release + elapsed); CHECK_FALSE(rig.last.lifecycle.gate.go);
                CHECK_FALSE(rig.last.outputs.motors_enabled);
                CHECK(rig.last.outputs.duty_l == 0.0F); CHECK(rig.last.outputs.duty_r == 0.0F);
                CHECK(rig.trace_size == 1U); physical(rig); app_test::zero(rig.port);
            }
            CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
            rig.step(release + 5100000U); CHECK(rig.last.lifecycle.gate.go);
            CHECK(rig.last.outputs.ui_state == State::OPENER); CHECK(rig.trace_size == 1U);
            physical(rig);
        }
    }
}

TEST_CASE("B4 R5 D135 all15 white masks interrupt each available opener before detection handover") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        for (unsigned mask = 1U; mask < 16U; ++mask) {
            CAPTURE(mode); CAPTURE(mask); Rig rig; rig.go(static_cast<Mode>(mode));
            rig.opponent(2U); rig.next(); rig.white(mask); const auto r = rig.next();
            CHECK(r.outputs.ui_state == State::EDGE_ESCAPE); CHECK(r.line_mask == mask);
            CHECK_FALSE(r.contact); terminal(r, INTERRUPTED, 1U, rig.now);
            CHECK(rig.trace_size == 2U); CHECK(count(r, QUALIFIED) == 0U); physical(rig);
            CHECK(std::fabs(r.outputs.duty_l) <= 0.80F); CHECK(std::fabs(r.outputs.duty_r) <= 0.80F);
            const bool fault = mask == 7U || mask == 11U || mask >= 13U;
            CHECK(r.escape_fault == (fault ? edge::EscapeFault::WHITE_PATTERN : edge::EscapeFault::NONE));
            if (fault || mask == 1U || mask == 2U || mask == 3U || mask == 6U || mask == 9U) {
                CHECK(r.outputs.duty_l == 0.0F); CHECK(r.outputs.duty_r == 0.0F);
                for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
            }
            noLaterTrace(rig);
        }
    }
}

TEST_CASE("B2 B13 D135 STOP before cue closes once and physical gate stays inhibited") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        Rig rig; rig.go(static_cast<Mode>(mode)); rig.opponent(2U); rig.next();
        rig.input.stop_requested = true; const auto r = rig.next();
        CHECK(r.outputs.ui_state == State::STOPPED); CHECK_FALSE(r.outputs.motors_enabled);
        CHECK(r.outputs.duty_l == 0.0F); CHECK(r.outputs.duty_r == 0.0F);
        terminal(r, INTERRUPTED, 2U, rig.now); CHECK(rig.trace_size == 2U);
        physical(rig); app_test::zero(rig.port); noLaterTrace(rig);
        CHECK(rig.last.outputs.ui_state == State::STOPPED); app_test::zero(rig.port);
    }
}

TEST_CASE("B2 B15 D135 invalid or stale source wins evidence disposition without overriding safety") {
    for (unsigned scenario = 0U; scenario < 4U; ++scenario) {
        Rig rig; rig.go(); auto value = rig.frontCandidate();
        if (scenario < 3U) value.opponent_read.valid = false;
        if (scenario == 1U) { rig.white(1U); value.line_raw_us[0] = 100U; }
        if (scenario == 2U) value.stop_requested = true;
        if (scenario == 3U) value.observations_fresh = false;
        const auto r = rig.submit(value); terminal(r, INVALID_SOURCE, 1U, rig.now);
        CHECK(rig.trace_size == 2U); CHECK(count(r, HANDOVER) == 0U);
        if (scenario == 0U) CHECK(r.outputs.ui_state == State::TRACK);
        if (scenario == 1U) CHECK(r.outputs.ui_state == State::EDGE_ESCAPE);
        if (scenario >= 2U) { CHECK(r.outputs.ui_state == State::STOPPED); app_test::zero(rig.port); }
        physical(rig); noLaterTrace(rig);
    }
}

TEST_CASE("B2 B4 B15 D135 valid prior application completes before later edge STOP or source fault") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        Rig rig; rig.go(); auto value = rig.frontCandidate(); rig.submit(value, 40U, 80U);
        const auto applied = rig.previous; CHECK(applied.token == rig.last.token);
        CHECK(applied.motors_enabled == (MOTORS_ALLOWED != 0)); physical(rig);
        if (scenario == 0U) rig.white(1U);
        if (scenario == 1U) rig.input.stop_requested = true;
        if (scenario == 2U) rig.input.observations_fresh = false;
        const auto r = rig.next(); CHECK(count(r) == 1U); CHECK(rig.trace_size == 6U);
        CHECK(event(r, APPLIED).t_us == applied.applied_us);
        APP_REQUIRE(r.events.count > 0U); CHECK(r.events.entries[0].type == TIMING);
        CHECK(r.events.entries[0].detail == APPLIED);
        CHECK(r.outputs.ui_state == (scenario == 0U ? State::EDGE_ESCAPE : State::STOPPED));
        physical(rig); noLaterTrace(rig);
    }
}

TEST_CASE("B3 B4 R1 R5 D13510000 fixed seed bounded streams keep hold and first white priority") {
    std::uint32_t seed = 0xd1355afeU;
    for (unsigned stream = 0U; stream < 10000U; ++stream) {
        CAPTURE(stream); Rig rig; const auto release = rig.release(Mode::DIRECT, random(seed));
        const auto mask = 1U + random(seed) % 15U; rig.white(mask);
        for (auto elapsed : {1U, 1500000U, 1501000U, 4500000U, 5099999U}) {
            rig.opponent(random(seed) & 127U); rig.step(release + elapsed);
            CHECK_FALSE(rig.last.lifecycle.gate.go); app_test::zero(rig.port);
            CHECK(rig.trace_size == 1U);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        rig.step(release + 5100000U);
        CHECK(rig.last.outputs.ui_state == State::EDGE_ESCAPE); CHECK(rig.last.line_mask == mask);
        CHECK(count(rig.last, QUALIFIED) == 0U); CHECK(count(rig.last, APPLIED) == 0U);
        physical(rig);
    }
}
