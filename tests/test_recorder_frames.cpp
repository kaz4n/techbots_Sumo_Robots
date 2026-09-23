// Checks B15/D-069 fixed frame retention against the approved public contract.
// Keeps byte ownership, ordering and incomplete evidence independent of the codec.
// Independent doctest fixtures and a seeded deque oracle cover boundaries and reuse.
#include "doctest.h"
#include "hal/recorder_frames.h"
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <deque>
#include <initializer_list>
#include <limits>
#include <type_traits>
#include <vector>

namespace {
constexpr std::size_t APPROVED_CAPACITY = 10001U;
using logframe::PackStatus;

logframe::FrameBytes ordinalBytes(std::uint32_t ordinal) {
    logframe::FrameBytes bytes;
    for (std::size_t index = 0U; index < 25U; ++index) {
        bytes.data[index] = static_cast<std::uint8_t>(ordinal * 37U + index * 19U);
    }
    for (std::size_t index = 0U; index < 4U; ++index) {
        bytes.data[index] = static_cast<std::uint8_t>(ordinal >> (8U * index));
    }
    return bytes;
}

void checkRecord(const recorder::FrameBuffer& buffer, std::size_t index,
                 const logframe::FrameBytes& expected, PackStatus status) {
    CAPTURE(index);
    const auto* record = buffer.at(index);
    CHECK(record != nullptr);
    if (record == nullptr) return;
    CHECK(std::memcmp(record->bytes.data, expected.data, 25U) == 0);
    CHECK(record->status == status);
}

void checkLiteral(const recorder::FrameBuffer& buffer, std::size_t index,
                  const std::uint8_t (&expected)[26]) {
    const auto* record = buffer.at(index);
    CHECK(record != nullptr);
    if (record == nullptr) return;
    for (std::size_t byte = 0U; byte < 25U; ++byte) {
        CAPTURE(index);
        CAPTURE(byte);
        CHECK(record->bytes.data[byte] == expected[byte]);
    }
    CHECK(static_cast<std::uint8_t>(record->status) == expected[25]);
}

void fillFrames(recorder::FrameBuffer& buffer, std::size_t count,
                std::uint32_t first = 0U) {
    for (std::size_t index = 0U; index < count; ++index) {
        const bool accepted = buffer.append(
            ordinalBytes(first + static_cast<std::uint32_t>(index)), PackStatus::OK);
        CHECK(accepted);
        if (!accepted) return;
    }
}

void checkClean(const recorder::FrameBuffer& buffer) {
    CHECK(buffer.overwrittenCount() == 0U);
    CHECK(buffer.rejectedStatusCount() == 0U);
    CHECK(buffer.clampedCount() == 0U);
    CHECK(buffer.invalidCount() == 0U);
    CHECK_FALSE(buffer.incomplete());
}

std::vector<recorder::StoredFrame> snapshot(const recorder::FrameBuffer& buffer) {
    std::vector<recorder::StoredFrame> records;
    for (std::size_t index = 0U; index < buffer.size(); ++index) {
        const auto* record = buffer.at(index);
        CHECK(record != nullptr);
        if (record == nullptr) return records;
        records.push_back(*record);
    }
    return records;
}

void checkSnapshot(const recorder::FrameBuffer& buffer,
                   const std::vector<recorder::StoredFrame>& expected) {
    CHECK(buffer.size() == expected.size());
    if (buffer.size() != expected.size()) return;
    for (std::size_t index = 0U; index < expected.size(); ++index) {
        checkRecord(buffer, index, expected[index].bytes, expected[index].status);
    }
}

struct ExpectedFrames {
    std::deque<recorder::StoredFrame> records;
    std::uint32_t overwritten = 0U;
    std::uint32_t rejected = 0U;
    std::uint32_t clamped = 0U;
    std::uint32_t invalid = 0U;
};

bool remember(ExpectedFrames& expected, const logframe::FrameBytes& bytes,
              PackStatus status) {
    if (status != PackStatus::OK && status != PackStatus::CLAMPED &&
        status != PackStatus::INVALID) {
        ++expected.rejected;
        return false;
    }
    expected.records.push_back({bytes, status});
    if (expected.records.size() > APPROVED_CAPACITY) {
        expected.records.pop_front();
        ++expected.overwritten;
    }
    if (status == PackStatus::CLAMPED) ++expected.clamped;
    if (status == PackStatus::INVALID) ++expected.invalid;
    return true;
}

void checkCounts(const recorder::FrameBuffer& buffer, const ExpectedFrames& expected) {
    CHECK(buffer.size() == expected.records.size());
    CHECK(buffer.overwrittenCount() == expected.overwritten);
    CHECK(buffer.rejectedStatusCount() == expected.rejected);
    CHECK(buffer.clampedCount() == expected.clamped);
    CHECK(buffer.invalidCount() == expected.invalid);
    const bool incomplete = expected.overwritten != 0U || expected.rejected != 0U ||
                            expected.clamped != 0U || expected.invalid != 0U;
    CHECK(buffer.incomplete() == incomplete);
    CHECK(buffer.at(expected.records.size()) == nullptr);
    CHECK(buffer.at(std::numeric_limits<std::size_t>::max()) == nullptr);
}

void checkOracle(const recorder::FrameBuffer& buffer, const ExpectedFrames& expected) {
    checkCounts(buffer, expected);
    for (std::size_t index = 0U; index < expected.records.size(); ++index) {
        checkRecord(buffer, index, expected.records[index].bytes,
                    expected.records[index].status);
    }
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed = 1664525U * seed + 1013904223U;
    return seed;
}

logframe::FrameBytes randomBytes(std::uint32_t& seed) {
    logframe::FrameBytes bytes;
    for (auto& byte : bytes.data) {
        byte = static_cast<std::uint8_t>(nextRandom(seed) >> 24U);
    }
    return bytes;
}
} // namespace

