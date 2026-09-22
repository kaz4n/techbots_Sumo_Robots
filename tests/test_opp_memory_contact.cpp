// Checks B5 bearing memory and contact lifetime under approved D-026/D-027.
// Keeps sensor interpretation and current governor eligibility independently testable.
// Spec-only doctest cases cover all masks, exact observations, faults and symmetry.
#include "doctest.h"
#include "config.h"
#include "core/governor.h"
#include "core/opp_fusion.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();
constexpr float FRONT_BEARINGS[8] = {0.0F, -15.0F, 0.0F, -6.0F, 15.0F, 0.0F, 6.0F, 0.0F};
constexpr bool FRONT_CENTERED[8] = {false, false, true, true, false, true, true, true};

struct ExpectedBearing {
    opp_fusion::Group group = opp_fusion::Group::NONE;
    bool detected = false;
    bool valid = false;
    bool centered = false;
    bool close = false;
    bool conflict = false;
    float relative = 0.0F;
};

ExpectedBearing expectedMask(unsigned mask, bool history) {
    ExpectedBearing expected;
    const unsigned front = mask & 7U;
    const unsigned side = mask & 24U;
    const unsigned rear = mask & 96U;
    if (front != 0U) {
        expected.group = opp_fusion::Group::FRONT;
        expected.detected = expected.valid = true;
        expected.centered = FRONT_CENTERED[front];
        expected.close = front == 5U || front == 7U;
        expected.relative = FRONT_BEARINGS[front];
    } else if (side != 0U || rear != 0U) {
        const bool use_side = side != 0U;
        expected.group = use_side ? opp_fusion::Group::SIDE : opp_fusion::Group::REAR;
        expected.detected = true;
        expected.conflict = use_side ? side == 24U : rear == 96U;
        expected.valid = !expected.conflict || history;
        if (expected.conflict) expected.relative = history ? 15.0F : 0.0F;
        else if (use_side) expected.relative = side == 8U ? -90.0F : 90.0F;
        else expected.relative = rear == 32U ? -135.0F : 135.0F;
    }
    return expected;
}

void checkBearing(const opp_fusion::BearingView& actual, const ExpectedBearing& expected) {
    CHECK(actual.group == expected.group);
    CHECK(actual.detected == expected.detected);
    CHECK(actual.bearing_valid == expected.valid);
    CHECK(actual.world_valid == expected.valid);
    CHECK(actual.centered == expected.centered);
    CHECK(actual.close == expected.close);
    CHECK(actual.conflict == expected.conflict);
    CHECK(actual.relative_deg == expected.relative);
    CHECK(actual.world_deg == (expected.valid ? expected.relative + 30.0F : 0.0F));
}

void checkNoContact(const opp_fusion::ContactResult& result) {
    CHECK_FALSE(result.contact);
    CHECK_FALSE(result.contact_started);
}

void checkMemorySame(const opp_fusion::Memory& actual, const opp_fusion::Memory& expected) {
    CHECK(actual.valid == expected.valid);
    CHECK(actual.world_valid == expected.world_valid);
    CHECK(actual.last_rel_bearing_deg == expected.last_rel_bearing_deg);
    CHECK(actual.last_world_bearing_deg == expected.last_world_bearing_deg);
    CHECK(actual.last_seen_us == expected.last_seen_us);
    CHECK(actual.last_front_side == expected.last_front_side);
    CHECK(actual.left_seen == expected.left_seen);
    CHECK(actual.right_seen == expected.right_seen);
    CHECK(actual.left_seen_us == expected.left_seen_us);
    CHECK(actual.right_seen_us == expected.right_seen_us);
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    constexpr unsigned reflected_bit[7] = {2U, 1U, 0U, 4U, 3U, 6U, 5U};
    std::uint8_t mirrored = 0U;
    for (unsigned bit = 0U; bit < 7U; ++bit) {
        if ((mask & (1U << bit)) != 0U) mirrored |= static_cast<std::uint8_t>(1U << reflected_bit[bit]);
    }
    return mirrored;
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}

