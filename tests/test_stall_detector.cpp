// Checks B11.1/D-032 qualified timer-or-deflection stall inference.
// Separates contact and edge history from timer qualification and D-025 suppression.
// Run with tools/test_host.sh; spec boundaries and unwrapped reference traces are covered.
#include "doctest.h"
#include "config.h"
#include "core/stall.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint32_t STALL_US = config::STALL_MS * 1000U;
constexpr float NAN_VALUE = std::numeric_limits<float>::quiet_NaN();
constexpr float INFINITY_VALUE = std::numeric_limits<float>::infinity();

stall::Sample qualifiedSample(std::uint32_t t_us = 0U) {
    stall::Sample sample;
    sample.t_us = t_us;
    sample.state = core::State::ATTACK;
    sample.centered = sample.contact = true;
    sample.duty_l = sample.duty_r = config::STALL_MIN_DUTY;
    sample.imu_ok = true;
    return sample;
}

void checkDetection(const stall::Detection& result, bool qualified, bool timer,
                    bool deflection, bool stalled) {
    CHECK(result.qualified == qualified);
    CHECK(result.timer_trigger == timer);
    CHECK(result.deflection_trigger == deflection);
    CHECK(result.stalled == stalled);
}

std::uint32_t nextRandom(std::uint32_t& state) {
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

void checkTimerTrace(std::uint32_t& random, unsigned trace) {
    CAPTURE(trace);
    stall::Detector detector;
    std::uint64_t now = 0x100000000ULL - nextRandom(random) % STALL_US;
    std::uint64_t qualified_since = 0U;
    bool has_qualified_since = false;
    bool edge_since_contact = false;
    const std::uint32_t gaps[] = {0U, 1U, 999U, 1000U, STALL_US - 1U,
                                  STALL_US, STALL_US + 1U, 0xFFFFFFFFU};
    for (unsigned index = 0U; index < 128U; ++index) {
        CAPTURE(index);
        const auto draw = nextRandom(random);
        now += gaps[(draw >> 8U) & 7U];
        auto sample = qualifiedSample(static_cast<std::uint32_t>(now));
        sample.imu_ok = false;
        sample.contact_started = index == 0U || (draw & 7U) == 0U;
        sample.edge_event = (draw & 31U) == 31U;
        sample.centered = (draw & 2U) != 0U;
        sample.duty_r = (draw & 4U) != 0U ? 1.0F : 0.0F;
        sample.suppress = (draw & 64U) != 0U;
        if (sample.contact_started) {
            edge_since_contact = false;
            has_qualified_since = false;
        }
        edge_since_contact = edge_since_contact || sample.edge_event;
        const bool qualified = sample.centered && sample.duty_r == 1.0F &&
                               !edge_since_contact;
        if (!qualified) has_qualified_since = false;
        if (qualified && !has_qualified_since) {
            qualified_since = now;
            has_qualified_since = true;
        }
        const bool timer = qualified && now - qualified_since >= STALL_US;
        checkDetection(detector.step(sample), qualified, timer, false,
                       timer && !sample.suppress);
    }
}
} // namespace

TEST_CASE("B11.1 stall sample and detection defaults are inert") {
    const stall::Sample sample;
    const stall::Detection result;
    stall::Detector detector;
    checkDetection(result, false, false, false, false);
    checkDetection(detector.step(sample), false, false, false, false);
    CHECK(sample.state == core::State::IDLE);
    CHECK_FALSE(sample.contact);
    CHECK_FALSE(sample.contact_started);
    CHECK_FALSE(sample.edge_event);
    CHECK(config::STALL_USE_IMU == 0U);
}

