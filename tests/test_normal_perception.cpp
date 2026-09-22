// Checks B2/B9 normal routing and the approved D-045/D-046 entry and loss rules.
// Keeps observation qualification and braking separate from external script arbitration.
// Independent host tests cover all masks and real Fusion/motion/governor composition.
#include "doctest.h"
#include "config.h"
#include "core/edge.h"
#include "core/fsm.h"
#include "core/governor.h"
#include "core/opp_fusion.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <initializer_list>

namespace {
constexpr std::array<bool, 8> CENTERED{{false, false, true, true, false, true, true, true}};
constexpr std::array<std::uint8_t, 5> CENTERED_ROWS{{2U, 3U, 5U, 6U, 7U}};

void checkNormal(const fsm::NormalResult& result, core::State state,
                 bool front, bool centered, bool brake = false) {
    CHECK(result.state == state);
    CHECK(result.front_detected == front);
    CHECK(result.centered == centered);
    CHECK(result.brake == brake);
}

void checkZero(const governor::Result& result) {
    CHECK(result.valid);
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
}

struct CommittedNormal {
    opp_fusion::ContactCommit contact;
    fsm::FrontDemand front;
    governor::Result duty;
};

// This wiring is test-owned: the real Robot must still supply arbitration,
// freshness, current script requests, permission and the final MotorGate path.
class NormalHarness {
public:
    void observe(std::uint32_t time, std::uint8_t logical, float impact = 0.0F) {
        opp_fusion::FusionSample sample;
        sample.t_us = time;
        sample.raw_mask = static_cast<std::uint8_t>(logical ^ 0x78U);
        sample.prior_state = selected.state;
        sample.imu_ok = true;
        sample.ax_g = impact;
        observation = fusion.observe(sample);
        time_us = time;
    }

    void route() {
        CHECK(observation.fresh);
        selected = normal.step(observation.phantom.filtered_mask);
    }

    void preempt(core::State state) {
        normal.reset();
        selected = {};
        selected.state = state;
    }

    CommittedNormal commit(const motion::Result& script = {},
            governor::Profile profile = governor::Profile::SEARCH_FORWARD,
            bool permission = true) {
        CommittedNormal result;
        result.contact = fusion.commit(selected.state);
        const bool contact = result.contact.valid && result.contact.result.contact;
        result.front = fsm::frontDemand(selected.state,
            observation.phantom.filtered_mask, contact);
        governor::Request request;
        request.duty_l = result.front.valid ? result.front.duty_l : script.duty_l;
        request.duty_r = result.front.valid ? result.front.duty_r : script.duty_r;
        request.profile = result.front.valid ? result.front.profile : profile;
        request.vbat_v = 9.0F;
        request.centered = selected.centered;
        request.contact = contact;
        request.brake = selected.brake;
        request.inhibited = !permission || !result.contact.valid;
        result.duty = governor.step(time_us, request);
        CHECK(result.duty.valid);
        CHECK(std::isfinite(result.duty.duty_l));
        CHECK(std::isfinite(result.duty.duty_r));
        CHECK(std::fabs(result.duty.duty_l) <= 1.0F);
        CHECK(std::fabs(result.duty.duty_r) <= 1.0F);
        return result;
    }

    CommittedNormal tick(std::uint32_t time, std::uint8_t logical,
                         float impact = 0.0F) {
        observe(time, logical, impact);
        route();
        return commit();
    }

    opp_fusion::Fusion fusion;
    fsm::NormalPerception normal;
    governor::Governor governor;
    opp_fusion::FusionObservation observation;
    fsm::NormalResult selected;
    std::uint32_t time_us = 0U;
};

void establishFullContact(NormalHarness& harness) {
    harness.tick(0U, 2U);
    harness.tick(1000U, 2U);
    harness.tick(2000U, 2U);
    const auto entry = harness.tick(3000U, 2U, 2.0F);
    checkNormal(harness.selected, core::State::ATTACK, true, true);
    CHECK(entry.contact.valid);
    CHECK(entry.contact.result.contact_started);
    const auto full = harness.tick(103000U, 2U);
    CHECK(full.contact.result.contact);
    CHECK_FALSE(full.contact.result.contact_started);
    CHECK(full.duty.duty_l == 1.0F);
    CHECK(full.duty.duty_r == 1.0F);
}
} // namespace

TEST_CASE("B2 NormalPerception has inert result defaults and no initial loss brake") {
    const fsm::NormalResult initial;
    checkNormal(initial, core::State::SEARCH, false, false);
    fsm::NormalPerception normal;
    checkNormal(normal.step(0U), core::State::SEARCH, false, false);
    checkNormal(normal.step(0x80U), core::State::SEARCH, false, false);
    checkNormal(normal.step(0x78U), core::State::DEFEND_TURN, false, false);
}