governor::Request attackRequest(const opp_fusion::ContactResult& contact,
                                std::uint8_t mask, float voltage) {
    governor::Request request;
    request.duty_l = 1.0F;
    request.duty_r = 1.0F;
    request.vbat_v = voltage;
    request.profile = governor::Profile::ATTACK;
    request.centered = opp_fusion::frontView(mask).centered;
    request.contact = contact.contact;
    request.inhibited = false;
    return request;
}
} // namespace

TEST_CASE("B5 memory and contact defaults invent no target side cue or contact") {
    opp_fusion::BearingMemory fusion;
    const opp_fusion::Memory empty;
    checkMemorySame(fusion.memory(), empty);
    CHECK_FALSE(empty.valid);
    CHECK_FALSE(empty.world_valid);
    CHECK(empty.last_front_side == opp_fusion::FrontSide::UNKNOWN);
    const auto view = fusion.step(0U, 0U, 0.0F);
    CHECK(view.group == opp_fusion::Group::NONE);
    CHECK_FALSE(view.detected); CHECK_FALSE(view.bearing_valid); CHECK_FALSE(view.world_valid);
    CHECK_FALSE(view.centered); CHECK_FALSE(view.close); CHECK_FALSE(view.conflict);
    CHECK(view.relative_deg == 0.0F); CHECK(view.world_deg == 0.0F);
    const opp_fusion::ContactResult contact;
    CHECK_FALSE(contact.close_cue); CHECK_FALSE(contact.impact_cue); CHECK_FALSE(contact.cue);
    checkNoContact(contact);
}

TEST_CASE("B5.2 all128 masks obey table group priority and no history conflict semantics") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        for (unsigned high_bit : {0U, 128U}) {
            CAPTURE(mask);
            CAPTURE(high_bit);
            opp_fusion::BearingMemory fusion;
            const auto expected = expectedMask(mask, false);
            const auto view = fusion.step(1234U, static_cast<std::uint8_t>(mask | high_bit), 30.0F);
            checkBearing(view, expected);
            CHECK(fusion.memory().valid == expected.valid);
            CHECK(fusion.memory().world_valid == expected.valid);
            CHECK(fusion.memory().last_seen_us == (expected.valid ? 1234U : 0U));
            CHECK(fusion.memory().last_rel_bearing_deg == expected.relative);
        }
    }
}

TEST_CASE("B5.2 all128 masks reuse previous relative bearing only for selected group conflicts") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mask);
        opp_fusion::BearingMemory fusion;
        fusion.step(10U, 4U, 15.0F);
        const auto expected = expectedMask(mask, true);
        const auto view = fusion.step(20U, static_cast<std::uint8_t>(mask), 30.0F);
        checkBearing(view, expected);
        CHECK(fusion.memory().valid);
        CHECK(fusion.memory().last_seen_us == (mask == 0U ? 10U : 20U));
        if (mask == 0U) {
            CHECK(fusion.memory().last_rel_bearing_deg == 15.0F);
            CHECK(fusion.memory().last_world_bearing_deg == 30.0F);
        } else {
            CHECK(fusion.memory().last_rel_bearing_deg == expected.relative);
            CHECK(fusion.memory().last_world_bearing_deg == expected.relative + 30.0F);
        }
    }
}

TEST_CASE("B5.2 bilateral side and rear conflicts retain history across repeated conflicts") {
    for (std::uint8_t first_group : {24U, 96U}) {
        opp_fusion::BearingMemory fusion;
        auto view = fusion.step(100U, first_group, 10.0F);
        CHECK(view.detected); CHECK(view.conflict); CHECK_FALSE(view.bearing_valid);
        CHECK_FALSE(fusion.memory().valid);
        fusion.step(200U, 8U, 10.0F);
        view = fusion.step(300U, first_group, 20.0F);
        CHECK(view.conflict); CHECK(view.bearing_valid); CHECK(view.world_valid);
        CHECK(view.relative_deg == -90.0F); CHECK(view.world_deg == -70.0F);
        view = fusion.step(400U, 120U, 30.0F);
        CHECK(view.group == opp_fusion::Group::SIDE);
        CHECK(view.conflict); CHECK(view.relative_deg == -90.0F);
        CHECK(view.world_deg == -60.0F); CHECK(fusion.memory().last_seen_us == 400U);
    }
}

