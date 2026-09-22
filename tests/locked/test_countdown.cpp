// Checks B0 inert defaults and standalone B3 Gate and Buttons contracts.
// Locks logical hold and qualification evidence while MotorGate integration is deferred.
// Run with tools/test_host.sh; independent spec cases and two fixed-seed stream sets.
#include "doctest.h"
#include "config.h"
#include "core/countdown.h"
#include "core/types.h"
#include "../support/countdown_runner.h"
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t HOLD_US =
    (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
constexpr std::uint32_t DEBOUNCE_US = config::BTN_DEBOUNCE_MS * 1000U;
constexpr countdown::Commands START{true, false, false};
constexpr countdown::Commands MODE{false, true, false};
constexpr countdown::Commands STOP{false, false, true};
using core::ButtonLevel;
using countdown::Phase;

void checkBlocked(const countdown::Result& result, Phase phase) {
    CHECK(result.phase == phase);
    CHECK_FALSE(result.motion_permitted);
    CHECK_FALSE(result.go);
}

void checkNoButtonPulse(const countdown::ButtonEvents& event) {
    CHECK_FALSE(event.start_release);
    CHECK_FALSE(event.mode_press);
}

// This oracle describes authorization windows on an unwrapped clock. It does not
// reuse the module's timestamps, returned phase or interval arithmetic.
void checkGateStream(test_support::FixedRandom& random, std::uint32_t stream) {
    const std::uint64_t origin = stream % 2U == 0U
        ? 0x100000000ULL - (random.next() % HOLD_US) : random.next();
    test_support::CountdownRunner runner(origin);
    bool stopped = false;
    bool has_release = false;
    bool granted = false;
    std::uint64_t earliest_go = 0;
    for (unsigned sample = 0; sample < 80; ++sample) {
        CAPTURE(stream);
        CAPTURE(sample);
        const auto draw = random.next();
        const std::uint32_t gaps[] = {0U, 1U, 999U, 1000U, HOLD_US - 1U,
                                     HOLD_US, HOLD_US + 1U, draw % HOLD_US};
        runner.now_us += gaps[random.next() % 8U];
        if ((draw & 31U) == 0U) {
            runner.gate.reset();
            stopped = has_release = granted = false;
        }
        countdown::Commands command;
        command.start_release = (draw & 4U) != 0U;
        command.mode_press = !command.start_release && (draw & 8U) != 0U;
        command.stop_requested = (draw & 63U) == 63U;
        if (command.stop_requested) {
            stopped = true;
            has_release = granted = false;
        }
        if (!stopped && command.mode_press && !granted) has_release = false;
        const bool new_release = !stopped && !has_release && !granted &&
                                 command.start_release;
        if (new_release) {
            has_release = true;
            earliest_go = runner.now_us + HOLD_US;
        }
        const bool expected_go = !stopped && has_release && !granted &&
                                 runner.now_us >= earliest_go;
        granted = granted || expected_go;
        const auto result = runner.sample(command);
        CHECK(result.motion_permitted == granted);
        CHECK(result.go == expected_go);
        CHECK(result.start_release == new_release);
        if (!has_release || stopped || runner.now_us < earliest_go)
            CHECK_FALSE(result.motion_permitted);
    }
}

void checkButtonStream(test_support::FixedRandom& random, std::uint32_t stream) {
    countdown::Buttons buttons;
    std::uint64_t t = stream % 2U == 0U
        ? 0x100000000ULL - (random.next() % (4U * DEBOUNCE_US)) : random.next();
    const bool boot_held = (random.next() & 1U) != 0U;
    auto sample = [&](ButtonLevel level) {
        return buttons.step(static_cast<std::uint32_t>(t), level);
    };
    checkNoButtonPulse(sample(boot_held ? ButtonLevel::START : ButtonLevel::NONE));
    t += DEBOUNCE_US + random.next() % DEBOUNCE_US;
    checkNoButtonPulse(sample(boot_held ? ButtonLevel::START : ButtonLevel::NONE));
    t += 1U;
    checkNoButtonPulse(sample(ButtonLevel::NONE));
    t += DEBOUNCE_US;
    checkNoButtonPulse(sample(ButtonLevel::NONE));
    for (unsigned bounce = 0; bounce < 4; ++bounce) {
        t += 1U;
        checkNoButtonPulse(sample(ButtonLevel::START));
        t += 1U + random.next() % (DEBOUNCE_US - 1U);
        checkNoButtonPulse(sample(ButtonLevel::NONE));
        t += DEBOUNCE_US;
        checkNoButtonPulse(sample(ButtonLevel::NONE));
    }
    t += 1U;
    checkNoButtonPulse(sample(ButtonLevel::START));
    t += DEBOUNCE_US;
    checkNoButtonPulse(sample(ButtonLevel::START));
    for (unsigned bounce = 0; bounce < 4; ++bounce) {
        t += 1U;
        checkNoButtonPulse(sample(ButtonLevel::NONE));
        t += 1U + random.next() % (DEBOUNCE_US - 1U);
        checkNoButtonPulse(sample(ButtonLevel::START));
    }
    t += 1U;
    const auto edge = static_cast<std::uint32_t>(t);
    checkNoButtonPulse(sample(ButtonLevel::NONE));
    t += DEBOUNCE_US - 1U;
    checkNoButtonPulse(sample(ButtonLevel::NONE));
    t += 1U;
    const auto release = sample(ButtonLevel::NONE);
    CHECK(release.start_release);
    CHECK_FALSE(release.mode_press);
    CHECK(release.edge_us == edge);
    CHECK(release.qualified_us == static_cast<std::uint32_t>(t));
    t += 1U + random.next() % DEBOUNCE_US;
    checkNoButtonPulse(sample(ButtonLevel::NONE));
}
} // namespace

