// Checks B8 SEARCH and D-041/D-042 direction, history and full-sweep fallback rules.
// Separates bounded motion requests from target routing, edge/STOP arbitration and motors.
// Independent host tests cover literal boundaries, mirrors, invalid inputs and composition.
#include "doctest.h"
#include "config.h"
#include "core/fsm.h"
#include "core/governor.h"
#include "core/opp_fusion.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Direction = motion::Direction;
using Phase = fsm::SearchPhase;
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();

void checkZero(const fsm::SearchResult& result, Phase phase, fsm::Intent intent) {
    CHECK(result.phase == phase);
    CHECK(result.intent == intent);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
    CHECK_FALSE(result.motion.imu_fallback);
    const auto expected = phase == Phase::INVALID ? motion::Status::INVALID :
        phase == Phase::IDLE ? motion::Status::IDLE : motion::Status::DONE;
    CHECK(result.motion.status == expected);
}

void checkActive(const fsm::SearchResult& result, Phase phase,
                 float left, float right) {
    CHECK(result.phase == phase);
    CHECK(result.intent == fsm::Intent::NONE);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(right));
    CHECK(result.profile == (phase == Phase::ADVANCE ?
          governor::Profile::SEARCH_FORWARD : governor::Profile::PIVOT));
}

void checkScan(const fsm::SearchResult& result, Direction direction) {
    const float left = direction == Direction::RIGHT ? 0.45F : -0.45F;
    checkActive(result, Phase::SCAN, left, -left);
    CHECK(result.scan_direction == direction);
}

void checkBounded(const fsm::SearchResult& result) {
    CHECK(std::isfinite(result.motion.duty_l));
    CHECK(std::isfinite(result.motion.duty_r));
    CHECK(std::abs(result.motion.duty_l) <= 1.0F);
    CHECK(std::abs(result.motion.duty_r) <= 1.0F);
}

fsm::SearchContext memoryContext(float target) {
    fsm::SearchContext context;
    context.world_valid = true;
    context.world_bearing_deg = target;
    return context;
}

