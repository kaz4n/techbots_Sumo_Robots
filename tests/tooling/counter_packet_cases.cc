// Tests the public P0 fixed-counter packet and transmit lifecycle contract.
// Uses standard decimal formatting as an independent oracle for opaque firmware.
// Compiled and executed by test_counter_packet.py with doctest on the host.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "bench/p0_matrix/src/counter_packet.h"

#include <array>
#include <cinttypes>
#include <climits>
#include <cstdio>
#include <cstdint>
#include <limits>
#include <string>
#include <vector>

namespace {
using p0::CounterPacket;
using p0::PacketStatus;
constexpr std::uint32_t TIMEOUT_US = 100U;
constexpr std::uint32_t MAX_COUNTER = std::numeric_limits<std::uint32_t>::max();

std::vector<std::uint8_t> expectedNotification(std::uint32_t counter) {
    char text[32] = {};
    const int size = std::snprintf(text, sizeof(text), "P0 counter=%010" PRIu32 "\n", counter);
    REQUIRE(size == 22);
    // MessagePack: array(3), integer(2), string(9), array(1), string(22).
    std::vector<std::uint8_t> expected = {
        0x93U, 0x02U, 0xa9U, 'm', 'o', 'n', '/', 'w', 'r', 'i', 't', 'e', 0x91U, 0xb6U
    };
    expected.insert(expected.end(), text, text + size);
    return expected;
}

std::vector<std::uint8_t> consumeRemaining(CounterPacket& packet) {
    std::vector<std::uint8_t> actual;
    const std::size_t count = packet.remaining();
    REQUIRE(count <= 36U);
    for (std::size_t index = 0; index < count; ++index) {
        INFO("byte index ", index, ", bytes initially remaining ", count);
        std::uint8_t byte = 0U;
        REQUIRE(packet.nextByte(byte));
        actual.push_back(byte);
        packet.accepted(1);
        CHECK(packet.status() == PacketStatus::BUSY);
        CHECK(packet.remaining() == count - index - 1U);
    }
    return actual;
}

void acceptPrefix(CounterPacket& packet, std::size_t count) {
    REQUIRE(count <= 36U);
    for (std::size_t index = 0; index < count; ++index) {
        std::uint8_t ignored = 0U;
        REQUIRE(packet.nextByte(ignored));
        packet.accepted(1);
    }
}

void checkNoNextByte(const CounterPacket& packet) {
    std::uint8_t out = 0xe7U;
    CHECK_FALSE(packet.nextByte(out));
    CHECK(out == 0xe7U);
}

void checkFault(CounterPacket& packet) {
    CHECK(packet.status() == PacketStatus::FAULT);
    CHECK(packet.remaining() == 0U);
    checkNoNextByte(packet);
    CHECK_FALSE(packet.submit(42U, 123U));
    packet.service(124U);
    packet.accepted(1);
    CHECK_FALSE(packet.complete());
    packet.fail();
    CHECK(packet.status() == PacketStatus::FAULT);
    CHECK(packet.remaining() == 0U);
    checkNoNextByte(packet);
}
} // namespace

TEST_CASE("P0 packet contract: valid timeout starts IDLE with exactly 36-byte capacity") {
    CHECK(CounterPacket::SIZE == 36U);
    for (const std::uint32_t timeout : {1U, 100U, 100000U, 0x7fffffffU}) {
        CAPTURE(timeout);
        const CounterPacket packet(timeout);
        CHECK(packet.status() == PacketStatus::IDLE);
        CHECK(packet.remaining() == 0U);
        checkNoNextByte(packet);
    }
}

TEST_CASE("P0 packet contract: zero and half-range-or-larger timeouts start permanent FAULT") {
    for (const std::uint32_t timeout : {0U, 0x80000000U, 0x80000001U, MAX_COUNTER}) {
        CAPTURE(timeout);
        CounterPacket packet(timeout);
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: notification bytes cover zero and decimal boundaries") {
    std::vector<std::uint32_t> counters = {0U, 1U, MAX_COUNTER - 1U, MAX_COUNTER};
    for (std::uint32_t power = 10U; power <= 1000000000U; power *= 10U) {
        counters.push_back(power - 1U);
        counters.push_back(power);
        counters.push_back(power + 1U);
        if (power == 1000000000U) break;
    }
    for (const std::uint32_t counter : counters) {
        CAPTURE(counter);
        CounterPacket packet(TIMEOUT_US);
        REQUIRE(packet.submit(counter, 900U));
        CHECK(packet.status() == PacketStatus::BUSY);
        CHECK(packet.remaining() == 36U);
        CHECK(consumeRemaining(packet) == expectedNotification(counter));
        REQUIRE(packet.complete());
        CHECK(packet.status() == PacketStatus::IDLE);
    }
}

TEST_CASE("P0 packet contract: fixed-seed counter samples all produce full exact notifications") {
    std::uint32_t counter = 0x84ea019bU;
    for (unsigned sample = 0U; sample < 1024U; ++sample) {
        counter = counter * 1664525U + 1013904223U;
        CAPTURE(sample);
        CAPTURE(counter);
        CounterPacket packet(TIMEOUT_US);
        REQUIRE(packet.submit(counter, 25U));
        CHECK(consumeRemaining(packet) == expectedNotification(counter));
        REQUIRE(packet.complete());
    }
}

TEST_CASE("P0 packet contract: nextByte is a read-only peek at every cursor") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(1234567890U, 0U));
    const auto expected = expectedNotification(1234567890U);
    for (std::size_t index = 0; index < expected.size(); ++index) {
        CAPTURE(index);
        const CounterPacket& view = packet;
        for (unsigned peek = 0U; peek < 3U; ++peek) {
            std::uint8_t out = 0U;
            REQUIRE(view.nextByte(out));
            CHECK(out == expected[index]);
            CHECK(view.remaining() == 36U - index);
            CHECK(view.status() == PacketStatus::BUSY);
        }
        packet.accepted(1);
    }
    checkNoNextByte(packet);
    CHECK(packet.status() == PacketStatus::BUSY);
}

