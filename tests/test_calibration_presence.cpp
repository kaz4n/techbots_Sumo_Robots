// Exercises B3/D024/D083 gyro admission through the public countdown services.
// Derives expected results from the frozen contract without production-source inspection.
// Host doctest cases cover admission, identity, lifecycle, wrap and an analytic stream.
#include "doctest.h"
#include "core/countdown.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using countdown::GyroPresence;
using countdown::ServiceSample;
using countdown::ServiceResult;
constexpr std::uint32_t CAL_BEGIN = config::CAL_START_MS * 1000U;
constexpr std::uint32_t CAL_END = config::CAL_END_MS * 1000U;
constexpr std::uint32_t HOLD =
    (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
constexpr std::uint32_t AGE = config::IMU_HEADING_MAX_GAP_US;
constexpr std::uint32_t DEBOUNCE = config::BTN_DEBOUNCE_MS * 1000U;
constexpr float OLD_BIAS = -7.0F;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();

ServiceSample observation(std::uint32_t decision, std::uint32_t source,
                          std::uint32_t sequence, float raw = 1.0F,
                          GyroPresence presence = GyroPresence::VALID) {
    ServiceSample sample;
    sample.t_us = decision;
    sample.raw_gyro_z_dps = raw;
    sample.gyro_presence = presence;
    sample.gyro_observation_us = source;
    sample.gyro_sequence = sequence;
    return sample;
}

ServiceSample absent(std::uint32_t time) {
    return observation(time, 0x87654321U, 0x12345678U, NAN_VALUE,
                       GyroPresence::ABSENT);
}

struct Attempt {
    countdown::Services services;
    std::uint32_t base;
    explicit Attempt(std::uint32_t release = 0U) : base(release) {
        CHECK(services.start(base, OLD_BIAS));
    }
    ServiceResult valid(std::uint32_t elapsed, std::uint32_t sequence,
                        float raw = 1.0F, std::uint32_t age = 0U) {
        return services.step(observation(base + elapsed, base + elapsed - age,
                                         sequence, raw));
    }
    ServiceResult finish() { return services.step(absent(base + CAL_END)); }
};

void accepted(const ServiceResult& result, std::uint32_t count, float bias) {
    CHECK(result.calibration_finished);
    CHECK_FALSE(result.calibration_rejected);
    CHECK(result.calibration_samples == count);
    CHECK(result.bias_dps == doctest::Approx(bias));
}

void rejected(const ServiceResult& result, std::uint32_t count) {
    CHECK(result.calibration_finished);
    CHECK(result.calibration_rejected);
    CHECK(result.calibration_samples == count);
    CHECK(result.bias_dps == OLD_BIAS);
}

void sameResult(const ServiceResult& actual, const ServiceResult& expected) {
    CHECK(actual.bias_dps == expected.bias_dps);
    CHECK(actual.calibration_samples == expected.calibration_samples);
    CHECK(actual.calibration_finished == expected.calibration_finished);
    CHECK(actual.calibration_rejected == expected.calibration_rejected);
    CHECK(actual.line_warning == expected.line_warning);
    CHECK(actual.opponent_snapshot == expected.opponent_snapshot);
    CHECK(actual.active == expected.active);
    CHECK(actual.finished == expected.finished);
}

countdown::LifecycleResult lifeStep(countdown::Lifecycle& life,
                                    std::uint32_t time, core::ButtonLevel button,
                                    bool stop = false) {
    return life.step(absent(time), button, OLD_BIAS, stop);
}

std::uint32_t startLifecycle(countdown::Lifecycle& life, std::uint32_t base = 0U) {
    using core::ButtonLevel;
    lifeStep(life, base, ButtonLevel::NONE);
    lifeStep(life, base + DEBOUNCE, ButtonLevel::NONE);
    lifeStep(life, base + DEBOUNCE + 1U, ButtonLevel::START);
    lifeStep(life, base + 2U * DEBOUNCE + 1U, ButtonLevel::START);
    lifeStep(life, base + 2U * DEBOUNCE + 2U, ButtonLevel::NONE);
    const auto release = base + 3U * DEBOUNCE + 2U;
    const auto result = lifeStep(life, release, ButtonLevel::NONE);
    CHECK(result.gate.start_release);
    CHECK(result.gate.release_us == release);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK(result.services.active);
    return release;
}
} // namespace

