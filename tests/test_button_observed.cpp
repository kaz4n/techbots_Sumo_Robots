// Checks B3/B13 public observed-time services against frozen D087 timing policy.
// Delayed acquisition must never backdate safety holds or promote retained data.
// Host tests use source and decision timelines independently, including wrap.
#include "doctest.h"
#include "core/countdown.h"
#include <initializer_list>

namespace {
using Button = core::ButtonLevel;
countdown::ButtonTiming timing(std::uint32_t source, bool fresh = true,
                              bool restart = false, bool ready = true) {
    return {source, fresh, restart, ready};
}
core::Inputs input(std::uint32_t time, Button level = Button::NONE) {
    core::Inputs value;
    value.t_us = time;
    value.button_level = level;
    return value;
}
countdown::MenuSample menu(std::uint32_t time, Button level = Button::NONE) {
    countdown::MenuSample value;
    value.t_us = time;
    value.button = level;
    value.state_at_entry = core::State::IDLE;
    return value;
}
}

TEST_CASE("B3 D087 Buttons expose source edge but decision qualification timestamps") {
    countdown::Buttons buttons;
    buttons.stepObserved(10000U, 8000U, Button::NONE);
    buttons.stepObserved(30000U, 28000U, Button::NONE);
    buttons.stepObserved(31000U, 29000U, Button::START);
    buttons.stepObserved(51000U, 49000U, Button::START);
    buttons.stepObserved(52000U, 50000U, Button::NONE);
    CHECK_FALSE(buttons.stepObserved(71999U, 69999U, Button::NONE).start_release);
    const auto release = buttons.stepObserved(74000U, 70000U, Button::NONE);
    CHECK(release.start_release);
    CHECK(release.edge_us == 50000U);
    CHECK(release.qualified_us == 74000U);
}

TEST_CASE("B3 D087 Controller no-new observation preserves unfinished qualification") {
    countdown::Controller controller;
    controller.stepObserved(input(10000U), timing(9000U, true, true));
    controller.stepObserved(input(30000U), timing(29000U));
    controller.stepObserved(input(31000U, Button::START), timing(30000U));
    controller.stepObserved(input(50000U, Button::BOTH), timing(0U, false));
    CHECK_FALSE(controller.buttonEvents().mode_press);
    controller.stepObserved(input(51000U, Button::START), timing(50000U));
    controller.stepObserved(input(52000U), timing(51000U));
    controller.stepObserved(input(71999U, Button::MODE), timing(0U, false));
    CHECK_FALSE(controller.buttonEvents().start_release);
    const auto release = controller.stepObserved(input(74000U), timing(71000U));
    CHECK(release.start_release);
    CHECK(release.release_us == 74000U);
    CHECK(controller.buttonEvents().edge_us == 51000U);
    const auto no_new = controller.stepObserved(input(75000U), timing(0U, false));
    CHECK_FALSE(no_new.start_release);
    CHECK_FALSE(controller.buttonEvents().start_release);
    CHECK(controller.stepObserved(input(5174000U), timing(0U, false)).go);
}

TEST_CASE("B3 D087 Controller restart cancels unfinished gesture but retains Gate hold") {
    countdown::Controller controller;
    controller.stepObserved(input(0U), timing(0U, true, true));
    controller.stepObserved(input(20000U), timing(20000U));
    controller.stepObserved(input(21000U, Button::START), timing(21000U));
    controller.stepObserved(input(41000U, Button::START), timing(41000U));
    controller.stepObserved(input(42000U), timing(42000U));
    CHECK(controller.stepObserved(input(62000U), timing(62000U)).start_release);
    controller.stepObserved(input(63000U), timing(63000U, false, true, false));
    CHECK(controller.stepObserved(input(5162000U), timing(0U, false)).go);
}

TEST_CASE("B13 D087 StopHold source before qualification anchor contributes zero") {
    countdown::StopHold stop;
    CHECK_FALSE(stop.stepObserved(1000U, 0U, Button::BOTH));
    CHECK_FALSE(stop.stepObserved(25000U, 20000U, Button::BOTH));
    CHECK_FALSE(stop.stepObserved(26000U, 21000U, Button::BOTH));
    CHECK_FALSE(stop.stepObserved(1025000U, 1024999U, Button::BOTH));
    CHECK(stop.stepObserved(1026000U, 1025000U, Button::BOTH));
    stop.interrupt();
    CHECK(stop.stepObserved(1027000U, 1026000U, Button::NONE));
    stop.reset();
    CHECK_FALSE(stop.stepObserved(1028000U, 1027000U, Button::NONE));
}

