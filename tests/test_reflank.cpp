// Checks B11 re-flank selection and execution against D-037/D-038/D-040/D-043.
// Separates phase requests and exact entry notifications from Robot arbitration and motors.
// Independent host tests cover masks, mirrors, histories, timing, fallback and governor composition.
#include "doctest.h"
#include "config.h"
#include "core/fsm.h"
#include "core/governor.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Direction = motion::Direction;
using Phase = fsm::ReflankPhase;
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();

fsm::ReflankResult sample(fsm::Reflank& command, std::uint32_t time, float heading,
                          bool imu = true, std::uint8_t mask = 0U, bool cue = false,
                          float bearing = 0.0F, bool valid = false) {
    return command.step(time, heading, imu, mask, cue, bearing, valid);
}

void checkChoice(const fsm::SwingContext& context, Direction expected) {
    const auto result = fsm::chooseSwing(context);
    CHECK(result.valid);
    CHECK(result.direction == expected);
}

void checkActive(const fsm::ReflankResult& result, Phase phase, float left, float right) {
    CHECK(result.phase == phase);
    CHECK(result.intent == fsm::Intent::NONE);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(right));
    CHECK(result.profile == (phase == Phase::BACK ?
        governor::Profile::REFLANK_BACK : governor::Profile::REFLANK_TURN));
}

void checkZero(const fsm::ReflankResult& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
    CHECK_FALSE(result.motion.imu_fallback);
    CHECK(result.intent == (phase == Phase::INVALID ? fsm::Intent::INVALID :
          phase == Phase::FINISHED ? fsm::Intent::PERCEPTION : fsm::Intent::NONE));
    CHECK(result.motion.status == (phase == Phase::INVALID ? motion::Status::INVALID :
          phase == Phase::FINISHED ? motion::Status::DONE : motion::Status::IDLE));
}

void checkNoEvents(const fsm::ReflankResult& result) {
    CHECK_FALSE(result.entered_swing);
    CHECK_FALSE(result.entered_turn_in);
    CHECK_FALSE(result.turn_timed_out);
}

float signOf(Direction direction) { return direction == Direction::RIGHT ? 1.0F : -1.0F; }
std::uint8_t innerBit(Direction direction) { return direction == Direction::RIGHT ? 8U : 16U; }
bool hasInner(std::uint8_t mask, Direction direction) {
    return (mask & (direction == Direction::RIGHT ? 40U : 80U)) != 0U;
}

// Literal B5 selected bearing; bilateral side/rear fixtures retain a prior -90.
float selectedBearing(std::uint8_t mask) {
    constexpr std::array<float, 8> FRONT{{0.0F, -15.0F, 0.0F, -6.0F, 15.0F, 0.0F, 6.0F, 0.0F}};
    if ((mask & 7U) != 0U) return FRONT[mask & 7U];
    if ((mask & 24U) != 0U) return (mask & 24U) == 16U ? 90.0F : -90.0F;
    if ((mask & 96U) == 64U) return 135.0F;
    return (mask & 96U) == 32U ? -135.0F : -90.0F;
}

void prepare(fsm::Reflank& command, unsigned stage, Direction direction) {
    const float sign = signOf(direction);
    CHECK(command.start(0U, 0.0F, true, direction));
    if (stage == 0U) return;
    checkActive(sample(command, 150000U, 0.0F), Phase::SWING, sign * 0.8F, -sign * 0.8F);
    if (stage == 2U) {
        const auto arc = sample(command, 150001U, sign * 60.0F);
        checkActive(arc, Phase::SWING, sign > 0.0F ? 0.32F : 0.8F,
                    sign > 0.0F ? 0.8F : 0.32F);
    } else if (stage == 3U) {
        checkActive(sample(command, 150001U, 0.0F, true, innerBit(direction), false,
                           -sign * 90.0F, true), Phase::TURN_IN, -sign * 0.8F, sign * 0.8F);
    }
}

