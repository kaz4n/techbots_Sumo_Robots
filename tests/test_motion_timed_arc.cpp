// Checks the B7/D-037 duration-only arc contract without a heading dependency.
// Keeps requested wheel ratios and timing separate from governor and motor permission.
// Spec-derived host tests cover validation, exact deadlines, wrap and mirrored requests.
#include "doctest.h"
#include "config.h"
#include "core/governor.h"
#include "core/motion.h"
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t MAX_DURATION_MS = 4294967U;
constexpr std::uint32_t MAX_DURATION_US = 4294967000U;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();

void checkZero(const motion::Result& result, motion::Status status) {
    CHECK(result.status == status);
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
    CHECK_FALSE(result.imu_fallback);
}

void checkActive(const motion::Result& result, motion::Direction direction,
                 float duty = 0.80F, float ratio = 0.40F) {
    CHECK(result.status == motion::Status::ACTIVE);
    const float inner = static_cast<float>(static_cast<double>(duty) * ratio);
    const bool right = direction == motion::Direction::RIGHT;
    CHECK(result.duty_l == (right ? duty : inner));
    CHECK(result.duty_r == (right ? inner : duty));
    CHECK_FALSE(result.imu_fallback);
}

void checkBounded(const motion::Result& result) {
    CHECK(std::isfinite(result.duty_l));
    CHECK(std::isfinite(result.duty_r));
    CHECK(result.duty_l >= 0.0F);
    CHECK(result.duty_l <= 1.0F);
    CHECK(result.duty_r >= 0.0F);
    CHECK(result.duty_r <= 1.0F);
    CHECK_FALSE(result.imu_fallback);
}

std::uint32_t randomValue(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}

governor::Request arcRequest(const motion::Result& motion, float voltage) {
    governor::Request request;
    request.duty_l = motion.duty_l;
    request.duty_r = motion.duty_r;
    request.vbat_v = voltage;
    request.profile = governor::Profile::REFLANK_TURN;
    request.inhibited = false;
    return request;
}

void checkPropertyResult(const motion::Result& result, motion::Direction direction,
                         float duty, float ratio, bool active) {
    checkBounded(result);
    if (active) checkActive(result, direction, duty, ratio);
    else checkZero(result, motion::Status::DONE);
}
} // namespace

TEST_CASE("B7 D037 timed arc starts inert and a timestamp alone cannot activate it") {
    motion::TimedArc arc;
    for (std::uint32_t time : {0U, 400000U, 0xFFFFFFFFU, 0U}) {
        checkZero(arc.step(time), motion::Status::IDLE);
    }
}

TEST_CASE("B7 D037 all256 direction encodings admit exactly LEFT and RIGHT") {
    for (std::uint32_t code = 0U; code < 256U; ++code) {
        const auto direction = static_cast<motion::Direction>(code);
        motion::TimedArc arc;
        const bool started = arc.start(0U, direction, 0.40F, 0.80F, 400U);
        CHECK(started == (code < 2U));
        if (code < 2U) checkActive(arc.step(0U), direction);
        else {
            checkZero(arc.step(0U), motion::Status::INVALID);
            checkZero(arc.step(900000U), motion::Status::INVALID);
        }
    }
}

TEST_CASE("B7 D037 invalid duty and ratio reject finite extremes nonfinite and adjacent limits") {
    const float invalid[] = {
        -std::numeric_limits<float>::denorm_min(), -1.0F,
        std::nextafter(1.0F, INF_VALUE), std::numeric_limits<float>::max(),
        -std::numeric_limits<float>::max(), NAN_VALUE, INF_VALUE, -INF_VALUE
    };
    for (auto direction : {motion::Direction::LEFT, motion::Direction::RIGHT}) {
        for (float value : invalid) {
            motion::TimedArc duty;
            CHECK_FALSE(duty.start(0U, direction, 0.40F, value, 400U));
            checkZero(duty.step(0U), motion::Status::INVALID);
            checkZero(duty.step(400000U), motion::Status::INVALID);
            motion::TimedArc ratio;
            CHECK_FALSE(ratio.start(0U, direction, value, 0.80F, 400U));
            checkZero(ratio.step(0U), motion::Status::INVALID);
            checkZero(ratio.step(400000U), motion::Status::INVALID);
        }
    }
}

