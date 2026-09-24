// Independent D134 probes derived from adopted contracts and public headers.
// Uses established pre-D134 fixtures and genuine Transaction/MotorGate receipts.
// Freeze before new implementation/public-test reads; run copied four-way builds.
#include "doctest.h"
#include "core/countdown.h"
#include "core/openers.h"
#include "core/logframe.h"
#include "hal/ui_display.h"
#include "fixtures/drive_test_fixture.h"
#include <array>
#include <cmath>
#include <cstdio>
#include <limits>

namespace {
using Mode = core::Mode;
using Button = core::ButtonLevel;
using State = core::State;
struct Cycle { std::array<unsigned, 6> ids{}; unsigned count = 0U; };
Cycle expectedCycle() {
    if (config::MODE_ARC_ENABLED == 0U && config::MODE_WAIT_ENABLED == 0U)
        return {{{1U, 2U, 3U, 0U, 0U, 0U}}, 3U};
    if (config::MODE_ARC_ENABLED == 0U)
        return {{{1U, 2U, 3U, 6U, 0U, 0U}}, 4U};
    if (config::MODE_WAIT_ENABLED == 0U)
        return {{{1U, 2U, 3U, 4U, 5U, 0U}}, 5U};
    return {{{1U, 2U, 3U, 4U, 5U, 6U}}, 6U};
}
unsigned indexOf(const Cycle& cycle, unsigned id) {
    for (unsigned i = 0U; i < cycle.count; ++i) if (cycle.ids[i] == id) return i;
    APP_REQUIRE(false); return 0U;
}
struct MenuRig {
    countdown::Menu menu;
    std::uint32_t now;
    explicit MenuRig(std::uint32_t base) : now(base) {}
    countdown::MenuResult at(std::uint32_t delta, Button button = Button::NONE) {
        now += delta;
        return menu.step({now, button, State::IDLE, false, false});
    }
    void arm() { at(1U); at(20000U); }
    countdown::MenuResult shortPress() {
        at(1000U, Button::MODE); at(20000U, Button::MODE);
        at(1000U); return at(20000U);
    }
    void longPress() {
        at(1000U, Button::MODE); at(20000U, Button::MODE);
        CHECK(at(1000000U, Button::MODE).menu_toggled);
        at(1000U); CHECK_FALSE(at(20000U).selection_changed);
    }
};
void invalid(const openers::FlankResult& r) {
    CHECK(r.phase == openers::Phase::INVALID);
    CHECK(r.exit == openers::Exit::INVALID);
    CHECK(r.motion.status == motion::Status::INVALID);
    CHECK(r.motion.duty_l == 0.0F); CHECK(r.motion.duty_r == 0.0F);
    CHECK_FALSE(r.phase_changed); CHECK_FALSE(r.motion_timed_out);
    CHECK_FALSE(r.scan_hint_valid);
}
void select(drive_test::Rig& rig, unsigned id) {
    rig.prime(); const auto cycle = expectedCycle();
    unsigned at = indexOf(cycle, config::MODE_DEFAULT);
    while (cycle.ids[at] != id) { rig.shortMode(); at = (at + 1U) % cycle.count; }
    APP_REQUIRE(static_cast<unsigned>(rig.owner.report().robot.menu.selection.mode) == id);
}
void services(drive_test::Rig& rig, std::uint32_t release) {
    rig.at(release + 1500000U); rig.next(); rig.at(release + 4500000U);
}
}

