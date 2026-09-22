// Checks B4.2 escape rows against B7 timing and D-020 through D-023 boundaries.
// Protects bounded requests and guard/governor composition without claiming a Robot or HAL.
// Independent spec-derived host tests cover every supported row and mirrored streams.
#include "doctest.h"
#include "config.h"
#include "core/edge.h"
#include "core/governor.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Phase = edge::ScriptPhase;
using Profile = governor::Profile;
constexpr std::array<std::uint8_t, 9> ROWS{{1U, 2U, 4U, 5U, 6U, 8U, 9U, 10U, 12U}};

bool supported(std::uint8_t mask) {
    for (const auto row : ROWS) {
        if ((mask & 15U) == row) return true;
    }
    return false;
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    return static_cast<std::uint8_t>(((mask & 1U) << 1U) |
        ((mask & 2U) >> 1U) | ((mask & 4U) << 1U) | ((mask & 8U) >> 1U));
}

bool frontRow(std::uint8_t mask) {
    return mask == 1U || mask == 2U || mask == 6U || mask == 9U;
}

void checkZero(const edge::RowResult& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
    CHECK(result.brake);
    if (phase != Phase::BRAKE) CHECK_FALSE(result.motion.imu_fallback);
}

void checkMoving(const edge::RowResult& result, Phase phase, Profile profile,
                 float left, float right) {
    CHECK(result.phase == phase);
    CHECK(result.profile == profile);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK_FALSE(result.brake);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(right));
}

void checkBounded(const edge::RowResult& result) {
    CHECK(std::isfinite(result.motion.duty_l));
    CHECK(std::isfinite(result.motion.duty_r));
    CHECK(std::abs(result.motion.duty_l) <= 1.0F);
    CHECK(std::abs(result.motion.duty_r) <= 1.0F);
}

edge::RowResult beginPivot(edge::RowExecutor& row, std::uint8_t mask,
                           std::uint32_t start, float heading, bool imu = true) {
    CHECK(row.start(start, mask, heading, imu));
    if (frontRow(mask)) {
        checkZero(row.step(start, heading, imu), Phase::BRAKE);
        checkMoving(row.step(start + 1000U, heading, imu), Phase::BACK,
                    Profile::EDGE_REVERSE, -0.8F, -0.8F);
        return row.step(start + 121000U, heading, imu);
    }
    return row.step(start, heading, imu);
}

governor::Request requestFor(const edge::RowResult& row,
                            const edge::GuardResult& guard,
                            bool permission, float voltage = 11.1F) {
    governor::Request request;
    request.duty_l = row.motion.duty_l;
    request.duty_r = row.motion.duty_r;
    request.profile = row.profile;
    request.brake = row.brake;
    request.inhibited = !permission || guard.inhibit_motion;
    request.vbat_v = voltage;
    return request;
}

struct ComposedTick {
    edge::RowResult row;
    edge::GuardResult guard;
    governor::Result duty;
};

// Test-owned wiring of pure components; this is not Robot::step or MotorGate.
class RowScenario {
public:
    ComposedTick step(std::uint32_t time, std::uint8_t mask,
                      float heading = 0.0F, bool permission = true) {
        ComposedTick tick;
        tick.row = row.step(time, heading, true);
        tick.guard = guard.step(mask, permission, tick.row.phase == Phase::DONE);
        tick.duty = governor.step(time, requestFor(tick.row, tick.guard, permission));
        return tick;
    }
    edge::RowExecutor row;
    edge::Guard guard;
    governor::Governor governor;
};

std::uint32_t randomWord(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}

void checkMirrored(const edge::RowResult& left, const edge::RowResult& right) {
    CHECK(left.phase == right.phase);
    CHECK(left.motion.status == right.motion.status);
    CHECK(left.brake == right.brake);
    CHECK(left.phase_changed == right.phase_changed);
    CHECK(left.turn_timed_out == right.turn_timed_out);
    CHECK(left.motion.imu_fallback == right.motion.imu_fallback);
    CHECK(left.motion.duty_l == doctest::Approx(right.motion.duty_r));
    CHECK(left.motion.duty_r == doctest::Approx(right.motion.duty_l));
    if (!left.brake) CHECK(left.profile == right.profile);
    checkBounded(left);
    checkBounded(right);
}
} // namespace

TEST_CASE("B4.2 escape row constants preserve the approved literal boundaries") {
    CHECK(config::TICK_US == 1000U);
    CHECK(config::EDGE_BACK_MS == 120U);
    CHECK(config::EDGE_FWD_MS == 200U);
    CHECK(config::EDGE_TURN_DEG == 120U);
    CHECK(config::EDGE_SIDE_TURN_DEG == 45U);
    CHECK(config::EDGE_BACK_DUTY == doctest::Approx(0.8F));
    CHECK(config::EDGE_FWD_INNER_RATIO == doctest::Approx(0.7F));
    CHECK(config::TURN_DUTY == doctest::Approx(0.8F));
    CHECK(config::HEADING_TOL_DEG == 5U);
    CHECK(config::TURN_TIMEOUT_MS == 700U);
    CHECK(config::TURN_MS_PER_DEG == doctest::Approx(2.0F));
}