TEST_CASE("B2 B5 B9 NormalPerception routes all 256 masks from literal front rows") {
    CHECK(config::ATTACK_ENTER_TICKS == 3U);
    for (unsigned raw = 0U; raw < 256U; ++raw) {
        CAPTURE(raw);
        const auto mask = static_cast<std::uint8_t>(raw);
        const unsigned front = raw & 7U;
        const bool centered = CENTERED[front];
        const auto no_front = (raw & 0x78U) != 0U
            ? core::State::DEFEND_TURN : core::State::SEARCH;
        fsm::NormalPerception normal;
        for (unsigned count = 1U; count <= 4U; ++count) {
            const auto expected = front == 0U ? no_front
                : centered && count >= 3U ? core::State::ATTACK : core::State::TRACK;
            checkNormal(normal.step(mask), expected, front != 0U, centered);
        }
    }
}

TEST_CASE("B9 D045 different centered front rows share one consecutive streak") {
    for (const auto first : CENTERED_ROWS) {
        for (const auto second : CENTERED_ROWS) {
            for (const auto third : CENTERED_ROWS) {
                fsm::NormalPerception normal;
                checkNormal(normal.step(first), core::State::TRACK, true, true);
                checkNormal(normal.step(static_cast<std::uint8_t>(second | 0x78U)),
                    core::State::TRACK, true, true);
                checkNormal(normal.step(static_cast<std::uint8_t>(third | 0x80U)),
                    core::State::ATTACK, true, true);
            }
        }
    }
}

TEST_CASE("B9 off-center front resets pending and saturated qualification without braking") {
    for (const unsigned prior_count : {2U, 3U, 20U}) {
        for (const std::uint8_t off_center : std::array<std::uint8_t, 2>{{1U, 4U}}) {
            fsm::NormalPerception normal;
            for (unsigned i = 0U; i < prior_count; ++i) normal.step(2U);
            checkNormal(normal.step(static_cast<std::uint8_t>(off_center | 0xF8U)),
                core::State::TRACK, true, false);
            checkNormal(normal.step(2U), core::State::TRACK, true, true);
            checkNormal(normal.step(2U), core::State::TRACK, true, true);
            checkNormal(normal.step(2U), core::State::ATTACK, true, true);
        }
    }
}

TEST_CASE("B9 D046 every residual mask brakes once after TRACK or ATTACK") {
    for (const unsigned prior_count : {1U, 2U, 3U}) {
        for (unsigned raw = 0U; raw < 256U; raw += 8U) {
            CAPTURE(prior_count);
            CAPTURE(raw);
            fsm::NormalPerception normal;
            for (unsigned i = 0U; i < prior_count; ++i) normal.step(2U);
            const auto expected = (raw & 0x78U) != 0U
                ? core::State::DEFEND_TURN : core::State::SEARCH;
            const auto mask = static_cast<std::uint8_t>(raw);
            checkNormal(normal.step(mask), expected, false, false, true);
            checkNormal(normal.step(mask), expected, false, false);
            checkNormal(normal.step(2U), core::State::TRACK, true, true);
            checkNormal(normal.step(2U), core::State::TRACK, true, true);
            checkNormal(normal.step(2U), core::State::ATTACK, true, true);
        }
    }
}

TEST_CASE("B9 D046 loss after either off-center TRACK row also brakes") {
    for (const std::uint8_t front : std::array<std::uint8_t, 2>{{1U, 4U}}) {
        for (const std::uint8_t residual : std::array<std::uint8_t, 3>{{0U, 8U, 64U}}) {
            fsm::NormalPerception normal;
            normal.step(front);
            const auto destination = residual == 0U
                ? core::State::SEARCH : core::State::DEFEND_TURN;
            checkNormal(normal.step(residual), destination, false, false, true);
            checkNormal(normal.step(residual), destination, false, false);
        }
    }
}

TEST_CASE("B2 D046 side or rear changes and disappearance do not invent front-loss brakes") {
    fsm::NormalPerception normal;
    for (const auto mask : std::array<std::uint8_t, 8>{{8U, 24U, 16U, 32U, 96U, 64U, 120U, 0U}}) {
        const auto destination = mask == 0U ? core::State::SEARCH : core::State::DEFEND_TURN;
        checkNormal(normal.step(mask), destination, false, false);
    }
    checkNormal(normal.step(1U), core::State::TRACK, true, false);
    checkNormal(normal.step(0U), core::State::SEARCH, false, false, true);
    checkNormal(normal.step(0U), core::State::SEARCH, false, false);
    checkNormal(normal.step(4U), core::State::TRACK, true, false);
    checkNormal(normal.step(0U), core::State::SEARCH, false, false, true);
}

