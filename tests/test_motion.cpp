// Checks B7 motion requests against B0/B6 and approved D-022/D-023 contracts.
// Keeps expected behavior independent of implementation and real motor permission.
// Spec-only doctest cases exercise boundaries, faults, symmetry and governor output.
#include "doctest.h"
#include "config.h"
#include "core/governor.h"
#include "core/motion.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t MAX_MS = std::numeric_limits<std::uint32_t>::max() / 1000U;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();

void checkZero(const motion::Result& result, motion::Status status) {
    CHECK(result.status == status);
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
}

void checkActive(const motion::Result& result, float left, float right) {
    CHECK(result.status == motion::Status::ACTIVE);
    CHECK(result.duty_l == doctest::Approx(left));
    CHECK(result.duty_r == doctest::Approx(right));
}

void checkBounded(const motion::Result& result) {
    CHECK(std::isfinite(result.duty_l));
    CHECK(std::isfinite(result.duty_r));
    CHECK(std::fabs(result.duty_l) <= 1.0F);
    CHECK(std::fabs(result.duty_r) <= 1.0F);
    if (result.status != motion::Status::ACTIVE) {
        CHECK(result.duty_l == 0.0F);
        CHECK(result.duty_r == 0.0F);
    }
}

void checkMirror(const motion::Result& right, const motion::Result& left) {
    CHECK(right.status == left.status);
    CHECK(right.imu_fallback == left.imu_fallback);
    CHECK(right.duty_l == doctest::Approx(left.duty_r));
    CHECK(right.duty_r == doctest::Approx(left.duty_l));
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}

governor::Request governed(const motion::Result& result, float voltage,
                           governor::Profile profile) {
    governor::Request request;
    request.duty_l = result.duty_l;
    request.duty_r = result.duty_r;
    request.vbat_v = voltage;
    request.profile = profile;
    request.inhibited = false;
    return request;
}
} // namespace

TEST_CASE("B7 motion defaults are IDLE with zero requests") {
    const motion::Result result;
    checkZero(result, motion::Status::IDLE);
    CHECK_FALSE(result.imu_fallback);
    motion::Turn turn;
    motion::Straight straight;
    motion::Arc arc;
    motion::Brake brake;
    checkZero(turn.step(1000U, NAN_VALUE, true), motion::Status::IDLE);
    checkZero(straight.step(1000U, NAN_VALUE, true), motion::Status::IDLE);
    checkZero(arc.step(1000U, NAN_VALUE, true), motion::Status::IDLE);
    checkZero(brake.step(1000U), motion::Status::IDLE);
}

TEST_CASE("B7 turn clockwise and counterclockwise use gain minimum and maximum") {
    const float errors[] = {5.0F, 10.0F, 20.0F, 40.0F, 90.0F};
    const float duties[] = {0.25F, 0.25F, 0.40F, 0.80F, 0.80F};
    for (unsigned index = 0U; index < 5U; ++index) {
        for (float sign : {-1.0F, 1.0F}) {
            CAPTURE(index);
            CAPTURE(sign);
            motion::Turn turn;
            CHECK(turn.start(1000U, 0.0F, sign * errors[index], 0.80F, true));
            const auto result = turn.step(1000U, 0.0F, true);
            checkActive(result, sign * duties[index], -sign * duties[index]);
            CHECK_FALSE(result.imu_fallback);
        }
    }
}

TEST_CASE("B7 turn completion uses strict five degree tolerance") {
    for (float sign : {-1.0F, 1.0F}) {
        motion::Turn turn;
        CHECK(turn.start(0U, 0.0F, sign * 10.0F, 0.8F, true));
        checkActive(turn.step(1000U, sign * 4.999F, true), sign * .25F, -sign * .25F);
        checkActive(turn.step(2000U, sign * 5.0F, true), sign * .25F, -sign * .25F);
        checkZero(turn.step(3000U, sign * 5.001F, true), motion::Status::DONE);
        checkZero(turn.step(4000U, NAN_VALUE, true), motion::Status::DONE);
    }
}

