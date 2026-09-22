// Checks B2/B7/B10 defensive turns from the committed public interface.
// Separates target intents and two timeout deadlines from global motor permission.
// Independent host cases cover capture, masks, fallback, wrap and mirrored demands.
#include "doctest.h"
#include "config.h"
#include "core/fsm.h"
#include "core/governor.h"
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();

void checkZero(const fsm::DefendResult& result, fsm::Intent intent) {
    CHECK(result.intent == intent);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
}

void checkActive(const fsm::DefendResult& result, float left = 0.80F) {
    CHECK(result.intent == fsm::Intent::NONE);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(-left));
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.defend_timed_out);
}

void checkNoTimeouts(const fsm::DefendResult& result) {
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.defend_timed_out);
}

void checkBounded(const fsm::DefendResult& result) {
    CHECK(std::isfinite(result.motion.duty_l));
    CHECK(std::isfinite(result.motion.duty_r));
    CHECK(std::abs(result.motion.duty_l) <= 0.800001F);
    CHECK(std::abs(result.motion.duty_r) <= 0.800001F);
    CHECK(result.motion.duty_l == doctest::Approx(-result.motion.duty_r));
    if (result.intent != fsm::Intent::NONE) {
        CHECK(result.motion.duty_l == 0.0F);
        CHECK(result.motion.duty_r == 0.0F);
    }
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    return static_cast<std::uint8_t>((mask & 0x02U) |
        ((mask & 0x01U) << 2U) | ((mask & 0x04U) >> 2U) |
        ((mask & 0x08U) << 1U) | ((mask & 0x10U) >> 1U) |
        ((mask & 0x20U) << 1U) | ((mask & 0x40U) >> 1U));
}

void checkMirrored(const fsm::DefendResult& right, const fsm::DefendResult& left) {
    checkBounded(right);
    checkBounded(left);
    CHECK(right.intent == left.intent);
    CHECK(right.motion.status == left.motion.status);
    CHECK(right.motion.imu_fallback == left.motion.imu_fallback);
    CHECK(right.turn_timed_out == left.turn_timed_out);
    CHECK(right.defend_timed_out == left.defend_timed_out);
    CHECK(right.motion.duty_l == doctest::Approx(left.motion.duty_r));
    CHECK(right.motion.duty_r == doctest::Approx(left.motion.duty_l));
}

std::uint32_t randomValue(std::uint32_t& seed) {
    seed = 1664525U * seed + 1013904223U;
    return seed;
}

governor::Request pivotRequest(const fsm::DefendResult& result, float voltage) {
    governor::Request request;
    request.duty_l = result.motion.duty_l;
    request.duty_r = result.motion.duty_r;
    request.profile = governor::Profile::PIVOT;
    request.vbat_v = voltage;
    request.inhibited = false;
    return request;
}
} // namespace

TEST_CASE("B10 default defensive turn is inert even with live target observations") {
    fsm::DefendTurn defend;
    for (auto mask : {0U, 2U, 8U, 0x7FU, 0xFFU}) {
        const auto result = defend.step(1000U, NAN_VALUE, true,
                                        static_cast<std::uint8_t>(mask));
        checkZero(result, fsm::Intent::NONE);
        CHECK(result.motion.status == motion::Status::IDLE);
        checkNoTimeouts(result);
    }
}

TEST_CASE("B10 invalid bearing evidence and nonfinite capture latch zero INVALID") {
    for (bool imu_ok : {false, true}) {
        for (float heading : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
            fsm::DefendTurn defend;
            CHECK_FALSE(defend.start(0U, heading, 90.0F, true, imu_ok));
            checkZero(defend.step(0U, 0.0F, true, 0x7FU), fsm::Intent::INVALID);
        }
        for (float bearing : {NAN_VALUE, INF_VALUE, -INF_VALUE, -180.0F, -181.0F,
                              std::nextafter(180.0F, INF_VALUE)}) {
            fsm::DefendTurn defend;
            CHECK_FALSE(defend.start(0U, 0.0F, bearing, true, imu_ok));
            checkZero(defend.step(1000000U, 0.0F, true, 0U), fsm::Intent::INVALID);
        }
        fsm::DefendTurn missing;
        CHECK_FALSE(missing.start(0U, 0.0F, 90.0F, false, imu_ok));
        const auto result = missing.step(900000U, 0.0F, true, 2U);
        checkZero(result, fsm::Intent::INVALID);
        checkNoTimeouts(result);
    }
}

