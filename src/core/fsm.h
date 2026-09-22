// Defines B8 search, B9 front requests and B10/B11 scripts for the future Robot.
// Keeps state deadlines and target exits separate from motor permission and I/O.
// Independent host tests cover capture, target priority, both deadlines and wrap.
#pragma once
#include "motion.h"
#include "governor.h"
#include "types.h"
#include <cstdint>

namespace fsm {
enum class HeadingOrigin : std::uint8_t {
    NONE, CURRENT_GO, LAST_KNOWN, NOMINAL_PENDING, FIRST_RECOVERY
};
struct HeadingResult {
    float heading_deg = 0.0F; // Finite match coordinate, never a synthetic measurement.
    bool imu_ok = false; // Current healthy measured MATCH coordinate only.
    bool match_started = false;
    bool origin_changed = false; // One-call pulse, including nominal GO establishment.
    bool fault = false; // Reset-only invalid coordinate or repeated GO.
    HeadingOrigin origin = HeadingOrigin::NONE;
    std::uint32_t origin_t_us = 0; // Actual source sample; nominal pending uses GO time.
};
struct HeadingProjection {
    float heading_deg = 0.0F;
    bool valid = false;
};
class HeadingReference {
public:
    // B0/B3/B14/D-059. Caller supplies continuous unreset raw integrated yaw
    // for the entire Robot lifetime; Fusion always keeps that raw domain.
    // Before GO, retain healthy finite history but expose match heading0/imu=false.
    // Actual GO (after cancel/STOP arbitration) captures current healthy yaw,
    // else last healthy yaw, else nominal0 with pending origin. In all cases
    // local heading0; absence preserves B14 timed fallback, never healthy evidence.
    // First healthy recovery resolves only a pending origin to current raw yaw;
    // local0 and existing references/deadlines remain unchanged. Later healthy
    // coordinates are double(raw)-origin, checked before narrowing to float.
    // Unavailable payload is ignored; retain last local coordinate/imu=false.
    // Healthy nonfinite yaw (even pre-GO), unrepresentable match difference or
    // a second GO latches fault until reset. Preserve finite last coordinate,
    // publish imu=false, inhibit projections; future Robot must inhibit motors.
    // Immediate duplicate time ignores changed input/GO and clears only pulses;
    // successive distinct calls must be less than one uint32 time wrap apart.
    // A real reset clears history/origin/fault. Never reset Fusion on GO, reset
    // the provider yaw, or use this helper as motor permission or physical proof.
    HeadingResult step(std::uint32_t t_us, float raw_heading_deg, bool imu_ok,
                       bool go = false);
    // Read-only directional views in (-180,180], exact +/-180 -> +180. A negative
    // non-tie that narrows to excluded -180 uses the nearest interior negative
    // float, preserving LEFT rather than becoming the exact RIGHT tie. Invalid
    // projections are finite0/valid=false, do not mutate/latch faults or freshness.
    // worldBearing requires this tick's healthy match yaw and relative bearing
    // in (-180,180]; reduce checked double(raw-origin) BEFORE adding the small
    // relative bearing or narrowing. Published float yaw may already be rounded.
    HeadingProjection worldBearing(float relative_deg) const;
    // Retained raw world input must be in (-180,180], rejecting -180/nonfinite/
    // out-of-range values. Computed +/-180 ties become +180. Caller retains
    // its original validity/time/age. Requires a resolved origin, not current IMU.
    HeadingProjection projectWorld(float raw_world_deg) const;
    // Retained actual raw continuous evidence (e.g. inward exit), without wrapping.
    // Requires a resolved origin and a finite, float-representable difference.
    // Never promote cached/nominal fallback yaw to a new inward measurement.
    HeadingProjection projectHeading(float raw_heading_deg) const;
    void reset();
private:
    void captureOrigin(std::uint32_t t_us, float raw_heading_deg, bool imu_ok);
    bool resolved() const;
    HeadingResult result_;
    double origin_deg_ = 0.0;
    float last_raw_deg_ = 0.0F;
    std::uint32_t last_raw_us_ = 0;
    std::uint32_t last_us_ = 0;
    bool has_raw_ = false;
    bool sampled_ = false;
};

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

struct NormalResult {
    core::State state = core::State::SEARCH;
    bool brake = false; // D-046: overrides all new-state motion on this tick.
    bool front_detected = false;
    bool centered = false;
};
class NormalPerception {
public:
    // B2/B9/D-034/D-038/D-045/D-046 normal routing only. Each call consumes
    // exactly one NEW effective confirmed mask from Fusion; high bit ignored.
    // Front priority: TRACK until ATTACK_ENTER_TICKS consecutive centered
    // observations, then ATTACK. Off-center front selects TRACK and resets the
    // count. No front: DEFEND_TURN if current side/rear exists, otherwise SEARCH.
    // On entry from a script/preemption, reset BEFORE calling step once with
    // this tick's observation; it counts as the first eligible sample (D-045).
    // Any front loss after this helper selected TRACK/ATTACK sets brake=true
    // for that one observation and resets qualification. Caller must apply it
    // immediately through Governor; new-state motion begins no earlier than
    // the next tick. Side/rear disappearance alone is not a front-loss brake.
    // Caller handles gate/edge/script arbitration first, resets on preemption,
    // commits Fusion contact once against the returned state, then obtains
    // frontDemand or the selected script's demand. TRACK uses SEARCH_FORWARD,
    // ATTACK uses its current contact/centering cap; no stale ATTACK latch.
    // No state persistence outside normal routing, duties, clock, allocation,
    // permission or I/O. Do not count repeated/stale observations as fresh.
    NormalResult step(std::uint8_t effective_mask);
    void reset();
private:
    FrontQualification qualification_;
    bool front_active_ = false;
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

struct SwingContext {
    bool edge_side_valid = false; // Genuine known side of a completed escape.
    motion::Direction edge_side = motion::Direction::RIGHT;
    std::uint64_t edge_age_us = 0; // Truthful ages, never raw wrapped timestamps.
    bool front_left_seen = false;
    bool front_right_seen = false;
    std::uint64_t front_left_age_us = 0;
    std::uint64_t front_right_age_us = 0;
    bool previous_swing_valid = false;
    motion::Direction previous_swing = motion::Direction::RIGHT;
};
struct SwingChoice {
    motion::Direction direction = motion::Direction::RIGHT;
    bool valid = false;
};
// B11/D-037/D-043: known edge age<RECENT_EDGE_MS -> away from that side;
// otherwise unseen front is older than seen, or larger age wins among two seen.
// Both unseen/equal age -> opposite previous actual swing, or RIGHT initially.
// Validate direction enums only if consumed; invalid consumed enum -> !valid.
// Caller preserves actual swing history across executor reset/start. Unknown or
// bilateral edge metadata must not invent a side; set edge_side_valid=false.
SwingChoice chooseSwing(const SwingContext& context);

enum class ReflankPhase : std::uint8_t { IDLE, BACK, SWING, TURN_IN, FINISHED, INVALID };
struct ReflankResult {
    motion::Result motion;
    governor::Profile profile = governor::Profile::REFLANK_TURN;
    Intent intent = Intent::NONE;
    ReflankPhase phase = ReflankPhase::IDLE;
    motion::Direction direction = motion::Direction::RIGHT;
    // One-call B15 entry notifications, decoded SWING then TURN_IN if both true.
    // BACK is recorded by the caller immediately on successful start, not later.
    bool entered_swing = false;
    bool entered_turn_in = false;
    bool turn_timed_out = false; // B7 timeout pulse, retained across transitions.
};
class Reflank {
public:
    // B11: finite initial/last-known heading, valid selected swing direction.
    // Enter BACK at this exact tick; caller records BACK and limiter admission.
    // Capture heading-held reverse at -REFLANK_BACK_DUTY for REFLANK_BACK_MS.
    // Failed start latches INVALID/zero. No motor permission is granted.
    bool start(std::uint32_t t_us, float heading_deg, bool imu_ok,
               motion::Direction direction);
    // Low seven effective bits only. BACK front + current contact cue skips
    // to SWING immediately; front alone is ignored in BACK/SWING. SWING pivots
    // REFLANK_PIVOT_DEG toward direction at TURN_DUTY, then arcs oppositely at
    // TURN_DUTY/REFLANK_ARC_RATIO for REFLANK_ARC_MS (time only, D-037).
    // Inner SL/RL for RIGHT, SR/RR for LEFT wins either SWING segment, including
    // its completion/timeout tick. Capture current valid finite relative bearing
    // in (-180,180] as one B7 TURN_IN target. Ignore unconsumed bearing payload;
    // invalid required bearing latches INVALID/zero (API defense, not fault policy).
    // D-040: TURN_IN retains captured turn despite lost/changed side readings;
    // current front or turn completion/timeout exits zero/PERCEPTION. Natural
    // arc completion also exits PERCEPTION. Caller applies D-038/D-045 centering.
    // TURN_IN front exits before checking yaw/deadlines. Otherwise healthy
    // nonfinite yaw invalidates active motion; unavailable yaw is ignored, with
    // last finite healthy yaw used for later entries and B7 fallback retained.
    // BACK profile REFLANK_BACK; all other phases REFLANK_TURN. Terminals are
    // zero/DONE, INVALID or IDLE and fallback=false, latched until start/reset.
    // At most four private-stage visits per call; new segments start at the
    // observed transition tick, never backdated. Entry/timeout flags never replay.
    // Caller owns edge/STOP preemption, limiter, events, governor and MotorGate.
    // No state assignment, clock, I/O or allocation; call gaps <one uint32 wrap.
    ReflankResult step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                       std::uint8_t effective_mask, bool contact_cue,
                       float bearing_deg, bool bearing_valid);
    void reset();
private:
    enum class Stage : std::uint8_t { IDLE, BACK, PIVOT, ARC, TURN_IN, FINISHED, INVALID };
    bool beginSwing(std::uint32_t t_us, bool imu_ok);
    bool beginTurnIn(std::uint32_t t_us, bool imu_ok, float bearing_deg, bool valid);
    bool advanceStage(std::uint32_t t_us, bool imu_ok);
    motion::Result runMotion(std::uint32_t t_us, float heading_deg, bool imu_ok);
    ReflankResult result(const motion::Result& motion) const;
    motion::Straight back_;
    motion::Turn turn_;
    motion::TimedArc arc_;
    Stage stage_ = Stage::IDLE;
    motion::Direction direction_ = motion::Direction::RIGHT;
    float last_heading_deg_ = 0.0F;
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
