// Checks B15/D-028 bounded event retention against the committed public contract.
// Preserves independent byte fixtures and overflow evidence without HAL assumptions.
// Host doctest cases cover capacity, insertion order, reset and saturation arithmetic.
#include "doctest.h"
#include "core/logframe.h"
#include <cstddef>
#include <cstdint>
#include <limits>

namespace {
constexpr std::size_t APPROVED_CAPACITY = 4096U;

logframe::EventInput eventInput(std::uint32_t ordinal) {
    logframe::EventInput input;
    input.t_us = 0xF1234000U + ordinal * 104729U;
    input.type = static_cast<core::Event>(ordinal % 10U);
    input.detail = static_cast<std::uint8_t>(ordinal ^ 0xD3U);
    input.value = static_cast<std::uint16_t>(ordinal ^ 0xA55AU);
    return input;
}

logframe::EventBytes encodedEvent(std::uint32_t ordinal) {
    logframe::EventBytes bytes;
    CHECK(logframe::packEvent(eventInput(ordinal), bytes) == logframe::PackStatus::OK);
    return bytes;
}

void checkRetained(const logframe::EventBuffer& buffer, std::size_t index,
                   std::uint32_t ordinal) {
    const std::uint32_t tick = 0xF1234000U + ordinal * 104729U;
    const std::uint16_t value = static_cast<std::uint16_t>(ordinal ^ 0xA55AU);
    const std::uint8_t expected[8] = {
        static_cast<std::uint8_t>(tick), static_cast<std::uint8_t>(tick >> 8U),
        static_cast<std::uint8_t>(tick >> 16U), static_cast<std::uint8_t>(tick >> 24U),
        static_cast<std::uint8_t>(ordinal % 10U),
        static_cast<std::uint8_t>(ordinal ^ 0xD3U),
        static_cast<std::uint8_t>(value), static_cast<std::uint8_t>(value >> 8U)
    };
    const auto* retained = buffer.at(index);
    CAPTURE(index);
    CAPTURE(ordinal);
    CHECK(retained != nullptr);
    if (retained == nullptr) return;
    for (std::size_t byte = 0U; byte < 8U; ++byte) {
        CAPTURE(byte);
        CHECK(retained->data[byte] == expected[byte]);
    }
}

void fillEvents(logframe::EventBuffer& buffer, std::size_t count) {
    for (std::size_t index = 0U; index < count; ++index) {
        CAPTURE(index);
        CHECK(buffer.append(encodedEvent(static_cast<std::uint32_t>(index))));
    }
}

void checkSaturationOracle(std::uint32_t value) {
    const std::uint64_t wide_sum = static_cast<std::uint64_t>(value) + 1U;
    const std::uint64_t maximum = 0xFFFFFFFFULL;
    const auto expected = static_cast<std::uint32_t>(
        wide_sum > maximum ? maximum : wide_sum);
    CAPTURE(value);
    CHECK(logframe::saturatingIncrement(value) == expected);
    CHECK(logframe::saturatingIncrement(value) >= value);
}
} // namespace

TEST_CASE("B15 D028 event buffer starts empty with the literal 4096 event capacity") {
    CHECK(config::LOG_EVENT_CAPACITY == 4096U);
    CHECK(logframe::EVENT_BYTES == 8U);
    logframe::EventBuffer buffer;
    CHECK(buffer.size() == 0U);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
    CHECK(buffer.at(0U) == nullptr);
    CHECK(buffer.at(4095U) == nullptr);
    CHECK(buffer.at(4096U) == nullptr);
    CHECK(buffer.at(std::numeric_limits<std::size_t>::max()) == nullptr);
}

TEST_CASE("B15 D028 exactly 4095 and 4096 events fit but event 4097 is rejected") {
    logframe::EventBuffer buffer;
    fillEvents(buffer, 4095U);
    CHECK(buffer.size() == 4095U);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
    checkRetained(buffer, 4094U, 4094U);
    CHECK(buffer.at(4095U) == nullptr);
    CHECK(buffer.append(encodedEvent(4095U)));
    CHECK(buffer.size() == 4096U);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
    checkRetained(buffer, 4095U, 4095U);
    CHECK(buffer.at(4096U) == nullptr);
    CHECK_FALSE(buffer.append(encodedEvent(4096U)));
    CHECK(buffer.size() == 4096U);
    CHECK(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 1U);
    checkRetained(buffer, 0U, 0U);
    checkRetained(buffer, 4095U, 4095U);
}

