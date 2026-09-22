// Checks B5.5/B5.6 phantom episodes and stuck bits under D-029/D-030/D-031.
// Keeps specification expectations independent of implementation and the FSM.
// Doctest covers exact thresholds, mask exemptions, history, faults and mirroring.
#include "doctest.h"
#include "config.h"
#include "core/opp_fusion.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t WINDOW_US = config::PHANTOM_WINDOW_MS * 1000U;
constexpr std::uint32_t MARKER_US = config::PHANTOM_MS * 1000U;
constexpr std::uint32_t STUCK_US = config::OPP_STUCK_MS * 1000U;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();
constexpr float FRONT_BEARING[8] = {0.0F, -15.0F, 0.0F, -6.0F, 15.0F, 0.0F, 6.0F, 0.0F};
constexpr core::State STATES[] = {core::State::BOOT, core::State::IDLE,
    core::State::COUNTDOWN, core::State::OPENER, core::State::SEARCH,
    core::State::TRACK, core::State::ATTACK, core::State::DEFEND_TURN,
    core::State::EDGE_ESCAPE, core::State::REFLANK, core::State::STOPPED,
    core::State::DRIVE_TEST};

opp_fusion::PhantomSample sample(std::uint32_t time, std::uint8_t mask = 0x02U,
                                float heading = 0.0F, bool edge = false) {
    opp_fusion::PhantomSample result;
    result.t_us = time;
    result.state = core::State::TRACK;
    result.confirmed_mask = mask;
    result.heading_deg = heading;
    result.imu_ok = true;
    result.edge_event = edge;
    return result;
}

void checkPhantom(const opp_fusion::PhantomResult& result, std::uint8_t mask,
                  bool active, bool newly_set = false) {
    CHECK(result.filtered_mask == mask);
    CHECK(result.active == active);
    CHECK(result.phantom_set == newly_set);
    if (active) {
        CHECK(std::isfinite(result.world_deg));
        CHECK(result.world_deg > -180.0F);
        CHECK(result.world_deg <= 180.0F);
    }
}

void checkStuck(const opp_fusion::StuckResult& result, std::uint8_t filtered,
                std::uint8_t fault = 0U, std::uint8_t newly_faulted = 0U) {
    CHECK(result.filtered_mask == filtered);
    CHECK(result.fault_mask == fault);
    CHECK(result.new_fault_mask == newly_faulted);
}

std::uint8_t mirrorMask(std::uint8_t mask) {
    return static_cast<std::uint8_t>((mask & 0x02U) |
        ((mask & 0x01U) << 2U) | ((mask & 0x04U) >> 2U) |
        ((mask & 0x08U) << 1U) | ((mask & 0x10U) >> 1U) |
        ((mask & 0x20U) << 1U) | ((mask & 0x40U) >> 1U));
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}
} // namespace

TEST_CASE("B5.5 B5.6 filters start inert with zero results") {
    const opp_fusion::PhantomResult phantom_result;
    const opp_fusion::StuckResult stuck_result;
    checkPhantom(phantom_result, 0U, false);
    checkStuck(stuck_result, 0U);
    opp_fusion::PhantomFilter phantom;
    opp_fusion::StuckFilter stuck;
    const opp_fusion::PhantomSample idle;
    checkPhantom(phantom.step(idle), 0U, false);
    checkStuck(stuck.step(0U, 0U, NAN_VALUE, false), 0U);
}

TEST_CASE("B5.5 D029 only TRACK and ATTACK can begin a phantom chase") {
    for (const auto state : STATES) {
        opp_fusion::PhantomFilter filter;
        auto input = sample(0U, 0x02U, 0.0F, true);
        input.state = state;
        const bool chase = state == core::State::TRACK || state == core::State::ATTACK;
        checkPhantom(filter.step(input), chase ? 0U : 0x02U, chase, chase);
    }
}