TEST_CASE("B10 bearing interval excludes minus180 and includes positive180") {
    const float near_negative = std::nextafter(-180.0F, 0.0F);
    fsm::DefendTurn negative;
    CHECK(negative.start(0U, 0.0F, near_negative, true, true));
    checkActive(negative.step(0U, 0.0F, true, 8U), -0.80F);
    fsm::DefendTurn positive;
    CHECK(positive.start(0U, 0.0F, 180.0F, true, true));
    checkActive(positive.step(0U, 0.0F, true, 16U), 0.80F);
    fsm::DefendTurn zero;
    CHECK(zero.start(0U, 0.0F, 0.0F, true, true));
    const auto done = zero.step(0U, 0.0F, true, 8U);
    checkZero(done, fsm::Intent::NONE);
    CHECK(done.motion.status == motion::Status::DONE);
    checkNoTimeouts(done);
}

TEST_CASE("B10 all four B5 side rear bearings demand the corresponding pivot") {
    const float bearings[4] = {-90.0F, 90.0F, -135.0F, 135.0F};
    const std::uint8_t masks[4] = {8U, 16U, 32U, 64U};
    for (std::size_t index = 0U; index < 4U; ++index) {
        fsm::DefendTurn defend;
        CHECK(defend.start(7000U, 37.0F, bearings[index], true, true));
        checkActive(defend.step(7000U, 37.0F, true, masks[index]),
                    bearings[index] > 0.0F ? 0.80F : -0.80F);
    }
}

TEST_CASE("B10 captured heading and bearing remain fixed when side masks change") {
    fsm::DefendTurn defend;
    CHECK(defend.start(0U, 170.0F, 90.0F, true, true));
    checkActive(defend.step(0U, 170.0F, true, 16U));
    checkActive(defend.step(1000U, 200.0F, true, 8U));
    checkActive(defend.step(2000U, 245.0F, true, 32U), 0.30F);
    checkActive(defend.step(3000U, 250.0F, true, 64U), 0.25F);
    const auto result = defend.step(4000U, -100.0F, true, 0x78U);
    checkZero(result, fsm::Intent::NONE);
    CHECK(result.motion.status == motion::Status::DONE);
}

TEST_CASE("B10 normalized accumulated headings preserve a finite relative turn") {
    const float maximum = std::numeric_limits<float>::max();
    for (float heading : {1080.0F, -1080.0F, 100000000.0F, -100000000.0F,
                           maximum, -maximum}) {
        for (float bearing : {-90.0F, 90.0F}) {
            fsm::DefendTurn defend;
            CHECK(defend.start(0U, heading, bearing, true, true));
            const auto result = defend.step(0U, heading, true, 8U);
            checkBounded(result);
            checkActive(result, bearing > 0.0F ? 0.80F : -0.80F);
        }
    }
}

TEST_CASE("B10 B7 strict five degree tolerance applies on both sides of the target") {
    const float samples[6] = {
        std::nextafter(85.0F, -INF_VALUE), 85.0F,
        std::nextafter(85.0F, INF_VALUE), std::nextafter(95.0F, -INF_VALUE),
        95.0F, std::nextafter(95.0F, INF_VALUE)
    };
    for (std::size_t index = 0U; index < 6U; ++index) {
        fsm::DefendTurn defend;
        CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
        const auto result = defend.step(1000U, samples[index], true, 16U);
        if (index == 2U || index == 3U) {
            checkZero(result, fsm::Intent::NONE);
            CHECK(result.motion.status == motion::Status::DONE);
        } else {
            checkActive(result, samples[index] < 90.0F ? 0.25F : -0.25F);
        }
    }
}

TEST_CASE("B10 B7 P gain minimum and maximum requests use existing literal defaults") {
    for (float bearing : {-40.0F, -20.0F, -10.0F, 10.0F, 20.0F, 40.0F}) {
        fsm::DefendTurn defend;
        CHECK(defend.start(0U, 0.0F, bearing, true, true));
        const float magnitude = std::min(0.80F, std::max(0.25F, 0.02F * std::abs(bearing)));
        checkActive(defend.step(0U, 0.0F, true, 8U),
                    bearing > 0.0F ? magnitude : -magnitude);
    }
}

