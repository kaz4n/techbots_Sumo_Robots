// Checks B13 mode and service gestures against the D-058 public contract.
// Keeps typed UI requests separate from service execution and countdown permission.
// Independent tests cover literal boundaries, contamination, selection cycles and wraps.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include <array>
#include <cstdint>
#include <initializer_list>

namespace {
using Button = core::ButtonLevel;
using Service = countdown::Service;
using State = core::State;
using Mode = core::Mode;
constexpr Button BAD_BUTTON = static_cast<Button>(255U);
constexpr State BAD_STATE = static_cast<State>(255U);

countdown::MenuResult tick(countdown::Menu& menu, std::uint32_t time,
        Button button = Button::NONE, State state = State::IDLE,
        bool fault = false, bool release = false) {
    countdown::MenuSample sample;
    sample.t_us = time;
    sample.button = button;
    sample.state_at_entry = state;
    sample.inhibited_fault = fault;
    sample.qualified_start_release = release;
    return menu.step(sample);
}

void silent(const countdown::MenuResult& result) {
    CHECK_FALSE(result.selection_changed);
    CHECK_FALSE(result.menu_toggled);
    CHECK(result.request == Service::NONE);
    CHECK_FALSE(result.request_unavailable);
}

void selected(const countdown::MenuSelection& result, Mode mode,
              bool services = false, Service service = Service::SENSOR_VIEW) {
    CHECK(result.mode == mode);
    CHECK(result.service_menu == services);
    CHECK(result.service == service);
}

void arm(countdown::Menu& menu, std::uint32_t base) {
    silent(tick(menu, base));
    silent(tick(menu, base + 19999U));
    silent(tick(menu, base + 20000U));
}

std::uint32_t press(countdown::Menu& menu, std::uint32_t base) {
    silent(tick(menu, base, Button::MODE));
    silent(tick(menu, base + 19999U, Button::MODE));
    silent(tick(menu, base + 20000U, Button::MODE));
    return base + 20000U;
}

std::uint32_t shortGesture(countdown::Menu& menu, std::uint32_t base) {
    const auto qualified = press(menu, base);
    silent(tick(menu, qualified + 1000U));
    silent(tick(menu, qualified + 20999U));
    const auto result = tick(menu, qualified + 21000U);
    CHECK(result.selection_changed);
    CHECK_FALSE(result.menu_toggled);
    CHECK(result.request == Service::NONE);
    return qualified + 21000U;
}

std::uint32_t longGesture(countdown::Menu& menu, std::uint32_t base) {
    const auto qualified = press(menu, base);
    silent(tick(menu, qualified + 999999U, Button::MODE));
    const auto result = tick(menu, qualified + 1000000U, Button::MODE);
    CHECK(result.selection_changed);
    CHECK(result.menu_toggled);
    CHECK(result.request == Service::NONE);
    silent(tick(menu, qualified + 1000001U));
    silent(tick(menu, qualified + 1020001U));
    return qualified + 1020001U;
}

std::uint32_t services(countdown::Menu& menu, std::uint32_t base = 0U) {
    arm(menu, base);
    const auto end = longGesture(menu, base + 20001U);
    selected(menu.selection(), Mode::SIDESTEP_R, true);
    return end;
}

void sameSelection(const countdown::MenuSelection& a, const countdown::MenuSelection& b) {
    selected(a, b.mode, b.service_menu, b.service);
}

std::uint32_t randomWord(std::uint32_t& value) {
    value ^= value << 13U;
    value ^= value >> 17U;
    value ^= value << 5U;
    return value;
}
} // namespace

