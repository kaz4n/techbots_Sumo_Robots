// Checks B12 O4 WAIT and the approved D-055 complete SIDESTEP_R delegation.
// Keeps ordered approach evidence separate from perception routing and motor permission.
// Independent host tests cover timing, phase priorities, finite yaw and governor composition.
#include "doctest.h"
#include "config.h"
#include "core/fsm.h"
#include "core/governor.h"
#include "core/openers.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Phase = openers::WaitPhase;
using FlankPhase = openers::Phase;
using Exit = openers::Exit;
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_YAW = std::numeric_limits<float>::infinity();

openers::Sample sample(std::uint32_t time, std::uint8_t mask = 0U,
                       float yaw = 0.0F, bool healthy = true) {
    openers::Sample result;
    result.t_us = time;
    result.confirmed_mask = mask;
    result.heading_deg = yaw;
    result.imu_ok = healthy;
    return result;
}

void checkZero(const openers::WaitResult& result) {
    CHECK(result.brake);
    CHECK(result.flank.motion.duty_l == 0.0F);
    CHECK(result.flank.motion.duty_r == 0.0F);
    CHECK_FALSE(result.flank.motion.imu_fallback);
}

void checkNoPulses(const openers::WaitResult& result) {
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.approach_cue);
    CHECK_FALSE(result.flank.phase_changed);
    CHECK_FALSE(result.flank.motion_timed_out);
}

void checkHold(const openers::WaitResult& result) {
    CHECK(result.phase == Phase::HOLD);
    CHECK(result.flank.phase == FlankPhase::IDLE);
    CHECK(result.flank.exit == Exit::NONE);
    CHECK(result.flank.motion.status == motion::Status::ACTIVE);
    CHECK(result.flank.profile == governor::Profile::OPENER);
    CHECK_FALSE(result.flank.scan_hint_valid);
    checkZero(result);
    checkNoPulses(result);
}

void checkTerminal(const openers::WaitResult& result, Exit exit) {
    const bool invalid = exit == Exit::INVALID;
    CHECK(result.phase == (invalid ? Phase::INVALID : Phase::FINISHED));
    CHECK(result.flank.phase == (invalid ? FlankPhase::INVALID : FlankPhase::FINISHED));
    CHECK(result.flank.motion.status == (invalid ? motion::Status::INVALID : motion::Status::DONE));
    CHECK(result.flank.exit == exit);
    checkZero(result);
}

void checkMoving(const openers::WaitResult& result, FlankPhase phase,
                 float left, float right) {
    CHECK(result.phase == Phase::FLANK);
    CHECK(result.flank.phase == phase);
    CHECK(result.flank.exit == Exit::NONE);
    CHECK(result.flank.motion.status == motion::Status::ACTIVE);
    CHECK_FALSE(result.brake);
    CHECK(result.flank.motion.duty_l == doctest::Approx(left));
    CHECK(result.flank.motion.duty_r == doctest::Approx(right));
    CHECK(result.flank.profile == (phase == FlankPhase::TRAVERSE ?
          governor::Profile::OPENER : governor::Profile::PIVOT));
}

void checkCue(const openers::WaitResult& result) {
    checkMoving(result, FlankPhase::PIVOT, 0.8F, -0.8F);
    CHECK(result.phase_changed);
    CHECK(result.approach_cue);
    CHECK_FALSE(result.flank.phase_changed);
    CHECK_FALSE(result.flank.motion_timed_out);
}

void beginFlank(openers::Wait& wait, std::uint32_t base = 0U, float yaw = 0.0F) {
    CHECK(wait.start(base, yaw));
    checkHold(wait.step(sample(base, 2U, yaw)));
    checkCue(wait.step(sample(base + 1U, 3U, yaw)));
}

