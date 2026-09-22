// Checks the approved B4 full Escape selection, replanning and inhibited recovery contract.
// Protects observation ordering and evidence validity independently of implementation.
// New locked host cases cover every mask, boundary, mirror and governed fault response.
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
using Direction = motion::Direction;
using Fault = edge::EscapeFault;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();
constexpr std::uint32_t MAX_TIME = std::numeric_limits<std::uint32_t>::max();
constexpr std::array<Phase, 16> ORDINARY{{
    Phase::IDLE, Phase::BRAKE, Phase::BRAKE, Phase::BRAKE,
    Phase::FORWARD, Phase::PIVOT, Phase::BRAKE, Phase::INVALID,
    Phase::FORWARD, Phase::BRAKE, Phase::PIVOT, Phase::INVALID,
    Phase::FORWARD, Phase::INVALID, Phase::INVALID, Phase::INVALID}};

edge::EscapeSample sample(std::uint32_t time, std::uint8_t mask, float yaw = 0.0F) {
    edge::EscapeSample value;
    value.t_us = time;
    value.line_mask = mask;
    value.heading_deg = yaw;
    value.imu_ok = true;
    value.motion_permitted = true;
    return value;
}

edge::EscapeSample pushing(std::uint32_t time, std::uint8_t mask, float yaw = 0.0F) {
    auto value = sample(time, mask, yaw);
    value.centered_front = true;
    value.applied_duty_l = 0.4F;
    value.applied_duty_r = 0.5F;
    return value;
}

void checkZero(const edge::RowResult& row) {
    CHECK(row.brake);
    CHECK(row.motion.duty_l == 0.0F);
    CHECK(row.motion.duty_r == 0.0F);
    CHECK_FALSE(row.motion.imu_fallback);
}

void checkBounded(const edge::EscapeResult& result) {
    CHECK(std::isfinite(result.row.motion.duty_l));
    CHECK(std::isfinite(result.row.motion.duty_r));
    CHECK(std::fabs(result.row.motion.duty_l) <= 1.0F);
    CHECK(std::fabs(result.row.motion.duty_r) <= 1.0F);
    CHECK(result.replans <= 3U);
}

void checkMoving(const edge::RowResult& row, Phase phase, float left, float right) {
    CHECK(row.phase == phase);
    CHECK(row.motion.status == motion::Status::ACTIVE);
    CHECK_FALSE(row.brake);
    CHECK(row.motion.duty_l == doctest::Approx(left));
    CHECK(row.motion.duty_r == doctest::Approx(right));
    const auto profile = phase == Phase::PIVOT ? governor::Profile::PIVOT
        : phase == Phase::BACK ? governor::Profile::EDGE_REVERSE : governor::Profile::EDGE_FORWARD;
    CHECK(row.profile == profile);
}

void checkFault(const edge::EscapeResult& result, Fault fault,
                bool permitted = true, std::uint32_t replacements = 0U) {
    CHECK(result.fault == fault);
    CHECK(result.escape_required == permitted);
    CHECK(result.inhibit_motion);
    CHECK(result.replans == replacements);
    CHECK_FALSE(result.replanned);
    CHECK_FALSE(result.exited);
    CHECK_FALSE(result.inward_valid);
    CHECK(result.inward_heading_deg == 0.0F);
    CHECK(result.row.motion.status == motion::Status::INVALID);
    checkZero(result.row);
}

void enterFrontPivot(edge::Escape& escape, std::uint8_t mask = 1U,
                     std::uint32_t start = 0U) {
    CHECK(escape.step(sample(start, mask)).entered);
    checkMoving(escape.step(sample(start + 1000U, mask)).row, Phase::BACK, -0.8F, -0.8F);
    const float sign = mask == 1U ? 1.0F : -1.0F;
    checkMoving(escape.step(sample(start + 121000U, mask)).row,
                Phase::PIVOT, sign * 0.8F, -sign * 0.8F);
}

void consumeThreeReplans(edge::Escape& escape) {
    CHECK(escape.step(sample(0U, 8U)).entered);
    for (std::uint32_t count = 1U; count <= 3U; ++count) {
        const auto result = escape.step(sample(count * 200000U, 8U));
        CHECK(result.replanned);
        CHECK_FALSE(result.entered);
        CHECK(result.replans == count);
        CHECK(result.fault == Fault::NONE);
        checkMoving(result.row, Phase::FORWARD, 0.56F, 0.8F);
    }
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    return static_cast<std::uint8_t>(((mask & 1U) << 1U) | ((mask & 2U) >> 1U)
        | ((mask & 4U) << 1U) | ((mask & 8U) >> 1U) | (mask & 0xF0U));
}

Direction opposite(Direction direction) {
    return direction == Direction::RIGHT ? Direction::LEFT : Direction::RIGHT;
}

governor::Result govern(governor::Governor& governor, std::uint32_t time,
                       const edge::EscapeResult& escape, bool permitted = true) {
    governor::Request request;
    request.duty_l = escape.row.motion.duty_l;
    request.duty_r = escape.row.motion.duty_r;
    request.profile = escape.row.profile;
    request.brake = escape.row.brake;
    request.inhibited = escape.inhibit_motion || !permitted;
    request.vbat_v = 9.0F;
    return governor.step(time, request);
}
} // namespace

