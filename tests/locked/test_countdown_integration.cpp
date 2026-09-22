// Checks the B3 logical Buttons-to-Gate composition approved by D-019.
// Locks full-hold timing after qualification without claiming hardware MotorGate proof.
// Run with tools/test_host.sh; boundaries and 10000 seeded input streams are covered.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include "../support/countdown_runner.h"
#include <cstdint>
#include <initializer_list>

namespace {
constexpr std::uint32_t HOLD_US =
    (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
constexpr std::uint32_t DEBOUNCE_US = config::BTN_DEBOUNCE_MS * 1000U;
using core::ButtonLevel;
using countdown::Phase;

class ControllerRunner {
public:
    explicit ControllerRunner(std::uint64_t origin = 0U) : now_us(origin) {}
    countdown::Result sample(ButtonLevel level = ButtonLevel::NONE,
                             bool stop = false) {
        core::Inputs input;
        input.t_us = static_cast<std::uint32_t>(now_us);
        input.button_level = level;
        last = controller.step(input, stop);
        release_pulses += last.start_release ? 1U : 0U;
        go_pulses += last.go ? 1U : 0U;
        return last;
    }
    countdown::Result after(std::uint32_t elapsed_us,
                            ButtonLevel level = ButtonLevel::NONE,
                            bool stop = false) {
        now_us += elapsed_us;
        return sample(level, stop);
    }
    countdown::Controller controller;
    countdown::Result last;
    std::uint64_t now_us;
    unsigned release_pulses = 0U;
    unsigned go_pulses = 0U;
};

void checkBlocked(const countdown::Result& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK_FALSE(result.motion_permitted);
    CHECK_FALSE(result.go);
}

std::uint64_t startHold(ControllerRunner& runner) {
    runner.sample();
    runner.after(1000U, ButtonLevel::START);
    runner.after(DEBOUNCE_US, ButtonLevel::START);
    runner.after(1000U);
    const auto release = runner.after(DEBOUNCE_US);
    checkBlocked(release, Phase::HOLDING);
    CHECK(release.start_release);
    CHECK(release.release_us == static_cast<std::uint32_t>(runner.now_us));
    return runner.now_us;
}

void checkRandomBootAndPress(ControllerRunner& runner,
                             test_support::FixedRandom& random) {
    const bool boot_held = (random.next() & 1U) != 0U;
    const auto boot = boot_held ? ButtonLevel::START : ButtonLevel::NONE;
    checkBlocked(runner.sample(boot), Phase::IDLE);
    checkBlocked(runner.after(HOLD_US, boot), Phase::IDLE);
    checkBlocked(runner.after(1U), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US), Phase::IDLE);
    for (unsigned bounce = 0; bounce < 4U; ++bounce) {
        checkBlocked(runner.after(1U, ButtonLevel::START), Phase::IDLE);
        checkBlocked(runner.after(1U + random.next() % (DEBOUNCE_US - 1U)),
                     Phase::IDLE);
        checkBlocked(runner.after(DEBOUNCE_US), Phase::IDLE);
    }
    checkBlocked(runner.after(1000U, ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US, ButtonLevel::START), Phase::IDLE);
    CHECK(runner.release_pulses == 0U);
}

void checkControllerStream(test_support::FixedRandom& random, unsigned stream) {
    CAPTURE(stream);
    const std::uint64_t origin = stream % 2U == 0U
        ? 0x100000000ULL - random.next() % (4U * DEBOUNCE_US) : random.next();
    ControllerRunner runner(origin);
    checkRandomBootAndPress(runner, random);
    for (unsigned bounce = 0; bounce < 4U; ++bounce) {
        checkBlocked(runner.after(1U), Phase::IDLE);
        checkBlocked(runner.after(1U + random.next() % (DEBOUNCE_US - 1U),
                                  ButtonLevel::START), Phase::IDLE);
    }
    checkBlocked(runner.after(1U), Phase::IDLE);
    const auto raw_release = runner.now_us;
    checkBlocked(runner.after(DEBOUNCE_US - 1U), Phase::IDLE);
    const auto delay = 1U + random.next() % (2U * DEBOUNCE_US);
    const auto release = runner.after(delay);
    const auto qualified = runner.now_us;
    checkBlocked(release, Phase::HOLDING);
    CHECK(release.start_release);
    CHECK(release.release_us == static_cast<std::uint32_t>(qualified));
    runner.now_us = raw_release + HOLD_US;
    checkBlocked(runner.sample(), Phase::HOLDING);
    runner.now_us = qualified + HOLD_US - 1U;
    checkBlocked(runner.sample(), Phase::HOLDING);
    const auto go = runner.after(1U);
    CHECK(go.go);
    CHECK(go.motion_permitted);
    CHECK_FALSE(runner.after(1000U).go);
    CHECK(runner.release_pulses == 1U);
    CHECK(runner.go_pulses == 1U);
}
} // namespace

