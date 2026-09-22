// Checks the D-017 approved B6 envelope on final electrical duties.
// Separates governor arithmetic from future FSM profile choice and hardware writes.
// Run with tools/test_host.sh; expectations come from B6 and governor.h only.
#include "doctest.h"
#include "config.h"
#include "core/governor.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
governor::Request request(governor::Profile profile, float left = 1.0F,
                           float right = 1.0F, float vbat = config::V_NOM_V) {
    governor::Request result;
    result.duty_l = left;
    result.duty_r = right;
    result.vbat_v = vbat;
    result.profile = profile;
    result.centered = true;
    result.contact = true;
    result.inhibited = false;
    return result;
}

void checkZero(const governor::Result& result) {
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
}

void checkProfile(governor::Profile profile, float cap, float sign_l, float sign_r) {
    for (float vbat : {9.0F, 11.1F, 12.6F}) {
        CAPTURE(vbat);
        governor::Governor governor;
        const auto input = request(profile, sign_l, sign_r, vbat);
        checkZero(governor.step(0U, input));
        const auto result = governor.step(100000U, input);
        const float compensated = config::V_NOM_V / vbat;
        const float expected = compensated < cap ? compensated : cap;
        CHECK(result.valid);
        CHECK(result.duty_l == doctest::Approx(sign_l * expected));
        CHECK(result.duty_r == doctest::Approx(sign_r * expected));
        CHECK(std::fabs(result.duty_l) <= cap);
        CHECK(std::fabs(result.duty_r) <= cap);
    }
}
} // namespace

TEST_CASE("B6 default Request is inhibited and Result duties are zero") {
    const governor::Request input;
    const governor::Result result;
    CHECK(input.inhibited);
    CHECK_FALSE(input.centered);
    CHECK_FALSE(input.contact);
    CHECK_FALSE(input.brake);
    CHECK(input.duty_l == 0.0F);
    CHECK(input.duty_r == 0.0F);
    CHECK(input.vbat_v == 0.0F);
    checkZero(result);
    CHECK(result.filtered_vbat_v == 0.0F);
    CHECK(result.valid);
}

TEST_CASE("B6 SEARCH forward cap remains final electrical duty at 9 11.1 and 12.6 V") {
    checkProfile(governor::Profile::SEARCH_FORWARD, config::SEARCH_DUTY_MAX, 1.0F, 1.0F);
}

TEST_CASE("B6 PIVOT cap applies to both opposing sides at 9 11.1 and 12.6 V") {
    checkProfile(governor::Profile::PIVOT, config::TURN_DUTY, 1.0F, -1.0F);
}

TEST_CASE("B6 OPENER cap cannot become full duty through low voltage compensation") {
    checkProfile(governor::Profile::OPENER, config::OPENER_DUTY_MAX, 1.0F, 1.0F);
}

TEST_CASE("B6 centered contact ATTACK permits its final cap at 9 11.1 and 12.6 V") {
    checkProfile(governor::Profile::ATTACK, config::ATTACK_DUTY, 1.0F, 1.0F);
}

TEST_CASE("B6 EDGE reverse cap applies at 9 11.1 and 12.6 V") {
    checkProfile(governor::Profile::EDGE_REVERSE, config::EDGE_BACK_DUTY, -1.0F, -1.0F);
}

TEST_CASE("B6 REFLANK back cap applies at 9 11.1 and 12.6 V") {
    checkProfile(governor::Profile::REFLANK_BACK, config::REFLANK_BACK_DUTY, -1.0F, -1.0F);
}

TEST_CASE("B6 REFLANK turn cap applies at 9 11.1 and 12.6 V") {
    checkProfile(governor::Profile::REFLANK_TURN, config::TURN_DUTY, -1.0F, 1.0F);
}

TEST_CASE("B6 first call establishes time with zero acceleration budget at any timestamp") {
    for (auto now : {0U, 9000000U, 0xFFFFFFFFU}) {
        governor::Governor governor;
        const auto input = request(governor::Profile::ATTACK);
        const auto first = governor.step(now, input);
        checkZero(first);
        CHECK(first.filtered_vbat_v == config::V_NOM_V);
        checkZero(governor.step(now, input));
        CHECK(governor.step(now + 1000U, input).duty_l ==
              doctest::Approx(config::SLEW_DUTY_PER_MS));
    }
}

