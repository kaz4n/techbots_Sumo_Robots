// Checks B9 centered-observation qualification and D-034/D-038 reacquisition pieces.
// Separates a fresh-observation counter from contact, state routing and motor permission.
// Independent host tests cover literal tables, streaks and Fusion/governor composition.
#include "doctest.h"
#include "config.h"
#include "core/fsm.h"
#include "core/opp_fusion.h"
#include "core/governor.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::array<bool, 8> CENTERED{{false, false, true, true, false, true, true, true}};
constexpr std::array<std::uint8_t, 5> CENTERED_ROWS{{2U, 3U, 5U, 6U, 7U}};

void checkQualification(const fsm::FrontQualificationResult& result,
                        bool front, bool centered, bool eligible) {
    CHECK(result.front_detected == front);
    CHECK(result.centered == centered);
    CHECK(result.attack_eligible == eligible);
}

struct CommittedFront {
    opp_fusion::ContactCommit contact;
    fsm::FrontDemand demand;
    governor::Result duty;
};

// Test-owned component wiring, with explicit caller-selected states and permission.
// No target-loss routing, normal-entry tick convention or Robot/MotorGate is modeled.
class FrontPipeline {
public:
    opp_fusion::FusionObservation observe(std::uint32_t time, std::uint8_t logical,
            core::State prior, float ax = 0.0F, bool edge = false,
            float heading = 0.0F, bool imu = true) {
        opp_fusion::FusionSample sample;
        sample.t_us = time;
        sample.raw_mask = static_cast<std::uint8_t>(logical ^ 0x78U);
        sample.prior_state = prior;
        sample.heading_deg = heading;
        sample.ax_g = ax;
        sample.imu_ok = imu;
        sample.edge_event = edge;
        observed = fusion.observe(sample);
        time_us = time;
        if (observed.fresh) qualified = qualification.observe(observed.phantom.filtered_mask);
        return observed;
    }

    CommittedFront commit(core::State selected, float voltage = 9.0F,
                          bool permission = true) {
        CHECK(observed.fresh);
        CommittedFront result;
        result.contact = fusion.commit(selected);
        const bool contact = result.contact.valid && result.contact.result.contact;
        result.demand = fsm::frontDemand(selected, observed.phantom.filtered_mask, contact);
        governor::Request request;
        request.duty_l = result.demand.duty_l;
        request.duty_r = result.demand.duty_r;
        request.profile = result.demand.profile;
        request.centered = qualified.centered;
        request.contact = contact;
        request.vbat_v = voltage;
        request.inhibited = !permission || !result.contact.valid || !result.demand.valid;
        result.duty = governor.step(time_us, request);
        return result;
    }

    opp_fusion::Fusion fusion;
    fsm::FrontQualification qualification;
    governor::Governor governor;
    opp_fusion::FusionObservation observed;
    fsm::FrontQualificationResult qualified;
    std::uint32_t time_us = 0U;
};

void checkNoContact(const CommittedFront& result) {
    CHECK(result.contact.valid);
    CHECK_FALSE(result.contact.result.contact);
    CHECK_FALSE(result.contact.result.contact_started);
}

void checkDutyBound(const governor::Result& result, float limit) {
    CHECK(result.valid);
    CHECK(std::isfinite(result.duty_l));
    CHECK(std::isfinite(result.duty_r));
    CHECK(std::abs(result.duty_l) <= limit);
    CHECK(std::abs(result.duty_r) <= limit);
}

void prepareQualifiedContact(FrontPipeline& pipeline) {
    for (std::uint32_t tick = 0U; tick <= 3U; ++tick) {
        pipeline.observe(tick * 1000U, 2U, core::State::TRACK,
                         tick == 3U ? 2.0F : 0.0F);
        const auto result = pipeline.commit(tick == 3U ? core::State::ATTACK : core::State::TRACK);
        if (tick < 3U) checkNoContact(result);
        else {
            CHECK(pipeline.qualified.attack_eligible);
            CHECK(result.contact.result.contact);
            CHECK(result.contact.result.contact_started);
        }
    }
}
} // namespace

TEST_CASE("B9.1 centered qualification uses the literal three-observation default") {
    CHECK(config::ATTACK_ENTER_TICKS == 3U);
    fsm::FrontQualification qualification;
    checkQualification(qualification.observe(2U), true, true, false);
    checkQualification(qualification.observe(2U), true, true, false);
    checkQualification(qualification.observe(2U), true, true, true);
    checkQualification(qualification.observe(2U), true, true, true);
}

