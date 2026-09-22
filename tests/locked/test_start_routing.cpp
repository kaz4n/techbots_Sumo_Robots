// Checks B3/R1 START routing and button snapshots under D-057.
// Separates service input events from accepted match releases and motor permission.
// Independent locked tests cover suppression, hold preservation, STOP and service lifetime.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include <array>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Button = core::ButtonLevel;
using Phase = countdown::Phase;
constexpr float NAN_BIAS = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_BIAS = std::numeric_limits<float>::infinity();

core::Inputs input(std::uint32_t time, Button button = Button::NONE) {
    core::Inputs result;
    result.t_us = time;
    result.button_level = button;
    return result;
}

countdown::ServiceSample service(std::uint32_t time, float gyro = 0.0F,
        bool imu = true, std::uint8_t line = 0U, std::uint8_t opponent = 0U) {
    countdown::ServiceSample result;
    result.t_us = time;
    result.raw_gyro_z_dps = gyro;
    result.imu_ok = imu;
    result.line_mask = line;
    result.confirmed_opp_mask = opponent;
    return result;
}

countdown::Result tick(countdown::Controller& controller, std::uint32_t time,
        Button button = Button::NONE, bool allowed = true, bool stop = false) {
    return controller.step(input(time, button), stop, allowed);
}

countdown::LifecycleResult tick(countdown::Lifecycle& lifecycle, std::uint32_t time,
        Button button = Button::NONE, bool allowed = true, float bias = 7.0F,
        bool stop = false) {
    return lifecycle.step(service(time), button, bias, stop, allowed);
}

void checkBlocked(const countdown::Result& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK_FALSE(result.motion_permitted);
    CHECK_FALSE(result.go);
}

void checkNoEvents(const countdown::ButtonEvents& events) {
    CHECK_FALSE(events.start_release);
    CHECK_FALSE(events.mode_press);
}

void checkEmptyEvents(const countdown::ButtonEvents& events) {
    checkNoEvents(events);
    CHECK(events.edge_us == 0U);
    CHECK(events.qualified_us == 0U);
}

void checkRelease(const countdown::ButtonEvents& events,
                  std::uint32_t edge, std::uint32_t qualification) {
    CHECK(events.start_release);
    CHECK_FALSE(events.mode_press);
    CHECK(events.edge_us == edge);
    CHECK(events.qualified_us == qualification);
}

void checkCleared(const countdown::ServiceResult& result, float bias = 0.0F) {
    CHECK_FALSE(result.active);
    CHECK_FALSE(result.finished);
    CHECK_FALSE(result.calibration_finished);
    CHECK_FALSE(result.calibration_rejected);
    CHECK_FALSE(result.line_warning);
    CHECK(result.calibration_samples == 0U);
    CHECK(result.opponent_snapshot == 0U);
    CHECK(result.bias_dps == doctest::Approx(bias));
}

void prepareRelease(countdown::Controller& controller, std::uint32_t base = 0U,
                    bool allowed = true) {
    checkBlocked(tick(controller, base, Button::NONE, allowed), Phase::IDLE);
    tick(controller, base + 1000U, Button::START, allowed);
    tick(controller, base + 20999U, Button::START, allowed);
    tick(controller, base + 21000U, Button::START, allowed);
    tick(controller, base + 22000U, Button::NONE, allowed);
    const auto early = tick(controller, base + 41999U, Button::NONE, allowed);
    checkBlocked(early, Phase::IDLE);
    CHECK_FALSE(early.start_release);
    checkNoEvents(controller.buttonEvents());
}

void prepareRelease(countdown::Lifecycle& lifecycle, std::uint32_t base = 0U,
                    bool allowed = true) {
    checkBlocked(tick(lifecycle, base, Button::NONE, allowed, NAN_BIAS).gate, Phase::IDLE);
    tick(lifecycle, base + 1000U, Button::START, allowed, NAN_BIAS);
    tick(lifecycle, base + 21000U, Button::START, allowed, NAN_BIAS);
    tick(lifecycle, base + 22000U, Button::NONE, allowed, NAN_BIAS);
    const auto early = tick(lifecycle, base + 41999U, Button::NONE, allowed, NAN_BIAS);
    checkBlocked(early.gate, Phase::IDLE);
    CHECK_FALSE(early.gate.start_release);
    CHECK_FALSE(early.service_start_failed);
    checkNoEvents(lifecycle.buttonEvents());
}