TEST_CASE("B9 D045 reset discards every partial or completed preemption streak") {
    for (unsigned prior_count = 0U; prior_count <= 5U; ++prior_count) {
        fsm::NormalPerception normal;
        for (unsigned i = 0U; i < prior_count; ++i) normal.step(2U);
        normal.reset();
        checkNormal(normal.step(2U), core::State::TRACK, true, true);
        checkNormal(normal.step(2U), core::State::TRACK, true, true);
        checkNormal(normal.step(2U), core::State::ATTACK, true, true);
    }
}

TEST_CASE("B9 D045 reset also clears prior front presence and a previous loss pulse") {
    fsm::NormalPerception normal;
    normal.step(2U);
    normal.reset();
    checkNormal(normal.step(8U), core::State::DEFEND_TURN, false, false);
    normal.step(2U);
    checkNormal(normal.step(0U), core::State::SEARCH, false, false, true);
    normal.reset();
    checkNormal(normal.step(0U), core::State::SEARCH, false, false);
    normal.reset();
    normal.reset();
    checkNormal(normal.step(2U), core::State::TRACK, true, true);
}

TEST_CASE("B9 saturated qualification remains ATTACK until a real interruption") {
    fsm::NormalPerception normal;
    normal.step(2U);
    normal.step(2U);
    for (unsigned count = 0U; count < 512U; ++count) {
        checkNormal(normal.step(CENTERED_ROWS[count % CENTERED_ROWS.size()]),
            core::State::ATTACK, true, true);
    }
    checkNormal(normal.step(0U), core::State::SEARCH, false, false, true);
    checkNormal(normal.step(2U), core::State::TRACK, true, true);
}

TEST_CASE("B5 B9 Fusion debounce precedes three fresh normal observations") {
    CHECK(config::OPP_SET_TICKS == 2U);
    NormalHarness harness;
    harness.tick(0U, 2U);
    checkNormal(harness.selected, core::State::SEARCH, false, false);
    harness.tick(1000U, 2U, 2.0F);
    checkNormal(harness.selected, core::State::TRACK, true, true);
    CHECK(harness.observation.cue.cue);
    harness.tick(2000U, 2U);
    checkNormal(harness.selected, core::State::TRACK, true, true);
    const auto entry = harness.tick(3000U, 2U);
    checkNormal(harness.selected, core::State::ATTACK, true, true);
    CHECK(entry.contact.valid);
    CHECK_FALSE(entry.contact.result.contact);
    CHECK_FALSE(entry.contact.result.contact_started);
    CHECK(entry.front.profile == governor::Profile::ATTACK);
    CHECK(entry.front.duty_l == 0.60F);
    CHECK(entry.front.duty_r == 0.60F);
}

TEST_CASE("B5 B9 caller skips cached Fusion observations without accelerating qualification") {
    NormalHarness harness;
    harness.tick(0U, 2U);
    harness.tick(1000U, 2U);
    for (unsigned repeat = 0U; repeat < 8U; ++repeat) {
        harness.observe(1000U, 127U, 3.0F);
        CHECK_FALSE(harness.observation.fresh);
        // The caller deliberately does not route or commit an already consumed sample.
    }
    harness.tick(2000U, 2U);
    checkNormal(harness.selected, core::State::TRACK, true, true);
    const auto entry = harness.tick(3000U, 2U, 2.0F);
    checkNormal(harness.selected, core::State::ATTACK, true, true);
    CHECK(entry.contact.result.contact_started);
}

TEST_CASE("B5 B6 B9 off-center loss of contact immediately applies TRACK cap without loss brake") {
    NormalHarness harness;
    establishFullContact(harness);
    harness.tick(104000U, 1U);
    harness.tick(105000U, 1U);
    const auto off_center = harness.tick(134000U, 1U);
    CHECK(harness.observation.phantom.filtered_mask == 1U);
    checkNormal(harness.selected, core::State::TRACK, true, false);
    CHECK(off_center.contact.valid);
    CHECK_FALSE(off_center.contact.result.contact);
    CHECK_FALSE(off_center.contact.result.contact_started);
    CHECK(off_center.front.profile == governor::Profile::SEARCH_FORWARD);
    CHECK(std::fabs(off_center.duty.duty_l) <= 0.30F);
    CHECK(std::fabs(off_center.duty.duty_r) <= 0.30F);
    CHECK(off_center.duty.duty_r == 0.30F);
}

