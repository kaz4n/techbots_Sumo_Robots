// Checks B7/B12/B13/D134 availability without changing historical mode identities.
// Uses specification literals and public entry points across four copied configs.
// Dedicated M0/M1 host targets exercise actual Robot selection and MotorGate receipts.
#include "doctest.h"
#include "fixtures/mode_availability_fixture.h"
#include "hal/ui_display.h"
#include "core/logframe.h"
#include <limits>

using namespace mode_test;
namespace {
struct MenuRig {
    countdown::Menu menu;
    countdown::MenuSample input;
    countdown::MenuResult last;
    explicit MenuRig(std::uint32_t base = 0U) {
        input.state_at_entry = State::IDLE; input.t_us = base;
        step(0U); step(20000U);
    }
    void step(std::uint32_t delta, Button button = Button::NONE) {
        input.t_us += delta; input.button = button; last = menu.step(input);
    }
    void shortMode(std::uint32_t held = 1000U) {
        step(1000U, Button::MODE); step(20000U, Button::MODE);
        step(held); step(20000U);
    }
};
void expectFrontHandover(Rig& rig) {
    CHECK(rig.last.outputs.ui_state == State::TRACK); governed(rig, 0.30F);
    rig.next(); CHECK(rig.last.outputs.ui_state == State::TRACK);
    rig.next(); CHECK(rig.last.outputs.ui_state == State::ATTACK);
    governed(rig, 0.60F);
}
void checkGlyph(unsigned id, const ui::Frame& frame) {
    constexpr unsigned digits[6][5] = {{2,6,2,2,7},{7,1,7,4,7},{7,1,7,1,7},
        {5,5,7,1,1},{7,4,7,1,7},{7,4,7,5,7}};
    constexpr unsigned icons[6][5] = {{4,2,31,2,4},{4,8,31,8,4},{4,14,21,4,4},
        {0,14,17,2,7},{0,14,17,8,28},{10,10,10,10,10}};
    for (unsigned row = 0U; row < 5U; ++row) {
        for (unsigned col = 0U; col < 3U; ++col)
            CHECK(frame.pixels[(row + 1U) * 13U + col] ==
                  ((digits[id - 1U][row] & (4U >> col)) ? 7U : 0U));
        for (unsigned col = 0U; col < 5U; ++col)
            CHECK(frame.pixels[(row + 1U) * 13U + 4U + col] ==
                  ((icons[id - 1U][row] & (16U >> col)) ? 7U : 0U));
    }
}
} // namespace

TEST_CASE("B13 D134 constexpr query admits only the configured literal IDs") {
    static_assert(core::modeAvailable(Mode::SIDESTEP_R), "mandatory right");
    static_assert(core::modeAvailable(Mode::SIDESTEP_L), "mandatory left");
    static_assert(core::modeAvailable(Mode::DIRECT), "mandatory direct");
    static_assert(!core::modeAvailable(static_cast<Mode>(0U)), "invalid zero");
    static_assert(core::modeAvailable(static_cast<Mode>(config::MODE_DEFAULT)), "default");
    for (unsigned id = 0U; id < 256U; ++id) {
        CAPTURE(id); CHECK(core::modeAvailable(static_cast<Mode>(id)) == expected(id));
    }
}

TEST_CASE("B13 D134 pure Menu completes two exact cycles and reset at normal and wrapped time") {
    for (auto base : {0U, 0xffff0000U}) {
        MenuRig rig(base); auto expected_mode = static_cast<Mode>(config::MODE_DEFAULT);
        CHECK(rig.menu.selection().mode == expected_mode);
        for (unsigned i = 0U; i < 2U * size(); ++i) {
            expected_mode = nextMode(expected_mode); rig.shortMode();
            CHECK(rig.last.selection_changed); CHECK(rig.last.selection.mode == expected_mode);
            rig.step(0U, Button::BOTH);
            CHECK_FALSE(rig.last.selection_changed); CHECK_FALSE(rig.last.menu_toggled);
            CHECK(rig.last.selection.mode == expected_mode);
        }
        rig.menu.reset();
        CHECK(rig.menu.selection().mode == static_cast<Mode>(config::MODE_DEFAULT));
        CHECK_FALSE(rig.menu.selection().service_menu);
    }
}

TEST_CASE("B13 D134 MODE duration bounds and unqualified pulses do not bypass availability") {
    for (auto held : {599999U, 600000U, 999999U, 1000000U}) {
        MenuRig rig; rig.shortMode(held);
        CHECK(rig.last.selection.mode == (held < 600000U ?
              nextMode(static_cast<Mode>(config::MODE_DEFAULT)) :
              static_cast<Mode>(config::MODE_DEFAULT)));
        CHECK_FALSE(rig.last.selection.service_menu);
    }
    MenuRig rig; rig.step(1000U, Button::MODE); rig.step(19999U, Button::MODE);
    rig.step(1U); rig.step(20000U);
    CHECK(rig.last.selection.mode == static_cast<Mode>(config::MODE_DEFAULT));
}

