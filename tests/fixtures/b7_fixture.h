// Supplies independent D244 receipt streams and actual Robot/Gate transactions.
// Keeps electrical acknowledgement distinct from physical motion or boot evidence.
// Frozen contract tests use only public interfaces and literal timing boundaries.
#pragma once
#include "app_transaction_fixture.h"
#include "app_service_reset/fixture.h"
#include "core/brownout_sequence.h"
#include <cmath>

namespace b7_test {
using brownout_sequence::Phase;
using brownout_sequence::Reason;
using brownout_sequence::Receipt;
using brownout_sequence::Report;
using brownout_sequence::Sequence;
using Button = core::ButtonLevel;
inline Receipt receipt(std::uint64_t token, unsigned leg, std::uint32_t time,
                       bool enabled = true, float scale = 1.0F) {
    const float sign = leg % 2U == 0U ? 1.0F : -1.0F;
    return {true, token, static_cast<std::uint8_t>(leg), time, enabled,
        enabled ? sign * scale : 0.0F, enabled ? sign * scale : 0.0F};
}
inline void same(const Report& a, const Report& b) {
    CHECK(a.phase == b.phase); CHECK(a.reason == b.reason);
    CHECK(a.leg_index == b.leg_index); CHECK(a.completed_legs == b.completed_legs);
    CHECK(a.completed_cycles == b.completed_cycles); CHECK(a.duty_l == b.duty_l);
    CHECK(a.duty_r == b.duty_r); CHECK(a.consumed == b.consumed); CHECK(a.started == b.started);
    CHECK(a.started_us == b.started_us); CHECK(a.leg_started_us == b.leg_started_us);
    CHECK(a.endpoint_valid == b.endpoint_valid); CHECK(a.endpoint_started_us == b.endpoint_started_us);
    CHECK(a.last_endpoint_us == b.last_endpoint_us);
    CHECK(a.completed_endpoint_started_us == b.completed_endpoint_started_us);
    CHECK(a.completed_endpoint_last_us == b.completed_endpoint_last_us);
    CHECK(a.receipt_seen == b.receipt_seen); CHECK(a.terminal_valid == b.terminal_valid);
    CHECK(a.terminal_us == b.terminal_us); CHECK(a.last_receipt.valid == b.last_receipt.valid);
    CHECK(a.last_receipt.token == b.last_receipt.token);
    CHECK(a.last_receipt.leg_index == b.last_receipt.leg_index);
    CHECK(a.last_receipt.applied_us == b.last_receipt.applied_us);
    CHECK(a.last_receipt.enabled == b.last_receipt.enabled);
    CHECK(a.last_receipt.duty_l == b.last_receipt.duty_l);
    CHECK(a.last_receipt.duty_r == b.last_receipt.duty_r);
}
inline void aborted(const Report& r) {
    CHECK(r.phase == Phase::ABORTED); CHECK(r.reason != Reason::NONE);
    CHECK(r.terminal_valid); CHECK(r.consumed); CHECK(r.duty_l == 0.0F); CHECK(r.duty_r == 0.0F);
}
inline void zero(const app::TransactionReport& r, const app_test::Port& p) {
    CHECK_FALSE(r.robot.outputs.motors_enabled); CHECK(r.robot.outputs.duty_l == 0.0F);
    CHECK(r.robot.outputs.duty_r == 0.0F); CHECK_FALSE(r.applied.feedback.motors_enabled);
    CHECK(r.applied.feedback.duty_l == 0.0F); CHECK(r.applied.feedback.duty_r == 0.0F);
    app_test::zero(p);
}
struct Rig : app_test::Rig {
    std::uint32_t now = 0U;
    std::uint32_t begin(std::uint32_t base = 0U) { now = go(base); return now; }
    const app::TransactionReport& next() { now += 1000U; return tick(now); }
    bool beforeFinal() {
        for (unsigned i = 0U; i < 35000U; ++i) {
            const auto& r = next().robot.brownout;
            if (r.phase == Phase::ABORTED || r.phase == Phase::COMPLETE) return false;
            if (r.completed_legs == 39U && r.endpoint_valid &&
                owner.previous().applied_us - r.endpoint_started_us >= 500000U) return true;
        }
        return false;
    }
};
struct ActualRobot {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::RobotResult result;
    std::uint32_t now = 0U;
    ActualRobot() { APP_REQUIRE(gate.begin()); }
    fsm::RobotResult at(std::uint32_t time, Button button = Button::NONE) {
        now = port.now = input.t_us = time; input.button = button;
        result = robot.step(input);
        if (result.fresh) input.previous = gate.apply(time, result).feedback;
        return result;
    }
    fsm::RobotResult next() { return at(now + 1000U); }
    std::uint32_t go() {
        at(0U); at(1000U); at(21000U); at(22000U, Button::START);
        at(42000U, Button::START); at(43000U); at(63000U);
        APP_REQUIRE(result.lifecycle.gate.start_release);
        at(1563000U); at(1564000U); at(4563000U); at(5162999U);
        APP_REQUIRE(at(5163000U).lifecycle.gate.go); return now;
    }
    bool beforeFinal() {
        for (unsigned i = 0U; i < 35000U; ++i) {
            const auto r = next().brownout;
            if (r.phase == Phase::ABORTED || r.phase == Phase::COMPLETE) return false;
            if (r.completed_legs == 39U && r.endpoint_valid &&
                input.previous.applied_us - r.endpoint_started_us >= 500000U) return true;
        }
        return false;
    }
};
} // namespace b7_test
