// Checks B5.1 electrical polarity and seven independent opponent hysteresis channels.
// Keeps confirmed samples distinct from later bearing memory and contact decisions.
// Run with tools/test_host.sh; authored from B0/B5.1 and the public Debouncer contract.
#include "doctest.h"
#include "config.h"
#include "core/opp_fusion.h"
#include <cstdint>
#include <initializer_list>

namespace {
constexpr std::uint32_t CLEAR_US = config::OPP_CLEAR_MS * 1000U;
// B0 order is FL15 FC FR15 SL SR RL RR; front sensors are active high.
constexpr bool ACTIVE_LOW[7] = {false, false, false, true, true, true, true};

std::uint8_t electrical(std::uint8_t detected) {
    std::uint8_t raw = 0;
    for (unsigned channel = 0; channel < 7; ++channel) {
        const bool present = (detected & (1U << channel)) != 0;
        if (present != ACTIVE_LOW[channel]) raw |= 1U << channel;
    }
    return raw;
}

std::uint32_t assertMask(opp_fusion::Debouncer& filter, std::uint8_t mask,
                         std::uint32_t start = 0U) {
    for (std::uint32_t sample = 1; sample <= config::OPP_SET_TICKS; ++sample) {
        const auto t = start + (sample - 1U) * config::TICK_US;
        CHECK(filter.step(t, electrical(mask)) ==
              (sample == config::OPP_SET_TICKS ? mask : 0U));
    }
    return start + (config::OPP_SET_TICKS - 1U) * config::TICK_US;
}
} // namespace

TEST_CASE("B0/B5.1 electrical clear and detected levels follow all seven named channels") {
    CHECK(electrical(0) == 0x78U);
    CHECK(electrical(0x7F) == 0x07U);
    for (unsigned channel = 0; channel < 7; ++channel) {
        CAPTURE(channel);
        opp_fusion::Debouncer filter;
        const auto bit = static_cast<std::uint8_t>(1U << channel);
        CHECK(filter.step(0U, 0x78U) == 0U);
        assertMask(filter, bit, config::TICK_US);
    }
}

TEST_CASE("B5.1 every one of the 128 detected masks asserts after consecutive samples") {
    for (unsigned mask = 0; mask < 128; ++mask) {
        CAPTURE(mask);
        opp_fusion::Debouncer filter;
        assertMask(filter, static_cast<std::uint8_t>(mask));
    }
}

TEST_CASE("B5.1 interrupted rising evidence cannot accumulate across clear samples") {
    for (unsigned channel = 0; channel < 7; ++channel) {
        CAPTURE(channel);
        opp_fusion::Debouncer filter;
        const auto bit = static_cast<std::uint8_t>(1U << channel);
        std::uint32_t t = 0;
        for (std::uint32_t sample = 1; sample < config::OPP_SET_TICKS; ++sample) {
            CHECK(filter.step(t, electrical(bit)) == 0U);
            t += config::TICK_US;
        }
        CHECK(filter.step(t, electrical(0)) == 0U);
        assertMask(filter, bit, t + config::TICK_US);
    }
}

TEST_CASE("B5.1 assertion counts fresh observations rather than elapsed milliseconds") {
    opp_fusion::Debouncer filter;
    for (std::uint32_t sample = 1; sample <= config::OPP_SET_TICKS; ++sample) {
        const auto t = sample * 1000000U;
        CHECK(filter.step(t, electrical(0x7F)) ==
              (sample == config::OPP_SET_TICKS ? 0x7FU : 0U));
    }
}

TEST_CASE("B5.1 each confirmed bit clears at exactly the clear duration from first clear sample") {
    for (unsigned channel = 0; channel < 7; ++channel) {
        CAPTURE(channel);
        opp_fusion::Debouncer filter;
        const auto bit = static_cast<std::uint8_t>(1U << channel);
        const auto first_clear = assertMask(filter, bit) + config::TICK_US;
        CHECK(filter.step(first_clear, electrical(0)) == bit);
        CHECK(filter.step(first_clear + CLEAR_US - 1000U, electrical(0)) == bit);
        CHECK(filter.step(first_clear + CLEAR_US - 1U, electrical(0)) == bit);
        CHECK(filter.step(first_clear + CLEAR_US, electrical(0)) == 0U);
        CHECK(filter.step(first_clear + CLEAR_US + 1U, electrical(0)) == 0U);
    }
}

TEST_CASE("B5.1 deassertion measures elapsed clear time rather than number of calls") {
    opp_fusion::Debouncer filter;
    const auto first_clear = assertMask(filter, 0x7F) + config::TICK_US;
    for (unsigned sample = 0; sample < 100; ++sample)
        CHECK(filter.step(first_clear, electrical(0)) == 0x7FU);
    CHECK(filter.step(first_clear + CLEAR_US - 1U, electrical(0)) == 0x7FU);
    CHECK(filter.step(first_clear + CLEAR_US, electrical(0)) == 0U);
}