governor::Request requestFor(const fsm::ReflankResult& result, bool allowed = true) {
    governor::Request request;
    request.duty_l = result.motion.duty_l;
    request.duty_r = result.motion.duty_r;
    request.profile = result.profile;
    request.vbat_v = 9.0F;
    request.inhibited = !allowed || result.intent != fsm::Intent::NONE;
    return request;
}
} // namespace

TEST_CASE("B11 re-flank literal defaults and idle output are inert") {
    CHECK(config::REFLANK_BACK_MS == 150U);
    CHECK(config::REFLANK_BACK_DUTY == doctest::Approx(0.8F));
    CHECK(config::REFLANK_PIVOT_DEG == 60U);
    CHECK(config::REFLANK_ARC_MS == 400U);
    CHECK(config::REFLANK_ARC_RATIO == doctest::Approx(0.4F));
    CHECK(config::RECENT_EDGE_MS == 5000U);
    fsm::Reflank command;
    const auto result = sample(command, 0U, 0.0F);
    checkZero(result, Phase::IDLE);
    checkNoEvents(result);
}

TEST_CASE("B11 D-037 side selection defaults right and alternates only supplied actual history") {
    fsm::SwingContext context;
    checkChoice(context, Direction::RIGHT);
    checkChoice(context, Direction::RIGHT);
    context.previous_swing_valid = true;
    context.previous_swing = Direction::RIGHT;
    checkChoice(context, Direction::LEFT);
    context.previous_swing = Direction::LEFT;
    checkChoice(context, Direction::RIGHT);
    fsm::Reflank command;
    CHECK(command.start(0U, 0.0F, true, Direction::LEFT));
    command.reset();
    checkChoice(context, Direction::RIGHT);
}

TEST_CASE("B11 D-043 unseen older and equal front histories follow exact selection precedence") {
    fsm::SwingContext context;
    context.previous_swing_valid = true;
    context.previous_swing = Direction::RIGHT;
    context.front_left_age_us = std::numeric_limits<std::uint64_t>::max();
    context.front_right_age_us = 0U;
    checkChoice(context, Direction::LEFT);
    context.front_left_seen = true;
    checkChoice(context, Direction::RIGHT);
    context.front_left_seen = false;
    context.front_right_seen = true;
    checkChoice(context, Direction::LEFT);
    context.front_left_seen = true;
    for (const auto age : std::initializer_list<std::uint64_t>{0U, 1U, 999U,
                                    std::numeric_limits<std::uint64_t>::max() - 1U}) {
        context.front_left_age_us = age;
        context.front_right_age_us = age;
        checkChoice(context, Direction::LEFT);
        context.front_left_age_us = age + 1U;
        checkChoice(context, Direction::LEFT);
        context.front_left_age_us = age;
        context.front_right_age_us = age + 1U;
        checkChoice(context, Direction::RIGHT);
    }
}

TEST_CASE("B11 known recent edge side wins until the strict five second boundary") {
    for (const auto edge : {Direction::LEFT, Direction::RIGHT}) {
        fsm::SwingContext context;
        context.edge_side_valid = true;
        context.edge_side = edge;
        context.front_left_seen = true;
        context.front_right_seen = true;
        context.front_left_age_us = edge == Direction::LEFT ? 2U : 1U;
        context.front_right_age_us = edge == Direction::RIGHT ? 2U : 1U;
        for (const auto age : std::initializer_list<std::uint64_t>{0U, 4999999U, 5000000U,
                               5000001U, std::numeric_limits<std::uint64_t>::max()}) {
            context.edge_age_us = age;
            checkChoice(context, age < 5000000U ?
                (edge == Direction::LEFT ? Direction::RIGHT : Direction::LEFT) : edge);
        }
    }
}