TEST_CASE("B0 B7 turn takes shortest angle across wrap and accumulated yaw") {
    for (float revolutions : {-1080.0F, 0.0F, 1080.0F}) {
        motion::Turn right;
        motion::Turn left;
        CHECK(right.start(0U, revolutions + 170.0F, -170.0F, .8F, true));
        CHECK(left.start(0U, -revolutions - 170.0F, 170.0F, .8F, true));
        checkActive(right.step(0U, revolutions + 170.0F, true), .4F, -.4F);
        checkActive(left.step(0U, -revolutions - 170.0F, true), -.4F, .4F);
    }
    motion::Turn tie;
    CHECK(tie.start(0U, 0.0F, -180.0F, .8F, true));
    checkActive(tie.step(0U, 0.0F, true), .8F, -.8F);
}

TEST_CASE("B7 turn healthy timeout has exact neighbors and wins completion tie") {
    motion::Turn turn;
    CHECK(turn.start(123U, 0.0F, 90.0F, .8F, true));
    checkActive(turn.step(123U + 699000U, 0.0F, true), .8F, -.8F);
    checkActive(turn.step(123U + 699999U, 0.0F, true), .8F, -.8F);
    checkZero(turn.step(123U + 700000U, 90.0F, true), motion::Status::TIMED_OUT);
    checkZero(turn.step(123U + 701000U, 90.0F, true), motion::Status::TIMED_OUT);
}

TEST_CASE("B7 turn initial fallback runs angle times two milliseconds at maximum duty") {
    for (float sign : {-1.0F, 1.0F}) {
        motion::Turn turn;
        CHECK(turn.start(100U, 0.0F, sign * 45.0F, .6F, false));
        const auto initial = turn.step(100U, NAN_VALUE, false);
        checkActive(initial, sign * .6F, -sign * .6F);
        CHECK(initial.imu_fallback);
        checkActive(turn.step(89100U, INF_VALUE, false), sign * .6F, -sign * .6F);
        checkActive(turn.step(90099U, sign * 45.0F, true), sign * .6F, -sign * .6F);
        checkZero(turn.step(90100U, 0.0F, true), motion::Status::DONE);
        checkZero(turn.step(91100U, 0.0F, false), motion::Status::DONE);
    }
}

TEST_CASE("B7 turn loss captures last remaining angle and recovery cannot extend it") {
    motion::Turn turn;
    CHECK(turn.start(0U, 0.0F, 90.0F, .6F, true));
    checkActive(turn.step(20000U, 30.0F, true), .6F, -.6F);
    const auto lost = turn.step(30000U, NAN_VALUE, false);
    checkActive(lost, .6F, -.6F);
    CHECK(lost.imu_fallback);
    const auto recovered = turn.step(100000U, 90.0F, true);
    checkActive(recovered, .6F, -.6F);
    CHECK(recovered.imu_fallback);
    checkActive(turn.step(149000U, -90.0F, true), .6F, -.6F);
    checkActive(turn.step(149999U, INF_VALUE, false), .6F, -.6F);
    checkZero(turn.step(150000U, 0.0F, true), motion::Status::DONE);
    checkZero(turn.step(151000U, 0.0F, true), motion::Status::DONE);
}

TEST_CASE("B7 fallback retains last valid direction after target overshoot") {
    motion::Turn turn;
    CHECK(turn.start(0U, 0.0F, 30.0F, .6F, true));
    checkActive(turn.step(10000U, 40.0F, true), -.25F, .25F);
    checkActive(turn.step(20000U, NAN_VALUE, false), -.6F, .6F);
    checkActive(turn.step(39999U, 0.0F, true), -.6F, .6F);
    checkZero(turn.step(40000U, 30.0F, true), motion::Status::DONE);
}

