// Checks composed B5 perception and post-arbitration contact against public contracts.
// Prevents duplicate sampling, stale contact permission and reordered safety filtering.
// Spec-derived host cases cover raw inputs, masks, protocols, events and mirrors.
#include "doctest.h"
#include "config.h"
#include "core/governor.h"
#include "core/opp_fusion.h"
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();

opp_fusion::FusionSample sample(std::uint32_t time, std::uint8_t logical,
                               core::State prior = core::State::TRACK,
                               float heading = 0.0F, float impact = 0.0F,
                               bool edge = false, bool imu_ok = true) {
    opp_fusion::FusionSample result;
    result.t_us = time;
    result.raw_mask = static_cast<std::uint8_t>(logical ^ 0x78U);
    result.prior_state = prior;
    result.heading_deg = heading;
    result.ax_g = impact;
    result.imu_ok = imu_ok;
    result.edge_event = edge;
    return result;
}

opp_fusion::FusionObservation observeAndCommit(opp_fusion::Fusion& fusion,
        const opp_fusion::FusionSample& input, core::State selected = core::State::TRACK) {
    const auto observation = fusion.observe(input);
    CHECK(observation.fresh);
    CHECK(fusion.commit(selected).valid);
    return observation;
}

void checkNoContact(const opp_fusion::ContactResult& result) {
    CHECK_FALSE(result.contact);
    CHECK_FALSE(result.contact_started);
}

void checkInvalidCommit(const opp_fusion::ContactCommit& commit) {
    CHECK_FALSE(commit.valid);
    checkNoContact(commit.result);
    CHECK_FALSE(commit.result.close_cue);
    CHECK_FALSE(commit.result.impact_cue);
    CHECK_FALSE(commit.result.cue);
}

void establishImpactContact(opp_fusion::Fusion& fusion, std::uint32_t start = 0U) {
    observeAndCommit(fusion, sample(start, 2U), core::State::TRACK);
    const auto observation = fusion.observe(sample(start + 1000U, 2U,
        core::State::TRACK, 0.0F, 2.0F));
    CHECK(observation.bearing.centered);
    CHECK(observation.cue.impact_cue);
    const auto contact = fusion.commit(core::State::ATTACK);
    CHECK(contact.valid);
    CHECK(contact.result.contact);
    CHECK(contact.result.contact_started);
}

void compareContact(const opp_fusion::ContactResult& a, const opp_fusion::ContactResult& b) {
    CHECK(a.close_cue == b.close_cue);
    CHECK(a.impact_cue == b.impact_cue);
    CHECK(a.cue == b.cue);
    CHECK(a.contact == b.contact);
    CHECK(a.contact_started == b.contact_started);
}

std::uint8_t mirrored(std::uint8_t mask) {
    return static_cast<std::uint8_t>((mask & 2U) |
        ((mask & 1U) << 2U) | ((mask & 4U) >> 2U) |
        ((mask & 8U) << 1U) | ((mask & 16U) >> 1U) |
        ((mask & 32U) << 1U) | ((mask & 64U) >> 1U));
}

governor::Request attackRequest(const opp_fusion::FusionObservation& observation,
                               const opp_fusion::ContactCommit& commit) {
    governor::Request request;
    request.duty_l = request.duty_r = 1.0F;
    request.vbat_v = 11.1F;
    request.profile = governor::Profile::ATTACK;
    request.centered = observation.bearing.centered;
    request.contact = commit.valid && commit.result.contact;
    request.inhibited = false;
    return request;
}
} // namespace

TEST_CASE("B5 Fusion defaults and missing commitment cannot produce contact permission") {
    opp_fusion::Fusion fusion;
    CHECK_FALSE(fusion.memory().valid);
    CHECK_FALSE(fusion.memory().world_valid);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::UNKNOWN);
    checkInvalidCommit(fusion.commit(core::State::ATTACK));
    checkInvalidCommit(fusion.commit(core::State::TRACK));
}

