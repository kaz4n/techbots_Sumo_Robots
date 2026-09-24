// Tests D138 pre-start metadata and literal B13 informational matrix pixels.
// Expectations come from the adopted contract and public source-only fixtures.
// Root runs these frozen tests in host motor variants and relevant profiles.
#include "doctest.h"
#include "hal/ui_display.h"
#include "robot_scenario.h"
#include "fixtures/qtr_cal_fixture.h"
#include <array>
#include <cmath>
#include <cstring>
#include <limits>

#define P7_REQUIRE(...) do { const bool ok = (__VA_ARGS__); CHECK(ok); if (!ok) return; } while (false)
#define P7_REQUIRE_FALSE(...) P7_REQUIRE(!(__VA_ARGS__))

namespace readiness_test {
using Rows = std::array<unsigned, 5>;
constexpr Rows DIGITS[] = {{7,5,7,5,7},{2,6,2,2,7},{7,1,7,4,7},
    {7,1,7,1,7},{5,5,7,1,1},{7,4,7,1,7},{7,4,7,5,7}};
constexpr Rows ICONS[] = {{4,2,31,2,4},{4,8,31,8,4},{4,14,21,4,4},
    {0,14,17,2,7},{0,14,17,8,28},{10,10,10,10,10}};
constexpr Rows FAULTS[] = {{7,2,2,2,7},{7,4,7,1,7},{7,5,7,3,1},
    {4,4,4,4,7},{7,4,4,4,7},{5,5,5,7,5},{7,4,6,4,7}};
constexpr Rows READY = {6,5,6,5,5};
constexpr bool ORDINARY = !(SUMOX_B4_STAND || SUMOX_P3_DRIVE_TEST ||
    SUMOX_P3_TURN_TRIAL || SUMOX_P3_STOP_TRIAL || SUMOX_P4_REACTIVE ||
    SUMOX_TIMING_EVIDENCE || SUMOX_P5_ABORT_TIMING);

void glyph(ui::Frame& f, Rows rows, unsigned x, unsigned width) {
    for (unsigned y = 0U; y < 5U; ++y)
        for (unsigned col = 0U; col < width; ++col)
            f.pixels[(y + 1U) * 13U + x + col] =
                (rows[y] & (1U << (width - col - 1U))) ? 7U : 0U;
}
ui::Frame normal(unsigned mode = 1U) {
    ui::Frame f; glyph(f, DIGITS[mode], 0U, 3U); glyph(f, ICONS[mode - 1U], 4U, 5U);
    for (unsigned x = 0U; x < 13U; ++x) f.pixels[91U+x] = 7U;
    return f;
}
ui::DisplaySample ready() {
    ui::DisplaySample s; s.state = core::State::IDLE;
    s.battery_available = s.opponents_available = s.lines_available = true;
    s.battery_v = config::UI_BATTERY_FULL_V;
    s.start_status_available = s.start_ready = true; return s;
}
void battery(ui::Frame& f, const ui::DisplaySample& s) {
    for (unsigned i = 1U; i <= 13U; ++i) {
        const double threshold = double(config::UI_BATTERY_EMPTY_V) +
            (double(config::UI_BATTERY_FULL_V) - double(config::UI_BATTERY_EMPTY_V)) * i / 13.0;
        f.pixels[90U+i] = s.battery_available ? (double(s.battery_v) >= threshold ? 7U : 0U)
                                                   : (i % 2U ? 7U : 0U);
    }
}
void exact(const ui::DisplaySample& s, const ui::Frame& expected,
           ui::RenderStatus status = ui::RenderStatus::OK) {
    struct Guard { std::uint8_t before[9]; ui::Frame frame; std::uint8_t after[11]; } g;
    std::memset(&g, 0xa5, sizeof g);
    CHECK(ui::render(s, g.frame) == status);
    for (unsigned i = 0U; i < 104U; ++i) {
        CAPTURE(i); CHECK(g.frame.pixels[i] == expected.pixels[i]);
    }
    for (auto b : g.before) CHECK(b == 0xa5U);
    for (auto b : g.after) CHECK(b == 0xa5U);
}
struct Core : robot_test::Rig {
    core::ButtonEvidence latest;
    std::uint32_t sequence = 0U;
    fsm::RobotResult fresh(std::uint32_t time, core::ButtonLevel level = core::ButtonLevel::NONE) {
        latest = {true, true, core::ButtonPresence::VALID, level,
            static_cast<std::uint16_t>(100U + static_cast<unsigned>(level)), ++sequence, time, time};
        auto source = at(time); source.buttons = latest; return submit(source);
    }
    fsm::RobotResult run(std::uint32_t first, std::uint32_t span,
                        core::ButtonLevel level = core::ButtonLevel::NONE) {
        for (std::uint32_t age = 0U; age <= span; age += 1000U) fresh(first + age, level);
        return last;
    }
    fsm::RobotResult replay(std::uint32_t time) {
        auto source = at(time); source.buttons = latest; return submit(source);
    }
};
} // namespace readiness_test
using namespace readiness_test;