TEST_CASE("B7 fallback never extends original turn timeout and timeout wins tie") {
    for (std::uint32_t lost_at : {520000U, 650000U}) {
        motion::Turn turn;
        CHECK(turn.start(0U, 0.0F, 90.0F, .8F, true));
        checkActive(turn.step(lost_at, NAN_VALUE, false), .8F, -.8F);
        checkActive(turn.step(699999U, 90.0F, true), .8F, -.8F);
        checkZero(turn.step(700000U, 90.0F, true), motion::Status::TIMED_OUT);
        checkZero(turn.step(701000U, 0.0F, false), motion::Status::TIMED_OUT);
    }
}

TEST_CASE("B0 B7 turn timeout and fallback use unsigned elapsed time through wrap") {
    const std::uint32_t start = std::numeric_limits<std::uint32_t>::max() - 5000U;
    motion::Turn healthy;
    CHECK(healthy.start(start, 0.0F, 90.0F, .8F, true));
    checkActive(healthy.step(start + 699999U, 0.0F, true), .8F, -.8F);
    checkZero(healthy.step(start + 700000U, 0.0F, true), motion::Status::TIMED_OUT);
    motion::Turn fallback;
    CHECK(fallback.start(start, 0.0F, -45.0F, .8F, false));
    checkActive(fallback.step(start + 89999U, NAN_VALUE, false), -.8F, .8F);
    checkZero(fallback.step(start + 90000U, NAN_VALUE, false), motion::Status::DONE);
}

TEST_CASE("B7 turn rejects each invalid start parameter and healthy heading") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        motion::Turn turn;
        CHECK_FALSE(turn.start(0U, invalid, 90.0F, .8F, false));
        checkZero(turn.step(0U, 0.0F, false), motion::Status::INVALID);
        CHECK_FALSE(turn.start(0U, 0.0F, invalid, .8F, true));
        checkZero(turn.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK_FALSE(turn.start(0U, 0.0F, 90.0F, invalid, true));
        checkZero(turn.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK(turn.start(0U, 0.0F, 90.0F, .8F, true));
        checkZero(turn.step(1000U, invalid, true), motion::Status::INVALID);
        checkZero(turn.step(2000U, 0.0F, true), motion::Status::INVALID);
    }
    for (float duty : {-.1F, 0.0F, .249F, 1.001F}) {
        motion::Turn turn;
        CHECK_FALSE(turn.start(0U, 0.0F, 90.0F, duty, true));
        checkZero(turn.step(0U, 0.0F, true), motion::Status::INVALID);
    }
    for (float duty : {.25F, 1.0F}) {
        motion::Turn turn;
        CHECK(turn.start(0U, 0.0F, 90.0F, duty, true));
        checkActive(turn.step(0U, 0.0F, true), duty, -duty);
    }
}

TEST_CASE("B7 straight D022 signed proportional correction holds original reference") {
    for (float base : {-.5F, .5F}) {
        motion::Straight straight;
        CHECK(straight.start(0U, 170.0F, base, 100U));
        checkActive(straight.step(0U, 170.0F, true), base, base);
        checkActive(straight.step(1000U, 160.0F, true), base + .2F, base - .2F);
        checkActive(straight.step(2000U, 180.0F, true), base - .2F, base + .2F);
        checkActive(straight.step(3000U, -180.0F, true), base - .2F, base + .2F);
        checkActive(straight.step(4000U, 170.0F, true), base, base);
    }
}

TEST_CASE("B7 straight D022 correction cap prevents reversing either wheel") {
    for (float base : {-.1F, .1F, 0.0F}) {
        for (float sign : {-1.0F, 1.0F}) {
            motion::Straight straight;
            CHECK(straight.start(0U, 0.0F, base, 100U));
            const float correction = std::fabs(base) * sign;
            checkActive(straight.step(0U, -sign * 90.0F, true),
                        base + correction, base - correction);
        }
    }
    motion::Straight forward;
    motion::Straight reverse;
    CHECK(forward.start(0U, 0.0F, .9F, 100U));
    CHECK(reverse.start(0U, 0.0F, -.9F, 100U));
    checkActive(forward.step(0U, -90.0F, true), 1.0F, .65F);
    checkActive(reverse.step(0U, -90.0F, true), -.65F, -1.0F);
}