void checkSameGate(const countdown::Result& left, const countdown::Result& right) {
    CHECK(left.phase == right.phase);
    CHECK(left.motion_permitted == right.motion_permitted);
    CHECK(left.start_release == right.start_release);
    CHECK(left.go == right.go);
    CHECK(left.release_us == right.release_us);
}

void checkSameEvents(const countdown::ButtonEvents& left,
                     const countdown::ButtonEvents& right) {
    CHECK(left.start_release == right.start_release);
    CHECK(left.mode_press == right.mode_press);
    CHECK(left.edge_us == right.edge_us);
    CHECK(left.qualified_us == right.qualified_us);
}

void checkSameServices(const countdown::LifecycleResult& left,
                       const countdown::LifecycleResult& right) {
    checkSameGate(left.gate, right.gate);
    CHECK(left.heading_reset_requested == right.heading_reset_requested);
    CHECK(left.service_start_failed == right.service_start_failed);
    CHECK(left.services.bias_dps == right.services.bias_dps);
    CHECK(left.services.calibration_samples == right.services.calibration_samples);
    CHECK(left.services.calibration_finished == right.services.calibration_finished);
    CHECK(left.services.calibration_rejected == right.services.calibration_rejected);
    CHECK(left.services.line_warning == right.services.line_warning);
    CHECK(left.services.opponent_snapshot == right.services.opponent_snapshot);
    CHECK(left.services.active == right.services.active);
    CHECK(left.services.finished == right.services.finished);
}

void calibrate(countdown::Lifecycle& lifecycle, std::uint32_t anchor) {
    lifecycle.step(service(anchor + 1500000U, 1.0F), Button::NONE, NAN_BIAS, false, false);
    lifecycle.step(service(anchor + 1500001U, 3.0F), Button::NONE, NAN_BIAS, false, false);
    const auto result = lifecycle.step(service(anchor + 4500000U, NAN_BIAS, false),
                                       Button::NONE, NAN_BIAS, false, false);
    checkBlocked(result.gate, Phase::HOLDING);
    CHECK(result.services.calibration_samples == 2U);
    CHECK(result.services.calibration_finished);
    CHECK_FALSE(result.services.calibration_rejected);
    CHECK(result.services.bias_dps == 2.0F);
}
} // namespace

TEST_CASE("B3 R1 D057 routing preserves literal debounce and full hold constants") {
    CHECK(config::BTN_DEBOUNCE_MS == 20U);
    CHECK(config::COUNTDOWN_MS == 5000U);
    CHECK(config::COUNTDOWN_MARGIN_MS == 100U);
    CHECK(config::BTN_LONG_MS == 1000U);
}

TEST_CASE("B3 D057 only eligibility on the qualified release observation routes START") {
    for (const bool before : {false, true}) {
        for (const bool at_release : {false, true}) {
            countdown::Controller controller;
            prepareRelease(controller, 0U, before);
            const auto result = tick(controller, 42000U, Button::NONE, at_release);
            checkBlocked(result, at_release ? Phase::HOLDING : Phase::IDLE);
            CHECK(result.start_release == at_release);
            CHECK(result.release_us == (at_release ? 42000U : 0U));
            checkRelease(controller.buttonEvents(), 22000U, 42000U);
        }
    }
}

TEST_CASE("B3 D057 suppressed release is consumed and requires a genuinely new qualified press") {
    countdown::Controller controller;
    prepareRelease(controller);
    checkBlocked(tick(controller, 42000U, Button::NONE, false), Phase::IDLE);
    for (const auto time : {42000U, 42001U, 5142000U, 10000000U}) {
        const auto result = tick(controller, time);
        checkBlocked(result, Phase::IDLE);
        CHECK_FALSE(result.start_release);
        checkNoEvents(controller.buttonEvents());
    }
    tick(controller, 10001000U, Button::START);
    tick(controller, 10021000U, Button::START);
    tick(controller, 10022000U, Button::NONE);
    const auto accepted = tick(controller, 10042000U);
    CHECK(accepted.start_release);
    CHECK(accepted.release_us == 10042000U);
    checkBlocked(tick(controller, 15141999U), Phase::HOLDING);
    CHECK(tick(controller, 15142000U).go);
}

