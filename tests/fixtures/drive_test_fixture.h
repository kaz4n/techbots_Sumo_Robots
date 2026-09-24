// Supplies genuine local B13 gestures to the actual P3 Transaction and Gate.
// Keeps expected times and physical callback observations independent of routing.
// Dedicated D123 M0/M1 tests use this fixture without production implementation reads.
#pragma once
#include "app_transaction_fixture.h"
#include <cmath>

namespace drive_test {
using Button = core::ButtonLevel;
struct Rig : app_test::Rig {
    std::uint32_t now = 0U;
    const app::TransactionReport& at(std::uint32_t time, Button button = Button::NONE) {
        now = time; return tick(time, button);
    }
    const app::TransactionReport& next(std::uint32_t delta = 1000U,
                                       Button button = Button::NONE) {
        return at(now + delta, button);
    }
    void prime(std::uint32_t base = 0U) {
        at(base); next(); next(20000U);
        APP_REQUIRE(owner.report().robot.outputs.ui_state == core::State::IDLE);
    }
    void shortMode() {
        next(1000U, Button::MODE); next(20000U, Button::MODE);
        next(); next(20000U);
    }
    void longMode() {
        next(1000U, Button::MODE); next(20000U, Button::MODE);
        next(1000000U, Button::MODE); next(); next(20000U);
    }
    void selectDrive(std::uint32_t base = 0U) {
        prime(base); longMode(); shortMode(); shortMode();
        const auto selected = owner.report().robot.menu.selection;
        APP_REQUIRE(selected.service_menu);
        APP_REQUIRE(selected.service == countdown::Service::DRIVE_TEST);
    }
    std::uint32_t releaseSelected() {
        next(1000U, Button::START); next(20000U, Button::START);
        next(); next(20000U); return now;
    }
    std::uint32_t releaseDrive(std::uint32_t base = 0U) {
        selectDrive(base); const auto release = releaseSelected();
        APP_REQUIRE(owner.report().robot.lifecycle.gate.start_release);
        APP_REQUIRE(owner.report().robot.lifecycle.gate.release_us == release);
        return release;
    }
    std::uint32_t goDrive(std::uint32_t base = 0U) {
        const auto release = releaseDrive(base);
        at(release + 1500000U); next(); at(release + 4500000U);
        at(release + 5099999U); at(release + 5100000U);
        APP_REQUIRE(owner.report().robot.lifecycle.gate.go); return now;
    }
    void opponent(unsigned logical) {
        source.opp_raw_mask = static_cast<std::uint8_t>(logical ^ 0x78U);
    }
    void white(unsigned mask) {
        for (unsigned i = 0U; i < 4U; ++i)
            source.line_raw_us[i] = (mask & (1U << i)) ? 100U : 1000U;
    }
};
inline void noCombat(const fsm::RobotResult& result) {
    CHECK_FALSE(result.contact); CHECK_FALSE(result.all_in);
    CHECK(result.outputs.ui_state != core::State::OPENER);
    CHECK(result.outputs.ui_state != core::State::TRACK);
    CHECK(result.outputs.ui_state != core::State::ATTACK);
    CHECK(result.outputs.ui_state != core::State::DEFEND_TURN);
    CHECK(result.outputs.ui_state != core::State::REFLANK);
    for (unsigned i = 0U; i < result.events.count; ++i) {
        CHECK(result.events.entries[i].type != core::Event::CONTACT);
        CHECK(result.events.entries[i].type != core::Event::STALL);
        CHECK(result.events.entries[i].type != core::Event::REFLANK_PHASE);
    }
}
inline void disabled(const app::TransactionReport& report, const app_test::Port& port) {
    CHECK_FALSE(report.robot.outputs.motors_enabled);
    CHECK(report.robot.outputs.duty_l == 0.0F); CHECK(report.robot.outputs.duty_r == 0.0F);
    CHECK_FALSE(report.applied.feedback.motors_enabled);
    CHECK(report.applied.feedback.duty_l == 0.0F); CHECK(report.applied.feedback.duty_r == 0.0F);
    app_test::zero(port);
}
inline void moving(const Rig& rig, const app::TransactionReport& report) {
    CHECK(report.robot.outputs.ui_state == core::State::DRIVE_TEST);
    CHECK(report.robot.outputs.motors_enabled); CHECK(report.robot.contract_faults == 0U);
    CHECK(report.applied.consumed); CHECK(report.applied.feedback.applied_valid);
    CHECK(report.applied.fault == motors::Fault::NONE);
    CHECK(report.applied.feedback.token == report.robot.token);
    CHECK(report.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
    CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0)); noCombat(report.robot);
    CHECK(std::fabs(report.applied.feedback.duty_l) <= std::fabs(report.robot.outputs.duty_l));
    CHECK(std::fabs(report.applied.feedback.duty_r) <= std::fabs(report.robot.outputs.duty_r));
    if (!MOTORS_ALLOWED) { CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U); }
}
inline unsigned eventCount(const recorder::AttemptRecorder& recording, core::Event kind,
                           std::uint32_t* timestamp = nullptr) {
    unsigned count = 0U;
    for (std::size_t i = 0U; i < recording.events().size(); ++i) {
        const auto* event = recording.events().at(i); APP_REQUIRE(event != nullptr);
        if (event->data[4] != static_cast<unsigned>(kind)) continue;
        ++count; if (timestamp != nullptr) *timestamp = app_test::u32(event->data);
    }
    return count;
}
} // namespace drive_test