TEST_CASE("B5.5 D029 all masks require front only to mark current world bearing") {
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        CAPTURE(mask);
        opp_fusion::PhantomFilter filter;
        const auto logical = static_cast<std::uint8_t>(mask & 127U);
        const auto front = mask & 7U;
        const bool eligible = front != 0U && (mask & 0x78U) == 0U;
        const bool close = front == 5U || front == 7U;
        const auto result = filter.step(sample(0U, static_cast<std::uint8_t>(mask), 30.0F, true));
        checkPhantom(result, eligible && !close ? 0U : logical, eligible, eligible);
        if (eligible) CHECK(result.world_deg == doctest::Approx(30.0F + FRONT_BEARING[front]));
    }
}

TEST_CASE("B5.5 D029 phantom window starts at first observation not state transition") {
    for (const auto final_age : {WINDOW_US - 1U, WINDOW_US, WINDOW_US + 1U}) {
        opp_fusion::PhantomFilter filter;
        checkPhantom(filter.step(sample(9000U)), 0x02U, false);
        auto later = sample(9000U + WINDOW_US - 1000U, 0x01U, 15.0F);
        later.state = core::State::ATTACK;
        checkPhantom(filter.step(later), 0x01U, false);
        auto edge = sample(9000U + final_age, 0x04U, -15.0F, true);
        edge.state = core::State::TRACK;
        const bool qualified = final_age <= WINDOW_US;
        checkPhantom(filter.step(edge), qualified ? 0U : 0x04U, qualified, qualified);
    }
}

TEST_CASE("B5.5 D029 phantom edge window is inclusive with adjacent us and ms") {
    for (const auto age : {0U, WINDOW_US - 1000U, WINDOW_US - 1U, WINDOW_US,
                           WINDOW_US + 1U, WINDOW_US + 1000U}) {
        opp_fusion::PhantomFilter filter;
        filter.step(sample(4321U));
        const bool qualified = age <= WINDOW_US;
        checkPhantom(filter.step(sample(4321U + age, 0x02U, 0.0F, true)),
                     qualified ? 0U : 0x02U, qualified, qualified);
    }
}

TEST_CASE("B5.5 D029 any prior or current contact cue prevents a later phantom mark") {
    for (const auto cue_time : {0U, 500000U, 1000000U}) {
        opp_fusion::PhantomFilter filter;
        for (const auto time : {0U, 500000U, 1000000U}) {
            auto input = sample(time, 0x02U, 0.0F, time == 1000000U);
            input.state = time == 500000U ? core::State::ATTACK : core::State::TRACK;
            input.contact_cue = time == cue_time;
            checkPhantom(filter.step(input), 0x02U, false);
        }
        checkPhantom(filter.step(sample(1100000U, 0x02U, 0.0F, true)), 0x02U, false);
        filter.step(sample(1100001U, 0U));
        checkPhantom(filter.step(sample(1100002U, 0x02U, 0.0F, true)), 0U, true, true);
    }
}

TEST_CASE("B5.5 D029 a consumed invalid edge cannot mark later in the same chase") {
    for (const bool unavailable : {false, true}) {
        opp_fusion::PhantomFilter filter;
        filter.step(sample(0U));
        auto first_edge = sample(1000U, 0x02U, unavailable ? 0.0F : NAN_VALUE, true);
        first_edge.imu_ok = !unavailable;
        checkPhantom(filter.step(first_edge), 0x02U, false);
        checkPhantom(filter.step(sample(2000U, 0x02U, 40.0F, true)), 0x02U, false);
        filter.step(sample(3000U, 0U));
        const auto renewed = filter.step(sample(4000U, 0x02U, 40.0F, true));
        checkPhantom(renewed, 0U, true, true);
        CHECK(renewed.world_deg == 40.0F);
    }
}

TEST_CASE("B5.5 D029 repeated edges cannot move a marker or refresh its expiry") {
    opp_fusion::PhantomFilter filter;
    checkPhantom(filter.step(sample(0U, 0x02U, 0.0F, true)), 0U, true, true);
    const auto repeated = filter.step(sample(WINDOW_US, 0x02U, 90.0F, true));
    checkPhantom(repeated, 0x02U, true);
    CHECK(repeated.world_deg == 0.0F);
    checkPhantom(filter.step(sample(MARKER_US - 1U, 0x02U, 0.0F, true)), 0U, true);
    checkPhantom(filter.step(sample(MARKER_US, 0x02U, 0.0F, true)), 0x02U, false);
}