TEST_CASE("B3 D057 toggling eligibility cannot qualify a short press or interrupted release") {
    countdown::Controller controller;
    tick(controller, 0U, Button::NONE, false);
    tick(controller, 1U, Button::START, false);
    tick(controller, 20000U, Button::NONE, true);
    checkBlocked(tick(controller, 40000U), Phase::IDLE);
    checkNoEvents(controller.buttonEvents());
    tick(controller, 41000U, Button::START, false);
    tick(controller, 61000U, Button::START, true);
    tick(controller, 62000U, Button::NONE, false);
    tick(controller, 81999U, Button::START, true);
    tick(controller, 82000U, Button::NONE, false);
    checkBlocked(tick(controller, 101999U), Phase::IDLE);
    checkNoEvents(controller.buttonEvents());
    const auto result = tick(controller, 102000U, Button::NONE, false);
    checkBlocked(result, Phase::IDLE);
    checkRelease(controller.buttonEvents(), 82000U, 102000U);
}

TEST_CASE("B3 D057 false selector does not turn a boot-held START into a valid press") {
    countdown::Controller controller;
    tick(controller, 0U, Button::START, false);
    tick(controller, 5100000U, Button::START, false);
    tick(controller, 5100001U, Button::NONE, true);
    checkBlocked(tick(controller, 5120001U), Phase::IDLE);
    checkNoEvents(controller.buttonEvents());
    tick(controller, 5120002U, Button::START, false);
    tick(controller, 5140002U, Button::START, false);
    tick(controller, 5140003U, Button::NONE, false);
    const auto result = tick(controller, 5160003U);
    checkBlocked(result, Phase::HOLDING);
    CHECK(result.start_release);
    checkRelease(controller.buttonEvents(), 5140003U, 5160003U);
}

TEST_CASE("B3 D019 D057 delayed qualification exposes both times without backdating GO") {
    for (const bool allowed : {false, true}) {
        countdown::Controller controller;
        prepareRelease(controller, 0U, !allowed);
        const auto result = tick(controller, 60000U, Button::NONE, allowed);
        checkRelease(controller.buttonEvents(), 22000U, 60000U);
        CHECK(result.start_release == allowed);
        checkBlocked(result, allowed ? Phase::HOLDING : Phase::IDLE);
        checkBlocked(tick(controller, 5159999U), allowed ? Phase::HOLDING : Phase::IDLE);
        const auto final = tick(controller, 5160000U);
        CHECK(final.go == allowed);
        CHECK(final.motion_permitted == allowed);
        CHECK_FALSE(final.start_release);
    }
}

TEST_CASE("B3 R1 D057 disabling later starts neither cancels nor shortens an accepted hold") {
    countdown::Controller controller;
    prepareRelease(controller);
    CHECK(tick(controller, 42000U).start_release);
    for (const auto elapsed : {0U, 1U, 4999999U, 5000000U, 5099999U}) {
        const auto result = tick(controller, 42000U + elapsed, Button::NONE, false);
        checkBlocked(result, Phase::HOLDING);
        CHECK(result.release_us == 42000U);
        CHECK_FALSE(result.start_release);
    }
    auto result = tick(controller, 5142000U, Button::NONE, false);
    CHECK(result.phase == Phase::READY);
    CHECK(result.motion_permitted);
    CHECK(result.go);
    CHECK(result.release_us == 42000U);
    result = tick(controller, 5142001U, Button::NONE, false);
    CHECK(result.motion_permitted);
    CHECK_FALSE(result.go);
}

TEST_CASE("B3 D057 READY permission survives selector false and later suppressed input pulses") {
    countdown::Controller controller;
    prepareRelease(controller);
    tick(controller, 42000U);
    CHECK(tick(controller, 5142000U).go);
    tick(controller, 5143000U, Button::START, false);
    tick(controller, 5163000U, Button::START, false);
    tick(controller, 5164000U, Button::NONE, false);
    const auto result = tick(controller, 5184000U, Button::NONE, false);
    CHECK(result.phase == Phase::READY);
    CHECK(result.motion_permitted);
    CHECK_FALSE(result.go);
    CHECK_FALSE(result.start_release);
    CHECK(result.release_us == 42000U);
    checkRelease(controller.buttonEvents(), 5164000U, 5184000U);
}

