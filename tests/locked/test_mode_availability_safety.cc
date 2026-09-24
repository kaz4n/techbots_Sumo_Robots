// Locks B3/B4/B13 safety while D134 removes optional choices from the menu.
// Exercises actual Robot and MotorGate callbacks with independently timed stimuli.
// New frozen M0/M1 configured tests retain hold, edge and STOP priority for every choice.
#include "doctest.h"
#include "../fixtures/mode_availability_fixture.h"

using namespace mode_test;

namespace {
struct EdgeDuty { float left; float right; };
EdgeDuty rowDuty(unsigned mask) {
    // B4.2/D021 at nominal voltage and unchanged heading; these rows do not brake.
    switch (mask) {
        case 4U: return {0.80F, 0.56F};
        case 5U: return {0.80F, -0.80F};
        case 8U: return {0.56F, 0.80F};
        case 10U: return {-0.80F, 0.80F};
        case 12U: return {0.80F, 0.80F};
        default: return {0.0F, 0.0F};
    }
}
void initialEdgeDuty(float actual, float previous, float target, std::uint32_t elapsed) {
    CHECK(actual * target >= 0.0F);
    CHECK(std::fabs(actual) <= std::fabs(target));
    if (previous * target < 0.0F) {
        CHECK(actual == 0.0F); // B6 requires a reversal brake before opposite acceleration.
        return;
    }
    const float budget = 0.02F * (static_cast<float>(elapsed) / 1000.0F);
    const float reachable = std::fabs(previous) + budget;
    const float magnitude = reachable < std::fabs(target) ? reachable : std::fabs(target);
    CHECK(actual == doctest::Approx(std::copysign(magnitude, target)));
}
void physicalEdge(const Rig& rig, bool permitted) {
    CHECK(rig.last.contract_faults == 0U);
    CHECK(rig.last.outputs.motors_enabled == permitted);
    CHECK(rig.applied.fault == motors::Fault::NONE);
    CHECK(rig.applied.feedback.token == rig.last.token);
    const bool enabled = permitted && MOTORS_ALLOWED != 0;
    CHECK(rig.applied.feedback.motors_enabled == enabled);
    CHECK(rig.port.enabled == enabled);
    constexpr std::uint32_t periods[] = {1000U, 997U, 251U, 65535U};
    const float demands[] = {rig.last.outputs.duty_l, rig.last.outputs.duty_r};
    for (unsigned side = 0U; side < 2U; ++side) {
        const unsigned channel = 2U * side + (demands[side] < 0.0F ? 1U : 0U);
        const auto pulse = enabled ? static_cast<std::uint32_t>(std::floor(
            std::fabs(static_cast<double>(demands[side])) * periods[channel])) : 0U;
        CHECK(rig.port.pulses[channel] == pulse);
        CHECK(rig.port.pulses[channel ^ 1U] == 0U);
        const float expected = std::copysign(static_cast<float>(pulse) /
                                            static_cast<float>(periods[channel]), demands[side]);
        const float actual = side == 0U ? rig.applied.feedback.duty_l : rig.applied.feedback.duty_r;
        CHECK(actual == doctest::Approx(expected));
    }
    if (!enabled) app_test::zero(rig.port);
}
void edgeRow(Rig& rig, unsigned mask, core::Outputs previous, std::uint32_t elapsed) {
    const bool fault = mask == 7U || mask == 11U || mask == 13U || mask == 14U || mask == 15U;
    CHECK(rig.last.escape_fault == (fault ? edge::EscapeFault::WHITE_PATTERN : edge::EscapeFault::NONE));
    physicalEdge(rig, !fault);
    const auto target = rowDuty(mask);
    if (target.left == 0.0F && target.right == 0.0F) {
        CHECK(rig.last.outputs.duty_l == 0.0F); CHECK(rig.last.outputs.duty_r == 0.0F);
        for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
        CHECK(rig.applied.feedback.duty_l == 0.0F);
        CHECK(rig.applied.feedback.duty_r == 0.0F);
        return;
    }
    initialEdgeDuty(rig.last.outputs.duty_l, previous.duty_l, target.left, elapsed);
    initialEdgeDuty(rig.last.outputs.duty_r, previous.duty_r, target.right, elapsed);
    // Forty ms reaches0.80 under B6 after reversal, before any B4 row deadline.
    rig.next(40000U);
    CHECK(rig.last.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(rig.last.line_mask == mask); CHECK_FALSE(rig.last.contact);
    CHECK(rig.last.escape_fault == edge::EscapeFault::NONE);
    CHECK(rig.last.outputs.duty_l == doctest::Approx(target.left));
    CHECK(rig.last.outputs.duty_r == doctest::Approx(target.right));
    physicalEdge(rig, true);
}
} // namespace

TEST_CASE("B3 R1 D134 every available mode and button source keeps the exact full hold") {
    for (bool explicit_source : {false, true}) for (unsigned id = 1U; id <= 6U; ++id) {
        if (!expected(id)) continue;
        for (auto base : {0U, 0xffff0000U}) {
            CAPTURE(explicit_source); CAPTURE(id); CAPTURE(base); Rig rig(explicit_source);
            rig.prime(base); rig.select(static_cast<Mode>(id)); const auto release = rig.release();
            zero(rig); CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
            for (auto elapsed : {1U, 1500000U, 1501000U, 4500000U, 5000000U, 5099999U}) {
                rig.at(release + elapsed); CHECK_FALSE(rig.last.lifecycle.gate.go); zero(rig);
                CHECK(rig.last.running_mode == static_cast<Mode>(id));
                CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
            }
            rig.at(release + 5100000U); CHECK(rig.last.lifecycle.gate.go);
            CHECK(rig.last.outputs.ui_state == State::OPENER);
            CHECK(rig.last.outputs.motors_enabled); governed(rig, 0.85F);
            CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0));
        }
    }
}

