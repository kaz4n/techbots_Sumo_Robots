// Probes D131 using its approved public contract and established D128 fixtures.
// Keeps private review expectations independent of the D131 author test bodies.
// Run separately against literal-zero and copied 20/100ms host configurations.
#include "doctest.h"
#include "core/edge.h"
#include "fixtures/reactive_profile_fixture.h"
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <iostream>

namespace private_d131 {
constexpr std::uint32_t duration = config::EDGE_PUSH_THROUGH_MS * 1000U;
edge::EscapeSample sample(std::uint32_t time, unsigned mask = 1U) {
    edge::EscapeSample s;
    s.t_us = time; s.line_mask = static_cast<std::uint8_t>(mask);
    s.heading_deg = 11.0F; s.imu_ok = true; s.motion_permitted = true;
    s.push_eligible = true; return s;
}
void deferred(const edge::Escape& e, const edge::EscapeResult& r) {
    CHECK(e.pushThroughActive()); CHECK_FALSE(r.escape_required);
    CHECK_FALSE(r.entered); CHECK_FALSE(r.exited); CHECK_FALSE(r.replanned);
    CHECK_FALSE(r.inward_valid); CHECK(r.replans == 0U);
    CHECK(r.fault == edge::EscapeFault::NONE);
}
void entered(const edge::Escape& e, const edge::EscapeResult& r, unsigned mask) {
    CHECK_FALSE(e.pushThroughActive()); CHECK(r.escape_required); CHECK(r.entered);
    CHECK_FALSE(r.exited); CHECK_FALSE(r.replanned); CHECK_FALSE(r.inward_valid);
    CHECK(r.replans == 0U); CHECK(r.selected_mask == mask);
}
}
using namespace private_d131;

TEST_CASE("Private B9.4 baseline layouts and all sixteen first observations") {
    std::cout << "private layout Escape=" << sizeof(edge::Escape)
              << " Sample=" << sizeof(edge::EscapeSample)
              << " pushoffset=" << offsetof(edge::EscapeSample, push_eligible)
              << " Robot=" << sizeof(fsm::Robot)
              << " Runtime=" << sizeof(app::Runtime) << '\n';
    for (unsigned mask = 0; mask != 16U; ++mask) {
        edge::Escape e; auto s = sample(0xFFF00000U, mask); auto r = e.step(s);
        if (duration != 0U && mask >= 1U && mask <= 3U) deferred(e, r);
        else { CHECK_FALSE(e.pushThroughActive()); CHECK(r.escape_required == (mask != 0U)); }
        CHECK(r.replans == 0U);
        edge::Guard guard;
        CHECK(guard.step(static_cast<std::uint8_t>(mask), true, false).escape_required == (mask != 0U));
    }
}

TEST_CASE("Private B9.4 front changes duplicates and uint32 wrap never renew") {
    if (duration == 0U) return;
    for (const auto anchor : {100U, 0xFFFFFF00U}) {
        edge::Escape e; auto s = sample(anchor);
        deferred(e, e.step(s));
        for (unsigned delta = 0U; delta < duration; delta += 137U) {
            s.t_us = anchor + delta; s.line_mask = static_cast<std::uint8_t>(1U + delta % 3U);
            s.opponent_side = delta % 2U ? motion::Direction::LEFT : motion::Direction::RIGHT;
            deferred(e, e.step(s));
        }
        s.t_us = anchor + duration - 1U; s.line_mask = 2U; deferred(e, e.step(s));
        s.t_us = anchor + duration; entered(e, e.step(s), 2U);
        s.t_us++; auto r = e.step(s); CHECK(r.escape_required); CHECK_FALSE(r.entered);
        CHECK(r.row.brake); CHECK(r.replans == 0U);
    }
}

TEST_CASE("Private B9.4 available retained white continues but cannot start") {
    if (duration == 0U) return;
    edge::Escape retained; auto s = sample(300U); s.line_updated = false;
    entered(retained, retained.step(s), 1U);
    edge::Escape e; s.line_updated = true; deferred(e, e.step(s));
    s.line_updated = false; s.t_us += duration - 1U;
    s.imu_ok = false; s.heading_deg = std::numeric_limits<float>::quiet_NaN();
    deferred(e, e.step(s));
    s.t_us++; auto r = e.step(s); entered(e, r, 1U);
    CHECK(r.fault == edge::EscapeFault::NONE); CHECK(r.row.brake);
}