TEST_CASE("B5.1 Fusion all128 raw polarity masks debounce before every downstream stage") {
    CHECK(config::OPP_ACTIVE_LOW_MASK == 0x78U);
    CHECK(config::OPP_SET_TICKS == 2U);
    for (unsigned logical = 0U; logical < 128U; ++logical) {
        for (unsigned high : {0U, 128U}) {
            opp_fusion::Fusion fusion;
            auto first = sample(0U, static_cast<std::uint8_t>(logical), core::State::SEARCH);
            first.raw_mask = static_cast<std::uint8_t>(first.raw_mask | high);
            const auto a = observeAndCommit(fusion, first, core::State::SEARCH);
            CHECK(a.confirmed_mask == 0U);
            CHECK(a.phantom.filtered_mask == 0U);
            CHECK_FALSE(a.bearing.detected);
            first.t_us = 1000U;
            const auto b = observeAndCommit(fusion, first, core::State::SEARCH);
            CHECK(b.confirmed_mask == logical);
            CHECK(b.stuck.filtered_mask == logical);
            CHECK(b.phantom.filtered_mask == logical);
            CHECK(b.stuck.fault_mask == 0U);
            CHECK_FALSE(b.cue.close_cue);
            CHECK(b.bearing.detected == (logical != 0U));
            const auto expected_group = (logical & 7U) != 0U ? opp_fusion::Group::FRONT :
                (logical & 24U) != 0U ? opp_fusion::Group::SIDE :
                (logical & 96U) != 0U ? opp_fusion::Group::REAR : opp_fusion::Group::NONE;
            CHECK(b.bearing.group == expected_group);
        }
    }
}

TEST_CASE("B5.1 Fusion duplicate timestamp cannot qualify a second electrical sample") {
    opp_fusion::Fusion fusion;
    const auto input = sample(0U, 2U);
    CHECK(fusion.observe(input).confirmed_mask == 0U);
    for (unsigned duplicate = 0U; duplicate < 30U; ++duplicate) {
        const auto cached = fusion.observe(input);
        CHECK_FALSE(cached.fresh);
        CHECK(cached.confirmed_mask == 0U);
    }
    CHECK(fusion.commit(core::State::ATTACK).valid);
    const auto next = fusion.observe(sample(1000U, 2U));
    CHECK(next.fresh);
    CHECK(next.confirmed_mask == 2U);
    CHECK(fusion.commit(core::State::ATTACK).valid);
}

TEST_CASE("B5.1 Fusion clear hysteresis uses exact30ms including micros wrap") {
    for (std::uint32_t start : {0U, 0xFFFFF000U}) {
        opp_fusion::Fusion fusion;
        observeAndCommit(fusion, sample(start, 8U));
        CHECK(observeAndCommit(fusion, sample(start + 1000U, 8U)).confirmed_mask == 8U);
        CHECK(observeAndCommit(fusion, sample(start + 2000U, 0U)).confirmed_mask == 8U);
        CHECK(observeAndCommit(fusion, sample(start + 31999U, 0U)).confirmed_mask == 8U);
        const auto cleared = observeAndCommit(fusion, sample(start + 32000U, 0U));
        CHECK(cleared.confirmed_mask == 0U);
        CHECK_FALSE(cleared.bearing.detected);
    }
}

TEST_CASE("B5.2 Fusion bilateral conflict preserves no-history uncertainty") {
    for (std::uint8_t mask : {std::uint8_t{24U}, std::uint8_t{96U}}) {
        opp_fusion::Fusion fusion;
        observeAndCommit(fusion, sample(0U, mask, core::State::SEARCH));
        const auto observation = observeAndCommit(fusion, sample(1000U, mask, core::State::SEARCH));
        CHECK(observation.bearing.detected);
        CHECK(observation.bearing.conflict);
        CHECK_FALSE(observation.bearing.bearing_valid);
        CHECK_FALSE(fusion.memory().valid);
    }
}

TEST_CASE("B5 Fusion unavailable or nonfinite IMU preserves relative but not world evidence") {
    for (bool imu_ok : {false, true}) {
        for (float heading : {30.0F, NAN_VALUE, INF_VALUE, -INF_VALUE}) {
            opp_fusion::Fusion fusion;
            observeAndCommit(fusion, sample(0U, 2U, core::State::SEARCH, heading, 0.0F, false, imu_ok));
            const auto observation = observeAndCommit(fusion,
                sample(1000U, 2U, core::State::SEARCH, heading, 0.0F, false, imu_ok));
            CHECK(observation.bearing.bearing_valid);
            CHECK(observation.bearing.relative_deg == 0.0F);
            const bool world_valid = imu_ok && std::isfinite(heading);
            CHECK(observation.bearing.world_valid == world_valid);
            CHECK(fusion.memory().world_valid == world_valid);
            if (world_valid) CHECK(observation.bearing.world_deg == 30.0F);
        }
    }
}