TEST_CASE("B11.1 timer triggers at exactly one second of continuous qualification as a level") {
    stall::Detector detector;
    auto sample = qualifiedSample(1234U);
    checkDetection(detector.step(sample), true, false, false, false);
    for (auto elapsed : {STALL_US - 1000U, STALL_US - 1U}) {
        sample.t_us = 1234U + elapsed;
        checkDetection(detector.step(sample), true, false, false, false);
    }
    for (auto elapsed : {STALL_US, STALL_US + 1U, STALL_US + 1000U}) {
        sample.t_us = 1234U + elapsed;
        checkDetection(detector.step(sample), true, true, false, true);
    }
}

TEST_CASE("B11.1 deflection is strictly above 25 degrees in either sign") {
    CHECK(config::STALL_DEFLECT_DEG == 25U);
    const float values[] = {std::nextafter(25.0F, 0.0F), 25.0F,
                            std::nextafter(25.0F, INFINITY_VALUE)};
    for (float sign : {-1.0F, 1.0F}) {
        for (float angle : values) {
            stall::Detector detector;
            auto sample = qualifiedSample();
            detector.step(sample);
            sample.t_us = 1U;
            sample.heading_deg = sign * angle;
            const bool triggered = angle > 25.0F;
            checkDetection(detector.step(sample), true, false, triggered, triggered);
        }
    }
}

TEST_CASE("B11.1 contact deflection uses continuous yaw without wrapping full revolutions") {
    for (float origin : {-720.0F, 0.0F, 359.0F, 720.0F}) {
        for (float change : {-720.0F, -360.0F, -26.0F, 26.0F, 360.0F, 720.0F}) {
            stall::Detector detector;
            auto sample = qualifiedSample();
            sample.heading_deg = origin;
            detector.step(sample);
            sample.t_us = 1U;
            sample.heading_deg = origin + change;
            checkDetection(detector.step(sample), true, false, true, true);
        }
    }
}

TEST_CASE("B11.1 both final forward duties must be finite and within inclusive 0.8 to 1") {
    const float values[] = {0.0F, -0.80F, std::nextafter(0.80F, 0.0F), 0.80F,
        std::nextafter(0.80F, 1.0F), 1.0F, std::nextafter(1.0F, 2.0F),
        NAN_VALUE, INFINITY_VALUE, -INFINITY_VALUE};
    for (unsigned side = 0U; side < 2U; ++side) {
        for (float duty : values) {
            stall::Detector detector;
            auto sample = qualifiedSample();
            detector.step(sample);
            sample.t_us = STALL_US;
            sample.heading_deg = 26.0F;
            if (side == 0U) sample.duty_l = duty;
            else sample.duty_r = duty;
            const bool qualified = std::isfinite(duty) && duty >= 0.80F && duty <= 1.0F;
            checkDetection(detector.step(sample), qualified, qualified, qualified, qualified);
        }
    }
}

TEST_CASE("B11.1 both stall routes require centered ATTACK contact including valid state") {
    for (unsigned state = 0U; state <= 255U; ++state) {
        if (state == static_cast<unsigned>(core::State::ATTACK)) continue;
        stall::Detector detector;
        auto sample = qualifiedSample();
        detector.step(sample);
        sample.t_us = STALL_US;
        sample.heading_deg = 26.0F;
        sample.state = static_cast<core::State>(state);
        checkDetection(detector.step(sample), false, false, false, false);
    }
    for (unsigned missing = 0U; missing < 2U; ++missing) {
        stall::Detector detector;
        auto sample = qualifiedSample();
        detector.step(sample);
        sample.t_us = STALL_US;
        sample.heading_deg = 26.0F;
        if (missing == 0U) sample.centered = false;
        else sample.contact = false;
        checkDetection(detector.step(sample), false, false, false, false);
    }
}