TEST_CASE("B5.3 front recency timestamps update only on newly lit left or right bits") {
    opp_fusion::BearingMemory fusion;
    fusion.step(100U, 1U, 0.0F);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::LEFT);
    CHECK(fusion.memory().left_seen); CHECK_FALSE(fusion.memory().right_seen);
    CHECK(fusion.memory().left_seen_us == 100U);
    fusion.step(200U, 3U, 0.0F);
    CHECK(fusion.memory().left_seen_us == 100U);
    CHECK(fusion.memory().last_seen_us == 200U);
    fusion.step(300U, 7U, 0.0F);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::RIGHT);
    CHECK(fusion.memory().right_seen_us == 300U);
    CHECK(fusion.memory().left_seen_us == 100U);
    fusion.step(400U, 5U, 0.0F);
    CHECK(fusion.memory().left_seen_us == 100U);
    CHECK(fusion.memory().right_seen_us == 300U);
    fusion.step(500U, 4U, 0.0F);
    fusion.step(600U, 5U, 0.0F);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::LEFT);
    CHECK(fusion.memory().left_seen_us == 600U);
    CHECK(fusion.memory().right_seen_us == 300U);
}

TEST_CASE("B5.3 simultaneous front rising ties keep unknown or previously remembered side") {
    for (std::uint8_t history : {0U, 1U, 4U}) {
        opp_fusion::BearingMemory fusion;
        fusion.step(0U, history, 0.0F);
        fusion.step(100U, 0U, 0.0F);
        fusion.step(200U, 5U, 0.0F);
        const auto expected = history == 1U ? opp_fusion::FrontSide::LEFT :
            history == 4U ? opp_fusion::FrontSide::RIGHT : opp_fusion::FrontSide::UNKNOWN;
        CHECK(fusion.memory().last_front_side == expected);
        CHECK(fusion.memory().left_seen); CHECK(fusion.memory().right_seen);
        CHECK(fusion.memory().left_seen_us == 200U);
        CHECK(fusion.memory().right_seen_us == 200U);
        fusion.step(300U, 7U, 0.0F);
        CHECK(fusion.memory().last_front_side == expected);
        CHECK(fusion.memory().left_seen_us == 200U);
        CHECK(fusion.memory().right_seen_us == 200U);
    }
}

TEST_CASE("B0 B5.3 front recency follows rising events across timestamp zero and wrap") {
    opp_fusion::BearingMemory fusion;
    fusion.step(0xFFFFFFF0U, 1U, 0.0F);
    fusion.step(0U, 5U, 0.0F);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::RIGHT);
    CHECK(fusion.memory().left_seen_us == 0xFFFFFFF0U);
    CHECK(fusion.memory().right_seen_us == 0U);
    CHECK(fusion.memory().right_seen);
    CHECK(fusion.memory().last_seen_us == 0U);
    fusion.step(100U, 5U, 0.0F);
    CHECK(fusion.memory().right_seen_us == 0U);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::RIGHT);
    fusion.step(200U, 0U, 0.0F);
    fusion.step(300U, 5U, 0.0F);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::RIGHT);
    CHECK(fusion.memory().left_seen_us == 300U);
    CHECK(fusion.memory().right_seen_us == 300U);
}

TEST_CASE("B5.3 no detection returns empty current view and retains unexpired or old memory") {
    opp_fusion::BearingMemory fusion;
    fusion.step(0xFFFF0000U, 3U, 50.0F);
    const auto remembered = fusion.memory();
    for (std::uint32_t now : {0xFFFF0001U, 0U, 3000000U, 10000000U}) {
        const auto view = fusion.step(now, 0x80U, NAN_VALUE);
        CHECK(view.group == opp_fusion::Group::NONE);
        CHECK_FALSE(view.detected); CHECK_FALSE(view.bearing_valid); CHECK_FALSE(view.world_valid);
        CHECK_FALSE(view.centered); CHECK_FALSE(view.close); CHECK_FALSE(view.conflict);
        CHECK(view.relative_deg == 0.0F); CHECK(view.world_deg == 0.0F);
        checkMemorySame(fusion.memory(), remembered);
    }
}

