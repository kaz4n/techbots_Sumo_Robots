// Defines fixed B15 frame and exact-tick event encodings.
// Keeps recorder representation independent of unresolved buffer overflow policy.
// Independent host tests use literal byte fixtures, boundaries and invalid inputs.
#pragma once
#include "types.h"
#include <cstddef>
#include <cstdint>

namespace logframe {
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
} // namespace logframe
