// Checks B3 countdown services against the D-024 sampling and retention contract.
// Locks logical service-to-gate isolation without claiming physical motor safety.
// Independent doctest cases use contract boundaries, faulty samples and real Controller.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include "core/governor.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t HOLD_US = 5100000U;
constexpr std::uint32_t CAL_START_US = 1500000U;
constexpr std::uint32_t CAL_END_US = 4500000U;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();

countdown::ServiceSample sample(std::uint32_t t_us, float gyro = 1.0F,
                                bool valid = true, std::uint8_t line = 0U,
                                std::uint8_t opponent = 0U) {
    countdown::ServiceSample result;
    result.t_us = t_us;
    result.raw_gyro_z_dps = gyro;
    result.imu_ok = valid;
    result.line_mask = line;
    result.confirmed_opp_mask = opponent;
    return result;
}

void checkCleared(const countdown::ServiceResult& result, float bias) {
    CHECK(result.bias_dps == doctest::Approx(bias));
    CHECK(result.calibration_samples == 0U);
    CHECK_FALSE(result.calibration_finished);
    CHECK_FALSE(result.calibration_rejected);
    CHECK_FALSE(result.line_warning);
    CHECK(result.opponent_snapshot == 0U);
    CHECK_FALSE(result.active);
    CHECK_FALSE(result.finished);
}

void checkCalibration(const countdown::ServiceResult& result, float bias,
                      std::uint32_t count, bool rejected) {
    CHECK(result.bias_dps == doctest::Approx(bias));
    CHECK(result.calibration_samples == count);
    CHECK(result.calibration_finished);
    CHECK(result.calibration_rejected == rejected);
}

void checkSame(const countdown::ServiceResult& actual,
               const countdown::ServiceResult& expected) {
    CHECK(actual.bias_dps == expected.bias_dps);
    CHECK(actual.calibration_samples == expected.calibration_samples);
    CHECK(actual.calibration_finished == expected.calibration_finished);
    CHECK(actual.calibration_rejected == expected.calibration_rejected);
    CHECK(actual.line_warning == expected.line_warning);
    CHECK(actual.opponent_snapshot == expected.opponent_snapshot);
    CHECK(actual.active == expected.active);
    CHECK(actual.finished == expected.finished);
}

struct LogicalTick {
    countdown::Result gate;
    countdown::ServiceResult services;
    governor::Result governed;
};

class LogicalHarness {
public:
    LogicalTick tick(countdown::ServiceSample observation,
                     core::ButtonLevel button = core::ButtonLevel::NONE,
                     bool stop = false) {
        core::Inputs input;
        input.t_us = observation.t_us;
        input.button_level = button;
        LogicalTick result;
        result.gate = controller.step(input, stop);
        if (result.gate.start_release) {
            CHECK(services.start(result.gate.release_us, bias_dps));
            pending = true;
        }
        if (pending && (result.gate.phase == countdown::Phase::IDLE ||
                        result.gate.phase == countdown::Phase::STOPPED)) {
            services.cancel();
            pending = false;
            ++cancel_calls;
        }
        result.services = services.step(observation);
        bias_dps = result.services.bias_dps;
        governor::Request request;
        request.duty_l = .30F;
        request.duty_r = .30F;
        request.vbat_v = 11.1F;
        request.profile = governor::Profile::SEARCH_FORWARD;
        request.inhibited = !result.gate.motion_permitted;
        result.governed = governor.step(observation.t_us, request);
        return result;
    }
    countdown::Controller controller;
    countdown::Services services;
    governor::Governor governor;
    float bias_dps = 0.0F;
    unsigned cancel_calls = 0U;
    bool pending = false;
};