TEST_CASE("B0 B5.3 world bearings wrap to minus180 exclusive plus180 inclusive") {
    const float headings[] = {170.0F, -170.0F, 165.0F, -165.0F, 1080.0F, -1080.0F};
    const std::uint8_t masks[] = {4U, 1U, 4U, 1U, 8U, 16U};
    const float expected[] = {-175.0F, 175.0F, 180.0F, 180.0F, -90.0F, 90.0F};
    for (unsigned index = 0U; index < 6U; ++index) {
        opp_fusion::BearingMemory fusion;
        const auto view = fusion.step(100U, masks[index], headings[index]);
        CHECK(view.world_valid);
        CHECK(view.world_deg == expected[index]);
        CHECK(fusion.memory().last_world_bearing_deg == expected[index]);
    }
}

TEST_CASE("B5.3 finite heading extremes yield bounded finite world angles") {
    for (float heading : {std::numeric_limits<float>::max(), -std::numeric_limits<float>::max(),
                          3600000.0F, -3600000.0F, std::numeric_limits<float>::denorm_min()}) {
        for (std::uint8_t mask : {1U, 2U, 4U, 8U, 16U, 32U, 64U}) {
            opp_fusion::BearingMemory fusion;
            const auto view = fusion.step(100U, mask, heading);
            CHECK(view.bearing_valid); CHECK(view.world_valid);
            CHECK(std::isfinite(view.relative_deg)); CHECK(std::isfinite(view.world_deg));
            CHECK(view.world_deg > -180.0F); CHECK(view.world_deg <= 180.0F);
            CHECK(fusion.memory().world_valid);
            CHECK(std::isfinite(fusion.memory().last_world_bearing_deg));
        }
    }
}

TEST_CASE("B5.3 each nonfinite heading preserves relative bearing and invalidates world memory") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        opp_fusion::BearingMemory fusion;
        fusion.step(100U, 4U, 45.0F);
        const auto view = fusion.step(200U, 1U, invalid);
        CHECK(view.detected); CHECK(view.bearing_valid); CHECK_FALSE(view.world_valid);
        CHECK(view.relative_deg == -15.0F); CHECK(view.world_deg == 0.0F);
        CHECK(fusion.memory().valid); CHECK_FALSE(fusion.memory().world_valid);
        CHECK(fusion.memory().last_rel_bearing_deg == -15.0F);
        CHECK(fusion.memory().last_world_bearing_deg == 0.0F);
        CHECK(fusion.memory().last_seen_us == 200U);
        const auto recovered = fusion.step(300U, 24U, 30.0F);
        CHECK(recovered.bearing_valid); CHECK(recovered.world_valid); CHECK(recovered.conflict);
        CHECK(recovered.relative_deg == -15.0F); CHECK(recovered.world_deg == 15.0F);
    }
}

TEST_CASE("B5.3 reset clears direction timestamps and conflict reuse history") {
    opp_fusion::BearingMemory fusion;
    fusion.step(100U, 1U, 10.0F);
    fusion.step(200U, 4U, 20.0F);
    fusion.reset();
    checkMemorySame(fusion.memory(), opp_fusion::Memory{});
    const auto conflicted = fusion.step(300U, 96U, 0.0F);
    CHECK(conflicted.detected); CHECK(conflicted.conflict); CHECK_FALSE(conflicted.bearing_valid);
    CHECK_FALSE(fusion.memory().valid);
    fusion.step(400U, 4U, 0.0F);
    CHECK(fusion.memory().last_front_side == opp_fusion::FrontSide::RIGHT);
    CHECK(fusion.memory().right_seen_us == 400U);
}

TEST_CASE("B5.4 visual close cues first qualify at observation20 for111 and101 separately") {
    CHECK(config::CONTACT_TICKS == 20U);
    for (std::uint8_t mask : {5U, 7U}) {
        opp_fusion::Contact contact;
        for (unsigned count = 1U; count <= 21U; ++count) {
            CAPTURE(count);
            const auto result = contact.step(core::State::ATTACK, mask, 0.0F, 0.0F, false);
            CHECK(result.close_cue == (count >= 20U));
            CHECK_FALSE(result.impact_cue);
            CHECK(result.cue == (count >= 20U));
            CHECK(result.contact == (count >= 20U));
            CHECK(result.contact_started == (count == 20U));
        }
    }
}