TEST_CASE("B3 D083 legacy aggregate defaults preserve D024 valid-tick behavior") {
    ServiceSample defaults;
    CHECK(defaults.gyro_presence == GyroPresence::LEGACY);
    CHECK(defaults.gyro_observation_us == 0U);
    CHECK(defaults.gyro_sequence == 0U);
    Attempt attempt;
    ServiceSample first{CAL_BEGIN, 1.0F, true, 0U, 0U};
    first.gyro_observation_us = 0xffffffffU;
    first.gyro_sequence = 0xffffffffU;
    CHECK(attempt.services.step(first).calibration_samples == 1U);
    auto second = first;
    second.t_us += 1U;
    second.raw_gyro_z_dps = 3.0F;
    CHECK(attempt.services.step(second).calibration_samples == 2U);
    accepted(attempt.finish(), 2U, 2.0F);
}

TEST_CASE("B3 D083 legacy invalid imu or numeric values still reject D024") {
    for (const float raw : {1.0F, NAN_VALUE,
                            std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        Attempt attempt;
        ServiceSample sample{CAL_BEGIN, raw, raw != 1.0F, 0U, 0U};
        attempt.services.step(sample);
        sample = {CAL_BEGIN + 1U, 2.0F, true, 0U, 0U};
        attempt.services.step(sample);
        sample.t_us += 1U;
        attempt.services.step(sample);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 ABSENT ignores every gyro field without invalidating later data") {
    Attempt attempt;
    auto sample = absent(CAL_BEGIN);
    CHECK(attempt.services.step(sample).calibration_samples == 0U);
    sample.t_us += 1U;
    sample.imu_ok = true;
    sample.raw_gyro_z_dps = std::numeric_limits<float>::infinity();
    CHECK(attempt.services.step(sample).calibration_samples == 0U);
    attempt.valid(CAL_BEGIN + 2U, 0U, 1.0F);
    attempt.valid(CAL_BEGIN + 3U, 1U, 2.0F);
    accepted(attempt.finish(), 2U, 1.5F);
}

TEST_CASE("B3 D083 ABSENT-only and one distinct reading fail D024 minimum") {
    for (std::uint32_t readings = 0U; readings < config::CAL_MIN_SAMPLES; ++readings) {
        Attempt attempt;
        attempt.services.step(absent(CAL_BEGIN));
        for (std::uint32_t i = 0U; i < readings; ++i) {
            attempt.valid(CAL_BEGIN + i + 1U, i);
        }
        attempt.services.step(absent(CAL_END - 1U));
        rejected(attempt.finish(), readings);
    }
}

TEST_CASE("B3 D083 VALID ignores heading imu_ok and accepts first sequence zero") {
    Attempt attempt;
    auto sample = observation(CAL_BEGIN, CAL_BEGIN, 0U, 2.0F);
    sample.imu_ok = false;
    attempt.services.step(sample);
    sample.t_us += 1U;
    sample.gyro_observation_us += 1U;
    sample.gyro_sequence = 500U;
    sample.imu_ok = true;
    attempt.services.step(sample);
    accepted(attempt.finish(), 2U, 2.0F);
}

TEST_CASE("B3 D083 INVALID and every unknown enum reject but permit diagnostic samples") {
    for (unsigned code = 3U; code <= 255U; ++code) {
        CAPTURE(code);
        Attempt attempt;
        attempt.services.step(observation(CAL_BEGIN, CAL_BEGIN + 9U, 99U,
                                          NAN_VALUE, static_cast<GyroPresence>(code)));
        CHECK(attempt.valid(CAL_BEGIN + 1U, 0U).calibration_samples == 1U);
        CHECK(attempt.valid(CAL_BEGIN + 2U, 1U).calibration_samples == 2U);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 unknown enum does not choose legacy or explicit attempt mode") {
    for (const bool legacy : {false, true}) {
        Attempt attempt;
        attempt.services.step(observation(CAL_BEGIN, 0U, 0U, NAN_VALUE,
                                          static_cast<GyroPresence>(255U)));
        for (std::uint32_t i = 1U; i <= 2U; ++i) {
            auto sample = observation(CAL_BEGIN + i, CAL_BEGIN + i, i);
            sample.imu_ok = true;
            sample.gyro_presence = legacy ? GyroPresence::LEGACY : GyroPresence::VALID;
            attempt.services.step(sample);
        }
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 explicit statuses choose mode and mixed legacy contributes nothing") {
    for (const auto first : {GyroPresence::ABSENT, GyroPresence::VALID,
                             GyroPresence::INVALID}) {
        Attempt attempt;
        attempt.services.step(observation(CAL_BEGIN, CAL_BEGIN, 99U, 1.0F, first));
        ServiceSample mixed{CAL_BEGIN + 1U, 2.0F, true, 0U, 0U};
        const auto first_count = first == GyroPresence::VALID ? 1U : 0U;
        CHECK(attempt.services.step(mixed).calibration_samples == first_count);
        attempt.valid(CAL_BEGIN + 2U, 100U);
        attempt.valid(CAL_BEGIN + 3U, 101U);
        rejected(attempt.finish(), first_count + 2U);
    }
}

TEST_CASE("B3 D083 legacy then any explicit status rejects without adding mixed sample") {
    for (const auto mixed : {GyroPresence::ABSENT, GyroPresence::VALID,
                             GyroPresence::INVALID}) {
        Attempt attempt;
        attempt.services.step({CAL_BEGIN, 1.0F, true, 0U, 0U});
        CHECK(attempt.services.step(observation(CAL_BEGIN + 1U, CAL_BEGIN + 1U,
                                               10U, 2.0F, mixed))
                  .calibration_samples == 1U);
        attempt.services.step({CAL_BEGIN + 2U, 1.0F, true, 0U, 0U});
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 outside decision window does not validate select mode or identity") {
    Attempt attempt;
    attempt.services.step(observation(CAL_BEGIN - 3U, 0U, 0U, NAN_VALUE,
                                      static_cast<GyroPresence>(200U)));
    attempt.services.step(observation(CAL_BEGIN - 2U, 0U, 0U, NAN_VALUE,
                                      GyroPresence::INVALID));
    attempt.services.step(observation(CAL_BEGIN - 1U, CAL_BEGIN + 1U,
                                      0xffffffffU, 1.0F));
    attempt.services.step({CAL_BEGIN, 1.0F, true, 0U, 0U});
    attempt.services.step({CAL_END - 1U, 3.0F, true, 0U, 0U});
    const auto finished = attempt.services.step(observation(CAL_END, 0U, 0U,
                                                           NAN_VALUE,
                                                           GyroPresence::INVALID));
    accepted(finished, 2U, 2.0F);
    accepted(attempt.services.step(observation(CAL_END + 1U, 0U, 0U, NAN_VALUE)),
             2U, 2.0F);
}

TEST_CASE("B3 D083 exact decision endpoints and delayed CAL_END delivery") {
    SUBCASE("CAL_START and CAL_END minus one are included") {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 77U);
        attempt.valid(CAL_END - 1U, 90U, 3.0F);
        accepted(attempt.finish(), 2U, 2.0F);
    }
    SUBCASE("fresh delayed second observation at CAL_END cannot reopen window") {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 77U);
        const auto result = attempt.valid(CAL_END, 78U, 1.0F, 1U);
        rejected(result, 1U);
        rejected(attempt.valid(CAL_END + 1U, 79U), 1U);
    }
}

TEST_CASE("B3 D083 fresh pre-window source is excluded and its identity is remembered") {
    SUBCASE("pre-window source and replay do not count or reject") {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 0U, 1.0F, 1U);
        CHECK(attempt.services.step(observation(CAL_BEGIN + 1U, CAL_BEGIN - 1U,
                                               0U)).calibration_samples == 0U);
        attempt.services.step(observation(CAL_BEGIN + 2U, CAL_BEGIN, 1U));
        attempt.valid(CAL_BEGIN + 3U, 2U, 3.0F);
        accepted(attempt.finish(), 2U, 2.0F);
    }
    SUBCASE("changing sequence alone on excluded identity is still invalid") {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 0U, 1.0F, 1U);
        attempt.services.step(observation(CAL_BEGIN + 1U, CAL_BEGIN - 1U, 1U));
        attempt.valid(CAL_BEGIN + 2U, 1U);
        attempt.valid(CAL_BEGIN + 3U, 2U);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 age bound accepts equality and rejects stale future and ambiguous") {
    for (const auto age : {0U, AGE, AGE + 1U, 0xffffffffU, 0x80000000U}) {
        CAPTURE(age);
        Attempt attempt;
        attempt.valid(CAL_BEGIN + AGE, 0U, 1.0F, age);
        attempt.valid(CAL_BEGIN + AGE + 1U, 1U, 1.0F);
        attempt.valid(CAL_BEGIN + AGE + 2U, 2U, 1.0F);
        if (age <= AGE) accepted(attempt.finish(), 3U, 1.0F);
        else rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 identical replay on later ticks counts once and stale replay rejects") {
    SUBCASE("fresh duplicate includes signed-zero equality") {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 0U, 0.0F);
        attempt.services.step(observation(CAL_BEGIN + 1U, CAL_BEGIN, 0U, -0.0F));
        attempt.services.step(observation(CAL_BEGIN + AGE, CAL_BEGIN, 0U, 0.0F));
        attempt.valid(CAL_BEGIN + AGE + 1U, 3U, 2.0F);
        accepted(attempt.finish(), 2U, 1.0F);
    }
    SUBCASE("age is checked before duplicate exemption") {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 0U);
        attempt.services.step(observation(CAL_BEGIN + AGE + 1U, CAL_BEGIN, 0U));
        attempt.valid(CAL_BEGIN + AGE + 2U, 1U);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 conflicting or partial identity rejects and cannot replace identity") {
    for (unsigned kind = 0U; kind < 5U; ++kind) {
        CAPTURE(kind);
        Attempt attempt;
        attempt.valid(CAL_BEGIN + 10U, 10U);
        auto bad = observation(CAL_BEGIN + 11U, CAL_BEGIN + 10U, 10U);
        if (kind == 0U) bad.raw_gyro_z_dps = 2.0F;
        if (kind == 1U) bad.gyro_sequence = 11U;
        if (kind == 2U) bad.gyro_observation_us += 1U;
        if (kind == 3U) bad.gyro_sequence = 9U;
        if (kind == 4U) bad.gyro_observation_us -= 1U;
        CHECK(attempt.services.step(bad).calibration_samples == 1U);
        CHECK(attempt.valid(CAL_BEGIN + 12U, 11U).calibration_samples == 2U);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 sequence forward gaps half-range and reversal bounds") {
    for (const auto delta : {1U, 1000000U, 0x7fffffffU, 0x80000000U, 0xffffffffU}) {
        CAPTURE(delta);
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 0U);
        attempt.valid(CAL_BEGIN + 1U, delta);
        const bool forward = delta < 0x80000000U;
        if (forward) accepted(attempt.finish(), 2U, 1.0F);
        else rejected(attempt.finish(), 1U);
    }
}

TEST_CASE("B3 D083 source reversal rejects even when delivery age remains fresh") {
    Attempt attempt;
    attempt.valid(CAL_BEGIN + 10U, 50U);
    attempt.services.step(observation(CAL_BEGIN + 11U, CAL_BEGIN + 9U, 51U));
    attempt.valid(CAL_BEGIN + 12U, 51U);
    rejected(attempt.finish(), 2U);
}

TEST_CASE("B3 D083 source half-range or older rejects before identity commit") {
    for (const auto source_delta : {0x80000000U, 0x80000001U}) {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 50U);
        attempt.services.step(observation(CAL_BEGIN + 1U, CAL_BEGIN + source_delta, 51U));
        attempt.valid(CAL_BEGIN + 2U, 51U);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 uint32 source sequence decision and release wrap are supported") {
    Attempt attempt(0U - CAL_BEGIN - 1000U);
    attempt.valid(CAL_BEGIN, 0xfffffffeU, 1.0F);
    attempt.valid(CAL_BEGIN + 1000U, 0xffffffffU, 2.0F, 1U);
    attempt.valid(CAL_BEGIN + 1001U, 0U, 3.0F);
    accepted(attempt.finish(), 3U, 2.0F);
}

TEST_CASE("B3 D083 explicit non-finite gyro rejects without poisoning later identities") {
    for (const auto raw : {NAN_VALUE, std::numeric_limits<float>::infinity(),
                           -std::numeric_limits<float>::infinity()}) {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 100U, raw);
        attempt.valid(CAL_BEGIN + 1U, 0U);
        attempt.valid(CAL_BEGIN + 2U, 1U);
        rejected(attempt.finish(), 2U);
    }
}

TEST_CASE("B3 D083 D024 finite spread equality and immediately greater threshold") {
    for (const bool exceeds : {false, true}) {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 0U, 0.0F);
        const float high = exceeds
            ? std::nextafter(config::CAL_MAX_SPREAD_DPS,
                             std::numeric_limits<float>::infinity())
            : config::CAL_MAX_SPREAD_DPS;
        attempt.valid(CAL_BEGIN + 1U, 1U, high);
        if (exceeds) rejected(attempt.finish(), 2U);
        else accepted(attempt.finish(), 2U, high / 2.0F);
    }
}