TEST_CASE("B7 D037 zero duration still rejects invalid capture arguments") {
    motion::TimedArc arc;
    CHECK_FALSE(arc.start(0U, static_cast<motion::Direction>(255U), 0.40F, 0.80F, 0U));
    checkZero(arc.step(0U), motion::Status::INVALID);
    CHECK_FALSE(arc.start(0U, motion::Direction::LEFT, NAN_VALUE, 0.80F, 0U));
    checkZero(arc.step(0U), motion::Status::INVALID);
    CHECK_FALSE(arc.start(0U, motion::Direction::RIGHT, 0.40F, INF_VALUE, 0U));
    checkZero(arc.step(0U), motion::Status::INVALID);
}

TEST_CASE("B7 D037 closed unit intervals accept zero one and finite adjacent values") {
    const float valid[] = {
        0.0F, -0.0F, std::numeric_limits<float>::denorm_min(),
        std::numeric_limits<float>::min(), std::nextafter(1.0F, 0.0F), 1.0F
    };
    for (auto direction : {motion::Direction::LEFT, motion::Direction::RIGHT}) {
        for (float duty : valid) {
            for (float ratio : valid) {
                motion::TimedArc arc;
                CHECK(arc.start(0U, direction, ratio, duty, 400U));
                const auto result = arc.step(0U);
                checkActive(result, direction, duty, ratio);
                checkBounded(result);
            }
        }
    }
}

TEST_CASE("B7 D037 zero duration completes immediately in both directions") {
    for (auto direction : {motion::Direction::LEFT, motion::Direction::RIGHT}) {
        motion::TimedArc arc;
        CHECK(arc.start(123456U, direction, 0.40F, 0.80F, 0U));
        checkZero(arc.step(123456U), motion::Status::DONE);
        checkZero(arc.step(123457U), motion::Status::DONE);
        checkZero(arc.step(123456U + 0xFFFFFFFFU), motion::Status::DONE);
    }
}

TEST_CASE("B7 D037 duration conversion accepts the literal maximum and rejects overflow") {
    CHECK(std::numeric_limits<std::uint32_t>::max() / 1000U == MAX_DURATION_MS);
    motion::TimedArc maximum;
    CHECK(maximum.start(0U, motion::Direction::RIGHT, 0.40F, 0.80F, MAX_DURATION_MS));
    checkActive(maximum.step(MAX_DURATION_US - 1U), motion::Direction::RIGHT);
    checkZero(maximum.step(MAX_DURATION_US), motion::Status::DONE);
    for (std::uint32_t duration : {4294968U, 0xFFFFFFFFU}) {
        motion::TimedArc invalid;
        CHECK_FALSE(invalid.start(0U, motion::Direction::RIGHT, 0.40F, 0.80F, duration));
        checkZero(invalid.step(0U), motion::Status::INVALID);
        checkZero(invalid.step(1000000U), motion::Status::INVALID);
    }
}

TEST_CASE("B7 D037 right and left arcs exchange outer and inner forward requests") {
    motion::TimedArc right;
    motion::TimedArc left;
    CHECK(right.start(0U, motion::Direction::RIGHT, 0.40F, 0.80F, 400U));
    CHECK(left.start(0U, motion::Direction::LEFT, 0.40F, 0.80F, 400U));
    const auto r = right.step(1000U);
    const auto l = left.step(1000U);
    checkActive(r, motion::Direction::RIGHT);
    checkActive(l, motion::Direction::LEFT);
    CHECK(r.duty_l == l.duty_r);
    CHECK(r.duty_r == l.duty_l);
    CHECK(r.duty_r == doctest::Approx(0.32F));
}