TEST_CASE("B5.5 D029 every nonchase state ends a consumed episode and rearms entry") {
    for (const auto state : STATES) {
        if (state == core::State::TRACK || state == core::State::ATTACK) continue;
        opp_fusion::PhantomFilter filter;
        filter.step(sample(0U, 0x02U, 0.0F, true));
        auto outside = sample(1000U);
        outside.state = state;
        filter.step(outside);
        const auto renewed = filter.step(sample(2000U, 0x02U, 90.0F, true));
        checkPhantom(renewed, 0U, true, true);
        CHECK(renewed.world_deg == 90.0F);
    }
}

TEST_CASE("B5.5 D029 target loss side or rear ends an episode and rearms a front chase") {
    for (const auto interruption : {0U, 0x08U, 0x10U, 0x20U, 0x40U, 0x0AU, 0x42U, 0x7FU}) {
        opp_fusion::PhantomFilter filter;
        auto contacted = sample(0U);
        contacted.contact_cue = true;
        filter.step(contacted);
        filter.step(sample(1000U, static_cast<std::uint8_t>(interruption)));
        checkPhantom(filter.step(sample(2000U, 0x02U, 0.0F, true)), 0U, true, true);
    }
}

TEST_CASE("B5.5 D030 replacement discards the old bearing and restarts a full marker lifetime") {
    opp_fusion::PhantomFilter filter;
    filter.step(sample(0U, 0x02U, 0.0F, true));
    filter.step(sample(1000000U, 0U));
    const auto second = filter.step(sample(2000000U, 0x02U, 90.0F, true));
    checkPhantom(second, 0U, true, true);
    CHECK(second.world_deg == 90.0F);
    checkPhantom(filter.step(sample(MARKER_US, 0x02U, 0.0F)), 0x02U, true);
    checkPhantom(filter.step(sample(2000000U + MARKER_US - 1U, 0x02U, 90.0F)), 0U, true);
    checkPhantom(filter.step(sample(2000000U + MARKER_US, 0x02U, 90.0F)), 0x02U, false);
}

TEST_CASE("B5.5 D030 phantom masking is exclusive at the exact 3000 ms expiry") {
    for (const auto age : {MARKER_US - 1000U, MARKER_US - 1U, MARKER_US,
                           MARKER_US + 1U, MARKER_US + 1000U}) {
        opp_fusion::PhantomFilter filter;
        filter.step(sample(4321U, 0x02U, 0.0F, true));
        checkPhantom(filter.step(sample(4321U + age)), age < MARKER_US ? 0U : 0x02U,
                     age < MARKER_US);
    }
}

TEST_CASE("B5.5 D030 every mask honors immediate close side and rear exemptions") {
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        CAPTURE(mask);
        opp_fusion::PhantomFilter filter;
        filter.step(sample(0U, 0x02U, 0.0F, true));
        const auto front = mask & 7U;
        const bool masked = front != 0U && front != 5U && front != 7U && (mask & 0x78U) == 0U;
        const auto current = sample(1000U, static_cast<std::uint8_t>(mask), -FRONT_BEARING[front]);
        checkPhantom(filter.step(current), masked ? 0U : static_cast<std::uint8_t>(mask & 127U), true);
    }
}

TEST_CASE("B5.5 D030 angular exclusion includes exactly 25 degrees and excludes next float") {
    const float inside = std::nextafter(25.0F, 0.0F);
    const float outside = std::nextafter(25.0F, INF_VALUE);
    for (const float distance : {inside, 25.0F, outside}) {
        for (const float sign : {-1.0F, 1.0F}) {
            opp_fusion::PhantomFilter filter;
            filter.step(sample(0U, 0x02U, 0.0F, true));
            checkPhantom(filter.step(sample(1000U, 0x02U, sign * distance)),
                         distance <= 25.0F ? 0U : 0x02U, true);
        }
    }
}

