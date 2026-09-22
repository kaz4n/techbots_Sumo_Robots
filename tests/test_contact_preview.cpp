// Checks B5.4 contact candidates against the D-027 and D-056 public contracts.
// Prevents speculative arbitration from creating contact or consuming observations.
// Independent host cases exercise purity, cue counts, commitment, cache and reset.
#include "doctest.h"
#include "config.h"
#include "core/opp_fusion.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr core::State STATES[] = {
    core::State::BOOT, core::State::IDLE, core::State::COUNTDOWN,
    core::State::OPENER, core::State::SEARCH, core::State::TRACK,
    core::State::ATTACK, core::State::DEFEND_TURN, core::State::EDGE_ESCAPE,
    core::State::REFLANK, core::State::STOPPED, core::State::DRIVE_TEST
};
constexpr opp_fusion::ContactCue IMPACT = {false, true, true};
constexpr opp_fusion::ContactCue NONE = {};

void checkResult(const opp_fusion::ContactResult& result,
                 const opp_fusion::ContactCue& cue, bool contact, bool started) {
    CHECK(result.close_cue == cue.close_cue);
    CHECK(result.impact_cue == cue.impact_cue);
    CHECK(result.cue == cue.cue);
    CHECK(result.contact == contact);
    CHECK(result.contact_started == started);
}

void checkInvalid(const opp_fusion::ContactCommit& result) {
    CHECK_FALSE(result.valid);
    checkResult(result.result, NONE, false, false);
}

opp_fusion::FusionSample sample(std::uint32_t t_us, std::uint8_t logical = 2U,
                               float ax_g = 0.0F) {
    opp_fusion::FusionSample input;
    input.t_us = t_us;
    input.raw_mask = static_cast<std::uint8_t>(logical ^ config::OPP_ACTIVE_LOW_MASK);
    input.prior_state = core::State::TRACK;
    input.ax_g = ax_g;
    input.imu_ok = true;
    return input;
}

void prepareCentered(opp_fusion::Fusion& fusion, bool contact = false) {
    CHECK(config::OPP_SET_TICKS == 2U);
    CHECK(fusion.observe(sample(0U)).fresh);
    CHECK(fusion.commit(core::State::TRACK).valid);
    CHECK(fusion.observe(sample(1000U, 2U, contact ? 2.0F : 0.0F)).bearing.centered);
    const auto committed = fusion.commit(contact ? core::State::ATTACK : core::State::TRACK);
    CHECK(committed.valid);
    checkResult(committed.result, contact ? IMPACT : NONE, contact, contact);
}
} // namespace

TEST_CASE("B5.4 D056 Contact const previews match every state and front eligibility row") {
    for (const auto state : STATES) {
        for (unsigned mask = 0U; mask < 128U; ++mask) {
            for (const bool latched : {false, true}) {
                opp_fusion::Contact contact;
                if (latched) CHECK(contact.commitLatch(core::State::ATTACK, 2U, IMPACT).contact);
                const auto& readonly = contact;
                const unsigned front = mask & 7U;
                const bool centered = front == 2U || front == 3U || front == 5U ||
                                      front == 6U || front == 7U;
                const bool eligible = state == core::State::ATTACK && centered;
                const auto bits = static_cast<std::uint8_t>(mask);
                for (unsigned repeat = 0U; repeat < 2U; ++repeat) {
                    checkResult(readonly.previewLatch(state, bits, IMPACT), IMPACT,
                                eligible, eligible && !latched);
                }
                checkResult(contact.commitLatch(state, bits, IMPACT), IMPACT,
                            eligible, eligible && !latched);
            }
        }
    }
}