TEST_CASE("Private B9.4 black spends allowance and real completed escape rearms") {
    if (duration == 0U) return;
    edge::Escape e; auto s = sample(1000U); deferred(e, e.step(s));
    s.t_us++; s.line_mask = 0U; auto black = e.step(s);
    CHECK_FALSE(e.pushThroughActive()); CHECK_FALSE(black.escape_required);
    CHECK_FALSE(black.exited); CHECK_FALSE(black.inward_valid); CHECK(black.replans == 0U);
    s.t_us++; s.line_mask = 1U; auto start = e.step(s); entered(e, start, 1U);
    s.line_mask = 0U; s.imu_ok = false; bool exited = false;
    for (unsigned i = 0; i < 2500U && !exited; ++i) {
        s.t_us += 1000U; const auto r = e.step(s); exited = r.exited;
        if (!exited) CHECK(r.escape_required);
        CHECK_FALSE(r.inward_valid);
    }
    REQUIRE(exited); s.t_us += 1000U; s.line_mask = 2U;
    deferred(e, e.step(s));
}

TEST_CASE("Private B9.4 permission before GO grants nothing and active loss spends") {
    if (duration == 0U) return;
    edge::Escape e; auto s = sample(1000U, 15U); s.motion_permitted = false;
    auto r = e.step(s); CHECK(r.fault == edge::EscapeFault::NONE);
    CHECK_FALSE(r.entered); CHECK_FALSE(e.pushThroughActive());
    s.t_us++; s.line_mask = 1U; s.motion_permitted = true; deferred(e, e.step(s));
    s.t_us++; s.motion_permitted = false; r = e.step(s);
    CHECK_FALSE(e.pushThroughActive()); CHECK(r.inhibit_motion);
    CHECK(r.fault == edge::EscapeFault::NONE); CHECK(r.replans == 0U);
    s.t_us++; s.motion_permitted = true; entered(e, e.step(s), 1U);
}

TEST_CASE("Private B9.4 fault transitions never expose timestamp as replan count") {
    if (duration == 0U) return;
    for (unsigned mode = 0; mode < 4U; ++mode) {
        edge::Escape e; auto s = sample(0xABCDEF00U); deferred(e, e.step(s));
        s.t_us++;
        if (mode == 0U) s.line_mask = 7U;
        if (mode == 1U) s.line_mask = 15U;
        if (mode == 2U) s.heading_deg = std::numeric_limits<float>::infinity();
        if (mode == 3U) { s.line_mask = 3U; s.opponent_side = static_cast<motion::Direction>(250); }
        auto r = e.step(s); CHECK(r.entered); CHECK(r.inhibit_motion);
        CHECK(r.fault == (mode < 2U ? edge::EscapeFault::WHITE_PATTERN : edge::EscapeFault::INVALID_CONTEXT));
        CHECK(r.replans == 0U); CHECK_FALSE(e.pushThroughActive());
        s.t_us++; s.line_mask = 0U; s.motion_permitted = false; r = e.step(s);
        CHECK(r.replans == 0U); CHECK(r.row.phase == edge::ScriptPhase::INVALID);
        e.reset(); s = sample(123U); deferred(e, e.step(s));
    }
}

TEST_CASE("Private B9.4 validates only consumed context including initial coordinate") {
    if (duration == 0U) return;
    edge::Escape e; auto s = sample(400U); s.opponent_side = static_cast<motion::Direction>(250);
    s.applied_duty_l = s.applied_duty_r = std::numeric_limits<float>::quiet_NaN();
    deferred(e, e.step(s)); s.t_us++; s.line_mask = 0U;
    s.heading_deg = std::numeric_limits<float>::infinity();
    CHECK(e.step(s).fault == edge::EscapeFault::NONE);
    edge::Escape invalid; s = sample(500U); s.imu_ok = false;
    s.heading_deg = std::numeric_limits<float>::quiet_NaN();
    CHECK(invalid.step(s).fault == edge::EscapeFault::INVALID_CONTEXT);
}

TEST_CASE("Private B9.4 eligibility loss retains front and rear row identity") {
    if (duration == 0U) return;
    for (unsigned mask = 1U; mask < 16U; ++mask) {
        edge::Escape e; auto s = sample(1000U); deferred(e, e.step(s));
        s.t_us++; s.line_mask = static_cast<std::uint8_t>(mask); s.push_eligible = false;
        auto r = e.step(s); CHECK_FALSE(e.pushThroughActive()); CHECK(r.entered);
        CHECK(r.escape_required); CHECK(r.replans == 0U);
        if (mask <= 3U) { CHECK(r.selected_mask == mask); CHECK(r.row.brake); }
    }
}

