// Checks B3/R1 and B13 Menu composition with the production Lifecycle.
// Routes each genuine button snapshot after countdown and final STOP arbitration.
// Independent locked tests prove typed service requests cannot start match services or GO.
#include "doctest.h"
#include "core/countdown.h"
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Button = core::ButtonLevel;
using Phase = countdown::Phase;
using State = core::State;
using Mode = core::Mode;
using Service = countdown::Service;
constexpr float NAN_BIAS = std::numeric_limits<float>::quiet_NaN();

struct Observation {
    countdown::LifecycleResult life;
    countdown::MenuResult menu;
    countdown::ButtonEvents buttons;
};

// This harness supplies the documented future Robot ordering, not an alternate
// button detector or a claim that full Robot/MotorGate integration exists.
class RoutedMenu {
public:
    Observation step(std::uint32_t time, Button button = Button::NONE,
                     bool stop = false, bool fault = false, float bias = NAN_BIAS) {
        const auto entry = state;
        const auto selection = menu.selection();
        const bool allow_match = entry == State::IDLE && !selection.service_menu && !fault;
        countdown::ServiceSample sample;
        sample.t_us = time;
        sample.raw_gyro_z_dps = NAN_BIAS;
        sample.imu_ok = false;
        sample.line_mask = 15U;
        sample.confirmed_opp_mask = 127U;
        Observation result;
        result.life = lifecycle.step(sample, button, bias, stop, allow_match);
        result.buttons = lifecycle.buttonEvents();
        countdown::MenuSample ui;
        ui.t_us = time;
        ui.button = button;
        ui.state_at_entry = entry;
        ui.inhibited_fault = fault || result.life.gate.phase == Phase::STOPPED;
        ui.qualified_start_release = result.buttons.start_release;
        result.menu = menu.step(ui);
        if (result.life.gate.start_release) running_mode = selection.mode;
        state = result.life.gate.phase == Phase::HOLDING ? State::COUNTDOWN :
            result.life.gate.phase == Phase::READY ? State::SEARCH :
            result.life.gate.phase == Phase::STOPPED ? State::STOPPED : State::IDLE;
        return result;
    }

    countdown::Lifecycle lifecycle;
    countdown::Menu menu;
    State state = State::IDLE;
    Mode running_mode = Mode::SIDESTEP_R;
};

void noMenuAction(const countdown::MenuResult& result) {
    CHECK_FALSE(result.selection_changed);
    CHECK_FALSE(result.menu_toggled);
    CHECK(result.request == Service::NONE);
    CHECK_FALSE(result.request_unavailable);
}

void idleWithoutAttempt(const Observation& result) {
    CHECK(result.life.gate.phase == Phase::IDLE);
    CHECK_FALSE(result.life.gate.start_release);
    CHECK_FALSE(result.life.gate.motion_permitted);
    CHECK_FALSE(result.life.gate.go);
    CHECK_FALSE(result.life.heading_reset_requested);
    CHECK_FALSE(result.life.service_start_failed);
    CHECK_FALSE(result.life.services.active);
    CHECK_FALSE(result.life.services.finished);
    CHECK_FALSE(result.life.services.calibration_finished);
    CHECK_FALSE(result.life.services.calibration_rejected);
    CHECK(result.life.services.calibration_samples == 0U);
    CHECK(result.life.services.bias_dps == 0.0F);
    CHECK_FALSE(result.life.services.line_warning);
    CHECK(result.life.services.opponent_snapshot == 0U);
}

void arm(RoutedMenu& robot, std::uint32_t time) {
    noMenuAction(robot.step(time).menu);
    noMenuAction(robot.step(time + 20000U).menu);
}

std::uint32_t shortMode(RoutedMenu& robot, std::uint32_t time) {
    noMenuAction(robot.step(time, Button::MODE).menu);
    noMenuAction(robot.step(time + 20000U, Button::MODE).menu);
    noMenuAction(robot.step(time + 20001U).menu);
    const auto result = robot.step(time + 40001U);
    CHECK(result.menu.selection_changed);
    CHECK_FALSE(result.menu.menu_toggled);
    CHECK(result.menu.request == Service::NONE);
    return time + 40001U;
}

