// Locks R1/R5 for D131 bounded deferral without altering established safety tests.
// Tests distinguish eligible front-white ticks from faults, stale evidence and exits.
// Fixed-seed bounded streams and real Gate callbacks cover default/20/100ms copies.
#include "../fixtures/push_through_fixture.h"

using namespace push_test;

TEST_CASE("B4 R5 B9.4 D131 all16 masks preserve immediate rear and pattern-fault priority") {
    for (unsigned mask = 0U; mask < 16U; ++mask) {
        CAPTURE(mask); edge::Escape owner; const auto s = sample(100000U, mask);
        const auto r = owner.step(s);
        if (mask == 0U) { CHECK_FALSE(owner.pushThroughActive()); CHECK_FALSE(r.escape_required); }
        else if (ENABLED && mask <= 3U) deferred(owner, r);
        else actualEntry(owner, r, mask);
    }
}

TEST_CASE("B4 R5 B9.4 D131 any rear or three-white appearance ends a running window immediately") {
    if (!ENABLED) return;
    for (unsigned front : {1U, 2U, 3U}) for (unsigned mask = 4U; mask < 16U; ++mask) {
        edge::Escape owner; auto s = sample(100000U, front); deferred(owner, owner.step(s));
        ++s.t_us; s.line_mask = static_cast<std::uint8_t>(mask);
        actualEntry(owner, owner.step(s), mask);
    }
}

TEST_CASE("B4 R5 B9.4 D131 standalone Guard and default-false caller never gain an exception") {
    for (unsigned mask = 1U; mask < 16U; ++mask) {
        edge::Guard guard; const auto g = guard.step(static_cast<std::uint8_t>(mask), true, false);
        CHECK(g.escape_required);
        edge::Escape owner; auto s = sample(100000U, mask); s.push_eligible = false;
        actualEntry(owner, owner.step(s), mask);
    }
}

TEST_CASE("B3 R1 B9.4 D131 before permission neither white nor eligibility consumes an allowance") {
    for (unsigned mask = 1U; mask < 16U; ++mask) {
        edge::Escape owner; auto s = sample(100000U, mask); s.motion_permitted = false;
        const auto r = owner.step(s); CHECK(r.inhibit_motion); CHECK_FALSE(r.escape_required);
        CHECK_FALSE(owner.pushThroughActive()); CHECK(r.fault == edge::EscapeFault::NONE);
        s.line_mask = 1U; s.motion_permitted = true; ++s.t_us;
        if (ENABLED) deferred(owner, owner.step(s)); else actualEntry(owner, owner.step(s), 1U);
    }
}