TEST_CASE("B13 D058 defaults reset and selection snapshot expose no implicit action") {
    CHECK(config::MODE_DEFAULT == 1U);
    CHECK(config::MODE_SHORT_MS == 600U);
    CHECK(config::BTN_DEBOUNCE_MS == 20U);
    CHECK(config::BTN_LONG_MS == 1000U);
    countdown::Menu menu;
    const countdown::Menu& view = menu;
    selected(view.selection(), Mode::SIDESTEP_R);
    silent(menu.step({}));
    auto copy = view.selection();
    copy.mode = Mode::WAIT;
    CHECK(copy.mode == Mode::WAIT);
    selected(view.selection(), Mode::SIDESTEP_R);
    menu.reset();
    selected(view.selection(), Mode::SIDESTEP_R);
    silent(tick(menu, 0U, Button::MODE));
    silent(tick(menu, 2000000U, Button::MODE));
}

TEST_CASE("B13 D058 NONE must qualify before exclusive MODE can begin its qualification") {
    for (const auto none_age : {19999U, 20000U, 20001U}) {
        countdown::Menu menu;
        silent(tick(menu, 0U));
        silent(tick(menu, none_age));
        const auto qualified = press(menu, none_age + 1U);
        silent(tick(menu, qualified + 1U));
        const auto result = tick(menu, qualified + 20001U);
        CHECK(result.selection_changed == (none_age >= 20000U));
        selected(result.selection, none_age >= 20000U ? Mode::SIDESTEP_L : Mode::SIDESTEP_R);
        CHECK_FALSE(result.menu_toggled);
    }
}

TEST_CASE("B13 D058 MODE press qualification has a literal strict adjacent boundary") {
    for (const auto press_age : {19999U, 20000U, 20001U}) {
        countdown::Menu menu;
        arm(menu, 0U);
        silent(tick(menu, 20001U, Button::MODE));
        silent(tick(menu, 20001U + press_age, Button::MODE));
        silent(tick(menu, 20002U + press_age));
        const auto result = tick(menu, 40002U + press_age);
        CHECK(result.selection_changed == (press_age >= 20000U));
        selected(result.selection, press_age >= 20000U ? Mode::SIDESTEP_L : Mode::SIDESTEP_R);
    }
}

TEST_CASE("B13 D058 short duration freezes on first NONE and cycles only below 600ms") {
    for (const auto age : {1U, 599000U, 599999U, 600000U, 600001U, 999999U, 1000000U, 1000001U}) {
        CAPTURE(age);
        countdown::Menu menu;
        arm(menu, 0U);
        const auto q = press(menu, 20001U);
        silent(tick(menu, q + age));
        silent(tick(menu, q + age + 19999U));
        const auto result = tick(menu, q + age + 20000U);
        CHECK(result.selection_changed == (age < 600000U));
        CHECK_FALSE(result.menu_toggled);
        CHECK(result.request == Service::NONE);
        selected(result.selection, age < 600000U ? Mode::SIDESTEP_L : Mode::SIDESTEP_R);
        silent(tick(menu, q + age + 20001U));
    }
}

TEST_CASE("B13 D058 delayed release qualification uses frozen short age rather than completion age") {
    countdown::Menu menu;
    arm(menu, 0U);
    const auto q = press(menu, 20001U);
    silent(tick(menu, q + 599999U));
    const auto result = tick(menu, q + 1500000U);
    CHECK(result.selection_changed);
    CHECK_FALSE(result.menu_toggled);
    selected(result.selection, Mode::SIDESTEP_L);
    silent(tick(menu, q + 1500001U));
}

TEST_CASE("B13 D058 continuous long MODE toggles once at 1000ms and release cannot also cycle") {
    countdown::Menu menu;
    arm(menu, 0U);
    const auto q = press(menu, 20001U);
    silent(tick(menu, q + 999000U, Button::MODE));
    silent(tick(menu, q + 999999U, Button::MODE));
    const auto result = tick(menu, q + 1000000U, Button::MODE);
    CHECK(result.menu_toggled);
    CHECK(result.selection_changed);
    selected(result.selection, Mode::SIDESTEP_R, true);
    silent(tick(menu, q + 1000001U, Button::MODE));
    silent(tick(menu, q + 2000000U, Button::MODE));
    silent(tick(menu, q + 2000001U));
    silent(tick(menu, q + 2020001U));
    selected(menu.selection(), Mode::SIDESTEP_R, true);
}

