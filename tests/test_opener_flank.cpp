// Checks B12 O1/O3 mirrored flank openers under D-033/D-034 and B7.
// Keeps phase requests and exit intents separate from the FSM and MotorGate.
// Spec-only doctest cases cover masks, motion boundaries, faults and symmetry.
#include "doctest.h"
#include "config.h"
#include "core/openers.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr core::Mode MODES[] = {core::Mode::SIDESTEP_R, core::Mode::SIDESTEP_L,
                              core::Mode::ARC_R, core::Mode::ARC_L};
constexpr openers::Phase PHASES[] = {openers::Phase::PIVOT,
                                    openers::Phase::TRAVERSE, openers::Phase::TURN_IN};
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();
constexpr std::uint32_t TURN_US = config::TURN_TIMEOUT_MS * 1000U;
constexpr std::uint32_t DRIVE_US = config::SS_DRIVE_MS * 1000U;
constexpr std::uint32_t ARC_US = config::ARC_MAX_MS * 1000U;

bool isArc(core::Mode mode) {
    return mode == core::Mode::ARC_R || mode == core::Mode::ARC_L;
}

float signOf(core::Mode mode) {
    return mode == core::Mode::SIDESTEP_L || mode == core::Mode::ARC_L ? -1.0F : 1.0F;
}

float pivotOf(core::Mode mode) {
    return signOf(mode) * (isArc(mode) ? 80.0F : 50.0F);
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    return static_cast<std::uint8_t>((mask & 0x82U) |
        ((mask & 0x01U) << 2U) | ((mask & 0x04U) >> 2U) |
        ((mask & 0x08U) << 1U) | ((mask & 0x10U) >> 1U) |
        ((mask & 0x20U) << 1U) | ((mask & 0x40U) >> 1U));
}

std::uint8_t orient(std::uint8_t right_mask, core::Mode mode) {
    return signOf(mode) > 0.0F ? right_mask : mirrorMask(right_mask);
}

openers::Sample sample(std::uint32_t time, float heading, std::uint8_t mask = 0U,
                       float bearing = 0.0F, bool valid = false, bool healthy = true) {
    openers::Sample result;
    result.t_us = time;
    result.heading_deg = heading;
    result.imu_ok = healthy;
    result.confirmed_mask = mask;
    result.bearing_deg = bearing;
    result.bearing_valid = valid;
    return result;
}

void checkZero(const openers::FlankResult& result, openers::Exit exit) {
    CHECK(result.exit == exit);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
}

void checkActive(const openers::FlankResult& result, openers::Phase phase,
                  float left, float right) {
    CHECK(result.exit == openers::Exit::NONE);
    CHECK(result.phase == phase);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(right));
}

void checkBounded(const openers::FlankResult& result) {
    CHECK(std::isfinite(result.motion.duty_l));
    CHECK(std::isfinite(result.motion.duty_r));
    CHECK(std::fabs(result.motion.duty_l) <= 1.0F);
    CHECK(std::fabs(result.motion.duty_r) <= 1.0F);
    if (result.exit != openers::Exit::NONE) checkZero(result, result.exit);
}

void checkMirror(const openers::FlankResult& right, const openers::FlankResult& left) {
    CHECK(right.exit == left.exit);
    CHECK(right.phase == left.phase);
    CHECK(right.profile == left.profile);
    CHECK(right.phase_changed == left.phase_changed);
    CHECK(right.motion_timed_out == left.motion_timed_out);
    CHECK(right.motion.status == left.motion.status);
    CHECK(right.motion.imu_fallback == left.motion.imu_fallback);
    CHECK(right.motion.duty_l == doctest::Approx(left.motion.duty_r));
    CHECK(right.motion.duty_r == doctest::Approx(left.motion.duty_l));
    CHECK(right.scan_hint_valid == left.scan_hint_valid);
    if (right.scan_hint_valid) CHECK(right.scan_direction != left.scan_direction);
    checkBounded(right);
    checkBounded(left);
}