TEST_CASE("B3 D083 duplicate decision timestamps ignore all changed fields wholly") {
    Attempt attempt;
    const auto first = attempt.valid(CAL_BEGIN, 0U);
    auto duplicate = observation(CAL_BEGIN, CAL_BEGIN + 100U, 900U, NAN_VALUE,
                                 GyroPresence::INVALID);
    duplicate.line_mask = 15U;
    duplicate.confirmed_opp_mask = 127U;
    sameResult(attempt.services.step(duplicate), first);
    attempt.valid(CAL_BEGIN + 1U, 1U);
    accepted(attempt.finish(), 2U, 1.0F);
}

TEST_CASE("B3 D083 absent observations advance warning snapshot and hold services") {
    Attempt attempt;
    attempt.services.step(absent(CAL_BEGIN));
    auto sample = absent(HOLD - config::COUNTDOWN_LINE_WARN_MS * 1000U - 1U);
    sample.line_mask = 1U;
    CHECK_FALSE(attempt.services.step(sample).line_warning);
    sample.t_us += 1U;
    CHECK(attempt.services.step(sample).line_warning);
    sample = absent(HOLD - config::COUNTDOWN_SNAPSHOT_MS * 1000U);
    sample.confirmed_opp_mask = 0xffU;
    const auto snapshot = attempt.services.step(sample);
    CHECK(snapshot.opponent_snapshot == 0x7fU);
    sample.confirmed_opp_mask = 0U;
    sameResult(attempt.services.step(sample), snapshot);
    sample.t_us += 1U;
    CHECK(attempt.services.step(sample).opponent_snapshot == 0U);
    sample.t_us = HOLD - 1U;
    sample.confirmed_opp_mask = 0x81U;
    CHECK(attempt.services.step(sample).opponent_snapshot == 1U);
    sample.t_us = HOLD;
    sample.confirmed_opp_mask = 7U;
    const auto finished = attempt.services.step(sample);
    rejected(finished, 0U);
    CHECK(finished.line_warning);
    CHECK(finished.opponent_snapshot == 1U);
    CHECK_FALSE(finished.active);
    CHECK(finished.finished);
    sameResult(attempt.services.step(observation(HOLD + 1U, HOLD + 1U, 9U)), finished);
    sameResult(attempt.services.step(absent(0xffffffffU)), finished);
}