TEST_CASE("B3 D057 Controller omitted selector equals explicit true across ordinary lifecycle") {
    countdown::Controller implicit;
    countdown::Controller explicit_true;
    constexpr std::array<std::uint32_t, 9> TIMES{{0U, 1000U, 21000U, 22000U,
        42000U, 5141999U, 5142000U, 5142001U, 5142002U}};
    constexpr std::array<Button, 9> BUTTONS{{Button::NONE, Button::START, Button::START,
        Button::NONE, Button::NONE, Button::NONE, Button::NONE, Button::MODE, Button::NONE}};
    for (unsigned i = 0U; i < TIMES.size(); ++i) {
        const auto in = input(TIMES[i], BUTTONS[i]);
        const bool stop = i + 1U == TIMES.size();
        checkSameGate(implicit.step(in, stop), explicit_true.step(in, stop, true));
        checkSameEvents(implicit.buttonEvents(), explicit_true.buttonEvents());
    }
}

TEST_CASE("B3 D057 MODE cancellation and timestamps are not filtered at the exact GO boundary") {
    for (const auto button : {Button::MODE, Button::BOTH}) {
        countdown::Controller controller;
        prepareRelease(controller);
        tick(controller, 42000U);
        tick(controller, 5122000U, button, false);
        checkBlocked(tick(controller, 5141999U, button, false), Phase::HOLDING);
        const auto result = tick(controller, 5142000U, button, false);
        checkBlocked(result, Phase::IDLE);
        CHECK_FALSE(result.start_release);
        const auto event = controller.buttonEvents();
        CHECK(event.mode_press);
        CHECK_FALSE(event.start_release);
        CHECK(event.edge_us == 5122000U);
        CHECK(event.qualified_us == 5142000U);
    }
}

TEST_CASE("B3 B13 D057 logical BOTH keeps its complete debounce and STOP hold with routing disabled") {
    countdown::Controller controller;
    tick(controller, 0U, Button::NONE, false);
    tick(controller, 1U, Button::BOTH, false);
    checkBlocked(tick(controller, 20000U, Button::BOTH, false), Phase::IDLE);
    checkNoEvents(controller.buttonEvents());
    checkBlocked(tick(controller, 20001U, Button::BOTH, false), Phase::IDLE);
    CHECK(controller.buttonEvents().mode_press);
    checkBlocked(tick(controller, 1020000U, Button::BOTH, false), Phase::IDLE);
    checkBlocked(tick(controller, 1020001U, Button::BOTH, false), Phase::STOPPED);
    checkBlocked(tick(controller, 1020002U, Button::NONE, true), Phase::STOPPED);
}

TEST_CASE("B3 D057 external STOP dominates accepted routing but preserves raw qualified event") {
    for (const bool allowed : {false, true}) {
        countdown::Controller controller;
        prepareRelease(controller);
        const auto result = tick(controller, 42000U, Button::NONE, allowed, true);
        checkBlocked(result, Phase::STOPPED);
        CHECK_FALSE(result.start_release);
        checkRelease(controller.buttonEvents(), 22000U, 42000U);
        checkBlocked(tick(controller, 5142000U, Button::NONE, true), Phase::STOPPED);
        checkNoEvents(controller.buttonEvents());
    }
}

TEST_CASE("B3 D057 Controller snapshot is pure copied state and clears on the next step or reset") {
    countdown::Controller controller;
    const countdown::Controller& view = controller;
    checkEmptyEvents(view.buttonEvents());
    prepareRelease(controller);
    tick(controller, 42000U, Button::NONE, false);
    for (unsigned read = 0U; read < 5U; ++read) {
        checkRelease(view.buttonEvents(), 22000U, 42000U);
    }
    auto copy = view.buttonEvents();
    copy.start_release = false;
    copy.edge_us = 999U;
    CHECK_FALSE(copy.start_release);
    CHECK(copy.edge_us == 999U);
    checkRelease(view.buttonEvents(), 22000U, 42000U);
    checkBlocked(tick(controller, 42000U, Button::NONE, true), Phase::IDLE);
    checkNoEvents(view.buttonEvents());
    controller.reset();
    checkEmptyEvents(view.buttonEvents());
    tick(controller, 43000U, Button::START, true);
    tick(controller, 63000U, Button::NONE, true);
    checkBlocked(tick(controller, 83000U), Phase::IDLE);
    checkNoEvents(view.buttonEvents());
}