TEST_CASE("B3 Controller starts a complete hold at exact release qualification") {
    ControllerRunner runner;
    checkBlocked(runner.sample(), Phase::IDLE);
    checkBlocked(runner.after(1000U, ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US - 1U, ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(1U, ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(1000U), Phase::IDLE);
    const auto raw_release = runner.now_us;
    checkBlocked(runner.after(DEBOUNCE_US - 1000U), Phase::IDLE);
    checkBlocked(runner.after(999U), Phase::IDLE);
    CHECK(runner.release_pulses == 0U);
    const auto release = runner.after(1U);
    const auto qualified = runner.now_us;
    checkBlocked(release, Phase::HOLDING);
    CHECK(release.start_release);
    CHECK(release.release_us == qualified);
    CHECK_FALSE(runner.after(1U).start_release);
    runner.now_us = raw_release + HOLD_US;
    checkBlocked(runner.sample(), Phase::HOLDING);
    for (auto remaining : {1000U, 1U}) {
        runner.now_us = qualified + HOLD_US - remaining;
        checkBlocked(runner.sample(), Phase::HOLDING);
    }
    CHECK(runner.after(1U).go);
    CHECK(runner.last.motion_permitted);
    CHECK(runner.last.phase == Phase::READY);
    CHECK_FALSE(runner.after(1U).go);
    CHECK_FALSE(runner.after(999U).go);
    CHECK(runner.release_pulses == 1U);
    CHECK(runner.go_pulses == 1U);
}

TEST_CASE("B3 Controller bounce rejects short presses and restarts release debounce") {
    ControllerRunner runner;
    runner.sample();
    runner.after(1000U, ButtonLevel::START);
    checkBlocked(runner.after(DEBOUNCE_US - 1U), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US), Phase::IDLE);
    CHECK(runner.release_pulses == 0U);
    runner.after(1000U, ButtonLevel::START);
    runner.after(DEBOUNCE_US, ButtonLevel::START);
    checkBlocked(runner.after(1000U), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US - 1U, ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(1U), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US - 1U), Phase::IDLE);
    CHECK(runner.release_pulses == 0U);
    CHECK(runner.after(1U).start_release);
    const auto qualified = runner.now_us;
    checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
    CHECK(runner.after(1U).go);
    CHECK(runner.last.release_us == qualified);
}