TEST_CASE("B0 B5.5 phantom distance wraps at 180 degrees and uses current front bearing") {
    opp_fusion::PhantomFilter filter;
    const auto marked = filter.step(sample(0U, 0x01U, -166.0F, true));
    checkPhantom(marked, 0U, true, true);
    CHECK(marked.world_deg == 179.0F);
    checkPhantom(filter.step(sample(1000U, 0x04U, -166.0F)), 0x04U, true);
    checkPhantom(filter.step(sample(2000U, 0x04U, -171.0F)), 0U, true);
    checkPhantom(filter.step(sample(3000U, 0x02U, -156.0F)), 0U, true);
    checkPhantom(filter.step(sample(4000U, 0x02U, -155.999F)), 0x02U, true);
}

TEST_CASE("B5.5 invalid or unavailable headings neither mark nor mask but expiry advances") {
    for (const float heading : {NAN_VALUE, INF_VALUE, -INF_VALUE, 0.0F}) {
        const bool healthy = !std::isfinite(heading);
        opp_fusion::PhantomFilter new_marker;
        auto edge = sample(0U, 0x02U, heading, true);
        edge.imu_ok = healthy;
        checkPhantom(new_marker.step(edge), 0x02U, false);
        opp_fusion::PhantomFilter existing;
        existing.step(sample(0U, 0x02U, 0.0F, true));
        auto invalid = sample(1000U, 0x02U, heading);
        invalid.imu_ok = healthy;
        checkPhantom(existing.step(invalid), 0x02U, true);
        invalid.t_us = MARKER_US;
        checkPhantom(existing.step(invalid), 0x02U, false);
        checkPhantom(existing.step(sample(MARKER_US + 1000U)), 0x02U, false);
    }
}

TEST_CASE("B5.5 invalid heading does not restart the original front chase window") {
    opp_fusion::PhantomFilter filter;
    auto invalid = sample(0U, 0x02U, NAN_VALUE);
    filter.step(invalid);
    filter.step(sample(WINDOW_US));
    checkPhantom(filter.step(sample(WINDOW_US + 1U, 0x02U, 0.0F, true)), 0x02U, false);
}

TEST_CASE("B0 B5.5 phantom window and marker duration survive micros wrap") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 100000U;
    opp_fusion::PhantomFilter filter;
    filter.step(sample(start));
    const auto mark_time = start + WINDOW_US;
    checkPhantom(filter.step(sample(mark_time, 0x02U, 0.0F, true)), 0U, true, true);
    checkPhantom(filter.step(sample(mark_time + MARKER_US - 1U)), 0U, true);
    checkPhantom(filter.step(sample(mark_time + MARKER_US)), 0x02U, false);
}

TEST_CASE("B0 B5.5 accumulated expired history cannot reappear after a full timer revolution") {
    opp_fusion::PhantomFilter filter;
    filter.step(sample(0U, 0x02U, 0.0F, true));
    const auto almost_wrap = std::numeric_limits<std::uint32_t>::max() - 100U;
    checkPhantom(filter.step(sample(almost_wrap)), 0x02U, false);
    checkPhantom(filter.step(sample(0U, 0x02U, 0.0F, true)), 0x02U, false);
    filter.reset();
    filter.step(sample(0U));
    checkPhantom(filter.step(sample(almost_wrap)), 0x02U, false);
    checkPhantom(filter.step(sample(0U, 0x02U, 0.0F, true)), 0x02U, false);
}

TEST_CASE("B5.5 reset clears marker consumed episode and remembered contact") {
    for (const bool had_contact : {false, true}) {
        opp_fusion::PhantomFilter filter;
        auto first = sample(0U, 0x02U, 90.0F, true);
        first.contact_cue = had_contact;
        filter.step(first);
        filter.reset();
        checkPhantom(filter.step(sample(1000U, 0x02U, 90.0F)), 0x02U, false);
        checkPhantom(filter.step(sample(1001U, 0x02U, 0.0F, true)), 0U, true, true);
    }
}