TEST_CASE("B3 D057 Lifecycle omitted selector equals explicit true including calibration and STOP") {
    countdown::Lifecycle implicit;
    countdown::Lifecycle explicit_true;
    constexpr std::array<std::uint32_t, 10> TIMES{{0U, 1000U, 21000U, 22000U, 42000U,
        1542000U, 1542001U, 4542000U, 5142000U, 5142001U}};
    constexpr std::array<Button, 10> BUTTONS{{Button::NONE, Button::START, Button::START,
        Button::NONE, Button::NONE, Button::NONE, Button::NONE, Button::NONE,
        Button::NONE, Button::NONE}};
    for (unsigned i = 0U; i < TIMES.size(); ++i) {
        const auto raw = service(TIMES[i], i == 5U ? 1.0F : 3.0F, true, 1U, 2U);
        const bool stop = i + 1U == TIMES.size();
        checkSameServices(implicit.step(raw, BUTTONS[i], 7.0F, stop),
                          explicit_true.step(raw, BUTTONS[i], 7.0F, stop, true));
        checkSameEvents(implicit.buttonEvents(), explicit_true.buttonEvents());
    }
}

TEST_CASE("B3 D024 D057 suppressed Lifecycle release ignores invalid bias and cannot start services") {
    for (const auto bias : {NAN_BIAS, INF_BIAS, -INF_BIAS}) {
        countdown::Lifecycle lifecycle;
        prepareRelease(lifecycle, 0U, false);
        auto result = lifecycle.step(service(42000U, NAN_BIAS, false, 15U, 127U),
                                      Button::NONE, bias, false, false);
        checkBlocked(result.gate, Phase::IDLE);
        CHECK_FALSE(result.gate.start_release);
        CHECK_FALSE(result.service_start_failed);
        CHECK_FALSE(result.heading_reset_requested);
        checkCleared(result.services);
        checkRelease(lifecycle.buttonEvents(), 22000U, 42000U);
        result = tick(lifecycle, 5142000U, Button::NONE, true, bias);
        checkBlocked(result.gate, Phase::IDLE);
        CHECK_FALSE(result.service_start_failed);
        CHECK_FALSE(result.heading_reset_requested);
        checkCleared(result.services);
    }
}

TEST_CASE("B3 D057 invalid prior bias is consumed on a real new attempt after suppression") {
    countdown::Lifecycle lifecycle;
    prepareRelease(lifecycle, 0U, false);
    tick(lifecycle, 42000U, Button::NONE, false, NAN_BIAS);
    prepareRelease(lifecycle, 50000U, false);
    auto result = tick(lifecycle, 92000U, Button::NONE, true, NAN_BIAS);
    checkBlocked(result.gate, Phase::HOLDING);
    CHECK(result.gate.start_release);
    CHECK(result.gate.release_us == 92000U);
    CHECK(result.service_start_failed);
    CHECK(result.services.calibration_rejected);
    CHECK_FALSE(result.services.active);
    result = tick(lifecycle, 5192000U, Button::NONE, false, 7.0F);
    CHECK(result.gate.go);
    CHECK(result.gate.motion_permitted);
    CHECK(result.heading_reset_requested);
    CHECK(result.service_start_failed);
}

TEST_CASE("B3 D024 D057 existing service windows and GO continue with future starts disabled") {
    countdown::Lifecycle lifecycle;
    prepareRelease(lifecycle);
    auto result = tick(lifecycle, 42000U, Button::NONE, true, 7.0F);
    CHECK(result.gate.start_release);
    calibrate(lifecycle, 42000U);
    result = lifecycle.step(service(4842000U, 0.0F, true, 1U, 6U),
                            Button::NONE, NAN_BIAS, false, false);
    CHECK(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 6U);
    result = lifecycle.step(service(5141999U, 0.0F, true, 0U, 6U),
                            Button::NONE, NAN_BIAS, false, false);
    checkBlocked(result.gate, Phase::HOLDING);
    CHECK_FALSE(result.heading_reset_requested);
    result = tick(lifecycle, 5142000U, Button::NONE, false, NAN_BIAS);
    CHECK(result.gate.go);
    CHECK(result.gate.motion_permitted);
    CHECK(result.heading_reset_requested);
    CHECK(result.services.finished);
    CHECK_FALSE(result.services.active);
    CHECK_FALSE(result.service_start_failed);
    CHECK(result.services.bias_dps == 2.0F);
    CHECK(result.services.calibration_samples == 2U);
    CHECK(result.services.opponent_snapshot == 6U);
    result = tick(lifecycle, 5142001U, Button::NONE, false, NAN_BIAS, true);
    checkBlocked(result.gate, Phase::STOPPED);
    CHECK_FALSE(result.heading_reset_requested);
    CHECK(result.services.finished);
    CHECK(result.services.bias_dps == 2.0F);
    CHECK(result.services.opponent_snapshot == 6U);
}