TEST_CASE("B4.2 unstarted and reset escape rows are inert") {
    edge::RowExecutor row;
    auto result = row.step(0U, 0.0F, true);
    checkZero(result, Phase::IDLE);
    CHECK(result.motion.status == motion::Status::IDLE);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
    CHECK(row.start(100U, 8U, 0.0F, true));
    checkMoving(row.step(100U, 0.0F, true), Phase::FORWARD,
                Profile::EDGE_FORWARD, 0.56F, 0.8F);
    row.reset();
    result = row.step(1000000U, 0.0F, true);
    checkZero(result, Phase::IDLE);
    CHECK(result.motion.status == motion::Status::IDLE);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B4.2 all 256 selected masks use only low bits and nine supported rows") {
    unsigned accepted = 0U;
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        CAPTURE(mask);
        edge::RowExecutor row;
        const auto selected = static_cast<std::uint8_t>(mask);
        CHECK(row.start(0U, selected, 0.0F, true) == supported(selected));
        const auto result = row.step(0U, 0.0F, true);
        CHECK_FALSE(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        if (!supported(selected)) {
            checkZero(result, Phase::UNSUPPORTED);
            CHECK(result.motion.status == motion::Status::INVALID);
        } else {
            ++accepted;
            CHECK(result.phase != Phase::INVALID);
            CHECK(result.phase != Phase::UNSUPPORTED);
            checkBounded(result);
        }
    }
    CHECK(accepted == 144U);
}

TEST_CASE("B4.2 unsupported masks precede bad heading validation without defining recovery") {
    for (const auto heading : {std::numeric_limits<float>::quiet_NaN(),
                               std::numeric_limits<float>::infinity(),
                               -std::numeric_limits<float>::infinity()}) {
        for (unsigned mask = 0U; mask < 16U; ++mask) {
            for (const bool imu : {false, true}) {
                edge::RowExecutor row;
                const auto selected = static_cast<std::uint8_t>(mask);
                CHECK_FALSE(row.start(0U, selected, heading, imu));
                const auto result = row.step(1U, 0.0F, true);
                checkZero(result, supported(selected) ? Phase::INVALID : Phase::UNSUPPORTED);
                CHECK(result.motion.status == motion::Status::INVALID);
            }
        }
    }
}

TEST_CASE("B4.2 all supported escape rows begin with the specified signs and profiles") {
    for (const auto mask : ROWS) {
        CAPTURE(mask);
        edge::RowExecutor row;
        CHECK(row.start(123U, mask, 0.0F, true));
        const auto result = row.step(123U, 0.0F, true);
        CHECK_FALSE(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        if (frontRow(mask)) checkZero(result, Phase::BRAKE);
        else if (mask == 5U) checkMoving(result, Phase::PIVOT, Profile::PIVOT, 0.8F, -0.8F);
        else if (mask == 10U) checkMoving(result, Phase::PIVOT, Profile::PIVOT, -0.8F, 0.8F);
        else if (mask == 4U) checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.56F);
        else if (mask == 8U) checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.56F, 0.8F);
        else checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.8F);
    }
}

TEST_CASE("B4.2 front and diagonal brake one tick then reverse exactly 120 ms") {
    for (const std::uint8_t mask : {1U, 2U, 6U, 9U}) {
        edge::RowExecutor row;
        CHECK(row.start(17U, mask, 0.0F, true));
        for (const auto offset : {0U, 999U}) {
            const auto result = row.step(17U + offset, 0.0F, true);
            checkZero(result, Phase::BRAKE);
            CHECK_FALSE(result.phase_changed);
        }
        auto result = row.step(1017U, 0.0F, true);
        checkMoving(result, Phase::BACK, Profile::EDGE_REVERSE, -0.8F, -0.8F);
        CHECK(result.phase_changed);
        for (const auto offset : {1001U, 120999U}) {
            result = row.step(17U + offset, 0.0F, true);
            checkMoving(result, Phase::BACK, Profile::EDGE_REVERSE, -0.8F, -0.8F);
            CHECK_FALSE(result.phase_changed);
        }
        result = row.step(121017U, 0.0F, true);
        const float left = mask == 1U || mask == 9U ? 0.8F : -0.8F;
        checkMoving(result, Phase::PIVOT, Profile::PIVOT, left, -left);
        CHECK(result.phase_changed);
        CHECK_FALSE(row.step(121018U, 0.0F, true).phase_changed);
    }
}