TEST_CASE("B5.4 D056 Contact preview cannot create a latch or clear a committed latch") {
    opp_fusion::Contact contact;
    checkResult(contact.previewLatch(core::State::ATTACK, 2U, IMPACT), IMPACT, true, true);
    checkResult(contact.commitLatch(core::State::ATTACK, 2U, NONE), NONE, false, false);
    checkResult(contact.commitLatch(core::State::ATTACK, 2U, IMPACT), IMPACT, true, true);
    for (const auto state : STATES) {
        for (const std::uint8_t mask : {0U, 1U, 2U, 4U, 8U, 64U}) {
            const bool eligible = state == core::State::ATTACK && mask == 2U;
            checkResult(contact.previewLatch(state, mask, NONE), NONE, eligible, false);
        }
    }
    checkResult(contact.commitLatch(core::State::ATTACK, 2U, NONE), NONE, true, false);
    checkResult(contact.commitLatch(core::State::REFLANK, 2U, IMPACT), IMPACT, false, false);
    checkResult(contact.previewLatch(core::State::ATTACK, 2U, NONE), NONE, false, false);
}

TEST_CASE("B5.4 D056 Contact repeated previews do not advance either visual cue counter") {
    for (const std::uint8_t mask : {5U, 7U}) {
        opp_fusion::Contact contact;
        for (std::uint32_t count = 1U; count <= config::CONTACT_TICKS + 1U; ++count) {
            const bool ready = count >= config::CONTACT_TICKS;
            const auto cue = contact.observeCue(mask, 0.0F, 0.0F, false);
            CHECK(cue.close_cue == ready);
            CHECK_FALSE(cue.impact_cue);
            CHECK(cue.cue == ready);
            for (unsigned repeat = 0U; repeat < 25U; ++repeat) {
                checkResult(contact.previewLatch(core::State::ATTACK, mask, cue),
                            cue, ready, ready);
                checkResult(contact.previewLatch(core::State::REFLANK, mask, cue),
                            cue, false, false);
            }
            checkResult(contact.commitLatch(core::State::TRACK, mask, cue), cue, false, false);
        }
    }
}

TEST_CASE("B5.4 D056 Alternative previews do not merge the two consecutive close patterns") {
    for (const std::uint8_t first : {5U, 7U}) {
        opp_fusion::Contact contact;
        for (std::uint32_t n = 1U; n < config::CONTACT_TICKS; ++n) {
            CHECK_FALSE(contact.observeCue(first, 0.0F, 0.0F, false).cue);
        }
        const auto second = static_cast<std::uint8_t>(first == 5U ? 7U : 5U);
        for (std::uint32_t n = 1U; n <= config::CONTACT_TICKS; ++n) {
            const auto cue = contact.observeCue(second, 0.0F, 0.0F, false);
            const bool ready = n == config::CONTACT_TICKS;
            CHECK(cue.close_cue == ready);
            checkResult(contact.previewLatch(core::State::ATTACK, first, cue), cue, ready, ready);
            checkResult(contact.previewLatch(core::State::REFLANK, second, cue), cue, false, false);
        }
    }
}

TEST_CASE("B5.4 D056 Preview preserves strict finite current impact cues without retaining them") {
    const float nan = std::numeric_limits<float>::quiet_NaN();
    const float inf = std::numeric_limits<float>::infinity();
    const float above = std::nextafter(config::IMPACT_G, inf);
    for (const float ax : {0.0F, config::IMPACT_G, above, 2.0F, nan, inf}) {
        for (const bool imu_ok : {false, true}) {
            opp_fusion::Contact contact;
            const bool ready = imu_ok && std::isfinite(ax) && ax > config::IMPACT_G;
            const auto cue = contact.observeCue(2U, ax, 0.0F, imu_ok);
            CHECK_FALSE(cue.close_cue);
            CHECK(cue.impact_cue == ready);
            CHECK(cue.cue == ready);
            checkResult(contact.previewLatch(core::State::ATTACK, 2U, cue), cue, ready, ready);
            const auto clear = contact.observeCue(2U, 0.0F, 0.0F, true);
            checkResult(contact.commitLatch(core::State::ATTACK, 2U, clear), NONE, false, false);
        }
    }
}