TEST_CASE("B7 D037 zero duty stays ACTIVE and endpoint ratios select stopped or equal inner wheel") {
    for (auto direction : {motion::Direction::LEFT, motion::Direction::RIGHT}) {
        for (float ratio : {0.0F, 1.0F}) {
            motion::TimedArc arc;
            CHECK(arc.start(0U, direction, ratio, 0.80F, 400U));
            checkActive(arc.step(399999U), direction, 0.80F, ratio);
            checkZero(arc.step(400000U), motion::Status::DONE);
            CHECK(arc.start(500000U, direction, ratio, 0.0F, 400U));
            checkActive(arc.step(500000U), direction, 0.0F, ratio);
            checkActive(arc.step(899999U), direction, 0.0F, ratio);
            checkZero(arc.step(900000U), motion::Status::DONE);
        }
    }
}

TEST_CASE("B7 D037 exact400ms deadline includes adjacent microseconds and milliseconds") {
    for (std::uint32_t elapsed : {399000U, 399999U, 400000U, 400001U, 401000U}) {
        for (std::uint32_t start : {7000U, 0xFFFF0000U}) {
            motion::TimedArc arc;
            CHECK(arc.start(start, motion::Direction::LEFT, 0.40F, 0.80F, 400U));
            const auto result = arc.step(start + elapsed);
            if (elapsed < 400000U) checkActive(result, motion::Direction::LEFT);
            else checkZero(result, motion::Status::DONE);
        }
    }
}

TEST_CASE("B7 D037 a1kHz timeline needs neither heading nor IMU to finish its400ms arc") {
    CHECK(config::TURN_DUTY == 0.80F);
    CHECK(config::REFLANK_ARC_RATIO == 0.40F);
    CHECK(config::REFLANK_ARC_MS == 400U);
    motion::TimedArc arc;
    CHECK(arc.start(1900U, motion::Direction::LEFT, config::REFLANK_ARC_RATIO,
                    config::TURN_DUTY, config::REFLANK_ARC_MS));
    for (std::uint32_t tick = 0U; tick <= 401U; ++tick) {
        const auto result = arc.step(1900U + tick * 1000U);
        if (tick < 400U) checkActive(result, motion::Direction::LEFT);
        else checkZero(result, motion::Status::DONE);
    }
}

TEST_CASE("B7 D037 duplicate timestamps do not consume time or change arc requests") {
    motion::TimedArc arc;
    CHECK(arc.start(999U, motion::Direction::RIGHT, 0.40F, 0.80F, 1U));
    for (std::size_t duplicate = 0U; duplicate < 2000U; ++duplicate) {
        checkActive(arc.step(999U), motion::Direction::RIGHT);
    }
    checkActive(arc.step(1998U), motion::Direction::RIGHT);
    checkZero(arc.step(1999U), motion::Status::DONE);
}

TEST_CASE("B7 D037 delayed first observation never backdates a new active interval") {
    for (std::uint32_t elapsed : {400000U, 900000U, 0xFFFFFFFFU}) {
        motion::TimedArc arc;
        CHECK(arc.start(123456U, motion::Direction::RIGHT, 0.40F, 0.80F, 400U));
        checkZero(arc.step(123456U + elapsed), motion::Status::DONE);
    }
}

TEST_CASE("B7 D037 cumulative legal gaps preserve longest duration across a start relative wrap") {
    for (std::uint32_t start : {0U, 1000U, 0xFFFFFF00U}) {
        motion::TimedArc arc;
        CHECK(arc.start(start, motion::Direction::LEFT, 0.40F, 0.80F, MAX_DURATION_MS));
        const std::uint32_t last_active = start + MAX_DURATION_US - 1U;
        checkActive(arc.step(last_active), motion::Direction::LEFT);
        const std::uint32_t after_deadline = last_active + 1000U;
        checkZero(arc.step(after_deadline), motion::Status::DONE);
        checkZero(arc.step(after_deadline + 1U), motion::Status::DONE);
    }
}