void prepare(openers::Wait& wait, unsigned phase) {
    beginFlank(wait);
    if (phase == 0U) return;
    checkMoving(wait.step(sample(2U, 0U, 50.0F)), FlankPhase::TRAVERSE, 0.85F, 0.85F);
    if (phase == 1U) return;
    checkMoving(wait.step(sample(3U, 8U, 50.0F)), FlankPhase::TURN_IN, -0.8F, 0.8F);
}

governor::Request governed(const openers::WaitResult& result, bool permission = true) {
    governor::Request request;
    request.duty_l = result.flank.motion.duty_l;
    request.duty_r = result.flank.motion.duty_r;
    request.profile = result.flank.profile;
    request.brake = result.brake;
    request.inhibited = !permission;
    request.vbat_v = 9.0F;
    return request;
}

void checkDutyZero(const governor::Result& result) {
    CHECK(result.valid);
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
}
} // namespace

TEST_CASE("B12 O4 WAIT literal approved timing and full-sidestep defaults") {
    CHECK(config::WAIT_MAX_MS == 2000U);
    CHECK(config::APPROACH_WINDOW_MS == 300U);
    CHECK(config::SS_PIVOT_DEG == 50U);
    CHECK(config::SS_DRIVE_MS == 250U);
    CHECK(config::SS_TURNIN_DEG == 110U);
    CHECK(config::TURN_TIMEOUT_MS == 700U);
    CHECK(config::TURN_MS_PER_DEG == 2.0F);
}

TEST_CASE("B12 O4 WAIT idle start and reset are zero without entry pulses") {
    openers::Wait wait;
    auto result = wait.step(sample(100U, 127U, NAN_YAW));
    CHECK(result.phase == Phase::IDLE);
    CHECK(result.flank.phase == FlankPhase::IDLE);
    CHECK(result.flank.motion.status == motion::Status::IDLE);
    CHECK(result.flank.exit == Exit::NONE);
    checkZero(result);
    checkNoPulses(result);
    CHECK(wait.start(100U, 10.0F));
    checkHold(wait.step(sample(100U, 0U, 10.0F)));
    wait.reset();
    result = wait.step(sample(200U, 2U));
    CHECK(result.phase == Phase::IDLE);
    CHECK(result.flank.motion.status == motion::Status::IDLE);
    checkZero(result);
    checkNoPulses(result);
}

TEST_CASE("B12 O4 WAIT all 256 initial masks brake or abort without unordered cues") {
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        CAPTURE(mask);
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        const auto result = wait.step(sample(0U, static_cast<std::uint8_t>(mask)));
        if ((mask & 0x78U) != 0U) {
            checkTerminal(result, Exit::SIDE_OR_REAR_TARGET);
            CHECK(result.phase_changed);
        } else {
            checkHold(result);
        }
        CHECK_FALSE(result.approach_cue);
    }
}

TEST_CASE("B12 O4 D055 cue window includes 300000us and excludes its next microsecond") {
    for (const auto elapsed : {299999U, 300000U, 300001U}) {
        for (const auto flank : {1U, 4U, 5U}) {
            CAPTURE(elapsed);
            CAPTURE(flank);
            openers::Wait wait;
            CHECK(wait.start(0U, 0.0F));
            checkHold(wait.step(sample(100U, 2U)));
            const auto result = wait.step(sample(100U + elapsed,
                static_cast<std::uint8_t>(2U | flank)));
            if (elapsed <= 300000U) checkCue(result);
            else checkHold(result);
        }
    }
}

TEST_CASE("B12 O4 initial simultaneous fronts and preheld flanks cannot invent ordering") {
    for (const auto mask : {3U, 6U, 7U}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(0U, static_cast<std::uint8_t>(mask))));
        checkHold(wait.step(sample(1U, static_cast<std::uint8_t>(mask))));
        checkHold(wait.step(sample(299999U, static_cast<std::uint8_t>(mask))));
    }
    for (const auto flank : {1U, 4U}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(0U, static_cast<std::uint8_t>(flank))));
        checkHold(wait.step(sample(100U, static_cast<std::uint8_t>(2U | flank))));
        checkHold(wait.step(sample(101U, static_cast<std::uint8_t>(2U | flank))));
        checkCue(wait.step(sample(102U, 7U)));
    }
}