void preparePhase(fsm::Search& search, unsigned stage) {
    const auto context = stage == 0U ? memoryContext(90.0F) : fsm::SearchContext{};
    CHECK(search.start(0U, 0.0F, true, context));
    if (stage == 2U) checkActive(search.step(1000U, 360.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
}

governor::Request requestFor(const fsm::SearchResult& result, bool permitted,
                            float voltage = 9.0F) {
    governor::Request request;
    request.duty_l = result.motion.duty_l;
    request.duty_r = result.motion.duty_r;
    request.profile = result.profile;
    request.vbat_v = voltage;
    request.inhibited = !permitted || result.intent != fsm::Intent::NONE;
    return request;
}
} // namespace

TEST_CASE("B8 SEARCH literal defaults and unstarted state are inert") {
    CHECK(config::SEARCH_MEMORY_MS == 3000U);
    CHECK(config::SEARCH_ADVANCE_MS == 300U);
    CHECK(config::SEARCH_SCAN_DEG == 360U);
    CHECK(config::RECENT_EDGE_MS == 5000U);
    CHECK(config::SCAN_DUTY == doctest::Approx(0.45F));
    CHECK(config::SEARCH_DUTY_MAX == doctest::Approx(0.3F));
    CHECK(config::TURN_MS_PER_DEG == doctest::Approx(2.0F));
    fsm::Search search;
    const auto result = search.step(0U, 0.0F, true, 0U);
    checkZero(result, Phase::IDLE, fsm::Intent::NONE);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B8 D-041 SearchSide retains zero unavailable and invalid selected bearings") {
    fsm::SearchSide side;
    CHECK(side.direction() == Direction::RIGHT);
    side.observe(-90.0F, true);
    CHECK(side.direction() == Direction::LEFT);
    for (const float value : {0.0F, -0.0F, NAN_YAW,
                              std::numeric_limits<float>::infinity(),
                              -std::numeric_limits<float>::infinity(), -180.0F,
                              -181.0F, std::nextafter(180.0F, 181.0F)}) {
        side.observe(value, true);
        CHECK(side.direction() == Direction::LEFT);
    }
    side.observe(90.0F, false);
    CHECK(side.direction() == Direction::LEFT);
    side.observe(180.0F, true);
    CHECK(side.direction() == Direction::RIGHT);
    side.observe(std::nextafter(-180.0F, 0.0F), true);
    CHECK(side.direction() == Direction::LEFT);
    side.observe(std::numeric_limits<float>::denorm_min(), true);
    CHECK(side.direction() == Direction::RIGHT);
    side.observe(-std::numeric_limits<float>::denorm_min(), true);
    CHECK(side.direction() == Direction::LEFT);
    side.reset();
    CHECK(side.direction() == Direction::RIGHT);
}

TEST_CASE("B2 B5 D-041 SearchSide consumes the selected group instead of lower-priority bits") {
    opp_fusion::BearingMemory bearing;
    fsm::SearchSide side;
    const std::array<std::uint8_t, 7> masks{{8U, 18U, 12U, 17U, 24U, 64U, 0U}};
    const std::array<Direction, 7> expected{{Direction::LEFT, Direction::LEFT,
        Direction::RIGHT, Direction::LEFT, Direction::LEFT, Direction::RIGHT, Direction::RIGHT}};
    for (unsigned i = 0U; i < masks.size(); ++i) {
        const auto selected = bearing.step(i, masks[i], 0.0F);
        side.observe(selected.relative_deg, selected.bearing_valid);
        CHECK(side.direction() == expected[i]);
    }
}

TEST_CASE("B8 default and retained sides start the first scan without a phase pulse") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        fsm::SearchContext context;
        context.last_side = direction;
        fsm::Search search;
        CHECK(search.start(123U, 10.0F, true, context));
        const auto result = search.step(123U, 10.0F, true, 0U);
        checkScan(result, direction);
        CHECK_FALSE(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
    }
}

TEST_CASE("B8 world memory is recent strictly before three seconds") {
    for (const auto age : std::initializer_list<std::uint64_t>{2999999U, 3000000U, 3000001U,
                                    std::numeric_limits<std::uint64_t>::max()}) {
        auto context = memoryContext(-90.0F);
        context.world_age_us = age;
        fsm::Search search;
        CHECK(search.start(0U, 0.0F, true, context));
        const auto result = search.step(0U, 0.0F, true, 0U);
        if (age < 3000000U) checkActive(result, Phase::MEMORY_TURN, -0.8F, 0.8F);
        else checkScan(result, Direction::RIGHT);
        CHECK_FALSE(result.phase_changed);
    }
}

TEST_CASE("B8 O1 first scan precedence is explicit hint then captured turn sign then retained side") {
    for (const auto retained : {Direction::LEFT, Direction::RIGHT}) {
        for (const float target : {-90.0F, -2.0F, 0.0F, 2.0F, 90.0F, 180.0F}) {
            for (unsigned hint = 0U; hint < 3U; ++hint) {
                auto context = memoryContext(target);
                context.last_side = retained;
                context.scan_hint_valid = hint != 0U;
                context.scan_hint = hint == 1U ? Direction::LEFT : Direction::RIGHT;
                fsm::Search search;
                CHECK(search.start(0U, 0.0F, true, context));
                const auto result = search.step(1000U, target, true, 0U);
                const auto expected = hint != 0U ? context.scan_hint :
                    target > 0.0F ? Direction::RIGHT : target < 0.0F ? Direction::LEFT : retained;
                checkScan(result, expected);
                CHECK(result.phase_changed);
            }
        }
    }
}