TEST_CASE("B7 straight unavailable IMU ignores heading and recovery resumes reference") {
    motion::Straight straight;
    CHECK(straight.start(500U, 20.0F, .5F, 100U));
    const auto failed = straight.step(500U, NAN_VALUE, false);
    checkActive(failed, .5F, .5F);
    CHECK(failed.imu_fallback);
    const auto recovered = straight.step(50000U, 10.0F, true);
    checkActive(recovered, .7F, .3F);
    CHECK_FALSE(recovered.imu_fallback);
    checkActive(straight.step(100499U, INF_VALUE, false), .5F, .5F);
    checkZero(straight.step(100500U, 20.0F, true), motion::Status::DONE);
    checkZero(straight.step(101500U, 20.0F, true), motion::Status::DONE);
}

TEST_CASE("B0 B7 straight duration exact neighbors wrap zero and maximum") {
    for (std::uint32_t start : {123U, 0xFFFFFF00U}) {
        motion::Straight straight;
        CHECK(straight.start(start, 0.0F, .5F, 100U));
        checkActive(straight.step(start + 99000U, 0.0F, true), .5F, .5F);
        checkActive(straight.step(start + 99999U, 0.0F, true), .5F, .5F);
        checkZero(straight.step(start + 100000U, 0.0F, true), motion::Status::DONE);
        checkZero(straight.step(start + 101000U, 90.0F, true), motion::Status::DONE);
        CHECK(straight.start(start, 0.0F, .5F, 0U));
        checkZero(straight.step(start, 0.0F, true), motion::Status::DONE);
        CHECK(straight.start(start, 0.0F, .5F, MAX_MS));
        checkActive(straight.step(start + MAX_MS * 1000U - 1U, 0.0F, true), .5F, .5F);
        checkZero(straight.step(start + MAX_MS * 1000U, 0.0F, true), motion::Status::DONE);
    }
}

TEST_CASE("B7 straight rejects each invalid parameter and latches healthy IMU faults") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        motion::Straight straight;
        CHECK_FALSE(straight.start(0U, invalid, .5F, 100U));
        checkZero(straight.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK_FALSE(straight.start(0U, 0.0F, invalid, 100U));
        checkZero(straight.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK(straight.start(0U, 0.0F, .5F, 100U));
        checkZero(straight.step(1000U, invalid, true), motion::Status::INVALID);
        checkZero(straight.step(2000U, 0.0F, true), motion::Status::INVALID);
    }
    for (float duty : {-1.001F, 1.001F}) {
        motion::Straight straight;
        CHECK_FALSE(straight.start(0U, 0.0F, duty, 100U));
        checkZero(straight.step(0U, 0.0F, true), motion::Status::INVALID);
    }
    motion::Straight straight;
    CHECK_FALSE(straight.start(0U, 0.0F, .5F, MAX_MS + 1U));
    checkZero(straight.step(0U, 0.0F, true), motion::Status::INVALID);
}

TEST_CASE("B7 arc duties mirror left right and include zero one ratio endpoints") {
    for (float ratio : {0.0F, .45F, 1.0F}) {
        for (float duty : {0.0F, .7F, 1.0F}) {
            motion::Arc right;
            motion::Arc left;
            CHECK(right.start(0U, 0.0F, motion::Direction::RIGHT, ratio, duty, 200.0F, 1500U));
            CHECK(left.start(0U, 0.0F, motion::Direction::LEFT, ratio, duty, 200.0F, 1500U));
            const auto r = right.step(0U, 0.0F, true);
            const auto l = left.step(0U, 0.0F, true);
            checkActive(r, duty, duty * ratio);
            checkActive(l, duty * ratio, duty);
            checkMirror(r, l);
        }
    }
}

