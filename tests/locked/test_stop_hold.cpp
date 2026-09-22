// Checks B13/D-035 debounced STOP hold and its B3 Controller integration.
// Locks logical reset-only inhibition without claiming physical A1 or MotorGate proof.
// Run with tools/test_host.sh; exact deadlines and 10000 seeded streams are covered.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include <cstdint>
#include <initializer_list>

namespace {
using core::ButtonLevel;
using countdown::Phase;
constexpr std::uint32_t DEBOUNCE_US = config::BTN_DEBOUNCE_MS * 1000U;
constexpr std::uint32_t LONG_US = config::BTN_LONG_MS * 1000U;
constexpr std::uint32_t START_HOLD_US =
    (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;

bool sampleStop(countdown::StopHold& stop, std::uint64_t now, ButtonLevel level) {
    return stop.step(static_cast<std::uint32_t>(now), level);
}

countdown::Result sampleController(countdown::Controller& controller,
                                  std::uint32_t now, ButtonLevel level,
                                  bool external_stop = false) {
    core::Inputs inputs;
    inputs.t_us = now;
    inputs.button_level = level;
    return controller.step(inputs, external_stop);
}

void checkBlocked(const countdown::Result& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK_FALSE(result.motion_permitted);
    CHECK_FALSE(result.go);
}

std::uint32_t startHold(countdown::Controller& controller, std::uint32_t now = 0U) {
    sampleController(controller, now, ButtonLevel::NONE);
    sampleController(controller, now + 1000U, ButtonLevel::START);
    sampleController(controller, now + 1000U + DEBOUNCE_US, ButtonLevel::START);
    sampleController(controller, now + 2000U + DEBOUNCE_US, ButtonLevel::NONE);
    const auto release = now + 2000U + 2U * DEBOUNCE_US;
    const auto result = sampleController(controller, release, ButtonLevel::NONE);
    checkBlocked(result, Phase::HOLDING);
    CHECK(result.start_release);
    CHECK(result.release_us == release);
    return release;
}

std::uint32_t nextRandom(std::uint32_t& state) {
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

void checkStopStream(std::uint32_t& random, unsigned stream) {
    CAPTURE(stream);
    countdown::StopHold stop;
    std::uint64_t now = stream % 2U == 0U
        ? 0x100000000ULL - nextRandom(random) % LONG_US : nextRandom(random);
    if ((nextRandom(random) & 1U) != 0U) {
        CHECK_FALSE(sampleStop(stop, now, ButtonLevel::NONE));
        ++now;
    }
    for (unsigned bounce = 0U; bounce < 3U; ++bounce) {
        CHECK_FALSE(sampleStop(stop, now, ButtonLevel::BOTH));
        now += nextRandom(random) % DEBOUNCE_US;
        const auto other = static_cast<ButtonLevel>(4U + nextRandom(random) % 252U);
        CHECK_FALSE(sampleStop(stop, now, other));
        ++now;
    }
    const auto raw_both = now;
    CHECK_FALSE(sampleStop(stop, now, ButtonLevel::BOTH));
    now = raw_both + DEBOUNCE_US - 1U;
    CHECK_FALSE(sampleStop(stop, now, ButtonLevel::BOTH));
    now += 1U + nextRandom(random) % DEBOUNCE_US;
    const auto qualified = now;
    CHECK_FALSE(sampleStop(stop, now, ButtonLevel::BOTH));
    CHECK_FALSE(sampleStop(stop, raw_both + LONG_US, ButtonLevel::BOTH));
    now = qualified + LONG_US - 1U;
    if ((nextRandom(random) & 3U) == 0U) {
        CHECK_FALSE(sampleStop(stop, now, ButtonLevel::NONE));
        CHECK_FALSE(sampleStop(stop, ++now, ButtonLevel::BOTH));
        now += DEBOUNCE_US;
        CHECK_FALSE(sampleStop(stop, now, ButtonLevel::BOTH));
        now += LONG_US - 1U;
    }
    CHECK_FALSE(sampleStop(stop, now, ButtonLevel::BOTH));
    CHECK(sampleStop(stop, ++now, ButtonLevel::BOTH));
    CHECK(sampleStop(stop, ++now, ButtonLevel::NONE));
    CHECK(sampleStop(stop, now + 0xFFFFFFFFU, ButtonLevel::START));
    stop.reset();
    CHECK_FALSE(sampleStop(stop, 0U, ButtonLevel::NONE));
}
} // namespace

TEST_CASE("B13 boot-held BOTH needs exact 20 ms qualification then a full 1000 ms hold") {
    CHECK(config::BTN_DEBOUNCE_MS == 20U);
    CHECK(config::BTN_LONG_MS == 1000U);
    countdown::StopHold stop;
    CHECK_FALSE(stop.step(0U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US - 1000U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US - 1U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US + 1U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(LONG_US, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US + LONG_US - 1000U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US + LONG_US - 1U, ButtonLevel::BOTH));
    CHECK(stop.step(DEBOUNCE_US + LONG_US, ButtonLevel::BOTH));
    CHECK(stop.step(DEBOUNCE_US + LONG_US + 1U, ButtonLevel::BOTH));
}

TEST_CASE("B13 any non-BOTH logical value including invalid enums cannot initiate STOP") {
    for (unsigned value = 0U; value <= 255U; ++value) {
        if (value == static_cast<unsigned>(ButtonLevel::BOTH)) continue;
        countdown::StopHold stop;
        const auto level = static_cast<ButtonLevel>(value);
        for (auto now : {0U, DEBOUNCE_US, LONG_US, DEBOUNCE_US + LONG_US, 0xFFFFFFFFU})
            CHECK_FALSE(stop.step(now, level));
    }
}

TEST_CASE("B13 delayed BOTH qualification starts the complete hold on the observed tick") {
    for (auto qualifying_gap : {DEBOUNCE_US, DEBOUNCE_US + 1U,
                                DEBOUNCE_US + LONG_US, 0xFFFFFFFFU}) {
        countdown::StopHold stop;
        const std::uint64_t raw = 1234U;
        CHECK_FALSE(sampleStop(stop, raw, ButtonLevel::BOTH));
        const auto qualified = raw + qualifying_gap;
        CHECK_FALSE(sampleStop(stop, qualified, ButtonLevel::BOTH));
        CHECK_FALSE(sampleStop(stop, qualified + LONG_US - 1U, ButtonLevel::BOTH));
        CHECK(sampleStop(stop, qualified + LONG_US, ButtonLevel::BOTH));
    }
}

TEST_CASE("B13 release wins at and around debounce or hold expiry before STOP latches") {
    for (bool release_during_hold : {false, true}) {
        for (int offset : {-1, 0, 1}) {
            countdown::StopHold stop;
            CHECK_FALSE(stop.step(0U, ButtonLevel::BOTH));
            const auto boundary = release_during_hold ? DEBOUNCE_US + LONG_US : DEBOUNCE_US;
            if (release_during_hold) CHECK_FALSE(stop.step(DEBOUNCE_US, ButtonLevel::BOTH));
            const auto release = static_cast<std::uint32_t>(
                static_cast<std::int64_t>(boundary) + offset);
            CHECK_FALSE(stop.step(release, ButtonLevel::NONE));
            const auto fresh = release + 1U;
            CHECK_FALSE(stop.step(fresh, ButtonLevel::BOTH));
            CHECK_FALSE(stop.step(fresh + DEBOUNCE_US, ButtonLevel::BOTH));
            CHECK_FALSE(stop.step(fresh + DEBOUNCE_US + LONG_US - 1U, ButtonLevel::BOTH));
            CHECK(stop.step(fresh + DEBOUNCE_US + LONG_US, ButtonLevel::BOTH));
        }
    }
}

TEST_CASE("B13 every non-BOTH value cancels a pending hold and requires new debounce") {
    for (unsigned value = 0U; value <= 255U; ++value) {
        if (value == static_cast<unsigned>(ButtonLevel::BOTH)) continue;
        countdown::StopHold stop;
        CHECK_FALSE(stop.step(0U, ButtonLevel::BOTH));
        CHECK_FALSE(stop.step(DEBOUNCE_US, ButtonLevel::BOTH));
        CHECK_FALSE(stop.step(DEBOUNCE_US + LONG_US - 1U, static_cast<ButtonLevel>(value)));
        const auto fresh = DEBOUNCE_US + LONG_US;
        CHECK_FALSE(stop.step(fresh, ButtonLevel::BOTH));
        CHECK_FALSE(stop.step(fresh + DEBOUNCE_US - 1U, ButtonLevel::BOTH));
        CHECK_FALSE(stop.step(fresh + DEBOUNCE_US, ButtonLevel::BOTH));
        CHECK_FALSE(stop.step(fresh + DEBOUNCE_US + LONG_US - 1U, ButtonLevel::BOTH));
        CHECK(stop.step(fresh + DEBOUNCE_US + LONG_US, ButtonLevel::BOTH));
    }
}

TEST_CASE("B13 latched STOP survives every release and invalid value until explicit reset") {
    countdown::StopHold stop;
    stop.step(0U, ButtonLevel::BOTH);
    stop.step(DEBOUNCE_US, ButtonLevel::BOTH);
    CHECK(stop.step(DEBOUNCE_US + LONG_US, ButtonLevel::BOTH));
    for (unsigned value = 0U; value <= 255U; ++value)
        CHECK(stop.step(DEBOUNCE_US + LONG_US + value, static_cast<ButtonLevel>(value)));
    stop.reset();
    CHECK_FALSE(stop.step(0U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US + LONG_US - 1U, ButtonLevel::BOTH));
    CHECK(stop.step(DEBOUNCE_US + LONG_US, ButtonLevel::BOTH));
}

TEST_CASE("B0/B13 STOP qualification and hold survive wrap and long legal observation gaps") {
    for (auto origin : {0x100000000ULL - DEBOUNCE_US / 2U,
                        0x100000000ULL - DEBOUNCE_US - LONG_US / 2U}) {
        countdown::StopHold stop;
        CHECK_FALSE(sampleStop(stop, origin, ButtonLevel::BOTH));
        CHECK_FALSE(sampleStop(stop, origin + DEBOUNCE_US, ButtonLevel::BOTH));
        CHECK_FALSE(sampleStop(stop, origin + DEBOUNCE_US + LONG_US - 1U, ButtonLevel::BOTH));
        CHECK(sampleStop(stop, origin + DEBOUNCE_US + LONG_US, ButtonLevel::BOTH));
    }
    countdown::StopHold stop;
    CHECK_FALSE(stop.step(0U, ButtonLevel::BOTH));
    CHECK_FALSE(stop.step(DEBOUNCE_US, ButtonLevel::BOTH));
    std::uint64_t now = DEBOUNCE_US;
    for (unsigned gap = 0U; gap < 4U; ++gap) {
        now += 0xFFFFFFFFU;
        CHECK(sampleStop(stop, now, ButtonLevel::BOTH));
    }
}

TEST_CASE("B3/B13 Controller internal STOP inhibits IDLE and READY after the qualified hold") {
    for (bool ready : {false, true}) {
        countdown::Controller controller;
        std::uint32_t both_at = 0U;
        if (ready) {
            const auto release = startHold(controller);
            const auto go = sampleController(controller, release + START_HOLD_US, ButtonLevel::NONE);
            CHECK(go.go);
            CHECK(go.motion_permitted);
            both_at = release + START_HOLD_US + 1000U;
        }
        const auto expected = ready ? Phase::READY : Phase::IDLE;
        CHECK(sampleController(controller, both_at, ButtonLevel::BOTH).phase == expected);
        CHECK(sampleController(controller, both_at + DEBOUNCE_US, ButtonLevel::BOTH).phase == expected);
        CHECK(sampleController(controller, both_at + DEBOUNCE_US + LONG_US - 1U,
                               ButtonLevel::BOTH).phase == expected);
        checkBlocked(sampleController(controller, both_at + DEBOUNCE_US + LONG_US,
                                       ButtonLevel::BOTH), Phase::STOPPED);
        checkBlocked(sampleController(controller, both_at + DEBOUNCE_US + LONG_US + 1U,
                                       ButtonLevel::NONE), Phase::STOPPED);
    }
}

TEST_CASE("B3/B13 BOTH first cancels COUNTDOWN as MODE then independently reaches STOP") {
    countdown::Controller controller;
    const auto release = startHold(controller);
    const auto both_at = release + 1000U;
    checkBlocked(sampleController(controller, both_at, ButtonLevel::BOTH), Phase::HOLDING);
    checkBlocked(sampleController(controller, both_at + DEBOUNCE_US - 1U,
                                   ButtonLevel::BOTH), Phase::HOLDING);
    checkBlocked(sampleController(controller, both_at + DEBOUNCE_US,
                                   ButtonLevel::BOTH), Phase::IDLE);
    checkBlocked(sampleController(controller, both_at + DEBOUNCE_US + LONG_US - 1U,
                                   ButtonLevel::BOTH), Phase::IDLE);
    checkBlocked(sampleController(controller, both_at + DEBOUNCE_US + LONG_US,
                                   ButtonLevel::BOTH), Phase::STOPPED);
    checkBlocked(sampleController(controller, release + START_HOLD_US,
                                   ButtonLevel::NONE), Phase::STOPPED);
}

TEST_CASE("B3/B13 external STOP remains immediate during BOTH debounce and wins at GO") {
    for (unsigned phase = 0U; phase < 4U; ++phase) {
        countdown::Controller controller;
        std::uint32_t now = 0U;
        if (phase != 0U) now = startHold(controller);
        if (phase == 2U) now += START_HOLD_US;
        if (phase == 3U) {
            now += START_HOLD_US;
            CHECK(sampleController(controller, now, ButtonLevel::NONE).go);
            ++now;
        }
        if (phase <= 1U) sampleController(controller, now, ButtonLevel::BOTH);
        const auto level = phase <= 1U ? ButtonLevel::BOTH : ButtonLevel::NONE;
        checkBlocked(sampleController(controller, now, level, true), Phase::STOPPED);
        checkBlocked(sampleController(controller, now + START_HOLD_US,
                                       ButtonLevel::NONE), Phase::STOPPED);
    }
}

TEST_CASE("B3/B13 Controller reset clears STOP but boot-held START still needs a fresh full hold") {
    countdown::Controller controller;
    sampleController(controller, 0U, ButtonLevel::BOTH);
    sampleController(controller, DEBOUNCE_US, ButtonLevel::BOTH);
    checkBlocked(sampleController(controller, DEBOUNCE_US + LONG_US,
                                   ButtonLevel::BOTH), Phase::STOPPED);
    controller.reset();
    checkBlocked(sampleController(controller, 0U, ButtonLevel::START), Phase::IDLE);
    checkBlocked(sampleController(controller, START_HOLD_US, ButtonLevel::START), Phase::IDLE);
    const auto raw_release = START_HOLD_US + 1000U;
    checkBlocked(sampleController(controller, raw_release, ButtonLevel::NONE), Phase::IDLE);
    checkBlocked(sampleController(controller, raw_release + DEBOUNCE_US,
                                   ButtonLevel::NONE), Phase::IDLE);
    const auto release = startHold(controller, raw_release + DEBOUNCE_US + 1000U);
    checkBlocked(sampleController(controller, release + START_HOLD_US - 1U,
                                   ButtonLevel::NONE), Phase::HOLDING);
    const auto go = sampleController(controller, release + START_HOLD_US, ButtonLevel::NONE);
    CHECK(go.go);
    CHECK(go.motion_permitted);
    CHECK(go.phase == Phase::READY);
}

TEST_CASE("B0/B13 STOP hold matches 10000 independently timed fixed-seed logical streams") {
    std::uint32_t random = 0xB013D035U;
    for (unsigned stream = 0U; stream < 10000U; ++stream)
        checkStopStream(random, stream);
}
