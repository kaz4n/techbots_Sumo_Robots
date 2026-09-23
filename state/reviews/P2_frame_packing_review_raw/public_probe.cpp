// Independently checks the D102 public byte/read/lifetime contract.
// Uses literal status values and chronological expected values, never storage lanes.
// Built in an isolated reviewer directory with ASan/UBSan.
#include "hal/recorder_frames.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <initializer_list>
#include <limits>

using recorder::FrameBuffer;
using recorder::StoredFrame;
using logframe::FrameBytes;
using logframe::PackStatus;
constexpr std::size_t CAPACITY = 5001U;
static unsigned checks = 0;
#define VERIFY(test) do { ++checks; assert(test); } while (false)
FrameBytes pattern(unsigned n) {
    FrameBytes value;
    for (unsigned i = 0; i < 25; ++i)
        value.data[i] = static_cast<unsigned char>((n * 13U + i * 29U) % 251U + 1U);
    value.data[0] = static_cast<unsigned char>(n);
    value.data[1] = static_cast<unsigned char>(n >> 8U);
    value.data[2] = static_cast<unsigned char>(n >> 16U);
    return value;
}
void same(const StoredFrame& a, const StoredFrame& b) {
    VERIFY(a.status == b.status);
    VERIFY(std::memcmp(a.bytes.data, b.bytes.data, 25) == 0);
}
void expected(const FrameBuffer& owner, std::size_t index, unsigned ordinal, unsigned code) {
    StoredFrame value;
    VERIFY(owner.read(index, value));
    const auto bytes = pattern(ordinal);
    VERIFY(std::memcmp(value.bytes.data, bytes.data, 25) == 0);
    VERIFY(static_cast<unsigned>(value.status) == code);
    const auto* borrowed = owner.bytesAt(index);
    VERIFY(borrowed != nullptr);
    VERIFY(std::memcmp(borrowed->data, bytes.data, 25) == 0);
    StoredFrame independent;
    VERIFY(owner.read((index + 117U) % owner.size(), independent));
    VERIFY(owner.bytesAt(index) == borrowed);
    VERIFY(std::memcmp(borrowed->data, bytes.data, 25) == 0);
}
int main() {
    static_assert(sizeof(StoredFrame) == 26U);
    static_assert(config::LOG_FRAME_CAPACITY == CAPACITY && config::LOG_HZ == 25U);
    static_assert(sizeof(FrameBuffer) <= CAPACITY * 25U + (CAPACITY + 3U) / 4U + 64U);
    StoredFrame durable_a, durable_b;
    {
        FrameBuffer owner;
        StoredFrame sentinel{pattern(70000U), static_cast<PackStatus>(255U)};
        const auto before = sentinel;
        for (std::size_t index : {std::size_t{0U}, CAPACITY, std::numeric_limits<std::size_t>::max()}) {
            VERIFY(!owner.read(index, sentinel)); same(sentinel, before);
            VERIFY(owner.bytesAt(index) == nullptr);
        }
        for (unsigned pass = 0U; pass < 6U; ++pass) {
            for (unsigned slot = 0U; slot < CAPACITY; ++slot) {
                const unsigned n = pass * CAPACITY + slot;
                VERIFY(owner.append(pattern(n), static_cast<PackStatus>(pass % 3U)));
                expected(owner, owner.size() - 1U, n, pass % 3U);
                if (pass && slot + 1U < CAPACITY)
                    expected(owner, 0U, (pass - 1U) * CAPACITY + slot + 1U, (pass - 1U) % 3U);
            }
            for (unsigned slot = 0U; slot < CAPACITY; ++slot)
                expected(owner, slot, pass * CAPACITY + slot, pass % 3U);
        }
        VERIFY(owner.overwrittenCount() == CAPACITY * 5U);
        VERIFY(owner.clampedCount() == CAPACITY * 2U);
        VERIFY(owner.invalidCount() == CAPACITY * 2U);
        VERIFY(owner.read(0U, durable_a)); VERIFY(owner.read(CAPACITY - 1U, durable_b));
        const auto saved_a = durable_a, saved_b = durable_b;
        for (unsigned code = 3U; code <= 255U; ++code) {
            const auto* alias = owner.bytesAt(code % CAPACITY);
            VERIFY(alias != nullptr);
            VERIFY(!owner.append(*alias, static_cast<PackStatus>(code)));
            VERIFY(owner.overwrittenCount() == CAPACITY * 5U);
            VERIFY(owner.clampedCount() == CAPACITY * 2U);
            VERIFY(owner.invalidCount() == CAPACITY * 2U);
            for (unsigned slot : {0U, 3U, 4U, 2500U, 5000U})
                expected(owner, slot, CAPACITY * 5U + slot, 2U);
        }
        VERIFY(owner.rejectedStatusCount() == 253U);
        for (std::size_t index : {CAPACITY, CAPACITY + 1U, std::numeric_limits<std::size_t>::max()}) {
            VERIFY(!owner.read(index, sentinel)); same(sentinel, before);
            VERIFY(owner.bytesAt(index) == nullptr);
        }
        for (unsigned source : {0U, 2500U, 5000U}) {
            const auto* alias = owner.bytesAt(source);
            const FrameBytes copied = *alias;
            VERIFY(owner.append(*alias, PackStatus::OK));
            StoredFrame value;
            VERIFY(owner.read(CAPACITY - 1U, value));
            VERIFY(value.status == PackStatus::OK);
            VERIFY(std::memcmp(value.bytes.data, copied.data, 25) == 0);
        }
        // Inspect object representation, not expired borrowed data or private offsets.
        unsigned char representation[sizeof(FrameBuffer)];
        std::memcpy(representation, &owner, sizeof owner);
        owner.reset();
        unsigned char cleared[sizeof(FrameBuffer)];
        std::memcpy(cleared, &owner, sizeof owner);
        unsigned changed = 0;
        for (std::size_t i = 0; i < sizeof owner; ++i) changed += representation[i] != cleared[i];
        VERIFY(changed <= 64U);
        VERIFY(owner.size() == 0U && !owner.incomplete());
        VERIFY(owner.overwrittenCount() == 0U && owner.rejectedStatusCount() == 0U);
        VERIFY(owner.clampedCount() == 0U && owner.invalidCount() == 0U);
        for (unsigned slot = 0U; slot < CAPACITY; ++slot) {
            VERIFY(!owner.read(slot, sentinel)); same(sentinel, before);
            VERIFY(owner.bytesAt(slot) == nullptr);
            VERIFY(owner.append(pattern(slot), static_cast<PackStatus>(slot % 3U)));
            expected(owner, slot, slot, slot % 3U);
        }
        same(durable_a, saved_a); same(durable_b, saved_b);
    }
    const StoredFrame expected_a{pattern(CAPACITY * 5U), PackStatus::INVALID};
    const StoredFrame expected_b{pattern(CAPACITY * 6U - 1U), PackStatus::INVALID};
    same(durable_a, expected_a); same(durable_b, expected_b);
    std::printf("D102 independent public probe PASS: %u checks, FrameBuffer=%zu align=%zu StoredFrame=%zu\n",
                checks, sizeof(FrameBuffer), alignof(FrameBuffer), sizeof(StoredFrame));
}