void prepare(openers::Flank& flank, core::Mode mode, openers::Phase phase,
             float base = 0.0F, std::uint32_t time = 0U) {
    CHECK(flank.start(time, base, true, mode));
    if (phase == openers::Phase::PIVOT) return;
    const auto traverse = flank.step(sample(time + 1000U, base + pivotOf(mode)));
    CHECK(traverse.phase == openers::Phase::TRAVERSE);
    CHECK(traverse.exit == openers::Exit::NONE);
    if (phase == openers::Phase::TRAVERSE) return;
    const auto turn = flank.step(sample(time + 2000U, base + pivotOf(mode),
                                        orient(0x08U, mode), -signOf(mode) * 90.0F, true));
    CHECK(turn.phase == openers::Phase::TURN_IN);
    CHECK(turn.exit == openers::Exit::NONE);
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed ^= seed << 13U;
    seed ^= seed >> 17U;
    seed ^= seed << 5U;
    return seed;
}

governor::Request governed(const openers::FlankResult& result, float voltage) {
    governor::Request request;
    request.duty_l = result.motion.duty_l;
    request.duty_r = result.motion.duty_r;
    request.profile = result.profile;
    request.vbat_v = voltage;
    request.inhibited = false;
    request.centered = true;
    request.contact = true;
    return request;
}
} // namespace

TEST_CASE("B12 O1 O3 Flank defaults and reset are inert without permission") {
    const openers::FlankResult result;
    checkZero(result, openers::Exit::NONE);
    CHECK(result.phase == openers::Phase::IDLE);
    CHECK_FALSE(result.scan_hint_valid);
    openers::Flank flank;
    const auto idle = flank.step(sample(0U, NAN_VALUE, 0x7FU));
    checkZero(idle, openers::Exit::NONE);
    CHECK(idle.phase == openers::Phase::IDLE);
    CHECK(flank.start(0U, 0.0F, true, core::Mode::ARC_R));
    flank.reset();
    checkZero(flank.step(sample(1000U, NAN_VALUE, 0x7FU)), openers::Exit::NONE);
}

TEST_CASE("B12 O1 O3 Flank accepts exactly four modes and rejects every other byte") {
    for (unsigned value = 0U; value < 256U; ++value) {
        const auto mode = static_cast<core::Mode>(value);
        const bool accepted = value == 1U || value == 2U || value == 4U || value == 5U;
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode) == accepted);
        const auto result = flank.step(sample(0U, 0.0F));
        if (accepted) CHECK(result.phase == openers::Phase::PIVOT);
        else checkZero(result, openers::Exit::INVALID);
    }
}

TEST_CASE("B7 B12 O1 O3 nonfinite start headings reject and replace any active command") {
    for (const auto mode : MODES) {
        for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
            openers::Flank flank;
            CHECK(flank.start(0U, 0.0F, true, mode));
            CHECK_FALSE(flank.start(1000U, invalid, false, mode));
            checkZero(flank.step(sample(2000U, 0.0F)), openers::Exit::INVALID);
        }
    }
}

TEST_CASE("B7 B12 O1 O3 pivot angles are relative 50 or 80 with mirrored 0.80 duty") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        CHECK(flank.start(100U, 123.0F, true, mode));
        const float sign = signOf(mode);
        const auto pivot = flank.step(sample(100U, 123.0F));
        checkActive(pivot, openers::Phase::PIVOT, sign * .8F, -sign * .8F);
        CHECK(pivot.profile == governor::Profile::PIVOT);
        const auto traverse = flank.step(sample(1100U, 123.0F + pivotOf(mode)));
        CHECK(traverse.phase == openers::Phase::TRAVERSE);
        CHECK(traverse.profile == governor::Profile::OPENER);
        CHECK(traverse.phase_changed);
        CHECK_FALSE(traverse.motion_timed_out);
    }
}

TEST_CASE("B7 B12 O1 O3 pivot tolerance is strict less than five degrees") {
    for (const auto mode : MODES) {
        for (const float error : {5.001F, 5.0F, 4.999F}) {
            openers::Flank flank;
            CHECK(flank.start(0U, 0.0F, true, mode));
            const auto result = flank.step(sample(1000U, pivotOf(mode) - signOf(mode) * error));
            CHECK(result.phase == (error < 5.0F ? openers::Phase::TRAVERSE : openers::Phase::PIVOT));
            if (error >= 5.0F) {
                CHECK(result.motion.duty_l == doctest::Approx(signOf(mode) * .25F));
                CHECK(result.motion.duty_r == doctest::Approx(-signOf(mode) * .25F));
            }
        }
    }
}