TEST_CASE("B5.4 visual patterns cannot share or accumulate nonconsecutive counts") {
    for (std::uint8_t first : {5U, 7U}) {
        const std::uint8_t second = first == 5U ? 7U : 5U;
        opp_fusion::Contact contact;
        for (unsigned count = 0U; count < 19U; ++count) {
            CHECK_FALSE(contact.step(core::State::ATTACK, first, 0.0F, 0.0F, false).close_cue);
        }
        for (unsigned count = 1U; count <= 20U; ++count) {
            const auto result = contact.step(core::State::ATTACK, second, 0.0F, 0.0F, false);
            CHECK(result.close_cue == (count == 20U));
            CHECK(result.contact_started == (count == 20U));
        }
        CHECK_FALSE(contact.step(core::State::ATTACK, first, 0.0F, 0.0F, false).close_cue);
        contact.reset();
        for (unsigned count = 0U; count < 100U; ++count) {
            const auto mask = count % 2U == 0U ? first : second;
            const auto result = contact.step(core::State::ATTACK, mask, 0.0F, 0.0F, false);
            CHECK_FALSE(result.close_cue); checkNoContact(result);
        }
    }
}

TEST_CASE("B5.4 every128 mask qualifies visual contact only for exact front111 or101") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        opp_fusion::Contact contact;
        const auto with_high_bit = static_cast<std::uint8_t>(mask | 128U);
        for (unsigned count = 1U; count <= 20U; ++count) {
            const auto result = contact.step(core::State::ATTACK, with_high_bit, 0.0F, 0.0F, false);
            const bool close = ((mask & 7U) == 5U || (mask & 7U) == 7U) && count >= 20U;
            CHECK(result.close_cue == close);
            CHECK(result.cue == close);
            CHECK(result.contact == close);
            CHECK(result.contact_started == close);
        }
    }
}

TEST_CASE("B5.4 exact impact threshold is strict with both axis signs and adjacent floats") {
    CHECK(config::IMPACT_G == 1.5F);
    for (float magnitude : {std::nextafter(1.5F, 0.0F), 1.5F, std::nextafter(1.5F, INF_VALUE)}) {
        for (float sign : {-1.0F, 1.0F}) {
            for (bool use_y : {false, true}) {
                opp_fusion::Contact contact;
                const float x = use_y ? 0.0F : magnitude * sign;
                const float y = use_y ? magnitude * sign : 0.0F;
                const auto result = contact.step(core::State::ATTACK, 2U, x, y, true);
                const bool above = magnitude > 1.5F;
                CHECK(result.impact_cue == above); CHECK(result.cue == above);
                CHECK_FALSE(result.close_cue);
                CHECK(result.contact == above); CHECK(result.contact_started == above);
            }
        }
    }
}

TEST_CASE("B5.4 horizontal Euclidean norm handles345 diagonals not axis maximum or sum") {
    const float x_values[] = {.75F, 1.5F, .9375F, 1.0F, 1.125F};
    const float y_values[] = {1.0F, 2.0F, 1.25F, 1.0F, 1.125F};
    const bool above[] = {false, true, true, false, true};
    for (unsigned index = 0U; index < 5U; ++index) {
        for (float sign_x : {-1.0F, 1.0F}) {
            for (float sign_y : {-1.0F, 1.0F}) {
                opp_fusion::Contact contact;
                const auto result = contact.step(core::State::ATTACK, 2U,
                    x_values[index] * sign_x, y_values[index] * sign_y, true);
                CHECK(result.impact_cue == above[index]);
                CHECK(result.contact == above[index]);
                CHECK(result.contact_started == above[index]);
            }
        }
    }
}

TEST_CASE("B5.4 any changed front pattern restarts consecutive close qualification") {
    for (std::uint8_t close_mask : {5U, 7U}) {
        for (unsigned interruption = 0U; interruption < 8U; ++interruption) {
            if (interruption == close_mask) continue;
            opp_fusion::Contact contact;
            for (unsigned count = 0U; count < 19U; ++count) {
                contact.step(core::State::ATTACK, close_mask, 0.0F, 0.0F, false);
            }
            checkNoContact(contact.step(core::State::ATTACK,
                static_cast<std::uint8_t>(interruption), 0.0F, 0.0F, false));
            for (unsigned count = 1U; count <= 20U; ++count) {
                const auto result = contact.step(core::State::ATTACK, close_mask, 0.0F, 0.0F, false);
                CHECK(result.close_cue == (count == 20U));
                CHECK(result.contact == (count == 20U));
                CHECK(result.contact_started == (count == 20U));
            }
        }
    }
}