TEST_CASE("B13 D138 all six literal ready frames preserve mode and full battery") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) for (bool blink : {false, true}) {
        auto s = ready(); s.mode = static_cast<core::Mode>(mode);
        s.t_us = blink ? 0U : config::UI_FAULT_PAGE_MS * 1000U;
        auto expected = normal(mode); expected.pixels[90U] = 7U;
        if (blink) glyph(expected, READY, 10U, 3U);
        exact(s, expected);
    }
}
TEST_CASE("B13 D138 exact threshold nextafter and unknown marker preserve all13 bar pixels") {
    const float values[] = {0.0F, std::nextafter(config::VBAT_WARN_V, 0.0F),
        config::VBAT_WARN_V, std::nextafter(config::VBAT_WARN_V, INFINITY),
        config::UI_BATTERY_FULL_V};
    for (float value : values) for (bool available : {false, true}) {
        auto s = ready(); s.battery_v = value; s.battery_available = available;
        auto expected = normal(); battery(expected, s);
        expected.pixels[90U] = !available ? 0U : (value < config::VBAT_WARN_V ? 3U : 7U);
        if (available && value >= config::VBAT_WARN_V) glyph(expected, READY, 10U, 3U);
        exact(s, expected);
    }
}
TEST_CASE("B13 D138 all fault bits retain priority with current battery marker independent of latch") {
    for (unsigned mask = 1U; mask < 128U; ++mask) {
        auto s = ready(); s.faults = static_cast<std::uint8_t>(mask);
        auto expected = normal(); expected.pixels[90U] = 7U;
        unsigned first = 0U; while ((mask & (1U << first)) == 0U) ++first;
        glyph(expected, FAULTS[first], 10U, 3U);
        for (unsigned bit = 0U; bit < 7U; ++bit)
            expected.pixels[bit*2U] = (mask & (1U << bit)) ? 7U : 0U;
        exact(s, expected);
    }
    auto s = ready(); s.battery_v = std::nextafter(config::VBAT_WARN_V, 0.0F);
    auto expected = normal(); battery(expected, s); expected.pixels[90U] = 3U;
    CHECK(s.faults == 0U); exact(s, expected);
}
TEST_CASE("B13 D138 every missing allclear component suppresses R but preserves marker") {
    for (unsigned missing = 0U; missing < 7U; ++missing) {
        auto s = ready(); auto expected = normal(); expected.pixels[90U] = 7U;
        if (missing == 0U) s.start_ready = false;
        if (missing == 1U) s.opponents_available = false;
        if (missing == 2U) s.lines_available = false;
        if (missing >= 3U) s.line_mask = static_cast<std::uint8_t>(1U << (missing - 3U));
        exact(s, expected);
    }
}
TEST_CASE("B13 D138 blink exact boundaries and uint32wrap are display pages only") {
    const std::uint32_t times[] = {0U, 499999U, 500000U, 999999U, 1000000U,
        1499999U, 1500000U, 0xfffffffeU, 0xffffffffU};
    for (auto time : times) {
        auto s = ready(); s.t_us = time;
        auto expected = normal(); expected.pixels[90U] = 7U;
        if (((time / 1000U / config::UI_FAULT_PAGE_MS) % 2U) == 0U)
            glyph(expected, READY, 10U, 3U);
        exact(s, expected);
    }
}
TEST_CASE("B13 D138 unbound fields are inert and every nonmatch view keeps its entire frame") {
    for (unsigned state = 0U; state <= 11U; ++state) for (unsigned service = 0U; service <= 4U; ++service) {
        auto s = ready(); s.state = static_cast<core::State>(state);
        s.service_menu = service != 0U; s.service = static_cast<countdown::Service>(service);
        s.start_status_available = false; s.start_ready = false;
        ui::Frame baseline, candidate; const auto status = ui::render(s, baseline);
        s.start_ready = true; CHECK(ui::render(s, candidate) == status);
        CHECK(std::memcmp(baseline.pixels, candidate.pixels, 104U) == 0);
        if (state != static_cast<unsigned>(core::State::IDLE) || service != 0U) {
            s.start_status_available = true; CHECK(ui::render(s, candidate) == status);
            CHECK(std::memcmp(baseline.pixels, candidate.pixels, 104U) == 0);
        }
    }
}
TEST_CASE("B13 D138 malformed available battery preserves literal invalid frame without extension") {
    const float bad[] = {-1.0F, INFINITY, -INFINITY, std::numeric_limits<float>::quiet_NaN()};
    for (float value : bad) {
        auto s = ready(); s.battery_v = value; ui::Frame expected;
        glyph(expected, {7,4,6,4,7}, 0U, 3U); glyph(expected, {17,10,4,10,17}, 4U, 5U);
        for (unsigned bit = 0U; bit < 7U; ++bit) expected.pixels[2U*bit] = 7U;
        for (unsigned x = 0U; x < 13U; x += 2U) expected.pixels[91U+x] = 7U;
        exact(s, expected, ui::RenderStatus::INVALID);
        s.battery_available = false; expected = normal(); battery(expected, s); exact(s, expected);
    }
}
TEST_CASE("B13 D138 pure Robot mapping never fabricates actual Runtime status") {
    robot_test::Rig rig; robot_test::idle(rig); auto out = rig.last;
    out.match_start_eligible = true;
    auto s = ui::displaySample(rig.at(rig.last_time), out);
    CHECK_FALSE(s.start_status_available); CHECK_FALSE(s.start_ready);
    out.fresh = false; s = ui::displaySample(rig.at(rig.last_time), out);
    CHECK_FALSE(s.start_status_available); CHECK_FALSE(s.start_ready);
}
TEST_CASE("B3 D138 neutralStartArmed observes real Buttons rearming without changing events") {
    countdown::Buttons buttons; const countdown::Buttons& view = buttons;
    CHECK_FALSE(view.neutralStartArmed()); buttons.step(0U, core::ButtonLevel::NONE);
    buttons.step(20000U, core::ButtonLevel::NONE); CHECK(view.neutralStartArmed());
    CHECK(view.neutralStartArmed());
    buttons.step(21000U, core::ButtonLevel::MODE); CHECK_FALSE(view.neutralStartArmed());
    CHECK(buttons.step(41000U, core::ButtonLevel::MODE).mode_press);
    buttons.step(42000U, core::ButtonLevel::NONE); CHECK_FALSE(view.neutralStartArmed());
    buttons.step(61999U, core::ButtonLevel::NONE); CHECK_FALSE(view.neutralStartArmed());
    buttons.step(62000U, core::ButtonLevel::NONE); CHECK(view.neutralStartArmed());
    buttons.step(63000U, core::ButtonLevel::START); CHECK_FALSE(view.neutralStartArmed());
    buttons.step(83000U, core::ButtonLevel::START); CHECK_FALSE(view.neutralStartArmed());
    buttons.step(84000U, core::ButtonLevel::NONE); CHECK_FALSE(view.neutralStartArmed());
    CHECK(buttons.step(104000U, core::ButtonLevel::NONE).start_release);
    CHECK(view.neutralStartArmed()); buttons.reset(); CHECK_FALSE(view.neutralStartArmed());
}
TEST_CASE("B3 D138 Controller and Lifecycle forward neutral observation independently of Gate permission") {
    countdown::Controller controller; countdown::Lifecycle lifecycle;
    CHECK_FALSE(controller.neutralStartArmed()); CHECK_FALSE(lifecycle.neutralStartArmed());
    const std::uint32_t times[] = {0U,20000U,21000U,41000U,42000U,62000U};
    const core::ButtonLevel levels[] = {core::ButtonLevel::NONE,core::ButtonLevel::NONE,
        core::ButtonLevel::START,core::ButtonLevel::START,core::ButtonLevel::NONE,core::ButtonLevel::NONE};
    for (unsigned i = 0U; i < 6U; ++i) {
        core::Inputs in; in.t_us = times[i]; in.button_level = levels[i];
        countdown::ServiceSample service; service.t_us = times[i];
        const auto a = controller.step(in); const auto b = lifecycle.step(service,levels[i],0.0F);
        CHECK(controller.neutralStartArmed() == lifecycle.neutralStartArmed());
        CHECK(a.phase == b.gate.phase);
    }
    CHECK(controller.neutralStartArmed()); CHECK(lifecycle.neutralStartArmed());
    controller.reset(); lifecycle.reset();
    CHECK_FALSE(controller.neutralStartArmed()); CHECK_FALSE(lifecycle.neutralStartArmed());
}
TEST_CASE("B3 D138 current qualified explicit neutral alone publishes eligible metadata") {
    Core rig; const auto first = rig.fresh(1000U); CHECK_FALSE(first.match_start_eligible);
    rig.run(2000U,18000U); CHECK_FALSE(rig.last.match_start_eligible);
    CHECK_FALSE(rig.fresh(20999U).match_start_eligible);
    const auto at = rig.fresh(21000U); CHECK(at.match_start_eligible == ORDINARY);
    CHECK(at.fresh); CHECK(at.button_updated); CHECK(at.outputs.ui_state == core::State::IDLE);
    robot_test::zero(at); CHECK_FALSE(at.lifecycle.gate.motion_permitted);
    CHECK_FALSE(at.lifecycle.gate.start_release); CHECK_FALSE(at.lifecycle.gate.go);
}
TEST_CASE("B3 D138 press replay duplicate malformed stop and reset cannot retain eligibility") {
    for (unsigned kind = 0U; kind < 8U; ++kind) {
        Core rig; rig.run(1000U,30000U); CHECK(rig.last.match_start_eligible == ORDINARY);
        fsm::RobotResult result;
        if (kind == 0U) result = rig.fresh(32000U,core::ButtonLevel::START);
        if (kind == 1U) result = rig.fresh(32000U,core::ButtonLevel::MODE);
        if (kind == 2U) result = rig.replay(32000U);
        if (kind == 3U) result = rig.replay(31000U);
        if (kind == 4U) { auto source = rig.at(32000U); source.buttons = rig.latest;
            source.buttons.contract_valid = false; result = rig.submit(source); }
        if (kind == 5U) { rig.input.stop_requested = true; result = rig.fresh(32000U); }
        if (kind == 6U) { rig.reset(); result = rig.fresh(32000U); }
        if (kind == 7U) result = rig.fresh(30999U);
        CHECK_FALSE(result.match_start_eligible);
    }
}
TEST_CASE("B3 D138 source and decision rollover preserve fresh neutral boundary") {
    Core rig; constexpr std::uint32_t base = 0xffffe000U;
    rig.fresh(base); rig.run(base+1000U,18000U);
    CHECK_FALSE(rig.fresh(base+19999U).match_start_eligible);
    CHECK(rig.fresh(base+20000U).match_start_eligible == ORDINARY);
    CHECK_FALSE(rig.replay(base+20000U).match_start_eligible);
}
TEST_CASE("B3 D138 legacy valid control does not fabricate explicit readiness") {
    robot_test::Rig rig; robot_test::idle(rig);
    CHECK_FALSE(rig.last.match_start_eligible);
    CHECK_FALSE(rig.step(30000U).match_start_eligible);
}
TEST_CASE("B13 D138 every compiled nondefault profile suppresses metadata on fresh neutral") {
    if (ORDINARY) return;
    Core rig;
    for (unsigned i = 0U; i < 100U; ++i) {
        const auto out = rig.fresh(1000U+i*1000U);
        CHECK(out.fresh); CHECK_FALSE(out.match_start_eligible);
    }
}
#if !SUMOX_B4_STAND && !SUMOX_P3_DRIVE_TEST && !SUMOX_P3_TURN_TRIAL && !SUMOX_P3_STOP_TRIAL && !SUMOX_P4_REACTIVE && !SUMOX_TIMING_EVIDENCE && !SUMOX_P5_ABORT_TIMING
TEST_CASE("B13 D138 mode-cycle transition and real neutral rearming suppress current eligibility") {
    Core rig; rig.run(1000U,30000U);
    rig.run(32000U,20000U,core::ButtonLevel::MODE);
    CHECK_FALSE(rig.fresh(53000U).match_start_eligible);
    rig.run(54000U,18000U); CHECK_FALSE(rig.last.match_start_eligible);
    const auto changed = rig.fresh(73000U); CHECK(changed.menu.selection_changed);
    CHECK_FALSE(changed.match_start_eligible);
    CHECK(rig.fresh(74000U).match_start_eligible);
}
TEST_CASE("B13 D138 service menu and exit transition do not assert ordinary match readiness") {
    Core rig; rig.run(1000U,30000U);
    rig.run(32000U,1020000U,core::ButtonLevel::MODE);
    CHECK(rig.last.menu.selection.service_menu); CHECK_FALSE(rig.last.match_start_eligible);
    rig.run(1053000U,30000U); CHECK_FALSE(rig.last.match_start_eligible);
    rig.run(1084000U,1020000U,core::ButtonLevel::MODE);
    CHECK_FALSE(rig.last.menu.selection.service_menu); CHECK(rig.last.menu.menu_toggled);
    CHECK_FALSE(rig.last.match_start_eligible);
    rig.run(2105000U,19000U); CHECK_FALSE(rig.last.match_start_eligible);
    CHECK(rig.fresh(2125000U).match_start_eligible);
}
TEST_CASE("B3 D138 countdown and cancel cannot skip real neutral rearming") {
    Core rig; rig.run(1000U,30000U); rig.run(32000U,20000U,core::ButtonLevel::START);
    rig.run(53000U,20000U); CHECK(rig.last.lifecycle.gate.start_release);
    CHECK_FALSE(rig.last.match_start_eligible); robot_test::zero(rig.last);
    rig.run(74000U,20000U,core::ButtonLevel::MODE);
    CHECK(rig.last.outputs.ui_state == core::State::IDLE); CHECK_FALSE(rig.last.match_start_eligible);
    rig.run(95000U,19000U); CHECK_FALSE(rig.last.match_start_eligible);
    CHECK(rig.fresh(115000U).match_start_eligible);
}
TEST_CASE("B4 B13 D138 raw calibration classified handover and rearming never advertise early") {
    qtr_cal_test::Pipeline p; p.explicit_buttons = true; p.completeCalibration();
    P7_REQUIRE(p.report.phase == qtr_cal::Phase::SUCCESS);
    CHECK_FALSE(p.result.match_start_eligible); CHECK(p.result.line_calibration_hold);
    p.raw = false;
    for (std::uint32_t i = 0U; i < config::QTR_CONFIRM_TICKS; ++i) {
        p.tick(core::ButtonLevel::START,2000U,true); CHECK_FALSE(p.result.match_start_eligible);
    }
    CHECK(p.result.line_start_rearming); p.hold(core::ButtonLevel::NONE,24000U,true);
    CHECK_FALSE(p.result.line_start_rearming); CHECK_FALSE(p.result.match_start_eligible);
    p.leaveServiceMenu(); P7_REQUIRE_FALSE(p.result.menu.selection.service_menu);
    CHECK(p.result.match_start_eligible); CHECK_FALSE(p.result.outputs.motors_enabled);
}
#endif
