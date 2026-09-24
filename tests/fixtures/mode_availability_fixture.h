// Supplies B13/D134 button timelines to the actual Robot and MotorGate.
// Separates literal mode-list expectations from the production availability query.
// New configured host tests share only finite stimuli and physical callback receipts.
#pragma once
#include "app_transaction_fixture.h"
#include "hal/motors.h"
#include <cmath>
#include <initializer_list>

namespace mode_test {
using Mode = core::Mode;
using State = core::State;
using Button = core::ButtonLevel;
constexpr bool expected(unsigned id) {
    return (id >= 1U && id <= 3U) ||
        ((id == 4U || id == 5U) && config::MODE_ARC_ENABLED == 1U) ||
        (id == 6U && config::MODE_WAIT_ENABLED == 1U);
}
constexpr unsigned size() {
    return 3U + 2U * config::MODE_ARC_ENABLED + config::MODE_WAIT_ENABLED;
}
inline Mode nextMode(Mode current) {
    unsigned id = static_cast<unsigned>(current);
    for (unsigned probe = 0U; probe < 6U; ++probe) {
        id = id == 6U ? 1U : id + 1U;
        if (expected(id)) return static_cast<Mode>(id);
    }
    return static_cast<Mode>(0U);
}
struct Rig {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::RobotResult last;
    motors::Result applied;
    std::uint32_t now = 0U, sequence = 0U;
    bool explicit_buttons;
    bool sampled = false;
    explicit Rig(bool explicit_source = false) : explicit_buttons(explicit_source) {
        APP_REQUIRE(gate.begin()); port.clear();
    }
    const fsm::RobotResult& observe(std::uint32_t time, Button button) {
        now = time; input.t_us = time; input.button = button;
        sampled = true;
        if (explicit_buttons) {
            input.buttons.explicit_values = true;
            input.buttons.presence = core::ButtonPresence::VALID;
            input.buttons.level = button; input.buttons.sequence = sequence++;
            input.buttons.started_us = time; input.buttons.completed_us = time;
        }
        last = robot.step(input); port.now = time;
        applied = gate.apply(time, last); input.previous = applied.feedback;
        CHECK(applied.consumed); CHECK(applied.feedback.applied_valid);
        input.previous.duration_valid = true; input.previous.completed_us = time;
        return last;
    }
    const fsm::RobotResult& at(std::uint32_t time, Button button = Button::NONE) {
        // D087 permits sparse legacy decisions, but explicit source gaps <=5000us.
        // Fill only the prior held level; the requested new edge remains at time.
        while (explicit_buttons && sampled && static_cast<std::uint32_t>(time - now) > 5000U)
            observe(now + 5000U, input.button);
        return observe(time, button);
    }
    const fsm::RobotResult& next(std::uint32_t delta = 1000U,
                               Button button = Button::NONE) {
        return at(now + delta, button);
    }
    void prime(std::uint32_t base = 0U) {
        at(base); next(); next(20000U);
        APP_REQUIRE(last.outputs.ui_state == State::IDLE);
    }
    void shortMode() {
        next(1000U, Button::MODE); next(20000U, Button::MODE);
        next(); next(20000U);
    }
    void longMode() {
        next(1000U, Button::MODE); next(20000U, Button::MODE);
        next(1000000U, Button::MODE); next(); next(20000U);
    }
    void select(Mode mode) {
        APP_REQUIRE(expected(static_cast<unsigned>(mode)));
        for (unsigned i = 0U; i < 6U && last.menu.selection.mode != mode; ++i)
            shortMode();
        APP_REQUIRE(last.menu.selection.mode == mode);
    }
    std::uint32_t release() {
        next(1000U, Button::START); next(20000U, Button::START);
        next(); next(20000U);
        APP_REQUIRE(last.lifecycle.gate.start_release); return now;
    }
    std::uint32_t finishHold(std::uint32_t release_us) {
        at(release_us + 1500000U); next(); at(release_us + 4500000U);
        at(release_us + 5099999U); at(release_us + 5100000U);
        APP_REQUIRE(last.lifecycle.gate.go); return now;
    }
    std::uint32_t go(Mode mode, std::uint32_t base = 0U) {
        prime(base); select(mode); return finishHold(release());
    }
    void opponent(unsigned mask) {
        input.opp_raw_mask = static_cast<std::uint8_t>(mask ^ 0x78U);
    }
    void white(unsigned mask) {
        for (unsigned i = 0U; i < 4U; ++i)
            input.line_raw_us[i] = (mask & (1U << i)) ? 100U : 1000U;
    }
    void reset() {
        robot.reset(); APP_REQUIRE(gate.reset()); input = app_test::input();
        sequence = 0U; sampled = false; port.clear(); last = {}; applied = {};
    }
};
inline void zero(const Rig& rig) {
    CHECK_FALSE(rig.last.outputs.motors_enabled);
    CHECK(rig.last.outputs.duty_l == 0.0F); CHECK(rig.last.outputs.duty_r == 0.0F);
    CHECK_FALSE(rig.applied.feedback.motors_enabled);
    CHECK(rig.applied.feedback.duty_l == 0.0F);
    CHECK(rig.applied.feedback.duty_r == 0.0F); app_test::zero(rig.port);
}
inline void governed(const Rig& rig, float cap) {
    CHECK(rig.last.contract_faults == 0U); CHECK_FALSE(rig.last.contact);
    CHECK(std::fabs(rig.last.outputs.duty_l) <= cap);
    CHECK(std::fabs(rig.last.outputs.duty_r) <= cap);
    CHECK(std::fabs(rig.applied.feedback.duty_l) <= std::fabs(rig.last.outputs.duty_l));
    CHECK(std::fabs(rig.applied.feedback.duty_r) <= std::fabs(rig.last.outputs.duty_r));
    if (!MOTORS_ALLOWED) app_test::zero(rig.port);
}
inline openers::Sample sample(std::uint32_t time, float heading = 0.0F,
                              unsigned mask = 0U, bool healthy = true) {
    openers::Sample value;
    value.t_us = time; value.heading_deg = heading; value.imu_ok = healthy;
    value.confirmed_mask = static_cast<std::uint8_t>(mask); return value;
}
inline void invalid(const openers::FlankResult& result) {
    CHECK(result.phase == openers::Phase::INVALID);
    CHECK(result.exit == openers::Exit::INVALID);
    CHECK(result.motion.status == motion::Status::INVALID);
    CHECK(result.motion.duty_l == 0.0F); CHECK(result.motion.duty_r == 0.0F);
    CHECK_FALSE(result.motion_timed_out); CHECK_FALSE(result.scan_hint_valid);
}
inline std::uint32_t random(std::uint32_t& seed) {
    seed ^= seed << 13U; seed ^= seed >> 17U; seed ^= seed << 5U; return seed;
}
} // namespace mode_test