TEST_CASE("B4.2 rear rows end at exactly 200 ms with latched terminal zero") {
    for (const std::uint8_t mask : {4U, 8U, 12U}) {
        edge::RowExecutor row;
        CHECK(row.start(900U, mask, 0.0F, true));
        CHECK(row.step(900U, 0.0F, true).phase == Phase::FORWARD);
        auto result = row.step(200899U, 0.0F, true);
        CHECK(result.phase == Phase::FORWARD);
        CHECK_FALSE(result.phase_changed);
        result = row.step(200900U, 0.0F, true);
        checkZero(result, Phase::DONE);
        CHECK(result.motion.status == motion::Status::DONE);
        CHECK(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        for (const auto time : {200901U, 123456789U}) {
            result = row.step(time, 30.0F, true);
            checkZero(result, Phase::DONE);
            CHECK_FALSE(result.phase_changed);
            CHECK_FALSE(result.turn_timed_out);
        }
    }
}

TEST_CASE("B4.2 B7 45 and 120 degree targets use strict five degree tolerance") {
    const float below = std::nextafter(5.0F, 0.0F);
    const float above = std::nextafter(5.0F, 6.0F);
    for (const std::uint8_t mask : {1U, 2U, 5U, 6U, 9U, 10U}) {
        const float angle = frontRow(mask) ? 120.0F : 45.0F;
        const bool right = mask == 1U || mask == 5U || mask == 9U;
        const float initial = right ? -angle : angle;
        const std::uint32_t pivot_time = frontRow(mask) ? 121000U : 0U;
        for (const float magnitude : {below, 5.0F, above}) {
            for (const float sign : {-1.0F, 1.0F}) {
                edge::RowExecutor row;
                CHECK(beginPivot(row, mask, 0U, initial).phase == Phase::PIVOT);
                const auto result = row.step(pivot_time + 1U, sign * magnitude, true);
                CHECK_FALSE(result.turn_timed_out);
                if (magnitude < 5.0F) {
                    CHECK(result.phase == (frontRow(mask) ? Phase::DONE : Phase::FORWARD));
                    CHECK(result.phase_changed);
                } else {
                    checkMoving(result, Phase::PIVOT, Profile::PIVOT,
                                -sign * 0.25F, sign * 0.25F);
                    CHECK_FALSE(result.phase_changed);
                }
            }
        }
    }
}

TEST_CASE("B4.2 B7 reverse and pivot capture heading at each entry and never retarget") {
    edge::RowExecutor row;
    CHECK(row.start(0U, 2U, 0.0F, true));
    checkZero(row.step(999U, 10.0F, true), Phase::BRAKE);
    checkMoving(row.step(1000U, 30.0F, true), Phase::BACK,
                Profile::EDGE_REVERSE, -0.8F, -0.8F);
    checkMoving(row.step(1001U, 40.0F, true), Phase::BACK,
                Profile::EDGE_REVERSE, -1.0F, -0.6F);
    checkMoving(row.step(121000U, 50.0F, true), Phase::PIVOT,
                Profile::PIVOT, -0.8F, 0.8F);
    checkMoving(row.step(121001U, -60.0F, true), Phase::PIVOT,
                Profile::PIVOT, -0.25F, 0.25F);
    const auto result = row.step(121002U, -70.0F, true);
    checkZero(result, Phase::DONE);
    CHECK(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B4.2 side rows capture forward heading after their mirrored 45 degree turn") {
    for (const float sign : {-1.0F, 1.0F}) {
        edge::RowExecutor row;
        const std::uint8_t mask = sign > 0.0F ? 5U : 10U;
        CHECK(row.start(0U, mask, sign * 10.0F, true));
        checkMoving(row.step(0U, sign * 10.0F, true), Phase::PIVOT,
                    Profile::PIVOT, sign * 0.8F, -sign * 0.8F);
        auto result = row.step(12345U, sign * 55.0F, true);
        checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.8F);
        CHECK(result.phase_changed);
        result = row.step(12346U, sign * 60.0F, true);
        checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD,
                    0.8F - sign * 0.1F, 0.8F + sign * 0.1F);
        CHECK(row.step(212344U, sign * 55.0F, true).phase == Phase::FORWARD);
        checkZero(row.step(212345U, sign * 55.0F, true), Phase::DONE);
        CHECK_FALSE(row.step(212346U, sign * 55.0F, true).phase_changed);
    }
}

TEST_CASE("B4.2 D-022 rear bias stays fixed while straight rear motion holds heading") {
    for (const std::uint8_t mask : {4U, 8U}) {
        edge::RowExecutor row;
        CHECK(row.start(0U, mask, 30.0F, true));
        const float left = mask == 4U ? 0.8F : 0.56F;
        const float right = mask == 4U ? 0.56F : 0.8F;
        for (const float heading : {-170.0F, 0.0F, 90.0F, 179.0F}) {
            checkMoving(row.step(1U, heading, true), Phase::FORWARD,
                        Profile::EDGE_FORWARD, left, right);
        }
    }
    edge::RowExecutor row;
    CHECK(row.start(0U, 12U, 30.0F, true));
    checkMoving(row.step(1U, 40.0F, true), Phase::FORWARD,
                Profile::EDGE_FORWARD, 0.6F, 1.0F);
    checkMoving(row.step(2U, -150.0F, true), Phase::FORWARD,
                Profile::EDGE_FORWARD, 1.0F, 0.55F);
}