TEST_CASE("B5.4 split Contact observes each close cue once despite repeated latch commitments") {
    for (std::uint8_t mask : {std::uint8_t{5U}, std::uint8_t{7U}}) {
        opp_fusion::Contact contact;
        for (unsigned count = 1U; count <= 20U; ++count) {
            const auto cue = contact.observeCue(mask, 0.0F, 0.0F, true);
            CHECK(cue.close_cue == (count == 20U));
            for (unsigned repeat = 0U; repeat < 8U; ++repeat) {
                const auto latch = contact.commitLatch(core::State::ATTACK, mask, cue);
                CHECK(latch.contact == (count == 20U));
                CHECK(latch.contact_started == (count == 20U && repeat == 0U));
            }
        }
    }
}

TEST_CASE("B5.4 split Contact preserves legacy step behavior across cues and state transitions") {
    opp_fusion::Contact legacy, split;
    const core::State states[5] = {core::State::TRACK, core::State::ATTACK,
        core::State::EDGE_ESCAPE, core::State::REFLANK, core::State::ATTACK};
    for (unsigned tick = 0U; tick < 160U; ++tick) {
        const auto state = states[(tick / 32U) % 5U];
        const std::uint8_t mask = tick < 50U ? 7U : tick < 100U ? 5U : tick < 130U ? 2U : 1U;
        const float impact = tick == 110U || tick == 140U ? 2.0F : 0.0F;
        const bool imu_ok = tick != 110U;
        const auto expected = legacy.step(state, mask, impact, 0.0F, imu_ok);
        const auto cue = split.observeCue(mask, impact, 0.0F, imu_ok);
        compareContact(expected, split.commitLatch(state, mask, cue));
    }
}

TEST_CASE("B5.4 Fusion close cues reach20 confirmed samples exactly despite cached observations") {
    for (std::uint8_t mask : {std::uint8_t{5U}, std::uint8_t{7U}}) {
        opp_fusion::Fusion fusion;
        for (unsigned tick = 0U; tick <= 20U; ++tick) {
            const auto input = sample(tick * 1000U, mask, core::State::TRACK);
            const auto observation = fusion.observe(input);
            CHECK(observation.cue.close_cue == (tick == 20U));
            for (unsigned duplicate = 0U; duplicate < 3U; ++duplicate) {
                const auto cached = fusion.observe(input);
                CHECK_FALSE(cached.fresh);
                CHECK(cached.cue.close_cue == observation.cue.close_cue);
            }
            const auto commit = fusion.commit(tick == 20U ? core::State::ATTACK : core::State::TRACK);
            CHECK(commit.valid);
            CHECK(commit.result.contact == (tick == 20U));
            CHECK(commit.result.contact_started == (tick == 20U));
        }
    }
}

TEST_CASE("B5.4 Fusion current impact latches on same-tick centered ATTACK entry") {
    opp_fusion::Fusion fusion;
    establishImpactContact(fusion);
    const auto observation = fusion.observe(sample(2000U, 2U, core::State::ATTACK));
    CHECK_FALSE(observation.cue.cue);
    const auto held = fusion.commit(core::State::ATTACK);
    CHECK(held.valid);
    CHECK(held.result.contact);
    CHECK_FALSE(held.result.contact_started);
}

TEST_CASE("B5.4 Fusion every nonATTACK state immediately clears contact and prevents carryover") {
    const core::State exits[] = {core::State::BOOT, core::State::IDLE, core::State::COUNTDOWN,
        core::State::OPENER, core::State::SEARCH, core::State::TRACK, core::State::DEFEND_TURN,
        core::State::EDGE_ESCAPE, core::State::REFLANK, core::State::STOPPED, core::State::DRIVE_TEST};
    for (auto exit : exits) {
        opp_fusion::Fusion fusion;
        establishImpactContact(fusion);
        CHECK(fusion.observe(sample(2000U, 2U, core::State::ATTACK)).fresh);
        const auto cleared = fusion.commit(exit);
        CHECK(cleared.valid);
        checkNoContact(cleared.result);
        CHECK(fusion.observe(sample(3000U, 2U, exit)).fresh);
        const auto reentry = fusion.commit(core::State::ATTACK);
        CHECK(reentry.valid);
        checkNoContact(reentry.result);
    }
}