TEST_CASE("B5.5 extreme finite headings still produce a finite canonical phantom marker") {
    const float maximum = std::numeric_limits<float>::max();
    for (const float heading : {-maximum, maximum}) {
        for (const auto mask : {0x01U, 0x02U, 0x04U}) {
            opp_fusion::PhantomFilter filter;
            const auto result = filter.step(sample(0U, static_cast<std::uint8_t>(mask), heading, true));
            CHECK(result.active);
            CHECK(result.phantom_set);
            CHECK(std::isfinite(result.world_deg));
            CHECK(result.world_deg > -180.0F);
            CHECK(result.world_deg <= 180.0F);
        }
    }
}

TEST_CASE("B5.6 D031 all seven stuck bits and every mask are independently removed") {
    for (unsigned mask = 0U; mask < 256U; ++mask) {
        opp_fusion::StuckFilter filter;
        const auto input = static_cast<std::uint8_t>(mask);
        const auto logical = static_cast<std::uint8_t>(mask & 127U);
        checkStuck(filter.step(0U, input, 0.0F, true), logical);
        checkStuck(filter.step(STUCK_US, input, 361.0F, true), 0U, logical, logical);
        checkStuck(filter.step(STUCK_US + 1U, input, 0.0F, true), 0U, logical);
    }
}

TEST_CASE("B5.6 D031 elapsed qualification includes exactly 5000 ms with adjacent samples") {
    for (const auto elapsed : {STUCK_US - 1000U, STUCK_US - 1U, STUCK_US,
                               STUCK_US + 1U, STUCK_US + 1000U}) {
        opp_fusion::StuckFilter filter;
        filter.step(8765U, 0x02U, 0.0F, true);
        const bool faulty = elapsed >= STUCK_US;
        checkStuck(filter.step(8765U + elapsed, 0x02U, 361.0F, true),
                   faulty ? 0U : 0x02U, faulty ? 0x02U : 0U, faulty ? 0x02U : 0U);
    }
}

TEST_CASE("B5.6 D031 heading span must exceed exactly 360 degrees") {
    const float lower = std::nextafter(360.0F, 0.0F);
    const float higher = std::nextafter(360.0F, INF_VALUE);
    for (const float angle : {lower, 360.0F, higher}) {
        for (const float sign : {-1.0F, 1.0F}) {
            opp_fusion::StuckFilter filter;
            filter.step(0U, 0x01U, 0.0F, true);
            const bool faulty = angle > 360.0F;
            checkStuck(filter.step(STUCK_US, 0x01U, sign * angle, true),
                       faulty ? 0U : 0x01U, faulty ? 0x01U : 0U, faulty ? 0x01U : 0U);
        }
    }
}

TEST_CASE("B5.6 D031 late rotation can complete a previously elapsed stuck interval") {
    opp_fusion::StuckFilter filter;
    filter.step(0U, 0x04U, 0.0F, true);
    checkStuck(filter.step(STUCK_US, 0x04U, 0.0F, true), 0x04U);
    checkStuck(filter.step(STUCK_US + 1000U, 0x04U, 360.0F, true), 0x04U);
    checkStuck(filter.step(STUCK_US + 2000U, 0x04U, 361.0F, true), 0U, 0x04U, 0x04U);
}

TEST_CASE("B5.6 D031 early rotation retained after return uses observed span rather than net heading") {
    for (const float sign : {-1.0F, 1.0F}) {
        opp_fusion::StuckFilter filter;
        filter.step(0U, 0x08U, 50.0F, true);
        checkStuck(filter.step(1000U, 0x08U, 50.0F + sign * 361.0F, true), 0x08U);
        checkStuck(filter.step(STUCK_US - 1U, 0x08U, 50.0F, true), 0x08U);
        checkStuck(filter.step(STUCK_US, 0x08U, 50.0F, true), 0U, 0x08U, 0x08U);
    }
}

TEST_CASE("B5.6 D031 cumulative oscillation below a 360 degree span is not stuck") {
    opp_fusion::StuckFilter filter;
    filter.step(0U, 0x10U, 0.0F, true);
    for (std::uint32_t tick = 1U; tick <= 10000U; ++tick) {
        const float heading = tick % 2U == 0U ? -180.0F : 180.0F;
        checkStuck(filter.step(tick * 1000U, 0x10U, heading, true), 0x10U);
    }
}