TEST_CASE("B4.2 delayed front calls start each segment now instead of backdating") {
    edge::RowExecutor row;
    CHECK(row.start(0U, 1U, 0.0F, true));
    checkMoving(row.step(5000U, 10.0F, true), Phase::BACK,
                Profile::EDGE_REVERSE, -0.8F, -0.8F);
    CHECK(row.step(124999U, 10.0F, true).phase == Phase::BACK);
    checkMoving(row.step(125000U, 20.0F, true), Phase::PIVOT,
                Profile::PIVOT, 0.8F, -0.8F);
    CHECK(row.step(824999U, 20.0F, true).phase == Phase::PIVOT);
    const auto result = row.step(825000U, 20.0F, true);
    checkZero(result, Phase::DONE);
    CHECK(result.turn_timed_out);
}

TEST_CASE("B4.2 B7 side timeout starts a complete 200 ms forward segment on observation") {
    edge::RowExecutor row;
    CHECK(row.start(0U, 10U, 0.0F, true));
    auto result = row.step(900000U, 70.0F, true);
    checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.8F);
    CHECK(result.turn_timed_out);
    CHECK(result.phase_changed);
    result = row.step(1099999U, 70.0F, true);
    CHECK(result.phase == Phase::FORWARD);
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.phase_changed);
    checkZero(row.step(1100000U, 70.0F, true), Phase::DONE);
}

TEST_CASE("B4.2 B7 pivot timeout wins a target tie at exactly 700 ms and pulses once") {
    for (const std::uint8_t mask : {1U, 2U, 5U, 6U, 9U, 10U}) {
        edge::RowExecutor row;
        const bool right = mask == 1U || mask == 5U || mask == 9U;
        const float target = (right ? 1.0F : -1.0F) * (frontRow(mask) ? 120.0F : 45.0F);
        CHECK(beginPivot(row, mask, 0U, 0.0F).phase == Phase::PIVOT);
        const std::uint32_t deadline = (frontRow(mask) ? 121000U : 0U) + 700000U;
        auto result = row.step(deadline - 1U, 0.0F, true);
        CHECK(result.phase == Phase::PIVOT);
        CHECK_FALSE(result.turn_timed_out);
        result = row.step(deadline, target, true);
        CHECK(result.phase == (frontRow(mask) ? Phase::DONE : Phase::FORWARD));
        CHECK(result.turn_timed_out);
        CHECK(result.phase_changed);
        result = row.step(deadline + 1U, target, true);
        CHECK_FALSE(result.turn_timed_out);
        CHECK_FALSE(result.phase_changed);
    }
}