TEST_CASE("B15 D069 literal capacity includes 200 second endpoints and 26 byte records") {
    CHECK(config::LOG_HZ == 50U);
    CHECK(config::LOG_FRAME_WINDOW_MS == 200000U);
    CHECK(config::LOG_FRAME_CAPACITY == APPROVED_CAPACITY);
    CHECK(logframe::FRAME_BYTES == 25U);
    CHECK(sizeof(recorder::StoredFrame) == 26U);
    CHECK(sizeof(recorder::StoredFrame) * config::LOG_FRAME_CAPACITY == 260026U);
    CHECK(sizeof(recorder::StoredFrame) * config::LOG_FRAME_CAPACITY +
          8U * config::LOG_EVENT_CAPACITY == 292794U);
    CHECK_FALSE(std::is_copy_constructible<recorder::FrameBuffer>::value);
    CHECK_FALSE(std::is_copy_assignable<recorder::FrameBuffer>::value);
}

TEST_CASE("B15 D069 empty frame storage has no visible entries or incomplete evidence") {
    recorder::FrameBuffer buffer;
    CHECK(buffer.size() == 0U);
    checkClean(buffer);
    CHECK(buffer.at(0U) == nullptr);
    CHECK(buffer.at(APPROVED_CAPACITY - 1U) == nullptr);
    CHECK(buffer.at(APPROVED_CAPACITY) == nullptr);
    CHECK(buffer.at(std::numeric_limits<std::size_t>::max()) == nullptr);
}