TEST_CASE("B3 D083 start cancel reset discard modes identities and rejection state") {
    for (unsigned operation = 0U; operation < 3U; ++operation) {
        Attempt attempt;
        attempt.valid(CAL_BEGIN, 999U);
        attempt.services.step(observation(CAL_BEGIN + 1U, 0U, 0U, NAN_VALUE,
                                          GyroPresence::INVALID));
        if (operation == 0U) {
            attempt.services.cancel();
            const auto idle = attempt.services.step(absent(CAL_BEGIN + 2U));
            CHECK_FALSE(idle.active);
            CHECK_FALSE(idle.calibration_rejected);
            CHECK(idle.calibration_samples == 0U);
            CHECK(idle.bias_dps == OLD_BIAS);
        }
        if (operation == 1U) {
            attempt.services.reset();
            CHECK(attempt.services.step(absent(CAL_BEGIN + 2U)).bias_dps == 0.0F);
        }
        CHECK(attempt.services.start(0U, OLD_BIAS));
        attempt.valid(CAL_BEGIN, 0U);
        attempt.valid(CAL_BEGIN + 1U, 1U);
        accepted(attempt.finish(), 2U, 1.0F);
        CHECK(attempt.services.start(0U, OLD_BIAS));
        attempt.services.step({CAL_BEGIN, 2.0F, true, 0U, 0U});
        attempt.services.step({CAL_BEGIN + 1U, 2.0F, true, 0U, 0U});
        accepted(attempt.finish(), 2U, 2.0F);
    }
}