TEST_CASE("B7 D037 terminal DONE never resurrects during several later clock wraps") {
    motion::TimedArc arc;
    CHECK(arc.start(0U, motion::Direction::RIGHT, 0.40F, 0.80F, 400U));
    std::uint32_t now = 400000U;
    checkZero(arc.step(now), motion::Status::DONE);
    for (std::size_t wrap = 0U; wrap < 8U; ++wrap) {
        now += 0xFFFFFFFFU;
        checkZero(arc.step(now), motion::Status::DONE);
    }
}

TEST_CASE("B7 D037 reset and successful restart discard prior terminal or active parameters") {
    motion::TimedArc arc;
    CHECK(arc.start(0U, motion::Direction::RIGHT, 0.40F, 0.80F, 400U));
    checkActive(arc.step(1000U), motion::Direction::RIGHT);
    arc.reset();
    checkZero(arc.step(2000U), motion::Status::IDLE);
    CHECK(arc.start(3000U, motion::Direction::LEFT, 0.25F, 0.60F, 1U));
    checkActive(arc.step(3999U), motion::Direction::LEFT, 0.60F, 0.25F);
    checkZero(arc.step(4000U), motion::Status::DONE);
    CHECK(arc.start(5000U, motion::Direction::RIGHT, 1.0F, 1.0F, 2U));
    checkActive(arc.step(5000U), motion::Direction::RIGHT, 1.0F, 1.0F);
    CHECK(arc.start(6000U, motion::Direction::LEFT, 0.0F, 0.50F, 1U));
    checkActive(arc.step(6000U), motion::Direction::LEFT, 0.50F, 0.0F);
    checkZero(arc.step(7000U), motion::Status::DONE);
}

TEST_CASE("B7 D037 invalid restart clears old nonzero motion and can later recover") {
    motion::TimedArc arc;
    CHECK(arc.start(0U, motion::Direction::RIGHT, 0.40F, 0.80F, 400U));
    checkActive(arc.step(1000U), motion::Direction::RIGHT);
    CHECK_FALSE(arc.start(2000U, motion::Direction::LEFT, NAN_VALUE, 0.80F, 400U));
    checkZero(arc.step(2000U), motion::Status::INVALID);
    checkZero(arc.step(900000U), motion::Status::INVALID);
    CHECK(arc.start(1000000U, motion::Direction::LEFT, 0.40F, 0.80F, 400U));
    checkActive(arc.step(1000000U), motion::Direction::LEFT);
    arc.reset();
    arc.reset();
    checkZero(arc.step(1001000U), motion::Status::IDLE);
}