TEST_CASE("B15 D069 literal OK CLAMPED and INVALID records retain all supplied bytes") {
    const std::uint8_t expected[3][26] = {
        {0x78, 0x56, 0x34, 0x12, 6, 5, 9, 0x45, 0x1F, 0x50, 0xFF, 0xFF,
         0x83, 0xFF, 0xE2, 4, 0x0C, 0xFE, 0x40, 0xC0, 0xE2, 4, 15, 0x34, 0x12, 0},
        {0xFF, 0xFF, 0xFF, 0xFF, 0, 1, 0, 0, 0xFF, 0xFF, 0xFF, 0x7F,
         0xFF, 0x7F, 0xFF, 0x7F, 0, 0x80, 0x7F, 0x81, 0xFF, 0xFF, 0, 0xFF, 0xFF, 1},
        {0xA5, 0x5A, 0xFF, 0, 0xFE, 0xFD, 0xFC, 0xFB, 0xFA, 0xF9, 0xF8, 0xF7,
         0xF6, 0xF5, 0xF4, 0xF3, 0xF2, 0xF1, 0xF0, 0xEF, 0xEE, 0xED, 0xEC, 0xEB, 0xEA, 2}
    };
    const PackStatus statuses[] = {PackStatus::OK, PackStatus::CLAMPED, PackStatus::INVALID};
    recorder::FrameBuffer buffer;
    for (std::size_t index = 0U; index < 3U; ++index) {
        logframe::FrameBytes bytes;
        std::memcpy(bytes.data, expected[index], 25U);
        CHECK(buffer.append(bytes, statuses[index]));
        checkLiteral(buffer, index, expected[index]);
    }
    CHECK(buffer.size() == 3U);
    CHECK(buffer.clampedCount() == 1U);
    CHECK(buffer.invalidCount() == 1U);
    CHECK(buffer.overwrittenCount() == 0U);
    CHECK(buffer.rejectedStatusCount() == 0U);
    CHECK(buffer.incomplete());
}

TEST_CASE("B15 D069 every known status independently sets only its evidence counter") {
    recorder::FrameBuffer buffer;
    const PackStatus statuses[] = {PackStatus::OK, PackStatus::CLAMPED, PackStatus::INVALID};
    for (auto status : statuses) {
        buffer.reset();
        CHECK(buffer.append(ordinalBytes(9U), status));
        CHECK(buffer.size() == 1U);
        CHECK(buffer.overwrittenCount() == 0U);
        CHECK(buffer.rejectedStatusCount() == 0U);
        CHECK(buffer.clampedCount() == (status == PackStatus::CLAMPED ? 1U : 0U));
        CHECK(buffer.invalidCount() == (status == PackStatus::INVALID ? 1U : 0U));
        CHECK(buffer.incomplete() == (status != PackStatus::OK));
        checkRecord(buffer, 0U, ordinalBytes(9U), status);
    }
}

TEST_CASE("B15 D069 append owns an exact value copy beyond caller mutation and lifetime") {
    recorder::FrameBuffer buffer;
    {
        auto bytes = ordinalBytes(829U);
        CHECK(buffer.append(bytes, PackStatus::CLAMPED));
        for (auto& byte : bytes.data) byte = 0U;
        checkRecord(buffer, 0U, ordinalBytes(829U), PackStatus::CLAMPED);
    }
    checkRecord(buffer, 0U, ordinalBytes(829U), PackStatus::CLAMPED);
    CHECK(buffer.clampedCount() == 1U);
}

TEST_CASE("B15 D069 capacity minus one exact capacity and plus one evict only oldest") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY - 1U);
    CHECK(buffer.size() == 10000U);
    CHECK(buffer.at(10000U) == nullptr);
    checkClean(buffer);
    CHECK(buffer.append(ordinalBytes(10000U), PackStatus::OK));
    CHECK(buffer.size() == 10001U);
    CHECK(buffer.at(10001U) == nullptr);
    checkClean(buffer);
    checkRecord(buffer, 0U, ordinalBytes(0U), PackStatus::OK);
    checkRecord(buffer, 10000U, ordinalBytes(10000U), PackStatus::OK);
    CHECK(buffer.append(ordinalBytes(10001U), PackStatus::OK));
    CHECK(buffer.size() == 10001U);
    CHECK(buffer.overwrittenCount() == 1U);
    CHECK(buffer.incomplete());
    CHECK(buffer.rejectedStatusCount() == 0U);
    CHECK(buffer.clampedCount() == 0U);
    CHECK(buffer.invalidCount() == 0U);
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        checkRecord(buffer, index, ordinalBytes(static_cast<std::uint32_t>(index + 1U)),
                    PackStatus::OK);
    }
}