TEST_CASE("B5.6 D031 independent candidates use their own first detected times") {
    opp_fusion::StuckFilter filter;
    for (unsigned bit = 0U; bit < 7U; ++bit) {
        const auto mask = static_cast<std::uint8_t>((1U << (bit + 1U)) - 1U);
        checkStuck(filter.step(bit * 1000U, mask, 0.0F, true), mask);
    }
    checkStuck(filter.step(STUCK_US - 1U, 0x7FU, 361.0F, true), 0x7FU);
    for (unsigned bit = 0U; bit < 7U; ++bit) {
        const auto faulty = static_cast<std::uint8_t>((1U << (bit + 1U)) - 1U);
        checkStuck(filter.step(STUCK_US + bit * 1000U, 0x7FU, 361.0F, true),
                   static_cast<std::uint8_t>(0x7FU & ~faulty), faulty,
                   static_cast<std::uint8_t>(1U << bit));
    }
}

TEST_CASE("B5.6 D031 clearing one bit resets only its candidate and removes its old span") {
    opp_fusion::StuckFilter filter;
    filter.step(0U, 0x03U, 0.0F, true);
    filter.step(1000U, 0x03U, 361.0F, true);
    checkStuck(filter.step(2000U, 0x02U, 361.0F, true), 0x02U);
    checkStuck(filter.step(3000U, 0x03U, 361.0F, true), 0x03U);
    checkStuck(filter.step(STUCK_US, 0x03U, 361.0F, true), 0x01U, 0x02U, 0x02U);
    checkStuck(filter.step(STUCK_US + 3000U, 0x03U, 361.0F, true), 0x01U, 0x02U);
    checkStuck(filter.step(STUCK_US + 4000U, 0x03U, 0.0F, true), 0U, 0x03U, 0x01U);
}

TEST_CASE("B5.6 D031 invalid or unavailable IMU restarts undeclared time and angle evidence") {
    for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE, 0.0F}) {
        opp_fusion::StuckFilter filter;
        filter.step(0U, 0x01U, 0.0F, true);
        filter.step(1000U, 0x01U, 361.0F, true);
        checkStuck(filter.step(2000U, 0x01U, invalid, !std::isfinite(invalid)), 0x01U);
        checkStuck(filter.step(3000U, 0x01U, 0.0F, true), 0x01U);
        checkStuck(filter.step(STUCK_US + 2999U, 0x01U, 361.0F, true), 0x01U);
        checkStuck(filter.step(STUCK_US + 3000U, 0x01U, 361.0F, true), 0U, 0x01U, 0x01U);
    }
}

TEST_CASE("B5.6 D031 fault latches across input clear IMU fault and reassert until reset") {
    opp_fusion::StuckFilter filter;
    filter.step(0U, 0x20U, 0.0F, true);
    checkStuck(filter.step(STUCK_US, 0x20U, 361.0F, true), 0U, 0x20U, 0x20U);
    checkStuck(filter.step(STUCK_US + 1000U, 0U, NAN_VALUE, false), 0U, 0x20U);
    checkStuck(filter.step(STUCK_US + 2000U, 0x60U, NAN_VALUE, true), 0x40U, 0x20U);
    filter.reset();
    checkStuck(filter.step(STUCK_US + 3000U, 0x20U, 0.0F, true), 0x20U);
    checkStuck(filter.step(2U * STUCK_US + 2999U, 0x20U, 361.0F, true), 0x20U);
    checkStuck(filter.step(2U * STUCK_US + 3000U, 0x20U, 361.0F, true), 0U, 0x20U, 0x20U);
}

TEST_CASE("B5.6 D031 preexisting clock time cannot age a newly asserted sensor") {
    opp_fusion::StuckFilter filter;
    checkStuck(filter.step(0U, 0U, -1000.0F, true), 0U);
    checkStuck(filter.step(STUCK_US, 0x40U, 0.0F, true), 0x40U);
    checkStuck(filter.step(STUCK_US + 1U, 0x40U, 361.0F, true), 0x40U);
    checkStuck(filter.step(2U * STUCK_US, 0x40U, 361.0F, true), 0U, 0x40U, 0x40U);
}