TEST_CASE("B15 D028 every retained byte survives repeated full buffer rejections") {
    logframe::EventBuffer buffer;
    fillEvents(buffer, APPROVED_CAPACITY);
    for (std::uint32_t rejection = 1U; rejection <= 129U; ++rejection) {
        CHECK_FALSE(buffer.append(encodedEvent(4095U + rejection)));
        CHECK(buffer.rejectedCount() == rejection);
        CHECK(buffer.overflowed());
        CHECK(buffer.size() == 4096U);
    }
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        checkRetained(buffer, index, static_cast<std::uint32_t>(index));
    }
    CHECK(buffer.at(4096U) == nullptr);
    CHECK(buffer.at(4224U) == nullptr);
}

TEST_CASE("B15 D028 append retains a value copy independent of the input lifetime") {
    logframe::EventBuffer buffer;
    {
        auto bytes = encodedEvent(782U);
        CHECK(buffer.append(bytes));
        for (auto& byte : bytes.data) byte = 0xFFU;
        checkRetained(buffer, 0U, 782U);
    }
    checkRetained(buffer, 0U, 782U);
    CHECK(buffer.size() == 1U);
    CHECK(buffer.at(1U) == nullptr);
}

TEST_CASE("B15 D028 equal tick events retain insertion order at the capacity boundary") {
    logframe::EventBuffer buffer;
    fillEvents(buffer, 4093U);
    const core::Event types[4] = {
        core::Event::FAULT, core::Event::GO,
        core::Event::EDGE, core::Event::START_RELEASE
    };
    const std::uint8_t encoded_types[3] = {9U, 1U, 4U};
    for (std::size_t index = 0U; index < 4U; ++index) {
        logframe::EventInput input;
        input.t_us = 0x12345678U;
        input.type = types[index];
        input.detail = static_cast<std::uint8_t>(index);
        logframe::EventBytes bytes;
        CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
        CHECK(buffer.append(bytes) == (index < 3U));
    }
    for (std::size_t index = 0U; index < 3U; ++index) {
        const auto* retained = buffer.at(4093U + index);
        CHECK(retained != nullptr);
        if (retained == nullptr) continue;
        CHECK(retained->data[0] == 0x78U);
        CHECK(retained->data[1] == 0x56U);
        CHECK(retained->data[2] == 0x34U);
        CHECK(retained->data[3] == 0x12U);
        CHECK(retained->data[4] == encoded_types[index]);
        CHECK(retained->data[5] == index);
        CHECK(retained->data[6] == 0U);
        CHECK(retained->data[7] == 0U);
    }
    CHECK(buffer.size() == 4096U);
    CHECK(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 1U);
}

TEST_CASE("B15 D028 micros wrap and descending times are preserved without sorting") {
    logframe::EventBuffer buffer;
    const std::uint32_t ticks[5] = {0xFFFFFFFEU, 0xFFFFFFFFU, 0U, 1U, 0U};
    const std::uint8_t expected_times[5][4] = {
        {0xFEU, 0xFFU, 0xFFU, 0xFFU}, {0xFFU, 0xFFU, 0xFFU, 0xFFU},
        {0U, 0U, 0U, 0U}, {1U, 0U, 0U, 0U}, {0U, 0U, 0U, 0U}
    };
    for (std::size_t index = 0U; index < 5U; ++index) {
        logframe::EventInput input;
        input.t_us = ticks[index];
        input.detail = static_cast<std::uint8_t>(index);
        logframe::EventBytes bytes;
        CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
        CHECK(buffer.append(bytes));
    }
    for (std::size_t index = 0U; index < 5U; ++index) {
        const auto* retained = buffer.at(index);
        CHECK(retained != nullptr);
        if (retained == nullptr) continue;
        for (std::size_t byte = 0U; byte < 4U; ++byte) {
            CHECK(retained->data[byte] == expected_times[index][byte]);
        }
        CHECK(retained->data[4] == 0U);
        CHECK(retained->data[5] == index);
        CHECK(retained->data[6] == 0U);
        CHECK(retained->data[7] == 0U);
    }
    CHECK(buffer.size() == 5U);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
}

TEST_CASE("B15 D028 const reads reject every index outside retained logical contents") {
    logframe::EventBuffer buffer;
    fillEvents(buffer, 7U);
    const logframe::EventBuffer& view = buffer;
    checkRetained(view, 0U, 0U);
    checkRetained(view, 6U, 6U);
    CHECK(view.at(7U) == nullptr);
    CHECK(view.at(4095U) == nullptr);
    CHECK(view.at(4096U) == nullptr);
    CHECK(view.at(std::numeric_limits<std::size_t>::max()) == nullptr);
    CHECK(view.size() == 7U);
    CHECK_FALSE(view.overflowed());
    CHECK(view.rejectedCount() == 0U);
}

