// Checks B15/D102 compact frame ownership against the frozen public contract.
// Prevents lane packing from changing raw evidence, loss accounting or lifetimes.
// Independent literal cases and a fixed-seed deque oracle exercise public APIs.
#include "doctest.h"
#include "hal/recorder_frames.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <deque>
#include <limits>
#include <type_traits>

namespace {
using logframe::PackStatus;
using recorder::StoredFrame;
constexpr std::size_t CAPACITY = 5001U;
constexpr PackStatus STATUSES[] = {
    PackStatus::OK, PackStatus::CLAMPED, PackStatus::INVALID};

logframe::FrameBytes payload(std::uint32_t serial) {
    logframe::FrameBytes result;
    for (std::size_t byte = 0U; byte < 25U; ++byte) {
        result.data[byte] = static_cast<std::uint8_t>(
            (serial >> ((byte % 4U) * 8U)) ^ (serial * 53U + byte * 109U));
    }
    result.data[0] = 0xFFU;
    result.data[1] = 0U;
    result.data[24] = static_cast<std::uint8_t>(serial);
    return result;
}

bool sameBytes(const logframe::FrameBytes& lhs, const logframe::FrameBytes& rhs) {
    return std::memcmp(lhs.data, rhs.data, 25U) == 0;
}

void sameFrame(const StoredFrame& actual, const StoredFrame& expected) {
    CHECK(sameBytes(actual.bytes, expected.bytes));
    CHECK(actual.status == expected.status);
}

struct Oracle {
    std::deque<StoredFrame> rows;
    std::uint32_t overwritten = 0U;
    std::uint32_t rejected = 0U;
    std::uint32_t clamped = 0U;
    std::uint32_t invalid = 0U;

    bool append(const logframe::FrameBytes& bytes, PackStatus status) {
        if (status != PackStatus::OK && status != PackStatus::CLAMPED &&
            status != PackStatus::INVALID) {
            ++rejected;
            return false;
        }
        if (rows.size() == CAPACITY) {
            rows.pop_front();
            ++overwritten;
        }
        rows.push_back({bytes, status});
        if (status == PackStatus::CLAMPED) ++clamped;
        if (status == PackStatus::INVALID) ++invalid;
        return true;
    }

    void counters(const recorder::FrameBuffer& buffer) const {
        CHECK(buffer.size() == rows.size());
        CHECK(buffer.overwrittenCount() == overwritten);
        CHECK(buffer.rejectedStatusCount() == rejected);
        CHECK(buffer.clampedCount() == clamped);
        CHECK(buffer.invalidCount() == invalid);
        CHECK(buffer.incomplete() ==
              (overwritten != 0U || rejected != 0U || clamped != 0U || invalid != 0U));
    }

    void at(const recorder::FrameBuffer& buffer, std::size_t index) const {
        CHECK(index < rows.size());
        if (index >= rows.size()) return;
        StoredFrame actual{payload(0xDEADBEEFU), PackStatus::INVALID};
        const bool present = buffer.read(index, actual);
        CHECK(present);
        if (!present) return;
        sameFrame(actual, rows[index]);
        const auto* borrowed = buffer.bytesAt(index);
        CHECK(borrowed != nullptr);
        if (borrowed == nullptr) return;
        CHECK(sameBytes(*borrowed, rows[index].bytes));
    }

    void all(const recorder::FrameBuffer& buffer) const {
        counters(buffer);
        for (std::size_t index = 0U; index < rows.size(); ++index) at(buffer, index);
    }
};

void append(recorder::FrameBuffer& buffer, Oracle& oracle,
            std::uint32_t serial, PackStatus status) {
    const auto bytes = payload(serial);
    CHECK(buffer.append(bytes, status) == oracle.append(bytes, status));
}

void fill(recorder::FrameBuffer& buffer, Oracle& oracle, std::size_t count,
          std::uint32_t serial = 0U) {
    for (std::size_t index = 0U; index < count; ++index) {
        append(buffer, oracle, serial + static_cast<std::uint32_t>(index),
               STATUSES[index % 3U]);
    }
}

void unchangedFailedRead(const recorder::FrameBuffer& buffer, std::size_t index) {
    const StoredFrame sentinel{payload(0xA5C3F00DU), static_cast<PackStatus>(255U)};
    StoredFrame output = sentinel;
    CHECK_FALSE(buffer.read(index, output));
    sameFrame(output, sentinel);
    CHECK(buffer.bytesAt(index) == nullptr);
}

std::uint32_t nextRandom(std::uint32_t& seed) {
    seed = seed * 1664525U + 1013904223U;
    return seed;
}

void checkEnds(const recorder::FrameBuffer& buffer, const Oracle& oracle) {
    oracle.counters(buffer);
    for (std::size_t index = 0U; index < 8U; ++index) {
        oracle.at(buffer, index);
        oracle.at(buffer, CAPACITY - 1U - index);
    }
}
}  // namespace