std::uint32_t beginHold(LogicalHarness& harness, std::uint32_t origin = 0U,
                        std::uint32_t qualified_offset = 42000U) {
    harness.tick(sample(origin));
    harness.tick(sample(origin + 1000U), core::ButtonLevel::START);
    harness.tick(sample(origin + 21000U), core::ButtonLevel::START);
    harness.tick(sample(origin + 22000U));
    const auto started = harness.tick(sample(origin + qualified_offset));
    CHECK(started.gate.start_release);
    CHECK(started.gate.release_us == origin + qualified_offset);
    CHECK(started.services.active);
    CHECK_FALSE(started.gate.motion_permitted);
    return origin + qualified_offset;
}

void checkInhibited(const LogicalTick& result, countdown::Phase phase) {
    CHECK(result.gate.phase == phase);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.gate.go);
    CHECK(result.governed.valid);
    CHECK(result.governed.duty_l == 0.0F);
    CHECK(result.governed.duty_r == 0.0F);
}
} // namespace

TEST_CASE("B3 Services defaults are inert and D024 constants match approved windows") {
    CHECK(config::CAL_START_MS == 1500U);
    CHECK(config::CAL_END_MS == 4500U);
    CHECK(config::CAL_MIN_SAMPLES == 2U);
    CHECK(config::COUNTDOWN_LINE_WARN_MS == 1000U);
    CHECK(config::COUNTDOWN_SNAPSHOT_MS == 300U);
    CHECK(config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS == 5100U);
    countdown::Services services;
    checkCleared(services.step(sample(0U)), 0.0F);
    checkCleared(services.step(sample(HOLD_US, NAN_VALUE, false, 15U, 127U)), 0.0F);
    const countdown::ServiceSample observation;
    CHECK(observation.t_us == 0U);
    CHECK(observation.raw_gyro_z_dps == 0.0F);
    CHECK_FALSE(observation.imu_ok);
    CHECK(observation.line_mask == 0U);
    CHECK(observation.confirmed_opp_mask == 0U);
    checkCleared(countdown::ServiceResult{}, 0.0F);
}

TEST_CASE("B3 calibration includes 1.5s and excludes exact4.5s with adjacent ticks") {
    countdown::Services services;
    CHECK(services.start(100U, 7.0F));
    auto result = services.step(sample(100U + CAL_START_US - 1000U, NAN_VALUE, false));
    CHECK(result.calibration_samples == 0U);
    result = services.step(sample(100U + CAL_START_US - 1U, NAN_VALUE, false));
    CHECK(result.calibration_samples == 0U);
    result = services.step(sample(100U + CAL_START_US, 1.0F));
    CHECK(result.calibration_samples == 1U);
    CHECK(result.bias_dps == 7.0F);
    CHECK_FALSE(result.calibration_finished);
    result = services.step(sample(100U + CAL_START_US + 1U, 2.0F));
    CHECK(result.calibration_samples == 2U);
    result = services.step(sample(100U + CAL_END_US - 1000U, 3.0F));
    CHECK(result.calibration_samples == 3U);
    result = services.step(sample(100U + CAL_END_US - 1U, 2.0F));
    CHECK(result.calibration_samples == 4U);
    CHECK_FALSE(result.calibration_finished);
    result = services.step(sample(100U + CAL_END_US, NAN_VALUE, false));
    checkCalibration(result, 2.0F, 4U, false);
    CHECK(result.active);
    CHECK_FALSE(result.finished);
    checkCalibration(services.step(sample(100U + CAL_END_US + 1000U, 100.0F)), 2.0F, 4U, false);
}

TEST_CASE("B3 calibration uses sample arithmetic mean and max minus min spread") {
    countdown::Services services;
    CHECK(services.start(0U, -7.0F));
    services.step(sample(CAL_START_US, .5F));
    services.step(sample(CAL_START_US + 1U, .5F));
    services.step(sample(CAL_END_US - 1U, 2.5F));
    const auto result = services.step(sample(CAL_END_US));
    checkCalibration(result, 3.5F / 3.0F, 3U, false);
    CHECK(result.bias_dps != 1.5F);
    CHECK(result.bias_dps != .5F);
}