TEST_CASE("B0 B5.6 D031 stuck elapsed time survives micros wrap and long gaps") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 100000U;
    opp_fusion::StuckFilter wrapped;
    wrapped.step(start, 0x01U, 0.0F, true);
    checkStuck(wrapped.step(start + STUCK_US - 1U, 0x01U, 361.0F, true), 0x01U);
    checkStuck(wrapped.step(start + STUCK_US, 0x01U, 361.0F, true), 0U, 0x01U, 0x01U);
    opp_fusion::StuckFilter long_lived;
    long_lived.step(0U, 0x02U, 0.0F, true);
    const auto almost_wrap = std::numeric_limits<std::uint32_t>::max() - 100U;
    checkStuck(long_lived.step(almost_wrap, 0x02U, 0.0F, true), 0x02U);
    checkStuck(long_lived.step(0U, 0x02U, 361.0F, true), 0U, 0x02U, 0x02U);
}

TEST_CASE("B5.6 D031 extreme finite heading spans do not overflow the evidence math") {
    const float maximum = std::numeric_limits<float>::max();
    for (const float sign : {-1.0F, 1.0F}) {
        opp_fusion::StuckFilter moving;
        moving.step(0U, 0x01U, sign * maximum, true);
        checkStuck(moving.step(STUCK_US, 0x01U, -sign * maximum, true), 0U, 0x01U, 0x01U);
        opp_fusion::StuckFilter stationary;
        stationary.step(0U, 0x01U, sign * maximum, true);
        checkStuck(stationary.step(STUCK_US, 0x01U, sign * maximum, true), 0x01U);
    }
}

TEST_CASE("B0 B5.5 B5.6 filters mirror 10000 seeded episodes masks angles and faults") {
    std::uint32_t seed = 0xF17E2026U;
    std::uint32_t mask_counts[128] = {};
    for (unsigned episode = 0U; episode < 10000U; ++episode) {
        const auto time = nextRandom(seed);
        // High bits avoid the short low-bit cycle at this four-draw cadence.
        const auto mask = static_cast<std::uint8_t>((nextRandom(seed) >> 16U) & 127U);
        ++mask_counts[mask];
        const float heading = static_cast<float>(static_cast<int>(nextRandom(seed) % 300U) - 150);
        const float travel = static_cast<float>(nextRandom(seed) % 501U);
        opp_fusion::PhantomFilter right;
        opp_fusion::PhantomFilter left;
        const auto marked_r = right.step(sample(time, 0x02U, heading, true));
        const auto marked_l = left.step(sample(time, 0x02U, -heading, true));
        CHECK(marked_r.world_deg == -marked_l.world_deg);
        const auto r = right.step(sample(time + 1000U, mask, heading + travel));
        const auto l = left.step(sample(time + 1000U, mirrorMask(mask), -heading - travel));
        CHECK(l.filtered_mask == mirrorMask(r.filtered_mask));
        CHECK(l.active == r.active);
        CHECK(l.phantom_set == r.phantom_set);
        opp_fusion::StuckFilter stuck_r;
        opp_fusion::StuckFilter stuck_l;
        stuck_r.step(time, mask, heading, true);
        stuck_l.step(time, mirrorMask(mask), -heading, true);
        const auto a = stuck_r.step(time + STUCK_US, mask, heading + travel, true);
        const auto b = stuck_l.step(time + STUCK_US, mirrorMask(mask), -heading - travel, true);
        CHECK(b.filtered_mask == mirrorMask(a.filtered_mask));
        CHECK(b.fault_mask == mirrorMask(a.fault_mask));
        CHECK(b.new_fault_mask == mirrorMask(a.new_fault_mask));
        CHECK(a.fault_mask == (travel > 360.0F ? mask : 0U));
    }
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mask);
        CHECK(mask_counts[mask] > 0U);
    }
}