TEST_CASE("B4.2 B7 initial IMU fallback uses 120 or 45 degrees times two ms") {
    const float nan = std::numeric_limits<float>::quiet_NaN();
    for (const std::uint8_t mask : {1U, 2U, 5U, 6U, 9U, 10U}) {
        edge::RowExecutor row;
        auto result = beginPivot(row, mask, 0U, 17.0F, false);
        CHECK(result.phase == Phase::PIVOT);
        CHECK(result.motion.imu_fallback);
        const std::uint32_t deadline = frontRow(mask) ? 361000U : 90000U;
        result = row.step(deadline - 1U, nan, false);
        CHECK(result.phase == Phase::PIVOT);
        CHECK(result.motion.imu_fallback);
        result = row.step(deadline, nan, false);
        CHECK(result.phase == (frontRow(mask) ? Phase::DONE : Phase::FORWARD));
        CHECK(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        if (!frontRow(mask)) {
            CHECK(result.motion.imu_fallback);
            CHECK(row.step(deadline + 199999U, nan, false).phase == Phase::FORWARD);
            checkZero(row.step(deadline + 200000U, nan, false), Phase::DONE);
        }
    }
}

TEST_CASE("B4.2 B7 reaching a pivot target one microsecond before timeout is healthy completion") {
    for (const std::uint8_t mask : {2U, 10U}) {
        edge::RowExecutor row;
        CHECK(beginPivot(row, mask, 0U, 0.0F).phase == Phase::PIVOT);
        const std::uint32_t deadline = frontRow(mask) ? 821000U : 700000U;
        const float target = frontRow(mask) ? -120.0F : -45.0F;
        const auto result = row.step(deadline - 1U, target, true);
        CHECK(result.phase == (frontRow(mask) ? Phase::DONE : Phase::FORWARD));
        CHECK(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        CHECK_FALSE(result.motion.imu_fallback);
    }
}

TEST_CASE("B4.2 B7 pivot IMU loss latches last remaining angle despite recovery") {
    edge::RowExecutor row;
    CHECK(beginPivot(row, 2U, 0U, 0.0F).phase == Phase::PIVOT);
    CHECK(row.step(122000U, -60.0F, true).phase == Phase::PIVOT);
    auto result = row.step(123000U, std::numeric_limits<float>::quiet_NaN(), false);
    checkMoving(result, Phase::PIVOT, Profile::PIVOT, -0.8F, 0.8F);
    CHECK(result.motion.imu_fallback);
    result = row.step(124000U, -120.0F, true);
    CHECK(result.phase == Phase::PIVOT);
    CHECK(result.motion.imu_fallback);
    CHECK(row.step(242999U, -120.0F, true).phase == Phase::PIVOT);
    result = row.step(243000U, -120.0F, true);
    checkZero(result, Phase::DONE);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B4.2 B7 late IMU loss cannot extend the original pivot deadline") {
    edge::RowExecutor row;
    CHECK(beginPivot(row, 1U, 0U, 0.0F).phase == Phase::PIVOT);
    CHECK(row.step(820000U, 0.0F, false).motion.imu_fallback);
    CHECK(row.step(820999U, 120.0F, true).phase == Phase::PIVOT);
    const auto result = row.step(821000U, 120.0F, true);
    checkZero(result, Phase::DONE);
    CHECK(result.turn_timed_out);
    CHECK_FALSE(row.step(821001U, 120.0F, true).turn_timed_out);
}

TEST_CASE("B4.2 B7 unavailable yaw preserves last healthy heading for later entry") {
    edge::RowExecutor row;
    const float nan = std::numeric_limits<float>::quiet_NaN();
    CHECK(row.start(0U, 2U, 5.0F, true));
    checkZero(row.step(999U, 10.0F, true), Phase::BRAKE);
    auto result = row.step(1000U, nan, false);
    checkMoving(result, Phase::BACK, Profile::EDGE_REVERSE, -0.8F, -0.8F);
    CHECK(result.motion.imu_fallback);
    result = row.step(1001U, 20.0F, true);
    checkMoving(result, Phase::BACK, Profile::EDGE_REVERSE, -1.0F, -0.6F);
    CHECK_FALSE(result.motion.imu_fallback);
    result = row.step(121000U, nan, false);
    checkMoving(result, Phase::PIVOT, Profile::PIVOT, -0.8F, 0.8F);
    CHECK(result.motion.imu_fallback);
    CHECK(row.step(360999U, -100.0F, true).phase == Phase::PIVOT);
    checkZero(row.step(361000U, -100.0F, true), Phase::DONE);
}

TEST_CASE("B4.2 B7 fallback recovery supplies the next phase reference without ending the turn early") {
    edge::RowExecutor row;
    CHECK(row.start(0U, 10U, 17.0F, false));
    CHECK(row.step(0U, 17.0F, false).motion.imu_fallback);
    auto result = row.step(89999U, 80.0F, true);
    CHECK(result.phase == Phase::PIVOT);
    CHECK(result.motion.imu_fallback);
    result = row.step(90000U, 90.0F, true);
    checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.8F);
    CHECK_FALSE(result.motion.imu_fallback);
    checkMoving(row.step(90001U, 95.0F, true), Phase::FORWARD,
                Profile::EDGE_FORWARD, 0.7F, 0.9F);
    checkZero(row.step(290000U, 90.0F, true), Phase::DONE);
}

TEST_CASE("B4.2 D-022 straight IMU recovery resumes its captured reference and timer") {
    edge::RowExecutor row;
    CHECK(row.start(100U, 12U, 30.0F, true));
    checkMoving(row.step(101U, 40.0F, true), Phase::FORWARD,
                Profile::EDGE_FORWARD, 0.6F, 1.0F);
    auto result = row.step(102U, std::numeric_limits<float>::infinity(), false);
    checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.8F);
    CHECK(result.motion.imu_fallback);
    result = row.step(103U, 40.0F, true);
    checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.6F, 1.0F);
    CHECK_FALSE(result.motion.imu_fallback);
    CHECK(row.step(200099U, 30.0F, true).phase == Phase::FORWARD);
    checkZero(row.step(200100U, 30.0F, true), Phase::DONE);
}

