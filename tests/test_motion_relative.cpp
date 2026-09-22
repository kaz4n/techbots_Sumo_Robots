// Checks B7 relative turn capture without losing the actual float yaw observation.
// Protects strict tolerance and the positive-180 tie across coordinate conversion.
// Independent host tests cover canonical inputs, fallback, wrap and absolute-mode restart.
#include "doctest.h"
#include "core/motion.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();

void checkActive(const motion::Result& result, float left, float right) {
    CHECK(result.status == motion::Status::ACTIVE);
    CHECK(result.duty_l == doctest::Approx(left));
    CHECK(result.duty_r == doctest::Approx(right));
}

void checkZero(const motion::Result& result, motion::Status status) {
    CHECK(result.status == status);
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
}

void primeFallback(motion::Turn& turn, bool relative, bool initially_missing) {
    if (relative) CHECK(turn.startRelative(0U, 0.0F, 90.0F, 0.8F, !initially_missing));
    else CHECK(turn.start(0U, 0.0F, 90.0F, 0.8F, !initially_missing));
    if (initially_missing) CHECK(turn.step(1U, NAN_YAW, false).imu_fallback);
    else {
        turn.step(1000U, 30.0F, true);
        CHECK(turn.step(2000U, NAN_YAW, false).imu_fallback);
    }
}
} // namespace

TEST_CASE("B7 startRelative accepts canonical negative-to-positive bearings and rejects negative 180") {
    for (const float relative : {std::nextafter(-180.0F, 0.0F), -90.0F, 0.0F, 90.0F, 180.0F}) {
        motion::Turn turn;
        CHECK(turn.startRelative(0U, 30.0F, relative, 0.8F, true));
        const auto result = turn.step(0U, 30.0F, true);
        if (relative == 0.0F) checkZero(result, motion::Status::DONE);
        else checkActive(result, relative > 0.0F ? 0.8F : -0.8F, relative > 0.0F ? -0.8F : 0.8F);
    }
    for (const float relative : {-180.0F, -181.0F, std::nextafter(180.0F, 181.0F),
                                 NAN_YAW, std::numeric_limits<float>::infinity(),
                                 -std::numeric_limits<float>::infinity()}) {
        motion::Turn turn;
        CHECK_FALSE(turn.startRelative(0U, 0.0F, relative, 0.8F, true));
        checkZero(turn.step(1U, 0.0F, true), motion::Status::INVALID);
    }
}

TEST_CASE("B7 startRelative retains finite-origin duty and healthy-yaw validation") {
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        for (const bool imu : {false, true}) {
            motion::Turn turn;
            CHECK_FALSE(turn.startRelative(0U, bad, 90.0F, 0.8F, imu));
            checkZero(turn.step(1U, 0.0F, true), motion::Status::INVALID);
        }
    }
    for (const float duty : {-1.0F, std::nextafter(0.25F, 0.0F),
                             std::nextafter(1.0F, 2.0F), NAN_YAW,
                             std::numeric_limits<float>::infinity()}) {
        motion::Turn turn;
        CHECK_FALSE(turn.startRelative(0U, 0.0F, 90.0F, duty, true));
        checkZero(turn.step(0U, 0.0F, true), motion::Status::INVALID);
    }
    for (const float duty : {0.25F, 0.8F, 1.0F}) {
        motion::Turn turn;
        CHECK(turn.startRelative(0U, 0.0F, 90.0F, duty, true));
        checkActive(turn.step(0U, 0.0F, true), duty, -duty);
        checkZero(turn.step(1U, NAN_YAW, true), motion::Status::INVALID);
        CHECK(turn.startRelative(2U, 0.0F, 90.0F, duty, false));
        const auto fallback = turn.step(3U, NAN_YAW, false);
        checkActive(fallback, duty, -duty);
        CHECK(fallback.imu_fallback);
    }
}

TEST_CASE("B7 relative positive 180 tie stays RIGHT at tiny ordinary and extreme actual origins") {
    for (const float origin : {-0.000001F, 0.000001F, 0.0F, 30.0F, -170.0F,
                               36000000.0F, std::numeric_limits<float>::max(),
                               -std::numeric_limits<float>::max()}) {
        motion::Turn turn;
        CHECK(turn.startRelative(0U, origin, 180.0F, 0.8F, true));
        checkActive(turn.step(0U, origin, true), 0.8F, -0.8F);
        checkActive(turn.step(1U, origin, true), 0.8F, -0.8F);
    }
}

TEST_CASE("B7 relative coordinates preserve adjacent strict five degree samples around zero target") {
    for (const float origin : {-90.0F, 90.0F}) {
        for (const float magnitude : {std::nextafter(5.0F, 0.0F), 5.0F,
                                      std::nextafter(5.0F, 6.0F)}) {
            for (const float sign : {-1.0F, 1.0F}) {
                motion::Turn turn;
                CHECK(turn.startRelative(0U, origin, -origin, 0.8F, true));
                const auto result = turn.step(1U, sign * magnitude, true);
                if (magnitude < 5.0F) checkZero(result, motion::Status::DONE);
                else checkActive(result, -sign * 0.25F, sign * 0.25F);
            }
        }
    }
}