TEST_CASE("B3 D057 suppressed second release exactly at GO cannot restart the original attempt") {
    countdown::Lifecycle lifecycle;
    prepareRelease(lifecycle);
    tick(lifecycle, 42000U, Button::NONE, true, 7.0F);
    calibrate(lifecycle, 42000U);
    tick(lifecycle, 5101000U, Button::START, false, NAN_BIAS);
    tick(lifecycle, 5121000U, Button::START, false, NAN_BIAS);
    tick(lifecycle, 5122000U, Button::NONE, false, NAN_BIAS);
    auto result = tick(lifecycle, 5142000U, Button::NONE, false, NAN_BIAS);
    CHECK(result.gate.phase == Phase::READY);
    CHECK(result.gate.go);
    CHECK(result.gate.motion_permitted);
    CHECK(result.heading_reset_requested);
    CHECK_FALSE(result.gate.start_release);
    CHECK(result.gate.release_us == 42000U);
    checkRelease(lifecycle.buttonEvents(), 5122000U, 5142000U);
    CHECK_FALSE(result.service_start_failed);
    CHECK(result.services.finished);
    CHECK_FALSE(result.services.active);
    CHECK(result.services.bias_dps == 2.0F);
    CHECK(result.services.calibration_samples == 2U);
    CHECK_FALSE(result.services.calibration_rejected);
    result = tick(lifecycle, 5142001U, Button::NONE, true, NAN_BIAS);
    CHECK(result.gate.motion_permitted);
    CHECK_FALSE(result.gate.go);
    CHECK_FALSE(result.heading_reset_requested);
    CHECK_FALSE(result.gate.start_release);
    checkNoEvents(lifecycle.buttonEvents());
}

TEST_CASE("B3 D024 D057 MODE still cancels before calibration completion sample is consumed") {
    countdown::Lifecycle lifecycle;
    prepareRelease(lifecycle);
    tick(lifecycle, 42000U, Button::NONE, true, 7.0F);
    lifecycle.step(service(1542000U, 1.0F), Button::NONE, NAN_BIAS, false, false);
    lifecycle.step(service(1542001U, 3.0F), Button::NONE, NAN_BIAS, false, false);
    tick(lifecycle, 4522000U, Button::MODE, false, NAN_BIAS);
    const auto result = lifecycle.step(service(4542000U, NAN_BIAS, false, 15U, 127U),
                                       Button::MODE, NAN_BIAS, false, false);
    checkBlocked(result.gate, Phase::IDLE);
    CHECK_FALSE(result.service_start_failed);
    CHECK_FALSE(result.heading_reset_requested);
    checkCleared(result.services, 7.0F);
    CHECK(lifecycle.buttonEvents().mode_press);
}

TEST_CASE("B3 D057 suppression after a canceled attempt retains prior bias without new diagnostics") {
    countdown::Lifecycle lifecycle;
    prepareRelease(lifecycle);
    tick(lifecycle, 42000U, Button::NONE, true, 7.0F);
    tick(lifecycle, 43000U, Button::MODE, false);
    checkCleared(tick(lifecycle, 63000U, Button::MODE, false).services, 7.0F);
    tick(lifecycle, 64000U, Button::NONE, false);
    tick(lifecycle, 84000U, Button::NONE, false);
    prepareRelease(lifecycle, 85000U, false);
    const auto result = tick(lifecycle, 127000U, Button::NONE, false, NAN_BIAS);
    checkBlocked(result.gate, Phase::IDLE);
    CHECK_FALSE(result.service_start_failed);
    CHECK_FALSE(result.heading_reset_requested);
    checkCleared(result.services, 7.0F);
    checkRelease(lifecycle.buttonEvents(), 107000U, 127000U);
}