TEST_CASE("P0 packet contract: BUSY refusal preserves bytes cursor and submission deadline") {
    for (std::size_t cursor = 0U; cursor <= 36U; ++cursor) {
        CAPTURE(cursor);
        CounterPacket packet(TIMEOUT_US);
        REQUIRE(packet.submit(1098765432U, 1000U));
        acceptPrefix(packet, cursor);
        CHECK_FALSE(packet.submit(MAX_COUNTER, 1050U));
        CHECK(packet.status() == PacketStatus::BUSY);
        CHECK(packet.remaining() == 36U - cursor);
        const auto expected = expectedNotification(1098765432U);
        const std::vector<std::uint8_t> suffix(expected.begin() + cursor, expected.end());
        CHECK(consumeRemaining(packet) == suffix);
        packet.service(1099U);
        CHECK(packet.status() == PacketStatus::BUSY);
        packet.service(1100U);
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: accepting byte 36 remains BUSY until complete") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(7U, 30U));
    acceptPrefix(packet, 35U);
    CHECK(packet.remaining() == 1U);
    packet.accepted(1);
    CHECK(packet.status() == PacketStatus::BUSY);
    CHECK(packet.remaining() == 0U);
    checkNoNextByte(packet);
    CHECK_FALSE(packet.submit(8U, 31U));
    packet.service(129U);
    CHECK(packet.status() == PacketStatus::BUSY);
    REQUIRE(packet.complete());
    CHECK(packet.status() == PacketStatus::IDLE);
    CHECK(packet.remaining() == 0U);
    checkNoNextByte(packet);
}

TEST_CASE("P0 packet contract: deadline still applies while awaiting physical completion") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(7U, 30U));
    acceptPrefix(packet, 36U);
    packet.service(129U);
    CHECK(packet.status() == PacketStatus::BUSY);
    packet.service(130U);
    checkFault(packet);
}

TEST_CASE("P0 packet contract: premature complete faults at every unsent cursor") {
    for (std::size_t cursor = 0U; cursor < 36U; ++cursor) {
        CAPTURE(cursor);
        CounterPacket packet(TIMEOUT_US);
        REQUIRE(packet.submit(8U, 0U));
        acceptPrefix(packet, cursor);
        CHECK_FALSE(packet.complete());
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: complete while IDLE faults") {
    CounterPacket packet(TIMEOUT_US);
    CHECK_FALSE(packet.complete());
    checkFault(packet);
}

TEST_CASE("P0 packet contract: duplicate complete cannot reuse a successful transaction") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(8U, 0U));
    acceptPrefix(packet, 36U);
    REQUIRE(packet.complete());
    CHECK_FALSE(packet.complete());
    checkFault(packet);
}

TEST_CASE("P0 packet contract: only accepted count one is valid while bytes remain") {
    for (const int count : {INT_MIN, -1, 0, 2, 36, INT_MAX}) {
        for (const std::size_t cursor : {0U, 1U, 17U, 35U}) {
            CAPTURE(count);
            CAPTURE(cursor);
            CounterPacket packet(TIMEOUT_US);
            REQUIRE(packet.submit(9U, 0U));
            acceptPrefix(packet, cursor);
            packet.accepted(count);
            checkFault(packet);
        }
    }
}