TEST_CASE("B5.2 B9.1 all 256 masks follow the literal front and centered table") {
    unsigned centered_masks = 0U;
    unsigned front_masks = 0U;
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        CAPTURE(mask);
        fsm::FrontQualification qualification;
        const unsigned front = mask & 7U;
        const bool centered = CENTERED[front];
        centered_masks += centered ? 1U : 0U;
        front_masks += front != 0U ? 1U : 0U;
        for (unsigned observation = 1U; observation <= 4U; ++observation) {
            const auto result = qualification.observe(static_cast<std::uint8_t>(mask));
            checkQualification(result, front != 0U, centered, centered && observation >= 3U);
        }
    }
    CHECK(centered_masks == 160U);
    CHECK(front_masks == 224U);
}

TEST_CASE("B5.2 B9.1 every centered triple qualifies even when its front pattern changes") {
    unsigned sequences = 0U;
    for (const auto first : CENTERED_ROWS) {
        for (const auto second : CENTERED_ROWS) {
            for (const auto third : CENTERED_ROWS) {
                fsm::FrontQualification qualification;
                checkQualification(qualification.observe(first), true, true, false);
                checkQualification(qualification.observe(second), true, true, false);
                checkQualification(qualification.observe(third), true, true, true);
                ++sequences;
            }
        }
    }
    CHECK(sequences == 125U);
}

TEST_CASE("B2 B5 front priority ignores changing side rear and unused high bits") {
    for (const auto front : CENTERED_ROWS) {
        fsm::FrontQualification qualification;
        checkQualification(qualification.observe(front), true, true, false);
        checkQualification(qualification.observe(static_cast<std::uint8_t>(front | 0xF8U)),
                           true, true, false);
        checkQualification(qualification.observe(static_cast<std::uint8_t>(front | 0x68U)),
                           true, true, true);
    }
    for (const auto front : std::initializer_list<std::uint8_t>{1U, 4U}) {
        fsm::FrontQualification qualification;
        for (unsigned sample = 0U; sample < 4U; ++sample) {
            checkQualification(qualification.observe(static_cast<std::uint8_t>(front | 0xF8U)),
                               true, false, false);
        }
    }
}

TEST_CASE("B9.1 every absent or off-center mask interrupts a two-observation streak") {
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        fsm::FrontQualification qualification;
        CHECK_FALSE(qualification.observe(2U).attack_eligible);
        CHECK_FALSE(qualification.observe(2U).attack_eligible);
        const bool centered = CENTERED[mask & 7U];
        checkQualification(qualification.observe(static_cast<std::uint8_t>(mask)),
                           (mask & 7U) != 0U, centered, centered);
        checkQualification(qualification.observe(2U), true, true, centered);
        checkQualification(qualification.observe(2U), true, true, centered);
        checkQualification(qualification.observe(2U), true, true, true);
    }
}

TEST_CASE("B9.1 a qualified streak clears immediately for every noncentered front view") {
    unsigned interruptions = 0U;
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        if (CENTERED[mask & 7U]) continue;
        fsm::FrontQualification qualification;
        for (unsigned i = 0U; i < 3U; ++i) qualification.observe(7U);
        checkQualification(qualification.observe(static_cast<std::uint8_t>(mask)),
                           (mask & 7U) != 0U, false, false);
        checkQualification(qualification.observe(5U), true, true, false);
        checkQualification(qualification.observe(6U), true, true, false);
        checkQualification(qualification.observe(3U), true, true, true);
        ++interruptions;
    }
    CHECK(interruptions == 96U);
}

TEST_CASE("B9.1 reset starts fresh qualification from any prior streak length") {
    for (const unsigned length : {0U, 1U, 2U, 3U, 4U}) {
        fsm::FrontQualification qualification;
        for (unsigned i = 0U; i < length; ++i) qualification.observe(2U);
        qualification.reset();
        qualification.reset();
        checkQualification(qualification.observe(2U), true, true, false);
        checkQualification(qualification.observe(2U), true, true, false);
        checkQualification(qualification.observe(2U), true, true, true);
    }
}

TEST_CASE("B9.1 saturated eligibility stays true through a bounded long centered streak") {
    fsm::FrontQualification qualification;
    for (unsigned i = 0U; i < 4096U; ++i) {
        const auto result = qualification.observe(CENTERED_ROWS[i % CENTERED_ROWS.size()]);
        checkQualification(result, true, true, i >= 2U);
    }
    checkQualification(qualification.observe(0U), false, false, false);
    checkQualification(qualification.observe(2U), true, true, false);
}