TEST_CASE("B3 D083 invalid start is inert and subsequent valid start clears failure") {
    countdown::Services services;
    for (const auto bias : {NAN_VALUE, std::numeric_limits<float>::infinity(),
                            -std::numeric_limits<float>::infinity()}) {
        CHECK_FALSE(services.start(0U, bias));
        const auto failed = services.step(observation(CAL_BEGIN, CAL_BEGIN, 0U));
        CHECK_FALSE(failed.active);
        CHECK(failed.calibration_rejected);
        CHECK(failed.calibration_samples == 0U);
    }
    CHECK(services.start(0U, OLD_BIAS));
    services.step(observation(CAL_BEGIN, CAL_BEGIN, 0U));
    services.step(observation(CAL_BEGIN + 1U, CAL_BEGIN + 1U, 1U));
    accepted(services.step(absent(CAL_END)), 2U, 1.0F);
}

TEST_CASE("B3 D083 fixed-seed stream averages only delivered distinct source observations") {
    Attempt attempt;
    std::uint32_t random = 0x63d083a1U;
    std::uint32_t distinct = 0U;
    std::uint32_t sequence = 0xffffff00U;
    double sum = 0.0;
    for (std::uint32_t slot = 0U; slot < 500U; ++slot) {
        random = random * 1664525U + 1013904223U;
        const auto time = CAL_BEGIN + slot * 5000U;
        if ((random & 3U) == 0U) {
            attempt.services.step(absent(time));
            continue;
        }
        sequence += 1U + ((random >> 4U) & 7U);
        const float raw = static_cast<float>((random >> 12U) & 7U) * 0.25F;
        const auto source = time + 1U;
        attempt.services.step(observation(source, source, sequence, raw));
        attempt.services.step(observation(source + 1U, source, sequence, raw));
        attempt.services.step(absent(source + 2U));
        ++distinct;
        sum += raw;
    }
    // Modulo four this LCG adds three, visiting every residue once per four
    // residue once per four slots: precisely 125 absent and 375 distinct slots.
    CHECK(distinct == 375U);
    accepted(attempt.finish(), 375U, static_cast<float>(sum / 375.0));
}