TEST_CASE("B13 D058 delayed MODE qualification anchors the complete long hold at observation") {
    countdown::Menu menu;
    arm(menu, 0U);
    silent(tick(menu, 20001U, Button::MODE));
    silent(tick(menu, 200000U, Button::MODE));
    silent(tick(menu, 1020001U, Button::MODE));
    silent(tick(menu, 1199999U, Button::MODE));
    const auto result = tick(menu, 1200000U, Button::MODE);
    CHECK(result.menu_toggled);
    selected(result.selection, Mode::SIDESTEP_R, true);
}

TEST_CASE("B13 D058 a delayed long observation toggles only while MODE is still observed") {
    for (const auto button : {Button::MODE, Button::NONE}) {
        countdown::Menu menu;
        arm(menu, 0U);
        const auto q = press(menu, 20001U);
        const auto result = tick(menu, q + 1700000U, button);
        CHECK(result.menu_toggled == (button == Button::MODE));
        CHECK(result.selection_changed == (button == Button::MODE));
        silent(tick(menu, q + 1720000U));
    }
}

TEST_CASE("B13 D058 interrupted release cancels rather than resuming short or long MODE") {
    countdown::Menu menu;
    arm(menu, 0U);
    const auto q = press(menu, 20001U);
    silent(tick(menu, q + 1000U));
    silent(tick(menu, q + 20999U, Button::MODE));
    silent(tick(menu, q + 2000000U, Button::MODE));
    selected(menu.selection(), Mode::SIDESTEP_R);
    arm(menu, q + 2000001U);
    shortGesture(menu, q + 2020002U);
    selected(menu.selection(), Mode::SIDESTEP_L);
}

TEST_CASE("B13 D058 NONE interrupting an unqualified press requires fresh NONE arming") {
    countdown::Menu menu;
    arm(menu, 0U);
    silent(tick(menu, 20001U, Button::MODE));
    silent(tick(menu, 40000U));
    silent(tick(menu, 59999U));
    silent(tick(menu, 60000U, Button::MODE));
    silent(tick(menu, 2000000U, Button::MODE));
    selected(menu.selection(), Mode::SIDESTEP_R);
    arm(menu, 2000001U);
    shortGesture(menu, 2020002U);
    selected(menu.selection(), Mode::SIDESTEP_L);
}

TEST_CASE("B13 D058 boot-held MODE START BOTH and invalid input cannot arm a gesture") {
    for (const auto boot : {Button::MODE, Button::START, Button::BOTH, BAD_BUTTON}) {
        countdown::Menu menu;
        silent(tick(menu, 0U, boot));
        silent(tick(menu, 2000000U, Button::MODE));
        silent(tick(menu, 4000000U, Button::MODE));
        selected(menu.selection(), Mode::SIDESTEP_R);
        arm(menu, 4000001U);
        shortGesture(menu, 4020002U);
        selected(menu.selection(), Mode::SIDESTEP_L);
    }
}

TEST_CASE("B13 D058 START BOTH and invalid contamination cancel press hold and release stages") {
    for (const auto contaminant : {Button::START, Button::BOTH, BAD_BUTTON}) {
        for (unsigned stage = 0U; stage < 3U; ++stage) {
            countdown::Menu menu;
            arm(menu, 0U);
            silent(tick(menu, 20001U, Button::MODE));
            if (stage > 0U) silent(tick(menu, 40001U, Button::MODE));
            if (stage > 1U) silent(tick(menu, 40002U));
            silent(tick(menu, 40003U, contaminant));
            silent(tick(menu, 2000000U, Button::MODE));
            silent(tick(menu, 2000001U));
            silent(tick(menu, 2020001U));
            selected(menu.selection(), Mode::SIDESTEP_R);
        }
    }
}

