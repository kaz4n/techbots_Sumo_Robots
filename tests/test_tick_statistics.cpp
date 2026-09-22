// Checks B14 supplied-duration statistics and their B15 maximum encoding boundary.
// Separates exact retained-count arithmetic from clocks, match membership and motor response.
// Independent host tests use strict thresholds and valid public limit fixtures.
#include "doctest.h"
#include "config.h"
#include "core/logframe.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
constexpr std::uint64_t MAX_TICKS = std::numeric_limits<std::uint64_t>::max();
constexpr std::uint32_t MAX_DURATION = std::numeric_limits<std::uint32_t>::max();

void checkStatistics(const logframe::TickStatistics& statistics,
                     std::uint64_t ticks, std::uint64_t overruns,
                     std::uint32_t maximum, bool saturated) {
    CHECK(statistics.ticks == ticks);
    CHECK(statistics.overruns == overruns);
    CHECK(statistics.max_us == maximum);
    CHECK(statistics.saturated == saturated);
    CHECK(statistics.overruns <= statistics.ticks);
}

struct RatioFixture {
    std::uint64_t ticks;
    std::uint64_t overruns;
    bool exceeded;
};

void checkRatio(const RatioFixture& fixture) {
    // Public value-state fixture, not fabricated private state or a measured run.
    const std::uint32_t maximum = fixture.overruns == 0U ? 1000U : 1001U;
    logframe::TickStatistics statistics{fixture.ticks, fixture.overruns, maximum, false};
    CHECK(statistics.overruns <= statistics.ticks);
    CHECK(logframe::overrunRateExceeded(statistics) == fixture.exceeded);
}
} // namespace

TEST_CASE("B14 empty tick statistics are complete and below the literal one percent warning") {
    CHECK(config::TICK_US == 1000U);
    CHECK(config::TICK_OVERRUN_PERCENT == 1U);
    const logframe::TickStatistics statistics;
    checkStatistics(statistics, 0U, 0U, 0U, false);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
}

TEST_CASE("B14 overrun requires strictly more than 1000 supplied microseconds") {
    struct DurationFixture { std::uint32_t duration; std::uint64_t overruns; };
    const std::array<DurationFixture, 7> fixtures{{
        {0U, 0U}, {1U, 0U}, {800U, 0U}, {999U, 0U},
        {1000U, 0U}, {1001U, 1U}, {MAX_DURATION, 1U}
    }};
    for (const auto& fixture : fixtures) {
        logframe::TickStatistics statistics;
        logframe::observeTick(statistics, fixture.duration);
        checkStatistics(statistics, 1U, fixture.overruns, fixture.duration, false);
        CHECK(logframe::overrunRateExceeded(statistics) == (fixture.overruns != 0U));
    }
}

TEST_CASE("B14 every supplied tick counts while the full maximum is monotonic") {
    logframe::TickStatistics statistics;
    const std::array<std::uint32_t, 8> durations{{1000U, 1001U, 999U, 2000U, 0U, 2000U, MAX_DURATION, 1U}};
    const std::array<std::uint32_t, 8> maxima{{1000U, 1001U, 1001U, 2000U, 2000U, 2000U, MAX_DURATION, MAX_DURATION}};
    const std::array<std::uint64_t, 8> overruns{{0U, 1U, 1U, 2U, 2U, 3U, 4U, 4U}};
    for (std::size_t i = 0U; i < durations.size(); ++i) {
        logframe::observeTick(statistics, durations[i]);
        checkStatistics(statistics, i + 1U, overruns[i], maxima[i], false);
    }
}

TEST_CASE("B14 zero one and two overruns in 100 real observations straddle exactly one percent") {
    for (const unsigned overruns : {0U, 1U, 2U}) {
        logframe::TickStatistics statistics;
        for (unsigned sample = 0U; sample < 100U; ++sample) {
            logframe::observeTick(statistics, sample < overruns ? 1001U : 1000U);
        }
        checkStatistics(statistics, 100U, overruns, overruns == 0U ? 1000U : 1001U, false);
        CHECK(logframe::overrunRateExceeded(statistics) == (overruns == 2U));
    }
}

TEST_CASE("B14 exact one percent denominator and numerator neighbors use strict comparison") {
    const std::array<RatioFixture, 12> fixtures{{
        {1U, 0U, false}, {1U, 1U, true},
        {99U, 1U, true}, {100U, 1U, false}, {101U, 1U, false},
        {199U, 2U, true}, {200U, 2U, false}, {201U, 2U, false},
        {200U, 1U, false}, {200U, 3U, true},
        {100U, 100U, true}, {100U, 0U, false}
    }};
    for (const auto& fixture : fixtures) checkRatio(fixture);
}

TEST_CASE("B14 overrun ratio is a current level and can fall back to exactly one percent") {
    logframe::TickStatistics statistics;
    logframe::observeTick(statistics, 1001U);
    CHECK(logframe::overrunRateExceeded(statistics));
    for (unsigned tick = 2U; tick <= 99U; ++tick) logframe::observeTick(statistics, 1000U);
    CHECK(logframe::overrunRateExceeded(statistics));
    logframe::observeTick(statistics, 1000U);
    checkStatistics(statistics, 100U, 1U, 1001U, false);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
    logframe::observeTick(statistics, 1001U);
    CHECK(logframe::overrunRateExceeded(statistics));
    for (unsigned tick = 102U; tick <= 200U; ++tick) logframe::observeTick(statistics, 1000U);
    checkStatistics(statistics, 200U, 2U, 1001U, false);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
}