TEST_CASE("B10 all128 masks use current target priority at both deadlines and wrap") {
    for (std::uint32_t start : {0U, 0xFFFFFF00U}) {
        for (std::uint32_t elapsed : {0U, 699999U, 700000U, 799999U, 800000U}) {
            for (std::uint32_t mask = 0U; mask < 128U; ++mask) {
                for (std::uint32_t high : {0U, 128U}) {
                    fsm::DefendTurn defend;
                    CHECK(defend.start(start, 0.0F, 90.0F, true, true));
                    const auto result = defend.step(start + elapsed, 0.0F, true,
                        static_cast<std::uint8_t>(mask | high));
                    if ((mask & 7U) != 0U || mask == 0U) {
                        checkZero(result, mask == 0U ? fsm::Intent::SEARCH : fsm::Intent::PERCEPTION);
                        checkNoTimeouts(result);
                    } else if (elapsed < 700000U) {
                        checkActive(result);
                    } else if (elapsed < 800000U) {
                        checkZero(result, fsm::Intent::NONE);
                        CHECK(result.motion.status == motion::Status::TIMED_OUT);
                        CHECK(result.turn_timed_out);
                        CHECK_FALSE(result.defend_timed_out);
                    } else {
                        checkZero(result, fsm::Intent::SEARCH);
                        CHECK(result.defend_timed_out);
                    }
                }
            }
        }
    }
}

TEST_CASE("B10 turn700ms and defend800ms are distinct exact one shot deadlines") {
    fsm::DefendTurn defend;
    CHECK(defend.start(100U, 0.0F, 90.0F, true, true));
    checkActive(defend.step(100U + 699999U, 0.0F, true, 16U));
    const auto turn_timeout = defend.step(100U + 700000U, 0.0F, true, 16U);
    checkZero(turn_timeout, fsm::Intent::NONE);
    CHECK(turn_timeout.motion.status == motion::Status::TIMED_OUT);
    CHECK(turn_timeout.turn_timed_out);
    CHECK_FALSE(turn_timeout.defend_timed_out);
    for (std::uint32_t elapsed : {700000U, 700001U, 799999U}) {
        const auto waiting = defend.step(100U + elapsed, 0.0F, true, 16U);
        checkZero(waiting, fsm::Intent::NONE);
        checkNoTimeouts(waiting);
    }
    const auto done = defend.step(100U + 800000U, 0.0F, true, 16U);
    checkZero(done, fsm::Intent::SEARCH);
    CHECK(done.defend_timed_out);
    CHECK_FALSE(done.turn_timed_out);
    for (std::uint32_t elapsed : {800000U, 800001U, 1600000U}) {
        const auto terminal = defend.step(100U + elapsed, 0.0F, true, 2U);
        checkZero(terminal, fsm::Intent::SEARCH);
        checkNoTimeouts(terminal);
    }
}

TEST_CASE("B10 B7 timeout takes precedence over reaching heading at exactly700ms") {
    fsm::DefendTurn defend;
    CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
    const auto result = defend.step(700000U, 90.0F, true, 16U);
    checkZero(result, fsm::Intent::NONE);
    CHECK(result.motion.status == motion::Status::TIMED_OUT);
    CHECK(result.turn_timed_out);
}

TEST_CASE("B10 healthy turn completion stays zero until the original state deadline") {
    fsm::DefendTurn defend;
    CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
    const auto done = defend.step(1000U, 90.0F, true, 16U);
    checkZero(done, fsm::Intent::NONE);
    CHECK(done.motion.status == motion::Status::DONE);
    for (std::uint32_t elapsed : {2000U, 700000U, 799999U}) {
        const auto waiting = defend.step(elapsed, -90.0F, true, 8U);
        checkZero(waiting, fsm::Intent::NONE);
        CHECK(waiting.motion.status == motion::Status::DONE);
        checkNoTimeouts(waiting);
    }
    const auto expired = defend.step(800000U, -90.0F, true, 8U);
    checkZero(expired, fsm::Intent::SEARCH);
    CHECK(expired.defend_timed_out);
    CHECK_FALSE(expired.turn_timed_out);
}

TEST_CASE("B10 front and clear observations end a completed turn before state timeout") {
    for (std::uint8_t mask : {std::uint8_t{0U}, std::uint8_t{2U}}) {
        fsm::DefendTurn defend;
        CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
        checkZero(defend.step(1000U, 90.0F, true, 16U), fsm::Intent::NONE);
        const auto result = defend.step(700000U, NAN_VALUE, true, mask);
        checkZero(result, mask == 0U ? fsm::Intent::SEARCH : fsm::Intent::PERCEPTION);
        checkNoTimeouts(result);
    }
}