TEST_CASE("B3 calibration accepts exactly2dps spread and rejects next float above") {
    for (float upper : {2.0F, std::nextafter(2.0F, INF_VALUE)}) {
        CAPTURE(upper);
        countdown::Services services;
        CHECK(services.start(0U, 7.0F));
        services.step(sample(CAL_START_US, 0.0F));
        services.step(sample(CAL_START_US + 1000U, upper));
        const bool rejected = upper > 2.0F;
        checkCalibration(services.step(sample(CAL_END_US)), rejected ? 7.0F : 1.0F, 2U, rejected);
    }
    countdown::Services negative;
    CHECK(negative.start(0U, 7.0F));
    negative.step(sample(CAL_START_US, -4.0F));
    negative.step(sample(CAL_START_US + 1000U, -2.0F));
    checkCalibration(negative.step(sample(CAL_END_US)), -3.0F, 2U, false);
}

TEST_CASE("B3 calibration rejects one sparse outlier even when most readings agree") {
    countdown::Services services;
    CHECK(services.start(0U, -7.0F));
    for (std::uint32_t index = 0U; index < 100U; ++index) {
        services.step(sample(CAL_START_US + index * 1000U, 0.0F));
    }
    services.step(sample(CAL_END_US - 1U, 2.25F));
    checkCalibration(services.step(sample(CAL_END_US)), -7.0F, 101U, true);
}

TEST_CASE("B3 calibration requires two supplied valid readings and preserves prior bias") {
    for (std::uint32_t count : {0U, 1U, 2U}) {
        countdown::Services services;
        CHECK(services.start(0U, 7.0F));
        for (std::uint32_t index = 0U; index < count; ++index) {
            services.step(sample(CAL_START_US + index * 1000U, 3.0F));
        }
        const bool rejected = count < 2U;
        checkCalibration(services.step(sample(CAL_END_US)), rejected ? 7.0F : 3.0F, count, rejected);
    }
}

TEST_CASE("B3 any unavailable IMU reading rejects even with enough finite valid readings") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(CAL_START_US, 1.0F));
    services.step(sample(CAL_START_US + 1000U, 1.0F, false));
    services.step(sample(CAL_START_US + 2000U, 1.0F));
    const auto result = services.step(sample(CAL_END_US));
    CHECK(result.calibration_finished);
    CHECK(result.calibration_rejected);
    CHECK(result.bias_dps == 7.0F);
}

TEST_CASE("B3 each nonfinite gyro reading rejects for both IMU flag values") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        for (bool healthy : {false, true}) {
            countdown::Services services;
            CHECK(services.start(0U, -7.0F));
            services.step(sample(CAL_START_US, 1.0F));
            services.step(sample(CAL_START_US + 1000U, invalid, healthy));
            services.step(sample(CAL_START_US + 2000U, 1.0F));
            const auto result = services.step(sample(CAL_END_US));
            CHECK(result.calibration_finished);
            CHECK(result.calibration_rejected);
            CHECK(result.bias_dps == -7.0F);
        }
    }
}

TEST_CASE("B3 invalid samples outside calibration window cannot poison accepted bias") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(0U, NAN_VALUE, false));
    services.step(sample(CAL_START_US - 1U, INF_VALUE, false));
    services.step(sample(CAL_START_US, 1.0F));
    services.step(sample(CAL_END_US - 1U, 1.0F));
    checkCalibration(services.step(sample(CAL_END_US, NAN_VALUE, false)), 1.0F, 2U, false);
    checkCalibration(services.step(sample(CAL_END_US + 1U, -INF_VALUE, false)), 1.0F, 2U, false);
}

