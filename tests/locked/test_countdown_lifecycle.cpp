// Checks B3 production countdown Lifecycle ordering and diagnostic lifetime.
// Preserves Controller gate authority while exercising D-019/D-024/D-035 services.
// Independent locked host tests cover hold boundaries, cancellation, STOP and wrapped streams.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Button = core::ButtonLevel;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();

countdown::LifecycleResult tick(countdown::Lifecycle& lifecycle, std::uint32_t time,
        Button button = Button::NONE, float bias = 7.0F, float gyro = 0.0F,
        bool imu = true, std::uint8_t lines = 0U, std::uint8_t opponent = 0U,
        bool stop = false) {
    countdown::ServiceSample sample;
    sample.t_us = time;
    sample.raw_gyro_z_dps = gyro;
    sample.imu_ok = imu;
    sample.line_mask = lines;
    sample.confirmed_opp_mask = opponent;
    return lifecycle.step(sample, button, bias, stop);
}

void checkHolding(const countdown::LifecycleResult& result) {
    CHECK(result.gate.phase == countdown::Phase::HOLDING);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.gate.go);
    CHECK_FALSE(result.heading_reset_requested);
}

void checkCleared(const countdown::ServiceResult& result, float bias) {
    CHECK_FALSE(result.active);
    CHECK_FALSE(result.finished);
    CHECK_FALSE(result.calibration_finished);
    CHECK_FALSE(result.calibration_rejected);
    CHECK_FALSE(result.line_warning);
    CHECK(result.opponent_snapshot == 0U);
    CHECK(result.calibration_samples == 0U);
    CHECK(result.bias_dps == doctest::Approx(bias));
}

std::uint32_t release(countdown::Lifecycle& lifecycle, std::uint32_t base = 0U,
                       float previous_bias = 7.0F) {
    tick(lifecycle, base, Button::NONE, NAN_VALUE);
    tick(lifecycle, base + 1000U, Button::START, NAN_VALUE);
    tick(lifecycle, base + 21000U, Button::START, NAN_VALUE);
    tick(lifecycle, base + 22000U, Button::NONE, NAN_VALUE);
    const auto early = tick(lifecycle, base + 41999U, Button::NONE, NAN_VALUE);
    CHECK_FALSE(early.gate.start_release);
    CHECK_FALSE(early.gate.motion_permitted);
    const auto accepted = tick(lifecycle, base + 42000U, Button::NONE, previous_bias);
    CHECK(accepted.gate.start_release);
    CHECK(accepted.gate.release_us == base + 42000U);
    checkHolding(accepted);
    return base + 42000U;
}

void finishCalibration(countdown::Lifecycle& lifecycle, std::uint32_t anchor) {
    checkHolding(tick(lifecycle, anchor + 1500000U, Button::NONE, NAN_VALUE, 1.0F));
    checkHolding(tick(lifecycle, anchor + 1500001U, Button::NONE, NAN_VALUE, 3.0F));
    const auto result = tick(lifecycle, anchor + 4500000U, Button::NONE, NAN_VALUE, NAN_VALUE, false);
    checkHolding(result);
    CHECK(result.services.calibration_finished);
    CHECK_FALSE(result.services.calibration_rejected);
    CHECK(result.services.calibration_samples == 2U);
    CHECK(result.services.bias_dps == doctest::Approx(2.0F));
}

countdown::LifecycleResult complete(countdown::Lifecycle& lifecycle, std::uint32_t anchor) {
    finishCalibration(lifecycle, anchor);
    tick(lifecycle, anchor + 4800000U, Button::NONE, NAN_VALUE, 0.0F, true, 1U, 2U);
    const auto result = tick(lifecycle, anchor + 5100000U, Button::NONE, NAN_VALUE);
    CHECK(result.gate.go);
    CHECK(result.gate.motion_permitted);
    CHECK(result.heading_reset_requested);
    CHECK(result.services.finished);
    CHECK(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 2U);
    return result;
}