TEST_CASE("B5 B9 Fusion debounce precedes three new centered observations and approach caps") {
    CHECK(config::OPP_SET_TICKS == 2U);
    CHECK(config::OPP_ACTIVE_LOW_MASK == 0x78U);
    FrontPipeline pipeline;
    for (std::uint32_t tick = 0U; tick <= 3U; ++tick) {
        const auto observed = pipeline.observe(tick * 1000U, 2U, core::State::TRACK);
        CHECK(observed.fresh);
        CHECK(observed.confirmed_mask == (tick == 0U ? 0U : 2U));
        CHECK(pipeline.qualified.attack_eligible == (tick == 3U));
        const auto result = pipeline.commit(tick == 3U ? core::State::ATTACK : core::State::TRACK);
        checkNoContact(result);
        if (tick > 0U) {
            CHECK(result.demand.valid);
            CHECK(result.demand.profile == (tick == 3U ? governor::Profile::ATTACK :
                                                                      governor::Profile::SEARCH_FORWARD));
            checkDutyBound(result.duty, tick == 3U ? 0.6F : 0.3F);
        }
    }
    pipeline.observe(40000U, 2U, core::State::ATTACK);
    const auto result = pipeline.commit(core::State::ATTACK);
    checkNoContact(result);
    CHECK(result.demand.duty_l == doctest::Approx(0.6F));
    CHECK(result.duty.duty_l == doctest::Approx(0.6F));
    CHECK(result.duty.duty_r == doctest::Approx(0.6F));
}

TEST_CASE("B5 B9 cached Fusion observations cannot advance a correctly guarded qualifier") {
    FrontPipeline pipeline;
    pipeline.observe(0U, 2U, core::State::TRACK);
    pipeline.commit(core::State::TRACK);
    pipeline.observe(1000U, 2U, core::State::TRACK);
    checkQualification(pipeline.qualified, true, true, false);
    pipeline.commit(core::State::TRACK);
    for (unsigned repeat = 0U; repeat < 20U; ++repeat) {
        const auto duplicate = pipeline.observe(1000U, 7U, core::State::ATTACK, 2.0F);
        CHECK_FALSE(duplicate.fresh);
        CHECK(duplicate.phantom.filtered_mask == 2U);
        CHECK_FALSE(duplicate.cue.cue);
        checkQualification(pipeline.qualified, true, true, false);
    }
    pipeline.observe(2000U, 2U, core::State::TRACK);
    checkQualification(pipeline.qualified, true, true, false);
    checkNoContact(pipeline.commit(core::State::TRACK));
    pipeline.observe(3000U, 2U, core::State::TRACK);
    checkQualification(pipeline.qualified, true, true, true);
    checkNoContact(pipeline.commit(core::State::ATTACK));
}

TEST_CASE("B5 B9 observation qualification is independent of elapsed time across micros wrap") {
    FrontPipeline pipeline;
    const std::uint32_t start = std::numeric_limits<std::uint32_t>::max() - 1U;
    const std::array<std::uint32_t, 4> offsets{{0U, 1U, 2U, 1000000U}};
    for (unsigned i = 0U; i < offsets.size(); ++i) {
        CHECK(pipeline.observe(start + offsets[i], 2U, core::State::TRACK).fresh);
        CHECK(pipeline.qualified.attack_eligible == (i == 3U));
        const auto result = pipeline.commit(i == 3U ? core::State::ATTACK : core::State::TRACK);
        checkNoContact(result);
        checkDutyBound(result.duty, i == 3U ? 0.6F : 0.3F);
    }
}

TEST_CASE("B5.4 B9 a fresh impact can latch on the qualified ATTACK commitment") {
    FrontPipeline pipeline;
    prepareQualifiedContact(pipeline);
    CHECK(pipeline.observed.cue.impact_cue);
    pipeline.observe(53000U, 2U, core::State::ATTACK);
    CHECK_FALSE(pipeline.observed.cue.cue);
    const auto result = pipeline.commit(core::State::ATTACK);
    CHECK(result.contact.valid);
    CHECK(result.contact.result.contact);
    CHECK_FALSE(result.contact.result.contact_started);
    CHECK(result.demand.duty_l == doctest::Approx(1.0F));
    CHECK(result.demand.duty_r == doctest::Approx(1.0F));
    CHECK(result.duty.duty_l == doctest::Approx(1.0F));
    CHECK(result.duty.duty_r == doctest::Approx(1.0F));
}

