// Tests B9 front steering against literal B5/B16/D-036 specification examples.
// Keeps request math and governor composition distinct from future Robot arbitration.
// Independent host cases exhaust masks, mirror directions, invalid states and caps.
#include "doctest.h"
#include "core/fsm.h"
#include "core/governor.h"
#include <cmath>
#include <cstdint>

namespace {
struct DutyPair { float left; float right; };
struct FrontRow {
    bool centered;
    DutyPair track;
    DutyPair approach;
    DutyPair contact;
};

// Index is the logical B0 mask FL15=1, FC=2, FR15=4. These are literal
// B5 bearing-table examples evaluated using the approved B16 defaults.
constexpr FrontRow FRONT_ROWS[] = {
    {false, {0.00F, 0.00F}, {0.00F, 0.00F}, {0.00F, 0.00F}},
    {false, {-0.10F, 1.00F}, {0.00F, 0.00F}, {0.00F, 0.00F}},
    {true, {0.45F, 0.45F}, {0.60F, 0.60F}, {1.00F, 1.00F}},
    {true, {0.33F, 0.57F}, {0.48F, 0.72F}, {0.88F, 1.00F}},
    {false, {1.00F, -0.10F}, {0.00F, 0.00F}, {0.00F, 0.00F}},
    {true, {0.45F, 0.45F}, {0.60F, 0.60F}, {1.00F, 1.00F}},
    {true, {0.57F, 0.33F}, {0.72F, 0.48F}, {1.00F, 0.88F}},
    {true, {0.45F, 0.45F}, {0.60F, 0.60F}, {1.00F, 1.00F}},
};
constexpr bool CONTACT_LEVELS[] = {false, true};
constexpr core::State FRONT_STATES[] = {core::State::TRACK, core::State::ATTACK};

void checkPair(float left, float right, DutyPair expected) {
    CHECK(left == doctest::Approx(expected.left));
    CHECK(right == doctest::Approx(expected.right));
}

void checkZero(const fsm::FrontDemand& demand) {
    CHECK_FALSE(demand.valid);
    CHECK(demand.duty_l == 0.0F);
    CHECK(demand.duty_r == 0.0F);
}

void checkBounded(const fsm::FrontDemand& demand) {
    CHECK(std::isfinite(demand.duty_l));
    CHECK(std::isfinite(demand.duty_r));
    CHECK(demand.duty_l >= -1.0F);
    CHECK(demand.duty_l <= 1.0F);
    CHECK(demand.duty_r >= -1.0F);
    CHECK(demand.duty_r <= 1.0F);
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    return static_cast<std::uint8_t>((mask & 0x82U)
        | ((mask & 0x01U) << 2U) | ((mask & 0x04U) >> 2U)
        | ((mask & 0x08U) << 1U) | ((mask & 0x10U) >> 1U)
        | ((mask & 0x20U) << 1U) | ((mask & 0x40U) >> 1U));
}

governor::Request governedRequest(const fsm::FrontDemand& demand, float voltage,
                                  bool centered, bool contact) {
    governor::Request request;
    request.duty_l = demand.duty_l;
    request.duty_r = demand.duty_r;
    request.vbat_v = voltage;
    request.profile = demand.profile;
    request.centered = centered;
    request.contact = contact;
    request.inhibited = false;
    return request;
}

governor::Result settled(const governor::Request& request) {
    governor::Governor governor;
    auto result = governor.step(0U, request);
    // Sixty 1 ms observations exceed the B16 full-duty acceleration interval.
    for (std::uint32_t tick = 1U; tick <= 60U; ++tick)
        result = governor.step(tick * 1000U, request);
    return result;
}
} // namespace

TEST_CASE("B5.2 B9.1 D-036 all seven TRACK rows have literal steering duties") {
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        CAPTURE(mask);
        const auto demand = fsm::frontDemand(core::State::TRACK, mask, false);
        CHECK(demand.valid);
        CHECK(demand.profile == governor::Profile::SEARCH_FORWARD);
        checkPair(demand.duty_l, demand.duty_r, FRONT_ROWS[mask].track);
    }
}