TEST_CASE("B4.2 healthy nonfinite yaw latches invalid zero in every active phase") {
    for (const float bad : {std::numeric_limits<float>::quiet_NaN(),
                            std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        for (const unsigned stage : {0U, 1U, 2U, 3U, 4U}) {
            edge::RowExecutor row;
            const std::uint8_t mask = stage == 3U ? 8U : stage == 4U ? 12U : 2U;
            CHECK(row.start(0U, mask, 0.0F, true));
            std::uint32_t time = 0U;
            if (stage == 1U || stage == 2U) {
                CHECK(row.step(1000U, 0.0F, true).phase == Phase::BACK);
                time = 1000U;
            }
            if (stage == 2U) {
                CHECK(row.step(121000U, 0.0F, true).phase == Phase::PIVOT);
                time = 121000U;
            }
            const auto result = row.step(time + 1U, bad, true);
            checkZero(result, Phase::INVALID);
            CHECK(result.motion.status == motion::Status::INVALID);
            CHECK(result.phase_changed);
            CHECK_FALSE(result.turn_timed_out);
            checkZero(row.step(time + 2U, 0.0F, true), Phase::INVALID);
            CHECK_FALSE(row.step(time + 3U, 0.0F, true).phase_changed);
        }
    }
}

TEST_CASE("B4.2 finite huge headings retain bounded requests without invalidating rows") {
    for (const float heading : {std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max(), 36000000.0F, -36000000.0F}) {
        for (const auto mask : ROWS) {
            edge::RowExecutor row;
            CHECK(row.start(0U, mask, heading, true));
            for (const auto time : {0U, 1000U, 121000U, 821000U, 1021000U}) {
                const auto result = row.step(time, heading, true);
                checkBounded(result);
                CHECK(result.phase != Phase::INVALID);
                CHECK(result.phase != Phase::UNSUPPORTED);
            }
            checkZero(row.step(1021001U, heading, true), Phase::DONE);
        }
    }
}

TEST_CASE("B4.2 finite huge headings retain the specified relative pivot after normalization") {
    for (const float heading : {std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max(), 350.0F, -350.0F}) {
        for (const std::uint8_t mask : {1U, 2U, 5U, 6U, 9U, 10U}) {
            edge::RowExecutor row;
            const bool right = mask == 1U || mask == 5U || mask == 9U;
            const float sign = right ? 1.0F : -1.0F;
            const double angle = frontRow(mask) ? 120.0 : 45.0;
            const double normalized = std::fmod(static_cast<double>(heading), 360.0);
            const float target = static_cast<float>(normalized + sign * angle);
            const auto first = beginPivot(row, mask, 0U, heading);
            checkMoving(first, Phase::PIVOT, Profile::PIVOT, sign * 0.8F, -sign * 0.8F);
            const auto result = row.step(frontRow(mask) ? 121001U : 1U, target, true);
            CHECK(result.phase == (frontRow(mask) ? Phase::DONE : Phase::FORWARD));
            CHECK_FALSE(result.turn_timed_out);
            CHECK(result.phase_changed);
        }
    }
}

TEST_CASE("B4.2 restart clears completed invalid unsupported and pending row history") {
    edge::RowExecutor row;
    for (const unsigned old : {0U, 1U, 2U, 3U}) {
        if (old == 0U) {
            CHECK(row.start(0U, 8U, 0.0F, true));
            checkZero(row.step(200000U, 0.0F, true), Phase::DONE);
        } else if (old == 1U) {
            CHECK_FALSE(row.start(0U, 8U, std::numeric_limits<float>::quiet_NaN(), true));
        } else if (old == 2U) CHECK_FALSE(row.start(0U, 15U, 0.0F, true));
        else CHECK(row.start(0U, 1U, 0.0F, false));
        CHECK(row.start(300000U, 10U, 10.0F, true));
        auto result = row.step(300000U, 10.0F, true);
        checkMoving(result, Phase::PIVOT, Profile::PIVOT, -0.8F, 0.8F);
        CHECK_FALSE(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        CHECK_FALSE(result.motion.imu_fallback);
        result = row.step(300001U, -35.0F, true);
        checkMoving(result, Phase::FORWARD, Profile::EDGE_FORWARD, 0.8F, 0.8F);
        checkZero(row.step(500001U, -35.0F, true), Phase::DONE);
    }
}

TEST_CASE("B4.2 terminal rows ignore later bad yaw and reset clears timeout pulses") {
    edge::RowExecutor row;
    CHECK(beginPivot(row, 2U, 0U, 0.0F).phase == Phase::PIVOT);
    CHECK(row.step(821000U, 0.0F, true).turn_timed_out);
    const float nan = std::numeric_limits<float>::quiet_NaN();
    auto result = row.step(821001U, nan, true);
    checkZero(result, Phase::DONE);
    CHECK(result.motion.status == motion::Status::DONE);
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.phase_changed);
    row.reset();
    result = row.step(821002U, nan, false);
    checkZero(result, Phase::IDLE);
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.phase_changed);
    CHECK(row.start(821003U, 12U, 10.0F, true));
    checkMoving(row.step(821003U, 10.0F, true), Phase::FORWARD,
                Profile::EDGE_FORWARD, 0.8F, 0.8F);
}

