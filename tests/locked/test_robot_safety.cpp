// Proves R1 and R5 decisions through the actual production Robot transaction.
// Explicit synthetic receipts model output settings without claiming physical MotorGate proof.
// New locked scenarios cover full holds, all line masks, reset-only faults and 10000 streams.
#include "../robot_scenario.h"
#include <array>
#include <limits>

using namespace robot_test;

TEST_CASE("R1 B3 actual Robot keeps full 5100000us hold after qualified release") {
    for (const std::uint32_t base : {0U, 0xfff00000U}) {
        Rig rig;
        const auto anchor = release(rig, idle(rig, base));
        for (const std::uint32_t age : {1U, 1000U, 1500000U, 4500000U, 4999999U, 5000000U, 5099999U}) {
            const auto result = rig.step(anchor + age);
            CHECK(result.outputs.ui_state == State::COUNTDOWN);
            CHECK_FALSE(result.lifecycle.gate.motion_permitted);
            CHECK_FALSE(result.lifecycle.gate.go);
            zero(result);
        }
        const auto result = rig.step(anchor + 5100000U);
        CHECK(result.lifecycle.gate.go);
        CHECK(result.lifecycle.gate.motion_permitted);
        CHECK(result.outputs.motors_enabled);
        CHECK(result.outputs.ui_state == State::OPENER);
        CHECK(event(result, core::Event::GO).t_us == anchor + 5100000U);
    }
}

TEST_CASE("R1 B3 Robot MODE qualification wins exact GO deadline and consumes attempt") {
    Rig rig;
    const auto anchor = release(rig, idle(rig));
    zero(rig.step(anchor + 5080000U, Button::MODE));
    const auto canceled = rig.step(anchor + 5100000U, Button::MODE);
    CHECK(canceled.outputs.ui_state == State::IDLE);
    CHECK_FALSE(canceled.lifecycle.gate.go);
    CHECK(count(canceled, core::Event::GO) == 0U);
    CHECK_FALSE(canceled.menu.selection_changed);
    zero(canceled);
    zero(rig.step(anchor + 6000000U));
    CHECK_FALSE(rig.last.lifecycle.gate.go);
}

TEST_CASE("R1 B13 Robot explicit STOP wins GO boundary and every later call") {
    for (const std::uint32_t stop_age : {5099999U, 5100000U, 6000000U}) {
        Rig rig;
        const auto anchor = release(rig, idle(rig));
        rig.input.stop_requested = true;
        const auto stopped = rig.step(anchor + stop_age);
        CHECK(stopped.outputs.ui_state == State::STOPPED);
        CHECK_FALSE(stopped.lifecycle.gate.go);
        zero(stopped);
        rig.input.stop_requested = false;
        zero(rig.step(anchor + stop_age + 1000U));
        CHECK(rig.last.outputs.ui_state == State::STOPPED);
    }
}

TEST_CASE("R1 B13 Robot BOTH requires full qualification plus hold then latches STOP") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT);
    rig.step(time + 1000U, Button::BOTH);
    rig.step(time + 21000U, Button::BOTH);
    CHECK(rig.step(time + 1020999U, Button::BOTH).outputs.ui_state != State::STOPPED);
    const auto stopped = rig.step(time + 1021000U, Button::BOTH);
    CHECK(stopped.outputs.ui_state == State::STOPPED);
    zero(stopped);
    CHECK(rig.step(time + 1022000U).outputs.ui_state == State::STOPPED);
}

TEST_CASE("R5 B4 actual Robot handles every line mask after GO and while persistent before GO") {
    for (unsigned mask = 0U; mask < 16U; ++mask) {
        for (const bool persistent : {false, true}) {
            CAPTURE(mask);
            CAPTURE(persistent);
            Rig rig;
            if (persistent) rig.lines(static_cast<std::uint8_t>(mask));
            const auto time = go(rig);
            if (!persistent) rig.lines(static_cast<std::uint8_t>(mask));
            const auto result = persistent ? rig.last : rig.step(time + 1000U);
            CHECK(result.line_mask == mask);
            CHECK(result.outputs.ui_state == (mask == 0U ? State::OPENER : State::EDGE_ESCAPE));
            CHECK(result.contract_faults == 0U);
            const bool invalid_pattern = mask == 7U || mask == 11U || mask == 13U || mask == 14U || mask == 15U;
            CHECK(result.escape_fault == (invalid_pattern ? edge::EscapeFault::WHITE_PATTERN : edge::EscapeFault::NONE));
            if (invalid_pattern) zero(result);
            if (mask != 0U) {
                const auto edge = event(result, core::Event::EDGE);
                CHECK((edge.detail & 2U) != 0U);
                CHECK((edge.value & 15U) == mask);
                CHECK(((edge.value >> 4U) & 15U) == (persistent ? 0U : mask));
            }
            bounded(result);
        }
    }
}