TEST_CASE("B3 duplicate timestamps cannot fabricate samples change mean or add faults") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(CAL_START_US, 1.0F));
    for (float duplicate : {1.0F, 9.0F, NAN_VALUE}) {
        const auto result = services.step(sample(CAL_START_US, duplicate, false));
        CHECK(result.calibration_samples == 1U);
        CHECK_FALSE(result.calibration_finished);
    }
    services.step(sample(CAL_START_US + 1U, 3.0F));
    checkCalibration(services.step(sample(CAL_END_US)), 2.0F, 2U, false);
    CHECK(services.start(100U, 7.0F));
    services.step(sample(100U + CAL_START_US, 1.0F));
    for (unsigned index = 0U; index < 100U; ++index) {
        services.step(sample(100U + CAL_START_US, 1.0F));
    }
    checkCalibration(services.step(sample(100U + CAL_END_US)), 7.0F, 1U, true);
}

TEST_CASE("B3 missing calls neither fabricate calibration data nor rescale the mean") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(CAL_START_US - 1U, 1.0F));
    checkCalibration(services.step(sample(CAL_END_US + 1000U, 1.0F)), 7.0F, 0U, true);
    CHECK(services.start(0U, 7.0F));
    services.step(sample(CAL_START_US, 1.0F));
    services.step(sample(CAL_END_US - 1U, 3.0F));
    checkCalibration(services.step(sample(CAL_END_US + 1000U, 100.0F)), 2.0F, 2U, false);
}

TEST_CASE("B3 late finalization happens once and does not ingest the late sample") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(CAL_START_US, 1.0F));
    services.step(sample(CAL_START_US + 1000U, 3.0F));
    const auto result = services.step(sample(4900000U, NAN_VALUE, false));
    checkCalibration(result, 2.0F, 2U, false);
    CHECK(result.active);
    CHECK_FALSE(result.finished);
    checkCalibration(services.step(sample(4901000U, 100.0F)), 2.0F, 2U, false);
    const auto end = services.step(sample(HOLD_US, -100.0F));
    checkCalibration(end, 2.0F, 2U, false);
    CHECK_FALSE(end.active);
    CHECK(end.finished);
}

TEST_CASE("B0 B3 service windows and completion survive unsigned timestamp wrap") {
    const std::uint32_t release = 0xFFFF0000U;
    countdown::Services services;
    CHECK(services.start(release, 7.0F));
    CHECK(services.step(sample(release + CAL_START_US - 1U)).calibration_samples == 0U);
    services.step(sample(release + CAL_START_US, 1.0F));
    services.step(sample(release + CAL_END_US - 1U, 3.0F));
    checkCalibration(services.step(sample(release + CAL_END_US)), 2.0F, 2U, false);
    const auto warning = services.step(sample(release + 4800000U, 1.0F, true, 1U, 8U));
    CHECK(warning.line_warning);
    CHECK(warning.opponent_snapshot == 8U);
    CHECK(services.step(sample(release + HOLD_US - 1U)).active);
    const auto result = services.step(sample(release + HOLD_US));
    CHECK_FALSE(result.active);
    CHECK(result.finished);
    checkCalibration(result, 2.0F, 2U, false);
}

TEST_CASE("B0 B3 late calls after full start wrap cannot revive services or fabricate readings") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(1000000U));
    // Consecutive call gap is less than one full wrap; total age exceeds one.
    const auto result = services.step(sample(500000U, 1.0F, true, 15U, 127U));
    checkCalibration(result, 7.0F, 0U, true);
    CHECK(result.finished);
    CHECK_FALSE(result.active);
    CHECK_FALSE(result.line_warning);
    CHECK(result.opponent_snapshot == 0U);
    checkSame(services.step(sample(CAL_START_US, 100.0F)), result);
}

TEST_CASE("B3 final second line warning starts at4.1s and latches every QTR bit") {
    for (std::uint8_t line : {1U, 2U, 4U, 8U}) {
        countdown::Services services;
        CHECK(services.start(0U, 0.0F));
        CHECK_FALSE(services.step(sample(4099000U, 1.0F, true, line)).line_warning);
        CHECK_FALSE(services.step(sample(4099999U, 1.0F, true, line)).line_warning);
        CHECK(services.step(sample(4100000U, 1.0F, true, line)).line_warning);
        CHECK(services.step(sample(4100001U, 1.0F, true, 0U)).line_warning);
        CHECK(services.step(sample(HOLD_US - 1U, 1.0F, true, 0U)).line_warning);
        CHECK(services.step(sample(HOLD_US, 1.0F, true, 0U)).line_warning);
    }
}