TEST_CASE("B8 captured memory turn sign survives overshoot and the positive 180 degree tie") {
    fsm::Search search;
    auto context = memoryContext(90.0F);
    context.last_side = Direction::LEFT;
    CHECK(search.start(0U, 0.0F, true, context));
    checkActive(search.step(1000U, 100.0F, true, 0U), Phase::MEMORY_TURN, -0.25F, 0.25F);
    checkScan(search.step(2000U, 90.0F, true, 0U), Direction::RIGHT);
    context = memoryContext(-90.0F);
    CHECK(search.start(0U, 90.0F, true, context));
    checkActive(search.step(0U, 90.0F, true, 0U), Phase::MEMORY_TURN, 0.8F, -0.8F);
    checkScan(search.step(1U, -90.0F, true, 0U), Direction::RIGHT);
}

TEST_CASE("B7 B8 near-antipodal memory direction preserves tiny finite offsets before the tie") {
    for (const float sign : {-1.0F, 1.0F}) {
        fsm::Search search;
        const auto context = memoryContext(sign * 0.000001F);
        CHECK(search.start(0U, sign * 180.0F, true, context));
        const auto turning = search.step(0U, sign * 180.0F, true, 0U);
        checkActive(turning, Phase::MEMORY_TURN, -sign * 0.8F, sign * 0.8F);
        const auto direction = sign > 0.0F ? Direction::LEFT : Direction::RIGHT;
        checkScan(search.step(1U, sign * 0.000001F, true, 0U), direction);
        CHECK(search.start(0U, sign * 180.0F, true, memoryContext(0.0F)));
        checkActive(search.step(0U, sign * 180.0F, true, 0U), Phase::MEMORY_TURN, 0.8F, -0.8F);
        checkScan(search.step(1U, 0.0F, true, 0U), Direction::RIGHT);
    }
}

TEST_CASE("B8 B7 expiring memory does not cancel its captured turn or extend its timeout") {
    auto context = memoryContext(90.0F);
    context.world_age_us = 2999999U;
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, context));
    checkActive(search.step(699999U, 0.0F, true, 0U), Phase::MEMORY_TURN, 0.8F, -0.8F);
    auto result = search.step(700000U, 90.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK(result.phase_changed);
    CHECK(result.turn_timed_out);
    result = search.step(700001U, 90.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B8 B7 memory turn strict tolerance and initially missing IMU feed a fresh scan") {
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, memoryContext(90.0F)));
    checkActive(search.step(1U, 85.0F, true, 0U), Phase::MEMORY_TURN, 0.25F, -0.25F);
    auto result = search.step(2U, std::nextafter(85.0F, 90.0F), true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK_FALSE(result.turn_timed_out);
    CHECK(search.start(0U, 0.0F, false, memoryContext(-90.0F)));
    CHECK(search.step(179999U, NAN_YAW, false, 0U).phase == Phase::MEMORY_TURN);
    result = search.step(180000U, NAN_YAW, false, 0U);
    checkScan(result, Direction::LEFT);
    CHECK(result.motion.imu_fallback);
    CHECK_FALSE(result.turn_timed_out);
    CHECK(search.step(899999U, NAN_YAW, false, 0U).phase == Phase::SCAN);
    checkActive(search.step(900000U, NAN_YAW, false, 0U), Phase::ADVANCE, 0.3F, 0.3F);
}