TEST_CASE("B5.4 Fusion target loss and off-centering clear at their confirmed observation") {
    for (std::uint8_t next_mask : {std::uint8_t{0U}, std::uint8_t{4U}}) {
        opp_fusion::Fusion fusion;
        establishImpactContact(fusion);
        for (std::uint32_t time : {2000U, 3000U, 31999U}) {
            const auto observation = fusion.observe(sample(time, next_mask, core::State::ATTACK));
            CHECK(observation.bearing.centered);
            CHECK(fusion.commit(core::State::ATTACK).result.contact);
        }
        const auto loss = fusion.observe(sample(32000U, next_mask, core::State::ATTACK));
        CHECK(loss.phantom.filtered_mask == next_mask);
        CHECK_FALSE(loss.bearing.centered);
        const auto cleared = fusion.commit(core::State::ATTACK);
        CHECK(cleared.valid);
        checkNoContact(cleared.result);
    }
}

TEST_CASE("B5 Fusion duplicate observation ignores changed data while preserving one pending commitment") {
    opp_fusion::Fusion fusion;
    observeAndCommit(fusion, sample(0U, 2U));
    const auto original = fusion.observe(sample(1000U, 2U));
    const auto changed = fusion.observe(sample(1000U, 7U, core::State::ATTACK, 361.0F, 2.0F, true));
    CHECK_FALSE(changed.fresh);
    CHECK(changed.confirmed_mask == original.confirmed_mask);
    CHECK(changed.phantom.filtered_mask == 2U);
    CHECK_FALSE(changed.cue.cue);
    CHECK_FALSE(changed.phantom.phantom_set);
    CHECK(changed.stuck.new_fault_mask == 0U);
    CHECK(changed.bearing.world_deg == 0.0F);
    const auto commit = fusion.commit(core::State::ATTACK);
    CHECK(commit.valid);
    checkNoContact(commit.result);
}

TEST_CASE("B5 Fusion double commitment clears latch and duplicate observe cannot reopen it") {
    opp_fusion::Fusion fusion;
    establishImpactContact(fusion);
    checkInvalidCommit(fusion.commit(core::State::ATTACK));
    const auto cached = fusion.observe(sample(1000U, 2U, core::State::ATTACK, 0.0F, 2.0F));
    CHECK_FALSE(cached.fresh);
    checkInvalidCommit(fusion.commit(core::State::ATTACK));
    CHECK(fusion.observe(sample(2000U, 2U, core::State::ATTACK)).fresh);
    const auto fresh = fusion.commit(core::State::ATTACK);
    CHECK(fresh.valid);
    checkNoContact(fresh.result);
}

TEST_CASE("B5 Fusion replacing an uncommitted observation discards the previous contact latch") {
    opp_fusion::Fusion fusion;
    establishImpactContact(fusion);
    CHECK(fusion.observe(sample(2000U, 2U, core::State::ATTACK)).fresh);
    CHECK(fusion.observe(sample(3000U, 2U, core::State::ATTACK)).fresh);
    const auto commit = fusion.commit(core::State::ATTACK);
    CHECK(commit.valid);
    checkNoContact(commit.result);
}

TEST_CASE("B5.5 Fusion uses pre-edge chase state and emits a single phantom event") {
    for (auto prior : {core::State::TRACK, core::State::ATTACK, core::State::EDGE_ESCAPE}) {
        opp_fusion::Fusion fusion;
        observeAndCommit(fusion, sample(0U, 2U, prior));
        observeAndCommit(fusion, sample(1000U, 2U, prior));
        const auto input = sample(2000U, 2U, prior, 20.0F, 0.0F, true);
        const auto observation = fusion.observe(input);
        const bool chase = prior != core::State::EDGE_ESCAPE;
        CHECK(observation.phantom.phantom_set == chase);
        CHECK(observation.phantom.active == chase);
        CHECK(observation.phantom.filtered_mask == (chase ? 0U : 2U));
        const auto committed = fusion.commit(core::State::EDGE_ESCAPE);
        CHECK(committed.valid);
        checkNoContact(committed.result);
        const auto cached = fusion.observe(input);
        CHECK_FALSE(cached.fresh);
        CHECK_FALSE(cached.phantom.phantom_set);
        checkInvalidCommit(fusion.commit(core::State::ATTACK));
    }
}

