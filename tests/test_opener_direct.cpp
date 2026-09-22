// Checks the B12 O2 DIRECT contract using B0/B2/B6/B7 and D-022/D-023.
// Keeps exit intents distinct from the future FSM, edge arbitration and motors.
// Spec-only doctest cases cover masks, deadlines, heading, faults and mirroring.
#include "doctest.h"
#include "config.h"
#include "core/governor.h"
#include "core/openers.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t DIRECT_US = config::DIRECT_MS * 1000U;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_VALUE = std::numeric_limits<float>::infinity();

void checkZero(const openers::Result& result, openers::Exit exit) {
    CHECK(result.exit == exit);
    CHECK(result.motion.duty_l == 0.0F);
    CHECK(result.motion.duty_r == 0.0F);
}

void checkActive(const openers::Result& result, float left = .85F, float right = .85F) {
    CHECK(result.exit == openers::Exit::NONE);
    CHECK(result.motion.status == motion::Status::ACTIVE);
    CHECK(result.motion.duty_l == doctest::Approx(left));
    CHECK(result.motion.duty_r == doctest::Approx(right));
}

void checkBounded(const openers::Result& result) {
    CHECK(std::isfinite(result.motion.duty_l));
    CHECK(std::isfinite(result.motion.duty_r));
    CHECK(result.motion.duty_l >= 0.0F);
    CHECK(result.motion.duty_l <= 1.0F);
    CHECK(result.motion.duty_r >= 0.0F);
    CHECK(result.motion.duty_r <= 1.0F);
    if (result.exit != openers::Exit::NONE) {
        CHECK(result.motion.duty_l == 0.0F);
        CHECK(result.motion.duty_r == 0.0F);
    }
}

std::uint8_t mirrored(std::uint8_t mask) {
    return static_cast<std::uint8_t>((mask & 0x02U) |
        ((mask & 0x01U) << 2U) | ((mask & 0x04U) >> 2U) |
        ((mask & 0x08U) << 1U) | ((mask & 0x10U) >> 1U) |
        ((mask & 0x20U) << 1U) | ((mask & 0x40U) >> 1U));
}

void checkMirror(const openers::Result& right, const openers::Result& left) {
    CHECK(right.exit == left.exit);
    CHECK(right.motion.status == left.motion.status);
    CHECK(right.motion.imu_fallback == left.motion.imu_fallback);
    CHECK(right.motion.duty_l == doctest::Approx(left.motion.duty_r));
    CHECK(right.motion.duty_r == doctest::Approx(left.motion.duty_l));
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}

governor::Request governed(const openers::Result& result, float voltage) {
    governor::Request request;
    request.duty_l = result.motion.duty_l;
    request.duty_r = result.motion.duty_r;
    request.vbat_v = voltage;
    request.profile = governor::Profile::OPENER;
    request.centered = true;
    request.contact = true;
    request.inhibited = false;
    return request;
}
} // namespace

TEST_CASE("B12 O2 DIRECT defaults are inert and detections cannot start the opener") {
    const openers::Result result;
    checkZero(result, openers::Exit::NONE);
    CHECK(result.motion.status == motion::Status::IDLE);
    openers::Direct direct;
    for (auto mask : {0U, 0x07U, 0x78U, 0x7FU}) {
        const auto idle = direct.step(1000U, NAN_VALUE, true,
                                      static_cast<std::uint8_t>(mask));
        checkZero(idle, openers::Exit::NONE);
        CHECK(idle.motion.status == motion::Status::IDLE);
    }
}

TEST_CASE("B12 O2 DIRECT starts a 0.85 straight request at its supplied time") {
    openers::Direct direct;
    CHECK(direct.start(123456U, 37.0F, 0U));
    const auto result = direct.step(123456U, 37.0F, true, 0U);
    checkActive(result);
    CHECK_FALSE(result.motion.imu_fallback);
}

TEST_CASE("B12 O2 DIRECT 1 kHz timeline requests straight for exactly 400 ms") {
    openers::Direct direct;
    CHECK(direct.start(91000U, -50.0F, 0U));
    for (std::uint32_t tick = 0U; tick <= config::DIRECT_MS + 1U; ++tick) {
        CAPTURE(tick);
        const auto result = direct.step(91000U + tick * 1000U, -50.0F, true, 0U);
        if (tick < config::DIRECT_MS) {
            checkActive(result);
        } else {
            checkZero(result, openers::Exit::SEARCH);
        }
    }
}