std::uint32_t longMode(RoutedMenu& robot, std::uint32_t time) {
    robot.step(time, Button::MODE);
    robot.step(time + 20000U, Button::MODE);
    const auto toggle = robot.step(time + 1020000U, Button::MODE);
    CHECK(toggle.menu.menu_toggled);
    CHECK(toggle.menu.selection_changed);
    noMenuAction(robot.step(time + 1020001U).menu);
    noMenuAction(robot.step(time + 1040001U).menu);
    return time + 1040001U;
}

std::uint32_t enterServices(RoutedMenu& robot, std::uint32_t base = 0U) {
    arm(robot, base);
    const auto time = longMode(robot, base + 20001U);
    CHECK(robot.menu.selection().service_menu);
    CHECK(robot.menu.selection().service == Service::SENSOR_VIEW);
    return time;
}

Observation startRelease(RoutedMenu& robot, std::uint32_t time,
                          bool stop = false, bool fault = false, float bias = NAN_BIAS) {
    robot.step(time, Button::START);
    robot.step(time + 20000U, Button::START);
    robot.step(time + 20001U);
    const auto before = robot.step(time + 40000U);
    CHECK_FALSE(before.buttons.start_release);
    CHECK_FALSE(before.life.gate.start_release);
    return robot.step(time + 40001U, Button::NONE, stop, fault, bias);
}
} // namespace

TEST_CASE("B3 R1 B13 each genuine service START stays IDLE without calibration or heading reset") {
    RoutedMenu robot;
    auto time = enterServices(robot);
    for (const auto item : {Service::SENSOR_VIEW, Service::QTR_CAL, Service::DRIVE_TEST, Service::LOG_DUMP}) {
        const auto result = startRelease(robot, time + 1U);
        time += 40002U;
        idleWithoutAttempt(result);
        CHECK(result.buttons.start_release);
        CHECK(result.menu.request == item);
        CHECK(result.menu.request_unavailable == (item == Service::DRIVE_TEST));
        CHECK_FALSE(result.menu.selection_changed);
        CHECK_FALSE(result.menu.menu_toggled);
        CHECK(robot.state == State::IDLE);
        idleWithoutAttempt(robot.step(time));
        noMenuAction(robot.step(time + 1U).menu);
        arm(robot, time + 2U);
        time = shortMode(robot, time + 20003U);
    }
}

TEST_CASE("B3 R1 B13 waiting after service request cannot replay START or create eventual GO") {
    RoutedMenu robot;
    const auto time = enterServices(robot) + 1U;
    const auto result = startRelease(robot, time);
    CHECK(result.menu.request == Service::SENSOR_VIEW);
    for (const auto age : {40001U, 40002U, 5140000U, 5140001U, 10000000U}) {
        const auto later = robot.step(time + age);
        idleWithoutAttempt(later);
        noMenuAction(later.menu);
        CHECK_FALSE(later.buttons.start_release);
    }
}

TEST_CASE("B3 R1 B13 service request needs new NONE qualification before another MODE action") {
    RoutedMenu robot;
    auto time = enterServices(robot) + 1U;
    CHECK(startRelease(robot, time).menu.request == Service::SENSOR_VIEW);
    time += 40001U;
    noMenuAction(robot.step(time + 19999U).menu);
    robot.step(time + 20000U, Button::MODE);
    robot.step(time + 40000U, Button::MODE);
    robot.step(time + 40001U);
    const auto release = robot.step(time + 60001U);
    noMenuAction(release.menu);
    CHECK(release.menu.selection.service == Service::SENSOR_VIEW);
    arm(robot, time + 60002U);
    shortMode(robot, time + 80003U);
    CHECK(robot.menu.selection().service == Service::QTR_CAL);
}

