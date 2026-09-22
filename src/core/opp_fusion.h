// Defines B5 filters, bearing memory, contact cues and their ordered fusion path.
// Separates fresh sensor observations from post-arbitration contact permission.
// Independent host tests cover tables, histories, composition, faults and wrap.
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

struct ContactCue {
    bool close_cue = false;
    bool impact_cue = false;
    bool cue = false;
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
    // Split composition API: advance cue counters exactly once per fresh sample,
    // then apply the final arbitrated state without taking another observation.
    // commitLatch consumes the supplied current cue, updates only the latch and
    // emits its rising flag. Repeating commitment never advances cue counters.
    ContactCue observeCue(std::uint8_t confirmed_mask, float ax_g, float ay_g,
                          bool imu_ok);
    // Read-only D-056 candidate: identical result to the next commitLatch with
    // these arguments, but changes neither latch nor cue counters. Repeated or
    // alternative-state previews must not create/clear contact or emit an event.
    ContactResult previewLatch(core::State state, std::uint8_t effective_mask,
                               const ContactCue& cue) const;
    ContactResult commitLatch(core::State state, std::uint8_t effective_mask,
                              const ContactCue& cue);
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

struct PhantomSample {
    std::uint32_t t_us = 0;
    core::State state = core::State::IDLE; // State before this tick's edge arbitration.
    std::uint8_t confirmed_mask = 0; // Before phantom suppression, after stuck removal.
    float heading_deg = 0.0F;
    bool imu_ok = false;
    bool edge_event = false;
    bool contact_cue = false; // Current B5.4 cue, not only its ATTACK latch.
};
struct PhantomResult {
    std::uint8_t filtered_mask = 0;
    bool active = false;
    bool phantom_set = false; // One call per qualified edge/episode.
    float world_deg = 0.0F; // Valid only while active; normalized (-180,180].
};
class PhantomFilter {
public:
    // D-029: front-only means some low three bits and no side/rear bits. Start
    // an episode only in TRACK/ATTACK; maintain across those two states, clear
    // it on any non-chase observation. Remember any contact cue. An edge at
    // age <= PHANTOM_WINDOW_MS marks current heading+front bearing if IMU-valid
    // and finite with no contact; that edge consumes the episode until it ends.
    // D-030: one marker, replaced on a new mark, expires at age >= PHANTOM_MS.
    // Mask only front-only observations within inclusive PHANTOM_MASK_DEG;
    // B5.2 close patterns101/111 and any side/rear observation override masking.
    // Invalid heading never marks/masks; expiry still advances. High bit ignored.
    // Successive call gaps must be less than one uint32 micros wrap.
    PhantomResult step(const PhantomSample& sample);
    void reset();
private:
    void advance(std::uint32_t t_us);
    std::uint32_t last_us_ = 0;
    std::uint64_t episode_age_us_ = 0;
    std::uint64_t marker_age_us_ = 0;
    float marker_deg_ = 0.0F;
    bool clock_started_ = false;
    bool episode_ = false;
    bool contacted_ = false;
    bool consumed_ = false;
    bool active_ = false;
};

struct StuckResult {
    std::uint8_t filtered_mask = 0;
    std::uint8_t fault_mask = 0; // Latched until reset even if current input clears.
    std::uint8_t new_fault_mask = 0; // Newly declared bits on this call only.
};
class StuckFilter {
public:
    // Inspect unsuppressed confirmed bits (before phantom masking). Each bit
    // independently requires continuous detection >= OPP_STUCK_MS and observed
    // continuous-heading span strictly >360 degrees. No modulo/cumulative travel.
    // Clear or unavailable/nonfinite IMU resets an undeclared candidate. D-031
    // declared faults persist until reset. High bit ignored; bounded seven-bit
    // work. Successive call gaps must be less than one uint32 micros wrap.
    StuckResult step(std::uint32_t t_us, std::uint8_t confirmed_mask,
                     float heading_deg, bool imu_ok);
    void reset();
private:
    struct Candidate {
        std::uint32_t age_us = 0;
        float min_deg = 0.0F;
        float max_deg = 0.0F;
        bool active = false;
    };
    Candidate candidates_[7];
    std::uint32_t last_us_ = 0;
    std::uint8_t faults_ = 0;
    bool clock_started_ = false;
};

struct FusionSample {
    std::uint32_t t_us = 0;
    std::uint8_t raw_mask = 0; // Electrical polarity, not confirmed logical bits.
    core::State prior_state = core::State::IDLE; // Before this tick's arbitration.
    float heading_deg = 0.0F; // Continuous yaw for stuck-span evidence.
    float ax_g = 0.0F;
    float ay_g = 0.0F;
    bool imu_ok = false;
    bool edge_event = false;
};
struct FusionObservation {
    std::uint8_t confirmed_mask = 0;
    StuckResult stuck;
    ContactCue cue;
    PhantomResult phantom; // filtered_mask is the final effective opponent mask.
    BearingView bearing;
    bool fresh = false;
};
struct ContactCommit {
    ContactResult result;
    bool valid = false; // Caller must not use an invalid result as permission.
};
class Fusion {
public:
    // One fresh electrical observation per tick: debounce -> stuck removal ->
    // contact cue -> phantom filtering with prior_state -> effective bearing.
    // Valid finite IMU yaw alone supplies world-bearing evidence; without it
    // relative bearing remains usable, but world_valid is false.
    // An immediate repeat timestamp returns the cached observation with fresh
    // false and event pulses cleared; it cannot resample or reopen commitment.
    // Changed data at the same timestamp is ignored. Gaps must be <one micros
    // wrap. A new observation replaces an uncommitted one and clears its latch,
    // so violating the once-observe/once-commit protocol cannot reuse contact.
    FusionObservation observe(const FusionSample& sample);
    // D-056: inspect this pending observation's candidate contact without
    // consuming it. Missing/already-consumed observation returns invalid zero
    // and does NOT mutate the latch. Repeated previews/alternative states are
    // allowed; they never resample or authorize motion/events. Robot may use an
    // ATTACK candidate for stall routing, then commit exactly once to the final
    // state (REFLANK clears contact). A new observe retains its existing skipped-
    // commit protection. An immediate cached observe does not consume pending.
    ContactCommit preview(core::State candidate_state) const;
    // Call once after selecting the final current state. Uses this observation's
    // cue and effective mask; no debounce/contact counter is sampled twice.
    // A missing/already-consumed observation yields invalid zero and clears the
    // latch. Same-tick centered ATTACK entry can latch; every ineligible exit
    // clears immediately. This still does not select state or authorize motors.
    ContactCommit commit(core::State selected_state);
    const Memory& memory() const;
    void reset();
private:
    Debouncer debounce_;
    StuckFilter stuck_;
    Contact contact_;
    PhantomFilter phantom_;
    BearingMemory bearing_;
    FusionObservation observation_;
    std::uint32_t observed_us_ = 0;
    bool observed_ = false;
    bool pending_ = false;
};
} // namespace opp_fusion
