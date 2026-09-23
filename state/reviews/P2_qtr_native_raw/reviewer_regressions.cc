// Tests reviewer-discovered D085 retained-entry behavior against real core sources.
// A white frame already admitted before GO must not become newly white afterward.
// This independent regression belongs to review evidence, not production or locked tests.
#include "doctest.h"
#include "core/edge.h"
#include "core/fsm.h"
#include "config.h"
#include <initializer_list>

TEST_CASE("D085 retained white at GO does not invent a later same-white replan") {
    for (const unsigned white : {1U, 2U, 3U, 4U, 8U, 12U}) {
        edge::Escape escape;
        edge::EscapeSample sample;
        sample.t_us = 10000U;
        sample.line_mask = static_cast<std::uint8_t>(white);
        sample.motion_permitted = true;
        sample.line_updated = false;
        sample.opponent_side = motion::Direction::LEFT;
        const auto entered = escape.step(sample);
        REQUIRE(entered.entered);
        REQUIRE(entered.fault == edge::EscapeFault::NONE);
        REQUIRE(entered.replans == 0U);
        sample.t_us += 1000U;
        sample.line_updated = true;
        const auto identical_white = escape.step(sample);
        CHECK_FALSE(identical_white.replanned);
        CHECK(identical_white.replans == 0U);
        CHECK(identical_white.fault == edge::EscapeFault::NONE);
    }
}

TEST_CASE("D085 expired BOOT line history cannot bridge confirmation counts") {
    if (config::QTR_CONFIRM_TICKS != 2U) return;
    fsm::Robot robot;
    fsm::RobotInput input;
    input.opponent_fresh = true;
    input.opp_raw_mask = 0x78U;
    input.vbat_valid = true;
    input.vbat_v = 11.1F;
    input.t_us = 1000U;
    input.line = {true, true, core::LinePresence::VALID, 1U, 900U, 950U, 1U};
    auto result = robot.step(input);
    CHECK(result.contract_faults == 0U);
    CHECK(result.line_mask == 0U);
    input.previous.applied_valid = true;
    input.previous.token = result.token;
    input.previous.applied_us = 1001U;
    input.t_us = 7000U;
    input.line.presence = core::LinePresence::ABSENT;
    result = robot.step(input);
    CHECK(result.contract_faults == 0U);
    CHECK_FALSE(result.line_available);
    input.previous.token = result.token;
    input.previous.applied_us = 7001U;
    input.t_us = 9000U;
    input.line = {true, true, core::LinePresence::VALID, 2U, 8900U, 8950U, 1U};
    result = robot.step(input);
    CHECK(result.contract_faults == 0U);
    CHECK(result.line_available);
    CHECK(result.line_mask == 0U);
}