TEST_CASE("B3 D083 Lifecycle absent data never advances GO before complete qualified hold") {
    for (const auto base : {0U, 0xfffff000U}) {
        countdown::Lifecycle life;
        const auto release = startLifecycle(life, base);
        auto result = lifeStep(life, release + CAL_BEGIN, core::ButtonLevel::NONE);
        CHECK_FALSE(result.gate.motion_permitted);
        result = lifeStep(life, release + HOLD - 1U, core::ButtonLevel::NONE);
        CHECK_FALSE(result.gate.motion_permitted);
        CHECK_FALSE(result.heading_reset_requested);
        rejected(result.services, 0U);
        result = lifeStep(life, release + HOLD, core::ButtonLevel::NONE);
        CHECK(result.gate.motion_permitted);
        CHECK(result.gate.go);
        CHECK(result.heading_reset_requested);
        CHECK(result.services.finished);
        result = lifeStep(life, release + HOLD + 1U, core::ButtonLevel::NONE);
        CHECK_FALSE(result.gate.go);
        CHECK_FALSE(result.heading_reset_requested);
    }
}

TEST_CASE("B3 D083 Lifecycle consumes valid explicit gyro then retains evidence after GO STOP") {
    countdown::Lifecycle life;
    const auto release = startLifecycle(life);
    life.step(observation(release + CAL_BEGIN, release + CAL_BEGIN, 0U, 2.0F),
              core::ButtonLevel::NONE, NAN_VALUE);
    life.step(observation(release + CAL_BEGIN + 1U, release + CAL_BEGIN + 1U, 1U, 3.0F),
              core::ButtonLevel::NONE, NAN_VALUE);
    auto result = lifeStep(life, release + HOLD, core::ButtonLevel::NONE);
    accepted(result.services, 2U, 2.5F);
    CHECK(result.gate.go);
    const auto completed = result.services;
    result = lifeStep(life, release + HOLD + 1U, core::ButtonLevel::NONE, true);
    CHECK(result.gate.phase == countdown::Phase::STOPPED);
    CHECK_FALSE(result.gate.motion_permitted);
    sameResult(result.services, completed);
}

