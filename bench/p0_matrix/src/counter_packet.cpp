// Packs one fixed counter notification and tracks acceptance versus completion.
// Bounds storage and refuses overlapping or failed diagnostic transmissions.
// Tested through the independent public-contract packet cases on the host.
#include "counter_packet.h"

namespace p0 {
CounterPacket::CounterPacket(std::uint32_t timeout_us) : timeout_us_(timeout_us) {
    if (timeout_us == 0U || timeout_us >= 0x80000000U) {
        fail();
    }
}

bool CounterPacket::submit(std::uint32_t counter, std::uint32_t now_us) {
    if (status_ != PacketStatus::IDLE) {
        return false;
    }
    // Existing MessagePack-RPC: [2, "mon/write", [a 22-byte string]].
    constexpr std::uint8_t prefix[] = {
        0x93, 0x02, 0xa9, 'm', 'o', 'n', '/', 'w', 'r', 'i', 't', 'e',
        0x91, 0xb6, 'P', '0', ' ', 'c', 'o', 'u', 'n', 't', 'e', 'r', '='
    };
    for (std::size_t i = 0; i < sizeof(prefix); ++i) {
        bytes_[i] = prefix[i];
    }
    for (std::size_t digit = 0; digit < 10U; ++digit) {
        bytes_[SIZE - 2U - digit] = static_cast<std::uint8_t>('0' + counter % 10U);
        counter /= 10U;
    }
    bytes_[SIZE - 1U] = '\n';
    cursor_ = 0U;
    started_us_ = now_us;
    status_ = PacketStatus::BUSY;
    return true;
}

bool CounterPacket::nextByte(std::uint8_t& out) const {
    if (status_ != PacketStatus::BUSY || cursor_ == SIZE) {
        return false;
    }
    out = bytes_[cursor_];
    return true;
}

void CounterPacket::accepted(int count) {
    if (status_ != PacketStatus::BUSY || cursor_ == SIZE || count != 1) {
        fail();
        return;
    }
    ++cursor_;
}

bool CounterPacket::complete() {
    if (status_ != PacketStatus::BUSY || cursor_ != SIZE) {
        fail();
        return false;
    }
    status_ = PacketStatus::IDLE;
    return true;
}

void CounterPacket::service(std::uint32_t now_us) {
    if (status_ == PacketStatus::BUSY && now_us - started_us_ >= timeout_us_) {
        fail();
    }
}

void CounterPacket::fail() { status_ = PacketStatus::FAULT; }
PacketStatus CounterPacket::status() const { return status_; }
std::size_t CounterPacket::remaining() const {
    return status_ == PacketStatus::BUSY ? SIZE - cursor_ : 0U;
}
} // namespace p0