TEST_CASE("B13 D134 actual Robot legacy and explicit menus preserve all service entries") {
    for (bool explicit_source : {false, true}) {
        Rig rig(explicit_source); rig.prime();
        auto selected = static_cast<Mode>(config::MODE_DEFAULT);
        for (unsigned i = 0U; i < 2U * size(); ++i) {
            rig.shortMode(); selected = nextMode(selected);
            CHECK(rig.last.menu.selection.mode == selected); zero(rig);
        }
        rig.longMode(); CHECK(rig.last.menu.selection.service_menu);
        for (unsigned service = 1U; service <= 4U; ++service) {
            CHECK(rig.last.menu.selection.service == static_cast<countdown::Service>(service));
            CHECK(rig.last.menu.selection.mode == selected); rig.shortMode(); zero(rig);
        }
        CHECK(rig.last.menu.selection.service == countdown::Service::SENSOR_VIEW);
        rig.longMode(); CHECK_FALSE(rig.last.menu.selection.service_menu);
        CHECK(rig.last.menu.selection.mode == selected);
        rig.reset(); rig.prime();
        CHECK(rig.last.menu.selection.mode == static_cast<Mode>(config::MODE_DEFAULT));
        CHECK(rig.last.running_mode == static_cast<Mode>(config::MODE_DEFAULT)); zero(rig);
    }
}

TEST_CASE("B13 D134 each available Robot choice is captured on release and retained at GO") {
    for (bool explicit_source : {false, true}) for (unsigned id = 1U; id <= 6U; ++id) {
        if (!expected(id)) continue;
        CAPTURE(explicit_source); CAPTURE(id); Rig rig(explicit_source); rig.prime();
        rig.select(static_cast<Mode>(id));
        CHECK(rig.last.running_mode == static_cast<Mode>(config::MODE_DEFAULT));
        const auto release = rig.release();
        CHECK(rig.last.running_mode == static_cast<Mode>(id)); zero(rig);
        rig.finishHold(release);
        CHECK(rig.last.running_mode == static_cast<Mode>(id));
        CHECK(rig.last.outputs.ui_state == State::OPENER); governed(rig, 0.85F);
        CHECK(rig.last.outputs.motors_enabled);
        CHECK(rig.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
    }
}

TEST_CASE("B12 D134 Flank rejects unavailable ARC and every nonflank ID after active SIDESTEP") {
    for (unsigned id = 0U; id < 256U; ++id) {
        if (id == 1U || id == 2U || ((id == 4U || id == 5U) && expected(id))) continue;
        CAPTURE(id); openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, Mode::SIDESTEP_R));
        CHECK(flank.step(sample(1000U)).motion.duty_l > 0.0F);
        CHECK_FALSE(flank.start(2000U, 0.0F, true, static_cast<Mode>(id)));
        for (auto time : {2000U, 3000U, 3000000U, 0xfffffff0U, 1000U}) {
            const auto result = flank.step(sample(time, 50.0F, 127U));
            invalid(result); CHECK_FALSE(result.phase_changed);
        }
        flank.reset(); CHECK(flank.step(sample(2000U)).phase == openers::Phase::IDLE);
        CHECK(flank.start(3000U, 0.0F, true, Mode::SIDESTEP_L));
        CHECK(flank.step(sample(4000U)).motion.duty_l < 0.0F);
    }
}

TEST_CASE("B7 B12 D134 enabled flank mirrors keep pivot ignore and exact fallback transition") {
    for (unsigned id : {1U, 2U, 4U, 5U}) {
        if (!expected(id)) continue;
        CAPTURE(id); const float sign = (id == 2U || id == 5U) ? -1.0F : 1.0F;
        const auto pivot_us = id < 3U ? 100000U : 160000U;
        openers::Flank flank;
        CHECK(flank.start(0xffff0000U, 0.0F, false, static_cast<Mode>(id)));
        const auto before = flank.step(sample(0xffff0000U + pivot_us - 1U, 0.0F, 2U, false));
        CHECK(before.phase == openers::Phase::PIVOT); CHECK(before.exit == openers::Exit::NONE);
        CHECK(before.motion.duty_l == doctest::Approx(sign * 0.80F));
        CHECK(before.motion.duty_r == doctest::Approx(-sign * 0.80F));
        const auto at = flank.step(sample(0xffff0000U + pivot_us, 0.0F, 2U, false));
        CHECK(at.exit == openers::Exit::FRONT_TARGET);
        CHECK(at.phase == openers::Phase::FINISHED);
        CHECK(at.motion.duty_l == 0.0F); CHECK(at.motion.duty_r == 0.0F);
    }
}