TEST_CASE("B4.3 pushed-out row has no initial brake and uses mirrored 45 degree then 200 ms motion") {
    CHECK(config::EDGE_SIDE_TURN_DEG == 45U);
    CHECK(config::EDGE_FWD_MS == 200U);
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        const float sign = direction == Direction::RIGHT ? 1.0F : -1.0F;
        edge::RowExecutor row;
        CHECK(row.startPushedOut(17U, 0.0F, true, direction));
        checkMoving(row.step(17U, 0.0F, true), Phase::PIVOT, sign * 0.8F, -sign * 0.8F);
        checkMoving(row.step(18U, sign * 40.0F, true), Phase::PIVOT, sign * 0.25F, -sign * 0.25F);
        const float inside = std::nextafter(sign * 40.0F, sign * 45.0F);
        checkMoving(row.step(19U, inside, true), Phase::FORWARD, 0.8F, 0.8F);
        checkMoving(row.step(200018U, inside, true), Phase::FORWARD, 0.8F, 0.8F);
        const auto done = row.step(200019U, inside, true);
        CHECK(done.phase == Phase::DONE);
        checkZero(done);
        checkZero(row.step(200020U, NAN_VALUE, true));
    }
}

TEST_CASE("B4 B7 relative pivot preserves strict tolerance at tiny raw heading origins") {
    for (const auto direction : {Direction::LEFT, Direction::RIGHT}) {
        const float sign = direction == Direction::RIGHT ? 1.0F : -1.0F;
        edge::RowExecutor row;
        CHECK(row.startPushedOut(0U, -sign * 1.0e-6F, true, direction));
        checkMoving(row.step(1U, sign * 40.0F, true), Phase::FORWARD, 0.8F, 0.8F);
        CHECK(row.startPushedOut(2U, 0.0F, true, direction));
        CHECK(row.step(3U, sign * 40.0F, true).phase == Phase::PIVOT);
        CHECK(row.startPushedOut(4U, sign * 1.0e-6F, true, direction));
        CHECK(row.step(5U, sign * 40.0F, true).phase == Phase::PIVOT);
    }
}

TEST_CASE("B4.3 B7 pushed-out fallback ends at 90 ms and recovery cannot shorten it") {
    edge::RowExecutor row;
    CHECK(row.startPushedOut(0U, 0.0F, false, Direction::RIGHT));
    CHECK(row.step(1000U, 45.0F, true).motion.imu_fallback);
    checkMoving(row.step(89999U, NAN_VALUE, false), Phase::PIVOT, 0.8F, -0.8F);
    const auto forward = row.step(90000U, 12.0F, true);
    checkMoving(forward, Phase::FORWARD, 0.8F, 0.8F);
    CHECK_FALSE(forward.turn_timed_out);
    CHECK(row.step(289999U, 12.0F, true).phase == Phase::FORWARD);
    checkZero(row.step(290000U, 12.0F, true));
}

TEST_CASE("B4.3 B7 pushed-out timeout pulses once while starting the forward segment") {
    edge::RowExecutor row;
    CHECK(row.startPushedOut(0U, 0.0F, true, Direction::LEFT));
    CHECK(row.step(699999U, 0.0F, true).phase == Phase::PIVOT);
    const auto timeout = row.step(700000U, 0.0F, true);
    checkMoving(timeout, Phase::FORWARD, 0.8F, 0.8F);
    CHECK(timeout.turn_timed_out);
    CHECK_FALSE(row.step(700001U, 0.0F, true).turn_timed_out);
    CHECK(row.step(899999U, 0.0F, true).phase == Phase::FORWARD);
    CHECK(row.step(900000U, 0.0F, true).phase == Phase::DONE);
}

TEST_CASE("B4.3 pushed-out invalid capture latches zero and reset restores ordinary rows") {
    edge::RowExecutor row;
    for (const float heading : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        for (const bool imu : {false, true}) {
            CHECK_FALSE(row.startPushedOut(0U, heading, imu, Direction::RIGHT));
            CHECK(row.step(1U, 0.0F, true).motion.status == motion::Status::INVALID);
            checkZero(row.step(2U, 0.0F, true));
        }
    }
    CHECK_FALSE(row.startPushedOut(0U, 0.0F, true, static_cast<Direction>(99U)));
    row.reset();
    CHECK(row.start(0U, 8U, 0.0F, true));
    checkMoving(row.step(0U, 0.0F, true), Phase::FORWARD, 0.56F, 0.8F);
    CHECK_FALSE(row.start(0U, 3U, 0.0F, true));
}