TEST_CASE("B13 D058 every non-IDLE state or fault cancels a pending long gesture") {
    for (unsigned raw_state = 0U; raw_state < 256U; ++raw_state) {
        for (const bool fault : {false, true}) {
            if (raw_state == static_cast<unsigned>(State::IDLE) && !fault) continue;
            countdown::Menu menu;
            arm(menu, 0U);
            const auto q = press(menu, 20001U);
            silent(tick(menu, q + 1000000U, Button::MODE, static_cast<State>(raw_state), fault));
            silent(tick(menu, q + 2000000U, Button::MODE));
            selected(menu.selection(), Mode::SIDESTEP_R);
            arm(menu, q + 2000001U);
            shortGesture(menu, q + 2020002U);
            selected(menu.selection(), Mode::SIDESTEP_L);
        }
    }
}

TEST_CASE("B13 D058 six match modes cycle in literal order with one release pulse") {
    constexpr std::array<Mode, 6> EXPECTED{{Mode::SIDESTEP_L, Mode::DIRECT, Mode::ARC_R,
        Mode::ARC_L, Mode::WAIT, Mode::SIDESTEP_R}};
    countdown::Menu menu;
    arm(menu, 0U);
    std::uint32_t time = 20001U;
    for (const auto expected : EXPECTED) {
        time = shortGesture(menu, time);
        selected(menu.selection(), expected);
        silent(tick(menu, ++time));
        ++time;
    }
}

TEST_CASE("B13 D058 service cycles entry reset and exit preserve the selected match mode") {
    countdown::Menu menu;
    arm(menu, 0U);
    auto time = shortGesture(menu, 20001U);
    time = shortGesture(menu, time + 1U);
    time = longGesture(menu, time + 1U);
    selected(menu.selection(), Mode::DIRECT, true);
    for (const auto item : {Service::QTR_CAL, Service::DRIVE_TEST, Service::LOG_DUMP,
                            Service::SENSOR_VIEW, Service::QTR_CAL}) {
        time = shortGesture(menu, time + 1U);
        selected(menu.selection(), Mode::DIRECT, true, item);
    }
    time = longGesture(menu, time + 1U);
    selected(menu.selection(), Mode::DIRECT, false, Service::QTR_CAL);
    longGesture(menu, time + 1U);
    selected(menu.selection(), Mode::DIRECT, true, Service::SENSOR_VIEW);
}

TEST_CASE("B13 D058 each selected service emits one typed intent and only DRIVE_TEST is unavailable") {
    countdown::Menu menu;
    auto time = services(menu);
    for (const auto item : {Service::SENSOR_VIEW, Service::QTR_CAL, Service::DRIVE_TEST, Service::LOG_DUMP}) {
        const auto request = tick(menu, ++time, Button::NONE, State::IDLE, false, true);
        CHECK(request.request == item);
        CHECK(request.request_unavailable == (item == Service::DRIVE_TEST));
        CHECK_FALSE(request.selection_changed);
        CHECK_FALSE(request.menu_toggled);
        silent(tick(menu, time, Button::NONE, State::IDLE, false, true));
        silent(tick(menu, time + 1U));
        silent(tick(menu, time + 20000U));
        time = shortGesture(menu, time + 20001U);
    }
}

TEST_CASE("B13 D058 service request requires raw NONE and every eligible state predicate") {
    for (unsigned raw_state = 0U; raw_state < 256U; ++raw_state) {
        for (const auto button : {Button::NONE, Button::START, Button::MODE, Button::BOTH, BAD_BUTTON}) {
            countdown::Menu menu;
            const auto time = services(menu) + 1U;
            const auto result = tick(menu, time, button, static_cast<State>(raw_state), false, true);
            const bool eligible = raw_state == static_cast<unsigned>(State::IDLE) && button == Button::NONE;
            CHECK(result.request == (eligible ? Service::SENSOR_VIEW : Service::NONE));
            CHECK_FALSE(result.request_unavailable);
            CHECK_FALSE(result.selection_changed);
            CHECK_FALSE(result.menu_toggled);
            selected(result.selection, Mode::SIDESTEP_R, true);
        }
    }
}