TEST_CASE("B7 B12 O1 O3 pivot timeout exact adjacent and delayed ticks advance once") {
    for (const auto mode : MODES) {
        for (const auto elapsed : {TURN_US - 1U, TURN_US, TURN_US + 1U, 5000000U}) {
            openers::Flank flank;
            CHECK(flank.start(123U, 0.0F, true, mode));
            const auto result = flank.step(sample(123U + elapsed, 0.0F));
            const bool expired = elapsed >= TURN_US;
            CHECK(result.phase == (expired ? openers::Phase::TRAVERSE : openers::Phase::PIVOT));
            CHECK(result.motion_timed_out == expired);
            if (expired) {
                const auto next = flank.step(sample(124U + elapsed, 0.0F));
                CHECK(next.phase == openers::Phase::TRAVERSE);
                CHECK_FALSE(next.motion_timed_out);
                CHECK_FALSE(next.phase_changed);
            }
        }
    }
}

TEST_CASE("B7 B12 O1 O3 pivot timeout wins a simultaneous heading completion") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode));
        const auto result = flank.step(sample(TURN_US, pivotOf(mode)));
        CHECK(result.phase == openers::Phase::TRAVERSE);
        CHECK(result.motion_timed_out);
    }
}

TEST_CASE("B7 B12 O1 O3 missing IMU pivot uses unchanged angle times two ms") {
    for (const auto mode : MODES) {
        const auto duration = static_cast<std::uint32_t>(std::fabs(pivotOf(mode)) * 2000.0F);
        openers::Flank flank;
        CHECK(flank.start(0U, 30.0F, false, mode));
        const auto before = flank.step(sample(duration - 1U, NAN_VALUE, 0U, 0.0F, false, false));
        CHECK(before.phase == openers::Phase::PIVOT);
        CHECK(before.motion.imu_fallback);
        const auto done = flank.step(sample(duration, NAN_VALUE, 0U, 0.0F, false, false));
        CHECK(done.phase == openers::Phase::TRAVERSE);
        CHECK(done.motion.imu_fallback);
        CHECK_FALSE(done.motion_timed_out);
    }
}

TEST_CASE("B7 B12 O1 O3 lost IMU pivot captures remaining angle without extending original timeout") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode));
        const float near = pivotOf(mode) - signOf(mode) * 10.0F;
        flank.step(sample(TURN_US - 3000U, near));
        const auto lost = flank.step(sample(TURN_US - 2000U, NAN_VALUE, 0U, 0.0F, false, false));
        CHECK(lost.phase == openers::Phase::PIVOT);
        CHECK(lost.motion.imu_fallback);
        const auto timed = flank.step(sample(TURN_US, near));
        CHECK(timed.phase == openers::Phase::TRAVERSE);
        CHECK(timed.motion_timed_out);
    }
}

TEST_CASE("B2 B12 D033 all masks have phase-specific SIDESTEP and ARC priority") {
    for (const auto mode : MODES) {
        for (const auto phase : PHASES) {
            for (unsigned raw = 0U; raw < 128U; ++raw) {
                CAPTURE(mode); CAPTURE(phase); CAPTURE(raw);
                openers::Flank flank;
                prepare(flank, mode, phase);
                const auto mask = orient(static_cast<std::uint8_t>(raw), mode);
                const auto result = flank.step(sample(3000U,
                    phase == openers::Phase::PIVOT ? 0.0F : pivotOf(mode),
                    mask, -signOf(mode) * 90.0F, true));
                openers::Exit expected = openers::Exit::NONE;
                if (phase != openers::Phase::PIVOT && (raw & 7U) != 0U)
                    expected = openers::Exit::FRONT_TARGET;
                else if (!isArc(mode) && (raw & 0x50U) != 0U)
                    expected = openers::Exit::SIDE_OR_REAR_TARGET;
                if (expected != openers::Exit::NONE) checkZero(result, expected);
                else {
                    CHECK(result.exit == openers::Exit::NONE);
                    const bool inward = phase == openers::Phase::TRAVERSE && (raw & 0x28U) != 0U;
                    CHECK(result.phase == (inward ? openers::Phase::TURN_IN : phase));
                }
                checkBounded(result);
            }
        }
    }
}

