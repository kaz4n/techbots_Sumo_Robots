// Supplies genuine ordinary-menu starts and actual Transaction/MotorGate receipts.
// Keeps D128 routing expectations separate from profile implementation details.
// Independent M0/M1 tests cover perception, physical callback traces and inhibition.
#pragma once
#include "drive_test_fixture.h"
#include "app_service_reset/fixture.h"

namespace reactive_test {
using Button = core::ButtonLevel;
using State = core::State;
using Mode = core::Mode;
struct Rig : drive_test::Rig {
    std::uint32_t releaseMatch(unsigned mode = 1U, std::uint32_t base = 0U) {
        prime(base); for (unsigned i = 1U; i < mode; ++i) shortMode();
        APP_REQUIRE(!owner.report().robot.menu.selection.service_menu);
        const auto release = releaseSelected();
        APP_REQUIRE(owner.report().robot.lifecycle.gate.start_release);
        APP_REQUIRE(owner.report().robot.running_mode == static_cast<Mode>(mode));
        return release;
    }
    std::uint32_t goMatch(unsigned mode = 1U, std::uint32_t base = 0U) {
        const auto release = releaseMatch(mode, base);
        at(release + 1500000U); next(); at(release + 4500000U);
        at(release + 5099999U); at(release + 5100000U);
        APP_REQUIRE(owner.report().robot.lifecycle.gate.go); return now;
    }
    std::uint32_t attack(bool contact = false) {
        opponent(2U); const auto go = goMatch();
        APP_REQUIRE(next().robot.outputs.ui_state == State::TRACK);
        APP_REQUIRE(next().robot.outputs.ui_state == State::TRACK);
        source.ax_g = contact ? 2.0F : 0.0F;
        APP_REQUIRE(next().robot.outputs.ui_state == State::ATTACK);
        APP_REQUIRE(owner.report().robot.contact == contact);
        source.ax_g = 0.0F; at(go + 53000U); return now;
    }
};
inline unsigned count(const fsm::RobotResult& r, core::Event type, unsigned detail = 256U) {
    unsigned n = 0U;
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == type && (detail == 256U || r.events.entries[i].detail == detail)) ++n;
    return n;
}
inline void noOpener(const fsm::RobotResult& r) {
    CHECK(r.outputs.ui_state != State::OPENER); CHECK(r.outputs.ui_state != State::DRIVE_TEST);
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == core::Event::STATE_CHANGE)
            CHECK(r.events.entries[i].value != static_cast<unsigned>(State::OPENER));
}
inline void active(const Rig& rig, const app::TransactionReport& r) {
    noOpener(r.robot); CHECK(r.robot.outputs.motors_enabled); CHECK(r.robot.contract_faults == 0U);
    CHECK(r.robot.escape_fault == edge::EscapeFault::NONE); CHECK(r.applied.consumed);
    CHECK(r.applied.feedback.applied_valid); CHECK(r.applied.fault == motors::Fault::NONE);
    CHECK(r.applied.feedback.token == r.robot.token);
    CHECK(r.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
    CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0));
    CHECK(std::isfinite(r.robot.outputs.duty_l)); CHECK(std::isfinite(r.robot.outputs.duty_r));
    CHECK(std::fabs(r.applied.feedback.duty_l) <= std::fabs(r.robot.outputs.duty_l));
    CHECK(std::fabs(r.applied.feedback.duty_r) <= std::fabs(r.robot.outputs.duty_r));
    if (!MOTORS_ALLOWED) { CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U); }
}
inline void brake(const Rig& rig, const app::TransactionReport& r) {
    active(rig, r); CHECK(r.robot.outputs.duty_l == 0.0F); CHECK(r.robot.outputs.duty_r == 0.0F);
    CHECK(r.applied.feedback.duty_l == 0.0F); CHECK(r.applied.feedback.duty_r == 0.0F);
    for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
}
inline std::uint32_t fullAfterReflank(Rig& rig, std::uint32_t start) {
    APP_REQUIRE(rig.at(start + 150000U).robot.outputs.ui_state == State::REFLANK);
    APP_REQUIRE(rig.at(start + 850000U).robot.outputs.ui_state == State::REFLANK);
    APP_REQUIRE(rig.at(start + 1250000U).robot.outputs.ui_state == State::TRACK);
    APP_REQUIRE(rig.next().robot.outputs.ui_state == State::TRACK); rig.source.ax_g = 2.0F;
    APP_REQUIRE(rig.next().robot.outputs.ui_state == State::ATTACK);
    APP_REQUIRE(rig.owner.report().robot.contact); rig.source.ax_g = 0.0F;
    rig.at(start + 1302000U); return rig.now;
}
struct ActualRobot {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    ActualRobot() { APP_REQUIRE(gate.begin()); }
    fsm::RobotResult at(std::uint32_t time, Button button = Button::NONE) {
        input.t_us = time; input.button = button; port.now = time;
        const auto r = robot.step(input);
        if (r.fresh) input.previous = gate.apply(time, r).feedback;
        return r;
    }
    std::uint32_t go() {
        at(0U); at(1000U); at(21000U); at(22000U, Button::START);
        at(42000U, Button::START); at(43000U); APP_REQUIRE(at(63000U).lifecycle.gate.start_release);
        APP_REQUIRE(at(5163000U).lifecycle.gate.go); return 5163000U;
    }
};
} // namespace reactive_test