TEST_CASE("B13 D134 private literal availability truth table and historical identities") {
    static_assert(core::modeAvailable(Mode::SIDESTEP_R));
    static_assert(core::modeAvailable(Mode::SIDESTEP_L));
    static_assert(core::modeAvailable(Mode::DIRECT));
    const auto cycle = expectedCycle();
    for (unsigned id = 0U; id < 256U; ++id) {
        bool expected = false;
        for (unsigned i = 0U; i < cycle.count; ++i) expected |= cycle.ids[i] == id;
        CHECK(core::modeAvailable(static_cast<Mode>(id)) == expected);
    }
    for (unsigned id = 1U; id <= 6U; ++id) {
        logframe::FrameInput input; input.mode = static_cast<Mode>(id);
        logframe::FrameBytes bytes;
        CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
        CHECK(bytes.data[5] == id);
        ui::DisplaySample sample; sample.state = State::IDLE; sample.mode = input.mode;
        ui::Frame pixels;
        CHECK(ui::render(sample, pixels) == ui::RenderStatus::OK);
    }
    std::printf("D134 private layouts Menu=%zu Flank=%zu Wait=%zu Robot=%zu Transaction=%zu\n",
                sizeof(countdown::Menu), sizeof(openers::Flank), sizeof(openers::Wait),
                sizeof(fsm::Robot), sizeof(app::Transaction));
}

TEST_CASE("B13 D134 private menu wraps twice and services retain selected mode") {
    for (const auto base : {0U, 0xfffffff0U}) {
        MenuRig rig(base); rig.arm(); const auto cycle = expectedCycle();
        unsigned index = indexOf(cycle, config::MODE_DEFAULT);
        CHECK(static_cast<unsigned>(rig.menu.selection().mode) == config::MODE_DEFAULT);
        for (unsigned i = 0U; i < 2U * cycle.count; ++i) {
            const auto result = rig.shortPress(); index = (index + 1U) % cycle.count;
            CHECK(result.selection_changed); CHECK_FALSE(result.menu_toggled);
            CHECK(static_cast<unsigned>(result.selection.mode) == cycle.ids[index]);
            CHECK_FALSE(rig.at(0U, Button::MODE).selection_changed);
        }
        const auto saved = rig.menu.selection().mode;
        rig.longPress(); CHECK(rig.menu.selection().service_menu);
        for (unsigned expected : {2U, 3U, 4U, 1U}) {
            const auto r = rig.shortPress();
            CHECK(static_cast<unsigned>(r.selection.service) == expected);
            CHECK(r.selection.mode == saved);
        }
        rig.longPress(); CHECK_FALSE(rig.menu.selection().service_menu);
        CHECK(rig.menu.selection().mode == saved);
        rig.menu.reset(); CHECK(static_cast<unsigned>(rig.menu.selection().mode) == config::MODE_DEFAULT);
    }
}

TEST_CASE("B12 D134 private rejected flank replacement cannot preserve old activity") {
    for (unsigned id : {0U, 1U, 2U, 3U, 4U, 5U, 6U, 7U, 255U}) {
        openers::Flank script;
        APP_REQUIRE(script.start(100U, 0.0F, false, Mode::SIDESTEP_R));
        const bool accepted = id == 1U || id == 2U ||
            ((id == 4U || id == 5U) && config::MODE_ARC_ENABLED == 1U);
        CHECK(script.start(0xfffffff0U, 30.0F, false, static_cast<Mode>(id)) == accepted);
        if (accepted) continue;
        for (unsigned mask = 0U; mask < 128U; ++mask) {
            const openers::Sample sample{0xfffffff0U + mask * 100000U,
                mask % 2U ? std::numeric_limits<float>::quiet_NaN() : 10.0F,
                mask % 2U != 0U, static_cast<std::uint8_t>(mask), 0.0F, true};
            invalid(script.step(sample));
        }
        APP_REQUIRE(script.start(9000000U, 0.0F, false, Mode::SIDESTEP_L));
        CHECK(script.step({9000000U, 0.0F, false, 0U, 0.0F, false}).phase == openers::Phase::PIVOT);
    }
}