TEST_CASE("B11 chooser validates only consumed enum fields and cannot invent an edge side") {
    const auto invalid = static_cast<Direction>(255U);
    fsm::SwingContext context;
    context.edge_side = invalid;
    context.previous_swing = invalid;
    checkChoice(context, Direction::RIGHT);
    context.edge_side_valid = true;
    CHECK_FALSE(fsm::chooseSwing(context).valid);
    context.edge_age_us = 5000000U;
    checkChoice(context, Direction::RIGHT);
    context.previous_swing_valid = true;
    CHECK_FALSE(fsm::chooseSwing(context).valid);
    context.front_left_seen = true;
    checkChoice(context, Direction::RIGHT);
    context.edge_age_us = 0U;
    CHECK_FALSE(fsm::chooseSwing(context).valid);
    context.edge_side = Direction::RIGHT;
    checkChoice(context, Direction::LEFT);
    context.edge_side_valid = false;
    checkChoice(context, Direction::RIGHT);
}

TEST_CASE("B11 BACK lasts exactly 150 ms and mirrored SWING captures a 60 degree pivot") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        fsm::Reflank command;
        const float sign = signOf(direction);
        CHECK(command.start(10U, 5.0F, true, direction));
        for (const auto time : {10U, 150009U}) {
            const auto result = sample(command, time, 5.0F);
            checkActive(result, Phase::BACK, -0.8F, -0.8F);
            checkNoEvents(result);
        }
        auto result = sample(command, 150010U, 20.0F);
        checkActive(result, Phase::SWING, sign * 0.8F, -sign * 0.8F);
        CHECK(result.direction == direction);
        CHECK(result.entered_swing);
        CHECK_FALSE(result.entered_turn_in);
        result = sample(command, 150011U, 20.0F + sign * 55.0F);
        checkActive(result, Phase::SWING, sign * 0.25F, -sign * 0.25F);
        checkNoEvents(result);
        result = sample(command, 150012U, 20.0F + sign * 60.0F);
        checkActive(result, Phase::SWING, sign > 0.0F ? 0.32F : 0.8F,
                    sign > 0.0F ? 0.8F : 0.32F);
        checkNoEvents(result);
    }
}

TEST_CASE("B11 all masks in BACK ignore detections unless front and current cue qualify charger skip") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (unsigned mask = 0U; mask < 256U; ++mask) {
            for (const bool cue : {false, true}) {
                fsm::Reflank command;
                CHECK(command.start(0U, 0.0F, true, direction));
                const auto bits = static_cast<std::uint8_t>(mask);
                const auto result = sample(command, 1U, 0.0F, true, bits, cue,
                                           selectedBearing(bits), (mask & 127U) != 0U);
                const bool skipped = cue && (mask & 7U) != 0U;
                CHECK(result.entered_swing == skipped);
                CHECK(result.entered_turn_in == (skipped && hasInner(bits, direction)));
                CHECK_FALSE(result.turn_timed_out);
                if (!skipped) checkActive(result, Phase::BACK, -0.8F, -0.8F);
                else if (hasInner(bits, direction)) checkZero(result, Phase::FINISHED);
                else checkActive(result, Phase::SWING, signOf(direction) * 0.8F, -signOf(direction) * 0.8F);
            }
        }
    }
}

TEST_CASE("B11 all masks in both SWING segments use inner detections before motion and ignore front alone") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (unsigned stage = 1U; stage <= 2U; ++stage) {
            for (unsigned mask = 0U; mask < 256U; ++mask) {
                fsm::Reflank command;
                prepare(command, stage, direction);
                const auto bits = static_cast<std::uint8_t>(mask);
                const float heading = stage == 2U ? signOf(direction) * 60.0F : 0.0F;
                const auto result = sample(command, 150002U, heading, true, bits, true,
                                           selectedBearing(bits), (mask & 127U) != 0U);
                CHECK_FALSE(result.entered_swing);
                CHECK(result.entered_turn_in == hasInner(bits, direction));
                CHECK_FALSE(result.turn_timed_out);
                if (!hasInner(bits, direction)) CHECK(result.phase == Phase::SWING);
                else if ((mask & 7U) != 0U) checkZero(result, Phase::FINISHED);
                else CHECK(result.phase == Phase::TURN_IN);
            }
        }
    }
}