TEST_CASE("B15 D028 reset clears overflow count and visibility of every old entry") {
    logframe::EventBuffer buffer;
    fillEvents(buffer, APPROVED_CAPACITY);
    for (std::uint32_t ordinal = 4096U; ordinal < 4099U; ++ordinal) {
        CHECK_FALSE(buffer.append(encodedEvent(ordinal)));
    }
    CHECK(buffer.rejectedCount() == 3U);
    CHECK(buffer.overflowed());
    buffer.reset();
    CHECK(buffer.size() == 0U);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        CHECK(buffer.at(index) == nullptr);
    }
    CHECK(buffer.append(encodedEvent(8128U)));
    checkRetained(buffer, 0U, 8128U);
    CHECK(buffer.size() == 1U);
    CHECK(buffer.at(1U) == nullptr);
    CHECK(buffer.at(4095U) == nullptr);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
}

TEST_CASE("B15 D028 reset is idempotent and restores full capacity after a partial run") {
    logframe::EventBuffer buffer;
    buffer.reset();
    CHECK(buffer.append(encodedEvent(42U)));
    buffer.reset();
    buffer.reset();
    fillEvents(buffer, APPROVED_CAPACITY);
    CHECK(buffer.size() == 4096U);
    CHECK_FALSE(buffer.overflowed());
    CHECK(buffer.rejectedCount() == 0U);
    checkRetained(buffer, 0U, 0U);
    checkRetained(buffer, 4095U, 4095U);
    CHECK_FALSE(buffer.append(encodedEvent(4096U)));
    CHECK(buffer.rejectedCount() == 1U);
}

TEST_CASE("B15 D028 overflow and reset belong to each buffer instance") {
    logframe::EventBuffer first;
    logframe::EventBuffer second;
    fillEvents(first, APPROVED_CAPACITY);
    CHECK_FALSE(first.append(encodedEvent(4096U)));
    CHECK(second.append(encodedEvent(77U)));
    CHECK(second.size() == 1U);
    CHECK_FALSE(second.overflowed());
    CHECK(second.rejectedCount() == 0U);
    first.reset();
    CHECK(first.size() == 0U);
    checkRetained(second, 0U, 77U);
    CHECK(second.size() == 1U);
    CHECK_FALSE(second.overflowed());
    CHECK(second.rejectedCount() == 0U);
}

TEST_CASE("B15 D028 production rejected counter increment saturates at uint32 maximum") {
    constexpr auto maximum = std::numeric_limits<std::uint32_t>::max();
    constexpr auto below = logframe::saturatingIncrement(maximum - 1U);
    constexpr auto saturated = logframe::saturatingIncrement(maximum);
    CHECK(logframe::saturatingIncrement(0U) == 1U);
    CHECK(logframe::saturatingIncrement(1U) == 2U);
    CHECK(below == maximum);
    CHECK(saturated == maximum);
    CHECK(logframe::saturatingIncrement(saturated) == maximum);
    for (std::uint32_t distance = 0U; distance <= 32U; ++distance) {
        checkSaturationOracle(maximum - distance);
    }
}

TEST_CASE("B15 D028 rejected counter arithmetic matches 10000 fixed seed uint64 oracles") {
    std::uint32_t seed = 0xB150D028U;
    for (std::size_t sample = 0U; sample < 10000U; ++sample) {
        seed = 1664525U * seed + 1013904223U;
        checkSaturationOracle(seed);
    }
}

TEST_CASE("B15 D028 event overflow leaves the independent frame codec usable") {
    logframe::EventBuffer buffer;
    fillEvents(buffer, APPROVED_CAPACITY);
    CHECK_FALSE(buffer.append(encodedEvent(4096U)));
    logframe::FrameInput input;
    input.t_ms = 0x01020304U;
    input.state = core::State::ATTACK;
    input.mode = core::Mode::DIRECT;
    input.duty_l = 0.5F;
    input.duty_r = -0.5F;
    const std::uint8_t expected[25] = {
        4U, 3U, 2U, 1U, 6U, 3U, 0U, 0U, 0U, 0U, 0U, 0U, 0U,
        0U, 0U, 0U, 0U, 0U, 64U, 0xC0U, 0U, 0U, 0U, 0U, 0U
    };
    for (std::uint32_t rejection = 1U; rejection <= 3U; ++rejection) {
        logframe::FrameBytes frame;
        CHECK(logframe::packFrame(input, frame) == logframe::PackStatus::OK);
        for (std::size_t byte = 0U; byte < 25U; ++byte) {
            CHECK(frame.data[byte] == expected[byte]);
        }
        CHECK(buffer.overflowed());
        CHECK(buffer.rejectedCount() == rejection);
        CHECK(buffer.size() == 4096U);
        if (rejection < 3U) CHECK_FALSE(buffer.append(encodedEvent(4096U + rejection)));
    }
    checkRetained(buffer, 0U, 0U);
    checkRetained(buffer, 4095U, 4095U);
    // This proves codec/container independence, not frame storage or dump behavior.
}