void checkCompletedEvidence(const countdown::LifecycleResult& result) {
    CHECK(result.services.finished);
    CHECK_FALSE(result.services.active);
    CHECK(result.services.calibration_finished);
    CHECK_FALSE(result.services.calibration_rejected);
    CHECK(result.services.calibration_samples == 2U);
    CHECK(result.services.bias_dps == doctest::Approx(2.0F));
    CHECK(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 2U);
}
} // namespace

TEST_CASE("B3 Lifecycle accepted release starts the complete literal hold and services together") {
    CHECK(config::COUNTDOWN_MS == 5000U);
    CHECK(config::COUNTDOWN_MARGIN_MS == 100U);
    CHECK(config::BTN_DEBOUNCE_MS == 20U);
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    auto result = tick(lifecycle, anchor, Button::NONE, NAN_VALUE);
    checkHolding(result);
    CHECK_FALSE(result.gate.start_release);
    CHECK(result.services.active);
    CHECK(result.services.bias_dps == doctest::Approx(7.0F));
    CHECK_FALSE(result.service_start_failed);
    result = tick(lifecycle, anchor + 5099999U);
    checkHolding(result);
    CHECK(result.services.active);
    result = tick(lifecycle, anchor + 5100000U);
    CHECK(result.gate.phase == countdown::Phase::READY);
    CHECK(result.gate.go);
    CHECK(result.gate.motion_permitted);
    CHECK(result.heading_reset_requested);
    CHECK(result.services.finished);
    CHECK_FALSE(result.services.active);
    for (const auto elapsed : {5100000U, 5100001U}) {
        result = tick(lifecycle, anchor + elapsed);
        CHECK(result.gate.motion_permitted);
        CHECK_FALSE(result.gate.go);
        CHECK_FALSE(result.heading_reset_requested);
    }
}

TEST_CASE("B3 D-019 delayed release qualification never backdates hold or service windows") {
    countdown::Lifecycle lifecycle;
    tick(lifecycle, 0U);
    tick(lifecycle, 1000U, Button::START);
    tick(lifecycle, 21000U, Button::START);
    tick(lifecycle, 22000U);
    const auto accepted = tick(lifecycle, 120000U);
    CHECK(accepted.gate.start_release);
    CHECK(accepted.gate.release_us == 120000U);
    CHECK(accepted.services.active);
    checkHolding(tick(lifecycle, 5122000U));
    const auto result = tick(lifecycle, 5220000U);
    CHECK(result.gate.go);
    CHECK(result.heading_reset_requested);
    CHECK(result.services.finished);
}

TEST_CASE("B3 D-024 raw calibration boundaries and duplicate timestamps preserve the accepted mean") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle, 0U, 7.0F);
    auto result = tick(lifecycle, anchor + 1499999U, Button::NONE, 99.0F, NAN_VALUE, false);
    CHECK(result.services.calibration_samples == 0U);
    CHECK_FALSE(result.services.calibration_rejected);
    result = tick(lifecycle, anchor + 1500000U, Button::NONE, NAN_VALUE, 1.0F);
    CHECK(result.services.calibration_samples == 1U);
    result = tick(lifecycle, anchor + 1500000U, Button::NONE, NAN_VALUE, NAN_VALUE, false);
    CHECK(result.services.calibration_samples == 1U);
    result = tick(lifecycle, anchor + 4499999U, Button::NONE, -999.0F, 3.0F);
    CHECK(result.services.calibration_samples == 2U);
    CHECK_FALSE(result.services.calibration_finished);
    result = tick(lifecycle, anchor + 4500000U, Button::NONE, NAN_VALUE, NAN_VALUE, false);
    checkHolding(result);
    CHECK(result.services.calibration_finished);
    CHECK_FALSE(result.services.calibration_rejected);
    CHECK(result.services.bias_dps == doctest::Approx(2.0F));
    result = tick(lifecycle, anchor + 4500001U, Button::NONE, 777.0F, 777.0F);
    CHECK(result.services.bias_dps == doctest::Approx(2.0F));
    CHECK(result.services.calibration_samples == 2U);
}

