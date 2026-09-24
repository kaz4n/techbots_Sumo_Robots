// Tests D131's explicit evidence-only white exclusion at the D129 arming boundary.
// Prevents deferred edge episodes from becoming favorable ordinary loss attempts.
// Independent public fixtures use actual Gate receipts and bounded retained frames.
#include "p4_timing_fixture.h"

static_assert(SUMOX_TIMING_EVIDENCE == 1, "These tests require the timing profile");

namespace push_time_test {
using p4_time::Button;
using p4_time::Detail;
using p4_time::State;
constexpr bool ENABLED = config::EDGE_PUSH_THROUGH_MS != 0U;

std::uint32_t firstAttack(p4_time::Rig& rig, std::uint32_t base = 0U) {
    rig.opponent(10U); const auto go = rig.go(base);
    APP_REQUIRE(rig.step(go + 1000U).outputs.ui_state == State::TRACK);
    APP_REQUIRE(rig.step(go + 2000U).outputs.ui_state == State::TRACK);
    APP_REQUIRE(rig.step(go + 3000U).outputs.ui_state == State::ATTACK);
    APP_REQUIRE(!rig.last.contact); APP_REQUIRE(rig.trace_size == 1U);
    CHECK(rig.previous.motors_enabled == (MOTORS_ALLOWED != 0));
    if (MOTORS_ALLOWED) {
        APP_REQUIRE(rig.previous.duty_l > 0.0F); APP_REQUIRE(rig.previous.duty_r > 0.0F);
    }
    return go;
}

void whiteExclusion(const p4_time::Rig& rig, const fsm::RobotResult& result, unsigned mask) {
    CHECK(result.outputs.ui_state == State::ATTACK); CHECK(result.line_mask == mask);
    CHECK_FALSE(result.contact); CHECK(result.contract_faults == 0U);
    CHECK(p4_time::count(result, Detail::INTERRUPTED_EDGE) == (MOTORS_ALLOWED ? 1U : 0U));
    CHECK(p4_time::count(result, Detail::LOSS_READ_START) == 0U);
    CHECK(p4_time::count(result, Detail::LOSS_BRAKE_DECISION) == 0U);
    CHECK(p4_time::count(result, Detail::LOSS_ZERO_APPLIED) == 0U);
    CHECK(rig.trace_size == (MOTORS_ALLOWED ? 2U : 1U));
}

void noRetry(p4_time::Rig& rig) {
    const auto size = rig.trace_size; rig.white(0U);
    CHECK(p4_time::count(rig.step(rig.now + 1000U)) == 0U);
    rig.opponent(0U); const auto loss = rig.now + 1000U;
    CHECK(p4_time::count(rig.step(loss)) == 0U);
    CHECK(p4_time::count(rig.step(loss + 30000U)) == 0U);
    CHECK(rig.last.outputs.ui_state == State::SEARCH);
    CHECK(p4_time::count(rig.step(loss + 31000U)) == 0U);
    CHECK(rig.trace_size == size);
}

struct ExplicitRig : p4_time::Rig {
    std::uint32_t sequence = 0U, source_decision = 0U;
    unsigned mask = 0U;
    ExplicitRig() : p4_time::Rig(true) {
        input.line.explicit_values = true; input.opponent_fresh = true;
    }
    fsm::RobotResult observe(std::uint32_t time, Button button = Button::NONE) {
        input.line.presence = core::LinePresence::ABSENT;
        if (sequence == 0U || time - source_decision >= 2000U) {
            source_decision = time; input.line.presence = core::LinePresence::VALID;
            input.line.sequence = ++sequence; input.line.started_us = time - 100U;
            input.line.completed_us = time - 1U;
            input.line.white_candidates = static_cast<std::uint8_t>(mask);
        }
        return step(time, button);
    }
    std::uint32_t attack() {
        opponent(10U); observe(0U); observe(1000U); observe(21000U);
        observe(22000U, Button::START); observe(42000U, Button::START);
        observe(43000U); APP_REQUIRE(observe(63000U).lifecycle.gate.start_release);
        observe(1563000U); observe(1564000U); observe(4563000U); observe(5162999U);
        APP_REQUIRE(observe(5163000U).lifecycle.gate.go);
        observe(5164000U); observe(5165000U);
        APP_REQUIRE(observe(5166000U).outputs.ui_state == State::ATTACK);
        APP_REQUIRE(trace_size == 1U); return now;
    }
};
} // namespace push_time_test