TEST_CASE("B0 B12 O2 DIRECT deadline includes exact adjacent microsecond boundaries") {
    for (const auto elapsed : {DIRECT_US - 1000U, DIRECT_US - 1U,
                               DIRECT_US, DIRECT_US + 1U, DIRECT_US + 1000U}) {
        CAPTURE(elapsed);
        openers::Direct direct;
        CHECK(direct.start(76543U, 0.0F, 0U));
        const auto result = direct.step(76543U + elapsed, 0.0F, true, 0U);
        if (elapsed < DIRECT_US) {
            checkActive(result);
        } else {
            checkZero(result, openers::Exit::SEARCH);
        }
    }
}

TEST_CASE("B0 B12 O2 DIRECT delayed first step does not restart its duration") {
    for (const auto gap : {DIRECT_US + 100000U, 10000000U,
                           std::numeric_limits<std::uint32_t>::max()}) {
        openers::Direct direct;
        CHECK(direct.start(100U, 0.0F, 0U));
        checkZero(direct.step(100U + gap, 0.0F, true, 0U), openers::Exit::SEARCH);
        checkZero(direct.step(101U + gap, NAN_VALUE, true, 0x7FU),
                  openers::Exit::SEARCH);
    }
}

TEST_CASE("B0 B12 O2 DIRECT expiry survives micros wrap from a nonzero start") {
    const auto start = std::numeric_limits<std::uint32_t>::max() - 150000U;
    openers::Direct direct;
    CHECK(direct.start(start, 0.0F, 0U));
    checkActive(direct.step(start + 149999U, 0.0F, true, 0U));
    checkActive(direct.step(start + 150001U, 0.0F, true, 0U));
    checkActive(direct.step(start + DIRECT_US - 1U, 0.0F, true, 0U));
    checkZero(direct.step(start + DIRECT_US, 0.0F, true, 0U), openers::Exit::SEARCH);
}

TEST_CASE("B12 O2 DIRECT all 128 snapshots preserve only front exit eligibility") {
    for (unsigned snapshot = 0U; snapshot < 128U; ++snapshot) {
        CAPTURE(snapshot);
        openers::Direct direct;
        CHECK(direct.start(0U, 0.0F, static_cast<std::uint8_t>(snapshot)));
        const auto result = direct.step(0U, 0.0F, true, 0U);
        if ((snapshot & 0x07U) != 0U) {
            checkZero(result, openers::Exit::FRONT_TARGET);
        } else {
            checkActive(result);
            checkZero(direct.step(DIRECT_US, 0.0F, true, 0U), openers::Exit::SEARCH);
        }
    }
}

TEST_CASE("B2 B12 O2 DIRECT all 128 current masks prioritize front over side rear") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mask);
        openers::Direct direct;
        CHECK(direct.start(0U, 0.0F, 0U));
        const auto result = direct.step(0U, 0.0F, true, static_cast<std::uint8_t>(mask));
        if ((mask & 0x07U) != 0U) {
            checkZero(result, openers::Exit::FRONT_TARGET);
        } else if ((mask & 0x78U) != 0U) {
            checkZero(result, openers::Exit::SIDE_OR_REAR_TARGET);
        } else {
            checkActive(result);
        }
    }
}

TEST_CASE("B2 B12 O2 DIRECT every snapshot current pair obeys front priority") {
    for (unsigned snapshot = 0U; snapshot < 128U; ++snapshot) {
        for (unsigned mask = 0U; mask < 128U; ++mask) {
            CAPTURE(snapshot);
            CAPTURE(mask);
            openers::Direct direct;
            CHECK(direct.start(0U, 0.0F, static_cast<std::uint8_t>(snapshot)));
            const auto result = direct.step(1000U, 0.0F, true,
                                            static_cast<std::uint8_t>(mask));
            if (((snapshot | mask) & 0x07U) != 0U) {
                checkZero(result, openers::Exit::FRONT_TARGET);
            } else if ((mask & 0x78U) != 0U) {
                checkZero(result, openers::Exit::SIDE_OR_REAR_TARGET);
            } else {
                checkActive(result);
            }
        }
    }
}