TEST_CASE("B7 arc measures signed continuous sweep past 180 and multiple revolutions") {
    for (float sweep : {200.0F, 720.0F}) {
        for (float sign : {-1.0F, 1.0F}) {
            motion::Arc arc;
            const auto direction = sign > 0.0F ? motion::Direction::RIGHT : motion::Direction::LEFT;
            const float start = sign * 720.0F;
            CHECK(arc.start(0U, start, direction, .4F, .7F, sweep, 1500U));
            CHECK(arc.step(1000U, start - sign * sweep, true).status == motion::Status::ACTIVE);
            CHECK(arc.step(2000U, start + sign * (sweep - .125F), true).status == motion::Status::ACTIVE);
            checkZero(arc.step(3000U, start + sign * sweep, true), motion::Status::DONE);
            checkZero(arc.step(4000U, NAN_VALUE, true), motion::Status::DONE);
        }
    }
}

TEST_CASE("B7 arc unavailable IMU skips sweep completion and recovery keeps deadline") {
    motion::Arc arc;
    CHECK(arc.start(500U, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
    const auto unavailable = arc.step(500U, 250.0F, false);
    checkActive(unavailable, .7F, .28F);
    CHECK(unavailable.imu_fallback);
    checkActive(arc.step(50000U, NAN_VALUE, false), .7F, .28F);
    const auto recovered = arc.step(100499U, 100.0F, true);
    checkActive(recovered, .7F, .28F);
    CHECK_FALSE(recovered.imu_fallback);
    checkZero(arc.step(100500U, 200.0F, true), motion::Status::TIMED_OUT);
    checkZero(arc.step(101500U, 250.0F, true), motion::Status::TIMED_OUT);
    CHECK(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
    CHECK(arc.step(1000U, NAN_VALUE, false).imu_fallback);
    checkZero(arc.step(2000U, 200.0F, true), motion::Status::DONE);
}

TEST_CASE("B0 B7 arc timeout exact neighbors wrap zero and maximum") {
    for (std::uint32_t start : {123U, 0xFFFFFF00U}) {
        motion::Arc arc;
        CHECK(arc.start(start, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
        checkActive(arc.step(start + 99000U, 0.0F, true), .7F, .28F);
        checkActive(arc.step(start + 99999U, NAN_VALUE, false), .7F, .28F);
        checkZero(arc.step(start + 100000U, 200.0F, true), motion::Status::TIMED_OUT);
        checkZero(arc.step(start + 101000U, 250.0F, true), motion::Status::TIMED_OUT);
        CHECK(arc.start(start, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, 0U));
        checkZero(arc.step(start, 0.0F, true), motion::Status::TIMED_OUT);
        CHECK(arc.start(start, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, MAX_MS));
        checkActive(arc.step(start + MAX_MS * 1000U - 1U, 0.0F, true), .7F, .28F);
        checkZero(arc.step(start + MAX_MS * 1000U, 0.0F, true), motion::Status::TIMED_OUT);
    }
}

TEST_CASE("B7 arc rejects every nonfinite parameter and healthy heading fault") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        motion::Arc arc;
        CHECK_FALSE(arc.start(0U, invalid, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, invalid, .7F, 200.0F, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, invalid, 200.0F, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, invalid, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
        checkZero(arc.step(1000U, invalid, true), motion::Status::INVALID);
        checkZero(arc.step(2000U, 0.0F, true), motion::Status::INVALID);
    }
}

TEST_CASE("B7 arc rejects out of range duties ratios sweep duration and direction") {
    motion::Arc arc;
    for (float invalid : {-.001F, 1.001F}) {
        CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, invalid, .7F, 200.0F, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
        CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, invalid, 200.0F, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
    }
    for (float invalid : {0.0F, -1.0F}) {
        CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, invalid, 100U));
        checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
    }
    CHECK_FALSE(arc.start(0U, 0.0F, static_cast<motion::Direction>(255U), .4F, .7F, 200.0F, 100U));
    checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
    CHECK_FALSE(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, MAX_MS + 1U));
    checkZero(arc.step(0U, 0.0F, true), motion::Status::INVALID);
}

TEST_CASE("B0 B7 brake is stationary through exact deadlines zero duration and wrap") {
    for (std::uint32_t start : {123U, 0xFFFFFF00U}) {
        motion::Brake brake;
        CHECK(brake.start(start, 100U));
        checkZero(brake.step(start), motion::Status::ACTIVE);
        checkZero(brake.step(start + 99000U), motion::Status::ACTIVE);
        checkZero(brake.step(start + 99999U), motion::Status::ACTIVE);
        checkZero(brake.step(start + 100000U), motion::Status::DONE);
        checkZero(brake.step(start + 101000U), motion::Status::DONE);
        CHECK(brake.start(start, 0U));
        checkZero(brake.step(start), motion::Status::DONE);
        CHECK(brake.start(start, MAX_MS));
        checkZero(brake.step(start + MAX_MS * 1000U - 1U), motion::Status::ACTIVE);
        checkZero(brake.step(start + MAX_MS * 1000U), motion::Status::DONE);
        CHECK_FALSE(brake.start(start, MAX_MS + 1U));
        checkZero(brake.step(start), motion::Status::INVALID);
        checkZero(brake.step(start + 1000U), motion::Status::INVALID);
    }
}

TEST_CASE("B7 reset discards active commands faults and fallback before restart") {
    motion::Turn turn;
    motion::Straight straight;
    motion::Arc arc;
    motion::Brake brake;
    CHECK(turn.start(0U, 0.0F, 45.0F, .8F, false));
    CHECK(straight.start(0U, 0.0F, .5F, 100U));
    CHECK(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
    CHECK(brake.start(0U, 100U));
    turn.reset(); straight.reset(); arc.reset(); brake.reset();
    checkZero(turn.step(1000U, 0.0F, true), motion::Status::IDLE);
    checkZero(straight.step(1000U, 0.0F, true), motion::Status::IDLE);
    checkZero(arc.step(1000U, 0.0F, true), motion::Status::IDLE);
    checkZero(brake.step(1000U), motion::Status::IDLE);
    CHECK(turn.start(500U, 0.0F, -90.0F, .8F, true));
    CHECK_FALSE(turn.step(500U, 0.0F, true).imu_fallback);
    checkActive(turn.step(500U, 0.0F, true), -.8F, .8F);
    CHECK(straight.start(500U, 20.0F, -.5F, 100U));
    checkActive(straight.step(500U, 20.0F, true), -.5F, -.5F);
    CHECK(arc.start(500U, 20.0F, motion::Direction::LEFT, .4F, .7F, 200.0F, 100U));
    checkActive(arc.step(500U, 20.0F, true), .28F, .7F);
    CHECK(brake.start(500U, 100U));
    checkZero(brake.step(500U), motion::Status::ACTIVE);
    CHECK_FALSE(turn.start(0U, NAN_VALUE, 90.0F, .8F, true));
    CHECK_FALSE(straight.start(0U, NAN_VALUE, .5F, 100U));
    CHECK_FALSE(arc.start(0U, NAN_VALUE, motion::Direction::RIGHT, .4F, .7F, 200.0F, 100U));
    CHECK_FALSE(brake.start(0U, MAX_MS + 1U));
    turn.reset(); straight.reset(); arc.reset(); brake.reset();
    checkZero(turn.step(1000U, 0.0F, true), motion::Status::IDLE);
    checkZero(straight.step(1000U, 0.0F, true), motion::Status::IDLE);
    checkZero(arc.step(1000U, 0.0F, true), motion::Status::IDLE);
    checkZero(brake.step(1000U), motion::Status::IDLE);
}

TEST_CASE("B6 B7 D023 fallback turn timing is identical at 9 11.1 and 12.6 volts") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        CAPTURE(voltage);
        motion::Turn turn;
        governor::Governor governor;
        CHECK(turn.start(0U, 0.0F, 90.0F, 1.0F, false));
        for (std::uint32_t t = 0U; t <= 181000U; t += 1000U) {
            const auto request = turn.step(t, NAN_VALUE, false);
            const auto result = governor.step(t, governed(request, voltage, governor::Profile::PIVOT));
            CHECK(result.valid);
            CHECK(std::fabs(result.duty_l) <= config::TURN_DUTY);
            CHECK(std::fabs(result.duty_r) <= config::TURN_DUTY);
            if (t < 180000U) CHECK(request.status == motion::Status::ACTIVE);
            else {
                checkZero(request, motion::Status::DONE);
                CHECK(result.duty_l == 0.0F);
                CHECK(result.duty_r == 0.0F);
            }
            if (t == 100000U) {
                CHECK(result.duty_l == doctest::Approx(.8F));
                CHECK(result.duty_r == doctest::Approx(-.8F));
            }
        }
    }
}

TEST_CASE("B6 B7 D023 straight arc and brake keep durations with final voltage caps") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        motion::Straight straight;
        motion::Arc arc;
        motion::Brake brake;
        governor::Governor straight_governor;
        governor::Governor arc_governor;
        CHECK(straight.start(0U, 0.0F, 1.0F, 100U));
        CHECK(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, 1.0F, 200.0F, 100U));
        CHECK(brake.start(0U, 100U));
        for (std::uint32_t t = 0U; t <= 101000U; t += 1000U) {
            const auto s = straight.step(t, NAN_VALUE, false);
            const auto a = arc.step(t, NAN_VALUE, false);
            const auto sg = straight_governor.step(t, governed(s, voltage, governor::Profile::SEARCH_FORWARD));
            const auto ag = arc_governor.step(t, governed(a, voltage, governor::Profile::OPENER));
            CHECK(sg.valid); CHECK(ag.valid);
            CHECK(std::fabs(sg.duty_l) <= .30F); CHECK(std::fabs(sg.duty_r) <= .30F);
            CHECK(std::fabs(ag.duty_l) <= .85F); CHECK(std::fabs(ag.duty_r) <= .85F);
            if (t < 100000U) {
                CHECK(s.status == motion::Status::ACTIVE);
                CHECK(a.status == motion::Status::ACTIVE);
                checkZero(brake.step(t), motion::Status::ACTIVE);
            } else {
                checkZero(s, motion::Status::DONE);
                checkZero(a, motion::Status::TIMED_OUT);
                checkZero(brake.step(t), motion::Status::DONE);
                CHECK(sg.duty_l == 0.0F); CHECK(sg.duty_r == 0.0F);
                CHECK(ag.duty_l == 0.0F); CHECK(ag.duty_r == 0.0F);
            }
            if (t == 90000U) {
                CHECK(sg.duty_l == doctest::Approx(.30F));
                CHECK(ag.duty_l == doctest::Approx(.85F));
                CHECK(ag.duty_r == doctest::Approx(.4F * config::V_NOM_V / voltage));
            }
        }
    }
}