TEST_CASE("B5.4 B9 a cue before eligibility does not become stale ATTACK contact") {
    FrontPipeline pipeline;
    for (std::uint32_t tick = 0U; tick <= 3U; ++tick) {
        pipeline.observe(tick * 1000U, 2U, core::State::TRACK, tick == 1U ? 2.0F : 0.0F);
        if (tick == 1U) CHECK(pipeline.observed.cue.impact_cue);
        const auto result = pipeline.commit(tick == 3U ? core::State::ATTACK : core::State::TRACK);
        checkNoContact(result);
        checkDutyBound(result.duty, tick == 3U ? 0.6F : 0.3F);
    }
    CHECK(pipeline.qualified.attack_eligible);
    pipeline.observe(4000U, 2U, core::State::ATTACK, 2.0F);
    const auto result = pipeline.commit(core::State::ATTACK);
    CHECK(result.contact.result.contact);
    CHECK(result.contact.result.contact_started);
}

TEST_CASE("B5.4 B9 visual contact still requires twenty confirmed samples after qualification") {
    CHECK(config::CONTACT_TICKS == 20U);
    for (const auto pattern : std::initializer_list<std::uint8_t>{5U, 7U}) {
        for (const float voltage : {9.0F, 11.1F}) {
            FrontPipeline pipeline;
            for (std::uint32_t tick = 0U; tick <= 20U; ++tick) {
                pipeline.observe(tick * 1000U, pattern,
                                 tick > 3U ? core::State::ATTACK : core::State::TRACK);
                CHECK(pipeline.qualified.attack_eligible == (tick >= 3U));
                CHECK(pipeline.observed.cue.close_cue == (tick == 20U));
                const auto result = pipeline.commit(tick >= 3U ? core::State::ATTACK :
                                                                               core::State::TRACK, voltage);
                CHECK(result.contact.valid);
                CHECK(result.contact.result.contact == (tick == 20U));
                CHECK(result.contact.result.contact_started == (tick == 20U));
                checkDutyBound(result.duty, tick >= 20U ? 1.0F : tick >= 3U ? 0.6F : 0.3F);
            }
            pipeline.observe(70000U, pattern, core::State::ATTACK);
            const auto result = pipeline.commit(core::State::ATTACK, voltage);
            CHECK(result.contact.result.contact);
            CHECK_FALSE(result.contact.result.contact_started);
            CHECK(result.duty.duty_l == doctest::Approx(1.0F));
            CHECK(result.duty.duty_r == doctest::Approx(1.0F));
        }
    }
}

TEST_CASE("D-034 D-038 caller reset on preemption requires new qualification and fresh contact") {
    for (const auto exit : {core::State::OPENER, core::State::REFLANK, core::State::EDGE_ESCAPE}) {
        FrontPipeline pipeline;
        prepareQualifiedContact(pipeline);
        pipeline.observe(4000U, 2U, core::State::ATTACK);
        const auto leaving = pipeline.commit(exit);
        checkNoContact(leaving);
        CHECK_FALSE(leaving.demand.valid);
        CHECK(leaving.duty.duty_l == 0.0F);
        CHECK(leaving.duty.duty_r == 0.0F);
        pipeline.qualification.reset();
        for (std::uint32_t tick = 5U; tick <= 7U; ++tick) {
            pipeline.observe(tick * 1000U, 2U, tick == 5U ? exit : core::State::TRACK);
            checkQualification(pipeline.qualified, true, true, tick == 7U);
            const auto result = pipeline.commit(tick == 7U ? core::State::ATTACK : core::State::TRACK);
            checkNoContact(result);
            checkDutyBound(result.duty, tick == 7U ? 0.6F : 0.3F);
        }
        pipeline.observe(8000U, 2U, core::State::ATTACK, 2.0F);
        const auto result = pipeline.commit(core::State::ATTACK);
        CHECK(result.contact.result.contact);
        CHECK(result.contact.result.contact_started);
    }
}