TEST_CASE("B0 B12 O2 DIRECT ignores unused high mask bit in snapshot and current") {
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        for (const bool snapshot_input : {false, true}) {
            openers::Direct low;
            openers::Direct high;
            const auto plain = static_cast<std::uint8_t>(mask);
            const auto extra = static_cast<std::uint8_t>(mask | 0x80U);
            CHECK(low.start(0U, 0.0F, snapshot_input ? plain : 0U));
            CHECK(high.start(0U, 0.0F, snapshot_input ? extra : 0U));
            const auto expected = low.step(1000U, 0.0F, true, snapshot_input ? 0U : plain);
            const auto actual = high.step(1000U, 0.0F, true, snapshot_input ? 0U : extra);
            CHECK(actual.exit == expected.exit);
            CHECK(actual.motion.status == expected.motion.status);
            CHECK(actual.motion.duty_l == expected.motion.duty_l);
            CHECK(actual.motion.duty_r == expected.motion.duty_r);
        }
    }
}

TEST_CASE("B2 B12 O2 DIRECT detection precedes completion at adjacent and delayed ticks") {
    for (const auto elapsed : {DIRECT_US - 1U, DIRECT_US, DIRECT_US + 1U,
                               DIRECT_US + 100000U}) {
        for (const auto mask : {0x01U, 0x02U, 0x04U, 0x08U, 0x40U, 0x7FU}) {
            openers::Direct direct;
            CHECK(direct.start(700U, 0.0F, 0U));
            checkActive(direct.step(1700U, 0.0F, true, 0U));
            checkZero(direct.step(700U + elapsed, 0.0F, true,
                                 static_cast<std::uint8_t>(mask)),
                      (mask & 0x07U) != 0U ? openers::Exit::FRONT_TARGET
                                           : openers::Exit::SIDE_OR_REAR_TARGET);
        }
    }
}

TEST_CASE("B12 O2 DIRECT saved front remains eligible on a delayed first step") {
    openers::Direct direct;
    CHECK(direct.start(0U, 0.0F, 0x01U));
    checkZero(direct.step(DIRECT_US + 1000U, 0.0F, true, 0x78U),
              openers::Exit::FRONT_TARGET);
}

TEST_CASE("B12 O2 DIRECT all normal exits latch zero despite later detection and faults") {
    for (const auto first_mask : {0U, 0x01U, 0x10U}) {
        openers::Direct direct;
        CHECK(direct.start(0U, 0.0F, 0U));
        const auto exit = first_mask == 0U ? openers::Exit::SEARCH :
            first_mask == 1U ? openers::Exit::FRONT_TARGET : openers::Exit::SIDE_OR_REAR_TARGET;
        checkZero(direct.step(DIRECT_US, 0.0F, true,
                             static_cast<std::uint8_t>(first_mask)), exit);
        for (const auto next_mask : {0U, 0x01U, 0x78U, 0x7FU}) {
            checkZero(direct.step(DIRECT_US + 1000U + next_mask, NAN_VALUE, true,
                                 static_cast<std::uint8_t>(next_mask)), exit);
        }
    }
}

TEST_CASE("B12 O2 DIRECT restart replaces terminal snapshot reference and deadline") {
    openers::Direct direct;
    CHECK(direct.start(0U, 0.0F, 0x02U));
    checkZero(direct.step(0U, 0.0F, true, 0U), openers::Exit::FRONT_TARGET);
    CHECK(direct.start(1000000U, 50.0F, 0x78U));
    checkActive(direct.step(1000000U, 45.0F, true, 0U), .95F, .75F);
    checkActive(direct.step(1000000U + DIRECT_US - 1U, 50.0F, true, 0U));
    checkZero(direct.step(1000000U + DIRECT_US, 50.0F, true, 0U), openers::Exit::SEARCH);
}

TEST_CASE("B12 O2 DIRECT starting while active captures a new complete command") {
    openers::Direct direct;
    CHECK(direct.start(0U, 0.0F, 0U));
    checkActive(direct.step(DIRECT_US - 1000U, 0.0F, true, 0U));
    CHECK(direct.start(DIRECT_US - 1000U, -30.0F, 0U));
    checkActive(direct.step(DIRECT_US, -30.0F, true, 0U));
    checkZero(direct.step(2U * DIRECT_US - 1000U, -30.0F, true, 0U), openers::Exit::SEARCH);
}

TEST_CASE("B12 O2 DIRECT reset clears active terminal and invalid commands") {
    for (const auto mode : {0U, 1U, 2U}) {
        openers::Direct direct;
        CHECK(direct.start(0U, 0.0F, mode == 1U ? 0x02U : 0U));
        direct.step(1000U, mode == 2U ? NAN_VALUE : 0.0F, true, 0U);
        direct.reset();
        const auto idle = direct.step(2000U, NAN_VALUE, true, 0x7FU);
        checkZero(idle, openers::Exit::NONE);
        CHECK(idle.motion.status == motion::Status::IDLE);
        CHECK(direct.start(3000U, 0.0F, 0U));
        checkActive(direct.step(3000U, 0.0F, true, 0U));
    }
}

