// Defines B14 supplied-tick statistics and B15 frame/exact-tick event encodings.
// Keeps encoding and D-028 bounded event retention independent of HAL transport.
// Independent host tests use literal byte fixtures, boundaries and invalid inputs.
#pragma once
#include "types.h"
#include "../config.h"
#include <cstddef>
#include <cstdint>
#include <limits>

namespace logframe {
struct TickStatistics {
    std::uint64_t ticks = 0;
    std::uint64_t overruns = 0;
    std::uint32_t max_us = 0;
    bool saturated = false;
};
// B14: caller supplies one measured execution duration per included match tick.
// No scheduler, clock, match membership or motor response is implemented here.
// Start/reset with TickStatistics{}; valid state has overruns<=ticks. Each call
// updates max_us and counts a strict measured_execution_us>TICK_US overrun.
// At UINT64_MAX retained ticks, reject further count updates, latch saturated and
// continue updating the full maximum. Counts then describe the retained prefix;
// saturated means incomplete statistics, never a measured pass or zero overruns.
// Plain value state permits exact arithmetic tests at representational limits.
void observeTick(TickStatistics& statistics, std::uint32_t measured_execution_us);
// Current retained-count ratio strictly above TICK_OVERRUN_PERCENT; empty=false.
// Uses exact integer arithmetic without overflowing even at UINT64_MAX. This is
// a statistical level, not a latched fault. Caller must preserve saturated status.
bool overrunRateExceeded(const TickStatistics& statistics);

// Representation constants, not behavior tunables. Explicit byte encoding has
// no struct padding or native-endian dependency. Layout version is documented.
inline constexpr std::size_t FRAME_BYTES = 25U;
inline constexpr std::size_t EVENT_BYTES = 8U;
enum class PackStatus : std::uint8_t { OK, CLAMPED, INVALID };
enum Flag : std::uint8_t {
    IMU_OK = 1U, PHANTOM_ACTIVE = 2U, STUCK = 4U, CAL_REJECTED = 8U
};
struct FrameInput {
    std::uint32_t t_ms = 0;
    core::State state = core::State::BOOT;
    core::Mode mode = core::Mode::SIDESTEP_R;
    std::uint8_t line_mask = 0;
    std::uint8_t opp_mask = 0;
    float heading_deg = 0.0F; // Accumulated yaw is preserved, not angle-wrapped.
    float gyro_z_dps = 0.0F;
    float ax_g = 0.0F;
    float ay_g = 0.0F;
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    float vbat_v = 0.0F;
    std::uint8_t flags = 0;
    std::uint32_t tick_max_us = 0;
};
struct FrameBytes { std::uint8_t data[FRAME_BYTES] = {}; };
struct EventInput {
    std::uint32_t t_us = 0; // Exact supplied tick, including natural wrap.
    core::Event type = core::Event::START_RELEASE;
    std::uint8_t detail = 0; // Caller-defined event metadata, no truncation.
    std::uint16_t value = 0;
};
struct EventBytes { std::uint8_t data[EVENT_BYTES] = {}; };

// D-060 metadata version1; explicit wire codes, not behavior tunables.
inline constexpr std::size_t ROBOT_EVENT_CAPACITY = 21U;
enum class FaultCode : std::uint8_t {
    IMU_UNAVAILABLE = 1, OPPONENT_STUCK, QTR_STUCK_WARNING, LOW_BATTERY,
    CALIBRATION, ESCAPE_FAULT, CORE_CONTRACT_FAULT, TURN_TIMEOUT,
    TICK_STATISTICS, RESET_CAUSE
};
enum EdgeDetail : std::uint8_t {
    NEW_WHITE = 1U, ENTERED = 2U, REPLANNED = 4U, EXITED = 8U, PUSHED_OUT = 16U
};
enum class ReflankCode : std::uint8_t { BACK = 1, SWING = 2, TURN_IN = 3 };
enum class DirectionCode : std::uint16_t { RIGHT = 1, LEFT = 2 };
struct EventBatch {
    EventInput entries[ROBOT_EVENT_CAPACITY] = {};
    std::uint8_t count = 0;
    bool overflowed = false;
    std::uint32_t rejected = 0; // Capacity rejection only, saturating.
    std::uint32_t invalid_metadata = 0; // Separate semantic failure, saturating.
};
// D-060 metadata table in state/analysis/P1_robot_event_contract_audit.md, adopted
// by D-060 with CORE_CONTRACT bits0..7 and TICK_STATISTICS bits0..2. Validate
// types/codes/masks, canonical encoded angles, duty bytes and zero reserved bits.
// Encoding alone still accepts caller-defined metadata (legacy packEvent unchanged).
bool validEventMetadata(const EventInput& input);
// Fixed prefix retention. Invalid metadata increments only invalid_metadata;
// otherwise full count latches overflow/rejected. Never recursively emit a fault,
// overwrite prior entries or affect motion. Clear with EventBatch{} each result.
bool appendEvent(EventBatch& batch, const EventInput& input);

// Little-endian layout: t_ms u32 @0; state/mode/line/opp u8 @4..7;
// heading i32 centidegrees @8; gyro i16 tenths dps @12; ax/ay i16 mg @14/16;
// duties i8 scale127 @18/19; vbat u16 centivolts @20; flags u8 @22;
// tick_max u16 microseconds @23. Signed fields use two's-complement encoding.
// Round nearest, exact halves away from zero; finite out-of-range fields clamp
// and report CLAMPED. Duty clamps to [-127,127], never the extra -128 code.
// Unknown enums, high mask/flag bits or any nonfinite field report INVALID and
// zero the entire destination. Caller must retain status; no silent valid data.
PackStatus packFrame(const FrameInput& input, FrameBytes& destination);
// t_us u32 @0; event u8 @4; detail u8 @5; value u16 @6. Invalid event enum
// returns INVALID and zeros destination. There is no ring, dropping or I/O here.
PackStatus packEvent(const EventInput& input, EventBytes& destination);

// Production overflow-counter operation, exposed as pure arithmetic so its
// saturation boundary is directly testable without billions of rejected events.
constexpr std::uint32_t saturatingIncrement(std::uint32_t value) {
    return value == std::numeric_limits<std::uint32_t>::max() ? value : value + 1U;
}
class EventBuffer {
public:
    // D-028: retain the first LOG_EVENT_CAPACITY successfully encoded events in
    // insertion order. On full, reject, latch overflow and increment a saturating
    // rejected count. Never overwrite retained bytes or reorder equal/wrap ticks.
    // Caller must check packEvent status before append; this stores bytes only.
    bool append(const EventBytes& event);
    std::size_t size() const;
    // Null outside retained entries. Returned pointers are valid only until reset
    // or buffer destruction; ownership is with the future HAL recorder instance.
    const EventBytes* at(std::size_t index) const;
    bool overflowed() const;
    std::uint32_t rejectedCount() const;
    // Clear logical contents/status in constant work; old entries become unreadable
    // through at(). Lifecycle decisions are the recorder's responsibility.
    void reset();
private:
    EventBytes events_[config::LOG_EVENT_CAPACITY];
    std::size_t size_ = 0;
    std::uint32_t rejected_ = 0;
    bool overflowed_ = false;
};
} // namespace logframe