TEST_CASE("B3 R1 B13 service exit cannot replay old START and next match release owns a full hold") {
    RoutedMenu robot;
    auto time = enterServices(robot) + 1U;
    CHECK(startRelease(robot, time).menu.request == Service::SENSOR_VIEW);
    time += 40001U;
    arm(robot, time + 1U);
    time = longMode(robot, time + 20002U);
    CHECK_FALSE(robot.menu.selection().service_menu);
    idleWithoutAttempt(robot.step(time + 1U));
    const auto accepted = startRelease(robot, time + 2U, false, false, 7.0F);
    const auto anchor = time + 40003U;
    CHECK(accepted.life.gate.start_release);
    CHECK(accepted.life.gate.release_us == anchor);
    CHECK(accepted.life.services.active);
    CHECK(accepted.life.services.bias_dps == 7.0F);
    noMenuAction(accepted.menu);
    for (const auto age : {4999999U, 5000000U, 5099999U}) {
        const auto before = robot.step(anchor + age);
        CHECK(before.life.gate.phase == Phase::HOLDING);
        CHECK_FALSE(before.life.gate.motion_permitted);
        CHECK_FALSE(before.life.heading_reset_requested);
    }
    const auto go = robot.step(anchor + 5100000U);
    CHECK(go.life.gate.go);
    CHECK(go.life.gate.motion_permitted);
    CHECK(go.life.heading_reset_requested);
    CHECK_FALSE(robot.step(anchor + 5100001U).life.gate.go);
}

TEST_CASE("B3 R1 B13 selected match mode is captured at accepted release and retained while moving") {
    RoutedMenu robot;
    arm(robot, 0U);
    auto time = shortMode(robot, 20001U);
    time = shortMode(robot, time + 1U);
    time = shortMode(robot, time + 1U);
    CHECK(robot.menu.selection().mode == Mode::ARC_R);
    CHECK(robot.running_mode == Mode::SIDESTEP_R);
    const auto accepted = startRelease(robot, time + 1U, false, false, 7.0F);
    const auto anchor = time + 40002U;
    CHECK(accepted.life.gate.start_release);
    CHECK(robot.running_mode == Mode::ARC_R);
    CHECK(robot.step(anchor + 5100000U).life.gate.go);
    noMenuAction(robot.step(anchor + 5100001U, Button::MODE).menu);
    noMenuAction(robot.step(anchor + 5120001U, Button::MODE).menu);
    noMenuAction(robot.step(anchor + 6120001U, Button::MODE).menu);
    noMenuAction(robot.step(anchor + 6120002U).menu);
    noMenuAction(robot.step(anchor + 6140002U).menu);
    CHECK(robot.running_mode == Mode::ARC_R);
    CHECK(robot.menu.selection().mode == Mode::ARC_R);
    CHECK_FALSE(robot.menu.selection().service_menu);
}

TEST_CASE("B3 R1 B13 countdown MODE cancellation cannot become an IDLE menu gesture") {
    for (const auto cancel_age : {100000U, 5100000U, 5107000U}) {
        RoutedMenu robot;
        robot.step(0U);
        const auto accepted = startRelease(robot, 1U, false, false, 7.0F);
        const auto anchor = accepted.life.gate.release_us;
        const auto time = anchor + cancel_age;
        robot.step(time - 20000U, Button::MODE);
        const auto canceled = robot.step(time, Button::MODE);
        CHECK(canceled.life.gate.phase == Phase::IDLE);
        CHECK_FALSE(canceled.life.gate.go);
        CHECK_FALSE(canceled.life.gate.motion_permitted);
        CHECK(canceled.buttons.mode_press);
        noMenuAction(canceled.menu);
        noMenuAction(robot.step(time + 1000000U, Button::MODE).menu);
        noMenuAction(robot.step(time + 1000001U).menu);
        noMenuAction(robot.step(time + 1020001U).menu);
        CHECK(robot.menu.selection().mode == Mode::SIDESTEP_R);
        CHECK_FALSE(robot.menu.selection().service_menu);
        shortMode(robot, time + 1020002U);
        CHECK(robot.menu.selection().mode == Mode::SIDESTEP_L);
    }
}