TEST_CASE("Private B9.4 deterministic chatter cannot buy a second window") {
    if (duration == 0U) return;
    std::uint32_t random = 0xD131AA55U;
    for (unsigned run = 0U; run < 128U; ++run) {
        edge::Escape e; auto s = sample(random); deferred(e, e.step(s));
        const auto anchor = s.t_us; bool black = false;
        for (unsigned tick = 1U; tick < 160U; ++tick) {
            random = random * 1664525U + 1013904223U;
            s.t_us = anchor + tick * 1000U;
            s.line_mask = static_cast<std::uint8_t>((random >> 25U) & 3U);
            const auto r = e.step(s);
            if (s.line_mask == 0U) black = true;
            if (black || tick * 1000U >= duration) CHECK_FALSE(e.pushThroughActive());
            if (e.pushThroughActive()) { CHECK(s.line_mask != 0U); CHECK_FALSE(r.entered); }
        }
    }
}

TEST_CASE("Private B9.4 actual Robot and MotorGate raw FC loss brakes that tick") {
    reactive_test::Rig rig; rig.source.imu_ok = false; rig.attack(false); rig.white(1U);
    const auto start = rig.now + 1000U; auto first = rig.next();
    REQUIRE(first.robot.outputs.ui_state == (duration ? core::State::ATTACK : core::State::EDGE_ESCAPE));
    CHECK(first.robot.line_mask == 1U); CHECK(first.applied.consumed);
    CHECK(first.applied.feedback.applied_valid);
    if (duration == 0U) return;
    CHECK_FALSE(first.robot.contact);
    CHECK(std::fabs(first.robot.outputs.duty_l) <= config::ATTACK_APPROACH_DUTY);
    CHECK(std::fabs(first.robot.outputs.duty_r) <= config::ATTACK_APPROACH_DUTY);
    rig.opponent(0U); auto lost = rig.at(start + 1000U);
    CHECK(lost.robot.opponent_mask == 2U); CHECK(lost.robot.line_mask == 1U);
    CHECK(lost.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    reactive_test::brake(rig, lost);
}

TEST_CASE("Private B9.4 actual Robot deadline and STOP outrank deferral") {
    reactive_test::Rig rig; rig.source.imu_ok = false; rig.attack(false); rig.white(2U);
    const auto first = rig.next(); const auto anchor = rig.now;
    REQUIRE(first.robot.outputs.ui_state == (duration ? core::State::ATTACK : core::State::EDGE_ESCAPE));
    if (duration == 0U) return;
    CHECK(rig.at(anchor + duration - 1U).robot.outputs.ui_state == core::State::ATTACK);
    auto expiry = rig.at(anchor + duration);
    CHECK(expiry.robot.outputs.ui_state == core::State::EDGE_ESCAPE); reactive_test::brake(rig, expiry);
    reactive_test::Rig stop; stop.source.imu_ok = false; stop.attack(false); stop.white(1U); stop.next();
    stop.source.stop_requested = true; const auto stopped = stop.next();
    CHECK(stopped.robot.outputs.ui_state == core::State::STOPPED);
    drive_test::disabled(stopped, stop.port);
}

TEST_CASE("Private B9.4 after new white later contact deflection escapes without stall event") {
    if (duration == 0U || !MOTORS_ALLOWED) return;
    reactive_test::Rig rig; rig.attack(false); rig.opponent(10U); rig.next(); rig.next(); rig.white(1U);
    REQUIRE(rig.next().robot.outputs.ui_state == core::State::ATTACK);
    rig.source.ax_g = 2.0F; REQUIRE(rig.next().robot.contact); rig.source.ax_g = 0.0F;
    for (unsigned tick = 0U; tick < 11U; ++tick) rig.next();
    REQUIRE(rig.owner.report().applied.feedback.duty_l >= config::STALL_MIN_DUTY);
    REQUIRE(rig.owner.report().applied.feedback.duty_r >= config::STALL_MIN_DUTY);
    rig.source.raw_heading_deg = 26.0F; const auto r = rig.next();
    CHECK(r.robot.outputs.ui_state == core::State::EDGE_ESCAPE);
    CHECK(reactive_test::count(r.robot, core::Event::STALL) == 0U);
    CHECK(reactive_test::count(r.robot, core::Event::REFLANK_PHASE) == 0U);
    reactive_test::brake(rig, r);
}