TEST_CASE("B3 line warning excludes GO and never backfills missing window samples") {
    for (std::uint32_t end : {HOLD_US, HOLD_US + 1U, HOLD_US + 1000U}) {
        countdown::Services services;
        CHECK(services.start(0U, 0.0F));
        services.step(sample(4099999U, 1.0F, true, 15U));
        const auto result = services.step(sample(end, 1.0F, true, 15U));
        CHECK_FALSE(result.line_warning);
        CHECK(result.finished);
    }
    countdown::Services final_tick;
    CHECK(final_tick.start(0U, 0.0F));
    CHECK(final_tick.step(sample(HOLD_US - 1U, 1.0F, true, 1U)).line_warning);
}

TEST_CASE("B3 opponent snapshot opens at4.8s and stores latest low seven bits not OR") {
    countdown::Services services;
    CHECK(services.start(0U, 0.0F));
    CHECK(services.step(sample(4799000U, 1.0F, true, 0U, 1U)).opponent_snapshot == 0U);
    CHECK(services.step(sample(4799999U, 1.0F, true, 0U, 2U)).opponent_snapshot == 0U);
    CHECK(services.step(sample(4800000U, 1.0F, true, 0U, 4U)).opponent_snapshot == 4U);
    CHECK(services.step(sample(4800001U, 1.0F, true, 0U, 8U)).opponent_snapshot == 8U);
    CHECK(services.step(sample(4801000U, 1.0F, true, 0U, 0U)).opponent_snapshot == 0U);
    CHECK(services.step(sample(4802000U, 1.0F, true, 0U, 0xFFU)).opponent_snapshot == 0x7FU);
    CHECK(services.step(sample(4803000U, 1.0F, true, 0U, 0x80U)).opponent_snapshot == 0U);
    CHECK(services.step(sample(HOLD_US - 1U, 1.0F, true, 0U, 64U)).opponent_snapshot == 64U);
    CHECK(services.step(sample(HOLD_US, 1.0F, true, 0U, 32U)).opponent_snapshot == 64U);
}

TEST_CASE("B3 opponent snapshot excludes GO and missing final window stays zero") {
    countdown::Services services;
    CHECK(services.start(0U, 0.0F));
    services.step(sample(4799999U, 1.0F, true, 0U, 127U));
    const auto result = services.step(sample(HOLD_US, 1.0F, true, 0U, 127U));
    CHECK(result.opponent_snapshot == 0U);
    CHECK(result.finished);
    CHECK(services.step(sample(HOLD_US + 1000U, 1.0F, true, 0U, 1U)).opponent_snapshot == 0U);
}

TEST_CASE("B3 GO freezes every service output despite later changed or invalid input") {
    countdown::Services services;
    CHECK(services.start(0U, 7.0F));
    services.step(sample(CAL_START_US, 1.0F));
    services.step(sample(CAL_START_US + 1000U, 3.0F));
    services.step(sample(4800000U, 1.0F, true, 1U, 4U));
    const auto finished = services.step(sample(HOLD_US, NAN_VALUE, false, 0U, 0U));
    checkCalibration(finished, 2.0F, 2U, false);
    CHECK(finished.line_warning);
    CHECK(finished.opponent_snapshot == 4U);
    CHECK_FALSE(finished.active);
    CHECK(finished.finished);
    checkSame(services.step(sample(HOLD_US + 1U, -100.0F, true, 15U, 127U)), finished);
    checkSame(services.step(sample(HOLD_US + 1000U, INF_VALUE, false, 0U, 0U)), finished);
    checkSame(services.step(sample(0U, 100.0F, true, 15U, 127U)), finished);
}