TEST_CASE("B4 D048 Escape ordinary selection covers all 16 masks and every unused high bit") {
    for (unsigned raw = 0U; raw < 256U; ++raw) {
        CAPTURE(raw);
        edge::Escape escape;
        const auto mask = static_cast<std::uint8_t>(raw & 15U);
        const auto result = escape.step(sample(0U, static_cast<std::uint8_t>(raw)));
        CHECK(result.entered == (mask != 0U));
        CHECK_FALSE(result.exited);
        CHECK_FALSE(result.replanned);
        CHECK(result.replans == 0U);
        CHECK_FALSE(result.inward_valid);
        if (ORDINARY[mask] == Phase::INVALID) {
            checkFault(result, Fault::WHITE_PATTERN);
        } else {
            CHECK(result.fault == Fault::NONE);
            CHECK(result.escape_required == (mask != 0U));
            CHECK(result.row.phase == ORDINARY[mask]);
            CHECK_FALSE(result.pushed_out);
            CHECK(result.selected_mask == mask);
            if (mask == 4U) checkMoving(result.row, Phase::FORWARD, 0.8F, 0.56F);
            if (mask == 8U) checkMoving(result.row, Phase::FORWARD, 0.56F, 0.8F);
            if (mask == 12U) checkMoving(result.row, Phase::FORWARD, 0.8F, 0.8F);
            if (mask == 5U) checkMoving(result.row, Phase::PIVOT, 0.8F, -0.8F);
            if (mask == 10U) checkMoving(result.row, Phase::PIVOT, -0.8F, 0.8F);
        }
        checkBounded(result);
    }
}

TEST_CASE("B4 D049 centered forward push precedes every ordinary rear-containing row") {
    for (unsigned raw = 0U; raw < 16U; ++raw) {
        CAPTURE(raw);
        edge::Escape escape;
        const auto mask = static_cast<std::uint8_t>(raw);
        const auto result = escape.step(pushing(0U, mask));
        if (ORDINARY[mask] == Phase::INVALID) {
            checkFault(result, Fault::WHITE_PATTERN);
        } else if ((mask & 12U) != 0U) {
            CHECK(result.pushed_out);
            CHECK(result.selected_mask == mask);
            const bool right = (mask & 12U) == 4U;
            CHECK(result.pivot_direction == (right ? Direction::RIGHT : Direction::LEFT));
            const float sign = right ? 1.0F : -1.0F;
            checkMoving(result.row, Phase::PIVOT, sign * 0.8F, -sign * 0.8F);
        } else {
            CHECK_FALSE(result.pushed_out);
            CHECK(result.row.phase == ORDINARY[mask]);
        }
    }
}

TEST_CASE("B4 D049 pushed-out qualification requires both final duties strictly positive") {
    const float tiny = std::numeric_limits<float>::denorm_min();
    const std::array<float, 6> duties{{-1.0F, -0.0F, 0.0F, tiny, 0.5F, 1.0F}};
    for (const bool centered : {false, true}) {
        for (const float left : duties) {
            for (const float right : duties) {
                edge::Escape escape;
                auto input = sample(0U, 8U);
                input.centered_front = centered;
                input.applied_duty_l = left;
                input.applied_duty_r = right;
                const auto result = escape.step(input);
                const bool expected = centered && left > 0.0F && right > 0.0F;
                CHECK(result.pushed_out == expected);
                CHECK(result.row.phase == (expected ? Phase::PIVOT : Phase::FORWARD));
                CHECK(result.fault == Fault::NONE);
            }
        }
    }
}

TEST_CASE("B4 D047 head-on captures shared side once and uses complete 180 ms reverse") {
    for (const auto side : {Direction::LEFT, Direction::RIGHT}) {
        edge::Escape escape;
        auto input = sample(17U, 3U, 5.0F);
        input.opponent_side = side;
        const auto entered = escape.step(input);
        CHECK(entered.entered);
        CHECK(entered.row.phase == Phase::BRAKE);
        input.opponent_side = opposite(side);
        input.t_us = 1016U;
        CHECK(escape.step(input).row.phase == Phase::BRAKE);
        input.t_us = 1017U;
        input.heading_deg = 20.0F;
        checkMoving(escape.step(input).row, Phase::BACK, -0.8F, -0.8F);
        input.t_us = 181016U;
        CHECK(escape.step(input).row.phase == Phase::BACK);
        input.t_us = 181017U;
        input.heading_deg = 30.0F;
        const auto pivot = escape.step(input);
        CHECK(pivot.pivot_direction == side);
        const float sign = side == Direction::RIGHT ? 1.0F : -1.0F;
        checkMoving(pivot.row, Phase::PIVOT, sign * 0.8F, -sign * 0.8F);
        input.t_us++;
        input.line_mask = 0U;
        input.heading_deg = 30.0F + sign * 160.0F;
        const auto exited = escape.step(input);
        CHECK(exited.exited);
        CHECK(exited.inward_valid);
        CHECK(exited.inward_heading_deg == input.heading_deg);
    }
}

TEST_CASE("B4 D047 D049 default RIGHT makes head-on right and both-rear pushed-out left") {
    edge::Escape head_on;
    head_on.step(sample(0U, 3U));
    head_on.step(sample(1000U, 3U));
    const auto default_pivot = head_on.step(sample(181000U, 3U));
    CHECK(default_pivot.pivot_direction == Direction::RIGHT);
    checkMoving(default_pivot.row, Phase::PIVOT, 0.8F, -0.8F);
    for (const auto side : {Direction::LEFT, Direction::RIGHT}) {
        edge::Escape escape;
        auto input = pushing(0U, 12U);
        input.opponent_side = side;
        const auto result = escape.step(input);
        CHECK(result.pivot_direction == opposite(side));
        CHECK(result.pushed_out);
        input.t_us++;
        input.opponent_side = opposite(side);
        CHECK(escape.step(input).pivot_direction == opposite(side));
    }
}

