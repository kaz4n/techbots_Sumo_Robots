// Defines one fixed MessagePack notification and its bounded transmit lifecycle.
// Keeps the P0 counter independent of allocation, clocks and RPC responses.
// Verified from the public P0 counter contract by independent host tests.
#pragma once
#include <cstddef>
#include <cstdint>

namespace p0 {
enum class PacketStatus : std::uint8_t { IDLE, BUSY, FAULT };

class CounterPacket {
public:
    static constexpr std::size_t SIZE = 36U;
    explicit CounterPacket(std::uint32_t timeout_us);
    bool submit(std::uint32_t counter, std::uint32_t now_us);
    bool nextByte(std::uint8_t& out) const;
    void accepted(int count);
    bool complete();
    void service(std::uint32_t now_us);
    void fail();
    PacketStatus status() const;
    std::size_t remaining() const;

private:
    std::uint8_t bytes_[SIZE] = {};
    std::size_t cursor_ = 0U;
    std::uint32_t started_us_ = 0U;
    std::uint32_t timeout_us_;
    PacketStatus status_ = PacketStatus::IDLE;
};
} // namespace p0
