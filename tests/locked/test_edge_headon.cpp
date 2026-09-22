// Checks the additive B4.2/D-044 explicit-side head-on row contract.
// Protects existing mask selection while exercising the approved long reverse and pivot.
// Independent locked host tests cover boundaries, mirrors, fallback and guard/governor composition.
#include "doctest.h"
#include "config.h"
#include "core/edge.h"
#include "core/governor.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Phase = edge::ScriptPhase;
using Direction = motion::Direction;
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();

void checkZero(const edge::RowResult& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK(result.brake);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
    if (phase != Phase::BRAKE) CHECK_FALSE(result.motion.imu_fallback);
}

void checkMoving(const edge::RowResult& result, Phase phase, float left, float right) {
    CHECK(result.phase == phase);
    CHECK_FALSE(result.brake);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(right));
    CHECK(result.profile == (phase == Phase::BACK ? governor::Profile::EDGE_REVERSE : governor::Profile::PIVOT));
}

void beginPivot(edge::RowExecutor& row, Direction direction, float heading = 0.0F,
                bool imu = true, std::uint32_t start = 0U) {
    CHECK(row.startHeadOn(start, heading, imu, direction));
    checkZero(row.step(start, heading, imu), Phase::BRAKE);
    checkMoving(row.step(start + 1000U, heading, imu), Phase::BACK, -0.8F, -0.8F);
    const float left = direction == Direction::RIGHT ? 0.8F : -0.8F;
    checkMoving(row.step(start + 181000U, heading, imu), Phase::PIVOT, left, -left);
}

struct ComposedTick {
    edge::RowResult row;
    edge::GuardResult guard;
    governor::Result duty;
};

class HeadOnScenario {
public:
    ComposedTick step(std::uint32_t time, float heading, std::uint8_t lines,
                      bool permitted = true) {
        ComposedTick result;
        result.row = row.step(time, heading, true);
        result.guard = guard.step(lines, permitted, result.row.phase == Phase::DONE);
        governor::Request request;
        request.duty_l = result.row.motion.duty_l;
        request.duty_r = result.row.motion.duty_r;
        request.profile = result.row.profile;
        request.brake = result.row.brake;
        request.inhibited = !permitted || result.guard.inhibit_motion;
        request.vbat_v = 9.0F;
        result.duty = governor.step(time, request);
        return result;
    }
    edge::RowExecutor row;
    edge::Guard guard;
    governor::Governor governor;
};
} // namespace

TEST_CASE("B4.2 D-044 head-on uses literal approved defaults without changing legacy mask selection") {
    CHECK(config::TICK_US == 1000U);
    CHECK(config::EDGE_BACK_LONG_MS == 180U);
    CHECK(config::EDGE_TURN_FULL_DEG == 160U);
    CHECK(config::EDGE_BACK_DUTY == doctest::Approx(0.8F));
    for (unsigned high = 0U; high < 256U; high += 16U) {
        edge::RowExecutor row;
        CHECK_FALSE(row.start(0U, static_cast<std::uint8_t>(high | 3U), 0.0F, true));
        checkZero(row.step(0U, 0.0F, true), Phase::UNSUPPORTED);
        CHECK(row.startHeadOn(1U, 0.0F, true, Direction::RIGHT));
        checkZero(row.step(1U, 0.0F, true), Phase::BRAKE);
    }
}

TEST_CASE("B4.2 D-044 mirrored head-on brakes one tick then reverses for exactly 180 ms") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        edge::RowExecutor row;
        CHECK(row.startHeadOn(17U, 0.0F, true, direction));
        for (const auto elapsed : {0U, 999U}) {
            const auto result = row.step(17U + elapsed, 0.0F, true);
            checkZero(result, Phase::BRAKE);
            CHECK_FALSE(result.phase_changed);
        }
        auto result = row.step(1017U, 0.0F, true);
        checkMoving(result, Phase::BACK, -0.8F, -0.8F);
        CHECK(result.phase_changed);
        for (const auto elapsed : {1001U, 180999U}) {
            result = row.step(17U + elapsed, 0.0F, true);
            checkMoving(result, Phase::BACK, -0.8F, -0.8F);
            CHECK_FALSE(result.phase_changed);
        }
        const float left = direction == Direction::RIGHT ? 0.8F : -0.8F;
        result = row.step(181017U, 0.0F, true);
        checkMoving(result, Phase::PIVOT, left, -left);
        CHECK(result.phase_changed);
        CHECK_FALSE(row.step(181018U, 0.0F, true).phase_changed);
    }
}