TEST_CASE("B11.1 interrupted qualification resets the timer while retaining contact heading") {
    for (unsigned interruption = 0U; interruption < 2U; ++interruption) {
        stall::Detector detector;
        auto sample = qualifiedSample();
        detector.step(sample);
        sample.t_us = STALL_US - 1U;
        if (interruption == 0U) sample.centered = false;
        else sample.duty_l = 0.0F;
        checkDetection(detector.step(sample), false, false, false, false);
        sample = qualifiedSample(STALL_US);
        checkDetection(detector.step(sample), true, false, false, false);
        sample.t_us = 2U * STALL_US - 1U;
        checkDetection(detector.step(sample), true, false, false, false);
        sample.t_us = 2U * STALL_US;
        checkDetection(detector.step(sample), true, true, false, true);
        sample.t_us += 1U;
        sample.heading_deg = 26.0F;
        checkDetection(detector.step(sample), true, true, true, true);
    }
}

TEST_CASE("B11.1 an edge remains recorded through failed qualification for the same contact") {
    stall::Detector detector;
    auto sample = qualifiedSample();
    detector.step(sample);
    sample.t_us = 1000U;
    sample.edge_event = true;
    sample.centered = false;
    sample.duty_l = 0.0F;
    checkDetection(detector.step(sample), false, false, false, false);
    sample.edge_event = false;
    sample.t_us = 2000U;
    checkDetection(detector.step(sample), false, false, false, false);
    sample = qualifiedSample(3000U);
    sample.heading_deg = 100.0F;
    checkDetection(detector.step(sample), false, false, false, false);
    sample.t_us += 2U * STALL_US;
    checkDetection(detector.step(sample), false, false, false, false);
}

TEST_CASE("B11.1 fresh contact resets timer edge and heading but a same-tick edge still vetoes") {
    stall::Detector detector;
    auto sample = qualifiedSample();
    detector.step(sample);
    sample.t_us = STALL_US;
    checkDetection(detector.step(sample), true, true, false, true);
    sample.contact_started = true;
    sample.heading_deg = 100.0F;
    checkDetection(detector.step(sample), true, false, false, false);
    sample.t_us += 1U;
    sample.edge_event = true;
    checkDetection(detector.step(sample), false, false, false, false);
    sample.contact_started = sample.edge_event = false;
    sample.t_us += STALL_US;
    sample.heading_deg = 150.0F;
    checkDetection(detector.step(sample), false, false, false, false);
    sample.contact = false;
    sample.t_us += 1U;
    checkDetection(detector.step(sample), false, false, false, false);
    sample.contact = true; // Missing rising flag is inferred from contact entry.
    sample.t_us += 1U;
    sample.heading_deg = 1000.0F;
    checkDetection(detector.step(sample), true, false, false, false);
    sample.t_us += 1U;
    sample.heading_deg = 1026.0F;
    checkDetection(detector.step(sample), true, false, true, true);
}

TEST_CASE("B11.1 missing contact-start IMU anchor cannot be invented from later headings") {
    for (unsigned missing = 0U; missing < 3U; ++missing) {
        stall::Detector detector;
        auto sample = qualifiedSample();
        if (missing == 0U) sample.imu_ok = false;
        if (missing == 1U) sample.heading_deg = NAN_VALUE;
        if (missing == 2U) sample.heading_deg = INFINITY_VALUE;
        checkDetection(detector.step(sample), true, false, false, false);
        sample = qualifiedSample(1000U);
        sample.heading_deg = 1000.0F;
        checkDetection(detector.step(sample), true, false, false, false);
        sample.t_us = STALL_US;
        checkDetection(detector.step(sample), true, true, false, true);
        sample.contact_started = true;
        sample.t_us += 1000U;
        checkDetection(detector.step(sample), true, false, false, false);
        sample.contact_started = false;
        sample.t_us += 1000U;
        sample.heading_deg = 1026.0F;
        checkDetection(detector.step(sample), true, false, true, true);
    }
}