TEST_CASE("B11 charger skip consumes the current cue rather than retaining an earlier cue") {
    fsm::Reflank command;
    CHECK(command.start(0U, 0.0F, true, Direction::RIGHT));
    checkActive(sample(command, 1U, 0.0F, true, 0U, true), Phase::BACK, -0.8F, -0.8F);
    checkActive(sample(command, 2U, 0.0F, true, 2U, false), Phase::BACK, -0.8F, -0.8F);
    const auto result = sample(command, 3U, 0.0F, true, 2U, true);
    checkActive(result, Phase::SWING, 0.8F, -0.8F);
    CHECK(result.entered_swing);
    CHECK_FALSE(result.entered_turn_in);
}

TEST_CASE("B11 D-040 all TURN_IN masks retain the captured command except current front") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (unsigned mask = 0U; mask < 256U; ++mask) {
            fsm::Reflank command;
            prepare(command, 3U, direction);
            const bool front = (mask & 7U) != 0U;
            const auto result = sample(command, 150002U, front ? NAN_YAW : 0.0F,
                                       true, static_cast<std::uint8_t>(mask), true, NAN_YAW, false);
            if (front) checkZero(result, Phase::FINISHED);
            else checkActive(result, Phase::TURN_IN, -signOf(direction) * 0.8F, signOf(direction) * 0.8F);
            checkNoEvents(result);
        }
    }
}

TEST_CASE("B11 D-037 opposite arc is time only and completes exactly 400 ms after entry") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        fsm::Reflank command;
        prepare(command, 2U, direction);
        const float sign = signOf(direction);
        for (const auto time : {150002U, 550000U}) {
            const auto result = sample(command, time, -sign * 10000.0F);
            checkActive(result, Phase::SWING, sign > 0.0F ? 0.32F : 0.8F,
                        sign > 0.0F ? 0.8F : 0.32F);
            checkNoEvents(result);
        }
        auto result = sample(command, 550001U, 0.0F);
        checkZero(result, Phase::FINISHED);
        checkNoEvents(result);
        result = sample(command, 550002U, NAN_YAW, true, 127U, true, NAN_YAW, false);
        checkZero(result, Phase::FINISHED);
        checkNoEvents(result);
    }
}

TEST_CASE("B11 D-040 inner trigger wins pivot timeout and natural arc expiry ties") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (unsigned stage = 1U; stage <= 2U; ++stage) {
            fsm::Reflank command;
            prepare(command, stage, direction);
            const auto time = stage == 1U ? 850000U : 550001U;
            const float heading = stage == 1U ? 0.0F : signOf(direction) * 60.0F;
            const auto result = sample(command, time, heading, true, innerBit(direction),
                                       false, -signOf(direction) * 90.0F, true);
            checkActive(result, Phase::TURN_IN, -signOf(direction) * 0.8F, signOf(direction) * 0.8F);
            CHECK(result.entered_turn_in);
            CHECK_FALSE(result.entered_swing);
            CHECK_FALSE(result.turn_timed_out);
        }
    }
}

TEST_CASE("B11 natural arc completion uses perception for every mask lacking an inner trigger") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (unsigned mask = 0U; mask < 256U; ++mask) {
            const auto bits = static_cast<std::uint8_t>(mask);
            if (hasInner(bits, direction)) continue;
            fsm::Reflank command;
            prepare(command, 2U, direction);
            const auto result = sample(command, 550001U, 0.0F, true, bits, false, NAN_YAW, false);
            checkZero(result, Phase::FINISHED);
            checkNoEvents(result);
        }
    }
}