TEST_CASE("B4.2 B7 head-on captures reverse and 160 degree turn headings at each entry") {
    edge::RowExecutor row;
    CHECK(row.startHeadOn(0U, 5.0F, true, Direction::RIGHT));
    checkZero(row.step(999U, 10.0F, true), Phase::BRAKE);
    checkMoving(row.step(1000U, 30.0F, true), Phase::BACK, -0.8F, -0.8F);
    checkMoving(row.step(1001U, 40.0F, true), Phase::BACK, -1.0F, -0.6F);
    checkMoving(row.step(181000U, 50.0F, true), Phase::PIVOT, 0.8F, -0.8F);
    checkMoving(row.step(181001U, -160.0F, true), Phase::PIVOT, 0.25F, -0.25F);
    const auto result = row.step(181002U, -150.0F, true);
    checkZero(result, Phase::DONE);
    CHECK(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B4.2 B7 head-on 160 degree target uses strict adjacent five degree tolerance") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (const float magnitude : {std::nextafter(5.0F, 0.0F), 5.0F, std::nextafter(5.0F, 6.0F)}) {
            for (const float sign : {-1.0F, 1.0F}) {
                edge::RowExecutor row;
                beginPivot(row, direction, direction == Direction::RIGHT ? -160.0F : 160.0F);
                const auto result = row.step(181001U, sign * magnitude, true);
                if (magnitude < 5.0F) checkZero(result, Phase::DONE);
                else checkMoving(result, Phase::PIVOT, -sign * 0.25F, sign * 0.25F);
                CHECK_FALSE(result.turn_timed_out);
            }
        }
    }
}

TEST_CASE("B4.2 B7 head-on timeout starts at pivot entry and wins target equality at 700 ms") {
    edge::RowExecutor row;
    beginPivot(row, Direction::RIGHT);
    checkMoving(row.step(880999U, 0.0F, true), Phase::PIVOT, 0.8F, -0.8F);
    auto result = row.step(881000U, 160.0F, true);
    checkZero(result, Phase::DONE);
    CHECK(result.turn_timed_out);
    CHECK(result.phase_changed);
    result = row.step(881001U, NAN_YAW, true);
    checkZero(result, Phase::DONE);
    CHECK_FALSE(result.turn_timed_out);
    CHECK_FALSE(result.phase_changed);
    beginPivot(row, Direction::RIGHT);
    result = row.step(880999U, 160.0F, true);
    checkZero(result, Phase::DONE);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B4.2 B7 head-on missing IMU times 160 degrees for 320 ms despite recovery") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        edge::RowExecutor row;
        beginPivot(row, direction, 17.0F, false);
        auto result = row.step(181001U, NAN_YAW, false);
        CHECK(result.motion.imu_fallback);
        const float target = 17.0F + (direction == Direction::RIGHT ? 160.0F : -160.0F);
        result = row.step(500999U, target, true);
        CHECK(result.phase == Phase::PIVOT);
        CHECK(result.motion.imu_fallback);
        result = row.step(501000U, target, true);
        checkZero(result, Phase::DONE);
        CHECK_FALSE(result.turn_timed_out);
    }
}

TEST_CASE("B4.2 B7 head-on mid-turn loss uses remaining angle and cannot extend original timeout") {
    edge::RowExecutor row;
    beginPivot(row, Direction::RIGHT);
    row.step(182000U, 80.0F, true);
    CHECK(row.step(183000U, NAN_YAW, false).motion.imu_fallback);
    CHECK(row.step(342999U, 160.0F, true).phase == Phase::PIVOT);
    checkZero(row.step(343000U, 160.0F, true), Phase::DONE);
    beginPivot(row, Direction::RIGHT);
    CHECK(row.step(880000U, NAN_YAW, false).motion.imu_fallback);
    const auto result = row.step(881000U, NAN_YAW, false);
    checkZero(result, Phase::DONE);
    CHECK(result.turn_timed_out);
}

TEST_CASE("B4.2 head-on delayed observations start complete new segments at observation time") {
    edge::RowExecutor row;
    CHECK(row.startHeadOn(0U, 0.0F, false, Direction::LEFT));
    checkMoving(row.step(5000U, NAN_YAW, false), Phase::BACK, -0.8F, -0.8F);
    CHECK(row.step(184999U, NAN_YAW, false).phase == Phase::BACK);
    checkMoving(row.step(185000U, NAN_YAW, false), Phase::PIVOT, -0.8F, 0.8F);
    CHECK(row.step(504999U, NAN_YAW, false).phase == Phase::PIVOT);
    checkZero(row.step(505000U, NAN_YAW, false), Phase::DONE);
}

TEST_CASE("B4.2 head-on rejects invalid capture and healthy bad yaw in all active phases") {
    edge::RowExecutor row;
    CHECK_FALSE(row.startHeadOn(0U, 0.0F, true, static_cast<Direction>(255U)));
    checkZero(row.step(0U, 0.0F, true), Phase::INVALID);
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        for (const bool imu : {false, true}) {
            CHECK_FALSE(row.startHeadOn(0U, bad, imu, Direction::LEFT));
            checkZero(row.step(0U, 0.0F, true), Phase::INVALID);
        }
        for (unsigned stage = 0U; stage < 3U; ++stage) {
            CHECK(row.startHeadOn(0U, 0.0F, true, Direction::LEFT));
            if (stage > 0U) row.step(1000U, 0.0F, true);
            if (stage > 1U) row.step(181000U, 0.0F, true);
            const auto time = stage == 0U ? 1U : stage == 1U ? 1001U : 181001U;
            checkZero(row.step(time, bad, true), Phase::INVALID);
            auto result = row.step(time + 1U, 0.0F, true);
            checkZero(result, Phase::INVALID);
            CHECK_FALSE(result.phase_changed);
            CHECK_FALSE(result.turn_timed_out);
        }
    }
}