TEST_CASE("B10 front and no target exits latch despite later contradictory detections") {
    for (std::uint8_t mask : {std::uint8_t{0U}, std::uint8_t{2U}}) {
        fsm::DefendTurn defend;
        CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
        const auto intent = mask == 0U ? fsm::Intent::SEARCH : fsm::Intent::PERCEPTION;
        checkZero(defend.step(1000U, 0.0F, true, mask), intent);
        for (std::uint32_t elapsed : {2000U, 800000U, 900000U}) {
            const auto result = defend.step(elapsed, NAN_VALUE, true, 0x7FU);
            checkZero(result, intent);
            checkNoTimeouts(result);
        }
    }
}

TEST_CASE("B10 unavailable IMU uses bearing times2ms fallback without extending on recovery") {
    for (float bearing : {-135.0F, -90.0F, 90.0F, 135.0F, 180.0F}) {
        fsm::DefendTurn defend;
        CHECK(defend.start(0U, 10.0F, bearing, true, false));
        const auto duration = static_cast<std::uint32_t>(std::abs(bearing) * 2000.0F);
        const float duty = bearing > 0.0F ? 0.80F : -0.80F;
        const auto first = defend.step(0U, NAN_VALUE, false, 8U);
        checkActive(first, duty);
        CHECK(first.motion.imu_fallback);
        const auto recovery = defend.step(duration - 1U, 10.0F + bearing, true, 16U);
        checkActive(recovery, duty);
        CHECK(recovery.motion.imu_fallback);
        const auto done = defend.step(duration, INF_VALUE, false, 32U);
        checkZero(done, fsm::Intent::NONE);
        CHECK(done.motion.status == motion::Status::DONE);
        checkNoTimeouts(done);
    }
}

TEST_CASE("B10 IMU loss captures last remaining angle and recovery cannot retarget it") {
    fsm::DefendTurn defend;
    CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
    checkActive(defend.step(100000U, 45.0F, true, 16U));
    checkActive(defend.step(150000U, NAN_VALUE, false, 16U));
    checkActive(defend.step(239999U, 90.0F, true, 16U));
    const auto done = defend.step(240000U, 0.0F, true, 16U);
    checkZero(done, fsm::Intent::NONE);
    CHECK(done.motion.status == motion::Status::DONE);
    CHECK(done.motion.imu_fallback);
    checkNoTimeouts(done);
}

TEST_CASE("B10 late IMU fallback remains bounded by the original700ms turn timeout") {
    fsm::DefendTurn defend;
    CHECK(defend.start(0U, 0.0F, 135.0F, true, true));
    checkActive(defend.step(599999U, 0.0F, true, 64U));
    checkActive(defend.step(600000U, NAN_VALUE, false, 64U));
    checkActive(defend.step(699999U, NAN_VALUE, false, 64U));
    const auto result = defend.step(700000U, NAN_VALUE, false, 64U);
    checkZero(result, fsm::Intent::NONE);
    CHECK(result.motion.status == motion::Status::TIMED_OUT);
    CHECK(result.turn_timed_out);
    CHECK(result.motion.imu_fallback);
    CHECK_FALSE(result.defend_timed_out);
}

TEST_CASE("B10 nonfinite healthy heading preserves B7 invalid zero motion") {
    for (float heading : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        fsm::DefendTurn defend;
        CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
        const auto result = defend.step(1000U, heading, true, 16U);
        CHECK(result.motion.status == motion::Status::INVALID);
        CHECK(result.motion.duty_l == 0.0F);
        CHECK(result.motion.duty_r == 0.0F);
        checkNoTimeouts(result);
        const auto later = defend.step(2000U, 0.0F, true, 16U);
        CHECK(later.motion.duty_l == 0.0F);
        CHECK(later.motion.duty_r == 0.0F);
    }
}

TEST_CASE("B10 a1kHz timeline crosses micros wrap with exactly two timeout pulses") {
    fsm::DefendTurn defend;
    const std::uint32_t start = 0xFFFF0000U;
    CHECK(defend.start(start, 0.0F, 90.0F, true, true));
    unsigned turn_pulses = 0U;
    unsigned defend_pulses = 0U;
    for (std::uint32_t tick = 0U; tick <= 900U; ++tick) {
        const auto result = defend.step(start + tick * 1000U, 0.0F, true, 16U);
        turn_pulses += result.turn_timed_out ? 1U : 0U;
        defend_pulses += result.defend_timed_out ? 1U : 0U;
        if (tick < 700U) checkActive(result);
        else checkZero(result, tick < 800U ? fsm::Intent::NONE : fsm::Intent::SEARCH);
    }
    CHECK(turn_pulses == 1U);
    CHECK(defend_pulses == 1U);
}