TEST_CASE("B5.4 finite acceleration extremes stay valid while tiny accelerations give no impact") {
    const float huge = std::numeric_limits<float>::max();
    for (float sign_x : {-1.0F, 1.0F}) {
        for (float sign_y : {-1.0F, 1.0F}) {
            opp_fusion::Contact contact;
            const auto result = contact.step(core::State::ATTACK, 2U, sign_x * huge, sign_y * huge, true);
            CHECK(result.impact_cue); CHECK(result.contact); CHECK(result.contact_started);
        }
    }
    opp_fusion::Contact tiny;
    const float subnormal = std::numeric_limits<float>::denorm_min();
    const auto result = tiny.step(core::State::ATTACK, 2U, subnormal, -subnormal, true);
    CHECK_FALSE(result.impact_cue); CHECK_FALSE(result.cue); checkNoContact(result);
}

TEST_CASE("B5.4 unavailable IMU and every nonfinite axis cannot supply an impact cue") {
    for (float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        for (bool invalid_y : {false, true}) {
            for (bool healthy : {false, true}) {
                opp_fusion::Contact contact;
                const float x = invalid_y ? 2.0F : invalid;
                const float y = invalid_y ? invalid : 2.0F;
                const auto result = contact.step(core::State::ATTACK, 2U, x, y, healthy);
                CHECK_FALSE(result.impact_cue); CHECK_FALSE(result.cue); checkNoContact(result);
            }
        }
    }
    opp_fusion::Contact unavailable;
    const auto result = unavailable.step(core::State::ATTACK, 2U, 100.0F, -100.0F, false);
    CHECK_FALSE(result.impact_cue); CHECK_FALSE(result.cue); checkNoContact(result);
}

TEST_CASE("B5.4 invalid IMU never suppresses independently qualified visual close cues") {
    for (std::uint8_t mask : {5U, 7U}) {
        for (bool healthy : {false, true}) {
            opp_fusion::Contact contact;
            for (unsigned count = 1U; count <= 20U; ++count) {
                const auto result = contact.step(core::State::ATTACK, mask, NAN_VALUE, INF_VALUE, healthy);
                CHECK_FALSE(result.impact_cue);
                CHECK(result.close_cue == (count == 20U));
                CHECK(result.contact == (count == 20U));
            }
        }
    }
}

TEST_CASE("B5.4 D027 cues stay visible in all states but only ATTACK can latch") {
    for (unsigned code = 0U; code <= 255U; ++code) {
        const auto state = static_cast<core::State>(code);
        const bool eligible = state == core::State::ATTACK;
        opp_fusion::Contact impact;
        const auto result = impact.step(state, 2U, 2.0F, 0.0F, true);
        CHECK(result.impact_cue); CHECK(result.cue);
        CHECK(result.contact == eligible); CHECK(result.contact_started == eligible);
        opp_fusion::Contact visual;
        for (unsigned count = 1U; count <= 20U; ++count) {
            const auto seen = visual.step(state, 7U, 0.0F, 0.0F, false);
            CHECK(seen.close_cue == (count == 20U));
            CHECK(seen.contact == (eligible && count == 20U));
            CHECK(seen.contact_started == (eligible && count == 20U));
        }
    }
}

TEST_CASE("B5.4 D027 every128 mask needs current front centering to latch an impact") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        opp_fusion::Contact contact;
        const auto result = contact.step(core::State::ATTACK, static_cast<std::uint8_t>(mask), 2.0F, 0.0F, true);
        CHECK(result.impact_cue); CHECK(result.cue);
        CHECK(result.contact == FRONT_CENTERED[mask & 7U]);
        CHECK(result.contact_started == FRONT_CENTERED[mask & 7U]);
    }
}