TEST_CASE("B12 O1 O3 unused mask bit never changes phase arbitration") {
    for (const auto mode : MODES) {
        for (const auto phase : PHASES) {
            for (unsigned mask = 0U; mask < 128U; ++mask) {
                openers::Flank low;
                openers::Flank high;
                prepare(low, mode, phase);
                prepare(high, mode, phase);
                const float heading = phase == openers::Phase::PIVOT ? 0.0F : pivotOf(mode);
                const auto a = low.step(sample(3000U, heading, static_cast<std::uint8_t>(mask), -90.0F, true));
                const auto b = high.step(sample(3000U, heading, static_cast<std::uint8_t>(mask | 128U), -90.0F, true));
                CHECK(a.exit == b.exit);
                CHECK(a.phase == b.phase);
                CHECK(a.motion.duty_l == b.motion.duty_l);
                CHECK(a.motion.duty_r == b.motion.duty_r);
            }
        }
    }
}

TEST_CASE("B2 B12 O1 O3 pivot completion rechecks the new phase front abort on the same tick") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode));
        CHECK(flank.step(sample(0U, 0.0F, 0x02U)).phase == openers::Phase::PIVOT);
        checkZero(flank.step(sample(1000U, pivotOf(mode), 0x02U)), openers::Exit::FRONT_TARGET);
    }
}

TEST_CASE("B2 B12 D033 simultaneous front outer at pivot completion retains old phase priority") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode));
        const auto result = flank.step(sample(1000U, pivotOf(mode), orient(0x12U, mode)));
        checkZero(result, isArc(mode) ? openers::Exit::FRONT_TARGET : openers::Exit::SIDE_OR_REAR_TARGET);
    }
}

TEST_CASE("B12 O1 O3 pivot completion can start traverse and inner turn on one tick") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode));
        const auto result = flank.step(sample(1000U, pivotOf(mode), orient(0x08U, mode),
                                              -signOf(mode) * 90.0F, true));
        checkActive(result, openers::Phase::TURN_IN, -signOf(mode) * .8F, signOf(mode) * .8F);
        CHECK(result.phase_changed);
        CHECK(result.profile == governor::Profile::PIVOT);
    }
}

TEST_CASE("B7 B12 O1 DRIVE holds its actual entry heading and uses approved correction") {
    for (const auto mode : {core::Mode::SIDESTEP_R, core::Mode::SIDESTEP_L}) {
        openers::Flank flank;
        CHECK(flank.start(0U, 0.0F, true, mode));
        const float captured = signOf(mode) * 47.0F;
        checkActive(flank.step(sample(1000U, captured)), openers::Phase::TRAVERSE, .85F, .85F);
        const auto result = flank.step(sample(2000U, captured - signOf(mode) * 2.0F));
        checkActive(result, openers::Phase::TRAVERSE, .85F + signOf(mode) * .04F,
                    .85F - signOf(mode) * .04F);
    }
}

TEST_CASE("B12 O1 DRIVE completes at 250 ms into a fixed 110 degree turn without a target") {
    for (const auto mode : {core::Mode::SIDESTEP_R, core::Mode::SIDESTEP_L}) {
        for (const auto elapsed : {DRIVE_US - 1U, DRIVE_US, DRIVE_US + 1U, DRIVE_US + 1000000U}) {
            openers::Flank flank;
            prepare(flank, mode, openers::Phase::TRAVERSE);
            const auto result = flank.step(sample(1000U + elapsed, pivotOf(mode)));
            if (elapsed < DRIVE_US) checkActive(result, openers::Phase::TRAVERSE, .85F, .85F);
            else {
                checkActive(result, openers::Phase::TURN_IN, -signOf(mode) * .8F, signOf(mode) * .8F);
                const float target = pivotOf(mode) - signOf(mode) * 110.0F;
                checkZero(flank.step(sample(1001U + elapsed, target)), openers::Exit::SEARCH);
            }
        }
    }
}

