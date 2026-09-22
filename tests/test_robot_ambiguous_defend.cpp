// Exercises D-061 ambiguous DEFEND entry through the actual production Robot.
// Keeps legitimate unknown bearing separate from malformed input and motion permission.
// Spec-derived cases check confirmed-mask timing, bounded waits, preemption and wrap.
#include "robot_scenario.h"
#include <array>
#include <initializer_list>
#include <limits>

using namespace robot_test;

namespace {
void waiting(const fsm::RobotResult& result) {
    CHECK(result.outputs.ui_state == State::DEFEND_TURN);
    CHECK(result.outputs.motors_enabled);
    CHECK(result.lifecycle.gate.motion_permitted);
    CHECK(result.contract_faults == 0U);
    CHECK(result.escape_fault == edge::EscapeFault::NONE);
    CHECK_FALSE(result.contact);
    zero(result, false);
    bounded(result);
}

std::uint32_t startAmbiguous(Rig& rig, std::uint8_t mask = 24U,
                             std::uint32_t base = 0U) {
    rig.opponent(mask);
    const auto time = go(rig, Mode::DIRECT, base);
    CHECK(rig.last.opponent_mask == (mask & 127U));
    waiting(rig.last);
    return time;
}
} // namespace

TEST_CASE("B5 B10 D061 initial side rear ambiguity waits at zero without inventing a bearing") {
    const std::array<std::uint8_t, 6U> masks{{24U, 56U, 88U, 120U, 96U, 224U}};
    for (const auto mask : masks) {
        CAPTURE(mask);
        Rig rig;
        const auto time = startAmbiguous(rig, mask);
        waiting(rig.step(time + 1000U));
        waiting(rig.step(time + 799999U));
        CHECK(count(rig.last, core::Event::FAULT, 7) == 0U);
        CHECK(count(rig.last, core::Event::FIRST_NONZERO_DUTY) == 0U);
    }
}

TEST_CASE("B5 D061 one valid side outranks both rear bits and starts the original defend turn") {
    for (const std::uint8_t side : {std::uint8_t{8U}, std::uint8_t{16U}}) {
        Rig rig;
        rig.opponent(static_cast<std::uint8_t>(96U | side));
        const auto time = go(rig, Mode::DIRECT);
        CHECK(rig.last.outputs.ui_state == State::DEFEND_TURN);
        const auto result = rig.step(time + 50000U);
        CHECK(result.contract_faults == 0U);
        CHECK(result.outputs.ui_state == State::DEFEND_TURN);
        CHECK((result.outputs.duty_l < 0.0F) == (side == 8U));
        CHECK((result.outputs.duty_r > 0.0F) == (side == 8U));
        CHECK(std::fabs(result.outputs.duty_l) > 0.0F);
        CHECK(std::fabs(result.outputs.duty_r) > 0.0F);
    }
}