TEST_CASE("B5.2 B9.2 D-036 five centered ATTACK approach rows have literal duties") {
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        if (!FRONT_ROWS[mask].centered) continue;
        CAPTURE(mask);
        const auto demand = fsm::frontDemand(core::State::ATTACK, mask, false);
        CHECK(demand.valid);
        CHECK(demand.profile == governor::Profile::ATTACK);
        checkPair(demand.duty_l, demand.duty_r, FRONT_ROWS[mask].approach);
    }
}

TEST_CASE("B5.2 B9.2 D-036 five centered contact rows clamp the outer request to one") {
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        if (!FRONT_ROWS[mask].centered) continue;
        CAPTURE(mask);
        const auto demand = fsm::frontDemand(core::State::ATTACK, mask, true);
        CHECK(demand.valid);
        CHECK(demand.profile == governor::Profile::ATTACK);
        checkPair(demand.duty_l, demand.duty_r, FRONT_ROWS[mask].contact);
    }
}

TEST_CASE("B5.4 B9.1 contact cannot promote TRACK requests or its governor profile") {
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        CAPTURE(mask);
        const auto demand = fsm::frontDemand(core::State::TRACK, mask, true);
        CHECK(demand.valid);
        CHECK(demand.profile == governor::Profile::SEARCH_FORWARD);
        checkPair(demand.duty_l, demand.duty_r, FRONT_ROWS[mask].track);
    }
}

TEST_CASE("B9.3 off-center ATTACK gives invalid zero even with contact") {
    constexpr std::uint8_t off_center[] = {0x01U, 0x04U};
    for (const auto mask : off_center) {
        for (const bool contact : CONTACT_LEVELS) {
            CAPTURE(mask);
            CAPTURE(contact);
            checkZero(fsm::frontDemand(core::State::ATTACK,
                                      static_cast<std::uint8_t>(mask), contact));
        }
    }
}

TEST_CASE("B5.2 B9.3 absent front gives zero for every side rear and high-bit combination") {
    for (unsigned mask = 0U; mask <= 255U; mask += 8U) {
        for (const auto state : FRONT_STATES) {
            for (const bool contact : CONTACT_LEVELS) {
                CAPTURE(mask);
                CAPTURE(state);
                CAPTURE(contact);
                checkZero(fsm::frontDemand(state, static_cast<std::uint8_t>(mask), contact));
            }
        }
    }
}

TEST_CASE("B1 B9 every unsupported and unknown state gives invalid zero") {
    for (unsigned state = 0U; state <= 255U; ++state) {
        const auto value = static_cast<core::State>(state);
        if (value == core::State::TRACK || value == core::State::ATTACK) continue;
        for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
            for (const bool contact : CONTACT_LEVELS) {
                CAPTURE(state);
                CAPTURE(mask);
                CAPTURE(contact);
                checkZero(fsm::frontDemand(value, mask, contact));
            }
        }
    }
}

TEST_CASE("B5.2 B9 all 256 masks use only the current front row in TRACK") {
    for (unsigned mask = 0U; mask <= 255U; ++mask) {
        const auto front = mask & 0x07U;
        for (const bool contact : CONTACT_LEVELS) {
            CAPTURE(mask);
            CAPTURE(contact);
            const auto demand = fsm::frontDemand(core::State::TRACK,
                                                 static_cast<std::uint8_t>(mask), contact);
            CHECK(demand.valid == (front != 0U));
            checkPair(demand.duty_l, demand.duty_r, FRONT_ROWS[front].track);
            if (demand.valid) CHECK(demand.profile == governor::Profile::SEARCH_FORWARD);
        }
    }
}