TEST_CASE("B5.4 D056 Contact reset clears latch and previewed visual history") {
    for (const std::uint8_t mask : {5U, 7U}) {
        opp_fusion::Contact contact;
        CHECK(contact.commitLatch(core::State::ATTACK, 2U, IMPACT).contact);
        for (std::uint32_t n = 0U; n < config::CONTACT_TICKS; ++n) {
            const auto cue = contact.observeCue(mask, 0.0F, 0.0F, false);
            CHECK(contact.previewLatch(core::State::ATTACK, mask, cue).contact);
        }
        contact.reset();
        checkResult(contact.previewLatch(core::State::ATTACK, 2U, NONE), NONE, false, false);
        const auto first = contact.observeCue(mask, 0.0F, 0.0F, false);
        checkResult(contact.commitLatch(core::State::ATTACK, mask, first), NONE, false, false);
    }
}

TEST_CASE("B5.4 D056 Fusion const preview without an observation is invalid zero") {
    opp_fusion::Fusion fusion;
    const auto& readonly = fusion;
    for (const auto state : STATES) checkInvalid(readonly.preview(state));
    CHECK_FALSE(fusion.memory().valid);
    CHECK(fusion.observe(sample(0U)).fresh);
    const auto pending = readonly.preview(core::State::ATTACK);
    CHECK(pending.valid);
    checkResult(pending.result, NONE, false, false);
    CHECK(fusion.commit(core::State::ATTACK).valid);
}

TEST_CASE("B5.4 D056 Fusion pending impact supports repeated alternative previews and one commit") {
    opp_fusion::Fusion fusion;
    prepareCentered(fusion);
    CHECK(fusion.observe(sample(2000U, 2U, 2.0F)).cue.impact_cue);
    const auto seen_us = fusion.memory().last_seen_us;
    const auto& readonly = fusion;
    for (unsigned repeat = 0U; repeat < 3U; ++repeat) {
        for (const auto state : STATES) {
            const auto candidate = readonly.preview(state);
            CHECK(candidate.valid);
            const bool attack = state == core::State::ATTACK;
            checkResult(candidate.result, IMPACT, attack, attack);
        }
    }
    CHECK(fusion.memory().last_seen_us == seen_us);
    const auto committed = fusion.commit(core::State::ATTACK);
    CHECK(committed.valid);
    checkResult(committed.result, IMPACT, true, true);
    checkInvalid(readonly.preview(core::State::ATTACK));
}

TEST_CASE("B5.4 D056 Fusion final ineligible state clears prior or provisional contact") {
    for (const auto final_state : STATES) {
        if (final_state == core::State::ATTACK) continue;
        for (const bool previous_contact : {false, true}) {
            opp_fusion::Fusion fusion;
            prepareCentered(fusion, previous_contact);
            CHECK(fusion.observe(sample(2000U, 2U, 2.0F)).fresh);
            const auto candidate = fusion.preview(core::State::ATTACK);
            CHECK(candidate.valid);
            checkResult(candidate.result, IMPACT, true, !previous_contact);
            const auto committed = fusion.commit(final_state);
            CHECK(committed.valid);
            checkResult(committed.result, IMPACT, false, false);
            checkInvalid(fusion.preview(core::State::ATTACK));
            CHECK(fusion.observe(sample(3000U)).fresh);
            const auto next = fusion.commit(core::State::ATTACK);
            CHECK(next.valid);
            checkResult(next.result, NONE, false, false);
        }
    }
}

TEST_CASE("B5.4 D056 Consumed Fusion previews preserve real contact but invalid commit clears it") {
    opp_fusion::Fusion fusion;
    prepareCentered(fusion, true);
    for (const auto state : STATES) checkInvalid(fusion.preview(state));
    CHECK(fusion.observe(sample(2000U)).fresh);
    const auto pending = fusion.preview(core::State::ATTACK);
    CHECK(pending.valid);
    checkResult(pending.result, NONE, true, false);
    const auto kept = fusion.commit(core::State::ATTACK);
    CHECK(kept.valid);
    checkResult(kept.result, NONE, true, false);
    checkInvalid(fusion.commit(core::State::ATTACK));
    CHECK(fusion.observe(sample(3000U)).fresh);
    const auto cleared = fusion.commit(core::State::ATTACK);
    CHECK(cleared.valid);
    checkResult(cleared.result, NONE, false, false);
}

