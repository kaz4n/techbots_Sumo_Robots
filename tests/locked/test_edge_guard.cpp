// Checks B2/B4 persistent edge arbitration and D-020 all-white inhibition.
// Exercises pure countdown/guard/governor composition without simulating HAL writes.
// Run with tools/test_host.sh; all masks, fault retention and 1 kHz GO are covered.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include "core/edge.h"
#include "core/governor.h"
#include <cstdint>
#include <initializer_list>

namespace {
constexpr std::uint32_t HOLD_US =
    (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
constexpr std::uint32_t DEBOUNCE_US = config::BTN_DEBOUNCE_MS * 1000U;

void checkGuard(const edge::GuardResult& result, bool escaping, bool fault,
                bool inhibited) {
    CHECK(result.escape_required == escaping);
    CHECK(result.fault_latched == fault);
    CHECK(result.inhibit_motion == inhibited);
}

struct LogicalTick {
    countdown::Result countdown;
    edge::GuardResult edge;
    governor::Request request;
    governor::Result duty;
};

// This is a test-owned logical composition, not Robot::step or MotorGate.
class ScenarioRunner {
public:
    LogicalTick sample(std::uint32_t t_us, core::ButtonLevel level,
                       std::uint8_t mask, bool finished = false,
                       bool stop = false) {
        core::Inputs input;
        input.t_us = t_us;
        input.button_level = level;
        input.line_mask = mask;
        last.countdown = countdown.step(input, stop);
        last.edge = guard.step(input.line_mask,
                               last.countdown.motion_permitted, finished);
        last.request.duty_l = 1.0F;
        last.request.duty_r = 1.0F;
        last.request.vbat_v = config::V_NOM_V;
        last.request.profile = governor::Profile::ATTACK;
        last.request.centered = true;
        last.request.contact = true;
        last.request.inhibited = !last.countdown.motion_permitted ||
                                  last.edge.inhibit_motion;
        last.duty = governor.step(t_us, last.request);
        release_pulses += last.countdown.start_release ? 1U : 0U;
        go_pulses += last.countdown.go ? 1U : 0U;
        return last;
    }
    countdown::Controller countdown;
    edge::Guard guard;
    governor::Governor governor;
    LogicalTick last;
    unsigned release_pulses = 0U;
    unsigned go_pulses = 0U;
};

void checkZero(const LogicalTick& tick) {
    CHECK(tick.request.inhibited);
    CHECK(tick.duty.valid);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
}

std::uint32_t runToGo(ScenarioRunner& runner, std::uint8_t mask) {
    const std::uint32_t raw_release = DEBOUNCE_US + 2U * config::TICK_US;
    const std::uint32_t qualified = raw_release + DEBOUNCE_US;
    const std::uint32_t deadline = qualified + HOLD_US;
    for (std::uint32_t t = 0U; t <= deadline; t += config::TICK_US) {
        const auto level = t >= config::TICK_US && t < raw_release
            ? core::ButtonLevel::START : core::ButtonLevel::NONE;
        const auto tick = runner.sample(t, level, mask);
        if (t < deadline) {
            CHECK_FALSE(tick.countdown.motion_permitted);
            checkGuard(tick.edge, false, false, true);
            checkZero(tick);
        }
    }
    CHECK(runner.release_pulses == 1U);
    CHECK(runner.go_pulses == 1U);
    CHECK(runner.last.countdown.go);
    CHECK(runner.last.countdown.motion_permitted);
    CHECK(runner.last.countdown.release_us == qualified);
    return deadline;
}
} // namespace

TEST_CASE("B2/B4 Guard handles every line mask immediately after motion permission") {
    for (std::uint8_t mask = 0U; mask < 16U; ++mask) {
        CAPTURE(mask);
        edge::Guard guard;
        checkGuard(guard.step(mask, true, false), mask != 0U,
                   mask == 15U, mask == 15U);
    }
}

TEST_CASE("B2/B4 Guard cannot enter escape or latch new line faults before GO") {
    for (std::uint8_t mask = 0U; mask < 16U; ++mask) {
        edge::Guard guard;
        checkGuard(guard.step(mask, false, false), false, false, true);
        checkGuard(guard.step(mask, false, true), false, false, true);
        checkGuard(guard.step(0U, true, true), false, false, false);
    }
}

TEST_CASE("B4.2 Guard all-white fault retains a motion veto until explicit reset") {
    edge::Guard guard;
    checkGuard(guard.step(15U, true, true), true, true, true);
    for (auto permission : {true, false, true}) {
        for (std::uint8_t mask = 0U; mask < 16U; ++mask) {
            for (auto finished : {false, true}) {
                const auto result = guard.step(mask, permission, finished);
                CHECK(result.fault_latched);
                CHECK(result.inhibit_motion);
                if (!permission) CHECK_FALSE(result.escape_required);
            }
        }
    }
    guard.reset();
    checkGuard(guard.step(0U, true, true), false, false, false);
    checkGuard(guard.step(1U, true, false), true, false, false);
}

TEST_CASE("B4.4 Guard needs black and script finished together to leave escape") {
    for (auto black_first : {false, true}) {
        edge::Guard guard;
        checkGuard(guard.step(2U, true, false), true, false, false);
        if (black_first) {
            checkGuard(guard.step(0U, true, false), true, false, false);
            checkGuard(guard.step(0U, true, false), true, false, false);
        } else {
            checkGuard(guard.step(2U, true, true), true, false, false);
            checkGuard(guard.step(0U, true, false), true, false, false);
        }
        checkGuard(guard.step(0U, true, true), false, false, false);
        checkGuard(guard.step(0U, true, false), false, false, false);
    }
}

TEST_CASE("B2/B4.4 Guard persistent white cannot exit when escape script finishes") {
    for (std::uint8_t mask = 1U; mask < 15U; ++mask) {
        edge::Guard guard;
        checkGuard(guard.step(mask, true, false), true, false, false);
        for (unsigned tick = 0U; tick < 100U; ++tick)
            checkGuard(guard.step(mask, true, true), true, false, false);
        checkGuard(guard.step(0U, true, true), false, false, false);
    }
}

TEST_CASE("B2/B4 Guard re-enters on new white after a completed clear escape") {
    edge::Guard guard;
    for (std::uint8_t mask = 1U; mask < 15U; ++mask) {
        checkGuard(guard.step(mask, true, true), true, false, false);
        checkGuard(guard.step(0U, true, false), true, false, false);
        checkGuard(guard.step(0U, true, true), false, false, false);
    }
    checkGuard(guard.step(15U, true, false), true, true, true);
}

TEST_CASE("B0/B4 Guard uses only four line bits with the default zero push-through") {
    CHECK(config::EDGE_PUSH_THROUGH_MS == 0U);
    for (std::uint8_t mask = 0U; mask < 16U; ++mask) {
        edge::Guard guard;
        const auto decorated = static_cast<std::uint8_t>(0xF0U | mask);
        checkGuard(guard.step(decorated, true, false), mask != 0U,
                   mask == 15U, mask == 15U);
    }
}

TEST_CASE("B2/B3/B4/B6 logical pipeline sees persistent white on the exact GO tick") {
    for (std::uint8_t mask = 0U; mask < 16U; ++mask) {
        CAPTURE(mask);
        ScenarioRunner runner;
        runToGo(runner, mask);
        checkGuard(runner.last.edge, mask != 0U, mask == 15U, mask == 15U);
        if (mask == 15U) {
            checkZero(runner.last);
        } else {
            CHECK_FALSE(runner.last.request.inhibited);
        }
    }
}

TEST_CASE("B2/B4.2/B6 logical pipeline all-white brakes existing duty and stays zero") {
    ScenarioRunner runner;
    const auto go_at = runToGo(runner, 0U);
    const auto moving = runner.sample(go_at + 100000U, core::ButtonLevel::NONE, 0U);
    CHECK(moving.duty.duty_l > 0.0F);
    CHECK(moving.duty.duty_r > 0.0F);
    const auto fault = runner.sample(go_at + 101000U, core::ButtonLevel::NONE, 15U);
    checkGuard(fault.edge, true, true, true);
    checkZero(fault);
    for (unsigned tick = 102U; tick < 202U; ++tick) {
        const auto clear = runner.sample(go_at + tick * 1000U,
                                         core::ButtonLevel::NONE, 0U, true);
        CHECK(clear.countdown.motion_permitted);
        CHECK(clear.edge.fault_latched);
        checkZero(clear);
    }
    runner.countdown.reset();
    checkZero(runner.sample(go_at + 203000U, core::ButtonLevel::NONE, 0U, true));
    CHECK(runner.last.edge.fault_latched);
    runner.guard.reset();
    checkZero(runner.sample(go_at + 204000U, core::ButtonLevel::NONE, 0U, true));
    CHECK_FALSE(runner.last.edge.fault_latched);
}

TEST_CASE("B2/B3/B4/B6 logical pipeline STOP closes permission ahead of an edge") {
    ScenarioRunner runner;
    const auto go_at = runToGo(runner, 0U);
    const auto moving = runner.sample(go_at + 100000U, core::ButtonLevel::NONE, 0U);
    CHECK(moving.duty.duty_l > 0.0F);
    CHECK(moving.duty.duty_r > 0.0F);
    const auto stop = runner.sample(go_at + 101000U, core::ButtonLevel::NONE,
                                    15U, false, true);
    CHECK(stop.countdown.phase == countdown::Phase::STOPPED);
    checkGuard(stop.edge, false, false, true);
    checkZero(stop);
    const auto later = runner.sample(go_at + HOLD_US, core::ButtonLevel::NONE,
                                     15U, true);
    checkGuard(later.edge, false, false, true);
    checkZero(later);
}