TEST_CASE("B0 default Inputs and Outputs are inert and zero initialized") {
    const core::Inputs input;
    const core::Outputs output;
    CHECK(input.t_us == 0U);
    CHECK(input.line_mask == 0U);
    for (auto raw : input.line_raw_us) CHECK(raw == 0U);
    CHECK(input.opp_raw_mask == 0U);
    CHECK(input.heading_deg == 0.0F);
    CHECK(input.gyro_z_dps == 0.0F);
    CHECK(input.ax_g == 0.0F);
    CHECK(input.ay_g == 0.0F);
    CHECK_FALSE(input.imu_ok);
    CHECK(input.vbat_v == 0.0F);
    CHECK(input.button_level == ButtonLevel::NONE);
    CHECK(output.duty_l == 0.0F);
    CHECK(output.duty_r == 0.0F);
    CHECK_FALSE(output.motors_enabled);
    CHECK(output.ui_state == core::State::BOOT);
}

TEST_CASE("B3 default commands and results contain no implicit start or permission") {
    const countdown::Commands commands;
    const countdown::Result result;
    const countdown::ButtonEvents events;
    CHECK_FALSE(commands.start_release);
    CHECK_FALSE(commands.mode_press);
    CHECK_FALSE(commands.stop_requested);
    checkBlocked(result, Phase::IDLE);
    CHECK_FALSE(result.start_release);
    CHECK(result.release_us == 0U);
    checkNoButtonPulse(events);
    CHECK(events.edge_us == 0U);
    CHECK(events.qualified_us == 0U);
}

TEST_CASE("B3 Gate remains idle indefinitely without a qualified release") {
    countdown::Gate gate;
    for (auto t : {0U, HOLD_US - 1U, HOLD_US, 0xFFFFFFFFU, 0U, HOLD_US}) {
        const auto result = gate.step(t);
        checkBlocked(result, Phase::IDLE);
        CHECK_FALSE(result.start_release);
    }
}