TEST_CASE("B7 D037 ten thousand mirrored arcs cover every declared timing and endpoint class") {
    std::uint32_t seed = 0xB7037A11U;
    unsigned duration_counts[5] = {};
    unsigned timing_counts[5] = {};
    unsigned active_count = 0U, done_count = 0U, left_count = 0U, right_count = 0U;
    unsigned zero_duty = 0U, full_duty = 0U, zero_ratio = 0U, full_ratio = 0U;
    for (std::uint32_t sample = 0U; sample < 10000U; ++sample) {
        const auto start = randomValue(seed);
        const std::uint32_t durations[5] = {0U, 1U, 400U, randomValue(seed) % 5000U + 1U, MAX_DURATION_MS};
        const auto kind = sample % 5U;
        const auto duration_ms = durations[kind];
        const auto duration_us = duration_ms * 1000U;
        const auto timing = (sample / 5U) % 5U;
        const std::uint32_t elapsed_options[5] = {
            0U, duration_us == 0U ? 0U : duration_us - 1U,
            duration_us, duration_us + 1U, 0xFFFFFFFFU
        };
        const auto elapsed = elapsed_options[timing];
        const auto duty_class = (sample / 25U) % 10U;
        const auto ratio_class = (sample / 250U) % 10U;
        const float duty = duty_class == 0U ? 0.0F : duty_class == 1U ? 1.0F :
            static_cast<float>(randomValue(seed) % 999U + 1U) / 1000.0F;
        const float ratio = ratio_class == 2U ? 0.0F : ratio_class == 3U ? 1.0F :
            static_cast<float>(randomValue(seed) % 999U + 1U) / 1000.0F;
        const auto direction = sample % 2U == 0U ? motion::Direction::LEFT : motion::Direction::RIGHT;
        const auto opposite = direction == motion::Direction::LEFT ? motion::Direction::RIGHT : motion::Direction::LEFT;
        motion::TimedArc original, mirror;
        CHECK(original.start(start, direction, ratio, duty, duration_ms));
        CHECK(mirror.start(start, opposite, ratio, duty, duration_ms));
        const auto result = original.step(start + elapsed);
        const auto mirrored = mirror.step(start + elapsed);
        const bool active = elapsed < duration_us;
        checkPropertyResult(result, direction, duty, ratio, active);
        checkPropertyResult(mirrored, opposite, duty, ratio, active);
        CHECK(result.duty_l == mirrored.duty_r);
        CHECK(result.duty_r == mirrored.duty_l);
        ++duration_counts[kind]; ++timing_counts[timing];
        active ? ++active_count : ++done_count;
        direction == motion::Direction::LEFT ? ++left_count : ++right_count;
        if (duty == 0.0F) ++zero_duty;
        if (duty == 1.0F) ++full_duty;
        if (ratio == 0.0F) ++zero_ratio;
        if (ratio == 1.0F) ++full_ratio;
    }
    for (auto count : duration_counts) CHECK(count == 2000U);
    for (auto count : timing_counts) CHECK(count == 2000U);
    CHECK(active_count == 3200U); CHECK(done_count == 6800U);
    CHECK(left_count == 5000U); CHECK(right_count == 5000U);
    CHECK(zero_duty == 1000U); CHECK(full_duty == 1000U);
    CHECK(zero_ratio == 1000U); CHECK(full_ratio == 1000U);
}

TEST_CASE("B7 B11 D023 D037 governor voltage changes duty but not the400ms arc deadline") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        for (auto direction : {motion::Direction::LEFT, motion::Direction::RIGHT}) {
            motion::TimedArc arc;
            governor::Governor governor;
            CHECK(arc.start(0U, direction, 0.40F, 0.80F, 400U));
            for (std::uint32_t tick = 0U; tick <= 401U; ++tick) {
                const auto request = arc.step(tick * 1000U);
                const auto output = governor.step(tick * 1000U, arcRequest(request, voltage));
                CHECK(output.valid);
                CHECK(output.duty_l >= 0.0F); CHECK(output.duty_l <= 0.800001F);
                CHECK(output.duty_r >= 0.0F); CHECK(output.duty_r <= 0.800001F);
                if (tick < 400U) checkActive(request, direction);
                else checkZero(request, motion::Status::DONE);
                if (tick == 0U || tick >= 400U) {
                    CHECK(output.duty_l == 0.0F); CHECK(output.duty_r == 0.0F);
                } else if (tick >= 100U) {
                    const float outer = std::min(0.80F, 0.80F * 11.1F / voltage);
                    const float inner = std::min(0.80F, 0.80F * 0.40F * 11.1F / voltage);
                    CHECK(output.duty_l == doctest::Approx(direction == motion::Direction::RIGHT ? outer : inner));
                    CHECK(output.duty_r == doctest::Approx(direction == motion::Direction::RIGHT ? inner : outer));
                }
            }
        }
    }
}