TEST_CASE("B5.2 B9 all 256 masks use current centering and contact in ATTACK") {
    for (unsigned mask = 0U; mask <= 255U; ++mask) {
        const auto& row = FRONT_ROWS[mask & 0x07U];
        for (const bool contact : CONTACT_LEVELS) {
            CAPTURE(mask);
            CAPTURE(contact);
            const auto demand = fsm::frontDemand(core::State::ATTACK,
                                                 static_cast<std::uint8_t>(mask), contact);
            CHECK(demand.valid == row.centered);
            checkPair(demand.duty_l, demand.duty_r, contact ? row.contact : row.approach);
            if (demand.valid) CHECK(demand.profile == governor::Profile::ATTACK);
        }
    }
}

TEST_CASE("B0 B9 exhaustive front steering mirrors exchange left and right duties") {
    for (unsigned mask = 0U; mask <= 255U; ++mask) {
        for (const auto state : FRONT_STATES) {
            for (const bool contact : CONTACT_LEVELS) {
                CAPTURE(mask);
                CAPTURE(state);
                CAPTURE(contact);
                const auto original = fsm::frontDemand(state,
                    static_cast<std::uint8_t>(mask), contact);
                const auto mirrored = fsm::frontDemand(state,
                    mirrorMask(static_cast<std::uint8_t>(mask)), contact);
                CHECK(mirrored.valid == original.valid);
                CHECK(mirrored.profile == original.profile);
                checkPair(mirrored.duty_l, mirrored.duty_r,
                          {original.duty_r, original.duty_l});
            }
        }
    }
}

TEST_CASE("B0 B9 every representable state mask and contact yields finite bounded requests") {
    for (unsigned state = 0U; state <= 255U; ++state) {
        for (unsigned mask = 0U; mask <= 255U; ++mask) {
            for (const bool contact : CONTACT_LEVELS) {
                CAPTURE(state);
                CAPTURE(mask);
                CAPTURE(contact);
                checkBounded(fsm::frontDemand(static_cast<core::State>(state),
                    static_cast<std::uint8_t>(mask), contact));
            }
        }
    }
}

TEST_CASE("B9.1 B9.3 requests follow each call without retaining a former contact demand") {
    const auto pushing = fsm::frontDemand(core::State::ATTACK, 0x02U, true);
    checkPair(pushing.duty_l, pushing.duty_r, {1.00F, 1.00F});
    checkZero(fsm::frontDemand(core::State::ATTACK, 0x00U, true));
    checkZero(fsm::frontDemand(core::State::ATTACK, 0x01U, true));
    const auto approach = fsm::frontDemand(core::State::ATTACK, 0x02U, false);
    CHECK(approach.valid);
    checkPair(approach.duty_l, approach.duty_r, {0.60F, 0.60F});
    const auto pending = fsm::frontDemand(core::State::TRACK, 0x02U, false);
    CHECK(pending.valid);
    checkPair(pending.duty_l, pending.duty_r, {0.45F, 0.45F});
}

TEST_CASE("B6 B9 TRACK composes with real SEARCH_FORWARD caps at nominal and low voltage") {
    constexpr DutyPair nominal[] = {{0, 0}, {-0.10F, 0.30F}, {0.30F, 0.30F},
        {0.30F, 0.30F}, {0.30F, -0.10F}, {0.30F, 0.30F},
        {0.30F, 0.30F}, {0.30F, 0.30F}};
    constexpr DutyPair low[] = {{0, 0}, {-0.123333333F, 0.30F}, {0.30F, 0.30F},
        {0.30F, 0.30F}, {0.30F, -0.123333333F}, {0.30F, 0.30F},
        {0.30F, 0.30F}, {0.30F, 0.30F}};
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        for (const bool contact : CONTACT_LEVELS) {
            CAPTURE(mask);
            CAPTURE(contact);
            const auto demand = fsm::frontDemand(core::State::TRACK, mask, contact);
            CHECK(demand.valid);
            const auto normal = settled(governedRequest(demand, 11.1F,
                FRONT_ROWS[mask].centered, contact));
            const auto tired = settled(governedRequest(demand, 9.0F,
                FRONT_ROWS[mask].centered, contact));
            CHECK(normal.valid);
            CHECK(tired.valid);
            checkPair(normal.duty_l, normal.duty_r, nominal[mask]);
            checkPair(tired.duty_l, tired.duty_r, low[mask]);
        }
    }
}