TEST_CASE("B4.2 front and rear exact deadlines survive unsigned micros wrap") {
    const std::uint32_t start = std::numeric_limits<std::uint32_t>::max() - 500U;
    edge::RowExecutor front;
    CHECK(front.start(start, 2U, 0.0F, false));
    checkZero(front.step(start + 999U, 0.0F, false), Phase::BRAKE);
    CHECK(front.step(start + 1000U, 0.0F, false).phase == Phase::BACK);
    CHECK(front.step(start + 120999U, 0.0F, false).phase == Phase::BACK);
    CHECK(front.step(start + 121000U, 0.0F, false).phase == Phase::PIVOT);
    CHECK(front.step(start + 360999U, 0.0F, false).phase == Phase::PIVOT);
    checkZero(front.step(start + 361000U, 0.0F, false), Phase::DONE);
    edge::RowExecutor rear;
    CHECK(rear.start(start, 12U, 20.0F, true));
    CHECK(rear.step(start + 199999U, 20.0F, true).phase == Phase::FORWARD);
    checkZero(rear.step(start + 200000U, 20.0F, true), Phase::DONE);
}

TEST_CASE("B4.2 delayed legal gaps accumulate several wraps without skipping new segments") {
    edge::RowExecutor row;
    std::uint32_t time = 99U;
    constexpr std::uint32_t GAP = std::numeric_limits<std::uint32_t>::max() - 7U;
    CHECK(row.start(time, 1U, 0.0F, true));
    time += GAP;
    checkMoving(row.step(time, 0.0F, true), Phase::BACK,
                Profile::EDGE_REVERSE, -0.8F, -0.8F);
    time += GAP;
    checkMoving(row.step(time, 0.0F, true), Phase::PIVOT, Profile::PIVOT, 0.8F, -0.8F);
    time += GAP;
    auto result = row.step(time, 0.0F, true);
    checkZero(result, Phase::DONE);
    CHECK(result.turn_timed_out);
    time += GAP;
    result = row.step(time, 0.0F, true);
    checkZero(result, Phase::DONE);
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.phase_changed);
}

TEST_CASE("B4.2 ten thousand fixed seed mirrored streams preserve signs bounds and phases") {
    std::uint32_t seed = 0xB4022026U;
    std::array<unsigned, 9> rows{};
    std::array<unsigned, 8> phases{};
    std::array<unsigned, 2> imu_modes{};
    unsigned wrapping = 0U;
    for (unsigned sample = 0U; sample < 10000U; ++sample) {
        const auto index = sample % ROWS.size();
        const auto mask = ROWS[index];
        const bool imu = (sample & 1U) != 0U;
        const float initial = static_cast<float>(randomWord(seed) % 16001U) / 100.0F - 80.0F;
        const std::uint32_t start = (sample & 2U) != 0U ?
            std::numeric_limits<std::uint32_t>::max() - randomWord(seed) % 1000U : randomWord(seed);
        ++rows[index];
        ++imu_modes[imu ? 1U : 0U];
        if (start > std::numeric_limits<std::uint32_t>::max() - 1021000U) ++wrapping;
        edge::RowExecutor left, right;
        CHECK(left.start(start, mask, initial, imu));
        CHECK(right.start(start, mirrorMask(mask), -initial, imu));
        for (const auto elapsed : {0U, 999U, 1000U, 120999U, 121000U, 321000U, 821000U, 1021000U}) {
            const auto a = left.step(start + elapsed, initial, imu);
            const auto b = right.step(start + elapsed, -initial, imu);
            checkMirrored(a, b);
            ++phases[static_cast<std::size_t>(a.phase)];
        }
        checkZero(left.step(start + 1021001U, initial, imu), Phase::DONE);
        checkZero(right.step(start + 1021001U, -initial, imu), Phase::DONE);
    }
    for (const auto count : rows) CHECK(count >= 1111U);
    CHECK(imu_modes[0] == 5000U);
    CHECK(imu_modes[1] == 5000U);
    CHECK(wrapping >= 5000U);
    for (const auto phase : {Phase::BRAKE, Phase::BACK, Phase::PIVOT, Phase::FORWARD, Phase::DONE})
        CHECK(phases[static_cast<std::size_t>(phase)] > 0U);
    CHECK(phases[static_cast<std::size_t>(Phase::INVALID)] == 0U);
    CHECK(phases[static_cast<std::size_t>(Phase::UNSUPPORTED)] == 0U);
}

TEST_CASE("B4.4 D-020 script done while white cannot leave escape in guard composition") {
    RowScenario scenario;
    CHECK(scenario.row.start(0U, 12U, 0.0F, true));
    CHECK(scenario.step(0U, 12U).guard.escape_required);
    auto tick = scenario.step(1000U, 0U);
    CHECK(tick.row.phase == Phase::FORWARD);
    CHECK(tick.guard.escape_required);
    CHECK_FALSE(tick.guard.inhibit_motion);
    tick = scenario.step(200000U, 12U);
    checkZero(tick.row, Phase::DONE);
    CHECK(tick.guard.escape_required);
    CHECK_FALSE(tick.guard.fault_latched);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
    CHECK(scenario.step(200001U, 12U).guard.escape_required);
    tick = scenario.step(200002U, 0U);
    CHECK_FALSE(tick.guard.escape_required);
    CHECK_FALSE(tick.guard.inhibit_motion);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
}