TEST_CASE("B5.5 Fusion current and prior episode contact cues both block phantom marking") {
    for (bool prior_impact : {false, true}) {
        opp_fusion::Fusion fusion;
        observeAndCommit(fusion, sample(0U, 2U));
        observeAndCommit(fusion, sample(1000U, 2U, core::State::TRACK, 0.0F,
            prior_impact ? 2.0F : 0.0F), core::State::ATTACK);
        const auto observation = fusion.observe(sample(2000U, 2U, core::State::ATTACK,
            0.0F, prior_impact ? 0.0F : 2.0F, true));
        CHECK_FALSE(observation.phantom.phantom_set);
        CHECK_FALSE(observation.phantom.active);
        CHECK(observation.phantom.filtered_mask == 2U);
        CHECK(fusion.commit(core::State::EDGE_ESCAPE).valid);
    }
}

TEST_CASE("B5.3 B5.5 Fusion remembers only effective detections through phantom expiry") {
    opp_fusion::Fusion fusion;
    observeAndCommit(fusion, sample(0U, 4U, core::State::TRACK, 10.0F));
    observeAndCommit(fusion, sample(1000U, 4U, core::State::TRACK, 10.0F));
    CHECK(fusion.memory().last_world_bearing_deg == 25.0F);
    const auto marked = observeAndCommit(fusion, sample(2000U, 4U, core::State::TRACK, 10.0F, 0.0F, true));
    CHECK(marked.phantom.phantom_set);
    CHECK_FALSE(marked.bearing.detected);
    CHECK(fusion.memory().last_seen_us == 1000U);
    const auto masked = observeAndCommit(fusion, sample(3000U, 4U, core::State::SEARCH, 20.0F));
    CHECK(masked.phantom.filtered_mask == 0U);
    CHECK(fusion.memory().last_seen_us == 1000U);
    const auto outside = observeAndCommit(fusion, sample(4000U, 4U, core::State::SEARCH, 50.0F));
    CHECK(outside.bearing.world_deg == 65.0F);
    CHECK(fusion.memory().last_seen_us == 4000U);
    const auto expiry = observeAndCommit(fusion, sample(3002000U, 4U, core::State::SEARCH, 10.0F));
    CHECK_FALSE(expiry.phantom.active);
    CHECK(expiry.phantom.filtered_mask == 4U);
    CHECK(fusion.memory().last_seen_us == 3002000U);
}

TEST_CASE("B5.4 B5.5 Fusion close masks override phantom before twenty-tick contact qualification") {
    for (std::uint8_t close_mask : {std::uint8_t{5U}, std::uint8_t{7U}}) {
        const std::uint8_t initial = close_mask == 5U ? 1U : 2U;
        opp_fusion::Fusion fusion;
        observeAndCommit(fusion, sample(0U, initial));
        CHECK(observeAndCommit(fusion, sample(1000U, initial, core::State::TRACK, 0.0F, 0.0F, true)).phantom.phantom_set);
        observeAndCommit(fusion, sample(2000U, close_mask));
        for (unsigned tick = 3U; tick <= 22U; ++tick) {
            const auto observation = fusion.observe(sample(tick * 1000U, close_mask));
            CHECK(observation.phantom.active);
            CHECK(observation.phantom.filtered_mask == close_mask);
            CHECK(observation.bearing.close);
            CHECK(observation.cue.close_cue == (tick == 22U));
            const auto commit = fusion.commit(tick == 22U ? core::State::ATTACK : core::State::TRACK);
            CHECK(commit.valid);
            CHECK(commit.result.contact == (tick == 22U));
        }
    }
}