TEST_CASE("B4.2 head-on finite extreme headings preserve relative 160 degree targets") {
    for (const float heading : {std::numeric_limits<float>::max(), -std::numeric_limits<float>::max()}) {
        for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
            edge::RowExecutor row;
            beginPivot(row, direction, heading);
            const double relative = direction == Direction::RIGHT ? 160.0 : -160.0;
            const float target = static_cast<float>(std::fmod(static_cast<double>(heading), 360.0) + relative);
            checkZero(row.step(181001U, target, true), Phase::DONE);
        }
    }
}

TEST_CASE("B4.2 head-on restart or reset cannot leak long reverse into the original front row") {
    for (const bool reset : {false, true}) {
        edge::RowExecutor row;
        beginPivot(row, Direction::LEFT, 0.0F, false);
        if (reset) {
            row.reset();
            checkZero(row.step(1000000U, 0.0F, true), Phase::IDLE);
        }
        CHECK(row.start(1000000U, 1U, 0.0F, true));
        checkZero(row.step(1000999U, 0.0F, true), Phase::BRAKE);
        checkMoving(row.step(1001000U, 0.0F, true), Phase::BACK, -0.8F, -0.8F);
        CHECK(row.step(1120999U, 0.0F, true).phase == Phase::BACK);
        checkMoving(row.step(1121000U, 0.0F, true), Phase::PIVOT, 0.8F, -0.8F);
        checkZero(row.step(1121001U, 120.0F, true), Phase::DONE);
    }
}

TEST_CASE("B4.2 head-on exact brake reverse and fallback endpoints survive micros wrap") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 500U;
    edge::RowExecutor row;
    CHECK(row.startHeadOn(start, 0.0F, false, Direction::RIGHT));
    checkZero(row.step(start + 999U, NAN_YAW, false), Phase::BRAKE);
    CHECK(row.step(start + 1000U, NAN_YAW, false).phase == Phase::BACK);
    CHECK(row.step(start + 180999U, NAN_YAW, false).phase == Phase::BACK);
    CHECK(row.step(start + 181000U, NAN_YAW, false).phase == Phase::PIVOT);
    CHECK(row.step(start + 500999U, NAN_YAW, false).phase == Phase::PIVOT);
    checkZero(row.step(start + 501000U, NAN_YAW, false), Phase::DONE);
}

TEST_CASE("B4.2 D-020 head-on completion while white stays in escape and terminal brake clears duty") {
    HeadOnScenario scenario;
    CHECK(scenario.row.startHeadOn(0U, 0.0F, true, Direction::RIGHT));
    scenario.step(0U, 0.0F, 3U);
    scenario.step(1000U, 0.0F, 3U);
    auto tick = scenario.step(101000U, 0.0F, 3U);
    CHECK(tick.duty.duty_l == doctest::Approx(-0.8F));
    CHECK(tick.duty.duty_r == doctest::Approx(-0.8F));
    tick = scenario.step(181000U, 0.0F, 3U);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == doctest::Approx(-0.8F));
    tick = scenario.step(182000U, 0.0F, 3U);
    CHECK(tick.duty.duty_l == doctest::Approx(0.02F));
    tick = scenario.step(182001U, 160.0F, 3U);
    checkZero(tick.row, Phase::DONE);
    CHECK(tick.guard.escape_required);
    CHECK(tick.duty.duty_l == 0.0F);
    CHECK(tick.duty.duty_r == 0.0F);
    CHECK_FALSE(scenario.step(182002U, 160.0F, 0U).guard.escape_required);
}

TEST_CASE("B4.2 D-020 all-white and revoked permission inhibit active head-on requests") {
    for (const bool all_white : {false, true}) {
        HeadOnScenario scenario;
        CHECK(scenario.row.startHeadOn(0U, 0.0F, true, Direction::LEFT));
        scenario.step(0U, 0.0F, 3U);
        scenario.step(1000U, 0.0F, 3U);
        CHECK(scenario.step(101000U, 0.0F, 3U).duty.duty_l < 0.0F);
        const auto tick = scenario.step(101001U, 0.0F, all_white ? 15U : 3U, all_white);
        CHECK(tick.row.phase == Phase::BACK);
        CHECK(tick.guard.inhibit_motion);
        CHECK(tick.guard.fault_latched == all_white);
        CHECK(tick.duty.duty_l == 0.0F);
        CHECK(tick.duty.duty_r == 0.0F);
        if (all_white) {
            const auto cleared = scenario.step(101002U, 0.0F, 0U);
            CHECK(cleared.guard.fault_latched);
            CHECK(cleared.guard.inhibit_motion);
            CHECK(cleared.duty.duty_l == 0.0F);
            CHECK(cleared.duty.duty_r == 0.0F);
        }
    }
}