TEST_CASE("B3 cancel clears attempt state and preserves either prior or accepted bias") {
    for (bool finish_calibration : {false, true}) {
        countdown::Services services;
        CHECK(services.start(0U, 7.0F));
        services.step(sample(CAL_START_US, 1.0F));
        services.step(sample(CAL_START_US + 1000U, 3.0F));
        if (finish_calibration) services.step(sample(4800000U, 1.0F, true, 1U, 4U));
        services.cancel();
        const float expected = finish_calibration ? 2.0F : 7.0F;
        checkCleared(services.step(sample(HOLD_US, NAN_VALUE, false, 15U, 127U)), expected);
        services.cancel();
        checkCleared(services.step(sample(HOLD_US + 1000U)), expected);
    }
}

TEST_CASE("B3 reset clears calibration warning snapshot bias and rejection history") {
    for (bool valid : {false, true}) {
        countdown::Services services;
        CHECK(services.start(0U, 7.0F));
        services.step(sample(CAL_START_US, 1.0F, valid));
        services.step(sample(CAL_START_US + 1000U, 3.0F, valid));
        services.step(sample(4800000U, 1.0F, true, 1U, 4U));
        services.reset();
        checkCleared(services.step(sample(HOLD_US, NAN_VALUE, false, 15U, 127U)), 0.0F);
        CHECK(services.start(HOLD_US, -2.0F));
        CHECK(services.step(sample(HOLD_US)).bias_dps == -2.0F);
    }
}

TEST_CASE("B3 restart replaces rejected active or completed attempt with clean state") {
    for (bool completed : {false, true}) {
        countdown::Services services;
        CHECK(services.start(0U, 7.0F));
        services.step(sample(CAL_START_US, NAN_VALUE, false));
        services.step(sample(4800000U, 1.0F, true, 1U, 4U));
        if (completed) services.step(sample(HOLD_US));
        CHECK(services.start(6000000U, -2.0F));
        const auto restarted = services.step(sample(6000000U));
        CHECK(restarted.active);
        CHECK_FALSE(restarted.finished);
        CHECK_FALSE(restarted.calibration_finished);
        CHECK_FALSE(restarted.calibration_rejected);
        CHECK(restarted.calibration_samples == 0U);
        CHECK_FALSE(restarted.line_warning);
        CHECK(restarted.opponent_snapshot == 0U);
        CHECK(restarted.bias_dps == -2.0F);
        services.step(sample(6000000U + CAL_START_US, 1.0F));
        services.step(sample(6000000U + CAL_START_US + 1000U, 1.0F));
        checkCalibration(services.step(sample(6000000U + CAL_END_US)), 1.0F, 2U, false);
    }
}

TEST_CASE("B3 nonfinite previous bias rejects start and a valid restart clears rejection") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        countdown::Services services;
        CHECK_FALSE(services.start(0U, invalid));
        const auto result = services.step(sample(CAL_START_US, 1.0F, true, 15U, 127U));
        CHECK_FALSE(result.active);
        CHECK_FALSE(result.finished);
        CHECK(result.calibration_rejected);
        CHECK(result.calibration_samples == 0U);
        CHECK(std::isfinite(result.bias_dps));
        CHECK(services.start(100U, 7.0F));
        const auto restarted = services.step(sample(100U));
        CHECK(restarted.active);
        CHECK_FALSE(restarted.calibration_rejected);
        CHECK(restarted.bias_dps == 7.0F);
    }
}