TEST_CASE("B12 O4 a flank may clear and newly rise during one continuous FC episode") {
    for (const auto flank : {1U, 4U}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(0U, static_cast<std::uint8_t>(2U | flank))));
        checkHold(wait.step(sample(1U, 2U)));
        checkCue(wait.step(sample(300000U, static_cast<std::uint8_t>(2U | flank))));
    }
}

TEST_CASE("B12 O4 fronts without FC and late first FC stay stationary") {
    openers::Wait wait;
    CHECK(wait.start(0U, 0.0F));
    for (unsigned i = 0U; i < 12U; ++i) {
        checkHold(wait.step(sample(i * 1000U,
            static_cast<std::uint8_t>(i % 3U == 0U ? 1U : i % 3U == 1U ? 4U : 5U))));
    }
    checkHold(wait.step(sample(1000000U, 7U)));
    checkHold(wait.step(sample(1000001U, 7U)));
}

TEST_CASE("B12 O4 held FC never refreshes or rearms an expired approach window") {
    openers::Wait wait;
    CHECK(wait.start(0U, 0.0F));
    checkHold(wait.step(sample(0U, 2U)));
    checkHold(wait.step(sample(299999U, 2U)));
    checkHold(wait.step(sample(300001U, 3U)));
    checkHold(wait.step(sample(400000U, 2U)));
    checkHold(wait.step(sample(400001U, 6U)));
    checkHold(wait.step(sample(500000U, 2U)));
    checkHold(wait.step(sample(500001U, 7U)));
}

TEST_CASE("B12 O4 FC clear cancels the episode and permits a new full window") {
    openers::Wait wait;
    CHECK(wait.start(0U, 0.0F));
    checkHold(wait.step(sample(0U, 2U)));
    checkHold(wait.step(sample(200000U, 0U)));
    checkHold(wait.step(sample(300000U, 1U)));
    checkHold(wait.step(sample(400000U, 3U)));
    checkHold(wait.step(sample(400001U, 3U)));
    checkCue(wait.step(sample(700000U, 7U)));
}

TEST_CASE("B12 O4 initial front masks do not change the exact 2 second wait limit") {
    for (unsigned mask = 0U; mask < 8U; ++mask) {
        openers::Wait wait;
        CHECK(wait.start(19U, 0.0F));
        checkHold(wait.step(sample(19U, static_cast<std::uint8_t>(mask))));
        checkHold(wait.step(sample(2000018U, static_cast<std::uint8_t>(mask))));
        auto result = wait.step(sample(2000019U, static_cast<std::uint8_t>(mask)));
        checkTerminal(result, Exit::SEARCH);
        CHECK(result.phase_changed);
        CHECK_FALSE(result.approach_cue);
        result = wait.step(sample(2000020U, 127U, NAN_YAW));
        checkTerminal(result, Exit::SEARCH);
        checkNoPulses(result);
    }
}

TEST_CASE("B12 O4 valid ordered cue wins exact and delayed wait expiry observations") {
    for (const auto cue_time : {1999999U, 2000000U, 2000001U, 2150000U}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(1900000U, 2U)));
        checkCue(wait.step(sample(cue_time, 3U)));
        checkMoving(wait.step(sample(cue_time + 1U, 0U)),
                    FlankPhase::PIVOT, 0.8F, -0.8F);
    }
}

TEST_CASE("B12 O4 expired cue cannot replace SEARCH at the wait deadline") {
    for (const auto fc_time : {1699999U, 1700000U, 1700001U}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(fc_time, 2U)));
        const auto result = wait.step(sample(2000000U, 3U));
        if (fc_time == 1699999U) {
            checkTerminal(result, Exit::SEARCH);
            CHECK_FALSE(result.approach_cue);
        } else checkCue(result);
    }
}