TEST_CASE("B13 D058 no service intent exists in match view or with final fault inhibition") {
    countdown::Menu match;
    arm(match, 0U);
    silent(tick(match, 20001U, Button::NONE, State::IDLE, false, true));
    countdown::Menu menu;
    const auto time = services(menu) + 1U;
    silent(tick(menu, time, Button::NONE, State::IDLE, true, true));
    silent(tick(menu, time + 1U));
    selected(menu.selection(), Mode::SIDESTEP_R, true);
}

TEST_CASE("B13 D058 ineligible observations preserve a nondefault mode and service item") {
    countdown::Menu menu;
    arm(menu, 0U);
    auto time = shortGesture(menu, 20001U);
    time = shortGesture(menu, time + 1U);
    time = longGesture(menu, time + 1U);
    time = shortGesture(menu, time + 1U);
    for (const auto state : {State::BOOT, State::COUNTDOWN, State::OPENER, State::SEARCH,
                             State::TRACK, State::ATTACK, State::DEFEND_TURN, State::EDGE_ESCAPE,
                             State::REFLANK, State::STOPPED, State::DRIVE_TEST, BAD_STATE}) {
        const auto result = tick(menu, ++time, Button::MODE, state);
        silent(result);
        selected(result.selection, Mode::DIRECT, true, Service::QTR_CAL);
    }
    silent(tick(menu, ++time, Button::MODE, State::IDLE, true));
    selected(menu.selection(), Mode::DIRECT, true, Service::QTR_CAL);
}

TEST_CASE("B13 D058 typed service request starts a fresh full NONE arming interval") {
    for (const auto none_age : {19999U, 20000U, 20001U}) {
        countdown::Menu menu;
        const auto time = services(menu) + 1U;
        CHECK(tick(menu, time, Button::NONE, State::IDLE, false, true).request == Service::SENSOR_VIEW);
        silent(tick(menu, time + none_age));
        const auto q = press(menu, time + none_age + 1U);
        silent(tick(menu, q + 1U));
        const auto result = tick(menu, q + 20001U);
        CHECK(result.selection_changed == (none_age >= 20000U));
        selected(result.selection, Mode::SIDESTEP_R, true,
                 none_age >= 20000U ? Service::QTR_CAL : Service::SENSOR_VIEW);
    }
}

TEST_CASE("B13 D058 duplicate timestamp ignores changed raw input state and fault before a deadline") {
    countdown::Menu menu;
    arm(menu, 0U);
    const auto q = press(menu, 20001U);
    silent(tick(menu, q + 999999U, Button::MODE));
    silent(tick(menu, q + 999999U, Button::BOTH, BAD_STATE, true, true));
    const auto result = tick(menu, q + 1000000U, Button::MODE);
    CHECK(result.menu_toggled);
    selected(result.selection, Mode::SIDESTEP_R, true);
    silent(tick(menu, q + 1000000U, Button::NONE, State::IDLE, false, true));
    silent(tick(menu, q + 1000001U, Button::MODE));
}

TEST_CASE("B13 D058 reset clears every gesture stage selection and pending typed request") {
    for (unsigned stage = 0U; stage < 6U; ++stage) {
        countdown::Menu menu;
        arm(menu, 0U);
        if (stage >= 1U) tick(menu, 20001U, Button::MODE);
        if (stage >= 2U) tick(menu, 40001U, Button::MODE);
        if (stage == 3U) tick(menu, 40002U);
        if (stage >= 4U) tick(menu, 1040001U, Button::MODE);
        if (stage == 5U) tick(menu, 1040002U, Button::NONE, State::IDLE, false, true);
        menu.reset();
        selected(menu.selection(), Mode::SIDESTEP_R);
        silent(tick(menu, 0U, Button::MODE));
        silent(tick(menu, 2000000U, Button::MODE));
        arm(menu, 2000001U);
        shortGesture(menu, 2020002U);
        selected(menu.selection(), Mode::SIDESTEP_L);
    }
}