TEST_CASE("B6 voltage compensation scales sub-cap requests before final envelope") {
    for (float vbat : {9.0F, 11.1F, 12.6F}) {
        governor::Governor governor;
        const auto input = request(governor::Profile::PIVOT, 0.10F, -0.20F, vbat);
        governor.step(0U, input);
        const auto result = governor.step(100000U, input);
        CHECK(result.duty_l == doctest::Approx(0.10F * 11.1F / vbat));
        CHECK(result.duty_r == doctest::Approx(-0.20F * 11.1F / vbat));
    }
}

TEST_CASE("B6 compensation denominator has a 9 V floor at exact and adjacent values") {
    for (float vbat : {-5.0F, 0.0F, 8.999F, 9.0F, 9.001F}) {
        governor::Governor governor;
        const auto input = request(governor::Profile::SEARCH_FORWARD, 0.1F, 0.1F, vbat);
        governor.step(0U, input);
        const auto result = governor.step(100000U, input);
        const float denominator = vbat < config::VBAT_MIN_COMP_V ? config::VBAT_MIN_COMP_V : vbat;
        CHECK(result.valid);
        CHECK(result.duty_l == doctest::Approx(0.1F * config::V_NOM_V / denominator));
        CHECK(result.duty_r == doctest::Approx(result.duty_l));
    }
}

TEST_CASE("B6 ATTACK full duty requires both centered and contact for all four combinations") {
    for (unsigned flags = 0; flags < 4; ++flags) {
        governor::Governor governor;
        auto input = request(governor::Profile::ATTACK, 1.0F, 1.0F, 9.0F);
        input.centered = (flags & 1U) != 0U;
        input.contact = (flags & 2U) != 0U;
        governor.step(0U, input);
        const auto result = governor.step(100000U, input);
        const float expected = flags == 3U ? config::ATTACK_DUTY : config::ATTACK_APPROACH_DUTY;
        CHECK(result.duty_l == doctest::Approx(expected));
        CHECK(result.duty_r == doctest::Approx(expected));
    }
}

TEST_CASE("B6 losing centering or contact reduces ATTACK cap immediately with no time budget") {
    for (unsigned loss = 0; loss < 2; ++loss) {
        governor::Governor governor;
        auto input = request(governor::Profile::ATTACK, 1.0F, 1.0F, 9.0F);
        governor.step(0U, input);
        CHECK(governor.step(100000U, input).duty_l == 1.0F);
        if (loss == 0U) input.centered = false;
        else input.contact = false;
        const auto reduced = governor.step(100000U, input);
        CHECK(reduced.duty_l == config::ATTACK_APPROACH_DUTY);
        CHECK(reduced.duty_r == config::ATTACK_APPROACH_DUTY);
        input.centered = input.contact = true;
        CHECK(governor.step(101000U, input).duty_l ==
              doctest::Approx(config::ATTACK_APPROACH_DUTY + config::SLEW_DUTY_PER_MS));
    }
}

TEST_CASE("B6 acceleration slew uses elapsed microseconds at 999 1000 and 1001 us") {
    for (auto elapsed : {999U, 1000U, 1001U}) {
        governor::Governor governor;
        const auto input = request(governor::Profile::PIVOT, 1.0F, -1.0F, 9.0F);
        governor.step(0U, input);
        const auto result = governor.step(elapsed, input);
        const float expected = config::SLEW_DUTY_PER_MS * (static_cast<float>(elapsed) / 1000.0F);
        CHECK(result.duty_l == doctest::Approx(expected));
        CHECK(result.duty_r == doctest::Approx(-expected));
    }
}

TEST_CASE("B6 low voltage acceleration stays within final electrical slew on every tick") {
    governor::Governor governor;
    const auto input = request(governor::Profile::PIVOT, 1.0F, -1.0F, 9.0F);
    auto previous = governor.step(0U, input);
    for (std::uint32_t tick = 1; tick <= 100; ++tick) {
        const auto result = governor.step(tick * 1000U, input);
        CHECK(result.duty_l >= previous.duty_l);
        CHECK(result.duty_l - previous.duty_l <= config::SLEW_DUTY_PER_MS + 0.000001F);
        CHECK(previous.duty_r - result.duty_r <= config::SLEW_DUTY_PER_MS + 0.000001F);
        CHECK(result.duty_r == doctest::Approx(-result.duty_l));
        CHECK(result.duty_l <= config::TURN_DUTY);
        previous = result;
    }
    CHECK(previous.duty_l == config::TURN_DUTY);
}