TEST_CASE("B5.1 a detected sample interrupts and fully restarts the clear interval") {
    for (unsigned channel = 0; channel < 7; ++channel) {
        opp_fusion::Debouncer filter;
        const auto bit = static_cast<std::uint8_t>(1U << channel);
        const auto first_clear = assertMask(filter, bit) + config::TICK_US;
        CHECK(filter.step(first_clear, electrical(0)) == bit);
        CHECK(filter.step(first_clear + CLEAR_US - 1U, electrical(bit)) == bit);
        const auto second_clear = first_clear + CLEAR_US;
        CHECK(filter.step(second_clear, electrical(0)) == bit);
        CHECK(filter.step(second_clear + CLEAR_US - 1U, electrical(0)) == bit);
        CHECK(filter.step(second_clear + CLEAR_US, electrical(0)) == 0U);
    }
}

TEST_CASE("B5.1 each channel keeps its own clear deadline while other channels stay detected") {
    opp_fusion::Debouncer filter;
    const auto first_clear = assertMask(filter, 0x7F) + config::TICK_US;
    for (unsigned channel = 0; channel < 7; ++channel) {
        const auto detected = static_cast<std::uint8_t>(0x7FU & ~((1U << (channel + 1U)) - 1U));
        CHECK(filter.step(first_clear + channel * 1000U, electrical(detected)) == 0x7FU);
    }
    for (unsigned channel = 0; channel < 7; ++channel) {
        const auto before = static_cast<std::uint8_t>(0x7FU & ~((1U << channel) - 1U));
        const auto after = static_cast<std::uint8_t>(before & ~(1U << channel));
        const auto deadline = first_clear + CLEAR_US + channel * 1000U;
        CHECK(filter.step(deadline - 1U, electrical(0)) == before);
        CHECK(filter.step(deadline, electrical(0)) == after);
    }
}

TEST_CASE("B5.1 fresh detections on one channel do not confirm another channel") {
    for (unsigned selected = 0; selected < 7; ++selected) {
        opp_fusion::Debouncer filter;
        std::uint32_t t = 0;
        for (unsigned sample = 0; sample < 21; ++sample) {
            const auto bit = static_cast<std::uint8_t>(1U << (sample % 7U));
            const auto result = filter.step(t, electrical(bit));
            if (config::OPP_SET_TICKS > 1U) CHECK(result == 0U);
            t += config::TICK_US;
        }
        filter.reset();
        assertMask(filter, static_cast<std::uint8_t>(1U << selected), t);
    }
}

TEST_CASE("B0/B5.1 clear intervals and first-clear zero survive micros rollover") {
    for (auto first_clear : {0U, 0xFFFFFFFFU, 0xFFFFFFFFU - CLEAR_US / 2U}) {
        opp_fusion::Debouncer filter;
        const auto start = first_clear - config::OPP_SET_TICKS * config::TICK_US;
        assertMask(filter, 0x7F, start);
        CHECK(filter.step(first_clear, electrical(0)) == 0x7FU);
        CHECK(filter.step(first_clear + CLEAR_US - 1U, electrical(0)) == 0x7FU);
        CHECK(filter.step(first_clear + CLEAR_US, electrical(0)) == 0U);
    }
}

TEST_CASE("B5.1 unused electrical bit seven cannot set or clear a sensor") {
    for (unsigned mask = 0; mask < 128; ++mask) {
        opp_fusion::Debouncer low;
        opp_fusion::Debouncer high;
        for (std::uint32_t sample = 0; sample < config::OPP_SET_TICKS + 3U; ++sample) {
            const auto t = sample * config::TICK_US;
            const auto raw = electrical(static_cast<std::uint8_t>(mask));
            const auto result = high.step(t, static_cast<std::uint8_t>(raw | 0x80U));
            CHECK(result == low.step(t, raw));
            CHECK((result & 0x80U) == 0U);
        }
    }
}

TEST_CASE("B5.1 reset clears confirmed bits partial assertion and pending clear intervals") {
    opp_fusion::Debouncer filter;
    const auto clear_at = assertMask(filter, 0x7F) + config::TICK_US;
    filter.step(clear_at, electrical(0));
    filter.reset();
    CHECK(filter.step(clear_at + CLEAR_US - 1U, electrical(0)) == 0U);
    for (std::uint32_t sample = 1; sample < config::OPP_SET_TICKS; ++sample)
        CHECK(filter.step(sample * config::TICK_US, electrical(0x7F)) == 0U);
    filter.reset();
    const auto last = assertMask(filter, 0x7F, CLEAR_US * 2U);
    CHECK(filter.step(last + CLEAR_US, electrical(0x7F)) == 0x7FU);
}