TEST_CASE("B12 O4 side rear abort wins cue deadline and invalid healthy yaw") {
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        if ((mask & 0x78U) == 0U) continue;
        CAPTURE(mask);
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(1900000U, 2U)));
        const auto result = wait.step(sample(2000000U,
            static_cast<std::uint8_t>(mask), NAN_YAW));
        checkTerminal(result, Exit::SIDE_OR_REAR_TARGET);
        CHECK(result.phase_changed);
        CHECK_FALSE(result.approach_cue);
        CHECK_FALSE(result.flank.motion_timed_out);
    }
}

TEST_CASE("B12 O4 healthy nonfinite yaw wins a cue and deadline when no side exists") {
    for (const auto yaw : {NAN_YAW, INF_YAW, -INF_YAW}) {
        for (const auto mask : {0U, 3U}) {
            openers::Wait wait;
            CHECK(wait.start(0U, 0.0F));
            checkHold(wait.step(sample(1900000U, 2U)));
            auto result = wait.step(sample(2000000U, static_cast<std::uint8_t>(mask), yaw));
            checkTerminal(result, Exit::INVALID);
            CHECK(result.phase_changed);
            CHECK_FALSE(result.approach_cue);
            result = wait.step(sample(2000001U, 16U, 0.0F));
            checkTerminal(result, Exit::INVALID);
            checkNoPulses(result);
        }
    }
}

TEST_CASE("B12 O4 initial nonfinite capture is invalid and finite restart clears it") {
    for (const auto yaw : {NAN_YAW, INF_YAW, -INF_YAW}) {
        openers::Wait wait;
        CHECK_FALSE(wait.start(0U, yaw));
        checkTerminal(wait.step(sample(1U)), Exit::INVALID);
        CHECK(wait.start(2U, 725.0F));
        checkHold(wait.step(sample(2U, 2U, 725.0F)));
        checkCue(wait.step(sample(3U, 3U, 725.0F)));
    }
}

TEST_CASE("B12 O4 cue captures current healthy yaw rather than WAIT start heading") {
    openers::Wait wait;
    CHECK(wait.start(0U, -20.0F));
    checkHold(wait.step(sample(100U, 2U, 10.0F)));
    checkCue(wait.step(sample(101U, 3U, 30.0F)));
    auto result = wait.step(sample(102U, 0U, 75.0F));
    checkMoving(result, FlankPhase::PIVOT, 0.25F, -0.25F);
    CHECK_FALSE(result.phase_changed);
    result = wait.step(sample(103U, 0U, std::nextafter(75.0F, 80.0F)));
    CHECK(result.flank.phase == FlankPhase::TRAVERSE);
    CHECK(result.flank.phase_changed);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.approach_cue);
}

TEST_CASE("B12 O4 unavailable yaw uses retained coordinate and latched 100ms pivot fallback") {
    openers::Wait wait;
    CHECK(wait.start(0U, -20.0F));
    checkHold(wait.step(sample(0U, 2U, 30.0F)));
    auto result = wait.step(sample(100U, 3U, NAN_YAW, false));
    checkCue(result);
    CHECK(result.flank.motion.imu_fallback);
    result = wait.step(sample(101U, 0U, 80.0F));
    checkMoving(result, FlankPhase::PIVOT, 0.8F, -0.8F);
    CHECK(result.flank.motion.imu_fallback);
    result = wait.step(sample(100099U, 0U, INF_YAW, false));
    checkMoving(result, FlankPhase::PIVOT, 0.8F, -0.8F);
    result = wait.step(sample(100100U, 0U, NAN_YAW, false));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    CHECK(result.flank.phase_changed);
    CHECK_FALSE(result.phase_changed);
    CHECK_FALSE(result.flank.motion_timed_out);
}