TEST_CASE("B3 D-024 rejected calibration retains supplied prior bias without changing Gate authority") {
    for (unsigned failure = 0U; failure < 3U; ++failure) {
        countdown::Lifecycle lifecycle;
        const auto anchor = release(lifecycle, 0U, 7.0F);
        tick(lifecycle, anchor + 1500000U, Button::NONE, 99.0F, 1.0F);
        if (failure == 1U) tick(lifecycle, anchor + 1500001U, Button::NONE, 99.0F, NAN_VALUE, false);
        if (failure == 2U) tick(lifecycle, anchor + 1500001U, Button::NONE, 99.0F, 3.001F);
        auto result = tick(lifecycle, anchor + 4500000U);
        checkHolding(result);
        CHECK(result.services.calibration_finished);
        CHECK(result.services.calibration_rejected);
        CHECK(result.services.bias_dps == doctest::Approx(7.0F));
        result = tick(lifecycle, anchor + 5100000U);
        CHECK(result.gate.go);
        CHECK(result.gate.motion_permitted);
        CHECK(result.heading_reset_requested);
        CHECK(result.services.calibration_rejected);
    }
}

TEST_CASE("B3 D-024 final warning and latest snapshot windows include their starts and exclude GO") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    auto result = tick(lifecycle, anchor + 4099999U, Button::NONE, 7.0F, 0.0F, true, 15U, 127U);
    CHECK_FALSE(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 0U);
    result = tick(lifecycle, anchor + 4100000U, Button::NONE, 7.0F, 0.0F, true, 1U, 127U);
    CHECK(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 0U);
    result = tick(lifecycle, anchor + 4799999U, Button::NONE, 7.0F, 0.0F, true, 0U, 127U);
    CHECK(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 0U);
    result = tick(lifecycle, anchor + 4800000U, Button::NONE, 7.0F, 0.0F, true, 0U, 130U);
    CHECK(result.services.opponent_snapshot == 2U);
    result = tick(lifecycle, anchor + 4800001U, Button::NONE, 7.0F, 0.0F, true, 0U, 132U);
    CHECK(result.services.opponent_snapshot == 4U);
    result = tick(lifecycle, anchor + 5099999U);
    CHECK(result.services.opponent_snapshot == 0U);
    result = tick(lifecycle, anchor + 5100000U, Button::NONE, 7.0F, 0.0F, true, 15U, 127U);
    CHECK(result.gate.go);
    CHECK(result.services.opponent_snapshot == 0U);
}

TEST_CASE("B3 a warning or snapshot first presented at GO cannot enter completed service evidence") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    const auto result = tick(lifecycle, anchor + 5100000U, Button::NONE, 7.0F, 0.0F, true, 15U, 127U);
    CHECK(result.gate.go);
    CHECK(result.services.finished);
    CHECK_FALSE(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 0U);
}

TEST_CASE("B3 Lifecycle MODE cancellation occurs before calibration completion can replace bias") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    tick(lifecycle, anchor + 1500000U, Button::NONE, 7.0F, 1.0F);
    tick(lifecycle, anchor + 1500001U, Button::NONE, 7.0F, 3.0F);
    checkHolding(tick(lifecycle, anchor + 4480000U, Button::MODE, 7.0F, 2.0F));
    const auto result = tick(lifecycle, anchor + 4500000U, Button::MODE, NAN_VALUE, 2.0F);
    CHECK(result.gate.phase == countdown::Phase::IDLE);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.gate.go);
    CHECK_FALSE(result.heading_reset_requested);
    checkCleared(result.services, 7.0F);
    CHECK_FALSE(result.service_start_failed);
}

TEST_CASE("B3 qualified MODE at GO cancels before the final sample and retains accepted bias only") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    finishCalibration(lifecycle, anchor);
    tick(lifecycle, anchor + 5080000U, Button::MODE, 7.0F, 0.0F, true, 1U, 2U);
    const auto result = tick(lifecycle, anchor + 5100000U, Button::MODE, NAN_VALUE, 0.0F, true, 15U, 4U);
    CHECK(result.gate.phase == countdown::Phase::IDLE);
    CHECK_FALSE(result.gate.go);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.heading_reset_requested);
    checkCleared(result.services, 2.0F);
}

