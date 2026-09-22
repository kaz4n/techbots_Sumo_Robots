// Defines B8 search, B9 front requests and B10 turns for the future Robot arbiter.
// Keeps state deadlines and target exits separate from motor permission and I/O.
// Independent host tests cover capture, target priority, both deadlines and wrap.
#pragma once
#include "core/motion.h"
#include "core/governor.h"
#include "core/types.h"
#include <cstdint>

namespace fsm {
struct FrontQualificationResult {
    bool front_detected = false;
    bool centered = false;
    bool attack_eligible = false;
};
class FrontQualification {
public:
    // B9.1: each call is one NEW confirmed effective opponent observation in
    // normal perception. Use Fusion's phantom.filtered_mask; ignore high bits.
    // Count centered front observations consecutively; absent/off-center front
    // resets the count. Saturate at ATTACK_ENTER_TICKS; the threshold observation
    // is eligible. Side/rear bits cannot displace a current front (B2/B5).
    // Caller must not pass repeated/stale observations and must reset on leaving
    // normal perception/preemption. This counter does not decide which tick
    // enters TRACK, select a Robot state, or bypass D-034/D-038 reacquisition.
    // Eligibility alone never grants contact or motor permission. Caller selects
    // state, commits Fusion contact once, then applies frontDemand/governor/gates.
    FrontQualificationResult observe(std::uint8_t effective_mask);
    void reset();
private:
    std::uint32_t centered_ticks_ = 0;
};

struct FrontDemand {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    governor::Profile profile = governor::Profile::SEARCH_FORWARD;
    bool valid = false;
};
// B9/D-036 request math only: current B5 front table determines bearing.
// TRACK base TRACK_DUTY, gain K_TRACK_PER_DEG plus signed TURN_MIN_DUTY
// for the +/-15-degree rows; SEARCH_FORWARD profile. ATTACK requires a current
// centered row, uses approach/contact base and gain limited to min(base,
// TURN_MIN_DUTY), ATTACK profile. Clamp each wheel to [-1,1]. High bits ignored.
// Missing front, off-center ATTACK or any other state -> invalid/zero. TRACK
// may consume centered rows while qualification is pending. Contact is the
// current D-027 latch, never a stale cue. Does not count centered observations,
// select state, brake the governor, or authorize motors; Robot owns those tasks.
FrontDemand frontDemand(core::State state, std::uint8_t effective_mask, bool contact);

enum class Intent : std::uint8_t { NONE, PERCEPTION, SEARCH, INVALID };

class SearchSide {
public:
    // D-041: current selected relative bearing in (-180,180], finite and valid.
    // Positive -> RIGHT, negative -> LEFT. Zero or invalid/unavailable observations
    // retain the previous side. Reset/default is RIGHT. Caller supplies the current
    // B5 selected bearing, not an unselected sensor or expired memory as a new cue.
    void observe(float relative_bearing_deg, bool valid);
    motion::Direction direction() const;
    void reset();
private:
    motion::Direction direction_ = motion::Direction::RIGHT;
};

struct SearchContext {
    motion::Direction last_side = motion::Direction::RIGHT; // From SearchSide.
    bool world_valid = false;
    float world_bearing_deg = 0.0F; // (-180,180], captured B5 world memory.
    std::uint64_t world_age_us = 0; // Truthful age, never a raw wrapped timestamp.
    bool scan_hint_valid = false; // SIDESTEP hint, consumed by first actual scan.
    motion::Direction scan_hint = motion::Direction::RIGHT;
    bool inward_valid = false; // Only a real completed escape supplies this.
    float inward_heading_deg = 0.0F;
    std::uint64_t inward_age_us = 0;
};
enum class SearchPhase : std::uint8_t { IDLE, MEMORY_TURN, SCAN, ADVANCE, FINISHED, INVALID };
struct SearchResult {
    motion::Result motion;
    governor::Profile profile = governor::Profile::PIVOT;
    Intent intent = Intent::NONE;
    SearchPhase phase = SearchPhase::IDLE;
    motion::Direction scan_direction = motion::Direction::RIGHT;
    bool phase_changed = false; // Changes made by step; start establishes first phase.
    bool turn_timed_out = false; // One-call pulse for the memory B7 turn only.
};
class Search {
public:
    // B8: finite initial/last-known heading; validate last_side always and the
    // scan_hint enum only when scan_hint_valid. Ignore an unused hint enum.
    // Recent valid world memory (age<SEARCH_MEMORY_MS) captures one B7 turn at
    // TURN_DUTY. Otherwise start SCAN. Memory age is tested only at entry; never
    // retarget/restart that turn if its memory expires during the command.
    // First-scan direction: explicit hint, else nonzero captured shortest memory
    // turn sign, else last_side. Existing B7 +180 tie is RIGHT; zero uses last_side.
    // Only recent valid headings are consumed/validated; unused expired/invalid
    // context values are ignored. A consumed nonfinite heading or world bearing
    // outside (-180,180] is INVALID/zero; never turn toward an invalid target.
    bool start(std::uint32_t t_us, float heading_deg, bool imu_ok,
               const SearchContext& context);
    // Any low-seven-bit current effective target exits PERCEPTION/zero before
    // motion/heading checks. High bit ignored. Caller owns edge/STOP preemption.
    // MEMORY_TURN done/timeout -> SCAN -> ADVANCE -> opposite SCAN, indefinitely.
    // SCAN requests (+SCAN_DUTY,-SCAN_DUTY) for RIGHT, mirrored for LEFT; complete
    // when directed continuous yaw from scan entry >=SEARCH_SCAN_DEG. No shortest
    // angle wrapping or inherited TURN_TIMEOUT_MS applies to a full scan.
    // D-042: on first IMU loss, latch the last known remaining sweep clamped to
    // [0,SEARCH_SCAN_DEG]*TURN_MS_PER_DEG from that observation. Initially missing
    // IMU times the entire sweep. Recovery never restarts/changes that fallback.
    // Healthy nonfinite yaw invalidates an active command; unavailable yaw is
    // ignored. Keep the last finite healthy yaw for subsequent primitive entry.
    // ADVANCE: SEARCH_ADVANCE_MS at SEARCH_DUTY_MAX with B7 heading hold. Use the
    // captured inward heading only while its internally aged age<RECENT_EDGE_MS;
    // otherwise use current/last-known yaw. Expired inward evidence never revives.
    // MEMORY_TURN/SCAN profile PIVOT; ADVANCE SEARCH_FORWARD. Terminals are zero
    // (DONE for PERCEPTION, INVALID for invalid, IDLE before start), fallback=false.
    // Each new segment begins at the observed transition tick, never backdated;
    // at most three phases per step. Timeout pulse survives same-tick transitions.
    // No state assignment, motor permission, clock, I/O or allocation. Consecutive
    // calls must be <one uint32 micros wrap. Terminal until reset/start.
    SearchResult step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                      std::uint8_t effective_mask);
    void reset();
private:
    bool beginScan(std::uint32_t t_us, bool imu_ok);
    bool beginAdvance(std::uint32_t t_us);
    motion::Result runScan(std::uint32_t t_us, float heading_deg, bool imu_ok);
    motion::Result runMotion(std::uint32_t t_us, float heading_deg, bool imu_ok);
    bool advancePhase(std::uint32_t t_us, bool imu_ok);
    SearchResult result(const motion::Result& motion) const;
    motion::Turn turn_;
    motion::Straight straight_;
    motion::Interval scan_clock_;
    SearchPhase phase_ = SearchPhase::IDLE;
    Intent intent_ = Intent::NONE;
    motion::Direction scan_direction_ = motion::Direction::RIGHT;
    std::uint32_t last_us_ = 0;
    std::uint32_t inward_remaining_us_ = 0;
    float inward_heading_deg_ = 0.0F;
    float last_heading_deg_ = 0.0F;
    float scan_start_deg_ = 0.0F;
    double remaining_deg_ = 0.0;
    double fallback_us_ = 0.0;
    bool scan_fallback_ = false;
};

