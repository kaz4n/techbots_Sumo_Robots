// Retains the latest B15 codec frames with their exact bytes and pack status.
// Makes overwritten or degraded evidence explicit without owning match lifecycle.
// Independent D-069 host tests cover boundaries, wraps, aliases and logical reset.
#include "recorder_frames.h"

namespace recorder {

bool FrameBuffer::append(const logframe::FrameBytes& bytes,
                         logframe::PackStatus status) {
    if (status != logframe::PackStatus::OK &&
        status != logframe::PackStatus::CLAMPED &&
        status != logframe::PackStatus::INVALID) {
        rejected_status_ = logframe::saturatingIncrement(rejected_status_);
        return false;
    }

    // A caller may borrow the frame that this append is about to overwrite.
    const logframe::FrameBytes incoming = bytes;
    const std::size_t destination = (first_ + size_) % config::LOG_FRAME_CAPACITY;
    payloads_[destination] = incoming;
    const auto shift = static_cast<unsigned>(2U * (destination % 4U));
    auto& lanes = statuses_[destination / 4U];
    lanes = static_cast<std::uint8_t>((lanes & ~(3U << shift)) |
        (static_cast<std::uint8_t>(status) << shift));
    if (size_ == config::LOG_FRAME_CAPACITY) {
        first_ = (first_ + 1U) % config::LOG_FRAME_CAPACITY;
        overwritten_ = logframe::saturatingIncrement(overwritten_);
    } else {
        ++size_;
    }
    if (status == logframe::PackStatus::CLAMPED) {
        clamped_ = logframe::saturatingIncrement(clamped_);
    } else if (status == logframe::PackStatus::INVALID) {
        invalid_ = logframe::saturatingIncrement(invalid_);
    }
    return true;
}

std::size_t FrameBuffer::size() const {
    return size_;
}

bool FrameBuffer::read(std::size_t chronological_index, StoredFrame& output) const {
    if (chronological_index >= size_) return false;
    const std::size_t source = (first_ + chronological_index) % config::LOG_FRAME_CAPACITY;
    output.bytes = payloads_[source];
    const auto shift = static_cast<unsigned>(2U * (source % 4U));
    output.status = static_cast<logframe::PackStatus>((statuses_[source / 4U] >> shift) & 3U);
    return true;
}

const logframe::FrameBytes* FrameBuffer::bytesAt(std::size_t chronological_index) const {
    if (chronological_index >= size_) return nullptr;
    return &payloads_[(first_ + chronological_index) % config::LOG_FRAME_CAPACITY];
}

std::uint32_t FrameBuffer::overwrittenCount() const {
    return overwritten_;
}

std::uint32_t FrameBuffer::rejectedStatusCount() const {
    return rejected_status_;
}

std::uint32_t FrameBuffer::clampedCount() const {
    return clamped_;
}

std::uint32_t FrameBuffer::invalidCount() const {
    return invalid_;
}

bool FrameBuffer::incomplete() const {
    return overwritten_ != 0U || rejected_status_ != 0U ||
        clamped_ != 0U || invalid_ != 0U;
}

void FrameBuffer::reset() {
    first_ = 0U;
    size_ = 0U;
    overwritten_ = 0U;
    rejected_status_ = 0U;
    clamped_ = 0U;
    invalid_ = 0U;
}

}  // namespace recorder