TEST_CASE("B8 full scan ends at a directed continuous 360 degree sweep for both directions") {
    for (const float sign : {-1.0F, 1.0F}) {
        fsm::SearchContext context;
        context.last_side = sign > 0.0F ? Direction::RIGHT : Direction::LEFT;
        fsm::Search search;
        CHECK(search.start(0U, 0.0F, true, context));
        checkScan(search.step(1U, sign * std::nextafter(360.0F, 0.0F), true, 0U), context.last_side);
        auto result = search.step(2U, sign * 360.0F, true, 0U);
        checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
        CHECK(result.phase_changed);
        CHECK_FALSE(result.turn_timed_out);
        CHECK_FALSE(search.step(3U, sign * 360.0F, true, 0U).phase_changed);
        CHECK(search.start(0U, sign * 350.0F, true, context));
        checkScan(search.step(1U, sign * 709.0F, true, 0U), context.last_side);
        checkActive(search.step(2U, sign * 710.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    }
}

TEST_CASE("B8 scan uses directed net progress and has no inherited 700 ms turn deadline") {
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, fsm::SearchContext{}));
    const std::array<float, 7> headings{{-180.0F, 180.0F, -180.0F, 180.0F, 0.0F, 359.0F, 0.0F}};
    const std::array<std::uint32_t, 7> times{{1U, 2U, 3U, 699999U, 700000U, 700001U, 10000000U}};
    for (unsigned i = 0U; i < headings.size(); ++i) {
        const auto result = search.step(times[i], headings[i], true, 0U);
        checkScan(result, Direction::RIGHT);
        CHECK_FALSE(result.turn_timed_out);
    }
    checkActive(search.step(10000001U, 360.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
}

TEST_CASE("B8 D-042 initial IMU loss times the full 720 ms sweep and not 700 ms") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        fsm::SearchContext context;
        context.last_side = direction;
        fsm::Search search;
        CHECK(search.start(0U, 10.0F, false, context));
        for (const auto time : {0U, 699999U, 700000U, 700001U, 719999U}) {
            const auto result = search.step(time, NAN_YAW, false, 0U);
            checkScan(result, direction);
            CHECK(result.motion.imu_fallback);
            CHECK_FALSE(result.turn_timed_out);
        }
        const auto result = search.step(720000U, NAN_YAW, false, 0U);
        checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
        CHECK(result.phase_changed);
        CHECK(result.motion.imu_fallback);
        CHECK_FALSE(result.turn_timed_out);
    }
}

TEST_CASE("B8 D-042 scan loss uses last known remaining sweep and clamps opposite progress") {
    const std::array<float, 4> progress{{0.0F, 90.0F, 359.0F, -90.0F}};
    const std::array<std::uint32_t, 4> remaining_us{{720000U, 540000U, 2000U, 720000U}};
    for (unsigned i = 0U; i < progress.size(); ++i) {
        for (const float sign : {-1.0F, 1.0F}) {
            fsm::SearchContext context;
            context.last_side = sign > 0.0F ? Direction::RIGHT : Direction::LEFT;
            fsm::Search search;
            CHECK(search.start(0U, 0.0F, true, context));
            checkScan(search.step(1000U, sign * progress[i], true, 0U), context.last_side);
            CHECK(search.step(2000U, sign * 360.0F, false, 0U).motion.imu_fallback);
            const auto deadline = 2000U + remaining_us[i];
            checkScan(search.step(deadline - 1U, NAN_YAW, false, 0U), context.last_side);
            const auto result = search.step(deadline, NAN_YAW, false, 0U);
            checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
            CHECK(result.phase_changed);
            CHECK_FALSE(result.turn_timed_out);
        }
    }
}