TEST_CASE("B5.4 D056 Cached Fusion observation neither changes nor consumes a pending candidate") {
    for (const bool impact : {false, true}) {
        opp_fusion::Fusion fusion;
        prepareCentered(fusion);
        const auto input = sample(2000U, 2U, impact ? 2.0F : 0.0F);
        CHECK(fusion.observe(input).fresh);
        for (unsigned repeat = 0U; repeat < 5U; ++repeat) {
            auto changed = sample(2000U, 64U, impact ? 0.0F : 2.0F);
            changed.edge_event = true;
            changed.heading_deg = 120.0F;
            const auto cached = fusion.observe(changed);
            CHECK_FALSE(cached.fresh);
            CHECK(cached.confirmed_mask == 2U);
            CHECK(cached.phantom.filtered_mask == 2U);
            CHECK_FALSE(cached.phantom.phantom_set);
            const auto preview = fusion.preview(core::State::ATTACK);
            CHECK(preview.valid);
            checkResult(preview.result, impact ? IMPACT : NONE, impact, impact);
        }
        const auto committed = fusion.commit(core::State::ATTACK);
        CHECK(committed.valid);
        checkResult(committed.result, impact ? IMPACT : NONE, impact, impact);
        CHECK_FALSE(fusion.observe(input).fresh);
        checkInvalid(fusion.preview(core::State::ATTACK));
        CHECK(fusion.observe(sample(3000U)).fresh);
        const auto next = fusion.commit(core::State::ATTACK);
        CHECK(next.valid);
        checkResult(next.result, NONE, impact, false);
    }
}

TEST_CASE("B5.1 B5.4 D056 Fusion previews and cached ticks cannot accelerate visual contact") {
    for (const std::uint8_t mask : {5U, 7U}) {
        for (const std::uint32_t origin : {0U, 0xFFFFF000U}) {
            opp_fusion::Fusion fusion;
            for (std::uint32_t n = 0U; n <= config::CONTACT_TICKS; ++n) {
                const auto input = sample(origin + n * config::TICK_US, mask);
                const auto observed = fusion.observe(input);
                CHECK(observed.fresh);
                const bool ready = n == config::CONTACT_TICKS;
                CHECK(observed.cue.close_cue == ready);
                CHECK_FALSE(observed.cue.impact_cue);
                for (unsigned repeat = 0U; repeat < 3U; ++repeat) {
                    CHECK_FALSE(fusion.observe(input).fresh);
                    const auto preview = fusion.preview(core::State::ATTACK);
                    CHECK(preview.valid);
                    checkResult(preview.result, observed.cue, ready, ready);
                    const auto alternative = fusion.preview(core::State::REFLANK);
                    CHECK(alternative.valid);
                    checkResult(alternative.result, observed.cue, false, false);
                }
                const auto committed = fusion.commit(core::State::ATTACK);
                CHECK(committed.valid);
                checkResult(committed.result, observed.cue, ready, ready);
            }
        }
    }
}

TEST_CASE("B5.4 D056 A skipped Fusion commit clears old contact despite a valid preview") {
    for (const bool previous_contact : {false, true}) {
        opp_fusion::Fusion fusion;
        prepareCentered(fusion, previous_contact);
        CHECK(fusion.observe(sample(2000U, 2U, previous_contact ? 0.0F : 2.0F)).fresh);
        const auto pending = fusion.preview(core::State::ATTACK);
        CHECK(pending.valid);
        CHECK(pending.result.contact);
        CHECK(pending.result.contact_started == !previous_contact);
        CHECK(fusion.observe(sample(3000U)).fresh);
        const auto replacement = fusion.preview(core::State::ATTACK);
        CHECK(replacement.valid);
        checkResult(replacement.result, NONE, false, false);
        const auto committed = fusion.commit(core::State::ATTACK);
        CHECK(committed.valid);
        checkResult(committed.result, NONE, false, false);
    }
}