TEST_CASE("B4 D049 changing opponent context cannot retarget an existing row") {
    edge::Escape escape;
    checkMoving(escape.step(sample(0U, 8U)).row, Phase::FORWARD, 0.56F, 0.8F);
    const auto unchanged = escape.step(pushing(1000U, 8U));
    CHECK_FALSE(unchanged.pushed_out);
    CHECK_FALSE(unchanged.replanned);
    checkMoving(unchanged.row, Phase::FORWARD, 0.56F, 0.8F);
    const auto replacement = escape.step(pushing(200000U, 8U));
    CHECK(replacement.replanned);
    CHECK(replacement.pushed_out);
    CHECK(replacement.replans == 1U);
    checkMoving(replacement.row, Phase::PIVOT, -0.8F, 0.8F);
}

TEST_CASE("B4 D050 persistent white replaces at exact completion and faults on fourth request") {
    edge::Escape escape;
    CHECK(escape.step(sample(0U, 8U)).entered);
    CHECK_FALSE(escape.step(sample(199999U, 8U)).replanned);
    for (std::uint32_t count = 1U; count <= 3U; ++count) {
        const auto result = escape.step(sample(count * 200000U, 8U));
        CHECK(result.replanned);
        CHECK(result.replans == count);
        CHECK_FALSE(result.entered);
        CHECK_FALSE(result.exited);
        CHECK_FALSE(result.inward_valid);
        checkMoving(result.row, Phase::FORWARD, 0.56F, 0.8F);
        CHECK_FALSE(escape.step(sample(count * 200000U + 1U, 8U)).replanned);
    }
    checkFault(escape.step(sample(800000U, 8U)), Fault::REPLAN_LIMIT, true, 3U);
    checkFault(escape.step(sample(900000U, 0U)), Fault::REPLAN_LIMIT, true, 3U);
}

TEST_CASE("B4 D050 clear and reassert observations retain budget and update new-bit baseline") {
    edge::Escape escape;
    CHECK(escape.step(sample(0U, 8U)).entered);
    for (std::uint32_t count = 1U; count <= 3U; ++count) {
        const auto clear = escape.step(sample(count * 2000U - 1000U, 0U));
        CHECK(clear.escape_required);
        CHECK_FALSE(clear.exited);
        CHECK(clear.replans == count - 1U);
        const auto reasserted = escape.step(sample(count * 2000U, 8U));
        CHECK(reasserted.replanned);
        CHECK(reasserted.replans == count);
    }
    escape.step(sample(7000U, 0U));
    checkFault(escape.step(sample(8000U, 8U)), Fault::REPLAN_LIMIT, true, 3U);
}

TEST_CASE("B4 D050 new bits plus old completion permit only one replacement on the observation") {
    edge::Escape escape;
    escape.step(sample(0U, 8U));
    const auto replacement = escape.step(sample(200000U, 12U));
    CHECK(replacement.replanned);
    CHECK(replacement.replans == 1U);
    CHECK(replacement.selected_mask == 12U);
    checkMoving(replacement.row, Phase::FORWARD, 0.8F, 0.8F);
    CHECK_FALSE(escape.step(sample(200001U, 12U)).replanned);
    CHECK_FALSE(escape.step(sample(399999U, 12U)).replanned);
    CHECK(escape.step(sample(400000U, 12U)).replans == 2U);
}

TEST_CASE("B4 D050 any new bit during BRAKE or BACK replaces before advancing the old phase") {
    for (const std::uint32_t time : {999U, 1000U, 120999U, 121000U}) {
        edge::Escape escape;
        escape.step(sample(0U, 1U));
        if (time > 1000U) escape.step(sample(1000U, 1U));
        const auto result = escape.step(sample(time, 5U));
        CHECK(result.replanned);
        CHECK(result.replans == 1U);
        CHECK(result.selected_mask == 5U);
        checkMoving(result.row, Phase::PIVOT, 0.8F, -0.8F);
    }
}

TEST_CASE("B4 D054 captured pivot side controls replanning even after correction reverses") {
    for (const bool mirrored : {false, true}) {
        const std::uint8_t initial = mirrored ? 4U : 8U;
        const std::uint8_t wrong_side = mirrored ? 5U : 10U;
        const std::uint8_t toward_side = mirrored ? 6U : 9U;
        const float yaw = mirrored ? 60.0F : -60.0F;
        edge::Escape escape;
        escape.step(pushing(0U, initial));
        const auto overshot = escape.step(sample(1000U, initial, yaw));
        CHECK(overshot.pivot_direction == (mirrored ? Direction::RIGHT : Direction::LEFT));
        CHECK(overshot.row.motion.duty_l * yaw < 0.0F);
        const auto ignored = escape.step(sample(2000U, wrong_side, yaw));
        CHECK_FALSE(ignored.replanned);
        CHECK(ignored.replans == 0U);
        CHECK(ignored.row.phase == Phase::PIVOT);
        escape.step(sample(3000U, initial, yaw));
        const auto replacement = escape.step(sample(4000U, toward_side, yaw));
        CHECK(replacement.replanned);
        CHECK(replacement.selected_mask == toward_side);
        CHECK(replacement.row.phase == Phase::BRAKE);
        CHECK(replacement.replans == 1U);
    }
}