TEST_CASE("B15 D069 50 Hz samples retain both literal zero and 200000 ms endpoints") {
    recorder::FrameBuffer buffer;
    for (std::uint32_t t_ms = 0U; t_ms <= 200000U; t_ms += 20U) {
        const bool accepted = buffer.append(ordinalBytes(t_ms), PackStatus::OK);
        CHECK(accepted);
        if (!accepted) return;
    }
    CHECK(buffer.size() == 10001U);
    checkClean(buffer);
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        checkRecord(buffer, index, ordinalBytes(static_cast<std::uint32_t>(index * 20U)),
                    PackStatus::OK);
    }
}

TEST_CASE("B15 D069 final off cadence sample fits after all preceding 50 Hz samples") {
    recorder::FrameBuffer buffer;
    for (std::uint32_t t_ms = 0U; t_ms < 199999U; t_ms += 20U) {
        const bool accepted = buffer.append(ordinalBytes(t_ms), PackStatus::OK);
        CHECK(accepted);
        if (!accepted) return;
    }
    CHECK(buffer.size() == 10000U);
    CHECK(buffer.append(ordinalBytes(199999U), PackStatus::OK));
    CHECK(buffer.size() == 10001U);
    checkRecord(buffer, 0U, ordinalBytes(0U), PackStatus::OK);
    checkRecord(buffer, 9999U, ordinalBytes(199980U), PackStatus::OK);
    checkRecord(buffer, 10000U, ordinalBytes(199999U), PackStatus::OK);
    checkClean(buffer);
}

TEST_CASE("B15 D069 multiple complete wraps preserve every byte in chronological order") {
    recorder::FrameBuffer buffer;
    constexpr std::size_t total = APPROVED_CAPACITY * 4U + 37U;
    fillFrames(buffer, total);
    CHECK(buffer.size() == APPROVED_CAPACITY);
    CHECK(buffer.overwrittenCount() == total - APPROVED_CAPACITY);
    CHECK(buffer.incomplete());
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        const auto ordinal = static_cast<std::uint32_t>(total - APPROVED_CAPACITY + index);
        checkRecord(buffer, index, ordinalBytes(ordinal), PackStatus::OK);
    }
    CHECK(buffer.at(APPROVED_CAPACITY) == nullptr);
    CHECK(buffer.at(std::numeric_limits<std::size_t>::max()) == nullptr);
}

TEST_CASE("B15 D069 timestamps remain opaque through equal descending and wrapped values") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY - 3U);
    const std::uint32_t timestamps[] = {0xFFFFFFFFU, 0U, 0U, 19U, 7U};
    std::vector<logframe::FrameBytes> records;
    for (std::size_t index = 0U; index < 5U; ++index) {
        auto bytes = ordinalBytes(timestamps[index]);
        bytes.data[24] = static_cast<std::uint8_t>(index);
        records.push_back(bytes);
        const bool accepted = buffer.append(bytes, PackStatus::OK);
        CHECK(accepted);
        if (!accepted) return;
    }
    CHECK(buffer.overwrittenCount() == 2U);
    for (std::size_t index = 0U; index < records.size(); ++index) {
        checkRecord(buffer, APPROVED_CAPACITY - 5U + index, records[index], PackStatus::OK);
    }
}