TEST_CASE("R5 B4 Robot raw QTR strict threshold is authoritative") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT);
    for (unsigned index = 0U; index < 4U; ++index) rig.input.line_raw_us[index] = 300U;
    CHECK(rig.step(time + 1000U).line_mask == 0U);
    rig.input.line_raw_us[0] = 299U;
    const auto result = rig.step(time + 2000U);
    CHECK(result.line_mask == 1U);
    CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
    zero(result, false);
}

TEST_CASE("R5 B4 D050 Robot allows three persistent replacements and faults fourth") {
    for (const std::uint32_t base : {0U, 0xfff00000U}) {
        Rig rig;
        const auto time = go(rig, Mode::WAIT, base) + 1000U;
        rig.lines(8U);
        CHECK(rig.step(time).outputs.ui_state == State::EDGE_ESCAPE);
        CHECK(count(rig.step(time + 199999U), core::Event::EDGE) == 0U);
        for (unsigned replacement = 1U; replacement <= 3U; ++replacement) {
            const auto result = rig.step(time + replacement * 200000U);
            CHECK(result.escape_fault == edge::EscapeFault::NONE);
            CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
            const auto edge = event(result, core::Event::EDGE);
            CHECK(edge.detail == 4U);
            CHECK(edge.value == static_cast<std::uint16_t>(8U | replacement << 8U));
        }
        const auto exhausted = rig.step(time + 800000U);
        CHECK(exhausted.escape_fault == edge::EscapeFault::REPLAN_LIMIT);
        CHECK(exhausted.outputs.ui_state == State::EDGE_ESCAPE);
        CHECK(count(exhausted, core::Event::EDGE) == 0U);
        CHECK(event(exhausted, core::Event::FAULT, 6).value == 2U);
        zero(exhausted);
        rig.lines(0U);
        const auto black = rig.step(time + 801000U);
        CHECK(black.escape_fault == edge::EscapeFault::REPLAN_LIMIT);
        CHECK(black.outputs.ui_state == State::EDGE_ESCAPE);
        zero(black);
    }
}

TEST_CASE("R5 D050 Robot black alone cannot exit before row completion and exit brakes once") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT) + 1000U;
    rig.lines(8U);
    rig.step(time);
    rig.lines(0U);
    CHECK(rig.step(time + 1000U).outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(rig.step(time + 199999U).outputs.ui_state == State::EDGE_ESCAPE);
    const auto exit = rig.step(time + 200000U);
    CHECK(exit.outputs.ui_state == State::SEARCH);
    CHECK(event(exit, core::Event::EDGE).detail == 8U);
    CHECK(event(exit, core::Event::EDGE).value == 0U);
    zero(exit, false);
    const auto next = rig.step(time + 250000U);
    CHECK(next.outputs.ui_state == State::SEARCH);
    CHECK(std::fabs(next.outputs.duty_l) + std::fabs(next.outputs.duty_r) > 0.0F);
    CHECK(count(next, core::Event::EDGE) == 0U);
}

TEST_CASE("R5 B4 Robot new white during reverse replans on observed call") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT) + 1000U;
    rig.lines(1U);
    rig.step(time);
    CHECK(rig.step(time + 1000U).outputs.ui_state == State::EDGE_ESCAPE);
    rig.lines(9U);
    const auto replacement = rig.step(time + 2000U);
    CHECK(event(replacement, core::Event::EDGE).detail == 5U);
    CHECK(event(replacement, core::Event::EDGE).value == 0x0189U);
    zero(replacement, false);
    zero(rig.step(time + 2999U), false);
    const auto back = rig.step(time + 3000U);
    CHECK(back.outputs.duty_l < 0.0F);
    CHECK(back.outputs.duty_r < 0.0F);
}