TEST_CASE("B4 D054 pivot call-entry phase ignores wrong-side addition at forward transition") {
    edge::Escape escape;
    escape.step(pushing(0U, 8U));
    const auto transition = escape.step(sample(1000U, 10U, -45.0F));
    CHECK_FALSE(transition.replanned);
    CHECK(transition.replans == 0U);
    CHECK(transition.selected_mask == 8U);
    CHECK(transition.pushed_out);
    checkMoving(transition.row, Phase::FORWARD, 0.8F, 0.8F);
    CHECK_FALSE(escape.step(sample(1001U, 10U, -45.0F)).replanned);
}

TEST_CASE("B4 D054 pivot toward-side addition wins its exact completion observation") {
    edge::Escape escape;
    escape.step(pushing(0U, 8U));
    const auto replacement = escape.step(sample(1000U, 9U, -45.0F));
    CHECK(replacement.replanned);
    CHECK(replacement.replans == 1U);
    CHECK(replacement.selected_mask == 9U);
    CHECK_FALSE(replacement.pushed_out);
    CHECK(replacement.row.phase == Phase::BRAKE);
    checkZero(replacement.row);
}

TEST_CASE("B4 D054 DONE with white replaces even when the new pivot bit was on the wrong side") {
    edge::Escape escape;
    enterFrontPivot(escape);
    const auto result = escape.step(sample(122000U, 5U, 120.0F));
    CHECK(result.replanned);
    CHECK(result.replans == 1U);
    CHECK(result.selected_mask == 5U);
    checkMoving(result.row, Phase::PIVOT, 0.8F, -0.8F);
    CHECK_FALSE(escape.step(sample(122001U, 5U, 120.0F)).replanned);
}

TEST_CASE("B4 D050 multiple new bits are one replacement and high bits never consume budget") {
    edge::Escape escape;
    escape.step(sample(0U, 8U));
    CHECK_FALSE(escape.step(sample(1U, 0xF8U)).replanned);
    const auto replaced = escape.step(sample(2U, 3U));
    CHECK(replaced.replanned);
    CHECK(replaced.replans == 1U);
    CHECK(replaced.selected_mask == 3U);
    CHECK(replaced.row.phase == Phase::BRAKE);
    CHECK_FALSE(escape.step(sample(3U, 0xF3U)).replanned);
}

TEST_CASE("B4 D048 fault patterns beat context faults row deadlines and exhausted budget") {
    for (const std::uint8_t mask : std::array<std::uint8_t, 5>{{7U, 11U, 13U, 14U, 15U}}) {
        edge::Escape escape;
        consumeThreeReplans(escape);
        auto invalid = pushing(800000U, mask, NAN_VALUE);
        invalid.applied_duty_l = INF_VALUE;
        invalid.opponent_side = static_cast<Direction>(99U);
        const auto fault = escape.step(invalid);
        checkFault(fault, Fault::WHITE_PATTERN, true, 3U);
        CHECK_FALSE(fault.entered);
        checkFault(escape.step(sample(900000U, 0U)), Fault::WHITE_PATTERN, true, 3U);
    }
}

TEST_CASE("B4 D050 exhausted request faults before consuming replacement context") {
    edge::Escape escape;
    consumeThreeReplans(escape);
    auto invalid_predicate = pushing(800000U, 8U);
    invalid_predicate.applied_duty_l = NAN_VALUE;
    checkFault(escape.step(invalid_predicate), Fault::REPLAN_LIMIT, true, 3U);
}

TEST_CASE("B4 D050 all-black completion exits and resets budget after the third replacement") {
    edge::Escape escape;
    consumeThreeReplans(escape);
    const auto exited = escape.step(sample(800000U, 0U, 17.0F));
    CHECK(exited.exited);
    CHECK_FALSE(exited.escape_required);
    CHECK_FALSE(exited.replanned);
    CHECK(exited.replans == 0U);
    CHECK(exited.row.motion.status == motion::Status::DONE);
    checkZero(exited.row);
    const auto next = escape.step(sample(800001U, 8U, 17.0F));
    CHECK(next.entered);
    CHECK_FALSE(next.exited);
    CHECK(next.replans == 0U);
}

TEST_CASE("B4 D054 permission closed while inactive ignores white and all unused invalid context") {
    edge::Escape escape;
    auto closed = pushing(0U, 15U, NAN_VALUE);
    closed.motion_permitted = false;
    closed.applied_duty_l = INF_VALUE;
    closed.opponent_side = static_cast<Direction>(99U);
    const auto ignored = escape.step(closed);
    CHECK(ignored.fault == Fault::NONE);
    CHECK_FALSE(ignored.escape_required);
    CHECK_FALSE(ignored.entered);
    CHECK(ignored.inhibit_motion);
    CHECK(ignored.row.motion.status == motion::Status::IDLE);
    checkZero(ignored.row);
    const auto active = escape.step(sample(1U, 15U));
    CHECK(active.entered);
    checkFault(active, Fault::WHITE_PATTERN);
}