TEST_CASE("B0 B7 ten thousand seeded turn and straight commands remain finite and mirrored") {
    std::uint32_t seed = 0xB7002201U;
    unsigned healthy_samples = 0U;
    unsigned fallback_samples = 0U;
    for (unsigned sample = 0U; sample < 10000U; ++sample) {
        const std::uint32_t start = nextRandom(seed);
        const float angle = static_cast<float>(nextRandom(seed) % 341U) - 170.0F;
        const float heading = static_cast<float>(nextRandom(seed) % 2001U) - 1000.0F;
        const float base = (static_cast<float>(nextRandom(seed) % 2001U) - 1000.0F) / 1000.0F;
        const bool healthy = (sample & 1U) != 0U;
        if (healthy) ++healthy_samples;
        else ++fallback_samples;
        const std::uint32_t elapsed = nextRandom(seed) % 800001U;
        motion::Turn right_turn, left_turn;
        CHECK(right_turn.start(start, heading, heading + angle, .8F, healthy));
        CHECK(left_turn.start(start, -heading, -heading - angle, .8F, healthy));
        const auto rt = right_turn.step(start + elapsed, heading, healthy);
        const auto lt = left_turn.step(start + elapsed, -heading, healthy);
        checkBounded(rt); checkBounded(lt); checkMirror(rt, lt);
        motion::Straight right_straight, left_straight;
        CHECK(right_straight.start(start, heading, base, 500U));
        CHECK(left_straight.start(start, -heading, base, 500U));
        const auto rs = right_straight.step(start + elapsed, heading + angle, healthy);
        const auto ls = left_straight.step(start + elapsed, -heading - angle, healthy);
        checkBounded(rs); checkBounded(ls); checkMirror(rs, ls);
        CHECK(rs.duty_l * base >= 0.0F); CHECK(rs.duty_r * base >= 0.0F);
    }
    CHECK(healthy_samples == 5000U);
    CHECK(fallback_samples == 5000U);
}