TEST_CASE("B15 D069 const lookup rejects size capacity and SIZE_MAX without mutation") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, 7U);
    const recorder::FrameBuffer& view = buffer;
    const auto expected = snapshot(buffer);
    CHECK(view.at(7U) == nullptr);
    CHECK(view.at(APPROVED_CAPACITY - 1U) == nullptr);
    CHECK(view.at(APPROVED_CAPACITY) == nullptr);
    CHECK(view.at(std::numeric_limits<std::size_t>::max()) == nullptr);
    checkSnapshot(buffer, expected);
    checkClean(buffer);
}

TEST_CASE("B15 D069 every unknown status is rejected while empty and only rejection counts") {
    recorder::FrameBuffer buffer;
    for (unsigned code = 3U; code <= 255U; ++code) {
        CAPTURE(code);
        CHECK_FALSE(buffer.append(ordinalBytes(code), static_cast<PackStatus>(code)));
        CHECK(buffer.size() == 0U);
        CHECK(buffer.rejectedStatusCount() == code - 2U);
        CHECK(buffer.overwrittenCount() == 0U);
        CHECK(buffer.clampedCount() == 0U);
        CHECK(buffer.invalidCount() == 0U);
        CHECK(buffer.incomplete());
        CHECK(buffer.at(0U) == nullptr);
    }
    CHECK(buffer.append(ordinalBytes(77U), PackStatus::OK));
    checkRecord(buffer, 0U, ordinalBytes(77U), PackStatus::OK);
    CHECK(buffer.rejectedStatusCount() == 253U);
    CHECK(buffer.incomplete());
}

TEST_CASE("B15 D069 full unknown status rejection preserves clean retained data and order") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY);
    const auto expected = snapshot(buffer);
    for (unsigned code = 3U; code <= 255U; ++code) {
        CHECK_FALSE(buffer.append(ordinalBytes(code), static_cast<PackStatus>(code)));
        CHECK(buffer.size() == APPROVED_CAPACITY);
        CHECK(buffer.overwrittenCount() == 0U);
        CHECK(buffer.rejectedStatusCount() == code - 2U);
        CHECK(buffer.clampedCount() == 0U);
        CHECK(buffer.invalidCount() == 0U);
        CHECK(buffer.incomplete());
    }
    checkSnapshot(buffer, expected);
    CHECK(buffer.append(ordinalBytes(10001U), PackStatus::OK));
    CHECK(buffer.overwrittenCount() == 1U);
    CHECK(buffer.rejectedStatusCount() == 253U);
    checkRecord(buffer, 0U, ordinalBytes(1U), PackStatus::OK);
    checkRecord(buffer, 10000U, ordinalBytes(10001U), PackStatus::OK);
}

TEST_CASE("B15 D069 mixed status totals include accepted records after those records are evicted") {
    recorder::FrameBuffer buffer;
    CHECK(buffer.append(ordinalBytes(0U), PackStatus::CLAMPED));
    CHECK(buffer.append(ordinalBytes(1U), PackStatus::INVALID));
    fillFrames(buffer, APPROVED_CAPACITY, 2U);
    CHECK(buffer.overwrittenCount() == 2U);
    CHECK(buffer.clampedCount() == 1U);
    CHECK(buffer.invalidCount() == 1U);
    CHECK(buffer.rejectedStatusCount() == 0U);
    CHECK(buffer.incomplete());
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        checkRecord(buffer, index, ordinalBytes(static_cast<std::uint32_t>(index + 2U)),
                    PackStatus::OK);
    }
    CHECK(buffer.append(ordinalBytes(10003U), PackStatus::CLAMPED));
    CHECK(buffer.append(ordinalBytes(10004U), PackStatus::INVALID));
    CHECK(buffer.clampedCount() == 2U);
    CHECK(buffer.invalidCount() == 2U);
    CHECK(buffer.overwrittenCount() == 4U);
    checkRecord(buffer, 9999U, ordinalBytes(10003U), PackStatus::CLAMPED);
    checkRecord(buffer, 10000U, ordinalBytes(10004U), PackStatus::INVALID);
}