TEST_CASE("B6 lower profile cap takes effect immediately from previously higher output") {
    governor::Governor governor;
    auto input = request(governor::Profile::ATTACK, 1.0F, 1.0F, 9.0F);
    governor.step(0U, input);
    CHECK(governor.step(100000U, input).duty_l == 1.0F);
    input.profile = governor::Profile::SEARCH_FORWARD;
    const auto lower = governor.step(100000U, input);
    CHECK(lower.duty_l == config::SEARCH_DUTY_MAX);
    CHECK(lower.duty_r == config::SEARCH_DUTY_MAX);
    input.profile = governor::Profile::ATTACK;
    CHECK(governor.step(101000U, input).duty_l ==
          doctest::Approx(config::SEARCH_DUTY_MAX + config::SLEW_DUTY_PER_MS));
}

TEST_CASE("B6 requested magnitude reduction and zero braking are immediate per side") {
    governor::Governor governor;
    auto input = request(governor::Profile::PIVOT, 0.8F, -0.8F);
    governor.step(0U, input);
    governor.step(100000U, input);
    input.duty_l = 0.2F;
    input.duty_r = 0.0F;
    const auto braking = governor.step(100000U, input);
    CHECK(braking.duty_l == doctest::Approx(0.2F));
    CHECK(braking.duty_r == 0.0F);
}