TEST_CASE("B7 relative initial fallback keeps full angle timing after IMU recovery") {
    for (const float sign : {-1.0F, 1.0F}) {
        motion::Turn turn;
        CHECK(turn.startRelative(0U, 10.0F, sign * 60.0F, 0.8F, false));
        auto result = turn.step(1U, 10.0F + sign * 60.0F, true);
        checkActive(result, sign * 0.8F, -sign * 0.8F);
        CHECK(result.imu_fallback);
        result = turn.step(119999U, NAN_YAW, false);
        checkActive(result, sign * 0.8F, -sign * 0.8F);
        checkZero(turn.step(120000U, NAN_YAW, false), motion::Status::DONE);
        checkZero(turn.step(120001U, 0.0F, true), motion::Status::DONE);
    }
}

TEST_CASE("B7 relative mid-turn loss uses remaining error and original timeout wins a deadline tie") {
    motion::Turn turn;
    CHECK(turn.startRelative(0U, 90.0F, -90.0F, 0.8F, true));
    turn.step(1000U, 45.0F, true);
    CHECK(turn.step(2000U, NAN_YAW, false).imu_fallback);
    auto result = turn.step(91999U, 0.0F, true);
    checkActive(result, -0.8F, 0.8F);
    CHECK(result.imu_fallback);
    checkZero(turn.step(92000U, 0.0F, true), motion::Status::DONE);
    CHECK(turn.startRelative(0U, 0.0F, 180.0F, 0.8F, true));
    CHECK(turn.step(699000U, NAN_YAW, false).imu_fallback);
    checkActive(turn.step(699999U, 180.0F, true), 0.8F, -0.8F);
    checkZero(turn.step(700000U, 180.0F, true), motion::Status::TIMED_OUT);
    CHECK(turn.startRelative(0U, 0.0F, 90.0F, 0.8F, true));
    checkZero(turn.step(699999U, 90.0F, true), motion::Status::DONE);
    CHECK(turn.startRelative(0U, 0.0F, 90.0F, 0.8F, true));
    checkZero(turn.step(700000U, 90.0F, true), motion::Status::TIMED_OUT);
}

TEST_CASE("B7 relative fallback and timeout boundaries survive unsigned micros wrap") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 10U;
    motion::Turn turn;
    CHECK(turn.startRelative(start, 350.0F, 60.0F, 0.8F, false));
    checkActive(turn.step(start + 119999U, NAN_YAW, false), 0.8F, -0.8F);
    checkZero(turn.step(start + 120000U, NAN_YAW, false), motion::Status::DONE);
    CHECK(turn.startRelative(start, 350.0F, 60.0F, 0.8F, true));
    checkActive(turn.step(start + 699999U, 350.0F, true), 0.8F, -0.8F);
    checkZero(turn.step(start + 700000U, 350.0F, true), motion::Status::TIMED_OUT);
}

TEST_CASE("B7 ordinary absolute start and reset clear relative coordinates and fallback mode") {
    motion::Turn turn;
    CHECK(turn.startRelative(0U, 90.0F, -90.0F, 0.8F, false));
    CHECK(turn.step(1U, NAN_YAW, false).imu_fallback);
    CHECK(turn.start(1000U, 0.0F, 90.0F, 0.8F, true));
    auto result = turn.step(1000U, 0.0F, true);
    checkActive(result, 0.8F, -0.8F);
    CHECK_FALSE(result.imu_fallback);
    checkZero(turn.step(1001U, 90.0F, true), motion::Status::DONE);
    CHECK(turn.startRelative(2000U, 90.0F, -90.0F, 0.8F, true));
    checkActive(turn.step(2000U, 90.0F, true), -0.8F, 0.8F);
    turn.reset();
    checkZero(turn.step(2001U, 0.0F, true), motion::Status::IDLE);
    CHECK(turn.start(3000U, 350.0F, 10.0F, 0.8F, true));
    checkActive(turn.step(3000U, 350.0F, true), 0.4F, -0.4F);
    checkZero(turn.step(3001U, 10.0F, true), motion::Status::DONE);
}

TEST_CASE("B7 healthy nonfinite yaw invalidates latched fallback while the exact deadline still wins") {
    for (const bool relative : {false, true}) {
        for (const bool initial : {false, true}) {
            for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                                    -std::numeric_limits<float>::infinity()}) {
                motion::Turn turn;
                primeFallback(turn, relative, initial);
                checkZero(turn.step(3000U, bad, true), motion::Status::INVALID);
                checkZero(turn.step(3001U, 90.0F, true), motion::Status::INVALID);
                checkZero(turn.step(700000U, bad, true), motion::Status::INVALID);
                primeFallback(turn, relative, initial);
                checkZero(turn.step(700000U, bad, true), motion::Status::TIMED_OUT);
                checkZero(turn.step(700001U, 90.0F, true), motion::Status::TIMED_OUT);
            }
        }
    }
}