TEST_CASE("B5.4 D027 centered ATTACK retains contact after cue disappears with one rising event") {
    opp_fusion::Contact contact;
    const auto initial = contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true);
    CHECK(initial.contact); CHECK(initial.contact_started);
    for (std::uint8_t centered : {2U, 3U, 5U, 6U, 7U}) {
        const auto result = contact.step(core::State::ATTACK, centered, 0.0F, 0.0F, false);
        CHECK_FALSE(result.close_cue); CHECK_FALSE(result.impact_cue); CHECK_FALSE(result.cue);
        CHECK(result.contact); CHECK_FALSE(result.contact_started);
    }
    const auto another_impact = contact.step(core::State::ATTACK, 2U, 3.0F, 4.0F, true);
    CHECK(another_impact.impact_cue); CHECK(another_impact.contact);
    CHECK_FALSE(another_impact.contact_started);
}

TEST_CASE("B5.4 D027 target loss or either offcenter front clears old contact immediately") {
    for (std::uint8_t lost : {0U, 1U, 4U, 8U, 16U, 32U, 64U, 120U}) {
        opp_fusion::Contact contact;
        CHECK(contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true).contact_started);
        const auto result = contact.step(core::State::ATTACK, lost, 2.0F, 0.0F, true);
        CHECK(result.impact_cue);
        checkNoContact(result);
        const auto new_target = contact.step(core::State::ATTACK, 2U, 0.0F, 0.0F, false);
        checkNoContact(new_target);
        const auto fresh = contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true);
        CHECK(fresh.contact); CHECK(fresh.contact_started);
    }
}

TEST_CASE("B5.4 D027 all state exits clear latch and reentry requires a qualified current cue") {
    for (unsigned code = 0U; code <= 255U; ++code) {
        const auto state = static_cast<core::State>(code);
        if (state == core::State::ATTACK) continue;
        opp_fusion::Contact contact;
        CHECK(contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true).contact_started);
        const auto exited = contact.step(state, 2U, 2.0F, 0.0F, true);
        CHECK(exited.impact_cue); checkNoContact(exited);
        checkNoContact(contact.step(core::State::ATTACK, 2U, 0.0F, 0.0F, false));
        const auto renewed = contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true);
        CHECK(renewed.contact); CHECK(renewed.contact_started);
    }
}

TEST_CASE("B5.4 D027 a qualified current visual cue may establish fresh contact after reflank") {
    opp_fusion::Contact contact;
    CHECK(contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true).contact_started);
    for (unsigned count = 1U; count <= 20U; ++count) {
        const auto result = contact.step(core::State::REFLANK, 7U, 0.0F, 0.0F, false);
        CHECK(result.close_cue == (count == 20U));
        checkNoContact(result);
    }
    const auto renewed = contact.step(core::State::ATTACK, 7U, 0.0F, 0.0F, false);
    CHECK(renewed.close_cue); CHECK(renewed.contact); CHECK(renewed.contact_started);
    CHECK_FALSE(contact.step(core::State::ATTACK, 7U, 0.0F, 0.0F, false).contact_started);
}

TEST_CASE("B5.4 contact reset clears both visual counters and latched event state") {
    for (std::uint8_t mask : {5U, 7U}) {
        opp_fusion::Contact contact;
        for (unsigned count = 0U; count < 25U; ++count) {
            contact.step(core::State::ATTACK, mask, 0.0F, 0.0F, false);
        }
        contact.reset();
        for (unsigned count = 1U; count <= 20U; ++count) {
            const auto result = contact.step(core::State::ATTACK, mask, 0.0F, 0.0F, false);
            CHECK(result.close_cue == (count == 20U));
            CHECK(result.contact == (count == 20U));
            CHECK(result.contact_started == (count == 20U));
        }
        contact.reset();
        checkNoContact(contact.step(core::State::ATTACK, 2U, 0.0F, 0.0F, false));
    }
}