TEST_CASE("B0 B7 ten thousand seeded arcs and brakes remain finite and mirrored") {
    std::uint32_t seed = 0xB7002202U;
    unsigned healthy_samples = 0U;
    unsigned fallback_samples = 0U;
    for (unsigned sample = 0U; sample < 10000U; ++sample) {
        const std::uint32_t start = nextRandom(seed);
        const std::uint32_t elapsed = nextRandom(seed) % 2000001U;
        const float heading = static_cast<float>(nextRandom(seed) % 2001U) - 1000.0F;
        const float progress = static_cast<float>(nextRandom(seed) % 1001U) - 100.0F;
        const float duty = static_cast<float>(nextRandom(seed) % 1001U) / 1000.0F;
        const float ratio = static_cast<float>(nextRandom(seed) % 1001U) / 1000.0F;
        const bool healthy = (sample & 1U) != 0U;
        if (healthy) ++healthy_samples;
        else ++fallback_samples;
        motion::Arc right, left;
        CHECK(right.start(start, heading, motion::Direction::RIGHT, ratio, duty, 400.0F, 1500U));
        CHECK(left.start(start, -heading, motion::Direction::LEFT, ratio, duty, 400.0F, 1500U));
        const auto r = right.step(start + elapsed, heading + progress, healthy);
        const auto l = left.step(start + elapsed, -heading - progress, healthy);
        checkBounded(r); checkBounded(l); checkMirror(r, l);
        CHECK(r.duty_l >= 0.0F); CHECK(r.duty_r >= 0.0F);
        motion::Brake brake;
        CHECK(brake.start(start, 1500U));
        checkZero(brake.step(start + elapsed), elapsed < 1500000U ? motion::Status::ACTIVE : motion::Status::DONE);
    }
    CHECK(healthy_samples == 5000U);
    CHECK(fallback_samples == 5000U);
}