TEST_CASE("B15 D069 rejection after mixed status wraps preserves all other counters and contents") {
    recorder::FrameBuffer buffer;
    CHECK(buffer.append(ordinalBytes(0U), PackStatus::CLAMPED));
    CHECK(buffer.append(ordinalBytes(1U), PackStatus::INVALID));
    fillFrames(buffer, APPROVED_CAPACITY + 7U, 2U);
    CHECK(buffer.append(ordinalBytes(10010U), PackStatus::INVALID));
    const auto expected = snapshot(buffer);
    for (unsigned code : {3U, 4U, 127U, 128U, 254U, 255U}) {
        CHECK_FALSE(buffer.append(ordinalBytes(code), static_cast<PackStatus>(code)));
        CHECK(buffer.overwrittenCount() == 10U);
        CHECK(buffer.clampedCount() == 1U);
        CHECK(buffer.invalidCount() == 2U);
        checkSnapshot(buffer, expected);
    }
    CHECK(buffer.rejectedStatusCount() == 6U);
}

TEST_CASE("B15 D069 a retained partial buffer source can append with an independent status") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, 8U);
    const auto* source = buffer.at(3U);
    CHECK(source != nullptr);
    if (source == nullptr) return;
    const auto expected = source->bytes;
    CHECK(buffer.append(source->bytes, PackStatus::INVALID));
    checkRecord(buffer, 3U, expected, PackStatus::OK);
    checkRecord(buffer, 8U, expected, PackStatus::INVALID);
    CHECK(buffer.size() == 9U);
    CHECK(buffer.invalidCount() == 1U);
    CHECK(buffer.overwrittenCount() == 0U);
}

TEST_CASE("B15 D069 full oldest source survives replacement of its own destination") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY);
    const auto* source = buffer.at(0U);
    CHECK(source != nullptr);
    if (source == nullptr) return;
    const auto expected = source->bytes;
    CHECK(buffer.append(source->bytes, PackStatus::CLAMPED));
    CHECK(buffer.overwrittenCount() == 1U);
    CHECK(buffer.clampedCount() == 1U);
    checkRecord(buffer, 0U, ordinalBytes(1U), PackStatus::OK);
    checkRecord(buffer, APPROVED_CAPACITY - 2U, ordinalBytes(10000U), PackStatus::OK);
    checkRecord(buffer, APPROVED_CAPACITY - 1U, expected, PackStatus::CLAMPED);
}

TEST_CASE("B15 D069 wrapped interior and newest borrowed sources preserve bytes and ordering") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY + 17U);
    const auto* middle = buffer.at(5000U);
    CHECK(middle != nullptr);
    if (middle == nullptr) return;
    const auto expected = middle->bytes;
    CHECK(buffer.append(middle->bytes, PackStatus::INVALID));
    checkRecord(buffer, 4999U, expected, PackStatus::OK);
    checkRecord(buffer, 10000U, expected, PackStatus::INVALID);
    const auto* newest = buffer.at(10000U);
    CHECK(newest != nullptr);
    if (newest == nullptr) return;
    CHECK(buffer.append(newest->bytes, PackStatus::CLAMPED));
    checkRecord(buffer, 9999U, expected, PackStatus::INVALID);
    checkRecord(buffer, 10000U, expected, PackStatus::CLAMPED);
    checkRecord(buffer, 0U, ordinalBytes(19U), PackStatus::OK);
    CHECK(buffer.overwrittenCount() == 19U);
    CHECK(buffer.invalidCount() == 1U);
    CHECK(buffer.clampedCount() == 1U);
}