TEST_CASE("B5.6 Fusion faults remove newly stuck bits before cues and effective bearing") {
    opp_fusion::Fusion fusion;
    for (unsigned tick = 0U; tick <= 20U; ++tick) {
        observeAndCommit(fusion, sample(tick * 1000U, 7U, core::State::ATTACK), core::State::ATTACK);
    }
    const auto last_seen = fusion.memory().last_seen_us;
    const auto input = sample(5001000U, 7U, core::State::ATTACK, 361.0F);
    const auto fault = fusion.observe(input);
    CHECK(fault.confirmed_mask == 7U);
    CHECK(fault.stuck.new_fault_mask == 7U);
    CHECK(fault.stuck.fault_mask == 7U);
    CHECK(fault.stuck.filtered_mask == 0U);
    CHECK_FALSE(fault.cue.cue);
    CHECK(fault.phantom.filtered_mask == 0U);
    CHECK_FALSE(fault.bearing.detected);
    CHECK(fusion.memory().last_seen_us == last_seen);
    const auto commit = fusion.commit(core::State::ATTACK);
    CHECK(commit.valid);
    checkNoContact(commit.result);
    const auto cached = fusion.observe(input);
    CHECK_FALSE(cached.fresh);
    CHECK(cached.stuck.new_fault_mask == 0U);
    CHECK(cached.stuck.fault_mask == 7U);
}

TEST_CASE("B5.5 B5.6 phantom suppression cannot interrupt raw stuck qualification") {
    opp_fusion::Fusion fusion;
    observeAndCommit(fusion, sample(0U, 2U));
    const auto first = observeAndCommit(fusion, sample(1000U, 2U, core::State::TRACK, 0.0F, 0.0F, true));
    CHECK(first.phantom.filtered_mask == 0U);
    observeAndCommit(fusion, sample(2000000U, 2U, core::State::SEARCH));
    observeAndCommit(fusion, sample(4000000U, 2U, core::State::TRACK));
    const auto replaced = observeAndCommit(fusion, sample(4001000U, 2U, core::State::TRACK, 0.0F, 0.0F, true));
    CHECK(replaced.phantom.phantom_set);
    CHECK(replaced.phantom.filtered_mask == 0U);
    const auto fault = observeAndCommit(fusion, sample(5001000U, 2U, core::State::TRACK, 361.0F));
    CHECK(fault.stuck.fault_mask == 2U);
    CHECK(fault.stuck.new_fault_mask == 2U);
    CHECK(fault.phantom.active);
    CHECK(fault.phantom.filtered_mask == 0U);
}

TEST_CASE("B5 Fusion reset clears all filters memory pulses and pending commitment") {
    opp_fusion::Fusion fusion;
    observeAndCommit(fusion, sample(0U, 2U));
    observeAndCommit(fusion, sample(1000U, 2U, core::State::TRACK, 0.0F, 0.0F, true));
    observeAndCommit(fusion, sample(5001000U, 2U, core::State::TRACK, 361.0F));
    CHECK(fusion.observe(sample(5002000U, 2U)).stuck.fault_mask == 2U);
    fusion.reset();
    CHECK_FALSE(fusion.memory().valid);
    CHECK_FALSE(fusion.memory().world_valid);
    checkInvalidCommit(fusion.commit(core::State::ATTACK));
    const auto first = observeAndCommit(fusion, sample(5002000U, 2U));
    CHECK(first.confirmed_mask == 0U);
    CHECK(first.stuck.fault_mask == 0U);
    CHECK(first.stuck.new_fault_mask == 0U);
    CHECK_FALSE(first.phantom.active);
    CHECK_FALSE(first.phantom.phantom_set);
    CHECK_FALSE(first.cue.cue);
    establishImpactContact(fusion, 6000000U);
}

TEST_CASE("B5 Fusion phantom deadline and fresh observations remain correct across micros wrap") {
    opp_fusion::Fusion fusion;
    const std::uint32_t start = 0xFFFFF000U;
    observeAndCommit(fusion, sample(start, 2U));
    observeAndCommit(fusion, sample(start + 1000U, 2U));
    const auto marked = observeAndCommit(fusion, sample(start + 1501000U, 2U,
        core::State::TRACK, 0.0F, 0.0F, true));
    CHECK(marked.phantom.phantom_set);
    const auto before = observeAndCommit(fusion, sample(start + 4500999U, 2U, core::State::SEARCH));
    CHECK(before.phantom.active);
    CHECK(before.phantom.filtered_mask == 0U);
    const auto at = observeAndCommit(fusion, sample(start + 4501000U, 2U, core::State::SEARCH));
    CHECK_FALSE(at.phantom.active);
    CHECK(at.phantom.filtered_mask == 2U);
}