TEST_CASE("B12 O4 held unavailable samples cannot overwrite the last finite coordinate") {
    openers::Wait wait;
    CHECK(wait.start(0U, 5.0F));
    checkHold(wait.step(sample(1U, 0U, 25.0F)));
    checkHold(wait.step(sample(2U, 2U, 1000.0F, false)));
    checkCue(wait.step(sample(3U, 3U, NAN_YAW, false)));
    auto result = wait.step(sample(100003U, 0U, NAN_YAW, false));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    result = wait.step(sample(100004U, 0U, 25.0F));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
}

TEST_CASE("B12 O4 both approach flank signs always select the complete RIGHT pivot") {
    for (const auto mask : {3U, 6U, 7U, 131U, 134U, 135U}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(0U, 2U)));
        checkCue(wait.step(sample(1U, static_cast<std::uint8_t>(mask))));
        const auto result = wait.step(sample(2U, static_cast<std::uint8_t>(mask), 50.0F));
        checkTerminal(result, Exit::FRONT_TARGET);
        CHECK(result.phase_changed);
        CHECK(result.flank.phase_changed);
        CHECK_FALSE(result.approach_cue);
    }
}

TEST_CASE("B12 O4 delegated SIDESTEP phases retain every literal front and side priority") {
    for (unsigned phase = 0U; phase < 3U; ++phase) {
        for (unsigned mask = 0U; mask < 256U; ++mask) {
            CAPTURE(phase);
            CAPTURE(mask);
            openers::Wait wait;
            prepare(wait, phase);
            const auto result = wait.step(sample(10U, static_cast<std::uint8_t>(mask),
                                                phase == 0U ? 0.0F : 50.0F));
            if (phase != 0U && (mask & 7U) != 0U) {
                checkTerminal(result, Exit::FRONT_TARGET);
            } else if ((mask & 80U) != 0U) {
                checkTerminal(result, Exit::SIDE_OR_REAR_TARGET);
            } else {
                const auto expected = phase == 0U ? FlankPhase::PIVOT :
                    phase == 2U || (mask & 40U) != 0U ? FlankPhase::TURN_IN : FlankPhase::TRAVERSE;
                CHECK(result.phase == Phase::FLANK);
                CHECK(result.flank.phase == expected);
                CHECK(result.flank.exit == Exit::NONE);
                CHECK_FALSE(result.brake);
            }
            CHECK_FALSE(result.approach_cue);
            CHECK(std::isfinite(result.flank.motion.duty_l));
            CHECK(std::isfinite(result.flank.motion.duty_r));
            CHECK(std::fabs(result.flank.motion.duty_l) <= 1.0F);
            CHECK(std::fabs(result.flank.motion.duty_r) <= 1.0F);
        }
    }
}

TEST_CASE("B12 O4 delegated drive runs 250ms then fixed left 110 degree turn and hint") {
    openers::Wait wait;
    beginFlank(wait);
    auto result = wait.step(sample(100U, 0U, 50.0F));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    CHECK(result.flank.phase_changed);
    CHECK_FALSE(result.phase_changed);
    result = wait.step(sample(250099U, 0U, 50.0F));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    checkNoPulses(result);
    result = wait.step(sample(250100U, 0U, 50.0F));
    checkMoving(result, FlankPhase::TURN_IN, -0.8F, 0.8F);
    CHECK(result.flank.phase_changed);
    CHECK_FALSE(result.phase_changed);
    result = wait.step(sample(250101U, 0U, -55.0F));
    checkMoving(result, FlankPhase::TURN_IN, -0.25F, 0.25F);
    result = wait.step(sample(250102U, 0U, std::nextafter(-55.0F, -60.0F)));
    checkTerminal(result, Exit::SEARCH);
    CHECK(result.phase_changed);
    CHECK(result.flank.phase_changed);
    CHECK(result.flank.scan_hint_valid);
    CHECK(result.flank.scan_direction == motion::Direction::LEFT);
    result = wait.step(sample(250103U, 127U, NAN_YAW));
    checkTerminal(result, Exit::SEARCH);
    checkNoPulses(result);
}