TEST_CASE("R5 B9 Robot all-white preempts previously full contact ATTACK immediately") {
    Rig rig;
    const auto time = attack(rig);
    rig.lines(15U);
    rig.input.ax_g = 2.0F;
    const auto edge = rig.step(time + 1000U);
    CHECK(edge.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(edge.escape_fault == edge::EscapeFault::WHITE_PATTERN);
    CHECK_FALSE(edge.contact);
    CHECK(count(edge, core::Event::CONTACT) == 0U);
    zero(edge);
    rig.input.stop_requested = true;
    const auto stopped = rig.step(time + 2000U);
    CHECK(stopped.outputs.ui_state == State::STOPPED);
    CHECK(stopped.escape_fault == edge::EscapeFault::WHITE_PATTERN);
    zero(stopped);
}

TEST_CASE("R5 D047 Robot head-on default pivots right after complete180ms reverse") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT) + 1000U;
    rig.lines(3U);
    zero(rig.step(time), false);
    rig.step(time + 1000U);
    const auto reverse = rig.step(time + 180999U);
    CHECK(reverse.outputs.duty_l < 0.0F);
    CHECK(reverse.outputs.duty_r < 0.0F);
    rig.step(time + 181000U);
    const auto pivot = rig.step(time + 231000U);
    CHECK(pivot.outputs.duty_l > 0.0F);
    CHECK(pivot.outputs.duty_r < 0.0F);
    CHECK(pivot.outputs.ui_state == State::EDGE_ESCAPE);
}

TEST_CASE("R5 B4 Robot front escape rows mirror governed motion") {
    Rig left;
    Rig right;
    const auto tl = go(left, Mode::WAIT) + 1000U;
    const auto tr = go(right, Mode::WAIT) + 1000U;
    left.lines(1U);
    right.lines(2U);
    left.step(tl);
    right.step(tr);
    for (const std::uint32_t age : {1000U, 51000U, 121000U, 171000U}) {
        const auto l = left.step(tl + age);
        const auto r = right.step(tr + age);
        CHECK(l.outputs.duty_l == doctest::Approx(r.outputs.duty_r));
        CHECK(l.outputs.duty_r == doctest::Approx(r.outputs.duty_l));
        CHECK(l.outputs.ui_state == State::EDGE_ESCAPE);
        CHECK(r.outputs.ui_state == State::EDGE_ESCAPE);
    }
}

TEST_CASE("R1 R5 10000 fixed-seed actual Robot streams remain inhibited or bounded") {
    std::uint32_t random = 0x36a891d5U;
    std::array<unsigned, 16U> masks{};
    unsigned go_count = 0U, cancel_count = 0U, stop_count = 0U, wrap_count = 0U;
    for (unsigned stream = 0U; stream < 10000U; ++stream) {
        Rig rig;
        const std::uint32_t base = stream % 2U == 0U ? 0U : 0xfff00000U;
        const auto anchor = release(rig, idle(rig, base));
        zero(rig.step(anchor + 5099999U));
        const bool cancel = stream % 5U == 0U;
        rig.input.stop_requested = cancel;
        auto time = anchor + 5100000U;
        auto result = rig.step(time);
        if (time < anchor) ++wrap_count;
        if (cancel) { ++cancel_count; zero(result); CHECK_FALSE(result.lifecycle.gate.go); }
        else { ++go_count; CHECK(result.lifecycle.gate.go); }
        for (unsigned sample = 0U; sample < 8U; ++sample) {
            const auto word = randomWord(random);
            const auto mask = static_cast<std::uint8_t>(word & 15U);
            ++masks[mask];
            rig.lines(mask);
            rig.opponent(static_cast<std::uint8_t>((word >> 4U) & 127U));
            rig.input.raw_heading_deg += static_cast<float>(static_cast<int>((word >> 12U) % 721U) - 360);
            rig.input.vbat_v = 9.0F + static_cast<float>((word >> 22U) % 40U) / 10.0F;
            rig.input.stop_requested = cancel || (sample == 7U && stream % 3U == 0U);
            time += sample % 2U == 0U ? 1000U : 200000U;
            result = rig.step(time);
            bounded(result);
            CHECK(result.contract_faults == 0U);
            CHECK(result.line_mask == mask);
            if (result.outputs.ui_state == State::STOPPED) { ++stop_count; zero(result); }
            else if (!cancel && mask != 0U) CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
            if (cancel) CHECK(result.outputs.ui_state == State::STOPPED);
        }
    }
    CHECK(go_count == 8000U);
    CHECK(cancel_count == 2000U);
    CHECK(wrap_count == 5000U);
    CHECK(stop_count > 16000U);
    for (const auto coverage : masks) CHECK(coverage > 4000U);
}