TEST_CASE("B11.1 missing current IMU disables deflection while timer qualification continues") {
    for (unsigned missing = 0U; missing < 3U; ++missing) {
        stall::Detector detector;
        auto sample = qualifiedSample();
        detector.step(sample);
        sample.t_us = 1000U;
        sample.heading_deg = 26.0F;
        if (missing == 0U) sample.imu_ok = false;
        if (missing == 1U) sample.heading_deg = NAN_VALUE;
        if (missing == 2U) sample.heading_deg = INFINITY_VALUE;
        checkDetection(detector.step(sample), true, false, false, false);
        sample.t_us = STALL_US;
        checkDetection(detector.step(sample), true, true, false, true);
        sample.imu_ok = true;
        sample.heading_deg = 26.0F;
        sample.t_us += 1U;
        checkDetection(detector.step(sample), true, true, true, true);
    }
}

TEST_CASE("B11.1/B11.3 ALL_IN suppression retains qualification diagnostics and actual history") {
    stall::Detector detector;
    auto sample = qualifiedSample();
    sample.suppress = true;
    checkDetection(detector.step(sample), true, false, false, false);
    sample.t_us = STALL_US - 1U;
    sample.heading_deg = 26.0F;
    checkDetection(detector.step(sample), true, false, true, false);
    sample.t_us = STALL_US;
    checkDetection(detector.step(sample), true, true, true, false);
    sample.suppress = false;
    sample.t_us += 1U;
    checkDetection(detector.step(sample), true, true, true, true);
    sample.suppress = true;
    sample.edge_event = true;
    sample.t_us += 1U;
    checkDetection(detector.step(sample), false, false, false, false);
    sample.suppress = sample.edge_event = false;
    sample.t_us += STALL_US;
    checkDetection(detector.step(sample), false, false, false, false);
}

TEST_CASE("B0/B11.1 delayed observations and cumulative micros wraps preserve timer thresholds") {
    for (auto elapsed : {STALL_US - 1U, STALL_US, STALL_US + 1U, 0xFFFFFFFFU}) {
        stall::Detector detector;
        const std::uint64_t origin = 0x100000000ULL - 100U;
        auto sample = qualifiedSample(static_cast<std::uint32_t>(origin));
        detector.step(sample);
        sample.t_us = static_cast<std::uint32_t>(origin + elapsed);
        const bool triggered = elapsed >= STALL_US;
        checkDetection(detector.step(sample), true, triggered, false, triggered);
    }
    stall::Detector detector;
    auto sample = qualifiedSample();
    detector.step(sample);
    std::uint64_t now = 0U;
    for (unsigned wrap = 0U; wrap < 4U; ++wrap) {
        now += 0xFFFFFFFFU; // Every gap remains strictly below one complete wrap.
        sample.t_us = static_cast<std::uint32_t>(now);
        checkDetection(detector.step(sample), true, true, false, true);
        now += 1U;
        sample.t_us = static_cast<std::uint32_t>(now);
        checkDetection(detector.step(sample), true, true, false, true);
    }
}

TEST_CASE("B11.1 reset clears timer contact heading and retained edge history") {
    for (unsigned history = 0U; history < 3U; ++history) {
        stall::Detector detector;
        auto sample = qualifiedSample(0xFFFFFF00U);
        sample.heading_deg = 1000.0F;
        detector.step(sample);
        sample.t_us += STALL_US;
        if (history == 1U) sample.edge_event = true;
        if (history == 2U) sample.heading_deg = 1100.0F;
        detector.step(sample);
        detector.reset();
        sample = qualifiedSample(0U);
        checkDetection(detector.step(sample), true, false, false, false);
        sample.t_us = STALL_US - 1U;
        checkDetection(detector.step(sample), true, false, false, false);
        sample.t_us = STALL_US;
        checkDetection(detector.step(sample), true, true, false, true);
    }
}

TEST_CASE("B0/B11.1 qualified timer traces agree with independent absolute-time history") {
    std::uint32_t random = 0xB111D032U;
    for (unsigned trace = 0U; trace < 500U; ++trace)
        checkTimerTrace(random, trace);
}