TEST_CASE("B12 O4 delegated turn target is captured once and ignores later bearing payload") {
    openers::Wait wait;
    prepare(wait, 1U);
    auto observation = sample(3U, 8U, 70.0F);
    observation.bearing_valid = true;
    observation.bearing_deg = NAN_YAW;
    checkMoving(wait.step(observation), FlankPhase::TURN_IN, -0.8F, 0.8F);
    observation = sample(4U, 32U, -35.0F);
    observation.bearing_valid = true;
    observation.bearing_deg = 180.0F;
    checkMoving(wait.step(observation), FlankPhase::TURN_IN, -0.25F, 0.25F);
    observation = sample(5U, 32U, -40.0F);
    const auto result = wait.step(observation);
    checkTerminal(result, Exit::SIDE_OR_REAR_TARGET);
    CHECK(result.phase_changed);
}

TEST_CASE("B12 O4 delegated pivot and turn timeout pulses occur once without restarting") {
    openers::Wait wait;
    beginFlank(wait);
    checkMoving(wait.step(sample(700000U)), FlankPhase::PIVOT, 0.8F, -0.8F);
    auto result = wait.step(sample(700001U));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    CHECK(result.flank.motion_timed_out);
    CHECK(result.flank.phase_changed);
    CHECK_FALSE(result.phase_changed);
    result = wait.step(sample(700002U));
    checkNoPulses(result);
    result = wait.step(sample(950001U));
    checkMoving(result, FlankPhase::TURN_IN, -0.8F, 0.8F);
    CHECK_FALSE(result.flank.motion_timed_out);
    result = wait.step(sample(1650000U));
    checkMoving(result, FlankPhase::TURN_IN, -0.8F, 0.8F);
    result = wait.step(sample(1650001U));
    checkTerminal(result, Exit::SEARCH);
    CHECK(result.flank.motion_timed_out);
    CHECK(result.phase_changed);
    result = wait.step(sample(1650002U));
    checkTerminal(result, Exit::SEARCH);
    checkNoPulses(result);
}

TEST_CASE("B12 O4 delegation stops WAIT deadline processing and starts segments on observation") {
    openers::Wait wait;
    CHECK(wait.start(0U, 0.0F));
    checkHold(wait.step(sample(1900000U, 2U)));
    checkCue(wait.step(sample(1900001U, 3U)));
    checkMoving(wait.step(sample(2000001U)), FlankPhase::PIVOT, 0.8F, -0.8F);
    auto result = wait.step(sample(3000000U));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    CHECK(result.flank.motion_timed_out);
    result = wait.step(sample(3249999U));
    checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
    result = wait.step(sample(3250000U));
    checkMoving(result, FlankPhase::TURN_IN, -0.8F, 0.8F);
}

TEST_CASE("B12 O4 healthy invalid yaw during delegated fallback still latches invalid") {
    for (const auto yaw : {NAN_YAW, INF_YAW, -INF_YAW}) {
        openers::Wait wait;
        CHECK(wait.start(0U, 0.0F));
        checkHold(wait.step(sample(0U, 2U, NAN_YAW, false)));
        checkCue(wait.step(sample(1U, 3U, NAN_YAW, false)));
        auto result = wait.step(sample(2U, 0U, yaw));
        checkTerminal(result, Exit::INVALID);
        CHECK(result.phase_changed);
        CHECK_FALSE(result.approach_cue);
        result = wait.step(sample(100001U, 0U, 50.0F));
        checkTerminal(result, Exit::INVALID);
        checkNoPulses(result);
    }
}