TEST_CASE("B0 B7 maximum accepted durations expire when final tick crosses full start wrap") {
    motion::Straight straight;
    motion::Arc arc;
    motion::Brake brake;
    CHECK(straight.start(0U, 0.0F, .5F, MAX_MS));
    CHECK(arc.start(0U, 0.0F, motion::Direction::RIGHT, .4F, .7F, 200.0F, MAX_MS));
    CHECK(brake.start(0U, MAX_MS));
    checkActive(straight.step(4294966500U, 0.0F, true), .5F, .5F);
    checkActive(arc.step(4294966500U, 0.0F, true), .7F, .28F);
    checkZero(brake.step(4294966500U), motion::Status::ACTIVE);
    // The next 1 kHz tick is 1000 us later, beyond the 4294967000 us deadline.
    checkZero(straight.step(204U, 0.0F, true), motion::Status::DONE);
    checkZero(arc.step(204U, 0.0F, true), motion::Status::TIMED_OUT);
    checkZero(brake.step(204U), motion::Status::DONE);
}

TEST_CASE("B0 B7 turn late sample crossing start wrap cannot resurrect timed out command") {
    motion::Turn turn;
    CHECK(turn.start(0U, 0.0F, 90.0F, .8F, true));
    checkActive(turn.step(600000U, 0.0F, true), .8F, -.8F);
    // Consecutive samples are less than a full wrap apart, total age exceeds one.
    checkZero(turn.step(1000U, 0.0F, true), motion::Status::TIMED_OUT);
    checkZero(turn.step(2000U, 90.0F, true), motion::Status::TIMED_OUT);
}