TEST_CASE("B3 Gate holds exactly countdown plus margin and emits GO once") {
    test_support::CountdownRunner runner(123456U);
    const auto release = runner.sample(START);
    checkBlocked(release, Phase::HOLDING);
    CHECK(release.start_release);
    CHECK(release.release_us == 123456U);
    for (std::uint32_t elapsed = config::TICK_US; elapsed < HOLD_US;
         elapsed += config::TICK_US) {
        const auto result = runner.after(config::TICK_US);
        CHECK_FALSE(result.motion_permitted);
        CHECK_FALSE(result.go);
        CHECK_FALSE(result.start_release);
    }
    checkBlocked(runner.after(999U), Phase::HOLDING);
    const auto go = runner.after(1U);
    CHECK(go.phase == Phase::READY);
    CHECK(go.motion_permitted);
    CHECK(go.go);
    CHECK(go.release_us == 123456U);
    const auto after = runner.after(1U);
    CHECK(after.motion_permitted);
    CHECK_FALSE(after.go);
    CHECK_FALSE(after.start_release);
}

TEST_CASE("B3 R1 Gate independently enforces the literal five-second legal minimum") {
    countdown::Gate gate;
    constexpr std::uint32_t release_us = 12000000U;
    gate.step(release_us, START);
    // Deliberately independent of config: a lower configured hold must fail here.
    for (std::uint32_t elapsed_us = 0U; elapsed_us < 5000000U; elapsed_us += 1000U) {
        const auto result = gate.step(release_us + elapsed_us);
        CHECK_FALSE(result.motion_permitted);
        CHECK_FALSE(result.go);
    }
    const auto adjacent = gate.step(release_us + 4999999U);
    CHECK_FALSE(adjacent.motion_permitted);
    CHECK_FALSE(adjacent.go);
}

TEST_CASE("B3 Gate accepts a zero timestamp and does not restart on duplicate releases") {
    countdown::Gate gate;
    CHECK(gate.step(0U, START).start_release);
    const auto duplicate = gate.step(HOLD_US - 1U, START);
    checkBlocked(duplicate, Phase::HOLDING);
    CHECK_FALSE(duplicate.start_release);
    CHECK(duplicate.release_us == 0U);
    CHECK(gate.step(HOLD_US).go);
    const auto ready = gate.step(HOLD_US + 1U, START);
    CHECK(ready.motion_permitted);
    CHECK_FALSE(ready.start_release);
    CHECK_FALSE(ready.go);
}

TEST_CASE("B3 Gate MODE cancels even at GO deadline and a new release needs a full hold") {
    for (auto cancel_at : {1U, HOLD_US - 1000U, HOLD_US - 1U, HOLD_US}) {
        CAPTURE(cancel_at);
        countdown::Gate gate;
        gate.step(0U, START);
        checkBlocked(gate.step(cancel_at, MODE), Phase::IDLE);
        checkBlocked(gate.step(cancel_at + HOLD_US), Phase::IDLE);
        const auto again = cancel_at + HOLD_US + 1U;
        CHECK(gate.step(again, START).start_release);
        checkBlocked(gate.step(again + HOLD_US - 1U), Phase::HOLDING);
        CHECK(gate.step(again + HOLD_US).go);
    }
}

TEST_CASE("B3 Gate STOP dominates releases and stays latched until explicit reset") {
    for (unsigned scenario = 0; scenario < 3; ++scenario) {
        countdown::Gate gate;
        if (scenario != 0U) gate.step(0U, START);
        if (scenario == 2U) CHECK(gate.step(HOLD_US).motion_permitted);
        checkBlocked(gate.step(HOLD_US + 1U, {true, true, true}), Phase::STOPPED);
        checkBlocked(gate.step(2U * HOLD_US, START), Phase::STOPPED);
        checkBlocked(gate.step(3U * HOLD_US, MODE), Phase::STOPPED);
        checkBlocked(gate.step(4U * HOLD_US), Phase::STOPPED);
        gate.reset();
        checkBlocked(gate.step(4U * HOLD_US + 1U), Phase::IDLE);
        CHECK(gate.step(4U * HOLD_US + 2U, START).start_release);
        checkBlocked(gate.step(5U * HOLD_US + 1U), Phase::HOLDING);
        CHECK(gate.step(5U * HOLD_US + 2U).go);
    }
}

