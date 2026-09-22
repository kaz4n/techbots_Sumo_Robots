// Counts B14 supplied ticks, encodes B15 frames/events and retains bounded events.
// Preserves portable evidence and exposes D-028 overflow without overwriting it.
// Independent host tests cover encoding, capacity boundaries and reset behavior.
#include "logframe.h"
#include <cmath>
#include <limits>

namespace logframe {
static_assert(config::LOG_EVENT_CAPACITY > 0U, "Event capacity must be positive");
static_assert(config::TICK_OVERRUN_PERCENT <= 100U, "Percentage cannot exceed 100");

void observeTick(TickStatistics& statistics, std::uint32_t measured_execution_us) {
    if (measured_execution_us > statistics.max_us) {
        statistics.max_us = measured_execution_us;
    }
    if (statistics.ticks == std::numeric_limits<std::uint64_t>::max()) {
        statistics.saturated = true;
        return;
    }
    ++statistics.ticks;
    if (measured_execution_us > config::TICK_US) {
        ++statistics.overruns;
    }
}

bool overrunRateExceeded(const TickStatistics& statistics) {
    if (statistics.ticks == 0U) return false;
    // Split the percentage product so even UINT64_MAX ticks cannot overflow.
    const std::uint64_t allowed = (statistics.ticks / 100U) * config::TICK_OVERRUN_PERCENT +
        ((statistics.ticks % 100U) * config::TICK_OVERRUN_PERCENT) / 100U;
    return statistics.overruns > allowed;
}

namespace {
void writeU16(std::uint8_t* destination, std::uint16_t value) {
    destination[0] = static_cast<std::uint8_t>(value & 0xFFU);
    destination[1] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
}

void writeU32(std::uint8_t* destination, std::uint32_t value) {
    destination[0] = static_cast<std::uint8_t>(value & 0xFFU);
    destination[1] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
    destination[2] = static_cast<std::uint8_t>((value >> 16U) & 0xFFU);
    destination[3] = static_cast<std::uint8_t>((value >> 24U) & 0xFFU);
}

bool validFrame(const FrameInput& input) {
    const auto state = static_cast<std::uint8_t>(input.state);
    const auto mode = static_cast<std::uint8_t>(input.mode);
    return state <= static_cast<std::uint8_t>(core::State::DRIVE_TEST) &&
        mode >= static_cast<std::uint8_t>(core::Mode::SIDESTEP_R) &&
        mode <= static_cast<std::uint8_t>(core::Mode::WAIT) &&
        (input.line_mask & 0xF0U) == 0U &&
        (input.opp_mask & 0x80U) == 0U && (input.flags & 0xF0U) == 0U &&
        std::isfinite(input.heading_deg) && std::isfinite(input.gyro_z_dps) &&
        std::isfinite(input.ax_g) && std::isfinite(input.ay_g) &&
        std::isfinite(input.duty_l) && std::isfinite(input.duty_r) &&
        std::isfinite(input.vbat_v);
}

std::int32_t quantize(float value, double scale, std::int32_t minimum,
                      std::int32_t maximum, bool& clamped) {
    // Double scaling cannot overflow for any finite float and these scales.
    // Clamp before integer conversion, including the asymmetric int32 limits.
    const double scaled = static_cast<double>(value) * scale;
    if (scaled < static_cast<double>(minimum)) {
        clamped = true;
        return minimum;
    }
    if (scaled > static_cast<double>(maximum)) {
        clamped = true;
        return maximum;
    }
    return static_cast<std::int32_t>(std::round(scaled));
}

void writeSigned16(std::uint8_t* destination, float value, double scale,
                   bool& clamped) {
    const auto encoded = quantize(value, scale,
        std::numeric_limits<std::int16_t>::min(),
        std::numeric_limits<std::int16_t>::max(), clamped);
    // Unsigned conversion defines the two's-complement byte representation.
    writeU16(destination, static_cast<std::uint16_t>(encoded));
}
} // namespace

PackStatus packFrame(const FrameInput& input, FrameBytes& destination) {
    destination = {};
    if (!validFrame(input)) {
        return PackStatus::INVALID;
    }
    bool clamped = false;
    writeU32(destination.data, input.t_ms);
    destination.data[4] = static_cast<std::uint8_t>(input.state);
    destination.data[5] = static_cast<std::uint8_t>(input.mode);
    destination.data[6] = input.line_mask;
    destination.data[7] = input.opp_mask;
    const auto heading = quantize(input.heading_deg, 100.0,
        std::numeric_limits<std::int32_t>::min(),
        std::numeric_limits<std::int32_t>::max(), clamped);
    writeU32(destination.data + 8, static_cast<std::uint32_t>(heading));
    writeSigned16(destination.data + 12, input.gyro_z_dps, 10.0, clamped);
    writeSigned16(destination.data + 14, input.ax_g, 1000.0, clamped);
    writeSigned16(destination.data + 16, input.ay_g, 1000.0, clamped);
    destination.data[18] = static_cast<std::uint8_t>(
        quantize(input.duty_l, 127.0, -127, 127, clamped));
    destination.data[19] = static_cast<std::uint8_t>(
        quantize(input.duty_r, 127.0, -127, 127, clamped));
    const auto battery = quantize(input.vbat_v, 100.0, 0,
        std::numeric_limits<std::uint16_t>::max(), clamped);
    writeU16(destination.data + 20, static_cast<std::uint16_t>(battery));
    destination.data[22] = input.flags;
    const auto tick_limit = std::numeric_limits<std::uint16_t>::max();
    const bool tick_clamped = input.tick_max_us > tick_limit;
    writeU16(destination.data + 23, tick_clamped ? tick_limit :
        static_cast<std::uint16_t>(input.tick_max_us));
    return clamped || tick_clamped ? PackStatus::CLAMPED : PackStatus::OK;
}

PackStatus packEvent(const EventInput& input, EventBytes& destination) {
    destination = {};
    const auto type = static_cast<std::uint8_t>(input.type);
    if (type > static_cast<std::uint8_t>(core::Event::FAULT)) {
        return PackStatus::INVALID;
    }
    writeU32(destination.data, input.t_us);
    destination.data[4] = type;
    destination.data[5] = input.detail;
    writeU16(destination.data + 6, input.value);
    return PackStatus::OK;
}

bool EventBuffer::append(const EventBytes& event) {
    if (size_ >= config::LOG_EVENT_CAPACITY) {
        overflowed_ = true;
        rejected_ = saturatingIncrement(rejected_);
        return false;
    }
    events_[size_] = event;
    ++size_;
    return true;
}

std::size_t EventBuffer::size() const {
    return size_;
}

const EventBytes* EventBuffer::at(std::size_t index) const {
    return index < size_ ? &events_[index] : nullptr;
}

bool EventBuffer::overflowed() const {
    return overflowed_;
}

std::uint32_t EventBuffer::rejectedCount() const {
    return rejected_;
}

void EventBuffer::reset() {
    // Retained storage need not be zeroed: at() hides every previous entry.
    size_ = 0U;
    rejected_ = 0U;
    overflowed_ = false;
}
} // namespace logframe