TEST_CASE("B5.4 D056 Skipped Fusion commitment does not discard fresh visual cue samples") {
    for (const std::uint8_t mask : {5U, 7U}) {
        opp_fusion::Fusion fusion;
        for (std::uint32_t n = 0U; n < config::CONTACT_TICKS; ++n) {
            CHECK(fusion.observe(sample(n * config::TICK_US, mask)).fresh);
            const auto candidate = fusion.preview(core::State::ATTACK);
            CHECK(candidate.valid);
            checkResult(candidate.result, NONE, false, false);
            if (n + 1U < config::CONTACT_TICKS) CHECK(fusion.commit(core::State::TRACK).valid);
        }
        const auto final = fusion.observe(sample(config::CONTACT_TICKS * config::TICK_US, mask));
        CHECK(final.cue.close_cue);
        const auto preview = fusion.preview(core::State::ATTACK);
        CHECK(preview.valid);
        checkResult(preview.result, final.cue, true, true);
        const auto committed = fusion.commit(core::State::ATTACK);
        CHECK(committed.valid);
        checkResult(committed.result, final.cue, true, true);
    }
}

TEST_CASE("B5.4 D056 Fusion reset discards pending preview latch debounce and cue history") {
    for (const std::uint8_t mask : {5U, 7U}) {
        opp_fusion::Fusion fusion;
        for (std::uint32_t n = 0U; n <= config::CONTACT_TICKS; ++n) {
            CHECK(fusion.observe(sample(n * config::TICK_US, mask)).fresh);
            CHECK(fusion.commit(core::State::ATTACK).valid);
        }
        const auto next_us = (config::CONTACT_TICKS + 1U) * config::TICK_US;
        CHECK(fusion.observe(sample(next_us, mask)).fresh);
        const auto before = fusion.preview(core::State::ATTACK);
        CHECK(before.valid);
        CHECK(before.result.contact);
        CHECK_FALSE(before.result.contact_started);
        fusion.reset();
        checkInvalid(fusion.preview(core::State::ATTACK));
        CHECK_FALSE(fusion.memory().valid);
        const auto fresh = fusion.observe(sample(next_us, mask));
        CHECK(fresh.fresh);
        CHECK(fresh.confirmed_mask == 0U);
        CHECK(fusion.commit(core::State::ATTACK).valid);
        const auto second = fusion.observe(sample(next_us + config::TICK_US, mask));
        CHECK(second.confirmed_mask == mask);
        CHECK_FALSE(second.cue.close_cue);
        const auto after = fusion.preview(core::State::ATTACK);
        CHECK(after.valid);
        checkResult(after.result, NONE, false, false);
    }
}

TEST_CASE("B5.4 B5.5 D056 Fusion preview uses effective target after phantom filtering") {
    opp_fusion::Fusion fusion;
    prepareCentered(fusion);
    auto edge = sample(2000U);
    edge.edge_event = true;
    const auto marked = fusion.observe(edge);
    CHECK(marked.phantom.phantom_set);
    CHECK(marked.phantom.filtered_mask == 0U);
    CHECK(fusion.commit(core::State::TRACK).valid);
    const auto impact = fusion.observe(sample(3000U, 2U, 2.0F));
    CHECK(impact.confirmed_mask == 2U);
    CHECK(impact.cue.impact_cue);
    CHECK(impact.phantom.filtered_mask == 0U);
    const auto preview = fusion.preview(core::State::ATTACK);
    CHECK(preview.valid);
    checkResult(preview.result, IMPACT, false, false);
    const auto committed = fusion.commit(core::State::ATTACK);
    CHECK(committed.valid);
    checkResult(committed.result, IMPACT, false, false);
}