TEST_CASE("B3 D-035 immediate STOP before GO cancels pending diagnostics before their sample") {
    for (const bool at_go : {false, true}) {
        countdown::Lifecycle lifecycle;
        const auto anchor = release(lifecycle);
        tick(lifecycle, anchor + 1500000U, Button::NONE, 7.0F, 1.0F);
        tick(lifecycle, anchor + 1500001U, Button::NONE, 7.0F, 3.0F);
        if (at_go) tick(lifecycle, anchor + 4500000U);
        const auto time = anchor + (at_go ? 5100000U : 4500000U);
        const auto result = tick(lifecycle, time, Button::NONE, NAN_VALUE, 99.0F, true, 15U, 127U, true);
        CHECK(result.gate.phase == countdown::Phase::STOPPED);
        CHECK_FALSE(result.gate.motion_permitted);
        CHECK_FALSE(result.gate.go);
        CHECK_FALSE(result.heading_reset_requested);
        checkCleared(result.services, at_go ? 2.0F : 7.0F);
    }
}

TEST_CASE("B3 Lifecycle invalid bias start remains explicit without adding a new gate veto") {
    for (const float invalid : {NAN_VALUE, std::numeric_limits<float>::infinity(),
                                -std::numeric_limits<float>::infinity()}) {
        countdown::Lifecycle lifecycle;
        const auto anchor = release(lifecycle, 0U, invalid);
        auto result = tick(lifecycle, anchor + 1U, Button::NONE, 7.0F);
        checkHolding(result);
        CHECK(result.service_start_failed);
        CHECK(result.services.calibration_rejected);
        CHECK_FALSE(result.services.active);
        result = tick(lifecycle, anchor + 5100000U, Button::NONE, 7.0F);
        CHECK(result.gate.go);
        CHECK(result.heading_reset_requested);
        CHECK(result.gate.motion_permitted);
        CHECK(result.service_start_failed);
        CHECK(result.services.calibration_rejected);
        result = tick(lifecycle, anchor + 5100001U, Button::NONE, 7.0F, 0.0F, true, 0U, 0U, true);
        CHECK(result.gate.phase == countdown::Phase::STOPPED);
        CHECK_FALSE(result.gate.motion_permitted);
        CHECK(result.service_start_failed);
        CHECK(result.services.calibration_rejected);
    }
}

TEST_CASE("B3 canceling an invalid service start clears its failure diagnostic") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle, 0U, NAN_VALUE);
    CHECK(tick(lifecycle, anchor + 1U, Button::MODE).service_start_failed);
    const auto result = tick(lifecycle, anchor + 20001U, Button::MODE);
    CHECK(result.gate.phase == countdown::Phase::IDLE);
    CHECK_FALSE(result.service_start_failed);
    CHECK_FALSE(result.services.calibration_rejected);
    CHECK_FALSE(result.services.active);
}

TEST_CASE("B3 D-035 external STOP after GO preserves completed diagnostics while inhibiting") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    complete(lifecycle, anchor);
    auto result = tick(lifecycle, anchor + 5100001U, Button::NONE, NAN_VALUE, NAN_VALUE, false, 0U, 0U, true);
    CHECK(result.gate.phase == countdown::Phase::STOPPED);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.gate.go);
    CHECK_FALSE(result.heading_reset_requested);
    checkCompletedEvidence(result);
    result = tick(lifecycle, anchor + 6000000U, Button::START, NAN_VALUE, NAN_VALUE, false);
    CHECK(result.gate.phase == countdown::Phase::STOPPED);
    CHECK_FALSE(result.gate.motion_permitted);
    checkCompletedEvidence(result);
}

TEST_CASE("B3 D-035 logical BOTH after GO retains completed diagnostics through STOP qualification") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    complete(lifecycle, anchor);
    const auto both = anchor + 5100001U;
    tick(lifecycle, both, Button::BOTH);
    auto result = tick(lifecycle, both + 20000U, Button::BOTH);
    CHECK(result.gate.motion_permitted);
    checkCompletedEvidence(result);
    result = tick(lifecycle, both + 1019999U, Button::BOTH);
    CHECK(result.gate.motion_permitted);
    result = tick(lifecycle, both + 1020000U, Button::BOTH);
    CHECK(result.gate.phase == countdown::Phase::STOPPED);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.heading_reset_requested);
    checkCompletedEvidence(result);
    result = tick(lifecycle, both + 1020001U, Button::NONE);
    CHECK(result.gate.phase == countdown::Phase::STOPPED);
    checkCompletedEvidence(result);
}