TEST_CASE("B7 B12 O2 DIRECT rejects every nonfinite start heading and stays zero") {
    for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        for (const auto snapshot : {0U, 0x07U, 0x78U}) {
            openers::Direct direct;
            CHECK(direct.start(0U, 0.0F, 0U));
            checkActive(direct.step(0U, 0.0F, true, 0U));
            CHECK_FALSE(direct.start(1000U, invalid, static_cast<std::uint8_t>(snapshot)));
            checkZero(direct.step(1000U, 0.0F, true, 0U), openers::Exit::INVALID);
            checkZero(direct.step(2000U, 0.0F, false, 0x7FU), openers::Exit::INVALID);
            CHECK(direct.start(3000U, 0.0F, 0U));
            checkActive(direct.step(3000U, 0.0F, true, 0U));
        }
    }
}

TEST_CASE("B7 B12 O2 DIRECT healthy nonfinite samples latch invalid zero") {
    for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        openers::Direct direct;
        CHECK(direct.start(0U, 0.0F, 0U));
        checkZero(direct.step(1000U, invalid, true, 0U), openers::Exit::INVALID);
        checkZero(direct.step(2000U, 0.0F, false, 0x7FU), openers::Exit::INVALID);
        checkZero(direct.step(DIRECT_US, 0.0F, true, 0U), openers::Exit::INVALID);
    }
}

TEST_CASE("B7 B12 O2 DIRECT unavailable IMU ignores heading and preserves original reference") {
    openers::Direct direct;
    CHECK(direct.start(0U, 40.0F, 0U));
    for (const float invalid : {NAN_VALUE, INF_VALUE, -INF_VALUE}) {
        const auto result = direct.step(1000U, invalid, false, 0U);
        checkActive(result);
        CHECK(result.motion.imu_fallback);
    }
    const auto recovered = direct.step(2000U, 35.0F, true, 0U);
    checkActive(recovered, .95F, .75F);
    CHECK_FALSE(recovered.motion.imu_fallback);
    checkZero(direct.step(DIRECT_US, NAN_VALUE, false, 0U), openers::Exit::SEARCH);
}

TEST_CASE("B7 D022 B12 O2 DIRECT keeps its captured heading through successive samples") {
    openers::Direct direct;
    CHECK(direct.start(0U, 20.0F, 0U));
    checkActive(direct.step(1000U, 15.0F, true, 0U), .95F, .75F);
    checkActive(direct.step(2000U, 15.0F, true, 0U), .95F, .75F);
    checkActive(direct.step(3000U, 25.0F, true, 0U), .75F, .95F);
    checkActive(direct.step(4000U, 20.0F, true, 0U));
}

TEST_CASE("B0 B7 D022 B12 O2 DIRECT shortest heading correction crosses angular wrap") {
    for (const float revolutions : {-1080.0F, 0.0F, 1080.0F}) {
        openers::Direct left;
        openers::Direct right;
        CHECK(left.start(0U, revolutions + 179.0F, 0U));
        CHECK(right.start(0U, -revolutions - 179.0F, 0U));
        checkActive(left.step(1000U, -179.0F, true, 0U), .81F, .89F);
        checkActive(right.step(1000U, 179.0F, true, 0U), .89F, .81F);
    }
}

TEST_CASE("B7 D022 B12 O2 DIRECT bounded correction cannot reverse a wheel") {
    const float heading[] = {-90.0F, -12.5F, -5.0F, 0.0F, 5.0F, 12.5F, 90.0F};
    const float left[] = {1.0F, 1.0F, .95F, .85F, .75F, .60F, .60F};
    const float right[] = {.60F, .60F, .75F, .85F, .95F, 1.0F, 1.0F};
    for (unsigned index = 0U; index < 7U; ++index) {
        openers::Direct direct;
        CHECK(direct.start(0U, 0.0F, 0U));
        const auto result = direct.step(1000U, heading[index], true, 0U);
        checkActive(result, left[index], right[index]);
        checkBounded(result);
    }
}

