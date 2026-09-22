// Defines the B5.1 polarity correction and hysteresis stage.
// Makes raw digital input filtering testable before higher fusion policies exist.
// Host tests cover each bit, consecutive samples, clear intervals and wraparound.
#pragma once
#include <cstdint>
#include "types.h"

namespace opp_fusion {
struct FrontView {
    bool detected = false;
    bool centered = false;
    bool close = false;
    float bearing_deg = 0.0F; // Meaningful only when detected is true.
};
// The seven unambiguous front rows in B5.2; input is already polarity-corrected
// and debounced. Side/rear bits do not change this front-only view. This neither
// selects side/rear bearings nor changes target memory/contact/phantom policy.
FrontView frontView(std::uint8_t confirmed_mask);

class Debouncer {
public:
    // One newly sampled raw electrical seven-bit mask per call/tick.
    // Assertion counts detected samples; deassertion measures elapsed clear time.
    // The first clear sample starts that interval; high unused bits are ignored.
    std::uint8_t step(std::uint32_t t_us, std::uint8_t raw_mask);
    void reset();
private:
    std::uint32_t detected_ticks_[7] = {};
    std::uint32_t clear_since_us_[7] = {};
    std::uint8_t clearing_mask_ = 0;
    std::uint8_t confirmed_mask_ = 0;
};

enum class Group : std::uint8_t { NONE, FRONT, SIDE, REAR };
enum class FrontSide : std::uint8_t { UNKNOWN, LEFT, RIGHT };
struct BearingView {
    Group group = Group::NONE;
    bool detected = false; // A selected group is present, even if conflicted.
    bool bearing_valid = false; // Never invent a direction when no history exists.
    bool world_valid = false;
    bool centered = false;
    bool close = false;
    bool conflict = false;
    float relative_deg = 0.0F;
    float world_deg = 0.0F;
};
struct Memory {
    bool valid = false;
    bool world_valid = false;
    float last_rel_bearing_deg = 0.0F;
    float last_world_bearing_deg = 0.0F;
    std::uint32_t last_seen_us = 0;
    FrontSide last_front_side = FrontSide::UNKNOWN;
    bool left_seen = false;
    bool right_seen = false;
    std::uint32_t left_seen_us = 0;
    std::uint32_t right_seen_us = 0;
};
class BearingMemory {
public:
    // Input already corrected/debounced, high bit ignored. B5 priority is front,
    // side, rear. Both side/rear bits reuse the previous valid relative bearing
    // with conflict=true (D-026); otherwise bearing_valid=false. Front suppresses
    // lower-group conflicts. No detection gives an empty view, retains memory.
    // Finite heading + valid relative bearing gives world angle in (-180,180].
    // Nonfinite heading keeps relative validity but sets world_valid=false/zero.
    // Valid selected bearing updates memory and last_seen at this exact tick.
    BearingView step(std::uint32_t t_us, std::uint8_t confirmed_mask, float heading_deg);
    const Memory& memory() const;
    void reset();
private:
    // Front recency means newly lit bits, not every tick of a held bit. A
    // simultaneous rising pair records both times but keeps last_front_side.
    void rememberFrontSide(std::uint32_t t_us, std::uint8_t mask);
    Memory memory_;
    std::uint8_t previous_mask_ = 0;
};

struct ContactResult {
    bool close_cue = false;
    bool impact_cue = false;
    bool cue = false;
    bool contact = false;
    bool contact_started = false; // Rising latch only, for CONTACT event/timer.
};
class Contact {
public:
    // One new confirmed logical observation/tick. Independent consecutive
    // counters for front mask111 and101; changing patterns resets the previous
    // pattern's count. Counters saturate at CONTACT_TICKS; cues are current levels.
    // Impact uses finite ax/ay, imu_ok and strict horizontal norm>IMPACT_G.
    // Invalid/unavailable IMU never supplies impact but does not suppress valid
    // visual cues. Cues remain observable in all states (e.g. re-flank BACK).
    // D-027 latch exists only in ATTACK with a currently centered front target.
    // Ineligible calls clear it. A qualified current cue can establish a fresh
    // latch on re-entry; the old latch alone cannot. Reset clears all counters.
    ContactResult step(core::State state, std::uint8_t confirmed_mask,
                       float ax_g, float ay_g, bool imu_ok);
    void reset();
private:
    std::uint32_t all_front_ticks_ = 0;
    std::uint32_t straddle_ticks_ = 0;
    bool contact_ = false;
};
} // namespace opp_fusion
