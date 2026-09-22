// Checks B4.1 completed-observation classification at every threshold and line mask.
// Locks the perception boundary without claiming R5 arbitration or physical escape.
// Run with tools/test_host.sh; authored from BEHAVIOR.md and public headers only.
#include "doctest.h"
#include "config.h"
#include "core/edge.h"
#include <cstdint>
#include <limits>

namespace {
void readingsFor(std::uint8_t mask, std::uint32_t (&raw)[4]) {
    for (unsigned i = 0; i < 4; ++i) {
        raw[i] = config::QTR_WHITE_US[i] - ((mask & (1U << i)) ? 1U : 0U);
    }
}

std::uint8_t confirm(edge::Classifier& classifier, std::uint32_t (&raw)[4]) {
    std::uint8_t actual = 0;
    for (std::uint32_t i = 0; i < config::QTR_CONFIRM_TICKS; ++i) {
        actual = classifier.observe(raw);
    }
    return actual;
}
} // namespace

TEST_CASE("B0/B4.1 all 16 white masks preserve FL FR RL RR bit order") {
    for (std::uint8_t mask = 0; mask < 16; ++mask) {
        CAPTURE(mask);
        edge::Classifier classifier;
        std::uint32_t raw[4] = {};
        readingsFor(mask, raw);
        for (std::uint32_t n = 1; n <= config::QTR_CONFIRM_TICKS; ++n) {
            CHECK(classifier.observe(raw) ==
                  (n == config::QTR_CONFIRM_TICKS ? mask : 0U));
        }
        CHECK(classifier.observe(raw) == mask);
    }
}

TEST_CASE("B4.1 each white threshold is strict with adjacent microsecond readings") {
    for (unsigned sensor = 0; sensor < 4; ++sensor) {
        CAPTURE(sensor);
        edge::Classifier classifier;
        std::uint32_t raw[4] = {};
        readingsFor(0, raw);
        raw[sensor] = config::QTR_WHITE_US[sensor] + 1U;
        CHECK(confirm(classifier, raw) == 0U);
        raw[sensor] = config::QTR_WHITE_US[sensor];
        CHECK(confirm(classifier, raw) == 0U);
        raw[sensor] = config::QTR_WHITE_US[sensor] - 1U;
        CHECK(confirm(classifier, raw) == (1U << sensor));
    }
}

TEST_CASE("B4.1 zero discharge is white and timeout or larger readings are black") {
    edge::Classifier classifier;
    std::uint32_t raw[4] = {};
    CHECK(confirm(classifier, raw) == 15U);
    for (auto& value : raw) value = config::QTR_TIMEOUT_US;
    CHECK(classifier.observe(raw) == 0U);
    for (auto& value : raw) value = std::numeric_limits<std::uint32_t>::max();
    CHECK(classifier.observe(raw) == 0U);
}

TEST_CASE("B4.1 black breaks consecutive confirmation independently on each channel") {
    for (unsigned interrupted = 0; interrupted < 4; ++interrupted) {
        CAPTURE(interrupted);
        edge::Classifier classifier;
        std::uint32_t raw[4] = {};
        for (std::uint32_t n = 1; n < config::QTR_CONFIRM_TICKS; ++n)
            CHECK(classifier.observe(raw) == 0U);
        raw[interrupted] = config::QTR_WHITE_US[interrupted];
        CHECK(classifier.observe(raw) == (15U ^ (1U << interrupted)));
        raw[interrupted] = 0;
        for (std::uint32_t n = 1; n <= config::QTR_CONFIRM_TICKS; ++n) {
            const auto expected = n == config::QTR_CONFIRM_TICKS
                ? 15U : (15U ^ (1U << interrupted));
            CHECK(classifier.observe(raw) == expected);
        }
    }
}

TEST_CASE("B4.1 confirmed white persists as a level and black clears immediately") {
    edge::Classifier classifier;
    std::uint32_t raw[4] = {};
    CHECK(confirm(classifier, raw) == 15U);
    for (unsigned sample = 0; sample < 1000; ++sample)
        CHECK(classifier.observe(raw) == 15U);
    for (std::uint8_t mask = 0; mask < 16; ++mask) {
        readingsFor(mask, raw);
        CHECK(confirm(classifier, raw) == mask);
        readingsFor(0, raw);
        CHECK(classifier.observe(raw) == 0U);
    }
}

TEST_CASE("B4.1 reset discards completed and partial white confirmation") {
    edge::Classifier classifier;
    std::uint32_t raw[4] = {};
    CHECK(confirm(classifier, raw) == 15U);
    classifier.reset();
    readingsFor(0, raw);
    CHECK(classifier.observe(raw) == 0U);
    readingsFor(15, raw);
    for (std::uint32_t n = 1; n < config::QTR_CONFIRM_TICKS; ++n)
        CHECK(classifier.observe(raw) == 0U);
    classifier.reset();
    for (std::uint32_t n = 1; n <= config::QTR_CONFIRM_TICKS; ++n)
        CHECK(classifier.observe(raw) == (n == config::QTR_CONFIRM_TICKS ? 15U : 0U));
}