TEST_CASE("B13 D087 StopHold interrupt resets pending qualification not latched STOP") {
    countdown::StopHold stop;
    stop.stepObserved(1000U, 0U, Button::BOTH);
    stop.stepObserved(21000U, 20000U, Button::BOTH);
    stop.interrupt();
    CHECK_FALSE(stop.stepObserved(1022000U, 1021000U, Button::BOTH));
    CHECK_FALSE(stop.stepObserved(1042000U, 1041000U, Button::BOTH));
    CHECK_FALSE(stop.stepObserved(2042000U, 2041000U, Button::BOTH));
    CHECK(stop.stepObserved(2043000U, 2042000U, Button::BOTH));
}

TEST_CASE("B13 D087 Menu delayed MODE never toggles early and release deadline wins") {
    for (const bool release_on_deadline : {false, true}) {
        countdown::Menu chooser;
        chooser.stepObserved(menu(10000U), timing(8000U, true, true));
        chooser.stepObserved(menu(30000U), timing(28000U));
        chooser.stepObserved(menu(31000U, Button::MODE), timing(29000U));
        chooser.stepObserved(menu(53000U, Button::MODE), timing(49000U));
        CHECK_FALSE(chooser.stepObserved(menu(54000U, Button::MODE), timing(50000U)).menu_toggled);
        CHECK_FALSE(chooser.stepObserved(menu(1053000U, Button::MODE), timing(0U, false)).menu_toggled);
        const auto result = chooser.stepObserved(
            menu(1055000U, release_on_deadline ? Button::NONE : Button::MODE), timing(1053000U));
        CHECK(result.menu_toggled == !release_on_deadline);
        CHECK(result.selection.service_menu == !release_on_deadline);
        CHECK_FALSE(chooser.stepObserved(menu(1075000U), timing(1073000U)).selection_changed);
    }
}

TEST_CASE("B13 D087 Menu freezes short hold on first fresh release and needs fresh debounce") {
    countdown::Menu chooser;
    chooser.stepObserved(menu(0U), timing(0U, true, true));
    chooser.stepObserved(menu(20000U), timing(20000U));
    chooser.stepObserved(menu(21000U, Button::MODE), timing(21000U));
    chooser.stepObserved(menu(41000U, Button::MODE), timing(41000U));
    chooser.stepObserved(menu(100000U), timing(99000U));
    CHECK_FALSE(chooser.stepObserved(menu(1500000U), timing(0U, false)).selection_changed);
    const auto release = chooser.stepObserved(menu(1501000U), timing(119000U));
    CHECK(release.selection_changed);
    CHECK(release.selection.mode == core::Mode::SIDESTEP_L);
    chooser.stepObserved(menu(1502000U), timing(0U, false, true));
    CHECK(chooser.selection().mode == core::Mode::SIDESTEP_L);
}

TEST_CASE("B13 D087 Menu final fault and non-IDLE disarm even without new button data") {
    for (const bool inhibited : {false, true}) {
        countdown::Menu chooser;
        chooser.stepObserved(menu(0U), timing(0U, true, true));
        chooser.stepObserved(menu(20000U), timing(20000U));
        chooser.stepObserved(menu(21000U, Button::MODE), timing(21000U));
        chooser.stepObserved(menu(41000U, Button::MODE), timing(41000U));
        auto blocked = menu(42000U, Button::MODE);
        blocked.inhibited_fault = inhibited;
        if (!inhibited) blocked.state_at_entry = core::State::COUNTDOWN;
        chooser.stepObserved(blocked, timing(0U, false));
        CHECK_FALSE(chooser.stepObserved(menu(1041000U, Button::MODE), timing(1041000U)).menu_toggled);
        chooser.stepObserved(menu(1042000U), timing(1042000U));
        CHECK_FALSE(chooser.stepObserved(menu(1062000U), timing(1062000U)).selection_changed);
    }
}