TEST_CASE("B3 Gate reset invalidates idle holding ready and stopped history") {
    for (unsigned scenario = 0; scenario < 4; ++scenario) {
        countdown::Gate gate;
        if (scenario >= 1U) gate.step(11U, START);
        if (scenario >= 2U) gate.step(11U + HOLD_US);
        if (scenario == 3U) gate.step(12U + HOLD_US, STOP);
        gate.reset();
        const auto result = gate.step(0U);
        checkBlocked(result, Phase::IDLE);
        CHECK(result.release_us == 0U);
        CHECK_FALSE(result.start_release);
        CHECK(gate.step(1U, START).start_release);
        checkBlocked(gate.step(HOLD_US), Phase::HOLDING);
        CHECK(gate.step(HOLD_US + 1U).go);
    }
}

TEST_CASE("B0/B3 Gate duration and release timestamp survive micros rollover") {
    for (auto origin : {0xFFFFFFFFU, 0xFFFFFFFFU - HOLD_US / 2U}) {
        test_support::CountdownRunner runner(origin);
        CHECK(runner.sample(START).release_us == origin);
        checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
        const auto result = runner.after(1U);
        CHECK(result.go);
        CHECK(result.motion_permitted);
        CHECK(result.release_us == origin);
        CHECK_FALSE(runner.after(1U).go);
    }
}

TEST_CASE("B3 R1 logical permission property on 10000 fixed-seed event streams") {
    test_support::FixedRandom random(0xB3005100U);
    for (std::uint32_t stream = 0; stream < 10000U; ++stream)
        checkGateStream(random, stream);
}