TEST_CASE("B4.4 D-020 all white immediately inhibits an active row and remains latched") {
    RowScenario scenario;
    CHECK(scenario.row.start(0U, 8U, 0.0F, true));
    scenario.step(0U, 8U);
    auto tick = scenario.step(50000U, 8U);
    CHECK(tick.duty.duty_l == doctest::Approx(0.56F));
    CHECK(tick.duty.duty_r == doctest::Approx(0.8F));
    tick = scenario.step(50001U, 15U);
    CHECK(tick.row.phase == Phase::FORWARD);
    CHECK(tick.guard.escape_required);
    CHECK(tick.guard.fault_latched);
    CHECK(tick.guard.inhibit_motion);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
    for (const bool permission : {true, false, true}) {
        tick = scenario.step(200000U, 0U, 0.0F, permission);
        checkZero(tick.row, Phase::DONE);
        CHECK(tick.guard.fault_latched);
        CHECK(tick.guard.inhibit_motion);
        CHECK(tick.duty.duty_l == 0.0F);
        CHECK(tick.duty.duty_r == 0.0F);
    }
}

TEST_CASE("B4.2 row requests never grant permission and a closed gate clears governor duty") {
    RowScenario scenario;
    CHECK(scenario.row.start(0U, 8U, 0.0F, true));
    auto tick = scenario.step(0U, 15U, 0.0F, false);
    CHECK_FALSE(tick.guard.fault_latched);
    CHECK_FALSE(tick.guard.escape_required);
    CHECK(tick.guard.inhibit_motion);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
    tick = scenario.step(50000U, 8U);
    CHECK(tick.duty.duty_l > 0.0F);
    CHECK(tick.duty.duty_r > 0.0F);
    tick = scenario.step(50001U, 8U, 0.0F, false);
    CHECK(tick.row.phase == Phase::FORWARD);
    CHECK(tick.guard.inhibit_motion);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
}

TEST_CASE("B4.2 D-021 D-022 reverse correction and pivot reversal obey governor caps") {
    RowScenario scenario;
    CHECK(scenario.row.start(0U, 2U, 0.0F, true));
    scenario.step(0U, 2U);
    scenario.step(1000U, 2U);
    auto tick = scenario.step(101000U, 2U, 10.0F);
    CHECK(tick.row.motion.duty_l == doctest::Approx(-1.0F));
    CHECK(tick.row.motion.duty_r == doctest::Approx(-0.6F));
    CHECK(tick.duty.duty_l == doctest::Approx(-0.8F));
    CHECK(tick.duty.duty_r == doctest::Approx(-0.6F));
    tick = scenario.step(121000U, 2U, 10.0F);
    checkMoving(tick.row, Phase::PIVOT, Profile::PIVOT, -0.8F, 0.8F);
    CHECK(tick.duty.duty_l == doctest::Approx(-0.8F));
    CHECK(tick.duty.duty_r == 0.0F);
    tick = scenario.step(122000U, 2U, 10.0F);
    CHECK(tick.duty.duty_l == doctest::Approx(-0.8F));
    CHECK(tick.duty.duty_r == doctest::Approx(0.02F));
    tick = scenario.step(122001U, 2U, -110.0F);
    checkZero(tick.row, Phase::DONE);
    CHECK(tick.guard.escape_required);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
}

TEST_CASE("B4.2 D-023 voltage changes duties but never escape forward duration") {
    for (const float voltage : {9.0F, 11.1F, 12.6F}) {
        edge::RowExecutor row;
        edge::Guard guard;
        governor::Governor governor;
        CHECK(row.start(0U, 8U, 0.0F, true));
        auto result = row.step(0U, 0.0F, true);
        auto guarded = guard.step(8U, true, false);
        governor.step(0U, requestFor(result, guarded, true, voltage));
        result = row.step(100000U, 0.0F, true);
        auto duty = governor.step(100000U, requestFor(result, guarded, true, voltage));
        CHECK(duty.duty_l == doctest::Approx(0.56F * 11.1F / voltage));
        CHECK(duty.duty_r == doctest::Approx(voltage < 11.1F ? 0.8F : 0.8F * 11.1F / voltage));
        CHECK(duty.duty_l <= 0.8F);
        CHECK(duty.duty_r <= 0.8F);
        CHECK(row.step(199999U, 0.0F, true).phase == Phase::FORWARD);
        result = row.step(200000U, 0.0F, true);
        checkZero(result, Phase::DONE);
        guarded = guard.step(8U, true, true);
        CHECK(guarded.escape_required);
        duty = governor.step(200000U, requestFor(result, guarded, true, voltage));
        CHECK(duty.duty_l == 0.0F);
        CHECK(duty.duty_r == 0.0F);
    }
}