TEST_CASE("B14 large exact ratios distinguish adjacent counts beyond floating point precision") {
    const std::array<RatioFixture, 11> fixtures{{
        {9007199254741000ULL, 90071992547409ULL, false},
        {9007199254741000ULL, 90071992547410ULL, false},
        {9007199254741000ULL, 90071992547411ULL, true},
        {18446744073709551600ULL, 184467440737095515ULL, false},
        {18446744073709551600ULL, 184467440737095516ULL, false},
        {18446744073709551600ULL, 184467440737095517ULL, true},
        {MAX_TICKS, 184467440737095516ULL, false},
        {MAX_TICKS, 184467440737095517ULL, true},
        {MAX_TICKS, 0U, false},
        {MAX_TICKS, MAX_TICKS - 1U, true},
        {MAX_TICKS, MAX_TICKS, true}
    }};
    for (const auto& fixture : fixtures) checkRatio(fixture);
}

TEST_CASE("B14 the last representable retained overrun is counted before saturation latches") {
    // A possible public history: all previous retained ticks were 1001 us.
    logframe::TickStatistics statistics{MAX_TICKS - 1U, MAX_TICKS - 1U, 1001U, false};
    logframe::observeTick(statistics, 1001U);
    checkStatistics(statistics, MAX_TICKS, MAX_TICKS, 1001U, false);
    CHECK(logframe::overrunRateExceeded(statistics));
    logframe::observeTick(statistics, 1000U);
    checkStatistics(statistics, MAX_TICKS, MAX_TICKS, 1001U, true);
    logframe::observeTick(statistics, MAX_DURATION);
    checkStatistics(statistics, MAX_TICKS, MAX_TICKS, MAX_DURATION, true);
    CHECK(logframe::overrunRateExceeded(statistics));
}

TEST_CASE("B14 rejected ticks preserve a zero-overrun retained prefix and mark it incomplete") {
    // A possible public history: all previous retained ticks were exactly 1000 us.
    logframe::TickStatistics statistics{MAX_TICKS - 1U, 0U, 1000U, false};
    logframe::observeTick(statistics, 999U);
    checkStatistics(statistics, MAX_TICKS, 0U, 1000U, false);
    logframe::observeTick(statistics, 1001U);
    checkStatistics(statistics, MAX_TICKS, 0U, 1001U, true);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
    logframe::observeTick(statistics, MAX_DURATION);
    checkStatistics(statistics, MAX_TICKS, 0U, MAX_DURATION, true);
    logframe::observeTick(statistics, 0U);
    checkStatistics(statistics, MAX_TICKS, 0U, MAX_DURATION, true);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
    // A false retained-prefix ratio does not erase incomplete-evidence status.
    CHECK(statistics.saturated);
}

TEST_CASE("B14 saturation does not change an exact large retained ratio") {
    logframe::TickStatistics statistics{MAX_TICKS - 1U, 184467440737095516ULL, 1001U, false};
    logframe::observeTick(statistics, 0U);
    checkStatistics(statistics, MAX_TICKS, 184467440737095516ULL, 1001U, false);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
    logframe::observeTick(statistics, 2000U);
    checkStatistics(statistics, MAX_TICKS, 184467440737095516ULL, 2000U, true);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
}

TEST_CASE("B14 value reset clears counts maximum and incomplete status for a fresh series") {
    logframe::TickStatistics statistics{MAX_TICKS, MAX_TICKS, MAX_DURATION, false};
    logframe::observeTick(statistics, 0U);
    CHECK(statistics.saturated);
    statistics = logframe::TickStatistics{};
    checkStatistics(statistics, 0U, 0U, 0U, false);
    CHECK_FALSE(logframe::overrunRateExceeded(statistics));
    logframe::observeTick(statistics, 0U);
    checkStatistics(statistics, 1U, 0U, 0U, false);
    logframe::observeTick(statistics, 1001U);
    checkStatistics(statistics, 2U, 1U, 1001U, false);
    CHECK(logframe::overrunRateExceeded(statistics));
}

TEST_CASE("B14 B15 packing the maximum clamps only frame representation and preserves statistics") {
    logframe::TickStatistics statistics;
    logframe::FrameInput input;
    input.t_ms = 0x12345678U;
    input.state = core::State::ATTACK;
    input.mode = core::Mode::ARC_L;
    input.opp_mask = 2U;
    input.flags = logframe::IMU_OK;
    const std::uint8_t prefix[23] = {
        0x78U, 0x56U, 0x34U, 0x12U, 6U, 5U, 0U, 2U,
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 1U
    };
    for (const std::uint32_t duration : {1000U, 65534U, 65535U, 65536U, MAX_DURATION}) {
        logframe::observeTick(statistics, duration);
        const auto retained = statistics;
        input.tick_max_us = statistics.max_us;
        logframe::FrameBytes bytes;
        const auto status = logframe::packFrame(input, bytes);
        CHECK(status == (duration <= 65535U ? logframe::PackStatus::OK : logframe::PackStatus::CLAMPED));
        for (std::size_t index = 0U; index < 23U; ++index) CHECK(bytes.data[index] == prefix[index]);
        const std::uint32_t encoded = duration <= 65535U ? duration : 65535U;
        CHECK(bytes.data[23] == (encoded & 255U));
        CHECK(bytes.data[24] == (encoded >> 8U));
        checkStatistics(statistics, retained.ticks, retained.overruns, retained.max_us, retained.saturated);
        CHECK(input.tick_max_us == duration);
    }
    checkStatistics(statistics, 5U, 4U, MAX_DURATION, false);
}