TEST_CASE("B6 explicit brake immediately zeros both sides and clears previous duty") {
    governor::Governor governor;
    auto input = request(governor::Profile::PIVOT, 1.0F, -1.0F);
    governor.step(0U, input);
    governor.step(100000U, input);
    input.brake = true;
    checkZero(governor.step(100000U, input));
    input.brake = false;
    checkZero(governor.step(100000U, input));
    const auto again = governor.step(101000U, input);
    CHECK(again.duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
    CHECK(again.duty_r == doctest::Approx(-config::SLEW_DUTY_PER_MS));
}

TEST_CASE("B6 inhibit zeros output immediately and resuming cannot restore old duty") {
    governor::Governor governor;
    auto input = request(governor::Profile::ATTACK);
    governor.step(0U, input);
    governor.step(100000U, input);
    input.inhibited = true;
    checkZero(governor.step(100000U, input));
    checkZero(governor.step(200000U, input));
    input.inhibited = false;
    checkZero(governor.step(200000U, input));
    CHECK(governor.step(201000U, input).duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
}

TEST_CASE("B6 reversal brakes the reversing side first while the other side is independent") {
    governor::Governor governor;
    auto input = request(governor::Profile::PIVOT, 0.8F, 0.8F);
    governor.step(0U, input);
    governor.step(100000U, input);
    input.duty_l = -0.8F;
    const auto reversed = governor.step(200000U, input);
    CHECK(reversed.duty_l == 0.0F);
    CHECK(reversed.duty_r == doctest::Approx(0.8F));
    const auto next = governor.step(201000U, input);
    CHECK(next.duty_l == doctest::Approx(-config::SLEW_DUTY_PER_MS));
    CHECK(next.duty_r == doctest::Approx(0.8F));
    input.duty_r = -0.8F;
    CHECK(governor.step(202000U, input).duty_r == 0.0F);
}

TEST_CASE("B0/B6 slew elapsed time survives micros rollover") {
    governor::Governor governor;
    const auto input = request(governor::Profile::ATTACK);
    constexpr std::uint32_t origin = 0xFFFFFFFFU - 500U;
    checkZero(governor.step(origin, input));
    CHECK(governor.step(origin + 1000U, input).duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
    CHECK(governor.step(origin + 2000U, input).duty_l ==
          doctest::Approx(2.0F * config::SLEW_DUTY_PER_MS));
}

TEST_CASE("B6 battery first-order lag has the contracted one-second backward-Euler response") {
    governor::Governor governor;
    auto input = request(governor::Profile::SEARCH_FORWARD, 0.0F, 0.0F, 9.0F);
    CHECK(governor.step(0U, input).filtered_vbat_v == 9.0F);
    input.vbat_v = 12.6F;
    const auto tau_us = config::VBAT_FILTER_MS * 1000U;
    CHECK(governor.step(tau_us, input).filtered_vbat_v == doctest::Approx(10.8F));
    CHECK(governor.step(2U * tau_us, input).filtered_vbat_v == doctest::Approx(11.7F));
    input.vbat_v = 9.0F;
    CHECK(governor.step(3U * tau_us, input).filtered_vbat_v == doctest::Approx(10.35F));
}

TEST_CASE("B6 battery lag stays bounded monotonic and reaches the analytic 1 kHz response") {
    governor::Governor governor;
    auto input = request(governor::Profile::SEARCH_FORWARD, 0.0F, 0.0F, 9.0F);
    auto previous = governor.step(0U, input);
    input.vbat_v = 12.6F;
    for (std::uint32_t tick = 1; tick <= 1000; ++tick) {
        const auto result = governor.step(tick * 1000U, input);
        CHECK(result.filtered_vbat_v >= previous.filtered_vbat_v);
        CHECK(result.filtered_vbat_v <= 12.6F);
        previous = result;
    }
    const double retention = static_cast<double>(config::VBAT_FILTER_MS) /
                             (config::VBAT_FILTER_MS + 1.0);
    const double expected = 12.6 - 3.6 * std::pow(retention, 1000);
    CHECK(previous.filtered_vbat_v == doctest::Approx(expected).epsilon(0.00001));
}

TEST_CASE("B6 filtering continues while inhibited without producing motion") {
    governor::Governor governor;
    auto input = request(governor::Profile::ATTACK, 1.0F, 1.0F, 9.0F);
    input.inhibited = true;
    checkZero(governor.step(0U, input));
    input.vbat_v = 12.6F;
    const auto result = governor.step(config::VBAT_FILTER_MS * 1000U, input);
    checkZero(result);
    CHECK(result.filtered_vbat_v == doctest::Approx(10.8F));
}

TEST_CASE("B6 changing battery voltage cannot bypass final cap or acceleration slew") {
    governor::Governor governor;
    auto input = request(governor::Profile::SEARCH_FORWARD, 0.25F, 0.25F, 12.6F);
    auto previous = governor.step(0U, input);
    for (std::uint32_t tick = 1; tick <= 2000; ++tick) {
        input.vbat_v = tick < 1000U ? 9.0F : 12.6F;
        const auto result = governor.step(tick * 1000U, input);
        CHECK(result.duty_l <= config::SEARCH_DUTY_MAX);
        CHECK(result.duty_l - previous.duty_l <= config::SLEW_DUTY_PER_MS + 0.000001F);
        CHECK(result.duty_l >= 0.0F);
        CHECK(result.duty_r == result.duty_l);
        previous = result;
    }
}

TEST_CASE("B6 reset discards duty history time and prior battery state") {
    governor::Governor governor;
    auto input = request(governor::Profile::ATTACK, 1.0F, 1.0F, 9.0F);
    governor.step(0U, input);
    governor.step(100000U, input);
    governor.reset();
    input.vbat_v = 12.6F;
    const auto first = governor.step(0U, input);
    checkZero(first);
    CHECK(first.filtered_vbat_v == 12.6F);
    CHECK(governor.step(1000U, input).duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
}

TEST_CASE("B6 nonfinite voltage or either requested duty immediately returns invalid zero output") {
    const float bad[] = {std::numeric_limits<float>::quiet_NaN(),
                         std::numeric_limits<float>::infinity(),
                         -std::numeric_limits<float>::infinity()};
    for (float value : bad) {
        for (unsigned field = 0; field < 3; ++field) {
            governor::Governor governor;
            auto input = request(governor::Profile::ATTACK);
            governor.step(0U, input);
            governor.step(100000U, input);
            if (field == 0U) input.duty_l = value;
            if (field == 1U) input.duty_r = value;
            if (field == 2U) input.vbat_v = value;
            const auto result = governor.step(101000U, input);
            CHECK_FALSE(result.valid);
            checkZero(result);
            CHECK(std::isfinite(result.filtered_vbat_v));
        }
    }
}

TEST_CASE("B6 unknown profile is rejected with zero output even after prior valid duty") {
    governor::Governor governor;
    auto input = request(governor::Profile::ATTACK);
    governor.step(0U, input);
    governor.step(100000U, input);
    input.profile = static_cast<governor::Profile>(255U);
    const auto result = governor.step(101000U, input);
    CHECK_FALSE(result.valid);
    checkZero(result);
}

TEST_CASE("B6 large finite request magnitudes remain finite and inside the selected cap") {
    for (float demand : {-100.0F, -1.0F, 0.0F, 1.0F, 100.0F}) {
        governor::Governor governor;
        const auto input = request(governor::Profile::PIVOT, demand, -demand, 9.0F);
        governor.step(0U, input);
        const auto result = governor.step(100000U, input);
        CHECK(std::isfinite(result.duty_l));
        CHECK(std::isfinite(result.duty_r));
        CHECK(std::fabs(result.duty_l) <= config::TURN_DUTY);
        CHECK(std::fabs(result.duty_r) <= config::TURN_DUTY);
    }
}