TEST_CASE("B12 O1 fixed turn captures heading at DRIVE exit rather than at original GO") {
    for (const auto mode : {core::Mode::SIDESTEP_R, core::Mode::SIDESTEP_L}) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TRAVERSE);
        const float current = signOf(mode) * 60.0F;
        const auto turn = flank.step(sample(1000U + DRIVE_US, current));
        CHECK(turn.phase == openers::Phase::TURN_IN);
        checkZero(flank.step(sample(2000U + DRIVE_US, current - signOf(mode) * 110.0F)),
                  openers::Exit::SEARCH);
    }
}

TEST_CASE("B2 B12 O1 current front and outer abort precede the exact DRIVE deadline") {
    for (const auto mode : {core::Mode::SIDESTEP_R, core::Mode::SIDESTEP_L}) {
        for (const auto mask : {0x02U, 0x10U, 0x12U, 0x7FU}) {
            openers::Flank flank;
            prepare(flank, mode, openers::Phase::TRAVERSE);
            const auto result = flank.step(sample(1000U + DRIVE_US, pivotOf(mode),
                                                  orient(static_cast<std::uint8_t>(mask), mode)));
            checkZero(result, (mask & 7U) != 0U ? openers::Exit::FRONT_TARGET : openers::Exit::SIDE_OR_REAR_TARGET);
        }
    }
}

TEST_CASE("B12 O3 ARC requests 0.70 outer and 0.45 ratio inner in both directions") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TRAVERSE);
        const auto result = flank.step(sample(2000U, pivotOf(mode)));
        checkActive(result, openers::Phase::TRAVERSE,
                    signOf(mode) > 0.0F ? .315F : .7F, signOf(mode) > 0.0F ? .7F : .315F);
        CHECK(result.profile == governor::Profile::OPENER);
    }
}

TEST_CASE("B7 B12 O3 ARC requires 200 signed continuous degrees and ignores opposite sweep") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        for (const float sweep : {-200.0F, 199.999F, 200.0F, 200.001F}) {
            openers::Flank flank;
            prepare(flank, mode, openers::Phase::TRAVERSE, 720.0F);
            const auto result = flank.step(sample(2000U, 720.0F + pivotOf(mode) - signOf(mode) * sweep));
            if (sweep < 200.0F) CHECK(result.phase == openers::Phase::TRAVERSE);
            else checkZero(result, openers::Exit::SEARCH);
            CHECK_FALSE(result.motion_timed_out);
        }
    }
}

TEST_CASE("B7 B12 O3 ARC time limit is 1500 ms with exact adjacent delayed and tie cases") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        for (const auto elapsed : {ARC_US - 1U, ARC_US, ARC_US + 1U, ARC_US + 1000000U}) {
            openers::Flank flank;
            prepare(flank, mode, openers::Phase::TRAVERSE);
            const auto result = flank.step(sample(1000U + elapsed, pivotOf(mode)));
            if (elapsed < ARC_US) CHECK(result.phase == openers::Phase::TRAVERSE);
            else checkZero(result, openers::Exit::SEARCH);
            CHECK(result.motion_timed_out == (elapsed >= ARC_US));
        }
        openers::Flank tie;
        prepare(tie, mode, openers::Phase::TRAVERSE);
        const auto result = tie.step(sample(1000U + ARC_US, pivotOf(mode) - signOf(mode) * 200.0F));
        checkZero(result, openers::Exit::SEARCH);
        CHECK(result.motion_timed_out);
    }
}

TEST_CASE("B12 O3 ARC completion turns toward a current outer target without inventing one") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TRAVERSE);
        const auto current = sample(1000U + ARC_US, pivotOf(mode), orient(0x10U, mode),
                                     signOf(mode) * 90.0F, true);
        const auto result = flank.step(current);
        checkActive(result, openers::Phase::TURN_IN, signOf(mode) * .8F, -signOf(mode) * .8F);
        CHECK(result.motion_timed_out);
        openers::Flank no_target;
        prepare(no_target, mode, openers::Phase::TRAVERSE);
        checkZero(no_target.step(sample(1000U + ARC_US, pivotOf(mode), 0U, 90.0F, true)), openers::Exit::SEARCH);
    }
}