TEST_CASE("B12 D134 disabled WAIT rejects repeated starts and every cue without pulses") {
    if constexpr (config::MODE_WAIT_ENABLED == 0U) {
        openers::Wait wait;
        for (auto base : {0U, 0xfffffff0U}) {
            CHECK_FALSE(wait.start(base, 0.0F));
            for (unsigned i = 0U; i < 128U; ++i) {
                const auto result = wait.step(sample(base + i * 30000U, 0.0F, i));
                CHECK(result.phase == openers::WaitPhase::INVALID); CHECK(result.brake);
                CHECK_FALSE(result.approach_cue); CHECK_FALSE(result.phase_changed);
                invalid(result.flank); CHECK_FALSE(result.flank.phase_changed);
            }
            wait.reset(); CHECK(wait.step(sample(base)).phase == openers::WaitPhase::IDLE);
        }
    }
}

TEST_CASE("B12 D055 D134 enabled WAIT cue retains complete timed SIDESTEP R") {
    if constexpr (config::MODE_WAIT_ENABLED == 1U) {
        openers::Wait wait; CHECK(wait.start(0U, 0.0F));
        CHECK(wait.step(sample(1000U, 0.0F, 2U, false)).brake);
        const auto cue = wait.step(sample(301000U, 0.0F, 3U, false));
        CHECK(cue.approach_cue); CHECK(cue.phase == openers::WaitPhase::FLANK);
        CHECK(cue.flank.phase == openers::Phase::PIVOT); CHECK_FALSE(cue.brake);
        CHECK(cue.flank.motion.duty_l > 0.0F); CHECK(cue.flank.motion.duty_r < 0.0F);
        CHECK(wait.step(sample(400999U, 0.0F, 0U, false)).flank.phase == openers::Phase::PIVOT);
        CHECK(wait.step(sample(401000U, 0.0F, 0U, false)).flank.phase == openers::Phase::TRAVERSE);
        CHECK(wait.step(sample(650999U, 0.0F, 0U, false)).flank.phase == openers::Phase::TRAVERSE);
        const auto turn = wait.step(sample(651000U, 0.0F, 0U, false));
        CHECK(turn.flank.phase == openers::Phase::TURN_IN);
        CHECK(turn.flank.motion.duty_l < 0.0F); CHECK(turn.flank.motion.duty_r > 0.0F);
        CHECK(wait.step(sample(870999U, 0.0F, 0U, false)).flank.phase == openers::Phase::TURN_IN);
        const auto end = wait.step(sample(871000U, 0.0F, 0U, false));
        CHECK(end.phase == openers::WaitPhase::FINISHED); CHECK(end.brake);
        CHECK(end.flank.exit == openers::Exit::SEARCH); CHECK_FALSE(end.approach_cue);
    }
}

TEST_CASE("B12 D034 D134 Robot DIRECT current front still requires three centered observations") {
    for (bool explicit_source : {false, true}) {
        Rig rig(explicit_source); rig.prime(); rig.select(Mode::DIRECT);
        const auto release = rig.release();
        rig.at(release + 1500000U); rig.next(); rig.at(release + 4500000U);
        rig.opponent(2U); rig.at(release + 5099000U); rig.at(release + 5100000U);
        CHECK(rig.last.lifecycle.gate.go); expectFrontHandover(rig);
    }
}

TEST_CASE("B12 D034 D134 Robot flank pivot ignores front then hands over on traverse entry") {
    for (unsigned id : {1U, 2U, 4U, 5U}) {
        if (!expected(id)) continue;
        CAPTURE(id); Rig rig; rig.go(static_cast<Mode>(id)); rig.opponent(2U);
        rig.next(); rig.next(); CHECK(rig.last.outputs.ui_state == State::OPENER);
        governed(rig, 0.80F);
        const float sign = (id == 2U || id == 5U) ? -1.0F : 1.0F;
        rig.input.raw_heading_deg = sign * (id < 3U ? 50.0F : 80.0F);
        rig.next(); expectFrontHandover(rig);
    }
}

TEST_CASE("B12 D034 D134 Robot current side routes DEFEND while stale countdown front routes SEARCH") {
    for (unsigned mask : {8U, 16U, 32U, 64U}) {
        Rig rig; rig.go(Mode::DIRECT); rig.opponent(mask); rig.next(); rig.next();
        CHECK(rig.last.outputs.ui_state == State::DEFEND_TURN); governed(rig, 0.80F);
    }
    Rig rig; rig.prime(); rig.select(Mode::DIRECT); const auto release = rig.release();
    rig.at(release + 1500000U); rig.next(); rig.at(release + 4500000U);
    rig.opponent(2U); rig.at(release + 5000000U); rig.next();
    CHECK(rig.last.lifecycle.services.opponent_snapshot == 2U);
    rig.opponent(0U); rig.at(release + 5060000U); rig.at(release + 5100000U);
    CHECK(rig.last.lifecycle.gate.go); CHECK(rig.last.opponent_mask == 0U);
    CHECK(rig.last.outputs.ui_state == State::SEARCH); governed(rig, 0.80F);
}