TEST_CASE("B6 B9 ATTACK approach composes with final 0.60 caps after voltage compensation") {
    constexpr DutyPair nominal[] = {{0, 0}, {0, 0}, {0.60F, 0.60F},
        {0.48F, 0.60F}, {0, 0}, {0.60F, 0.60F}, {0.60F, 0.48F}, {0.60F, 0.60F}};
    constexpr DutyPair low[] = {{0, 0}, {0, 0}, {0.60F, 0.60F},
        {0.592F, 0.60F}, {0, 0}, {0.60F, 0.60F}, {0.60F, 0.592F}, {0.60F, 0.60F}};
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        if (!FRONT_ROWS[mask].centered) continue;
        CAPTURE(mask);
        const auto demand = fsm::frontDemand(core::State::ATTACK, mask, false);
        CHECK(demand.valid);
        const auto normal = settled(governedRequest(demand, 11.1F, true, false));
        const auto tired = settled(governedRequest(demand, 9.0F, true, false));
        CHECK(normal.valid);
        CHECK(tired.valid);
        checkPair(normal.duty_l, normal.duty_r, nominal[mask]);
        checkPair(tired.duty_l, tired.duty_r, low[mask]);
    }
}

TEST_CASE("B6 B9 ATTACK contact composition retains nominal steering and bounds low voltage") {
    for (std::uint8_t mask = 1U; mask <= 7U; ++mask) {
        if (!FRONT_ROWS[mask].centered) continue;
        CAPTURE(mask);
        const auto demand = fsm::frontDemand(core::State::ATTACK, mask, true);
        CHECK(demand.valid);
        const auto normal = settled(governedRequest(demand, 11.1F, true, true));
        const auto tired = settled(governedRequest(demand, 9.0F, true, true));
        CHECK(normal.valid);
        CHECK(tired.valid);
        checkPair(normal.duty_l, normal.duty_r, FRONT_ROWS[mask].contact);
        checkPair(tired.duty_l, tired.duty_r, {1.00F, 1.00F});
    }
}

TEST_CASE("B6 B9 the real governor permits full duty only with centered contact") {
    const auto demand = fsm::frontDemand(core::State::ATTACK, 0x02U, true);
    CHECK(demand.valid);
    for (const bool centered : CONTACT_LEVELS) {
        for (const bool contact : CONTACT_LEVELS) {
            CAPTURE(centered);
            CAPTURE(contact);
            const auto result = settled(governedRequest(demand, 9.0F, centered, contact));
            CHECK(result.valid);
            const DutyPair expected = centered && contact
                ? DutyPair{1.00F, 1.00F} : DutyPair{0.60F, 0.60F};
            checkPair(result.duty_l, result.duty_r, expected);
        }
    }
}

TEST_CASE("B6 B9 contact acceleration slews and contact-cap loss is immediate") {
    governor::Governor governor;
    const auto approach = fsm::frontDemand(core::State::ATTACK, 0x02U, false);
    auto request = governedRequest(approach, 9.0F, true, false);
    auto result = governor.step(0U, request);
    checkPair(result.duty_l, result.duty_r, {0.00F, 0.00F});
    for (std::uint32_t tick = 1U; tick <= 30U; ++tick)
        result = governor.step(tick * 1000U, request);
    checkPair(result.duty_l, result.duty_r, {0.60F, 0.60F});
    const auto contact = fsm::frontDemand(core::State::ATTACK, 0x02U, true);
    request = governedRequest(contact, 9.0F, true, true);
    result = governor.step(31000U, request);
    checkPair(result.duty_l, result.duty_r, {0.62F, 0.62F});
    for (std::uint32_t tick = 32U; tick <= 50U; ++tick)
        result = governor.step(tick * 1000U, request);
    checkPair(result.duty_l, result.duty_r, {1.00F, 1.00F});
    request = governedRequest(approach, 9.0F, true, false);
    result = governor.step(51000U, request);
    checkPair(result.duty_l, result.duty_r, {0.60F, 0.60F});
}