using namespace push_time_test;

TEST_CASE("B9.4 B15 D131 first eligible arming tick with white closes before any favorable retry") {
    if (!ENABLED) return;
    for (auto base : {0U, 0xfff00000U}) for (unsigned mask : {1U, 2U, 3U}) {
        p4_time::Rig rig(true); firstAttack(rig, base); rig.white(mask);
        const auto white = rig.step(rig.now + 1000U); whiteExclusion(rig, white, mask);
        noRetry(rig);
    }
}

TEST_CASE("B9.4 B15 D131 already armed actual approach closes on first deferred white") {
    if (!ENABLED) return;
    p4_time::Rig rig(true); firstAttack(rig);
    CHECK(p4_time::count(rig.step(rig.now + 1000U)) == 0U);
    APP_REQUIRE(rig.last.outputs.ui_state == State::ATTACK); rig.white(2U);
    whiteExclusion(rig, rig.step(rig.now + 1000U), 2U); noRetry(rig);
}

TEST_CASE("B9.4 B15 D131 retained admitted white stays deferred but cannot repeat or reopen closed trace") {
    if (!ENABLED) return;
    ExplicitRig rig; const auto attack = rig.attack(); rig.mask = 1U;
    const auto fresh = rig.observe(attack + 1000U); APP_REQUIRE(fresh.line_updated);
    whiteExclusion(rig, fresh, 1U); const auto size = rig.trace_size;
    const auto retained = rig.observe(attack + 2000U);
    CHECK(retained.line_available); CHECK_FALSE(retained.line_updated);
    CHECK(retained.outputs.ui_state == State::ATTACK); CHECK(retained.line_mask == 1U);
    CHECK(p4_time::count(retained) == 0U); CHECK(rig.trace_size == size);
    rig.mask = 0U; const auto black = rig.observe(attack + 3000U);
    APP_REQUIRE(black.line_updated); CHECK(p4_time::count(black) == 0U);
    rig.opponent(0U); CHECK(p4_time::count(rig.observe(attack + 4000U)) == 0U);
    CHECK(p4_time::count(rig.observe(attack + 34000U)) == 0U);
    CHECK(rig.last.outputs.ui_state == State::SEARCH);
    CHECK(p4_time::count(rig.observe(attack + 35000U)) == 0U); CHECK(rig.trace_size == size);
}

TEST_CASE("B14 B15 D131 invalid source retains precedence over white on an armed trace") {
    if (!ENABLED) return;
    p4_time::Rig rig(true); firstAttack(rig); rig.step(rig.now + 1000U);
    rig.white(3U); auto value = rig.at(rig.now + 1000U); value.opponent_read.valid = false;
    const auto result = rig.submit(value); CHECK(result.outputs.ui_state == State::ATTACK);
    CHECK(p4_time::count(result, Detail::INVALID_SOURCE_TIME) == (MOTORS_ALLOWED ? 1U : 0U));
    CHECK(p4_time::count(result, Detail::INTERRUPTED_EDGE) == 0U);
    CHECK(p4_time::count(result, Detail::LOSS_ZERO_APPLIED) == 0U);
}

TEST_CASE("B15 D131 genuine completed loss receipt precedes new current white evidence") {
    p4_time::Rig rig(true); rig.approach(0U, 10U); const auto loss = rig.onset();
    const auto brake = rig.brake(loss); rig.white(1U); const auto result = rig.step(brake + 1000U);
    CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(p4_time::count(result, Detail::LOSS_ZERO_APPLIED) == (MOTORS_ALLOWED ? 1U : 0U));
    CHECK(p4_time::count(result, Detail::INTERRUPTED_EDGE) == 0U);
}