TEST_CASE("B15 D069 rejecting a borrowed source leaves its record and order intact") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY + 5U);
    const auto expected = snapshot(buffer);
    const auto* source = buffer.at(0U);
    CHECK(source != nullptr);
    if (source == nullptr) return;
    CHECK_FALSE(buffer.append(source->bytes, static_cast<PackStatus>(255U)));
    checkSnapshot(buffer, expected);
    CHECK(buffer.overwrittenCount() == 5U);
    CHECK(buffer.rejectedStatusCount() == 1U);
    CHECK(buffer.clampedCount() == 0U);
    CHECK(buffer.invalidCount() == 0U);
}

TEST_CASE("B15 D069 reset hides every old entry and clears all four lifetime counters") {
    recorder::FrameBuffer buffer;
    fillFrames(buffer, APPROVED_CAPACITY + 9U);
    CHECK(buffer.append(ordinalBytes(22U), PackStatus::CLAMPED));
    CHECK(buffer.append(ordinalBytes(23U), PackStatus::INVALID));
    CHECK_FALSE(buffer.append(ordinalBytes(24U), static_cast<PackStatus>(255U)));
    buffer.reset();
    CHECK(buffer.size() == 0U);
    checkClean(buffer);
    for (std::size_t index = 0U; index <= APPROVED_CAPACITY; ++index) {
        CHECK(buffer.at(index) == nullptr);
    }
    CHECK(buffer.at(std::numeric_limits<std::size_t>::max()) == nullptr);
    CHECK(buffer.append(ordinalBytes(91U), PackStatus::OK));
    checkRecord(buffer, 0U, ordinalBytes(91U), PackStatus::OK);
    CHECK(buffer.at(1U) == nullptr);
    checkClean(buffer);
}

TEST_CASE("B15 D069 repeated reset restores full capacity after partial and wrapped runs") {
    recorder::FrameBuffer buffer;
    buffer.reset();
    fillFrames(buffer, 31U);
    buffer.reset();
    buffer.reset();
    fillFrames(buffer, APPROVED_CAPACITY + 2U);
    buffer.reset();
    fillFrames(buffer, APPROVED_CAPACITY, 100000U);
    CHECK(buffer.size() == APPROVED_CAPACITY);
    checkClean(buffer);
    for (std::size_t index = 0U; index < APPROVED_CAPACITY; ++index) {
        checkRecord(buffer, index, ordinalBytes(100000U + static_cast<std::uint32_t>(index)),
                    PackStatus::OK);
    }
    CHECK(buffer.append(ordinalBytes(110001U), PackStatus::OK));
    CHECK(buffer.overwrittenCount() == 1U);
    checkRecord(buffer, 0U, ordinalBytes(100001U), PackStatus::OK);
}

TEST_CASE("B15 D069 frame instances own independent contents counters and reset state") {
    recorder::FrameBuffer first;
    recorder::FrameBuffer second;
    fillFrames(first, APPROVED_CAPACITY + 1U);
    CHECK(first.append(ordinalBytes(51U), PackStatus::INVALID));
    CHECK(second.append(ordinalBytes(99U), PackStatus::OK));
    first.reset();
    CHECK(first.size() == 0U);
    checkClean(first);
    CHECK(second.size() == 1U);
    checkRecord(second, 0U, ordinalBytes(99U), PackStatus::OK);
    checkClean(second);
}

TEST_CASE("B15 D069 D028 event overflow does not stop frame recording or mark local frame loss") {
    recorder::FrameBuffer frames;
    logframe::EventBuffer events;
    const logframe::EventBytes event{{0x78, 0x56, 0x34, 0x12, 9, 0xAB, 0xCD, 0xEF}};
    for (std::size_t index = 0U; index < 4096U; ++index) {
        const bool accepted = events.append(event);
        CHECK(accepted);
        if (!accepted) return;
    }
    CHECK_FALSE(events.append(event));
    CHECK(events.overflowed());
    fillFrames(frames, APPROVED_CAPACITY);
    checkClean(frames);
    checkRecord(frames, 10000U, ordinalBytes(10000U), PackStatus::OK);
    CHECK(events.size() == 4096U);
    CHECK(events.rejectedCount() == 1U);
    frames.reset();
    CHECK(events.size() == 4096U);
    CHECK(events.overflowed());
    CHECK(events.rejectedCount() == 1U);
    const auto* retained = events.at(0U);
    CHECK(retained != nullptr);
    if (retained == nullptr) return;
    CHECK(std::memcmp(retained->data, event.data, 8U) == 0);
}

