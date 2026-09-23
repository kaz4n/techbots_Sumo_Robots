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
    const StoredFrame incoming{bytes, status};
    const std::size_t destination = (first_ + size_) % config::LOG_FRAME_CAPACITY;
    frames_[destination] = incoming;
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

const StoredFrame* FrameBuffer::at(std::size_t chronological_index) const {
    if (chronological_index >= size_) return nullptr;
    return &frames_[(first_ + chronological_index) % config::LOG_FRAME_CAPACITY];
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