TEST_CASE("B3 D019 services and calibration never grant motion before qualified full hold") {
    for (bool calibration_valid : {false, true}) {
        LogicalHarness harness;
        const auto release = beginHold(harness);
        for (std::uint32_t elapsed = 1000U; elapsed <= HOLD_US + 1000U; elapsed += 1000U) {
            const bool valid = calibration_valid || elapsed != 2000000U;
            const auto result = harness.tick(sample(release + elapsed, 1.0F, valid, 1U, 4U));
            if (elapsed < HOLD_US) checkInhibited(result, countdown::Phase::HOLDING);
            else {
                CHECK(result.gate.motion_permitted);
                CHECK(result.gate.go == (elapsed == HOLD_US));
                CHECK(result.services.finished);
                CHECK_FALSE(result.services.active);
            }
            if (elapsed == CAL_END_US) {
                CHECK(result.services.calibration_finished);
                CHECK(result.services.calibration_rejected == !calibration_valid);
                CHECK(result.services.bias_dps == (calibration_valid ? 1.0F : 0.0F));
                CHECK_FALSE(result.gate.motion_permitted);
            }
        }
        CHECK(harness.cancel_calls == 0U);
    }
}

TEST_CASE("B3 D019 delayed release qualification anchors services and gate without backdating") {
    for (std::uint32_t origin : {0U, 0xFFFF0000U}) {
        LogicalHarness harness;
        const auto release = beginHold(harness, origin, 90000U);
        auto result = harness.tick(sample(origin + 22000U + CAL_START_US, 1.0F));
        CHECK(result.services.calibration_samples == 0U);
        checkInhibited(result, countdown::Phase::HOLDING);
        result = harness.tick(sample(release + CAL_START_US, 1.0F));
        CHECK(result.services.calibration_samples == 1U);
        harness.tick(sample(release + CAL_START_US + 1000U, 1.0F));
        result = harness.tick(sample(origin + 22000U + HOLD_US));
        checkInhibited(result, countdown::Phase::HOLDING);
        result = harness.tick(sample(release + HOLD_US - 1U));
        checkInhibited(result, countdown::Phase::HOLDING);
        result = harness.tick(sample(release + HOLD_US));
        CHECK(result.gate.go);
        CHECK(result.gate.motion_permitted);
        CHECK(result.services.finished);
        CHECK(result.services.bias_dps == 1.0F);
    }
}

TEST_CASE("B3 MODE cancellation explicitly cancels services and prevents later service GO") {
    LogicalHarness harness;
    const auto release = beginHold(harness);
    harness.tick(sample(release + CAL_START_US, 1.0F));
    harness.tick(sample(release + CAL_START_US + 1000U, 1.0F));
    harness.tick(sample(release + 4800000U, 1.0F, true, 1U, 4U));
    auto result = harness.tick(sample(release + 4810000U), core::ButtonLevel::MODE);
    checkInhibited(result, countdown::Phase::HOLDING);
    CHECK(harness.cancel_calls == 0U);
    result = harness.tick(sample(release + 4830000U), core::ButtonLevel::MODE);
    checkInhibited(result, countdown::Phase::IDLE);
    CHECK(harness.cancel_calls == 1U);
    checkCleared(result.services, 1.0F);
    result = harness.tick(sample(release + HOLD_US + 1000U, NAN_VALUE, false, 15U, 127U));
    checkInhibited(result, countdown::Phase::IDLE);
    checkCleared(result.services, 1.0F);
}

TEST_CASE("B3 STOP explicitly cancels active services immediately and stays latched") {
    LogicalHarness harness;
    const auto release = beginHold(harness);
    harness.tick(sample(release + CAL_START_US, 1.0F));
    harness.tick(sample(release + CAL_START_US + 1000U, 1.0F));
    const auto stopped = harness.tick(sample(release + CAL_START_US + 1001U), core::ButtonLevel::NONE, true);
    checkInhibited(stopped, countdown::Phase::STOPPED);
    CHECK(harness.cancel_calls == 1U);
    checkCleared(stopped.services, 0.0F);
    const auto later = harness.tick(sample(release + 2U * HOLD_US, 1.0F, true, 15U, 127U));
    checkInhibited(later, countdown::Phase::STOPPED);
    checkCleared(later.services, 0.0F);
    CHECK(harness.cancel_calls == 1U);
}