TEST_CASE("B3 D057 Lifecycle STOP on release exposes input but starts no calibration or heading reset") {
    for (const bool allowed : {false, true}) {
        countdown::Lifecycle lifecycle;
        prepareRelease(lifecycle);
        const auto result = tick(lifecycle, 42000U, Button::NONE, allowed, NAN_BIAS, true);
        checkBlocked(result.gate, Phase::STOPPED);
        CHECK_FALSE(result.gate.start_release);
        CHECK_FALSE(result.service_start_failed);
        CHECK_FALSE(result.heading_reset_requested);
        checkCleared(result.services);
        checkRelease(lifecycle.buttonEvents(), 22000U, 42000U);
    }
}

TEST_CASE("B3 D057 Lifecycle external STOP still cancels at GO while routing selector is false") {
    countdown::Lifecycle lifecycle;
    prepareRelease(lifecycle);
    tick(lifecycle, 42000U);
    calibrate(lifecycle, 42000U);
    const auto result = tick(lifecycle, 5142000U, Button::NONE, false, NAN_BIAS, true);
    checkBlocked(result.gate, Phase::STOPPED);
    CHECK_FALSE(result.gate.start_release);
    CHECK_FALSE(result.heading_reset_requested);
    checkCleared(result.services, 2.0F);
}

TEST_CASE("B3 D057 Lifecycle snapshots are const copied state with no duplicate observations") {
    countdown::Lifecycle lifecycle;
    const countdown::Lifecycle& view = lifecycle;
    checkEmptyEvents(view.buttonEvents());
    prepareRelease(lifecycle, 0U, false);
    tick(lifecycle, 42000U, Button::NONE, false, NAN_BIAS);
    for (unsigned read = 0U; read < 5U; ++read) {
        checkRelease(view.buttonEvents(), 22000U, 42000U);
    }
    auto copy = view.buttonEvents();
    copy.qualified_us = 0U;
    CHECK(copy.qualified_us == 0U);
    checkRelease(view.buttonEvents(), 22000U, 42000U);
    const auto result = tick(lifecycle, 42000U, Button::NONE, true, NAN_BIAS);
    checkBlocked(result.gate, Phase::IDLE);
    checkCleared(result.services);
    checkNoEvents(view.buttonEvents());
    lifecycle.reset();
    checkEmptyEvents(view.buttonEvents());
    tick(lifecycle, 43000U, Button::START, true, NAN_BIAS);
    tick(lifecycle, 63000U, Button::NONE, true, NAN_BIAS);
    checkBlocked(tick(lifecycle, 83000U).gate, Phase::IDLE);
    checkNoEvents(view.buttonEvents());
}

TEST_CASE("B3 D019 D057 wrapped delayed releases preserve raw event and independent routing") {
    const std::uint32_t base = 0xffffffffU - 30000U;
    for (const bool allowed : {false, true}) {
        countdown::Controller controller;
        countdown::Lifecycle lifecycle;
        prepareRelease(controller, base, !allowed);
        prepareRelease(lifecycle, base, !allowed);
        const auto qualified = static_cast<std::uint32_t>(base + 80000U);
        const auto gate = tick(controller, qualified, Button::NONE, allowed);
        const auto life = tick(lifecycle, qualified, Button::NONE, allowed, 7.0F);
        checkSameGate(gate, life.gate);
        checkRelease(controller.buttonEvents(), base + 22000U, qualified);
        checkSameEvents(controller.buttonEvents(), lifecycle.buttonEvents());
        CHECK(gate.start_release == allowed);
        CHECK(life.services.active == allowed);
        const auto before = tick(controller, qualified + 5099999U, Button::NONE, false);
        checkBlocked(before, allowed ? Phase::HOLDING : Phase::IDLE);
        const auto end = tick(lifecycle, qualified + 5100000U, Button::NONE, false, NAN_BIAS);
        CHECK(end.gate.motion_permitted == allowed);
        CHECK(end.gate.go == allowed);
        CHECK(end.heading_reset_requested == allowed);
        CHECK_FALSE(end.gate.start_release);
    }
}