TEST_CASE("B12 O3 ARC inner triggers capture current selected bearing once") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        for (const auto inner : {0x08U, 0x20U}) {
            openers::Flank flank;
            prepare(flank, mode, openers::Phase::TRAVERSE);
            const float target = pivotOf(mode) - signOf(mode) * 135.0F;
            const auto trigger = flank.step(sample(2000U, pivotOf(mode), orient(static_cast<std::uint8_t>(inner), mode),
                                                    -signOf(mode) * 135.0F, true));
            CHECK(trigger.phase == openers::Phase::TURN_IN);
            const auto held = flank.step(sample(3000U, pivotOf(mode), orient(0x08U, mode), signOf(mode) * 90.0F, true));
            checkActive(held, openers::Phase::TURN_IN, -signOf(mode) * .8F, signOf(mode) * .8F);
            checkZero(flank.step(sample(4000U, target)), openers::Exit::SEARCH);
        }
    }
}

TEST_CASE("B12 O3 ARC rejects missing nonfinite and out-of-range required bearings") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE, -180.0F, -181.0F, 180.001F}) {
            for (const bool early_inner : {false, true}) {
                openers::Flank flank;
                prepare(flank, mode, openers::Phase::TRAVERSE);
                checkZero(flank.step(sample(early_inner ? 2000U : 1000U + ARC_US, pivotOf(mode),
                    orient(early_inner ? 0x08U : 0x10U, mode), invalid, true)), openers::Exit::INVALID);
            }
        }
        openers::Flank missing;
        prepare(missing, mode, openers::Phase::TRAVERSE);
        checkZero(missing.step(sample(2000U, pivotOf(mode), orient(0x08U, mode), -90.0F, false)), openers::Exit::INVALID);
    }
}

TEST_CASE("B12 O3 ARC accepts canonical 180 bearing and front abort ignores unusable bearing") {
    openers::Flank flank;
    prepare(flank, core::Mode::ARC_R, openers::Phase::TRAVERSE);
    CHECK(flank.step(sample(2000U, 80.0F, 0x08U, 180.0F, true)).phase == openers::Phase::TURN_IN);
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        openers::Flank front;
        prepare(front, mode, openers::Phase::TRAVERSE);
        checkZero(front.step(sample(1000U + ARC_US, pivotOf(mode), 0x7FU, NAN_VALUE, false)), openers::Exit::FRONT_TARGET);
    }
}

TEST_CASE("B12 D034 TURN_IN completion uses current target after loss or reacquisition") {
    for (const auto mode : MODES) {
        for (const auto raw : {0U, 0x02U, 0x08U, 0x10U, 0x20U, 0x40U, 0x7FU}) {
            openers::Flank flank;
            prepare(flank, mode, openers::Phase::TURN_IN);
            CHECK(flank.step(sample(3000U, pivotOf(mode))).phase == openers::Phase::TURN_IN);
            const float target = pivotOf(mode) - signOf(mode) * (isArc(mode) ? 90.0F : 110.0F);
            const auto result = flank.step(sample(4000U, target, orient(static_cast<std::uint8_t>(raw), mode)));
            const auto expected = (raw & 7U) != 0U ? openers::Exit::FRONT_TARGET :
                raw != 0U ? openers::Exit::SIDE_OR_REAR_TARGET : openers::Exit::SEARCH;
            checkZero(result, expected);
            CHECK(result.scan_hint_valid == (!isArc(mode) && raw == 0U));
            if (result.scan_hint_valid) CHECK(result.scan_direction ==
                (signOf(mode) > 0.0F ? motion::Direction::LEFT : motion::Direction::RIGHT));
        }
    }
}

TEST_CASE("B7 B12 O1 O3 TURN_IN timeout has exact deadline and one-call pulse") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TURN_IN);
        const auto before = flank.step(sample(2000U + TURN_US - 1U, pivotOf(mode)));
        CHECK(before.phase == openers::Phase::TURN_IN);
        CHECK_FALSE(before.motion_timed_out);
        const auto done = flank.step(sample(2000U + TURN_US, pivotOf(mode)));
        checkZero(done, openers::Exit::SEARCH);
        CHECK(done.motion_timed_out);
        const auto later = flank.step(sample(2001U + TURN_US, NAN_VALUE, 0x7FU));
        checkZero(later, openers::Exit::SEARCH);
        CHECK_FALSE(later.motion_timed_out);
    }
}