TEST_CASE("B3 D083 Lifecycle MODE cancellation clears pending admission before its sample") {
    countdown::Lifecycle life;
    const auto release = startLifecycle(life);
    life.step(observation(release + CAL_BEGIN, release + CAL_BEGIN, 50U),
              core::ButtonLevel::NONE, OLD_BIAS);
    lifeStep(life, release + CAL_BEGIN + 1U, core::ButtonLevel::MODE);
    const auto time = release + CAL_BEGIN + 1U + DEBOUNCE;
    const auto cancelled = life.step(observation(time, time, 51U),
                                     core::ButtonLevel::MODE, OLD_BIAS);
    CHECK(cancelled.gate.phase == countdown::Phase::IDLE);
    CHECK_FALSE(cancelled.gate.motion_permitted);
    CHECK_FALSE(cancelled.services.active);
    CHECK(cancelled.services.calibration_samples == 0U);
    CHECK_FALSE(cancelled.services.calibration_rejected);
    CHECK(cancelled.services.bias_dps == OLD_BIAS);
    const auto new_release = startLifecycle(life, time + 1U);
    life.step(observation(new_release + CAL_BEGIN, new_release + CAL_BEGIN, 0U),
              core::ButtonLevel::NONE, OLD_BIAS);
    life.step(observation(new_release + CAL_BEGIN + 1U, new_release + CAL_BEGIN + 1U, 1U),
              core::ButtonLevel::NONE, OLD_BIAS);
    accepted(lifeStep(life, new_release + CAL_END, core::ButtonLevel::NONE).services,
             2U, 1.0F);
}

TEST_CASE("B3 D083 Lifecycle STOP at calibration or GO deadline cancels before admission") {
    for (const auto elapsed : {CAL_BEGIN + 1U, CAL_END, HOLD}) {
        countdown::Lifecycle life;
        const auto release = startLifecycle(life);
        life.step(observation(release + CAL_BEGIN, release + CAL_BEGIN, 50U),
                  core::ButtonLevel::NONE, OLD_BIAS);
        const auto time = release + elapsed;
        const auto stopped = life.step(observation(time, time, 51U),
                                        core::ButtonLevel::NONE, OLD_BIAS, true);
        CHECK(stopped.gate.phase == countdown::Phase::STOPPED);
        CHECK_FALSE(stopped.gate.motion_permitted);
        CHECK_FALSE(stopped.gate.go);
        CHECK_FALSE(stopped.services.active);
        CHECK(stopped.services.calibration_samples == 0U);
        CHECK_FALSE(stopped.heading_reset_requested);
        CHECK_FALSE(lifeStep(life, time + HOLD, core::ButtonLevel::NONE)
                        .gate.motion_permitted);
        life.reset();
        const auto restarted = startLifecycle(life, time + HOLD + 1U);
        CHECK_FALSE(lifeStep(life, restarted + HOLD - 1U, core::ButtonLevel::NONE)
                        .gate.motion_permitted);
    }
}

TEST_CASE("B3 D083 absent gyro does not stall logical BOTH STOP qualification") {
    countdown::Lifecycle life;
    const auto release = startLifecycle(life);
    const auto both = release + CAL_BEGIN;
    lifeStep(life, both, core::ButtonLevel::BOTH);
    lifeStep(life, both + DEBOUNCE, core::ButtonLevel::BOTH);
    const auto deadline = both + DEBOUNCE + config::BTN_LONG_MS * 1000U;
    auto result = lifeStep(life, deadline - 1U, core::ButtonLevel::BOTH);
    CHECK(result.gate.phase != countdown::Phase::STOPPED);
    result = lifeStep(life, deadline, core::ButtonLevel::BOTH);
    CHECK(result.gate.phase == countdown::Phase::STOPPED);
    CHECK_FALSE(result.gate.motion_permitted);
    CHECK_FALSE(result.services.active);
    CHECK(result.services.calibration_samples == 0U);
}