TEST_CASE("B15 D102 capacity cadence and compact representation remain bounded") {
    CHECK(config::LOG_HZ == 25U);
    CHECK(config::LOG_FRAME_WINDOW_MS == 200000U);
    CHECK(config::LOG_FRAME_CAPACITY == CAPACITY);
    CHECK(config::LOG_EVENT_CAPACITY == 4096U);
    CHECK(sizeof(logframe::FrameBytes) == 25U);
    CHECK(sizeof(StoredFrame) == 26U);
    CHECK(static_cast<std::uint8_t>(PackStatus::OK) == 0U);
    CHECK(static_cast<std::uint8_t>(PackStatus::CLAMPED) == 1U);
    CHECK(static_cast<std::uint8_t>(PackStatus::INVALID) == 2U);
    // Two indices, four uint32 counters and at most three alignment gaps.
    constexpr std::size_t metadata = 2U * sizeof(std::size_t) +
        4U * sizeof(std::uint32_t) + 3U * alignof(std::max_align_t);
    constexpr std::size_t arrays = CAPACITY * 25U + (CAPACITY + 3U) / 4U;
    CHECK(sizeof(recorder::FrameBuffer) <= arrays + metadata);
    CHECK(sizeof(recorder::FrameBuffer) < CAPACITY * sizeof(StoredFrame));
    CHECK_FALSE(std::is_copy_constructible<recorder::FrameBuffer>::value);
    CHECK_FALSE(std::is_copy_assignable<recorder::FrameBuffer>::value);
}

TEST_CASE("B15 D102 every accepted status occupies all four lanes exactly") {
    for (const auto status : STATUSES) {
        recorder::FrameBuffer buffer;
        Oracle oracle;
        for (std::uint32_t lane = 0U; lane < 8U; ++lane) {
            append(buffer, oracle, 0xFF00U + lane, status);
            oracle.all(buffer);
        }
    }
}

TEST_CASE("B15 D102 mixed adjacent statuses survive every replacement transition") {
    recorder::FrameBuffer buffer;
    Oracle oracle;
    fill(buffer, oracle, CAPACITY);
    oracle.all(buffer);
    // Each physical slot takes OK, CLAMPED, INVALID and OK across four wraps.
    for (unsigned pass = 0U; pass < 4U; ++pass) {
        for (std::size_t slot = 0U; slot < CAPACITY; ++slot) {
            const auto serial = static_cast<std::uint32_t>(10000U + pass * CAPACITY + slot);
            append(buffer, oracle, serial, STATUSES[pass % 3U]);
            checkEnds(buffer, oracle);
            // The next seven retained slots straddle the lane-byte boundary.
            if (slot % 997U == 0U) oracle.all(buffer);
        }
        oracle.all(buffer);
    }
}

TEST_CASE("B15 D102 slot three four final slot and first wrap preserve raw bytes") {
    recorder::FrameBuffer buffer;
    Oracle oracle;
    fill(buffer, oracle, 4U);
    oracle.at(buffer, 3U);
    unchangedFailedRead(buffer, 4U);
    append(buffer, oracle, 4U, PackStatus::INVALID);
    oracle.at(buffer, 3U);
    oracle.at(buffer, 4U);
    fill(buffer, oracle, CAPACITY - 6U, 5U);
    CHECK(buffer.size() == CAPACITY - 1U);
    unchangedFailedRead(buffer, CAPACITY - 1U);
    append(buffer, oracle, 0xFEFFFFFEU, PackStatus::CLAMPED);
    oracle.at(buffer, CAPACITY - 2U);
    oracle.at(buffer, CAPACITY - 1U);
    append(buffer, oracle, 0x00000000U, PackStatus::INVALID);
    oracle.all(buffer);
    CHECK(buffer.overwrittenCount() == 1U);
}

TEST_CASE("B15 D102 fixed seed mixed oracle crosses multiple complete wraps") {
    recorder::FrameBuffer buffer;
    Oracle oracle;
    std::uint32_t seed = 0xD10225A5U;
    for (std::size_t operation = 0U; operation < CAPACITY * 7U; ++operation) {
        const auto value = nextRandom(seed);
        const auto status = value % 13U == 0U ? static_cast<PackStatus>(3U + value % 253U)
                                             : STATUSES[value % 3U];
        if (!oracle.rows.empty() && operation % 17U == 0U) {
            const auto index = static_cast<std::size_t>(nextRandom(seed)) % oracle.rows.size();
            const auto expected = oracle.rows[index].bytes;
            const auto* source = buffer.bytesAt(index);
            CHECK(source != nullptr);
            if (source == nullptr) return;
            CHECK(buffer.append(*source, status) == oracle.append(expected, status));
        } else {
            append(buffer, oracle, nextRandom(seed), status);
        }
        oracle.counters(buffer);
        if (!oracle.rows.empty()) {
            oracle.at(buffer, 0U);
            oracle.at(buffer, oracle.rows.size() - 1U);
            oracle.at(buffer, nextRandom(seed) % oracle.rows.size());
        }
        if (operation % 983U == 0U) oracle.all(buffer);
    }
    CHECK(oracle.overwritten > CAPACITY * 5U);
    oracle.all(buffer);
}