TEST_CASE("B15 D069 D028 degraded frame storage neither rejects events nor resets with events") {
    recorder::FrameBuffer frames;
    logframe::EventBuffer events;
    fillFrames(frames, APPROVED_CAPACITY + 1U);
    CHECK(frames.append(ordinalBytes(1U), PackStatus::CLAMPED));
    CHECK(frames.append(ordinalBytes(2U), PackStatus::INVALID));
    CHECK_FALSE(frames.append(ordinalBytes(3U), static_cast<PackStatus>(3U)));
    const auto expected = snapshot(frames);
    const logframe::EventBytes event{{0xFF, 0xFF, 0xFF, 0xFF, 4, 7, 0x34, 0x12}};
    CHECK(events.append(event));
    CHECK_FALSE(events.overflowed());
    CHECK(events.rejectedCount() == 0U);
    const auto* retained = events.at(0U);
    CHECK(retained != nullptr);
    if (retained == nullptr) return;
    CHECK(std::memcmp(retained->data, event.data, 8U) == 0);
    events.reset();
    checkSnapshot(frames, expected);
    CHECK(frames.overwrittenCount() == 3U);
    CHECK(frames.rejectedStatusCount() == 1U);
    CHECK(frames.clampedCount() == 1U);
    CHECK(frames.invalidCount() == 1U);
    CHECK(frames.incomplete());
}

TEST_CASE("B15 D069 fixed seed deque oracle checks mixed statuses aliasing wraps and reuse") {
    recorder::FrameBuffer buffer;
    ExpectedFrames expected;
    std::uint32_t seed = 0xB150D069U;
    const PackStatus statuses[] = {PackStatus::OK, PackStatus::CLAMPED,
                                  PackStatus::INVALID, PackStatus::OK,
                                  static_cast<PackStatus>(3U), static_cast<PackStatus>(255U)};
    for (unsigned attempt = 0U; attempt < 3U; ++attempt) {
        buffer.reset();
        expected = ExpectedFrames{};
        checkOracle(buffer, expected);
        for (std::size_t step = 0U; step < 4U * APPROVED_CAPACITY + 23U; ++step) {
            CAPTURE(attempt);
            CAPTURE(step);
            const auto choice = nextRandom(seed);
            const auto status = statuses[(choice >> 16U) % 6U];
            auto bytes = randomBytes(seed);
            bool accepted = false;
            if (!expected.records.empty() && choice % 11U == 0U) {
                const std::size_t index = (choice >> 8U) % expected.records.size();
                bytes = expected.records[index].bytes;
                const auto* borrowed = buffer.at(index);
                CHECK(borrowed != nullptr);
                if (borrowed == nullptr) return;
                accepted = buffer.append(borrowed->bytes, status);
            } else {
                accepted = buffer.append(bytes, status);
            }
            CHECK(accepted == remember(expected, bytes, status));
            checkCounts(buffer, expected);
            if (!expected.records.empty()) {
                checkRecord(buffer, 0U, expected.records.front().bytes,
                            expected.records.front().status);
                checkRecord(buffer, expected.records.size() - 1U,
                            expected.records.back().bytes, expected.records.back().status);
            }
            if (step % 4096U == 0U) checkOracle(buffer, expected);
        }
        CHECK(expected.overwritten > APPROVED_CAPACITY);
        CHECK(expected.rejected > 0U);
        CHECK(expected.clamped > 0U);
        CHECK(expected.invalid > 0U);
        checkOracle(buffer, expected);
    }
}