TEST_CASE("B7 B12 O1 O3 unavailable phase-entry yaw reuses last healthy heading") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TRAVERSE, 30.0F);
        auto trigger = sample(2000U, NAN_VALUE, orient(0x08U, mode), -signOf(mode) * 90.0F, true, false);
        const auto turn = flank.step(trigger);
        CHECK(turn.phase == openers::Phase::TURN_IN);
        CHECK(turn.motion.imu_fallback);
        const auto duration = isArc(mode) ? 180000U : 220000U;
        CHECK(flank.step(sample(2000U + duration - 1U, NAN_VALUE, 0U, 0.0F, false, false)).phase == openers::Phase::TURN_IN);
        checkZero(flank.step(sample(2000U + duration, NAN_VALUE, 0U, 0.0F, false, false)), openers::Exit::SEARCH);
    }
}

TEST_CASE("B7 B12 O3 ARC unavailable IMU uses time limit and recovery preserves sweep anchor") {
    for (const auto mode : {core::Mode::ARC_R, core::Mode::ARC_L}) {
        openers::Flank timed;
        prepare(timed, mode, openers::Phase::TRAVERSE);
        CHECK(timed.step(sample(1000U + ARC_US - 1U, NAN_VALUE, 0U, 0.0F, false, false)).phase == openers::Phase::TRAVERSE);
        checkZero(timed.step(sample(1000U + ARC_US, NAN_VALUE, 0U, 0.0F, false, false)), openers::Exit::SEARCH);
        openers::Flank restored;
        prepare(restored, mode, openers::Phase::TRAVERSE);
        restored.step(sample(2000U, NAN_VALUE, 0U, 0.0F, false, false));
        checkZero(restored.step(sample(3000U, pivotOf(mode) - signOf(mode) * 200.0F)), openers::Exit::SEARCH);
    }
}

TEST_CASE("B7 B12 O1 O3 healthy nonfinite yaw terminates every active phase") {
    for (const auto mode : MODES) {
        for (const auto phase : PHASES) {
            for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
                openers::Flank flank;
                prepare(flank, mode, phase);
                checkZero(flank.step(sample(3000U, invalid)), openers::Exit::INVALID);
                checkZero(flank.step(sample(4000U, 0.0F, 0x7FU)), openers::Exit::INVALID);
            }
        }
    }
}

TEST_CASE("B0 B12 O1 O3 finite extreme headings keep every request finite and bounded") {
    const float maximum = std::numeric_limits<float>::max();
    for (const auto mode : MODES) {
        for (const float start : {-maximum, maximum}) {
            openers::Flank flank;
            CHECK(flank.start(0U, start, true, mode));
            checkBounded(flank.step(sample(1000U, start)));
            checkBounded(flank.step(sample(2000U, -start)));
            checkBounded(flank.step(sample(5000000U, -start)));
        }
    }
}

TEST_CASE("B0 B12 O1 O3 micros wrap preserves each newly entered phase deadline") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 500U;
    for (const auto mode : MODES) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TRAVERSE, 0.0F, start);
        const auto duration = isArc(mode) ? ARC_US : DRIVE_US;
        CHECK(flank.step(sample(start + 1000U + duration - 1U, pivotOf(mode))).phase == openers::Phase::TRAVERSE);
        const auto result = flank.step(sample(start + 1000U + duration, pivotOf(mode)));
        if (isArc(mode)) checkZero(result, openers::Exit::SEARCH);
        else CHECK(result.phase == openers::Phase::TURN_IN);
    }
}

TEST_CASE("B12 O1 O3 terminal exits latch zero and reset or restart clears old targets") {
    for (const auto mode : MODES) {
        openers::Flank flank;
        prepare(flank, mode, openers::Phase::TRAVERSE);
        checkZero(flank.step(sample(2000U, pivotOf(mode), 0x02U)), openers::Exit::FRONT_TARGET);
        checkZero(flank.step(sample(3000U, NAN_VALUE, 0x78U)), openers::Exit::FRONT_TARGET);
        CHECK(flank.start(4000U, 35.0F, true, mode));
        CHECK(flank.step(sample(4000U, 35.0F)).phase == openers::Phase::PIVOT);
        flank.reset();
        const auto idle = flank.step(sample(5000U, NAN_VALUE, 0x7FU));
        checkZero(idle, openers::Exit::NONE);
        CHECK(idle.phase == openers::Phase::IDLE);
        CHECK_FALSE(idle.scan_hint_valid);
    }
}