TEST_CASE("B7 B12 O2 DIRECT finite extreme headings produce finite bounded requests") {
    const float maximum = std::numeric_limits<float>::max();
    for (const float start : {-maximum, 0.0F, maximum}) {
        for (const float current : {-maximum, 0.0F, maximum}) {
            openers::Direct direct;
            CHECK(direct.start(0U, start, 0U));
            const auto result = direct.step(1000U, current, true, 0U);
            CHECK(result.exit == openers::Exit::NONE);
            CHECK(result.motion.status == motion::Status::ACTIVE);
            checkBounded(result);
        }
    }
}

TEST_CASE("B0 B7 B12 O2 DIRECT 10000 seeded episodes mirror heading masks and exits") {
    std::uint32_t seed = 0xD12EC726U;
    for (unsigned episode = 0U; episode < 10000U; ++episode) {
        const auto start = nextRandom(seed);
        const float heading = static_cast<float>(static_cast<int>(nextRandom(seed) % 4001U) - 2000);
        const float drift = static_cast<float>(static_cast<int>(nextRandom(seed) % 321U) - 160);
        const auto snapshot = static_cast<std::uint8_t>(episode % 3U == 0U ? nextRandom(seed) & 127U : 0U);
        const auto mask = static_cast<std::uint8_t>(nextRandom(seed) & 127U);
        openers::Direct right;
        openers::Direct left;
        CHECK(right.start(start, heading, snapshot));
        CHECK(left.start(start, -heading, mirrored(snapshot)));
        for (const auto elapsed : {0U, 1000U, DIRECT_US - 1U, DIRECT_US, DIRECT_US + 1000U}) {
            const auto current = static_cast<std::uint8_t>(elapsed >= DIRECT_US ? mask : 0U);
            const bool healthy = elapsed != 1000U;
            const auto a = right.step(start + elapsed, heading + drift, healthy, current);
            const auto b = left.step(start + elapsed, -heading - drift, healthy, mirrored(current));
            checkMirror(a, b);
            checkBounded(a);
            checkBounded(b);
        }
    }
}

TEST_CASE("B6 B12 O2 DIRECT governor composition respects slew OPENER cap and immediate exit zero") {
    for (const float voltage : {9.0F, 11.1F, 12.6F}) {
        for (const float heading : {-90.0F, 0.0F, 90.0F}) {
            openers::Direct direct;
            governor::Governor governor;
            CHECK(direct.start(0U, 0.0F, 0U));
            const auto demand = direct.step(0U, heading, true, 0U);
            const auto request = governed(demand, voltage);
            const auto first = governor.step(0U, request);
            CHECK(first.duty_l == 0.0F);
            CHECK(first.duty_r == 0.0F);
            const auto accelerated = governor.step(1000U, request);
            CHECK(accelerated.duty_l == doctest::Approx(.02F));
            CHECK(accelerated.duty_r == doctest::Approx(.02F));
            const auto settled = governor.step(100000U, request);
            CHECK(settled.valid);
            const float scale = config::V_NOM_V / voltage;
            CHECK(settled.duty_l == doctest::Approx(std::min(.85F, demand.motion.duty_l * scale)));
            CHECK(settled.duty_r == doctest::Approx(std::min(.85F, demand.motion.duty_r * scale)));
            const auto exit = direct.step(101000U, heading, true, 0x02U);
            checkZero(exit, openers::Exit::FRONT_TARGET);
            const auto stopped = governor.step(101000U, governed(exit, voltage));
            CHECK(stopped.duty_l == 0.0F);
            CHECK(stopped.duty_r == 0.0F);
        }
    }
}

TEST_CASE("B6 B7 D023 B12 O2 DIRECT duration stays 400 ms at every composed voltage") {
    for (const float voltage : {9.0F, 11.1F, 12.6F}) {
        openers::Direct direct;
        governor::Governor governor;
        CHECK(direct.start(100U, 0.0F, 0U));
        governor.step(100U, governed(direct.step(100U, 0.0F, false, 0U), voltage));
        const auto active = direct.step(100U + DIRECT_US - 1U, NAN_VALUE, false, 0U);
        checkActive(active);
        const auto driven = governor.step(100U + DIRECT_US - 1U, governed(active, voltage));
        CHECK(driven.duty_l > 0.0F);
        CHECK(driven.duty_l <= config::OPENER_DUTY_MAX);
        const auto done = direct.step(100U + DIRECT_US, NAN_VALUE, false, 0U);
        checkZero(done, openers::Exit::SEARCH);
        const auto stopped = governor.step(100U + DIRECT_US, governed(done, voltage));
        CHECK(stopped.duty_l == 0.0F);
        CHECK(stopped.duty_r == 0.0F);
    }
}
