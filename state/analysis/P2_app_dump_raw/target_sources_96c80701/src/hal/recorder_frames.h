// Declares bounded B15 frame storage with explicit retained codec status.
// Keeps RAM ownership separate from cadence, Robot lifecycle and dump transport.
// Independent D-069 host tests cover ordering, overwrite, status and logical reset.
#pragma once

#include "../core/logframe.h"
#include "../config.h"
#include <cstddef>
#include <cstdint>

namespace recorder {

struct StoredFrame {
    logframe::FrameBytes bytes;
    logframe::PackStatus status = logframe::PackStatus::INVALID;
};
static_assert(sizeof(StoredFrame) == logframe::FRAME_BYTES + 1U,
              "Frame storage must preserve the 25-byte payload plus status");
static_assert(config::LOG_HZ > 0U && config::LOG_FRAME_CAPACITY > 0U,
              "Frame storage requires a positive cadence and capacity");

class FrameBuffer {
public:
    // Create the fixed owner before the control loop; never copy a whole buffer.
    FrameBuffer() = default;
    FrameBuffer(const FrameBuffer&) = delete;
    FrameBuffer& operator=(const FrameBuffer&) = delete;
    // D-069: preserve exact bytes and known OK/CLAMPED/INVALID status. Accept even
    // INVALID codec records as visibly invalid evidence. Unknown enum rejects,
    // increments rejectedStatusCount and leaves contents/order/other counts intact.
    // A full buffer replaces exactly the oldest entry and counts that overwrite.
    bool append(const logframe::FrameBytes& bytes, logframe::PackStatus status);
    std::size_t size() const;
    // Insertion order, oldest first; timestamp values are opaque, never sorted.
    // Null outside size. Borrowed pointer must not survive append/reset/destruction.
    const StoredFrame* at(std::size_t chronological_index) const;
    std::uint32_t overwrittenCount() const;
    std::uint32_t rejectedStatusCount() const;
    // Attempt-lifetime accepted counts, including entries subsequently overwritten.
    std::uint32_t clampedCount() const;
    std::uint32_t invalidCount() const;
    // Any overwrite, rejection, clamped or invalid record means incomplete evidence.
    bool incomplete() const;
    // Constant logical clear, no array clearing. Only the future owner may invoke
    // this for a new accepted attempt; Robot reset/services must not imply a clear.
    void reset();
private:
    StoredFrame frames_[config::LOG_FRAME_CAPACITY];
    std::size_t first_ = 0U;
    std::size_t size_ = 0U;
    std::uint32_t overwritten_ = 0U;
    std::uint32_t rejected_status_ = 0U;
    std::uint32_t clamped_ = 0U;
    std::uint32_t invalid_ = 0U;
};

}  // namespace recorder