TEST_CASE("B5 Fusion ten thousand mirrored observations explicitly cover all128 raw masks") {
    opp_fusion::Fusion right, left;
    std::uint32_t seed = 0xB5F0510U;
    unsigned coverage[128] = {};
    const core::State priors[4] = {core::State::TRACK, core::State::ATTACK,
        core::State::SEARCH, core::State::REFLANK};
    for (unsigned tick = 0U; tick < 10000U; ++tick) {
        seed = 1664525U * seed + 1013904223U;
        const auto mask = static_cast<std::uint8_t>((tick * 73U + 31U) & 127U);
        ++coverage[mask];
        const float heading = static_cast<float>((seed >> 16U) % 121U) - 60.0F;
        auto a = sample(0xFFFF0000U + tick * 1000U, mask, priors[tick % 4U],
            heading, tick % 1000U == 0U ? 2.0F : 0.0F, tick % 200U == 0U);
        auto b = a;
        b.raw_mask = static_cast<std::uint8_t>(mirrored(mask) ^ 0x78U);
        b.heading_deg = -heading;
        const auto r = right.observe(a), l = left.observe(b);
        CHECK(r.fresh); CHECK(l.fresh);
        CHECK(mirrored(r.confirmed_mask) == l.confirmed_mask);
        CHECK(mirrored(r.stuck.fault_mask) == l.stuck.fault_mask);
        CHECK(mirrored(r.phantom.filtered_mask) == l.phantom.filtered_mask);
        CHECK(r.cue.close_cue == l.cue.close_cue);
        CHECK(r.cue.impact_cue == l.cue.impact_cue);
        CHECK(r.phantom.phantom_set == l.phantom.phantom_set);
        CHECK(r.bearing.group == l.bearing.group);
        CHECK(r.bearing.bearing_valid == l.bearing.bearing_valid);
        CHECK(r.bearing.world_valid == l.bearing.world_valid);
        CHECK(r.bearing.centered == l.bearing.centered);
        if (r.bearing.bearing_valid) CHECK(r.bearing.relative_deg == -l.bearing.relative_deg);
        if (r.bearing.world_valid) CHECK(std::remainder(r.bearing.world_deg + l.bearing.world_deg, 360.0F) == 0.0F);
        const auto state = tick % 2U == 0U ? core::State::ATTACK : core::State::TRACK;
        const auto rc = right.commit(state), lc = left.commit(state);
        CHECK(rc.valid); CHECK(lc.valid);
        compareContact(rc.result, lc.result);
    }
    unsigned total = 0U;
    for (auto count : coverage) { CHECK(count >= 78U); total += count; }
    CHECK(total == 10000U);
}

TEST_CASE("B5 B6 Fusion current centered committed contact alone enables governor full duty") {
    opp_fusion::Fusion fusion;
    governor::Governor governor;
    const auto first = fusion.observe(sample(0U, 2U));
    const auto first_commit = fusion.commit(core::State::TRACK);
    CHECK(governor.step(0U, attackRequest(first, first_commit)).duty_l == 0.0F);
    const auto impact = fusion.observe(sample(1000U, 2U, core::State::TRACK, 0.0F, 2.0F));
    const auto impact_commit = fusion.commit(core::State::ATTACK);
    CHECK(impact_commit.result.contact_started);
    CHECK(governor.step(1000U, attackRequest(impact, impact_commit)).duty_l == doctest::Approx(0.02F));
    const auto held = fusion.observe(sample(100000U, 2U, core::State::ATTACK));
    const auto held_commit = fusion.commit(core::State::ATTACK);
    const auto full = governor.step(100000U, attackRequest(held, held_commit));
    CHECK(full.duty_l == 1.0F); CHECK(full.duty_r == 1.0F);
    const auto exit = fusion.observe(sample(100001U, 2U, core::State::ATTACK));
    const auto exit_commit = fusion.commit(core::State::TRACK);
    checkNoContact(exit_commit.result);
    const auto reduced = governor.step(100001U, attackRequest(exit, exit_commit));
    CHECK(reduced.duty_l == doctest::Approx(0.60F));
    CHECK(reduced.duty_r == doctest::Approx(0.60F));
    const auto invalid = fusion.commit(core::State::ATTACK);
    checkInvalidCommit(invalid);
    const auto rejected = governor.step(100002U, attackRequest(exit, invalid));
    CHECK(rejected.duty_l <= 0.60F); CHECK(rejected.duty_r <= 0.60F);
}