TEST_CASE("B4 D054 permission loss cancels active motion and preserves fault and budget until reset") {
    edge::Escape escape;
    escape.step(sample(0U, 8U));
    escape.step(sample(200000U, 8U));
    auto closed = sample(201000U, 15U, NAN_VALUE);
    closed.motion_permitted = false;
    const auto lost = escape.step(closed);
    CHECK_FALSE(lost.entered);
    checkFault(lost, Fault::PERMISSION_LOST, false, 1U);
    checkFault(escape.step(sample(1000000U, 0U)), Fault::PERMISSION_LOST, true, 1U);
    closed.t_us = 1000001U;
    checkFault(escape.step(closed), Fault::PERMISSION_LOST, false, 1U);
    escape.reset();
    const auto idle = escape.step(sample(1000002U, 0U));
    CHECK(idle.fault == Fault::NONE);
    CHECK(idle.replans == 0U);
    CHECK_FALSE(idle.escape_required);
    CHECK(escape.step(sample(1000003U, 8U)).entered);
}

TEST_CASE("B4 D048 existing line fault survives closed permission and reset clears it") {
    edge::Escape escape;
    const auto first = escape.step(sample(0U, 7U));
    CHECK(first.entered);
    checkFault(first, Fault::WHITE_PATTERN);
    auto closed = sample(1U, 0U);
    closed.motion_permitted = false;
    const auto retained = escape.step(closed);
    CHECK_FALSE(retained.entered);
    checkFault(retained, Fault::WHITE_PATTERN, false);
    escape.reset();
    const auto reset = escape.step(closed);
    CHECK(reset.fault == Fault::NONE);
    CHECK(reset.row.motion.status == motion::Status::IDLE);
}

TEST_CASE("B4 D054 invalid initial heading faults even without IMU but all-black idle ignores it") {
    for (const float yaw : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        for (const bool imu : {false, true}) {
            edge::Escape escape;
            auto input = sample(0U, 0U, yaw);
            input.imu_ok = imu;
            CHECK(escape.step(input).fault == Fault::NONE);
            input.t_us++;
            input.line_mask = 8U;
            const auto invalid = escape.step(input);
            CHECK(invalid.entered);
            checkFault(invalid, Fault::INVALID_CONTEXT);
        }
    }
}

TEST_CASE("B4 D054 both forward-duty fields are validated exactly when rear centering consumes them") {
    for (const float bad : {NAN_VALUE, INF_VALUE, -INF_VALUE, 1.01F, -1.01F}) {
        for (const bool left_bad : {false, true}) {
            edge::Escape escape;
            auto input = pushing(0U, 8U);
            input.applied_duty_l = left_bad ? bad : 0.0F;
            input.applied_duty_r = left_bad ? 0.0F : bad;
            const auto result = escape.step(input);
            CHECK(result.entered);
            checkFault(result, Fault::INVALID_CONTEXT);
        }
    }
}

TEST_CASE("B4 D054 unused duty and opponent-side payloads do not invalidate supported rows") {
    for (const std::uint8_t mask : std::array<std::uint8_t, 5>{{0U, 1U, 4U, 8U, 12U}}) {
        edge::Escape escape;
        auto input = sample(0U, mask);
        input.applied_duty_l = NAN_VALUE;
        input.applied_duty_r = INF_VALUE;
        input.opponent_side = static_cast<Direction>(99U);
        CHECK(escape.step(input).fault == Fault::NONE);
    }
    edge::Escape front;
    auto input = pushing(0U, 1U);
    input.applied_duty_l = NAN_VALUE;
    input.opponent_side = static_cast<Direction>(99U);
    CHECK(front.step(input).fault == Fault::NONE);
    edge::Escape single_rear;
    input = pushing(0U, 8U);
    input.opponent_side = static_cast<Direction>(99U);
    CHECK(single_rear.step(input).pushed_out);
}

TEST_CASE("B4 D054 opponent-side enum is consumed only for head-on or selected both-rear push") {
    for (const bool push : {false, true}) {
        edge::Escape escape;
        auto input = push ? pushing(0U, 12U) : sample(0U, 3U);
        input.opponent_side = static_cast<Direction>(99U);
        checkFault(escape.step(input), Fault::INVALID_CONTEXT);
    }
    edge::Escape not_pushing;
    auto input = pushing(0U, 12U);
    input.applied_duty_l = 0.0F;
    input.opponent_side = static_cast<Direction>(99U);
    const auto normal = not_pushing.step(input);
    CHECK(normal.fault == Fault::NONE);
    CHECK_FALSE(normal.pushed_out);
    checkMoving(normal.row, Phase::FORWARD, 0.8F, 0.8F);
}

TEST_CASE("B4 D054 invalid replacement context does not consume budget and active context is not resampled") {
    edge::Escape escape;
    escape.step(sample(0U, 12U));
    auto input = pushing(1000U, 12U);
    input.applied_duty_r = NAN_VALUE;
    CHECK(escape.step(input).fault == Fault::NONE);
    input.t_us = 200000U;
    const auto failed = escape.step(input);
    checkFault(failed, Fault::INVALID_CONTEXT);
    CHECK_FALSE(failed.entered);
    CHECK_FALSE(failed.replanned);
}