TEST_CASE("B3 Buttons qualifies press and release only at exact debounce boundaries") {
    countdown::Buttons buttons;
    checkNoButtonPulse(buttons.step(0U, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(1000U, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(1000U + DEBOUNCE_US - 1U, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(1000U + DEBOUNCE_US, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(1001U + DEBOUNCE_US, ButtonLevel::START));
    const auto release_at = 2000U + DEBOUNCE_US;
    checkNoButtonPulse(buttons.step(release_at, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(release_at + DEBOUNCE_US - 1000U, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(release_at + DEBOUNCE_US - 1U, ButtonLevel::NONE));
    const auto result = buttons.step(release_at + DEBOUNCE_US, ButtonLevel::NONE);
    CHECK(result.start_release);
    CHECK_FALSE(result.mode_press);
    CHECK(result.edge_us == release_at);
    CHECK(result.qualified_us == release_at + DEBOUNCE_US);
    checkNoButtonPulse(buttons.step(release_at + DEBOUNCE_US + 1U, ButtonLevel::NONE));
}

TEST_CASE("B3 Buttons rejects a press one microsecond shorter than debounce") {
    countdown::Buttons buttons;
    buttons.step(0U, ButtonLevel::NONE);
    buttons.step(1U, ButtonLevel::START);
    checkNoButtonPulse(buttons.step(DEBOUNCE_US, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(2U * DEBOUNCE_US, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(3U * DEBOUNCE_US, ButtonLevel::NONE));
}

TEST_CASE("B3 Buttons START held at boot needs release then a fresh qualified press") {
    countdown::Buttons buttons;
    checkNoButtonPulse(buttons.step(0U, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(HOLD_US, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(HOLD_US + 1U, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(HOLD_US + 1U + DEBOUNCE_US, ButtonLevel::NONE));
    const auto fresh = HOLD_US + 2U + DEBOUNCE_US;
    checkNoButtonPulse(buttons.step(fresh, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(fresh + DEBOUNCE_US, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(fresh + DEBOUNCE_US + 1U, ButtonLevel::NONE));
    CHECK(buttons.step(fresh + 2U * DEBOUNCE_US + 1U, ButtonLevel::NONE).start_release);
}

TEST_CASE("B3 Buttons interrupted release restarts qualification at the last edge") {
    countdown::Buttons buttons;
    buttons.step(0U, ButtonLevel::NONE);
    buttons.step(1U, ButtonLevel::START);
    buttons.step(1U + DEBOUNCE_US, ButtonLevel::START);
    const auto first_release = 2U + DEBOUNCE_US;
    buttons.step(first_release, ButtonLevel::NONE);
    checkNoButtonPulse(buttons.step(first_release + DEBOUNCE_US - 1U, ButtonLevel::START));
    const auto last_release = first_release + DEBOUNCE_US;
    checkNoButtonPulse(buttons.step(last_release, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(last_release + DEBOUNCE_US - 1U, ButtonLevel::NONE));
    const auto event = buttons.step(last_release + DEBOUNCE_US, ButtonLevel::NONE);
    CHECK(event.start_release);
    CHECK(event.edge_us == last_release);
    CHECK(event.qualified_us == last_release + DEBOUNCE_US);
}

TEST_CASE("B3 Buttons MODE and BOTH produce one qualified mode pulse without START") {
    for (auto level : {ButtonLevel::MODE, ButtonLevel::BOTH}) {
        countdown::Buttons buttons;
        buttons.step(0U, ButtonLevel::NONE);
        checkNoButtonPulse(buttons.step(1U, level));
        checkNoButtonPulse(buttons.step(DEBOUNCE_US, level));
        const auto mode = buttons.step(1U + DEBOUNCE_US, level);
        CHECK(mode.mode_press);
        CHECK_FALSE(mode.start_release);
        CHECK(mode.edge_us == 1U);
        CHECK(mode.qualified_us == 1U + DEBOUNCE_US);
        checkNoButtonPulse(buttons.step(2U + DEBOUNCE_US, level));
        checkNoButtonPulse(buttons.step(3U + DEBOUNCE_US, ButtonLevel::NONE));
        checkNoButtonPulse(buttons.step(3U + 2U * DEBOUNCE_US, ButtonLevel::NONE));
    }
}

TEST_CASE("B3 Buttons reset drops a qualified press and treats next held START as boot") {
    countdown::Buttons buttons;
    buttons.step(0U, ButtonLevel::NONE);
    buttons.step(1U, ButtonLevel::START);
    buttons.step(1U + DEBOUNCE_US, ButtonLevel::START);
    buttons.reset();
    checkNoButtonPulse(buttons.step(0U, ButtonLevel::START));
    checkNoButtonPulse(buttons.step(DEBOUNCE_US, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(2U * DEBOUNCE_US, ButtonLevel::NONE));
    buttons.step(3U * DEBOUNCE_US, ButtonLevel::START);
    buttons.reset();
    checkNoButtonPulse(buttons.step(0U, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(4U * DEBOUNCE_US, ButtonLevel::NONE));
}

TEST_CASE("B0/B3 Buttons release and qualification timestamps survive micros rollover") {
    countdown::Buttons buttons;
    const auto release = std::numeric_limits<std::uint32_t>::max() - DEBOUNCE_US / 2U;
    buttons.step(release - 2U * DEBOUNCE_US - 1U, ButtonLevel::NONE);
    buttons.step(release - DEBOUNCE_US - 1U, ButtonLevel::START);
    buttons.step(release - 1U, ButtonLevel::START);
    checkNoButtonPulse(buttons.step(release, ButtonLevel::NONE));
    checkNoButtonPulse(buttons.step(release + DEBOUNCE_US - 1U, ButtonLevel::NONE));
    const auto event = buttons.step(release + DEBOUNCE_US, ButtonLevel::NONE);
    CHECK(event.start_release);
    CHECK(event.edge_us == release);
    CHECK(event.qualified_us == release + DEBOUNCE_US);
    checkNoButtonPulse(buttons.step(release + DEBOUNCE_US + 1U, ButtonLevel::NONE));
}

TEST_CASE("B3 Buttons rejects bounce and boot-held START on 10000 fixed-seed streams") {
    test_support::FixedRandom random(0xB3000020U);
    for (std::uint32_t stream = 0; stream < 10000U; ++stream) {
        CAPTURE(stream);
        checkButtonStream(random, stream);
    }
}