TEST_CASE("B5 B9 D045 script reentry clears contact and consumes current observation once") {
    for (const auto script : std::array<core::State, 3>{{
            core::State::OPENER, core::State::REFLANK, core::State::EDGE_ESCAPE}}) {
        NormalHarness harness;
        establishFullContact(harness);
        harness.observe(104000U, 2U);
        harness.preempt(script);
        const auto exit = harness.commit();
        CHECK(exit.contact.valid);
        CHECK_FALSE(exit.contact.result.contact);
        for (unsigned entry = 0U; entry < 3U; ++entry) {
            const auto result = harness.tick(204000U + entry * 1000U, 2U);
            const auto state = entry < 2U ? core::State::TRACK : core::State::ATTACK;
            checkNormal(harness.selected, state, true, true);
            CHECK_FALSE(result.contact.result.contact);
            CHECK_FALSE(result.contact.result.contact_started);
            const float cap = entry < 2U ? 0.30F : 0.60F;
            CHECK(result.duty.duty_l <= cap);
            CHECK(result.duty.duty_r <= cap);
        }
        const auto approach = harness.tick(306000U, 2U);
        CHECK(approach.duty.duty_l == 0.60F);
        CHECK(approach.duty.duty_r == 0.60F);
        const auto fresh = harness.tick(307000U, 2U, 2.0F);
        CHECK(fresh.contact.result.contact_started);
    }
}

TEST_CASE("B6 B9 D046 full-duty target loss overrides real SEARCH or DEFEND motion for one tick") {
    CHECK(config::OPP_CLEAR_MS == 30U);
    for (const auto residual : std::array<std::uint8_t, 3>{{0U, 8U, 16U}}) {
        NormalHarness harness;
        establishFullContact(harness);
        harness.tick(104000U, residual);
        harness.tick(105000U, residual);
        const auto before = harness.tick(133999U, residual);
        CHECK(before.contact.result.contact);
        CHECK(before.duty.duty_l == 1.0F);
        CHECK(before.duty.duty_r == 1.0F);
        harness.observe(134000U, residual);
        harness.route();
        const auto state = residual == 0U ? core::State::SEARCH : core::State::DEFEND_TURN;
        checkNormal(harness.selected, state, false, false, true);
        CHECK(harness.observation.phantom.filtered_mask == residual);
        fsm::Search search;
        fsm::DefendTurn defend;
        motion::Result demand;
        if (residual == 0U) {
            CHECK(search.start(134000U, 0.0F, true, {}));
            demand = search.step(134000U, 0.0F, true, 0U).motion;
        } else {
            const float bearing = residual == 8U ? -90.0F : 90.0F;
            CHECK(defend.start(134000U, 0.0F, bearing, true, true));
            demand = defend.step(134000U, 0.0F, true, residual).motion;
        }
        CHECK(std::fabs(demand.duty_l) > 0.0F);
        CHECK(std::fabs(demand.duty_r) > 0.0F);
        const auto loss = harness.commit(demand, governor::Profile::PIVOT);
        CHECK_FALSE(loss.contact.result.contact);
        CHECK_FALSE(loss.front.valid);
        checkZero(loss.duty);
        harness.observe(135000U, residual);
        harness.route();
        checkNormal(harness.selected, state, false, false);
        demand = residual == 0U ? search.step(135000U, 0.0F, true, 0U).motion
            : defend.step(135000U, 0.0F, true, residual).motion;
        const auto next = harness.commit(demand, governor::Profile::PIVOT);
        CHECK(std::fabs(next.duty.duty_l) == doctest::Approx(0.02F));
        CHECK(std::fabs(next.duty.duty_r) == doctest::Approx(0.02F));
        CHECK(next.duty.duty_l * demand.duty_l > 0.0F);
        CHECK(next.duty.duty_r * demand.duty_r > 0.0F);
    }
}

TEST_CASE("B2 B4 B9 external gate or edge preemption clears normal history in the harness") {
    for (const bool gate_closed : {false, true}) {
        NormalHarness harness;
        establishFullContact(harness);
        edge::Guard guard;
        harness.observe(104000U, 2U);
        const auto safety = guard.step(15U, !gate_closed, false);
        CHECK(safety.inhibit_motion);
        CHECK(safety.fault_latched == !gate_closed);
        const auto state = gate_closed ? core::State::STOPPED : core::State::EDGE_ESCAPE;
        harness.preempt(state);
        motion::Result otherwise_moving;
        otherwise_moving.duty_l = 0.8F;
        otherwise_moving.duty_r = -0.8F;
        const auto stopped = harness.commit(otherwise_moving,
            governor::Profile::PIVOT, !safety.inhibit_motion);
        CHECK_FALSE(stopped.contact.result.contact);
        checkZero(stopped.duty);
        // Qualification alone can be inspected; this does not release the latched guard.
        checkNormal(harness.normal.step(2U), core::State::TRACK, true, true);
        CHECK(guard.step(0U, true, true).fault_latched == !gate_closed);
    }
}