TEST_CASE("B4 R5 D134 every nonblack mask preempts every available opener on its first observation") {
    for (unsigned id = 1U; id <= 6U; ++id) {
        if (!expected(id)) continue;
        for (unsigned mask = 1U; mask < 16U; ++mask) for (bool at_go : {false, true}) {
            CAPTURE(id); CAPTURE(mask); CAPTURE(at_go); Rig rig;
            rig.prime(); rig.select(static_cast<Mode>(id)); const auto release = rig.release();
            rig.at(release + 1500000U); rig.next(); rig.at(release + 4500000U);
            auto previous = rig.last.outputs; auto previous_us = rig.now;
            if (at_go) rig.white(mask);
            rig.at(release + 5100000U);
            if (!at_go) {
                previous = rig.last.outputs; previous_us = rig.now;
                rig.white(mask); rig.next();
            }
            CHECK(rig.last.outputs.ui_state == State::EDGE_ESCAPE);
            CHECK(rig.last.line_mask == mask); CHECK_FALSE(rig.last.contact);
            edgeRow(rig, mask, previous, static_cast<std::uint32_t>(rig.now - previous_us));
        }
    }
}

TEST_CASE("B13 R1 R5 D134 STOP wins GO white and target ties and BOTH retains its full hold") {
    for (bool explicit_source : {false, true}) for (unsigned id = 1U; id <= 6U; ++id) {
        if (!expected(id)) continue;
        Rig rig(explicit_source); rig.prime(); rig.select(static_cast<Mode>(id));
        const auto release = rig.release();
        rig.at(release + 1500000U); rig.next();
        rig.at(release + 4500000U); rig.at(release + 5099999U); zero(rig);
        rig.white(1U); rig.opponent(2U);
        rig.input.stop_requested = true; rig.at(release + 5100000U);
        CHECK(rig.last.outputs.ui_state == State::STOPPED);
        CHECK_FALSE(rig.last.lifecycle.gate.go); zero(rig);
        rig.next(); rig.shortMode();
        CHECK(rig.last.outputs.ui_state == State::STOPPED); zero(rig);
        rig.reset(); rig.prime(); CHECK(rig.last.outputs.ui_state == State::IDLE); zero(rig);
        CHECK(rig.last.menu.selection.mode == static_cast<Mode>(config::MODE_DEFAULT));
        rig.select(static_cast<Mode>(id)); rig.finishHold(rig.release());
        const auto go = rig.now;
        rig.at(go + 1000U, Button::BOTH); rig.at(go + 21000U, Button::BOTH);
        rig.at(go + 1020999U, Button::BOTH);
        CHECK(rig.last.outputs.ui_state != State::STOPPED);
        rig.white(1U); rig.at(go + 1021000U, Button::BOTH);
        CHECK(rig.last.outputs.ui_state == State::STOPPED); zero(rig);
        rig.next(); CHECK(rig.last.outputs.ui_state == State::STOPPED); zero(rig);
    }
}

TEST_CASE("B3 R1 D134 10000 fixed seed bounded button streams never energize before full hold") {
    std::uint32_t seed = 0xd1345afeU;
    for (unsigned stream = 0U; stream < 10000U; ++stream) {
        CAPTURE(stream); Rig rig;
        const auto base = random(seed); rig.prime(base);
        const unsigned presses = random(seed) % (size() + 1U);
        for (unsigned press = 0U; press < presses; ++press) rig.shortMode();
        CHECK(expected(static_cast<unsigned>(rig.last.menu.selection.mode)));
        // Each deliberately sub-debounce START pulse must be discarded.
        rig.next(1000U, Button::START); rig.next(1U + random(seed) % 19000U);
        rig.next(20000U); CHECK_FALSE(rig.last.lifecycle.gate.start_release); zero(rig);
        const auto release = rig.release(); std::uint32_t elapsed = 0U;
        for (unsigned tick = 0U; tick < 12U; ++tick) {
            elapsed += 1U + random(seed) % 300000U;
            rig.opponent(random(seed) & 127U); rig.white(random(seed) & 15U);
            rig.at(release + elapsed); CHECK_FALSE(rig.last.lifecycle.gate.go); zero(rig);
        }
        rig.at(release + 5099999U); zero(rig);
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
    }
}