TEST_CASE("B8 D-042 recovered yaw cannot restart or shorten fallback but feeds the next phase") {
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, fsm::SearchContext{}));
    search.step(1000U, 90.0F, true, 0U);
    search.step(2000U, NAN_YAW, false, 0U);
    auto result = search.step(3000U, 360.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK(result.motion.imu_fallback);
    result = search.step(541999U, 500.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK(result.motion.imu_fallback);
    result = search.step(542000U, 500.0F, true, 0U);
    checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
    CHECK_FALSE(result.motion.imu_fallback);
    checkActive(search.step(542001U, 505.0F, true, 0U), Phase::ADVANCE, 0.2F, 0.4F);
}

TEST_CASE("B8 D-042 recovery after initial IMU absence still waits the original full sweep time") {
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, false, fsm::SearchContext{}));
    auto result = search.step(1U, 360.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK(result.motion.imu_fallback);
    result = search.step(719999U, 720.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK(result.motion.imu_fallback);
    result = search.step(720000U, 720.0F, true, 0U);
    checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
    CHECK_FALSE(result.motion.imu_fallback);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B8 unavailable yaw is not invented as the subsequent advance reference") {
    fsm::Search search;
    CHECK(search.start(0U, 10.0F, true, fsm::SearchContext{}));
    search.step(1000U, 100.0F, true, 0U);
    search.step(2000U, NAN_YAW, false, 0U);
    auto result = search.step(542000U, NAN_YAW, false, 0U);
    checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
    CHECK(result.motion.imu_fallback);
    result = search.step(542001U, 105.0F, true, 0U);
    checkActive(result, Phase::ADVANCE, 0.2F, 0.4F);
    CHECK_FALSE(result.motion.imu_fallback);
}

TEST_CASE("B8 advance uses inward history strictly before its internally aged five second boundary") {
    for (const auto elapsed : {999U, 1000U, 1001U}) {
        fsm::SearchContext context;
        context.inward_valid = true;
        context.inward_heading_deg = 10.0F;
        context.inward_age_us = 4999000U;
        fsm::Search search;
        CHECK(search.start(0U, 0.0F, true, context));
        const auto result = search.step(elapsed, 360.0F, true, 0U);
        checkActive(result, Phase::ADVANCE, elapsed < 1000U ? 0.5F : 0.3F,
                    elapsed < 1000U ? 0.1F : 0.3F);
    }
}

TEST_CASE("B8 an advance keeps its captured heading for exactly 300 ms then alternates scan") {
    fsm::SearchContext context;
    context.inward_valid = true;
    context.inward_heading_deg = 10.0F;
    context.inward_age_us = 4999000U;
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, context));
    checkActive(search.step(999U, 360.0F, true, 0U), Phase::ADVANCE, 0.5F, 0.1F);
    checkActive(search.step(1000U, 360.0F, true, 0U), Phase::ADVANCE, 0.5F, 0.1F);
    checkActive(search.step(300998U, 360.0F, true, 0U), Phase::ADVANCE, 0.5F, 0.1F);
    auto result = search.step(300999U, 360.0F, true, 0U);
    checkScan(result, Direction::LEFT);
    CHECK(result.phase_changed);
    CHECK_FALSE(search.step(301000U, 360.0F, true, 0U).phase_changed);
}