TEST_CASE("B11 B15 same tick entry flags preserve SWING then TURN_IN including immediate exits") {
    for (const bool front : {false, true}) {
        fsm::Reflank command;
        CHECK(command.start(0U, 0.0F, true, Direction::RIGHT));
        const auto time = front ? 1U : 150000U;
        const std::uint8_t mask = front ? 10U : 8U;
        auto result = sample(command, time, 0.0F, true, mask, front,
                             front ? 0.0F : -90.0F, true);
        CHECK(result.entered_swing);
        CHECK(result.entered_turn_in);
        CHECK_FALSE(result.turn_timed_out);
        if (front) checkZero(result, Phase::FINISHED);
        else checkActive(result, Phase::TURN_IN, -0.8F, 0.8F);
        result = sample(command, time + 1U, 0.0F);
        checkNoEvents(result);
    }
}

TEST_CASE("B11 B7 reverse pivot and TURN_IN capture their own headings without retargeting") {
    fsm::Reflank command;
    CHECK(command.start(0U, 5.0F, true, Direction::RIGHT));
    checkActive(sample(command, 1U, 15.0F), Phase::BACK, -1.0F, -0.6F);
    checkActive(sample(command, 150000U, 20.0F), Phase::SWING, 0.8F, -0.8F);
    checkActive(sample(command, 150001U, 75.0F), Phase::SWING, 0.25F, -0.25F);
    checkActive(sample(command, 150002U, 80.0F), Phase::SWING, 0.32F, 0.8F);
    checkActive(sample(command, 150003U, 100.0F, true, 8U, false, -90.0F, true),
                Phase::TURN_IN, -0.8F, 0.8F);
    checkActive(sample(command, 150004U, 30.0F, true, 64U, false, 135.0F, true),
                Phase::TURN_IN, -0.4F, 0.4F);
    checkZero(sample(command, 150005U, 10.0F, true, 0U, false, NAN_YAW, false), Phase::FINISHED);
}

TEST_CASE("B11 B7 TURN_IN uses strict five degree tolerance on both sides of the captured target") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        for (const float magnitude : {std::nextafter(5.0F, 0.0F), 5.0F, std::nextafter(5.0F, 6.0F)}) {
            for (const float offset : {-1.0F, 1.0F}) {
                fsm::Reflank command;
                const float initial = signOf(direction) * 90.0F;
                CHECK(command.start(0U, initial, true, direction));
                sample(command, 150000U, initial);
                sample(command, 150001U, initial, true, innerBit(direction), false, -initial, true);
                const auto result = sample(command, 150002U, offset * magnitude);
                if (magnitude < 5.0F) checkZero(result, Phase::FINISHED);
                else checkActive(result, Phase::TURN_IN, -offset * 0.25F, offset * 0.25F);
                checkNoEvents(result);
            }
        }
    }
}

TEST_CASE("B11 B7 pivot timeout enters arc and TURN_IN timeout exits with single pulses") {
    fsm::Reflank command;
    prepare(command, 1U, Direction::RIGHT);
    checkActive(sample(command, 849999U, 0.0F), Phase::SWING, 0.8F, -0.8F);
    auto result = sample(command, 850000U, 60.0F);
    checkActive(result, Phase::SWING, 0.32F, 0.8F);
    CHECK(result.turn_timed_out);
    CHECK_FALSE(result.entered_swing);
    CHECK_FALSE(result.entered_turn_in);
    checkNoEvents(sample(command, 850001U, 60.0F));
    prepare(command, 3U, Direction::RIGHT);
    checkActive(sample(command, 850000U, 0.0F), Phase::TURN_IN, -0.8F, 0.8F);
    result = sample(command, 850001U, -90.0F);
    checkZero(result, Phase::FINISHED);
    CHECK(result.turn_timed_out);
    checkNoEvents(sample(command, 850002U, -90.0F));
    prepare(command, 3U, Direction::RIGHT);
    result = sample(command, 850001U, NAN_YAW, true, 2U);
    checkZero(result, Phase::FINISHED);
    checkNoEvents(result);
}