TEST_CASE("D061 ambiguous entry immediately brakes a moving DIRECT request") {
    Rig rig;
    const auto time = go(rig, Mode::DIRECT);
    const auto moving = rig.step(time + 50000U);
    CHECK(moving.outputs.duty_l == doctest::Approx(0.85F));
    CHECK(moving.outputs.duty_r == doctest::Approx(0.85F));
    rig.opponent(24U);
    CHECK(rig.step(time + 51000U).outputs.ui_state == State::OPENER);
    const auto entered = rig.step(time + 52000U);
    waiting(entered);
    CHECK(entered.opponent_mask == 24U);
    CHECK(event(entered, core::Event::STATE_CHANGE).value == static_cast<unsigned>(State::DEFEND_TURN));
    waiting(rig.step(time + 851999U));
    CHECK(rig.step(time + 852000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("D061 first confirmed valid side captures current heading once and retains original deadline") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.opponent(8U);
    waiting(rig.step(time + 100000U)); // SR clear interval begins here.
    rig.input.raw_heading_deg = 40.0F;
    waiting(rig.step(time + 129999U));
    const auto captured = rig.step(time + 130000U);
    CHECK(captured.opponent_mask == 8U);
    CHECK(captured.outputs.ui_state == State::DEFEND_TURN);
    CHECK(captured.outputs.duty_l < 0.0F);
    CHECK(captured.outputs.duty_r > 0.0F);
    CHECK(captured.contract_faults == 0U);
    rig.input.raw_heading_deg = -50.0F; //40 + selected SL bearing(-90).
    waiting(rig.step(time + 180000U));
    waiting(rig.step(time + 799999U));
    CHECK(rig.step(time + 800000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("D061 late valid capture cannot add another800ms to an unresolved entry") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.opponent(16U);
    waiting(rig.step(time + 740000U));
    const auto captured = rig.step(time + 770000U);
    CHECK(captured.opponent_mask == 16U);
    CHECK(captured.outputs.duty_l > 0.0F);
    CHECK(captured.outputs.duty_r < 0.0F);
    CHECK(rig.step(time + 799999U).outputs.ui_state == State::DEFEND_TURN);
    const auto expired = rig.step(time + 800000U);
    CHECK(expired.outputs.ui_state == State::SEARCH);
    CHECK(expired.contract_faults == 0U);
    CHECK(count(expired, core::Event::FAULT, 8) == 0U); // Its B7 turn has not reached700ms.
}

TEST_CASE("D061 exact original expiry wins a newly confirmed usable side bearing") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.opponent(8U);
    waiting(rig.step(time + 770000U));
    waiting(rig.step(time + 799999U));
    const auto expired = rig.step(time + 800000U);
    CHECK(expired.opponent_mask == 8U);
    CHECK(expired.outputs.ui_state == State::SEARCH);
    CHECK(expired.contract_faults == 0U);
    const auto new_entry = rig.step(time + 801000U);
    CHECK(new_entry.outputs.ui_state == State::DEFEND_TURN);
    CHECK(new_entry.outputs.duty_l < 0.0F);
    CHECK(new_entry.outputs.duty_r > 0.0F);
}

TEST_CASE("D061 repeated ambiguity starts a new bounded wait only after the SEARCH exit tick") {
    for (const std::uint32_t base : {0U, 0U - 5643004U}) {
        Rig rig;
        const auto time = startAmbiguous(rig, 96U, base);
        waiting(rig.step(time + 799999U));
        CHECK(rig.step(time + 800000U).outputs.ui_state == State::SEARCH);
        const auto retry = time + 800001U;
        waiting(rig.step(retry));
        waiting(rig.step(retry + 799999U));
        CHECK(rig.step(retry + 800000U).outputs.ui_state == State::SEARCH);
        CHECK(rig.last.contract_faults == 0U);
        if (base != 0U) CHECK(time + 800000U < time);
    }
}

TEST_CASE("B2 D061 current confirmed front wins expiry with fresh three-observation qualification") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.opponent(26U); // FC plus the same ambiguous sides.
    waiting(rig.step(time + 799000U)); // Raw rise alone is not confirmed.
    const auto front = rig.step(time + 800000U);
    CHECK(front.opponent_mask == 26U);
    CHECK(front.outputs.ui_state == State::TRACK);
    CHECK_FALSE(front.contact);
    CHECK(front.contract_faults == 0U);
    CHECK(rig.step(time + 801000U).outputs.ui_state == State::TRACK);
    CHECK(rig.step(time + 802000U).outputs.ui_state == State::ATTACK);
    CHECK_FALSE(rig.last.contact);
}

TEST_CASE("B2 D061 a confirmed clear at expiry leaves SEARCH instead of retrying ambiguity") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.opponent(0U);
    waiting(rig.step(time + 770000U));
    waiting(rig.step(time + 799999U));
    const auto clear = rig.step(time + 800000U);
    CHECK(clear.opponent_mask == 0U);
    CHECK(clear.outputs.ui_state == State::SEARCH);
    CHECK(clear.contract_faults == 0U);
    CHECK(rig.step(time + 801000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("R5 D061 escape preempts unresolved wait and discards its old deadline") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.lines(8U);
    const auto edge = rig.step(time + 700000U);
    CHECK(edge.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(edge.escape_fault == edge::EscapeFault::NONE);
    CHECK(edge.contract_faults == 0U);
    rig.lines(0U);
    CHECK(rig.step(time + 701000U).outputs.ui_state == State::EDGE_ESCAPE);
    const auto exited = rig.step(time + 900000U);
    CHECK(exited.outputs.ui_state == State::DEFEND_TURN);
    zero(exited, false);
    waiting(rig.step(time + 901000U));
    waiting(rig.step(time + 1000000U)); // The old800ms deadline cannot survive preemption.
}

TEST_CASE("B13 D061 STOP preempts ambiguity and reset creates a fresh full wait") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    rig.input.stop_requested = true;
    const auto stopped = rig.step(time + 800000U);
    CHECK(stopped.outputs.ui_state == State::STOPPED);
    zero(stopped);
    rig.input.stop_requested = false;
    CHECK(rig.step(time + 801000U).outputs.ui_state == State::STOPPED);
    rig.reset();
    const auto restarted = startAmbiguous(rig);
    waiting(rig.step(restarted + 799999U));
    CHECK(rig.step(restarted + 800000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("D061 duplicate observations neither grant a bearing nor extend the pending deadline") {
    Rig rig;
    const auto time = startAmbiguous(rig);
    waiting(rig.step(time + 700000U));
    const auto token = rig.last.token;
    for (unsigned duplicate = 0U; duplicate < 40U; ++duplicate) {
        auto sample = rig.at(time + 700000U);
        sample.opp_raw_mask = static_cast<std::uint8_t>(2U ^ 0x78U);
        sample.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        sample.stop_requested = true;
        sample.previous.applied_valid = false;
        const auto result = rig.submit(sample);
        waiting(result);
        CHECK_FALSE(result.fresh);
        CHECK(result.token == token);
        CHECK(result.opponent_mask == 24U);
        CHECK(result.events.count == 0U);
    }
    waiting(rig.step(time + 799999U));
    CHECK(rig.step(time + 800000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("D026 D061 an existing valid side history still supports a conflicted defend turn") {
    Rig rig;
    rig.opponent(8U);
    const auto time = go(rig, Mode::DIRECT);
    rig.opponent(24U);
    rig.step(time + 1000U);
    const auto conflict = rig.step(time + 50000U);
    CHECK(conflict.opponent_mask == 24U);
    CHECK(conflict.outputs.ui_state == State::DEFEND_TURN);
    CHECK(conflict.outputs.duty_l < 0.0F);
    CHECK(conflict.outputs.duty_r > 0.0F);
    CHECK(conflict.contract_faults == 0U);
    waiting(rig.step(time + 700000U)); // Original B7 timeout, not a new ambiguity wait.
    CHECK(rig.step(time + 800000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("B7 D061 delayed real relative bearing uses missing-IMU fallback without extending wait") {
    Rig rig;
    rig.input.imu_ok = false;
    rig.input.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
    const auto time = startAmbiguous(rig);
    rig.opponent(8U);
    waiting(rig.step(time + 100000U));
    const auto captured = rig.step(time + 130000U);
    CHECK(captured.outputs.duty_l < 0.0F);
    CHECK(captured.outputs.duty_r > 0.0F);
    CHECK(captured.contract_faults == 0U);
    const auto before = rig.step(time + 309999U);
    CHECK(before.outputs.duty_l < 0.0F);
    CHECK(before.outputs.duty_r > 0.0F);
    waiting(rig.step(time + 310000U)); //90 degrees *2ms, measured from real capture.
    waiting(rig.step(time + 799999U));
    CHECK(rig.step(time + 800000U).outputs.ui_state == State::SEARCH);
}

TEST_CASE("D061 ambiguous wait starts on forced-brake escape exit before deferred executor tick") {
    for (const std::uint32_t base : {0U, 0U - 6543004U}) {
        Rig rig;
        const auto time = startAmbiguous(rig, 24U, base);
        rig.lines(8U);
        CHECK(rig.step(time + 700000U).outputs.ui_state == State::EDGE_ESCAPE);
        rig.lines(0U);
        CHECK(rig.step(time + 701000U).outputs.ui_state == State::EDGE_ESCAPE);
        const auto exit_time = time + 900000U;
        const auto exited = rig.step(exit_time);
        waiting(exited);
        CHECK(event(exited, core::Event::EDGE).detail == 8U);
        CHECK(event(exited, core::Event::EDGE).value == 0U);
        waiting(rig.step(exit_time + 799999U));
        const auto expired = rig.step(exit_time + 800000U);
        CHECK(expired.outputs.ui_state == State::SEARCH);
        CHECK(expired.opponent_mask == 24U);
        CHECK(expired.contract_faults == 0U);
        if (base != 0U) CHECK(exit_time + 800000U < exit_time);
    }
}

TEST_CASE("D061 sparse first call after escape-exit deadline expires without starting a late wait") {
    for (const std::uint32_t age : {800000U, 800001U, 1500000U}) {
        Rig rig;
        const auto time = startAmbiguous(rig);
        rig.lines(8U);
        CHECK(rig.step(time + 700000U).outputs.ui_state == State::EDGE_ESCAPE);
        rig.lines(0U);
        CHECK(rig.step(time + 701000U).outputs.ui_state == State::EDGE_ESCAPE);
        const auto exit_time = time + 900000U;
        waiting(rig.step(exit_time));
        const auto expired = rig.step(exit_time + age);
        CHECK(expired.outputs.ui_state == State::SEARCH);
        CHECK(expired.opponent_mask == 24U);
        CHECK(expired.contract_faults == 0U);
        CHECK(expired.escape_fault == edge::EscapeFault::NONE);
        waiting(rig.step(exit_time + age + 1000U)); // Only this new entry may retry.
    }
}