TEST_CASE("B6 B12 O1 O3 returned PIVOT versus OPENER profiles preserve low voltage caps") {
    for (const auto mode : MODES) {
        for (const auto phase : PHASES) {
            openers::Flank flank;
            prepare(flank, mode, phase);
            const auto result = flank.step(sample(3000U, phase == openers::Phase::PIVOT ? 0.0F : pivotOf(mode)));
            const float cap = phase == openers::Phase::TRAVERSE ? .85F : .8F;
            CHECK(result.profile == (phase == openers::Phase::TRAVERSE ? governor::Profile::OPENER : governor::Profile::PIVOT));
            for (const float voltage : {9.0F, 11.1F, 12.6F}) {
                governor::Governor governor;
                const auto request = governed(result, voltage);
                governor.step(0U, request);
                const auto output = governor.step(100000U, request);
                CHECK(output.valid);
                CHECK(std::fabs(output.duty_l) == doctest::Approx(std::min(cap, std::fabs(result.motion.duty_l) * 11.1F / voltage)));
                CHECK(std::fabs(output.duty_r) == doctest::Approx(std::min(cap, std::fabs(result.motion.duty_r) * 11.1F / voltage)));
                CHECK(std::fabs(output.duty_l) <= cap);
                CHECK(std::fabs(output.duty_r) <= cap);
            }
        }
    }
}

TEST_CASE("B0 B12 O1 O3 10000 seeded sequences mirror both families phases and faults") {
    std::uint32_t seed = 0xF1A02633U;
    std::uint32_t mask_counts[128] = {};
    std::uint32_t phase_counts[2][3] = {};
    std::uint32_t validity_counts[3] = {};
    for (unsigned episode = 0U; episode < 10000U; ++episode) {
        const unsigned family = (nextRandom(seed) >> 16U) % 2U;
        const unsigned phase = (nextRandom(seed) >> 16U) % 3U;
        const unsigned validity = (nextRandom(seed) >> 16U) % 3U;
        const auto mask = static_cast<std::uint8_t>((nextRandom(seed) >> 16U) & 127U);
        const auto time = nextRandom(seed);
        const float base = static_cast<float>(static_cast<int>(nextRandom(seed) % 301U) - 150);
        ++mask_counts[mask]; ++phase_counts[family][phase]; ++validity_counts[validity];
        const auto right_mode = family == 0U ? core::Mode::SIDESTEP_R : core::Mode::ARC_R;
        const auto left_mode = family == 0U ? core::Mode::SIDESTEP_L : core::Mode::ARC_L;
        openers::Flank right;
        openers::Flank left;
        prepare(right, right_mode, PHASES[phase], base, time);
        prepare(left, left_mode, PHASES[phase], -base, time);
        const float yaw = base + (phase == 0U ? 0.0F : pivotOf(right_mode));
        const auto a = right.step(sample(time + 3000U, validity == 0U ? yaw : NAN_VALUE,
                                         mask, -90.0F, true, validity != 1U));
        const auto b = left.step(sample(time + 3000U, validity == 0U ? -yaw : NAN_VALUE,
                                        mirrorMask(mask), 90.0F, true, validity != 1U));
        checkMirror(a, b);
        checkMirror(right.step(sample(time + 2000000U, yaw)), left.step(sample(time + 2000000U, -yaw)));
    }
    for (unsigned mask = 0U; mask < 128U; ++mask) CHECK(mask_counts[mask] > 0U);
    for (unsigned family = 0U; family < 2U; ++family)
        for (unsigned phase = 0U; phase < 3U; ++phase) CHECK(phase_counts[family][phase] > 0U);
    for (unsigned validity = 0U; validity < 3U; ++validity) CHECK(validity_counts[validity] > 0U);
}