TEST_CASE("B3 R1 B9.4 D131 fullhold actual writes stay zero and frontwhite atGO cannot defer") {
    for (auto base : {0U, 0xfff00000U}) {
        Rig rig; rig.opponent(7U); const auto release = rig.release(base); rig.white(1U);
        for (auto age : {1U, 1000000U, 4999999U, 5000000U, 5099999U}) {
            const auto held = rig.at(release + age); stopped(rig, held);
            CHECK_FALSE(held.lifecycle.gate.go); CHECK(held.escape_fault == edge::EscapeFault::NONE);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.at(release + 5100000U); CHECK(go.lifecycle.gate.go);
        escaped(rig, go, 1U); CHECK((edgeFlags(go) & logframe::ENTERED) != 0U);
    }
}

TEST_CASE("B2 R5 B9.4 D131 SEARCH TRACK and new centered admission cannot borrow ATTACK allowance") {
    for (unsigned phase = 0U; phase < 3U; ++phase) {
        Rig rig; rig.opponent(2U); const auto go = rig.go();
        if (phase >= 1U) rig.at(go + 1000U);
        if (phase == 2U) rig.at(go + 2000U);
        rig.white(1U); escaped(rig, rig.next(), 1U);
    }
}

TEST_CASE("B2 R5 B9.4 D131 all15 masks traverse real Robot with current centered contact") {
    for (unsigned mask = 1U; mask < 16U; ++mask) {
        Rig rig; rig.attack(); rig.white(mask); const auto r = rig.next();
        if (ENABLED && mask <= 3U) attacking(rig, r, mask);
        else { escaped(rig, r, mask);
            if (bits(mask) >= 3U) { CHECK(r.escape_fault == edge::EscapeFault::WHITE_PATTERN);
                stopped(rig, r); } }
    }
}

TEST_CASE("B3 B14 R1 B9.4 D131 STOP invalidsources badheading and Gatefailures terminate deferral") {
    if (!ENABLED) return;
    for (unsigned fault = 0U; fault < 5U; ++fault) {
        Rig rig; rig.attack(); rig.white(1U); attacking(rig, rig.next(), 1U);
        if (fault == 0U) rig.input.stop_requested = true;
        if (fault == 1U) rig.input.observations_fresh = false;
        if (fault == 2U) rig.input.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        if (fault == 3U) rig.input.vbat_v = std::numeric_limits<float>::quiet_NaN();
        if (fault == 4U) {
            rig.allow_gate_fault = true;
            rig.port.fail_at = rig.port.operations + 1U;
            rig.input.t_us = rig.now + 1000U; const auto next = rig.robot.step(rig.input);
            rig.port.now = rig.input.t_us; const auto failed = rig.gate.apply(rig.input.t_us, next);
            CHECK_FALSE(failed.feedback.applied_valid); app_test::zero(rig.port);
            rig.input.previous = failed.feedback; rig.now = rig.input.t_us; rig.port.fail_at = 0U;
        }
        const auto stop = rig.next(); CHECK(stop.outputs.ui_state == State::STOPPED); stopped(rig, stop);
        rig.input.stop_requested = false; rig.input.observations_fresh = true;
        rig.input.raw_heading_deg = 0.0F; rig.input.vbat_v = 11.1F; rig.white(0U);
        stopped(rig, rig.next(1000000U)); CHECK(rig.last.outputs.ui_state == State::STOPPED);
    }
}

TEST_CASE("B4 B9.4 D131 invalid consumed initial context cannot hide behind deferral") {
    for (bool healthy : {false, true}) for (unsigned mask : {1U, 2U, 3U}) {
        edge::Escape owner; auto s = sample(100000U, mask); s.imu_ok = healthy;
        s.heading_deg = std::numeric_limits<float>::quiet_NaN(); const auto r = owner.step(s);
        CHECK_FALSE(owner.pushThroughActive()); CHECK(r.escape_required); CHECK(r.inhibit_motion);
        CHECK(r.fault == edge::EscapeFault::INVALID_CONTEXT);
    }
    edge::Escape owner; auto s = sample(100000U, 3U);
    s.opponent_side = static_cast<motion::Direction>(255U); const auto r = owner.step(s);
    CHECK(r.fault == edge::EscapeFault::INVALID_CONTEXT); CHECK_FALSE(owner.pushThroughActive());
}

TEST_CASE("B4 B9.4 D131 unusedside and duties stay unused while unavailable retainedyaw is ignored") {
    if (!ENABLED) return;
    for (unsigned mask : {1U, 2U}) {
        edge::Escape owner; auto s = sample(100000U, mask);
        s.opponent_side = static_cast<motion::Direction>(255U);
        s.applied_duty_l = s.applied_duty_r = std::numeric_limits<float>::quiet_NaN();
        deferred(owner, owner.step(s)); s.t_us += 1000U;
        s.heading_deg = std::numeric_limits<float>::quiet_NaN(); deferred(owner, owner.step(s));
        s.t_us = 100000U + WINDOW_US; actualEntry(owner, owner.step(s), mask);
    }
}

TEST_CASE("B4 B9.4 D131 newly consumed invalid context faults during a running allowance") {
    if (!ENABLED) return;
    for (bool invalid_heading : {false, true}) {
        edge::Escape owner; auto s = sample(); deferred(owner, owner.step(s)); ++s.t_us;
        if (invalid_heading) { s.imu_ok = true; s.heading_deg = std::numeric_limits<float>::infinity(); }
        else { s.line_mask = 3U; s.opponent_side = static_cast<motion::Direction>(255U); }
        const auto r = owner.step(s); CHECK_FALSE(owner.pushThroughActive());
        CHECK(r.escape_required); CHECK(r.inhibit_motion); CHECK(r.fault == edge::EscapeFault::INVALID_CONTEXT);
    }
}

namespace {
std::uint32_t randomWord(std::uint32_t& seed) {
    seed ^= seed << 13U; seed ^= seed >> 17U; seed ^= seed << 5U; return seed;
}
void stream(unsigned trial, std::uint32_t& seed) {
    edge::Escape owner; const auto start = randomWord(seed); auto s = sample(start, 1U + trial % 3U);
    auto r = owner.step(s);
    if (!ENABLED) { CHECK(r.escape_required); CHECK_FALSE(owner.pushThroughActive()); return; }
    deferred(owner, r); bool spent = false; std::uint32_t age = 0U;
    for (unsigned tick = 0U; tick < 24U; ++tick) {
        const auto random = randomWord(seed); age += random % (WINDOW_US / 16U + 1U);
        s.t_us = start + age; s.line_mask = static_cast<std::uint8_t>(random & 15U);
        s.push_eligible = ((random >> 4U) & 7U) != 0U; s.line_updated = true;
        const bool qualifies = s.line_mask != 0U && s.line_mask <= 3U && s.push_eligible && age < WINDOW_US;
        if (!qualifies) spent = true;
        r = owner.step(s);
        if (s.line_mask != 0U && (spent || !qualifies)) {
            CHECK(r.escape_required); CHECK_FALSE(owner.pushThroughActive());
        }
        if (owner.pushThroughActive()) { CHECK_FALSE(spent); CHECK(qualifies);
            CHECK_FALSE(r.entered); CHECK_FALSE(r.exited); CHECK_FALSE(r.replanned); }
        if (bits(s.line_mask) >= 3U) { CHECK(r.inhibit_motion);
            CHECK(r.fault != edge::EscapeFault::NONE); }
    }
}
}

TEST_CASE("B4 R5 B9.4 D131 10000 fixedseed bounded white streams never renew a spent allowance") {
    std::uint32_t seed = 0xD131B94U;
    for (unsigned trial = 0U; trial < 10000U; ++trial) stream(trial, seed);
}

TEST_CASE("B4 R5 B9.4 D131 10000 real Robot streams admit only a bounded frontwhite exception") {
    std::uint32_t seed = 0x5AFE131U;
    for (unsigned trial = 0U; trial < 10000U; ++trial) {
        const auto random = randomWord(seed); Rig rig; rig.attack(true, random);
        const auto mask = 1U + random % 15U; rig.white(mask); const auto first = rig.next();
        if (!ENABLED || mask > 3U) { CHECK(first.outputs.ui_state == State::EDGE_ESCAPE); continue; }
        CHECK(first.outputs.ui_state == State::ATTACK); const auto start = rig.now;
        rig.at(start + WINDOW_US - 1U); CHECK(rig.last.outputs.ui_state == State::ATTACK);
        rig.at(start + WINDOW_US); CHECK(rig.last.outputs.ui_state == State::EDGE_ESCAPE);
        CHECK(rig.last.outputs.duty_l == 0.0F); CHECK(rig.last.outputs.duty_r == 0.0F);
        for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
    }
}