TEST_CASE("B11 B7 initial and recovered IMU fallback preserves 120 ms pivot timing then 400 ms arc") {
    fsm::Reflank command;
    CHECK(command.start(0U, 10.0F, false, Direction::RIGHT));
    CHECK(sample(command, 149999U, NAN_YAW, false).motion.imu_fallback);
    auto result = sample(command, 150000U, NAN_YAW, false);
    checkActive(result, Phase::SWING, 0.8F, -0.8F);
    CHECK(result.motion.imu_fallback);
    result = sample(command, 269999U, 70.0F, true);
    checkActive(result, Phase::SWING, 0.8F, -0.8F);
    CHECK(result.motion.imu_fallback);
    checkActive(sample(command, 270000U, 70.0F), Phase::SWING, 0.32F, 0.8F);
    checkActive(sample(command, 669999U, NAN_YAW, false), Phase::SWING, 0.32F, 0.8F);
    checkZero(sample(command, 670000U, NAN_YAW, false), Phase::FINISHED);
}

TEST_CASE("B11 B7 mid-pivot IMU loss times the last remaining angle without recovery extension") {
    fsm::Reflank command;
    prepare(command, 1U, Direction::RIGHT);
    sample(command, 151000U, 30.0F);
    CHECK(sample(command, 152000U, NAN_YAW, false).motion.imu_fallback);
    auto result = sample(command, 211999U, 60.0F);
    checkActive(result, Phase::SWING, 0.8F, -0.8F);
    CHECK(result.motion.imu_fallback);
    checkActive(sample(command, 212000U, 60.0F), Phase::SWING, 0.32F, 0.8F);
}

TEST_CASE("B11 B7 TURN_IN fallback captures last healthy yaw and ignores unavailable replacements") {
    fsm::Reflank command;
    CHECK(command.start(0U, 5.0F, true, Direction::RIGHT));
    sample(command, 149999U, 20.0F);
    sample(command, 150000U, NAN_YAW, false);
    auto result = sample(command, 150001U, NAN_YAW, false, 8U, false, -90.0F, true);
    checkActive(result, Phase::TURN_IN, -0.8F, 0.8F);
    CHECK(result.motion.imu_fallback);
    result = sample(command, 330000U, -70.0F);
    checkActive(result, Phase::TURN_IN, -0.8F, 0.8F);
    CHECK(result.motion.imu_fallback);
    result = sample(command, 330001U, -70.0F);
    checkZero(result, Phase::FINISHED);
    CHECK_FALSE(result.turn_timed_out);
}

TEST_CASE("B11 delayed phase observations start fresh segment timers rather than backdating") {
    fsm::Reflank command;
    CHECK(command.start(0U, 0.0F, false, Direction::RIGHT));
    checkActive(sample(command, 1000000U, NAN_YAW, false), Phase::SWING, 0.8F, -0.8F);
    checkActive(sample(command, 1119999U, NAN_YAW, false), Phase::SWING, 0.8F, -0.8F);
    checkActive(sample(command, 1120000U, NAN_YAW, false), Phase::SWING, 0.32F, 0.8F);
    checkActive(sample(command, 1519999U, NAN_YAW, false), Phase::SWING, 0.32F, 0.8F);
    checkZero(sample(command, 1520000U, NAN_YAW, false), Phase::FINISHED);
}

TEST_CASE("B11 only required TURN_IN bearings are validated") {
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity(), -180.0F,
                            -181.0F, std::nextafter(180.0F, 181.0F)}) {
        fsm::Reflank command;
        CHECK(command.start(0U, 0.0F, true, Direction::RIGHT));
        checkActive(sample(command, 1U, 0.0F, true, 0U, false, bad, true), Phase::BACK, -0.8F, -0.8F);
        sample(command, 150000U, 0.0F);
        checkActive(sample(command, 150001U, 0.0F, true, 16U, false, bad, true), Phase::SWING, 0.8F, -0.8F);
        checkZero(sample(command, 150002U, 0.0F, true, 8U, false, bad, true), Phase::INVALID);
    }
    fsm::Reflank command;
    prepare(command, 1U, Direction::RIGHT);
    checkZero(sample(command, 150001U, 0.0F, true, 8U, false, -90.0F, false), Phase::INVALID);
    for (const float bearing : {std::nextafter(-180.0F, 0.0F), 180.0F}) {
        prepare(command, 1U, Direction::RIGHT);
        CHECK(sample(command, 150001U, 0.0F, true, 8U, false, bearing, true).phase == Phase::TURN_IN);
    }
}

