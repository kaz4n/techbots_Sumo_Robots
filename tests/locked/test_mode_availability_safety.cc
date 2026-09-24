// Locks B3/B4/B13 safety while D134 removes optional choices from the menu.
// Exercises actual Robot and MotorGate callbacks with independently timed stimuli.
// New frozen M0/M1 configured tests retain hold, edge and STOP priority for every choice.
#include "doctest.h"
#include "../fixtures/mode_availability_fixture.h"

using namespace mode_test;

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
            if (at_go) rig.white(mask);
            rig.at(release + 5100000U);
            if (!at_go) { rig.white(mask); rig.next(); }
            CHECK(rig.last.outputs.ui_state == State::EDGE_ESCAPE);
            CHECK(rig.last.line_mask == mask); CHECK_FALSE(rig.last.contact);
            CHECK(rig.last.outputs.duty_l == 0.0F); CHECK(rig.last.outputs.duty_r == 0.0F);
            for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
            CHECK(rig.applied.feedback.duty_l == 0.0F);
            CHECK(rig.applied.feedback.duty_r == 0.0F);
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
