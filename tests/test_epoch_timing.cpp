// Checks the D229 exact nearest-rank distribution against independent samples.
// Exercises range loss and saturated retained prefixes without target claims.
// The focused runner executes these checks with undefined-behavior sanitization.
#include "doctest.h"
#include "app/epoch_timing.h"
#include <algorithm>
#include <cstdio>
#include <limits>
#include <type_traits>
#include <vector>

using app::epoch_timing::Data;
using app::epoch_timing::Distribution;
using app::epoch_timing::Status;
static_assert(std::is_same_v<decltype(std::declval<const Distribution&>().data()), const Data&>);

TEST_CASE("B14 P2.2 D229 empty and zero durations remain distinct") {
    Distribution owner;
    CHECK(owner.summary().status == Status::EMPTY);
    CHECK(owner.summary().samples == 0U);
    owner.observe(0U, 0U, 0U);
    const auto report = owner.summary();
    CHECK(report.status == Status::EXACT);
    CHECK(report.rank == 1U);
    CHECK(report.p99_us == 0U);
    CHECK(owner.data().bins[0] == 1U);
}

TEST_CASE("B14 P2.2 D229 nearest rank matches independently sorted per-epoch samples") {
    for (const unsigned count : {1U, 2U, 98U, 99U, 100U, 101U, 199U, 200U, 201U, 2000U}) {
        for (const unsigned range : {800U, 925U}) {
            Distribution owner;
            std::vector<unsigned> samples;
            for (unsigned i = 0U; i < count; ++i) {
                const auto duration = (i * 37U + 11U) % range;
                samples.push_back(duration);
                owner.observe(duration, i * 1000U, i * 1000U + duration);
            }
            std::sort(samples.begin(), samples.end());
            const auto rank = (99U * count + 99U) / 100U;
            const auto expected = samples[rank - 1U];
            const auto result = owner.summary();
            CAPTURE(count); CAPTURE(range);
            CHECK(result.rank == rank);
            CHECK(result.samples == count);
            CHECK(result.maximum_us == samples.back());
            CHECK(result.status == (expected < 800U ? Status::EXACT : Status::RANGE_OVERFLOW));
            if (expected < 800U) CHECK(result.p99_us == expected);
        }
    }
}

TEST_CASE("B14 P2.2 D229 overflow rank boundary preserves unclipped worst case") {
    Distribution owner;
    for (unsigned i = 0U; i < 98U; ++i) owner.observe(799U, i, i + 799U);
    owner.observe(1600U, 1000U, 2600U);
    CHECK(owner.summary().status == Status::RANGE_OVERFLOW);
    owner.observe(799U, 3000U, 3799U);
    CHECK(owner.summary().status == Status::EXACT);
    CHECK(owner.summary().p99_us == 799U);
    CHECK(owner.summary().maximum_us == 1600U);
    CHECK(owner.summary().overflow == 1U);
    owner.observe(800U, 4000U, 4800U);
    CHECK(owner.summary().status == Status::RANGE_OVERFLOW);
    CHECK(owner.summary().overflow == 2U);
}

TEST_CASE("B14 P2.2 D229 modular anchors do not infer elapsed window") {
    Distribution owner;
    owner.observe(400U, 0xFFFFFF00U, 144U);
    owner.observe(1U, 744U, 745U);
    const auto result = owner.summary();
    CHECK(result.first_started_us == 0xFFFFFF00U);
    CHECK(result.retained_completed_us == 745U);
    CHECK(result.last_completed_us == 745U);
    CHECK(result.p99_us == 400U);
}

TEST_CASE("B14 P2.2 D229 saturation freezes prefix bins but observes later maxima and anchors") {
    Distribution owner;
    // Test-only coherent near-limit image; the actual object is nonconst.
    // This avoids billions of observations and adds no production mutation API.
    auto& image = const_cast<Data&>(owner.data());
    const auto limit = std::numeric_limits<std::uint32_t>::max();
    image.samples = image.bins[7] = limit - 1U;
    image.maximum_us = image.retained_maximum_us = 7U;
    image.first_started_us = 123U;
    owner.observe(7U, 400U, 407U);
    CHECK(owner.summary().status == Status::EXACT);
    CHECK(owner.summary().rank == 4252017623U);
    CHECK(image.bins[7] == limit);
    owner.observe(1000U, 500U, 1500U);
    const auto result = owner.summary();
    CHECK(result.status == Status::SATURATED);
    CHECK(result.retained_status == Status::EXACT);
    CHECK(result.p99_us == 7U);
    CHECK(result.samples == limit);
    CHECK(result.rejected == 1U);
    CHECK(result.overflow == 0U);
    CHECK(result.retained_maximum_us == 7U);
    CHECK(result.maximum_us == 1000U);
    CHECK(result.first_started_us == 123U);
    CHECK(result.retained_completed_us == 407U);
    CHECK(result.last_completed_us == 1500U);
}

TEST_CASE("B14 P2.2 D229 overflow and rejection counters never wrap") {
    Distribution owner;
    auto& image = const_cast<Data&>(owner.data());
    const auto limit = std::numeric_limits<std::uint32_t>::max();
    image.samples = image.overflow = limit - 1U;
    image.maximum_us = image.retained_maximum_us = 800U;
    owner.observe(800U, 10U, 810U);
    CHECK(owner.summary().status == Status::RANGE_OVERFLOW);
    CHECK(image.overflow == limit);
    owner.observe(900U, 20U, 920U);
    image.rejected = limit - 1U;
    owner.observe(limit, 30U, 29U);
    owner.observe(0U, 40U, 40U);
    const auto result = owner.summary();
    CHECK(result.status == Status::SATURATED);
    CHECK(result.retained_status == Status::RANGE_OVERFLOW);
    CHECK(result.samples == limit);
    CHECK(result.overflow == limit);
    CHECK(result.rejected == limit);
    CHECK(result.maximum_us == limit);
    CHECK(result.retained_completed_us == 810U);
    CHECK(result.last_completed_us == 40U);
}

TEST_CASE("B14 P2.2 D229 inconsistent histogram is not an exact percentile") {
    Distribution owner;
    auto& image = const_cast<Data&>(owner.data());
    image.bins[0] = 1U;
    CHECK(owner.summary().status == Status::INCONSISTENT);
    owner.observe(3U, 1U, 4U);
    CHECK(owner.summary().retained_status == Status::INCONSISTENT);
}

TEST_CASE("B14 P2.2 D229 host data sizes are reported as host ABI only") {
    std::printf("D229 host sizes: Data=%zu Distribution=%zu Summary=%zu bins=%zu\n",
                sizeof(Data), sizeof(Distribution), sizeof(app::epoch_timing::Summary),
                sizeof(Data::bins));
    CHECK(sizeof(Data::bins) == 3200U);
    CHECK(sizeof(Distribution) == sizeof(Data));
}