TEST_CASE("B3 a new accepted release starts fresh services and consumes only its supplied bias") {
    countdown::Lifecycle lifecycle;
    const auto first = release(lifecycle);
    finishCalibration(lifecycle, first);
    tick(lifecycle, first + 4800000U, Button::MODE, 7.0F, 0.0F, true, 1U, 2U);
    const auto canceled = tick(lifecycle, first + 4820000U, Button::MODE);
    checkCleared(canceled.services, 2.0F);
    const auto base = first + 4900000U;
    tick(lifecycle, base, Button::NONE);
    tick(lifecycle, base + 20000U, Button::NONE);
    const auto second = release(lifecycle, base + 21000U, 5.0F);
    const auto result = tick(lifecycle, second + 1U, Button::NONE, NAN_VALUE);
    checkHolding(result);
    CHECK(result.services.active);
    CHECK(result.services.bias_dps == doctest::Approx(5.0F));
    CHECK(result.services.calibration_samples == 0U);
    CHECK_FALSE(result.services.calibration_finished);
    CHECK_FALSE(result.services.calibration_rejected);
    CHECK_FALSE(result.services.line_warning);
    CHECK(result.services.opponent_snapshot == 0U);
    CHECK_FALSE(result.service_start_failed);
}

TEST_CASE("B3 Lifecycle reset clears diagnostics and still ignores START held at reset") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    complete(lifecycle, anchor);
    tick(lifecycle, anchor + 5100001U, Button::NONE, 7.0F, 0.0F, true, 0U, 0U, true);
    lifecycle.reset();
    auto result = tick(lifecycle, 0U, Button::START, NAN_VALUE);
    CHECK(result.gate.phase == countdown::Phase::IDLE);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.service_start_failed);
    checkCleared(result.services, 0.0F);
    tick(lifecycle, 20000U, Button::START);
    tick(lifecycle, 21000U, Button::NONE);
    result = tick(lifecycle, 41000U, Button::NONE);
    CHECK_FALSE(result.gate.start_release);
    CHECK_FALSE(result.services.active);
    const auto new_anchor = release(lifecycle, 50000U, 3.0F);
    result = tick(lifecycle, new_anchor + 5099999U);
    checkHolding(result);
}

TEST_CASE("B3 Lifecycle release services and GO retain exact boundaries across micros wrap") {
    countdown::Lifecycle lifecycle;
    const auto base = std::numeric_limits<std::uint32_t>::max() - 30000U;
    const auto anchor = release(lifecycle, base);
    finishCalibration(lifecycle, anchor);
    checkHolding(tick(lifecycle, anchor + 5099999U));
    const auto result = tick(lifecycle, anchor + 5100000U);
    CHECK(result.gate.go);
    CHECK(result.gate.motion_permitted);
    CHECK(result.heading_reset_requested);
    CHECK(result.services.finished);
    CHECK(result.services.bias_dps == doctest::Approx(2.0F));
}

TEST_CASE("B3 Lifecycle finished services cannot grant motion ahead of Gate on a sparse wrapped stream") {
    countdown::Lifecycle lifecycle;
    const auto anchor = release(lifecycle);
    checkHolding(tick(lifecycle, anchor + 4000000U));
    constexpr std::uint32_t GAP = std::numeric_limits<std::uint32_t>::max() - 3000000U;
    const auto aliased_time = anchor + 4000000U + GAP;
    const auto result = tick(lifecycle, aliased_time);
    checkHolding(result);
    CHECK(result.services.finished);
    CHECK_FALSE(result.services.active);
    CHECK(result.services.calibration_rejected);
    const auto ready = tick(lifecycle, anchor + 5100000U);
    CHECK(ready.gate.go);
    CHECK(ready.gate.motion_permitted);
    CHECK(ready.heading_reset_requested);
}