TEST_CASE("B15 D102 logical reset hides old statuses and rewrites every reused lane") {
    recorder::FrameBuffer buffer;
    Oracle oracle;
    for (unsigned cycle = 0U; cycle < 3U; ++cycle) {
        fill(buffer, oracle, CAPACITY + 7U, 100000U * cycle);
        append(buffer, oracle, 0U, static_cast<PackStatus>(255U));
        buffer.reset();
        oracle = Oracle{};
        oracle.counters(buffer);
        unchangedFailedRead(buffer, 0U);
        unchangedFailedRead(buffer, CAPACITY - 1U);
        for (std::size_t index = 0U; index < CAPACITY; ++index) {
            append(buffer, oracle, static_cast<std::uint32_t>(index), STATUSES[cycle]);
            if (index < 9U) oracle.all(buffer);
        }
        oracle.all(buffer);
    }
}

TEST_CASE("B15 D102 all 253 unknown codes reject without touching stored evidence") {
    for (const auto initial : std::array<std::size_t, 4U>{0U, 7U, CAPACITY, CAPACITY + 9U}) {
        recorder::FrameBuffer buffer;
        Oracle oracle;
        fill(buffer, oracle, initial);
        for (unsigned code = 3U; code <= 255U; ++code) {
            CAPTURE(initial);
            CAPTURE(code);
            append(buffer, oracle, 0xF0000000U + code, static_cast<PackStatus>(code));
            oracle.all(buffer);
            CHECK(buffer.rejectedStatusCount() == code - 2U);
            unchangedFailedRead(buffer, oracle.rows.size());
        }
    }
}

TEST_CASE("B15 D102 every out of range read preserves caller output and counters") {
    recorder::FrameBuffer buffer;
    Oracle oracle;
    for (const auto count : std::array<std::size_t, 3U>{0U, 7U, CAPACITY + 3U}) {
        fill(buffer, oracle, count);
        unchangedFailedRead(buffer, buffer.size());
        unchangedFailedRead(buffer, buffer.size() + 1U);
        unchangedFailedRead(buffer, std::numeric_limits<std::size_t>::max());
        unchangedFailedRead(buffer, std::numeric_limits<std::size_t>::max() - 1U);
        oracle.all(buffer);
    }
}

TEST_CASE("B15 D102 caller snapshots survive other reads mutation reset and destruction") {
    std::array<StoredFrame, 12U> outputs{};
    std::array<StoredFrame, 12U> expected{};
    {
        recorder::FrameBuffer buffer;
        Oracle oracle;
        fill(buffer, oracle, outputs.size());
        for (std::size_t index = 0U; index < outputs.size(); ++index) {
            CHECK(buffer.read(index, outputs[index]));
            expected[index] = oracle.rows[index];
        }
        oracle.all(buffer);
        fill(buffer, oracle, CAPACITY * 2U, 999U);
        buffer.reset();
        oracle = Oracle{};
        fill(buffer, oracle, CAPACITY, 100000U);
        for (std::size_t index = 0U; index < outputs.size(); ++index) {
            sameFrame(outputs[index], expected[index]);
        }
    }
    for (std::size_t index = 0U; index < outputs.size(); ++index) {
        sameFrame(outputs[index], expected[index]);
    }
}

TEST_CASE("B15 D102 borrowed payload pointers survive all reads without scratch aliasing") {
    recorder::FrameBuffer buffer;
    Oracle oracle;
    fill(buffer, oracle, CAPACITY + 3U);
    std::array<const logframe::FrameBytes*, CAPACITY> pointers{};
    for (std::size_t index = 0U; index < CAPACITY; ++index) {
        pointers[index] = buffer.bytesAt(index);
        CHECK(pointers[index] != nullptr);
        if (pointers[index] == nullptr) return;
    }
    oracle.all(buffer);
    for (std::size_t index = CAPACITY; index-- > 0U;) {
        CHECK(buffer.bytesAt(index) == pointers[index]);
        CHECK(sameBytes(*pointers[index], oracle.rows[index].bytes));
        if (index > 0U) CHECK(pointers[index] != pointers[index - 1U]);
    }
    oracle.counters(buffer);
}

TEST_CASE("B15 D102 genuine oldest interior newest borrows append before and after full") {
    for (const auto count : std::array<std::size_t, 3U>{8U, CAPACITY, CAPACITY + 6U}) {
        for (const unsigned selection : {0U, 1U, 2U}) {
            recorder::FrameBuffer buffer;
            Oracle oracle;
            fill(buffer, oracle, count);
            const std::size_t indices[] = {0U, oracle.rows.size() / 2U,
                                           oracle.rows.size() - 1U};
            const auto index = indices[selection];
            const auto expected = oracle.rows[index].bytes;
            const auto* source = buffer.bytesAt(index);
            CHECK(source != nullptr);
            if (source == nullptr) return;
            // Use the actual borrowed source, never the detached oracle copy.
            CHECK(buffer.append(*source, STATUSES[selection]));
            CHECK(oracle.append(expected, STATUSES[selection]));
            oracle.all(buffer);
        }
    }
}