TEST_CASE("B11 invalid start and healthy nonfinite yaw stop all active private stages") {
    fsm::Reflank command;
    CHECK_FALSE(command.start(0U, 0.0F, true, static_cast<Direction>(255U)));
    checkZero(sample(command, 0U, 0.0F), Phase::INVALID);
    for (const float bad : {NAN_YAW, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        for (const bool imu : {false, true}) {
            CHECK_FALSE(command.start(0U, bad, imu, Direction::RIGHT));
            checkZero(sample(command, 0U, 0.0F), Phase::INVALID);
        }
        for (unsigned stage = 0U; stage < 4U; ++stage) {
            prepare(command, stage, Direction::RIGHT);
            checkZero(sample(command, 150002U, bad), Phase::INVALID);
            const auto retained = sample(command, 150003U, 0.0F, true, 127U, true, 0.0F, true);
            checkZero(retained, Phase::INVALID);
            checkNoEvents(retained);
        }
    }
}

TEST_CASE("B11 finite huge headings preserve relative pivot and bounded TURN_IN capture") {
    for (const float heading : {std::numeric_limits<float>::max(), -std::numeric_limits<float>::max()}) {
        for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
            fsm::Reflank command;
            const float sign = signOf(direction);
            CHECK(command.start(0U, heading, true, direction));
            checkActive(sample(command, 0U, heading), Phase::BACK, -0.8F, -0.8F);
            checkActive(sample(command, 150000U, heading), Phase::SWING, sign * 0.8F, -sign * 0.8F);
            auto result = sample(command, 150001U, heading, true, innerBit(direction), false, -sign * 90.0F, true);
            checkActive(result, Phase::TURN_IN, -sign * 0.8F, sign * 0.8F);
            const float target = static_cast<float>(std::fmod(static_cast<double>(heading), 360.0) - sign * 90.0);
            checkZero(sample(command, 150002U, target), Phase::FINISHED);
        }
    }
}

TEST_CASE("B7 B11 exact positive 180 degree TURN_IN tie remains RIGHT at every finite capture") {
    for (const float heading : {-0.000001F, 0.000001F, 0.0F, 30.0F, -170.0F,
                                36000000.0F, std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max()}) {
        fsm::Reflank command;
        CHECK(command.start(0U, heading, true, Direction::RIGHT));
        sample(command, 150000U, heading);
        const auto result = sample(command, 150001U, heading, true, 8U, false, 180.0F, true);
        checkActive(result, Phase::TURN_IN, 0.8F, -0.8F);
        CHECK(result.entered_turn_in);
        CHECK_FALSE(result.turn_timed_out);
    }
}

TEST_CASE("B11 exact fallback segment deadlines survive micros wrap") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 50U;
    fsm::Reflank command;
    CHECK(command.start(start, 0.0F, false, Direction::LEFT));
    checkActive(sample(command, start + 149999U, NAN_YAW, false), Phase::BACK, -0.8F, -0.8F);
    checkActive(sample(command, start + 150000U, NAN_YAW, false), Phase::SWING, -0.8F, 0.8F);
    checkActive(sample(command, start + 269999U, NAN_YAW, false), Phase::SWING, -0.8F, 0.8F);
    checkActive(sample(command, start + 270000U, NAN_YAW, false), Phase::SWING, 0.8F, 0.32F);
    checkActive(sample(command, start + 669999U, NAN_YAW, false), Phase::SWING, 0.8F, 0.32F);
    checkZero(sample(command, start + 670000U, NAN_YAW, false), Phase::FINISHED);
}