TEST_CASE("B12 O4 start and reset discard terminal cue timer and delegated motion histories") {
    openers::Wait wait;
    beginFlank(wait);
    CHECK(wait.start(100U, 0.0F));
    checkHold(wait.step(sample(100U, 3U)));
    checkHold(wait.step(sample(101U, 3U)));
    checkTerminal(wait.step(sample(2000100U, 3U)), Exit::SEARCH);
    CHECK(wait.start(2000101U, 0.0F));
    checkHold(wait.step(sample(2000101U, 2U)));
    checkCue(wait.step(sample(2000102U, 3U)));
    wait.reset();
    auto result = wait.step(sample(2000103U, 7U));
    CHECK(result.phase == Phase::IDLE);
    checkZero(result);
    checkNoPulses(result);
    CHECK(wait.start(2000104U, 0.0F));
    checkHold(wait.step(sample(2000104U, 7U)));
}

TEST_CASE("B12 O4 WAIT cue and complete sidestep cross uint32 micros wrap repeatedly") {
    const std::uint32_t base = std::numeric_limits<std::uint32_t>::max() - 200000U;
    openers::Wait wait;
    for (unsigned episode = 0U; episode < 4U; ++episode) {
        const auto start = static_cast<std::uint32_t>(base + episode * 100U);
        CHECK(wait.start(start, 0.0F));
        checkHold(wait.step(sample(start + 1U, 2U)));
        checkCue(wait.step(sample(start + 300001U, 3U)));
        checkMoving(wait.step(sample(start + 300002U, 0U, 50.0F)),
                    FlankPhase::TRAVERSE, 0.85F, 0.85F);
        checkMoving(wait.step(sample(start + 550002U, 0U, 50.0F)),
                    FlankPhase::TURN_IN, -0.8F, 0.8F);
        const auto result = wait.step(sample(start + 550003U, 0U, -60.0F));
        checkTerminal(result, Exit::SEARCH);
        CHECK(result.flank.scan_hint_valid);
    }
}

TEST_CASE("B12 O4 long legal delayed observation cannot revive expired wait or cue") {
    for (const auto gap : {2000000U, 2000001U, 0xffffffffU}) {
        openers::Wait wait;
        CHECK(wait.start(0xfffffff0U, 0.0F));
        checkHold(wait.step(sample(0xfffffff0U, 2U)));
        const auto result = wait.step(sample(static_cast<std::uint32_t>(0xfffffff0U + gap), 3U));
        checkTerminal(result, Exit::SEARCH);
        CHECK_FALSE(result.approach_cue);
    }
}

TEST_CASE("B12 O4 finite extreme heading preserves bounded right pivot and timed completion") {
    for (const auto yaw : {std::numeric_limits<float>::max(),
                           -std::numeric_limits<float>::max(), 1.0e20F, -1.0e20F}) {
        openers::Wait wait;
        CHECK(wait.start(0U, yaw));
        checkHold(wait.step(sample(0U, 2U, yaw)));
        checkCue(wait.step(sample(1U, 3U, yaw)));
        const auto result = wait.step(sample(700001U, 0U, yaw));
        checkMoving(result, FlankPhase::TRAVERSE, 0.85F, 0.85F);
        CHECK(result.flank.motion_timed_out);
    }
}

TEST_CASE("B7 B12 Flank relative pivot preserves strict five degree raw-coordinate boundary") {
    for (const auto sign : {-1.0F, 1.0F}) {
        openers::Flank flank;
        const auto mode = sign > 0.0F ? core::Mode::SIDESTEP_R : core::Mode::SIDESTEP_L;
        CHECK(flank.start(0U, -sign * 1.0e-6F, true, mode));
        auto result = flank.step(sample(1U, 0U, sign * 45.0F));
        CHECK(result.phase == FlankPhase::TRAVERSE);
        CHECK(result.phase_changed);
        CHECK(result.motion.status == motion::Status::ACTIVE);
        CHECK(flank.start(2U, 0.0F, true, mode));
        result = flank.step(sample(3U, 0U, sign * 45.0F));
        CHECK(result.phase == FlankPhase::PIVOT);
        CHECK_FALSE(result.phase_changed);
        CHECK(result.motion.duty_l == doctest::Approx(sign * 0.25F));
        CHECK(flank.start(4U, sign * 1.0e-6F, true, mode));
        result = flank.step(sample(5U, 0U, sign * 45.0F));
        CHECK(result.phase == FlankPhase::PIVOT);
    }
}