TEST_CASE("B5.4 B6 D027 governor full duty eligibility uses current centered contact at low voltage") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        opp_fusion::Contact contact;
        governor::Governor governor;
        auto cue = contact.step(core::State::ATTACK, 2U, 0.0F, 0.0F, false);
        governor.step(0U, attackRequest(cue, 2U, voltage));
        auto duty = governor.step(100000U, attackRequest(cue, 2U, voltage));
        CHECK(duty.duty_l == doctest::Approx(.6F)); CHECK(duty.duty_r == doctest::Approx(.6F));
        cue = contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true);
        duty = governor.step(200000U, attackRequest(cue, 2U, voltage));
        const float full = voltage <= 11.1F ? 1.0F : 11.1F / voltage;
        CHECK(cue.contact_started); CHECK(duty.duty_l == doctest::Approx(full));
        CHECK(duty.duty_r == doctest::Approx(full));
        cue = contact.step(core::State::ATTACK, 1U, 0.0F, 0.0F, false);
        duty = governor.step(201000U, attackRequest(cue, 1U, voltage));
        CHECK_FALSE(cue.contact);
        CHECK(duty.duty_l == doctest::Approx(.6F)); CHECK(duty.duty_r == doctest::Approx(.6F));
        cue = contact.step(core::State::ATTACK, 2U, 0.0F, 0.0F, false);
        duty = governor.step(300000U, attackRequest(cue, 2U, voltage));
        CHECK(duty.duty_l == doctest::Approx(.6F)); CHECK(duty.duty_r == doctest::Approx(.6F));
        cue = contact.step(core::State::ATTACK, 2U, 2.0F, 0.0F, true);
        duty = governor.step(400000U, attackRequest(cue, 2U, voltage));
        CHECK(cue.contact_started); CHECK(duty.duty_l == doctest::Approx(full));
        cue = contact.step(core::State::REFLANK, 2U, 2.0F, 0.0F, true);
        duty = governor.step(401000U, attackRequest(cue, 2U, voltage));
        CHECK_FALSE(cue.contact);
        CHECK(duty.duty_l == doctest::Approx(.6F)); CHECK(duty.duty_r == doctest::Approx(.6F));
    }
}

TEST_CASE("B0 B5 ten thousand seeded memory and contact observations preserve mirror symmetry") {
    std::uint32_t seed = 0xB5262701U;
    unsigned history_cases = 0U;
    unsigned no_history_cases = 0U;
    for (unsigned sample = 0U; sample < 10000U; ++sample) {
        const std::uint32_t now = nextRandom(seed);
        const auto mask = static_cast<std::uint8_t>((nextRandom(seed) >> 16U) & 127U);
        const float heading = static_cast<float>(nextRandom(seed) % 2001U) - 1000.0F + .25F;
        opp_fusion::BearingMemory right, left;
        if ((sample & 1U) != 0U) {
            right.step(now - 1000U, 4U, 0.0F); left.step(now - 1000U, 1U, 0.0F);
            ++history_cases;
        } else ++no_history_cases;
        const auto r = right.step(now, mask, heading);
        const auto l = left.step(now, mirrorMask(mask), -heading);
        CHECK(r.group == l.group); CHECK(r.detected == l.detected);
        CHECK(r.bearing_valid == l.bearing_valid); CHECK(r.world_valid == l.world_valid);
        CHECK(r.centered == l.centered); CHECK(r.close == l.close); CHECK(r.conflict == l.conflict);
        CHECK(r.relative_deg == doctest::Approx(-l.relative_deg));
        CHECK(r.world_deg == doctest::Approx(-l.world_deg));
        CHECK(std::isfinite(r.world_deg)); CHECK(std::isfinite(l.world_deg));
        if (r.world_valid) { CHECK(r.world_deg > -180.0F); CHECK(r.world_deg <= 180.0F); }
        opp_fusion::Contact right_contact, left_contact;
        const float ax = static_cast<float>(nextRandom(seed) % 401U) / 100.0F - 2.0F;
        const float ay = static_cast<float>(nextRandom(seed) % 401U) / 100.0F - 2.0F;
        const bool healthy = (sample & 1U) != 0U;
        const auto state = sample % 3U == 0U ? core::State::ATTACK : core::State::REFLANK;
        const auto rc = right_contact.step(state, mask, ax, ay, healthy);
        const auto lc = left_contact.step(state, mirrorMask(mask), ax, -ay, healthy);
        CHECK(rc.close_cue == lc.close_cue); CHECK(rc.impact_cue == lc.impact_cue);
        CHECK(rc.cue == lc.cue); CHECK(rc.contact == lc.contact);
        CHECK(rc.contact_started == lc.contact_started);
    }
    CHECK(history_cases == 5000U); CHECK(no_history_cases == 5000U);
}