TEST_CASE("P0 packet contract: accepted faults from IDLE for every representative count") {
    for (const int count : {INT_MIN, -1, 0, 1, 2, INT_MAX}) {
        CAPTURE(count);
        CounterPacket packet(TIMEOUT_US);
        packet.accepted(count);
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: accepting after all 36 bytes faults even with count one") {
    for (const int count : {-1, 0, 1, 2, INT_MAX}) {
        CAPTURE(count);
        CounterPacket packet(TIMEOUT_US);
        REQUIRE(packet.submit(10U, 0U));
        acceptPrefix(packet, 36U);
        packet.accepted(count);
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: accepted after successful completion faults") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(10U, 0U));
    acceptPrefix(packet, 36U);
    REQUIRE(packet.complete());
    packet.accepted(1);
    checkFault(packet);
}

TEST_CASE("P0 packet contract: 100 us timeout stays BUSY through 99 us and faults at 100 us") {
    for (const std::size_t cursor : {0U, 1U, 35U, 36U}) {
        CAPTURE(cursor);
        CounterPacket packet(TIMEOUT_US);
        REQUIRE(packet.submit(11U, 400U));
        acceptPrefix(packet, cursor);
        for (const std::uint32_t now : {400U, 401U, 498U, 499U}) {
            packet.service(now);
            CHECK(packet.status() == PacketStatus::BUSY);
            CHECK(packet.remaining() == 36U - cursor);
        }
        packet.service(500U);
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: first service at 101 us also expires the submission") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(12U, 400U));
    packet.service(501U);
    checkFault(packet);
}

TEST_CASE("P0 packet contract: timeout boundaries survive uint32 clock wrap") {
    for (const std::uint32_t start : {0U, MAX_COUNTER - 101U, MAX_COUNTER - 99U,
                                      MAX_COUNTER - 49U, MAX_COUNTER}) {
        for (const std::uint32_t elapsed : {98U, 99U, 100U, 101U}) {
            CAPTURE(start);
            CAPTURE(elapsed);
            CounterPacket packet(TIMEOUT_US);
            REQUIRE(packet.submit(13U, start));
            acceptPrefix(packet, 17U);
            packet.service(start + elapsed);
            if (elapsed < TIMEOUT_US) {
                CHECK(packet.status() == PacketStatus::BUSY);
                CHECK(packet.remaining() == 19U);
            } else {
                checkFault(packet);
            }
        }
    }
}

TEST_CASE("P0 packet contract: minimum valid timeout expires at one microsecond") {
    CounterPacket packet(1U);
    REQUIRE(packet.submit(14U, MAX_COUNTER));
    packet.service(MAX_COUNTER);
    CHECK(packet.status() == PacketStatus::BUSY);
    packet.service(0U);
    checkFault(packet);
}

TEST_CASE("P0 packet contract: maximum valid timeout has adjacent exact boundary") {
    CounterPacket packet(0x7fffffffU);
    REQUIRE(packet.submit(15U, 0xf0000000U));
    packet.service(0x6ffffffeU);
    CHECK(packet.status() == PacketStatus::BUSY);
    packet.service(0x6fffffffU);
    checkFault(packet);
}

TEST_CASE("P0 packet contract: IDLE service is inert before and after a completed packet") {
    CounterPacket packet(TIMEOUT_US);
    for (const std::uint32_t now : {0U, 100U, MAX_COUNTER}) {
        packet.service(now);
        CHECK(packet.status() == PacketStatus::IDLE);
        CHECK(packet.remaining() == 0U);
    }
    REQUIRE(packet.submit(16U, 0U));
    acceptPrefix(packet, 36U);
    REQUIRE(packet.complete());
    packet.service(100U);
    packet.service(MAX_COUNTER);
    CHECK(packet.status() == PacketStatus::IDLE);
    CHECK(packet.remaining() == 0U);
}

TEST_CASE("P0 packet contract: fail is permanent from IDLE BUSY and fully accepted BUSY") {
    for (const int accepted : {-1, 0, 1, 35, 36}) {
        CAPTURE(accepted);
        CounterPacket packet(TIMEOUT_US);
        if (accepted >= 0) {
            REQUIRE(packet.submit(17U, 20U));
            acceptPrefix(packet, static_cast<std::size_t>(accepted));
        }
        packet.fail();
        checkFault(packet);
    }
}

TEST_CASE("P0 packet contract: fail after successful completion remains terminal") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(18U, 0U));
    acceptPrefix(packet, 36U);
    REQUIRE(packet.complete());
    packet.fail();
    checkFault(packet);
}

TEST_CASE("P0 packet contract: timeout cannot be cured by later service or completion") {
    CounterPacket packet(TIMEOUT_US);
    REQUIRE(packet.submit(19U, MAX_COUNTER - 49U));
    acceptPrefix(packet, 35U);
    packet.service(50U);
    for (const std::uint32_t now : {51U, 1000000U, MAX_COUNTER, 0U}) {
        packet.service(now);
        CHECK(packet.status() == PacketStatus::FAULT);
    }
    checkFault(packet);
}

TEST_CASE("P0 packet contract: repeated successful packets replace payload and reset deadline") {
    CounterPacket packet(TIMEOUT_US);
    std::uint32_t start = MAX_COUNTER - 150U;
    std::uint32_t counter = MAX_COUNTER;
    for (unsigned transaction = 0U; transaction < 256U; ++transaction) {
        CAPTURE(transaction);
        CAPTURE(counter);
        REQUIRE(packet.submit(counter, start));
        CHECK(packet.remaining() == 36U);
        CHECK(consumeRemaining(packet) == expectedNotification(counter));
        packet.service(start + 99U);
        CHECK(packet.status() == PacketStatus::BUSY);
        REQUIRE(packet.complete());
        CHECK(packet.status() == PacketStatus::IDLE);
        checkNoNextByte(packet);
        start += 1000U;
        counter = counter * 1664525U + 1013904223U;
    }
}