TEST_CASE("B12 O4 B6 HOLD brake immediately cancels a prior fully authorized ATTACK duty") {
    governor::Governor governor;
    governor::Request attack;
    attack.duty_l = 1.0F;
    attack.duty_r = 1.0F;
    attack.vbat_v = 9.0F;
    attack.profile = governor::Profile::ATTACK;
    attack.centered = true;
    attack.contact = true;
    attack.inhibited = false;
    governor.step(0U, attack);
    const auto full = governor.step(50000U, attack);
    CHECK(full.duty_l == 1.0F);
    CHECK(full.duty_r == 1.0F);
    openers::Wait wait;
    CHECK(wait.start(51000U, 0.0F));
    const auto hold = wait.step(sample(51000U, 2U));
    checkHold(hold);
    checkDutyZero(governor.step(51000U, governed(hold)));
}

TEST_CASE("B12 O4 B6 low voltage caps delegated phases and caller permission remains authoritative") {
    openers::Wait wait;
    governor::Governor governor;
    CHECK(wait.start(0U, 0.0F));
    auto result = wait.step(sample(0U, 2U));
    checkDutyZero(governor.step(0U, governed(result)));
    result = wait.step(sample(100000U, 3U));
    auto duty = governor.step(100000U, governed(result));
    CHECK(duty.duty_l == doctest::Approx(0.8F));
    CHECK(duty.duty_r == doctest::Approx(-0.8F));
    result = wait.step(sample(101000U, 0U));
    checkDutyZero(governor.step(101000U, governed(result, false)));
    result = wait.step(sample(200000U, 0U, 50.0F));
    duty = governor.step(200000U, governed(result));
    CHECK(duty.duty_l == doctest::Approx(0.85F));
    CHECK(duty.duty_r == doctest::Approx(0.85F));
    result = wait.step(sample(450000U, 0U, 50.0F));
    CHECK(result.flank.phase == FlankPhase::TURN_IN);
    duty = governor.step(450000U, governed(result));
    CHECK(std::fabs(duty.duty_l) <= 0.8F);
    CHECK(std::fabs(duty.duty_r) <= 0.8F);
    result = wait.step(sample(500000U, 0U, 50.0F));
    duty = governor.step(500000U, governed(result));
    CHECK(duty.duty_l == doctest::Approx(-0.8F));
    CHECK(duty.duty_r == doctest::Approx(0.8F));
    result = wait.step(sample(501000U, 2U, 50.0F));
    checkTerminal(result, Exit::FRONT_TARGET);
    checkDutyZero(governor.step(501000U, governed(result)));
}

TEST_CASE("B12 O4 D034 exit intent composes with fresh three-observation normal qualification") {
    openers::Wait wait;
    beginFlank(wait);
    const auto exit = wait.step(sample(2U, 7U, 50.0F));
    checkTerminal(exit, Exit::FRONT_TARGET);
    fsm::NormalPerception normal;
    normal.reset();
    for (unsigned observation = 1U; observation <= 3U; ++observation) {
        const auto selected = normal.step(7U);
        CHECK(selected.state == (observation == 3U ? core::State::ATTACK : core::State::TRACK));
        CHECK(selected.centered);
        CHECK_FALSE(selected.brake);
        const auto front = fsm::frontDemand(selected.state, 7U, false);
        CHECK(front.valid);
        CHECK(front.duty_l == doctest::Approx(observation == 3U ? 0.6F : 0.45F));
        CHECK(front.duty_r == doctest::Approx(observation == 3U ? 0.6F : 0.45F));
    }
}