TEST_CASE("B12 D055 D134 actual WAIT cue starts a full pivot before current front handover") {
    if constexpr (config::MODE_WAIT_ENABLED == 1U) {
        Rig rig; rig.go(Mode::WAIT);
        CHECK(rig.last.outputs.ui_state == State::OPENER);
        CHECK(rig.last.outputs.duty_l == 0.0F); CHECK(rig.last.outputs.duty_r == 0.0F);
        rig.opponent(2U); rig.next(); rig.next();
        rig.opponent(3U); rig.next(); rig.next();
        CHECK(rig.last.outputs.ui_state == State::OPENER);
        CHECK(rig.last.outputs.duty_l > 0.0F); CHECK(rig.last.outputs.duty_r < 0.0F);
        governed(rig, 0.80F);
        rig.input.raw_heading_deg = 50.0F; rig.next(); expectFrontHandover(rig);
    }
}

TEST_CASE("B13 D134 service START stays an intent and cannot capture a match mode") {
    for (bool explicit_source : {false, true}) for (unsigned service = 1U; service <= 4U; ++service) {
        Rig rig(explicit_source); rig.prime(); rig.select(Mode::DIRECT); rig.longMode();
        for (unsigned i = 1U; i < service; ++i) rig.shortMode();
        rig.next(1000U, Button::START); rig.next(20000U, Button::START);
        rig.next(); rig.next(20000U);
        CHECK(rig.last.menu.request == static_cast<countdown::Service>(service));
        CHECK(rig.last.menu.request_unavailable == (service == 3U));
        CHECK_FALSE(rig.last.lifecycle.gate.start_release);
        CHECK(rig.last.running_mode == static_cast<Mode>(config::MODE_DEFAULT));
        CHECK(rig.last.outputs.ui_state == State::IDLE); zero(rig);
        rig.next(); CHECK(rig.last.menu.request == countdown::Service::NONE);
    }
}

TEST_CASE("B13 D134 actual Robot duplicate source cannot repeat a completed mode gesture") {
    for (bool explicit_source : {false, true}) {
        Rig rig(explicit_source); rig.prime(); rig.shortMode();
        const auto selected = nextMode(static_cast<Mode>(config::MODE_DEFAULT));
        CHECK(rig.last.menu.selection.mode == selected);
        const auto token = rig.last.token; const auto calls = rig.port.count;
        rig.input.button = Button::BOTH; rig.input.buttons.level = Button::BOTH;
        const auto duplicate = rig.robot.step(rig.input);
        CHECK_FALSE(duplicate.fresh); CHECK(duplicate.token == token);
        CHECK_FALSE(duplicate.menu.selection_changed); CHECK(duplicate.events.count == 0U);
        CHECK(duplicate.menu.selection.mode == selected); CHECK(rig.port.count == calls);
        rig.next(); CHECK(rig.last.menu.selection.mode == selected); zero(rig);
    }
}

TEST_CASE("B13 B15 D134 all six historical IDs retain exact glyphs frame and event codes") {
    for (unsigned id = 1U; id <= 6U; ++id) {
        CAPTURE(id); ui::DisplaySample display; display.state = State::IDLE;
        display.mode = static_cast<Mode>(id); ui::Frame pixels;
        CHECK(ui::render(display, pixels) == ui::RenderStatus::OK); checkGlyph(id, pixels);
        logframe::FrameInput input; input.mode = static_cast<Mode>(id);
        logframe::FrameBytes frame;
        CHECK(logframe::packFrame(input, frame) == logframe::PackStatus::OK);
        CHECK(frame.data[5] == id);
        for (auto type : {core::Event::START_RELEASE, core::Event::GO}) {
            logframe::EventInput event{123U, type, static_cast<std::uint8_t>(id), 0U};
            CHECK(logframe::validEventMetadata(event)); logframe::EventBytes packed;
            CHECK(logframe::packEvent(event, packed) == logframe::PackStatus::OK);
            CHECK(packed.data[5] == id);
            const logframe::EventInput restored{app_test::u32(packed.data),
                static_cast<core::Event>(packed.data[4]), packed.data[5],
                static_cast<std::uint16_t>(packed.data[6] | (packed.data[7] << 8U))};
            CHECK(logframe::validEventMetadata(restored));
        }
    }
}