TEST_CASE("B5.5 B9 phantom filtered observations reset qualification before close reacquisition") {
    FrontPipeline pipeline;
    for (std::uint32_t tick = 0U; tick < 3U; ++tick) {
        pipeline.observe(tick * 1000U, 2U, core::State::TRACK);
        CHECK_FALSE(pipeline.qualified.attack_eligible);
        pipeline.commit(core::State::TRACK);
    }
    pipeline.observe(3000U, 2U, core::State::TRACK, 0.0F, true);
    CHECK(pipeline.observed.confirmed_mask == 2U);
    CHECK(pipeline.observed.phantom.phantom_set);
    CHECK(pipeline.observed.phantom.filtered_mask == 0U);
    checkQualification(pipeline.qualified, false, false, false);
    checkNoContact(pipeline.commit(core::State::EDGE_ESCAPE));
    pipeline.qualification.reset();
    pipeline.observe(4000U, 2U, core::State::EDGE_ESCAPE);
    checkQualification(pipeline.qualified, false, false, false);
    CHECK_FALSE(pipeline.commit(core::State::TRACK).demand.valid);
    for (std::uint32_t tick = 5U; tick <= 8U; ++tick) {
        pipeline.observe(tick * 1000U, 7U, core::State::TRACK);
        CHECK(pipeline.qualified.attack_eligible == (tick == 8U));
        if (tick >= 6U) CHECK(pipeline.observed.phantom.filtered_mask == 7U);
        CHECK_FALSE(pipeline.observed.cue.close_cue);
        checkNoContact(pipeline.commit(tick == 8U ? core::State::ATTACK : core::State::TRACK));
    }
}

TEST_CASE("B5.6 B9 a newly stuck front bit cannot supply the third qualifying observation") {
    CHECK(config::OPP_STUCK_MS == 5000U);
    FrontPipeline pipeline;
    pipeline.observe(0U, 2U, core::State::TRACK);
    pipeline.commit(core::State::TRACK);
    pipeline.observe(1000U, 2U, core::State::TRACK);
    checkQualification(pipeline.qualified, true, true, false);
    pipeline.commit(core::State::TRACK);
    pipeline.observe(2000U, 2U, core::State::TRACK, 0.0F, false, 100.0F);
    checkQualification(pipeline.qualified, true, true, false);
    pipeline.commit(core::State::TRACK);
    pipeline.observe(5001000U, 2U, core::State::TRACK, 0.0F, false, 361.0F);
    CHECK(pipeline.observed.confirmed_mask == 2U);
    CHECK(pipeline.observed.stuck.new_fault_mask == 2U);
    CHECK(pipeline.observed.phantom.filtered_mask == 0U);
    checkQualification(pipeline.qualified, false, false, false);
    const auto result = pipeline.commit(core::State::TRACK);
    checkNoContact(result);
    CHECK_FALSE(result.demand.valid);
    CHECK(result.duty.duty_l == 0.0F);
    CHECK(result.duty.duty_r == 0.0F);
}

TEST_CASE("B5 B9 confirmed off-center observation clears qualification and contact together") {
    FrontPipeline pipeline;
    prepareQualifiedContact(pipeline);
    pipeline.observe(4000U, 1U, core::State::ATTACK);
    CHECK(pipeline.observed.phantom.filtered_mask == 2U);
    CHECK(pipeline.commit(core::State::ATTACK).contact.result.contact);
    pipeline.observe(5000U, 1U, core::State::ATTACK);
    CHECK(pipeline.observed.phantom.filtered_mask == 3U);
    CHECK(pipeline.commit(core::State::ATTACK).contact.result.contact);
    pipeline.observe(33999U, 1U, core::State::ATTACK);
    CHECK(pipeline.qualified.attack_eligible);
    pipeline.commit(core::State::ATTACK);
    pipeline.observe(34000U, 1U, core::State::ATTACK);
    CHECK(pipeline.observed.phantom.filtered_mask == 1U);
    checkQualification(pipeline.qualified, true, false, false);
    const auto result = pipeline.commit(core::State::TRACK);
    checkNoContact(result);
    CHECK(result.demand.valid);
    CHECK(result.demand.profile == governor::Profile::SEARCH_FORWARD);
    checkDutyBound(result.duty, 0.3F);
}

TEST_CASE("B6 B9 contact and attack eligibility cannot override externally closed permission") {
    FrontPipeline pipeline;
    prepareQualifiedContact(pipeline);
    pipeline.observe(53000U, 2U, core::State::ATTACK);
    CHECK(pipeline.commit(core::State::ATTACK).duty.duty_l == doctest::Approx(1.0F));
    pipeline.observe(54000U, 2U, core::State::ATTACK);
    CHECK(pipeline.qualified.attack_eligible);
    const auto result = pipeline.commit(core::State::ATTACK, 9.0F, false);
    CHECK(result.contact.result.contact);
    CHECK(result.demand.valid);
    CHECK(result.demand.duty_l == doctest::Approx(1.0F));
    CHECK(result.duty.duty_l == 0.0F);
    CHECK(result.duty.duty_r == 0.0F);
}