TEST_CASE("B8 O1 explicit hint is consumed by the first scan and later cycles alternate") {
    auto context = memoryContext(-90.0F);
    context.last_side = Direction::LEFT;
    context.scan_hint_valid = true;
    context.scan_hint = Direction::RIGHT;
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, context));
    checkScan(search.step(1000U, -90.0F, true, 0U), Direction::RIGHT);
    checkActive(search.step(2000U, 270.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    checkScan(search.step(302000U, 270.0F, true, 0U), Direction::LEFT);
    checkActive(search.step(303000U, -90.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    checkScan(search.step(603000U, -90.0F, true, 0U), Direction::RIGHT);
}

TEST_CASE("B8 late transitions begin a complete new advance rather than backdating it") {
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, false, fsm::SearchContext{}));
    auto result = search.step(1000000U, NAN_YAW, false, 0U);
    checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
    CHECK(result.phase_changed);
    checkActive(search.step(1299999U, NAN_YAW, false, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    result = search.step(1300000U, NAN_YAW, false, 0U);
    checkScan(result, Direction::LEFT);
    CHECK(result.phase_changed);
    checkScan(search.step(2019999U, NAN_YAW, false, 0U), Direction::LEFT);
    checkActive(search.step(2020000U, NAN_YAW, false, 0U), Phase::ADVANCE, 0.3F, 0.3F);
}

TEST_CASE("B2 B8 every current effective target exits each phase before heading or deadline checks") {
    for (unsigned stage = 0U; stage < 3U; ++stage) {
        for (unsigned mask = 0U; mask < 256U; ++mask) {
            fsm::Search search;
            preparePhase(search, stage);
            const bool detected = (mask & 127U) != 0U;
            const std::uint32_t time = stage == 0U ? 700000U : stage == 1U ? 720000U : 301000U;
            const float heading = detected ? NAN_YAW : stage == 2U ? 360.0F : 0.0F;
            auto result = search.step(time, heading, true, static_cast<std::uint8_t>(mask));
            if (detected) {
                checkZero(result, Phase::FINISHED, fsm::Intent::PERCEPTION);
                CHECK(result.phase_changed);
                CHECK_FALSE(result.turn_timed_out);
                result = search.step(time + 1U, NAN_YAW, true, 0U);
                checkZero(result, Phase::FINISHED, fsm::Intent::PERCEPTION);
                CHECK_FALSE(result.phase_changed);
                CHECK_FALSE(result.turn_timed_out);
            } else {
                CHECK(result.intent == fsm::Intent::NONE);
                CHECK(result.phase == Phase::SCAN);
                CHECK(result.turn_timed_out == (stage == 0U));
            }
        }
    }
}

TEST_CASE("B8 consumed direction and canonical world-memory inputs are validated") {
    const auto bad_direction = static_cast<Direction>(255U);
    fsm::Search search;
    fsm::SearchContext context;
    context.last_side = bad_direction;
    CHECK_FALSE(search.start(0U, 0.0F, true, context));
    checkZero(search.step(0U, 0.0F, true, 0U), Phase::INVALID, fsm::Intent::INVALID);
    context.world_valid = true;
    context.world_bearing_deg = 90.0F;
    context.scan_hint_valid = true;
    CHECK_FALSE(search.start(0U, 0.0F, true, context));
    context = fsm::SearchContext{};
    context.last_side = Direction::RIGHT;
    context.scan_hint = bad_direction;
    CHECK(search.start(0U, 0.0F, true, context));
    checkScan(search.step(0U, 0.0F, true, 0U), Direction::RIGHT);
    context.scan_hint_valid = true;
    CHECK_FALSE(search.start(0U, 0.0F, true, context));
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity(), -180.0F,
                            -181.0F, std::nextafter(180.0F, 181.0F)}) {
        context = memoryContext(bad);
        CHECK_FALSE(search.start(0U, 0.0F, true, context));
        checkZero(search.step(0U, 0.0F, true, 0U), Phase::INVALID, fsm::Intent::INVALID);
        context.world_age_us = 3000000U;
        CHECK(search.start(0U, 0.0F, true, context));
        checkScan(search.step(0U, 0.0F, true, 0U), Direction::RIGHT);
        context.world_age_us = 0U;
        context.world_valid = false;
        CHECK(search.start(0U, 0.0F, true, context));
    }
}

TEST_CASE("B8 unavailable or expired inward payloads are ignored and recent nonfinite payloads fail") {
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        fsm::Search search;
        fsm::SearchContext context;
        context.inward_heading_deg = bad;
        CHECK(search.start(0U, 0.0F, true, context));
        context.inward_valid = true;
        CHECK_FALSE(search.start(0U, 0.0F, true, context));
        for (const auto age : std::initializer_list<std::uint64_t>{5000000U, 5000001U,
                                        std::numeric_limits<std::uint64_t>::max()}) {
            context.inward_age_us = age;
            CHECK(search.start(0U, 0.0F, true, context));
            checkActive(search.step(1U, 360.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
        }
    }
}

TEST_CASE("B8 nonfinite initial yaw always fails and healthy bad yaw invalidates every active phase") {
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        for (const bool imu : {false, true}) {
            fsm::Search search;
            CHECK_FALSE(search.start(0U, bad, imu, fsm::SearchContext{}));
            checkZero(search.step(0U, 0.0F, true, 0U), Phase::INVALID, fsm::Intent::INVALID);
        }
        for (unsigned stage = 0U; stage < 3U; ++stage) {
            fsm::Search search;
            preparePhase(search, stage);
            auto result = search.step(2000U, bad, true, 0U);
            checkZero(result, Phase::INVALID, fsm::Intent::INVALID);
            CHECK(result.phase_changed);
            CHECK_FALSE(result.turn_timed_out);
            result = search.step(2001U, 0.0F, true, 2U);
            checkZero(result, Phase::INVALID, fsm::Intent::INVALID);
            CHECK_FALSE(result.phase_changed);
        }
    }
}

TEST_CASE("B8 extreme finite continuous yaw keeps directed progress and demands bounded") {
    const float huge = std::numeric_limits<float>::max();
    for (const float sign : {-1.0F, 1.0F}) {
        fsm::SearchContext context;
        context.last_side = sign > 0.0F ? Direction::RIGHT : Direction::LEFT;
        fsm::Search search;
        CHECK(search.start(0U, -sign * huge, true, context));
        checkScan(search.step(0U, -sign * huge, true, 0U), context.last_side);
        auto result = search.step(1U, sign * huge, true, 0U);
        checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
        checkBounded(result);
        CHECK(search.start(0U, sign * huge, true, context));
        checkScan(search.step(1U, -sign * huge, true, 0U), context.last_side);
        CHECK(search.step(2U, NAN_YAW, false, 0U).motion.imu_fallback);
        checkScan(search.step(720001U, NAN_YAW, false, 0U), context.last_side);
        result = search.step(720002U, NAN_YAW, false, 0U);
        checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
        checkBounded(result);
    }
}

TEST_CASE("B8 reset and restart discard terminal phase hint fallback and timeout history") {
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, memoryContext(90.0F)));
    CHECK(search.step(700000U, 0.0F, true, 0U).turn_timed_out);
    search.reset();
    auto result = search.step(700001U, 0.0F, true, 0U);
    checkZero(result, Phase::IDLE, fsm::Intent::NONE);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
    fsm::SearchContext context;
    context.last_side = Direction::LEFT;
    CHECK(search.start(800000U, 0.0F, false, context));
    CHECK(search.step(800001U, NAN_YAW, false, 0U).motion.imu_fallback);
    checkZero(search.step(800002U, NAN_YAW, false, 1U), Phase::FINISHED, fsm::Intent::PERCEPTION);
    CHECK(search.start(900000U, 0.0F, true, fsm::SearchContext{}));
    result = search.step(900000U, 0.0F, true, 0U);
    checkScan(result, Direction::RIGHT);
    CHECK_FALSE(result.motion.imu_fallback);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B8 fallback and advance exact deadlines survive micros wrap") {
    const std::uint32_t start = std::numeric_limits<std::uint32_t>::max() - 100U;
    fsm::Search search;
    CHECK(search.start(start, 0.0F, false, fsm::SearchContext{}));
    checkScan(search.step(start + 719999U, NAN_YAW, false, 0U), Direction::RIGHT);
    checkActive(search.step(start + 720000U, NAN_YAW, false, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    checkActive(search.step(start + 1019999U, NAN_YAW, false, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    checkScan(search.step(start + 1020000U, NAN_YAW, false, 0U), Direction::LEFT);
}

TEST_CASE("B8 expired histories never revive over repeated cycles and cumulative wraps") {
    fsm::SearchContext context;
    context.world_valid = true;
    context.world_bearing_deg = -90.0F;
    context.world_age_us = 3000000U;
    context.inward_valid = true;
    context.inward_heading_deg = 20.0F;
    fsm::Search search;
    CHECK(search.start(0U, 0.0F, true, context));
    checkActive(search.step(1000U, 360.0F, true, 0U), Phase::ADVANCE, 0.55F, 0.05F);
    checkScan(search.step(3001000U, 360.0F, true, 0U), Direction::LEFT);
    checkActive(search.step(6000000U, 0.0F, true, 0U), Phase::ADVANCE, 0.3F, 0.3F);
    std::uint32_t time = 6000000U;
    float heading = 0.0F;
    constexpr std::uint32_t GAP = std::numeric_limits<std::uint32_t>::max() - 17U;
    for (unsigned cycle = 0U; cycle < 4U; ++cycle) {
        time += GAP;
        const auto direction = cycle % 2U == 0U ? Direction::RIGHT : Direction::LEFT;
        checkScan(search.step(time, heading, true, 0U), direction);
        time += GAP;
        heading += direction == Direction::RIGHT ? 360.0F : -360.0F;
        const auto result = search.step(time, heading, true, 0U);
        checkActive(result, Phase::ADVANCE, 0.3F, 0.3F);
        CHECK_FALSE(result.turn_timed_out);
    }
}

TEST_CASE("B8 mirrored search streams preserve phase timing and bounded wheel symmetry") {
    for (const float initial : {-170.0F, -30.0F, 0.0F, 30.0F, 170.0F}) {
        for (const bool imu : {false, true}) {
            fsm::SearchContext right_context, left_context;
            left_context.last_side = Direction::LEFT;
            fsm::Search right, left;
            CHECK(right.start(0U, initial, imu, right_context));
            CHECK(left.start(0U, -initial, imu, left_context));
            const std::array<std::uint32_t, 6> times{{0U, 720000U, 1020000U, 1740000U, 2040000U, 2760000U}};
            const std::array<float, 6> progress{{0.0F, 360.0F, 360.0F, 0.0F, 0.0F, 360.0F}};
            for (unsigned i = 0U; i < times.size(); ++i) {
                const auto a = right.step(times[i], initial + progress[i], imu, 0U);
                const auto b = left.step(times[i], -initial - progress[i], imu, 0U);
                CHECK(a.phase == b.phase);
                CHECK(a.phase_changed == b.phase_changed);
                CHECK(a.turn_timed_out == b.turn_timed_out);
                CHECK(a.motion.imu_fallback == b.motion.imu_fallback);
                CHECK(a.motion.duty_l == doctest::Approx(b.motion.duty_r));
                CHECK(a.motion.duty_r == doctest::Approx(b.motion.duty_l));
                CHECK(a.scan_direction != b.scan_direction);
                checkBounded(a);
                checkBounded(b);
            }
        }
    }
}

TEST_CASE("B8 B6 governor composition caps advance correction and revoked permission clears output") {
    fsm::Search search;
    governor::Governor governor;
    CHECK(search.start(0U, 0.0F, true, fsm::SearchContext{}));
    auto result = search.step(0U, 0.0F, true, 0U);
    governor.step(0U, requestFor(result, true));
    result = search.step(50000U, 0.0F, true, 0U);
    auto duty = governor.step(50000U, requestFor(result, true));
    CHECK(duty.duty_l == doctest::Approx(0.45F * 11.1F / 9.0F));
    CHECK(duty.duty_r == doctest::Approx(-0.45F * 11.1F / 9.0F));
    result = search.step(50001U, 0.0F, true, 0U);
    duty = governor.step(50001U, requestFor(result, false));
    CHECK(duty.duty_l == 0.0F);
    CHECK(duty.duty_r == 0.0F);
    result = search.step(60000U, 360.0F, true, 0U);
    governor.step(60000U, requestFor(result, true));
    result = search.step(110000U, 370.0F, true, 0U);
    checkActive(result, Phase::ADVANCE, 0.1F, 0.5F);
    duty = governor.step(110000U, requestFor(result, true));
    CHECK(duty.duty_l == doctest::Approx(0.1F * 11.1F / 9.0F));
    CHECK(duty.duty_r == doctest::Approx(0.3F));
    result = search.step(110001U, NAN_YAW, true, 2U);
    checkZero(result, Phase::FINISHED, fsm::Intent::PERCEPTION);
    duty = governor.step(110001U, requestFor(result, true));
    CHECK(duty.duty_l == 0.0F);
    CHECK(duty.duty_r == 0.0F);
}