TEST_CASE("B10 delayed and nearly full legal micros gaps cannot miss state expiry") {
    for (std::uint32_t elapsed : {800000U, 800001U, 2000000U, 0xFFFFFFFFU}) {
        fsm::DefendTurn defend;
        CHECK(defend.start(4321U, 0.0F, 90.0F, true, true));
        const auto result = defend.step(4321U + elapsed, 0.0F, true, 16U);
        checkZero(result, fsm::Intent::SEARCH);
        CHECK(result.defend_timed_out);
        const auto latched = defend.step(4321U + elapsed + 1U, 0.0F, true, 16U);
        checkZero(latched, fsm::Intent::SEARCH);
        checkNoTimeouts(latched);
    }
}

TEST_CASE("B10 reset and restart discard old capture intents and deadline pulses") {
    fsm::DefendTurn defend;
    CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
    CHECK(defend.step(800000U, 0.0F, true, 16U).defend_timed_out);
    defend.reset();
    const auto idle = defend.step(900000U, NAN_VALUE, true, 0x7FU);
    checkZero(idle, fsm::Intent::NONE);
    CHECK(idle.motion.status == motion::Status::IDLE);
    CHECK(defend.start(1000000U, 30.0F, -90.0F, true, true));
    checkActive(defend.step(1000000U, 30.0F, true, 8U), -0.80F);
    CHECK_FALSE(defend.start(1001000U, 0.0F, -180.0F, true, true));
    checkZero(defend.step(1002000U, 30.0F, true, 8U), fsm::Intent::INVALID);
    CHECK(defend.start(2000000U, 0.0F, 90.0F, true, true));
    checkActive(defend.step(2000000U, 0.0F, true, 16U));
    CHECK(defend.step(2700000U, 0.0F, true, 16U).turn_timed_out);
}

TEST_CASE("B10 ten thousand fixed seed mirrored captures keep finite bounded requests") {
    std::uint32_t seed = 0xB10D2026U;
    for (std::size_t sample = 0U; sample < 10000U; ++sample) {
        const auto start = randomValue(seed);
        const float heading = static_cast<float>(randomValue(seed) % 2881U) - 1440.0F;
        const float bearing = (randomValue(seed) & 1U) != 0U ? 90.0F : 135.0F;
        const float progress = static_cast<float>(randomValue(seed) % 151U);
        const auto elapsed = randomValue(seed) % 800002U;
        const auto mask = static_cast<std::uint8_t>((randomValue(seed) >> 16U) & 0x7FU);
        const bool imu_ok = (randomValue(seed) & 1U) != 0U;
        fsm::DefendTurn right;
        fsm::DefendTurn left;
        CHECK(right.start(start, heading, bearing, true, imu_ok));
        CHECK(left.start(start, -heading, -bearing, true, imu_ok));
        const auto right_result = right.step(start + elapsed, heading + progress, imu_ok, mask);
        const auto left_result = left.step(start + elapsed, -heading - progress, imu_ok,
                                           mirrorMask(mask));
        checkMirrored(right_result, left_result);
    }
}

TEST_CASE("B10 B6 PIVOT composition caps low voltage and brakes on a front exit") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        fsm::DefendTurn defend;
        governor::Governor governor;
        CHECK(defend.start(0U, 0.0F, 90.0F, true, true));
        const auto start = governor.step(0U, pivotRequest(defend.step(0U, 0.0F, true, 16U), voltage));
        CHECK(start.duty_l == 0.0F);
        CHECK(start.duty_r == 0.0F);
        const auto ramp = governor.step(1000U,
            pivotRequest(defend.step(1000U, 0.0F, true, 16U), voltage));
        CHECK(ramp.duty_l == doctest::Approx(0.02F));
        CHECK(ramp.duty_r == doctest::Approx(-0.02F));
        const auto settled = governor.step(100000U,
            pivotRequest(defend.step(100000U, 0.0F, true, 16U), voltage));
        const float expected = std::min(0.80F, 0.80F * 11.1F / voltage);
        CHECK(settled.valid);
        CHECK(settled.duty_l == doctest::Approx(expected));
        CHECK(settled.duty_r == doctest::Approx(-expected));
        const auto acquired = defend.step(100001U, 0.0F, true, 2U);
        checkZero(acquired, fsm::Intent::PERCEPTION);
        const auto stopped = governor.step(100001U, pivotRequest(acquired, voltage));
        CHECK(stopped.duty_l == 0.0F);
        CHECK(stopped.duty_r == 0.0F);
    }
}