TEST_CASE("B3 Controller ignores boot-held START until a fresh qualified press") {
    ControllerRunner runner;
    checkBlocked(runner.sample(ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(2U * HOLD_US, ButtonLevel::START), Phase::IDLE);
    checkBlocked(runner.after(1000U), Phase::IDLE);
    checkBlocked(runner.after(DEBOUNCE_US), Phase::IDLE);
    checkBlocked(runner.after(HOLD_US), Phase::IDLE);
    CHECK(runner.release_pulses == 0U);
    startHold(runner);
    checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
    CHECK(runner.after(1U).go);
}

TEST_CASE("B3 Controller reset discards partial press holding ready and STOP history") {
    for (unsigned scenario = 0U; scenario < 4U; ++scenario) {
        CAPTURE(scenario);
        ControllerRunner runner;
        if (scenario == 0U) {
            runner.sample();
            runner.after(1000U, ButtonLevel::START);
            runner.after(DEBOUNCE_US - 1U, ButtonLevel::START);
        } else {
            startHold(runner);
            if (scenario >= 2U) runner.after(HOLD_US);
            if (scenario == 3U) runner.after(1000U, ButtonLevel::NONE, true);
        }
        runner.controller.reset();
        checkBlocked(runner.after(1000U, ButtonLevel::START), Phase::IDLE);
        CHECK(runner.last.release_us == 0U);
        checkBlocked(runner.after(DEBOUNCE_US, ButtonLevel::START), Phase::IDLE);
        checkBlocked(runner.after(1000U), Phase::IDLE);
        checkBlocked(runner.after(DEBOUNCE_US), Phase::IDLE);
        checkBlocked(runner.after(HOLD_US), Phase::IDLE);
        startHold(runner);
        CHECK(runner.after(HOLD_US).go);
    }
}

TEST_CASE("B3 Controller qualified MODE cancels at GO deadline and requires a new hold") {
    for (auto mode : {ButtonLevel::MODE, ButtonLevel::BOTH}) {
        ControllerRunner runner;
        const auto release = startHold(runner);
        runner.now_us = release + HOLD_US - DEBOUNCE_US;
        checkBlocked(runner.sample(mode), Phase::HOLDING);
        checkBlocked(runner.after(DEBOUNCE_US - 1U, mode), Phase::HOLDING);
        checkBlocked(runner.after(1U, mode), Phase::IDLE);
        CHECK(runner.go_pulses == 0U);
        if (mode == ButtonLevel::BOTH) {
            checkBlocked(runner.after(HOLD_US, mode), Phase::STOPPED);
            checkBlocked(runner.after(1000U), Phase::STOPPED);
            checkBlocked(runner.after(DEBOUNCE_US), Phase::STOPPED);
            checkBlocked(runner.after(HOLD_US, ButtonLevel::START), Phase::STOPPED);
            checkBlocked(runner.after(DEBOUNCE_US), Phase::STOPPED);
            CHECK_FALSE(runner.last.start_release);
            CHECK(runner.go_pulses == 0U);
            runner.controller.reset();
        } else {
            checkBlocked(runner.after(HOLD_US, mode), Phase::IDLE);
            runner.after(1000U);
            runner.after(DEBOUNCE_US);
        }
        startHold(runner);
        checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
        CHECK(runner.after(1U).go);
    }
}

TEST_CASE("B2/B3 Controller external STOP is immediate latched and wins at GO deadline") {
    for (unsigned scenario = 0U; scenario < 4U; ++scenario) {
        CAPTURE(scenario);
        ControllerRunner runner;
        if (scenario != 0U) startHold(runner);
        if (scenario == 2U) runner.now_us += HOLD_US;
        if (scenario == 3U) CHECK(runner.after(HOLD_US).go);
        checkBlocked(runner.sample(ButtonLevel::NONE, true), Phase::STOPPED);
        checkBlocked(runner.after(HOLD_US, ButtonLevel::START), Phase::STOPPED);
        checkBlocked(runner.after(DEBOUNCE_US, ButtonLevel::START), Phase::STOPPED);
        checkBlocked(runner.after(1000U), Phase::STOPPED);
        checkBlocked(runner.after(DEBOUNCE_US), Phase::STOPPED);
        checkBlocked(runner.after(HOLD_US), Phase::STOPPED);
        CHECK_FALSE(runner.last.start_release);
        runner.controller.reset();
        startHold(runner);
        CHECK(runner.after(HOLD_US).go);
    }
}

TEST_CASE("B3 Controller delayed release-qualifying tick cannot backdate the hold") {
    for (auto missed_us : {1000U, DEBOUNCE_US, HOLD_US + 1000U}) {
        CAPTURE(missed_us);
        ControllerRunner runner;
        runner.sample();
        runner.after(1000U, ButtonLevel::START);
        runner.after(DEBOUNCE_US, ButtonLevel::START);
        runner.after(1000U);
        const auto delayed = runner.after(DEBOUNCE_US + missed_us);
        checkBlocked(delayed, Phase::HOLDING);
        CHECK(delayed.start_release);
        CHECK(delayed.release_us == runner.now_us);
        checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
        CHECK(runner.after(1U).go);
    }
}

TEST_CASE("B0/B3 Controller debounce and full hold survive micros wraparound") {
    for (auto origin : {0x100000000ULL - DEBOUNCE_US,
                        0x100000000ULL - HOLD_US / 2U}) {
        ControllerRunner runner(origin);
        const auto release = startHold(runner);
        checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
        const auto go = runner.after(1U);
        CHECK(go.go);
        CHECK(go.motion_permitted);
        CHECK(go.release_us == static_cast<std::uint32_t>(release));
        CHECK_FALSE(runner.after(1000U).go);
    }
}

TEST_CASE("B3 Controller subsequent START cycles cannot shorten or restart a hold") {
    ControllerRunner runner;
    const auto release = startHold(runner);
    runner.after(1000U, ButtonLevel::START);
    runner.after(DEBOUNCE_US, ButtonLevel::START);
    runner.after(1000U);
    checkBlocked(runner.after(DEBOUNCE_US), Phase::HOLDING);
    CHECK_FALSE(runner.last.start_release);
    CHECK(runner.last.release_us == release);
    runner.now_us = release + HOLD_US - 1U;
    checkBlocked(runner.sample(), Phase::HOLDING);
    CHECK(runner.after(1U).go);
    runner.after(1000U, ButtonLevel::START);
    runner.after(DEBOUNCE_US, ButtonLevel::START);
    runner.after(1000U);
    CHECK(runner.after(DEBOUNCE_US).motion_permitted);
    CHECK(runner.release_pulses == 1U);
    CHECK(runner.go_pulses == 1U);
}

TEST_CASE("B3 Controller full-hold property on 10000 seeded START bounce boot-held streams") {
    test_support::FixedRandom random(0xD0195100U);
    for (unsigned stream = 0U; stream < 10000U; ++stream)
        checkControllerStream(random, stream);
}