TEST_CASE("B11 delayed legal gaps span several wraps with fresh phase starts and one timeout pulse") {
    std::uint32_t time = 42U;
    constexpr std::uint32_t GAP = std::numeric_limits<std::uint32_t>::max() - 9U;
    fsm::Reflank command;
    CHECK(command.start(time, 0.0F, true, Direction::RIGHT));
    time += GAP;
    CHECK(sample(command, time, 0.0F).entered_swing);
    time += GAP;
    auto result = sample(command, time, 0.0F);
    checkActive(result, Phase::SWING, 0.32F, 0.8F);
    CHECK(result.turn_timed_out);
    CHECK_FALSE(result.entered_swing);
    time += GAP;
    result = sample(command, time, 0.0F);
    checkZero(result, Phase::FINISHED);
    checkNoEvents(result);
}

TEST_CASE("B11 restart and reset clear terminal state entry flags and fallback") {
    fsm::Reflank command;
    CHECK(command.start(0U, 0.0F, false, Direction::RIGHT));
    const auto finish = sample(command, 1U, NAN_YAW, false, 10U, true, 0.0F, true);
    checkZero(finish, Phase::FINISHED);
    CHECK(finish.entered_swing);
    CHECK(finish.entered_turn_in);
    command.reset();
    checkZero(sample(command, 2U, 0.0F), Phase::IDLE);
    CHECK(command.start(3U, 0.0F, true, Direction::LEFT));
    auto result = sample(command, 3U, 0.0F);
    checkActive(result, Phase::BACK, -0.8F, -0.8F);
    checkNoEvents(result);
    CHECK_FALSE(result.motion.imu_fallback);
    checkZero(sample(command, 4U, NAN_YAW), Phase::INVALID);
    CHECK(command.start(5U, 0.0F, true, Direction::RIGHT));
    result = sample(command, 5U, 0.0F);
    checkActive(result, Phase::BACK, -0.8F, -0.8F);
    checkNoEvents(result);
}

TEST_CASE("B11 B6 low-voltage governor composition caps reverse pivot and arc without bypassing permission") {
    fsm::Reflank command;
    governor::Governor governor;
    CHECK(command.start(0U, 0.0F, true, Direction::RIGHT));
    governor.step(0U, requestFor(sample(command, 0U, 0.0F)));
    auto result = sample(command, 100000U, 0.0F);
    auto duty = governor.step(100000U, requestFor(result));
    CHECK(duty.duty_l == doctest::Approx(-0.8F));
    CHECK(duty.duty_r == doctest::Approx(-0.8F));
    result = sample(command, 150000U, 0.0F);
    duty = governor.step(150000U, requestFor(result));
    CHECK(duty.duty_l == 0.0F);
    CHECK(duty.duty_r == doctest::Approx(-0.8F));
    result = sample(command, 200000U, 0.0F);
    duty = governor.step(200000U, requestFor(result));
    CHECK(duty.duty_l == doctest::Approx(0.8F));
    result = sample(command, 200001U, 60.0F);
    duty = governor.step(200001U, requestFor(result));
    CHECK(duty.duty_r == 0.0F);
    result = sample(command, 250001U, 60.0F);
    duty = governor.step(250001U, requestFor(result));
    CHECK(duty.duty_l == doctest::Approx(0.32F * 11.1F / 9.0F));
    CHECK(duty.duty_r == doctest::Approx(0.8F));
    duty = governor.step(250002U, requestFor(sample(command, 250002U, 60.0F), false));
    CHECK(duty.duty_l == 0.0F);
    CHECK(duty.duty_r == 0.0F);
    checkZero(sample(command, 600001U, 60.0F), Phase::FINISHED);
}
