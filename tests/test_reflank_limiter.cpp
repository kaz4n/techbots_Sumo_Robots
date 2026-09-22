// Checks B11.3 rolling admission and D-025's bounded ALL_IN suppression timer.
// Counts accepted starts without granting motion or modeling the unfinished FSM.
// Run with tools/test_host.sh; exact deadlines and independent wrap traces are covered.
#include "doctest.h"
#include "config.h"
#include "core/stall.h"
#include <cstdint>
#include <initializer_list>
#include <vector>

namespace {
constexpr std::uint32_t WINDOW_US = config::REFLANK_WINDOW_MS * 1000U;
constexpr std::uint32_t ALL_IN_US = config::ALL_IN_MS * 1000U;
constexpr std::uint64_t WRAP_US = 0x100000000ULL;

void checkResult(const stall::LimitResult& result, bool allowed, bool active,
                 bool started, std::uint32_t count) {
    CHECK(result.allowed == allowed);
    CHECK(result.all_in_active == active);
    CHECK(result.all_in_started == started);
    CHECK(result.attempts_in_window == count);
}

void fillWindow(stall::ReflankLimiter& limiter, std::uint32_t first = 0U) {
    checkResult(limiter.request(first), true, false, false, 1U);
    checkResult(limiter.request(first + 1000U), true, false, false, 2U);
}

// Test-only receipt log: unwrapped absolute times and an absolute expiry.
// It retains old receipts rather than reproducing the limiter's bounded storage.
class Reference {
public:
    stall::LimitResult sample(std::uint64_t now, bool request) {
        stall::LimitResult result;
        for (auto accepted : accepted_us_)
            if (now < accepted + WINDOW_US) ++result.attempts_in_window;
        result.all_in_active = now < suppression_until_us_;
        if (!request || result.all_in_active) return result;
        if (result.attempts_in_window < config::REFLANK_MAX_PER_10S) {
            accepted_us_.push_back(now);
            ++result.attempts_in_window;
            result.allowed = true;
        } else {
            suppression_until_us_ = now + ALL_IN_US;
            result.all_in_active = true;
            result.all_in_started = true;
        }
        return result;
    }
    void reset() {
        accepted_us_.clear();
        suppression_until_us_ = 0U;
    }
private:
    std::vector<std::uint64_t> accepted_us_;
    std::uint64_t suppression_until_us_ = 0U;
};

std::uint32_t nextRandom(std::uint32_t& state) {
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

void checkTrace(std::uint32_t& random, unsigned trace) {
    CAPTURE(trace);
    stall::ReflankLimiter limiter;
    Reference reference;
    std::uint64_t now = trace % 2U == 0U
        ? WRAP_US - nextRandom(random) % WINDOW_US : nextRandom(random);
    const std::uint32_t gaps[] = {0U, 1U, 1000U, ALL_IN_US - 1U,
        ALL_IN_US, WINDOW_US - 1U, WINDOW_US, 0xFFFFFFFFU};
    for (unsigned index = 0U; index < 128U; ++index) {
        CAPTURE(index);
        const auto draw = nextRandom(random);
        now += gaps[(draw >> 3U) & 7U];
        if ((draw & 63U) == 63U) {
            limiter.reset();
            reference.reset();
        }
        const bool request = (draw & 1U) != 0U;
        const auto expected = reference.sample(now, request);
        const auto t_us = static_cast<std::uint32_t>(now);
        const auto actual = request ? limiter.request(t_us) : limiter.step(t_us);
        checkResult(actual, expected.allowed, expected.all_in_active,
                    expected.all_in_started, expected.attempts_in_window);
    }
}
} // namespace

TEST_CASE("B11.3 limiter admits the first two starts and starts ALL_IN on the third") {
    const stall::LimitResult initial;
    checkResult(initial, false, false, false, 0U);
    CHECK(config::REFLANK_MAX_PER_10S == 2U);
    CHECK(config::REFLANK_WINDOW_MS == 10000U);
    CHECK(config::ALL_IN_MS == 1500U);
    stall::ReflankLimiter limiter;
    checkResult(limiter.step(0U), false, false, false, 0U);
    fillWindow(limiter);
    checkResult(limiter.request(2000U), false, true, true, 2U);
    checkResult(limiter.step(2000U), false, true, false, 2U);
}

TEST_CASE("B11.3 rolling window admits at exactly ten seconds but not one microsecond early") {
    for (int offset : {-1, 0, 1}) {
        CAPTURE(offset);
        stall::ReflankLimiter limiter;
        checkResult(limiter.request(100U), true, false, false, 1U);
        checkResult(limiter.request(100U + WINDOW_US / 2U), true, false, false, 2U);
        const auto t = static_cast<std::uint32_t>(
            static_cast<std::int64_t>(100U + WINDOW_US) + offset);
        if (offset < 0)
            checkResult(limiter.request(t), false, true, true, 2U);
        else
            checkResult(limiter.request(t), true, false, false, 2U);
    }
}

TEST_CASE("B11.3 staggered starts expire individually rather than resetting a fixed bucket") {
    stall::ReflankLimiter limiter;
    checkResult(limiter.request(0U), true, false, false, 1U);
    checkResult(limiter.request(4000000U), true, false, false, 2U);
    checkResult(limiter.step(WINDOW_US - 1U), false, false, false, 2U);
    checkResult(limiter.step(WINDOW_US), false, false, false, 1U);
    checkResult(limiter.request(WINDOW_US + 1U), true, false, false, 2U);
    checkResult(limiter.step(4000000U + WINDOW_US - 1U), false, false, false, 2U);
    checkResult(limiter.step(4000000U + WINDOW_US), false, false, false, 1U);
    checkResult(limiter.step(2U * WINDOW_US), false, false, false, 1U);
    checkResult(limiter.step(2U * WINDOW_US + 1U), false, false, false, 0U);
}

TEST_CASE("B11.3 ALL_IN expires at 1500 ms and repeated denial cannot extend it") {
    stall::ReflankLimiter limiter;
    fillWindow(limiter);
    constexpr std::uint32_t denied_at = 2000U;
    checkResult(limiter.request(denied_at), false, true, true, 2U);
    for (auto elapsed : {0U, 1U, ALL_IN_US / 2U, ALL_IN_US - 1000U,
                         ALL_IN_US - 1U})
        checkResult(limiter.request(denied_at + elapsed), false, true, false, 2U);
    checkResult(limiter.step(denied_at + ALL_IN_US), false, false, false, 2U);
    checkResult(limiter.step(denied_at + ALL_IN_US + 1U), false, false, false, 2U);
    const auto next_denial = denied_at + ALL_IN_US + 2U;
    checkResult(limiter.request(next_denial), false, true, true, 2U);
    checkResult(limiter.step(next_denial + ALL_IN_US), false, false, false, 2U);
}

TEST_CASE("B11.3 timer-only steps cannot admit a start or automatically activate ALL_IN") {
    stall::ReflankLimiter limiter;
    for (auto t : {0U, 1U, ALL_IN_US, WINDOW_US})
        checkResult(limiter.step(t), false, false, false, 0U);
    fillWindow(limiter, WINDOW_US + 1U);
    for (auto elapsed : {0U, 1U, ALL_IN_US, 2U * ALL_IN_US})
        checkResult(limiter.step(WINDOW_US + 1001U + elapsed),
                    false, false, false, 2U);
}

TEST_CASE("B11.3 active ALL_IN denies starts even after old admission slots expire") {
    stall::ReflankLimiter limiter;
    fillWindow(limiter);
    const auto denial = WINDOW_US - 1000U;
    checkResult(limiter.request(denial), false, true, true, 2U);
    checkResult(limiter.request(WINDOW_US), false, true, false, 1U);
    checkResult(limiter.request(WINDOW_US + 1000U), false, true, false, 0U);
    checkResult(limiter.request(denial + ALL_IN_US - 1U), false, true, false, 0U);
    checkResult(limiter.request(denial + ALL_IN_US), true, false, false, 1U);
}

TEST_CASE("B11.3 repeated requests at one timestamp count distinct starts and one ALL_IN pulse") {
    stall::ReflankLimiter limiter;
    checkResult(limiter.request(42U), true, false, false, 1U);
    checkResult(limiter.request(42U), true, false, false, 2U);
    checkResult(limiter.request(42U), false, true, true, 2U);
    for (unsigned repeat = 0U; repeat < 10U; ++repeat) {
        checkResult(limiter.request(42U), false, true, false, 2U);
        checkResult(limiter.step(42U), false, true, false, 2U);
    }
    checkResult(limiter.request(42U + ALL_IN_US), false, true, true, 2U);
}

TEST_CASE("B11.3 accepted starts still count after their maneuvers are interrupted") {
    stall::ReflankLimiter limiter;
    checkResult(limiter.request(0U), true, false, false, 1U);
    // Timer-only calls represent time after a higher-priority interruption;
    // admission is charged at start, without a completion/cancel callback.
    checkResult(limiter.step(1000U), false, false, false, 1U);
    checkResult(limiter.request(2000U), true, false, false, 2U);
    checkResult(limiter.step(3000U), false, false, false, 2U);
    checkResult(limiter.request(4000U), false, true, true, 2U);
}

TEST_CASE("B11.3 reset clears admission history suppression and clock origin") {
    for (unsigned requests = 0U; requests <= 3U; ++requests) {
        stall::ReflankLimiter limiter;
        for (unsigned i = 0U; i < requests; ++i)
            limiter.request(0xFFFF0000U + i * 1000U);
        limiter.reset();
        checkResult(limiter.step(0U), false, false, false, 0U);
        fillWindow(limiter);
        checkResult(limiter.request(2000U), false, true, true, 2U);
    }
}

TEST_CASE("B0/B11.3 admission and ALL_IN deadlines remain exact across micros wrap") {
    stall::ReflankLimiter limiter;
    const std::uint64_t origin = WRAP_US - 1000U;
    auto step = [&](std::uint64_t offset) {
        return limiter.step(static_cast<std::uint32_t>(origin + offset));
    };
    checkResult(limiter.request(static_cast<std::uint32_t>(origin)),
                true, false, false, 1U);
    checkResult(limiter.request(static_cast<std::uint32_t>(origin + 100U)),
                true, false, false, 2U);
    checkResult(limiter.request(static_cast<std::uint32_t>(origin + 200U)),
                false, true, true, 2U);
    checkResult(step(200U + ALL_IN_US - 1U), false, true, false, 2U);
    checkResult(step(200U + ALL_IN_US), false, false, false, 2U);
    checkResult(step(WINDOW_US - 1U), false, false, false, 2U);
    checkResult(step(WINDOW_US), false, false, false, 1U);
    checkResult(step(WINDOW_US + 100U), false, false, false, 0U);
}

TEST_CASE("B0/B11.3 expired history never returns after cumulative wraps with legal call gaps") {
    stall::ReflankLimiter limiter;
    fillWindow(limiter, 100U);
    checkResult(limiter.request(2100U), false, true, true, 2U);
    std::uint64_t now = WINDOW_US + 2100U;
    checkResult(limiter.step(static_cast<std::uint32_t>(now)), false, false, false, 0U);
    for (std::uint64_t wrap = 1U; wrap <= 4U; ++wrap) {
        const auto next = wrap * WRAP_US + 100U;
        CHECK(next - now < WRAP_US);
        now = next;
        checkResult(limiter.step(static_cast<std::uint32_t>(now)),
                    false, false, false, 0U);
        now += 1000U;
        checkResult(limiter.step(static_cast<std::uint32_t>(now)),
                    false, false, false, 0U);
    }
    checkResult(limiter.request(static_cast<std::uint32_t>(now)),
                true, false, false, 1U);
}

TEST_CASE("B0/B11.3 varied limiter traces match an independent unwrapped receipt log") {
    std::uint32_t random = 0xB113D025U;
    for (unsigned trace = 0U; trace < 1000U; ++trace)
        checkTrace(random, trace);
}