TEST_CASE("B4 B7 D054 healthy invalid yaw faults active rows and missing yaw uses retained coordinates") {
    for (const float bad : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        edge::Escape escape;
        escape.step(sample(0U, 8U, 25.0F));
        checkFault(escape.step(sample(1U, 8U, bad)), Fault::INVALID_CONTEXT);
        checkFault(escape.step(sample(2U, 0U, 25.0F)), Fault::INVALID_CONTEXT);
    }
    edge::Escape unavailable;
    unavailable.step(sample(0U, 8U, 25.0F));
    auto input = sample(1000U, 10U, NAN_VALUE);
    input.imu_ok = false;
    const auto replanned = unavailable.step(input);
    CHECK(replanned.replanned);
    CHECK(replanned.fault == Fault::NONE);
    CHECK(replanned.row.motion.imu_fallback);
    checkMoving(replanned.row, Phase::PIVOT, -0.8F, 0.8F);
    input.t_us = 91000U;
    CHECK(unavailable.step(input).row.phase == Phase::FORWARD);
}

TEST_CASE("B4 B8 D054 inward heading is current raw healthy yaw only on the actual exit pulse") {
    edge::Escape escape;
    escape.step(sample(0U, 12U, 123.0F));
    const auto before = escape.step(sample(199999U, 0U, 124.0F));
    CHECK(before.escape_required);
    CHECK_FALSE(before.exited);
    CHECK_FALSE(before.inward_valid);
    const auto exited = escape.step(sample(200000U, 0U, 725.0F));
    CHECK(exited.exited);
    CHECK(exited.inward_valid);
    CHECK(exited.inward_heading_deg == 725.0F);
    CHECK_FALSE(exited.escape_required);
    CHECK(exited.row.motion.status == motion::Status::DONE);
    checkZero(exited.row);
    const auto later = escape.step(sample(200001U, 0U, 999.0F));
    CHECK_FALSE(later.exited);
    CHECK_FALSE(later.inward_valid);
    CHECK(later.inward_heading_deg == 0.0F);
}

TEST_CASE("B4 B8 D054 unavailable exit yaw never promotes cached motion coordinates to inward evidence") {
    for (const float ignored : {NAN_VALUE, 345.0F}) {
        edge::Escape escape;
        escape.step(sample(0U, 12U, 123.0F));
        auto done = sample(200000U, 0U, ignored);
        done.imu_ok = false;
        const auto exited = escape.step(done);
        CHECK(exited.exited);
        CHECK_FALSE(exited.inward_valid);
        CHECK(exited.inward_heading_deg == 0.0F);
        checkZero(exited.row);
    }
}

TEST_CASE("B4 D050 B7 turn timeout pulse survives replacement or exit exactly once") {
    for (const bool black : {false, true}) {
        edge::Escape escape;
        enterFrontPivot(escape);
        const auto mask = static_cast<std::uint8_t>(black ? 0U : 1U);
        const auto timeout = escape.step(sample(821000U, mask));
        CHECK(timeout.row.turn_timed_out);
        CHECK(timeout.exited == black);
        CHECK(timeout.replanned == !black);
        CHECK(timeout.replans == (black ? 0U : 1U));
        CHECK(timeout.row.phase == (black ? Phase::DONE : Phase::BRAKE));
        checkZero(timeout.row);
        CHECK_FALSE(escape.step(sample(821001U, mask)).row.turn_timed_out);
    }
}

TEST_CASE("B4 D054 delayed observations start new phases at observation time without backdating") {
    edge::Escape escape;
    escape.step(sample(0U, 1U));
    checkMoving(escape.step(sample(100000U, 1U)).row, Phase::BACK, -0.8F, -0.8F);
    CHECK(escape.step(sample(219999U, 1U)).row.phase == Phase::BACK);
    CHECK(escape.step(sample(220000U, 1U)).row.phase == Phase::PIVOT);
    edge::Escape replacement;
    replacement.step(sample(0U, 8U));
    CHECK(replacement.step(sample(50000U, 9U)).row.phase == Phase::BRAKE);
    CHECK(replacement.step(sample(50999U, 9U)).row.phase == Phase::BRAKE);
    CHECK(replacement.step(sample(51000U, 9U)).row.phase == Phase::BACK);
}

TEST_CASE("B4 Escape repeated complete episodes cross uint32 wrap without reviving old budget") {
    edge::Escape escape;
    std::uint32_t start = MAX_TIME - 100000U;
    for (unsigned episode = 0U; episode < 6U; ++episode) {
        const auto first = escape.step(sample(start, 12U));
        CHECK(first.entered);
        CHECK(first.replans == 0U);
        CHECK_FALSE(escape.step(sample(start + 199999U, 0U)).exited);
        const auto done = escape.step(sample(start + 200000U, 0U));
        CHECK(done.exited);
        CHECK(done.inward_valid);
        CHECK(done.replans == 0U);
        start += 3000200000U;
    }
}

TEST_CASE("B4 finite extreme headings retain bounded movement and raw exit evidence") {
    for (const float yaw : {std::numeric_limits<float>::max(), -std::numeric_limits<float>::max()}) {
        edge::Escape pivot;
        const auto first = pivot.step(pushing(0U, 8U, yaw));
        CHECK(first.fault == Fault::NONE);
        checkMoving(first.row, Phase::PIVOT, -0.8F, 0.8F);
        checkBounded(first);
        edge::Escape forward;
        forward.step(sample(0U, 12U, yaw));
        const auto exited = forward.step(sample(200000U, 0U, yaw));
        CHECK(exited.exited);
        CHECK(exited.inward_valid);
        CHECK(exited.inward_heading_deg == yaw);
    }
}