TEST_CASE("B12 D055 D134 private WAIT admission preserves ordered full SIDESTEP cue") {
    openers::Wait script;
    CHECK(script.start(0xfffffff0U, 0.0F) == (config::MODE_WAIT_ENABLED == 1U));
    if (config::MODE_WAIT_ENABLED == 0U) {
        for (unsigned mask = 0U; mask < 128U; ++mask) {
            const auto r = script.step({0xfffffff0U + mask * 100000U, 0.0F, true,
                static_cast<std::uint8_t>(mask), 0.0F, true});
            CHECK(r.phase == openers::WaitPhase::INVALID); CHECK(r.brake);
            CHECK_FALSE(r.phase_changed); CHECK_FALSE(r.approach_cue); invalid(r.flank);
        }
        CHECK_FALSE(script.start(20U, 0.0F));
    } else {
        auto r = script.step({0xfffffff0U, 0.0F, false, 2U, 0.0F, true});
        CHECK(r.phase == openers::WaitPhase::HOLD); CHECK(r.brake); CHECK_FALSE(r.approach_cue);
        r = script.step({984U, 0.0F, false, 3U, 0.0F, true});
        CHECK(r.approach_cue); CHECK(r.phase == openers::WaitPhase::FLANK);
        CHECK(r.flank.phase == openers::Phase::PIVOT);
        CHECK(r.flank.motion.status == motion::Status::ACTIVE);
    }
}

TEST_CASE("B3 B12 B13 D134 private actual menu capture keeps Gate hold and edge priority") {
    const auto cycle = expectedCycle();
    for (unsigned i = 0U; i < cycle.count; ++i) {
        drive_test::Rig rig; select(rig, cycle.ids[i]);
        const auto release = rig.releaseSelected();
        APP_REQUIRE(rig.owner.report().robot.lifecycle.gate.start_release);
        CHECK(static_cast<unsigned>(rig.owner.report().robot.running_mode) == cycle.ids[i]);
        services(rig, release);
        const auto& held = rig.at(release + 5099999U);
        drive_test::disabled(held, rig.port);
        const auto& go = rig.at(release + 5100000U);
        CHECK(go.robot.lifecycle.gate.go);
        CHECK(static_cast<unsigned>(go.robot.running_mode) == cycle.ids[i]);
        CHECK(go.robot.outputs.ui_state == State::OPENER);
        CHECK(go.robot.contract_faults == 0U);
        CHECK(go.applied.feedback.applied_valid);
        CHECK(go.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
        CHECK(std::fabs(go.robot.outputs.duty_l) <= 0.85F);
        CHECK(std::fabs(go.robot.outputs.duty_r) <= 0.85F);
        rig.white(1U); CHECK(rig.next().robot.outputs.ui_state == State::EDGE_ESCAPE);
        rig.white(0U);
        rig.next(1000U, Button::BOTH);
        rig.next(20000U, Button::BOTH);
        const auto& stopped = rig.next(1000000U, Button::BOTH);
        CHECK(stopped.robot.outputs.ui_state == State::STOPPED);
        drive_test::disabled(stopped, rig.port);
    }
}

TEST_CASE("B12 D034 D134 private stale snapshot cannot replace current routing") {
    for (unsigned current : {0U, 2U, 8U}) {
        drive_test::Rig rig; select(rig, 3U); rig.opponent(2U);
        const auto release = rig.releaseSelected();
        APP_REQUIRE(rig.owner.report().robot.lifecycle.gate.start_release);
        rig.opponent(current); services(rig, release);
        const auto& r = rig.at(release + 5100000U).robot;
        const auto expected = current == 0U ? State::SEARCH :
            current == 2U ? State::TRACK : State::DEFEND_TURN;
        CHECK(r.outputs.ui_state == expected); CHECK_FALSE(r.contact);
        CHECK(r.contract_faults == 0U); CHECK(r.outputs.ui_state != State::ATTACK);
        CHECK(std::fabs(r.outputs.duty_l) <= 0.8F);
        CHECK(std::fabs(r.outputs.duty_r) <= 0.8F);
    }
}