TEST_CASE("B3 R1 B13 final STOP on genuine service release suppresses its typed request") {
    RoutedMenu robot;
    const auto time = enterServices(robot) + 1U;
    const auto stopped = startRelease(robot, time, true);
    CHECK(stopped.buttons.start_release);
    CHECK(stopped.life.gate.phase == Phase::STOPPED);
    CHECK_FALSE(stopped.life.gate.start_release);
    CHECK_FALSE(stopped.life.gate.motion_permitted);
    CHECK_FALSE(stopped.life.heading_reset_requested);
    CHECK_FALSE(stopped.life.service_start_failed);
    CHECK_FALSE(stopped.life.services.active);
    noMenuAction(stopped.menu);
    for (const auto age : {40002U, 1040002U, 5140001U}) {
        const auto later = robot.step(time + age);
        CHECK(later.life.gate.phase == Phase::STOPPED);
        CHECK_FALSE(later.life.gate.motion_permitted);
        noMenuAction(later.menu);
    }
}

TEST_CASE("B3 R1 B13 final inhibited fault rejects a service request without queueing it") {
    RoutedMenu robot;
    const auto time = enterServices(robot) + 1U;
    const auto faulted = startRelease(robot, time, false, true);
    CHECK(faulted.buttons.start_release);
    idleWithoutAttempt(faulted);
    noMenuAction(faulted.menu);
    const auto clear = robot.step(time + 40002U);
    idleWithoutAttempt(clear);
    noMenuAction(clear.menu);
    CHECK_FALSE(clear.buttons.start_release);
}

TEST_CASE("B3 B13 logical BOTH STOP remains live in match service countdown and moving contexts") {
    for (unsigned context = 0U; context < 4U; ++context) {
        RoutedMenu robot;
        std::uint32_t time = 1U;
        robot.step(0U);
        if (context == 1U) time = enterServices(robot, 1U) + 1U;
        if (context >= 2U) {
            const auto start = startRelease(robot, time, false, false, 7.0F);
            time = start.life.gate.release_us + 1U;
            if (context == 3U) {
                time = start.life.gate.release_us + 5100000U;
                CHECK(robot.step(time).life.gate.go);
                ++time;
            }
        }
        noMenuAction(robot.step(time, Button::BOTH).menu);
        noMenuAction(robot.step(time + 20000U, Button::BOTH).menu);
        const auto before = robot.step(time + 1019999U, Button::BOTH);
        CHECK(before.life.gate.phase != Phase::STOPPED);
        const auto stopped = robot.step(time + 1020000U, Button::BOTH);
        CHECK(stopped.life.gate.phase == Phase::STOPPED);
        CHECK_FALSE(stopped.life.gate.motion_permitted);
        noMenuAction(stopped.menu);
        CHECK(robot.step(time + 1020001U).life.gate.phase == Phase::STOPPED);
    }
}

TEST_CASE("B3 R1 B13 service request then a second genuine START produces only a fresh service intent") {
    RoutedMenu robot;
    auto time = enterServices(robot) + 1U;
    const auto first = startRelease(robot, time);
    CHECK(first.menu.request == Service::SENSOR_VIEW);
    time += 40002U;
    const auto second = startRelease(robot, time);
    CHECK(second.menu.request == Service::SENSOR_VIEW);
    CHECK(second.buttons.start_release);
    idleWithoutAttempt(second);
    noMenuAction(robot.step(time + 40002U).menu);
}

TEST_CASE("B3 R1 B13 wrapped service routing has one request and no deferred countdown") {
    RoutedMenu robot;
    const std::uint32_t base = 0xffffffffU - 100000U;
    const auto time = enterServices(robot, base) + 1U;
    const auto result = startRelease(robot, time);
    CHECK(result.buttons.edge_us == time + 20001U);
    CHECK(result.buttons.qualified_us == time + 40001U);
    CHECK(result.menu.request == Service::SENSOR_VIEW);
    idleWithoutAttempt(result);
    const auto later = robot.step(time + 5140001U);
    idleWithoutAttempt(later);
    noMenuAction(later.menu);
}