TEST_CASE("B4 all-mask mirrored streams preserve phases replans faults and finite demands across wrap") {
    const std::array<std::uint32_t, 8> offsets{{0U, 1000U, 121000U, 181000U,
                                             200000U, 701000U, 901000U, 1101000U}};
    for (unsigned mask = 0U; mask < 16U; ++mask) {
        for (const bool push : {false, true}) {
            edge::Escape right;
            edge::Escape left;
            for (const auto elapsed : offsets) {
                const auto time = MAX_TIME - 2000U + elapsed;
                auto a = push ? pushing(time, static_cast<std::uint8_t>(mask), 13.0F)
                              : sample(time, static_cast<std::uint8_t>(mask), 13.0F);
                auto b = a;
                b.line_mask = mirrorMask(a.line_mask);
                b.heading_deg = -a.heading_deg;
                b.applied_duty_l = a.applied_duty_r;
                b.applied_duty_r = a.applied_duty_l;
                b.opponent_side = Direction::LEFT;
                const auto ra = right.step(a);
                const auto rb = left.step(b);
                checkBounded(ra);
                checkBounded(rb);
                CHECK(ra.row.phase == rb.row.phase);
                CHECK(ra.fault == rb.fault);
                CHECK(ra.replans == rb.replans);
                CHECK(ra.replanned == rb.replanned);
                CHECK(ra.entered == rb.entered);
                CHECK(ra.exited == rb.exited);
                CHECK(ra.pushed_out == rb.pushed_out);
                CHECK(ra.row.motion.duty_l == doctest::Approx(rb.row.motion.duty_r));
                CHECK(ra.row.motion.duty_r == doctest::Approx(rb.row.motion.duty_l));
                CHECK(ra.row.turn_timed_out == rb.row.turn_timed_out);
                if (ra.row.phase == Phase::PIVOT && ra.fault == Fault::NONE)
                    CHECK(ra.pivot_direction == opposite(rb.pivot_direction));
            }
        }
    }
}

TEST_CASE("B4 B6 low-voltage Escape composition caps requests and immediately inhibits recovery faults") {
    edge::Escape escape;
    governor::Governor governor;
    const auto first = escape.step(sample(0U, 8U));
    const auto initial = govern(governor, 0U, first);
    CHECK(initial.duty_l == 0.0F);
    CHECK(initial.duty_r == 0.0F);
    const auto running = govern(governor, 100000U, escape.step(sample(100000U, 8U)));
    CHECK(running.valid);
    CHECK(running.duty_l > 0.56F);
    CHECK(running.duty_l <= 0.8F);
    CHECK(running.duty_r == 0.8F);
    const auto fault = escape.step(sample(100001U, 7U));
    checkFault(fault, Fault::WHITE_PATTERN);
    const auto stopped = govern(governor, 100001U, fault);
    CHECK(stopped.duty_l == 0.0F);
    CHECK(stopped.duty_r == 0.0F);
    const auto black = govern(governor, 100002U, escape.step(sample(100002U, 0U)));
    CHECK(black.duty_l == 0.0F);
    CHECK(black.duty_r == 0.0F);
}

TEST_CASE("B4 B6 governor receives the escape brake on first front entry from previous full duty") {
    governor::Governor governor;
    governor::Request attack;
    attack.duty_l = 1.0F;
    attack.duty_r = 1.0F;
    attack.profile = governor::Profile::ATTACK;
    attack.centered = true;
    attack.contact = true;
    attack.inhibited = false;
    attack.vbat_v = 9.0F;
    governor.step(0U, attack);
    CHECK(governor.step(100000U, attack).duty_l == 1.0F);
    edge::Escape escape;
    const auto entered = escape.step(sample(100001U, 1U));
    CHECK(entered.entered);
    CHECK(entered.row.phase == Phase::BRAKE);
    const auto stopped = govern(governor, 100001U, entered);
    CHECK(stopped.duty_l == 0.0F);
    CHECK(stopped.duty_r == 0.0F);
}

TEST_CASE("B4 B6 permission loss inhibits existing governed duty and repermission cannot restart it") {
    edge::Escape escape;
    governor::Governor governor;
    govern(governor, 0U, escape.step(sample(0U, 12U)));
    const auto moving = govern(governor, 100000U, escape.step(sample(100000U, 12U)));
    CHECK(moving.duty_l == 0.8F);
    CHECK(moving.duty_r == 0.8F);
    auto closed = sample(100001U, 0U);
    closed.motion_permitted = false;
    const auto cancelled = escape.step(closed);
    checkFault(cancelled, Fault::PERMISSION_LOST, false);
    const auto stopped = govern(governor, 100001U, cancelled, false);
    CHECK(stopped.duty_l == 0.0F);
    CHECK(stopped.duty_r == 0.0F);
    const auto restored = govern(governor, 900000U, escape.step(sample(900000U, 0U)));
    CHECK(restored.duty_l == 0.0F);
    CHECK(restored.duty_r == 0.0F);
}