struct DefendResult {
    motion::Result motion;
    Intent intent = Intent::NONE;
    bool turn_timed_out = false; // One-call pulse from the B7 primitive.
    bool defend_timed_out = false; // One-call pulse at B10's state deadline.
};
class DefendTurn {
public:
    // Capture finite last-known heading plus a valid finite B5 relative bearing
    // in (-180,180] once; no target retarget/restart during this command. Turn at
    // TURN_DUTY using B7, and start the separate DEFEND_TIMEOUT_MS interval.
    // Invalid capture latches INVALID/zero. DEFEND_EVADE_FIRST remains disabled.
    bool start(std::uint32_t t_us, float heading_deg, float bearing_deg,
               bool bearing_valid, bool imu_ok);
    // Current confirmed front -> PERCEPTION, no current target -> SEARCH (B2).
    // Otherwise retain the captured turn for side/rear readings; high bit ignored.
    // Target exits take precedence at deadlines. Normal turn completion/700ms
    // timeout gives zero demand while waiting for a front/clear observation or
    // the separate800ms state deadline. Never restart the turn to fill that gap.
    // At DEFEND_TIMEOUT_MS -> SEARCH with zero; timeout pulses occur once, and
    // terminal intent stays latched until reset/start. Preserve B7 IMU fallback.
    // Caller must apply governor PIVOT and edge/STOP/gates; no motor authorization.
    // Successive calls <one uint32 micros wrap; all elapsed time is caller supplied.
    DefendResult step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                      std::uint8_t confirmed_mask);
    void reset();
private:
    DefendResult finish(Intent intent);
    motion::Turn turn_;
    motion::Interval interval_;
    Intent intent_ = Intent::NONE;
    bool active_ = false;
    bool turn_timeout_reported_ = false;
};
} // namespace fsm