TEST_CASE("B13 D058 long holds spanning multiple micros wraps never replay a toggle") {
    countdown::Menu menu;
    const std::uint32_t base = 0xfffffff0U;
    arm(menu, base);
    const auto q = press(menu, base + 20001U);
    CHECK(tick(menu, q + 1000000U, Button::MODE).menu_toggled);
    std::uint64_t time = static_cast<std::uint64_t>(q) + 1000000U;
    for (unsigned wrap = 0U; wrap < 5U; ++wrap) {
        time += 0xffffffffULL;
        silent(tick(menu, static_cast<std::uint32_t>(time), Button::MODE));
        selected(menu.selection(), Mode::SIDESTEP_R, true);
    }
    silent(tick(menu, static_cast<std::uint32_t>(++time)));
    time += 20000U;
    silent(tick(menu, static_cast<std::uint32_t>(time)));
    shortGesture(menu, static_cast<std::uint32_t>(time + 1U));
    selected(menu.selection(), Mode::SIDESTEP_R, true, Service::QTR_CAL);
}

TEST_CASE("B13 D058 wrapped exact short and long boundaries preserve their distinct outcomes") {
    for (const auto age : {599999U, 600000U, 999999U, 1000000U}) {
        countdown::Menu menu;
        const std::uint32_t base = 0xffffffffU - 500000U;
        arm(menu, base);
        const auto q = press(menu, base + 20001U);
        silent(tick(menu, q + age));
        const auto result = tick(menu, q + age + 20000U);
        CHECK(result.selection_changed == (age < 600000U));
        CHECK_FALSE(result.menu_toggled);
    }
}

TEST_CASE("B13 D058 fixed-seed wrapped gestures agree with independent selection transitions") {
    countdown::Menu menu;
    countdown::MenuSelection expected;
    std::uint32_t random = 0xD0582026U;
    std::uint64_t time = 0xffff0000ULL;
    std::array<unsigned, 4> coverage{};
    for (unsigned episode = 0U; episode < 128U; ++episode) {
        const auto draw = randomWord(random);
        const unsigned kind = draw & 3U;
        ++coverage[kind];
        if (episode % 8U == 0U) time += 0xfffffff0ULL;
        arm(menu, static_cast<std::uint32_t>(time));
        time += 20001U;
        press(menu, static_cast<std::uint32_t>(time));
        time += 20000U;
        if (kind == 2U) {
            time += 1000000U;
            CHECK(tick(menu, static_cast<std::uint32_t>(time), Button::MODE).menu_toggled);
            expected.service_menu = !expected.service_menu;
            if (expected.service_menu) expected.service = Service::SENSOR_VIEW;
        } else {
            const auto age = kind == 0U ? 1U + draw % 599999U : 600000U + draw % 400000U;
            time += age;
            silent(tick(menu, static_cast<std::uint32_t>(time), kind == 3U ? Button::START : Button::NONE));
            if (kind == 3U) silent(tick(menu, static_cast<std::uint32_t>(++time)));
            time += 20000U;
            const auto result = tick(menu, static_cast<std::uint32_t>(time));
            CHECK(result.selection_changed == (kind == 0U));
            if (kind == 0U && expected.service_menu)
                expected.service = static_cast<Service>(static_cast<unsigned>(expected.service) % 4U + 1U);
            if (kind == 0U && !expected.service_menu)
                expected.mode = static_cast<Mode>(static_cast<unsigned>(expected.mode) % 6U + 1U);
        }
        sameSelection(menu.selection(), expected);
        silent(tick(menu, static_cast<std::uint32_t>(time), Button::BOTH, BAD_STATE, true, true));
        sameSelection(menu.selection(), expected);
        time += 1U;
    }
    for (const auto count : coverage) CHECK(count > 0U);
}
