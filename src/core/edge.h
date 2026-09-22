// Defines B4 classification, persistent-edge guarding, rows and escape composition.
// Separates bounded motion requests and approved recovery faults from hardware writes.
// Locked host tests cover thresholds, rows, selection, replanning and inhibition.
#pragma once
#include "motion.h"
#include "governor.h"
#include <cstdint>

namespace edge {
enum class ForwardBias : std::uint8_t { NONE, LEFT, RIGHT };
struct ForwardDemand {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    bool valid = false;
};
// B4.2/D-021 base requests only: NONE is straight, LEFT slows the left/inner side
// (rear-right row), RIGHT mirrors it (rear-left row). Pass these requests through
// governor EDGE_FORWARD, with the guard's veto. This does not run a timed script
// or heading hold; 70% is the requested ratio before compensation/caps/slew.
// Unknown bias values return invalid zero demand.
ForwardDemand forwardDemand(ForwardBias bias);

class Classifier {
public:
    // Each call represents one NEW complete observation. Repeated/stale samples
    // must not be passed as fresh. This API does not implement or validate a HAL.
    // Returns confirmed white levels (not rising edges), so white persists.
    std::uint8_t observe(const std::uint32_t (&raw_us)[4]);
    void reset();
private:
    std::uint32_t consecutive_[4] = {};
};

struct GuardResult {
    bool escape_required = false;
    bool fault_latched = false;
    bool inhibit_motion = true; // A veto; false does not itself authorize motion.
};
class Guard {
public:
    // One confirmed fresh line mask per tick; only the low four bits are used.
    // This implements the default zero push-through window only; compilation
    // rejects a positive configured window until that bounded exception exists.
    // Before motion permission, do not enter escape/latch a new line fault.
    // Afterwards any persistent white requires escape. Once entered, all black
    // AND script_finished are both required to leave. All-white latches a motion
    // veto until reset, even if later black or permission is revoked. When the
    // permission gate is closed, escape_required is false and inhibition wins.
    // This does not choose a motion direction or execute a script/MotorGate.
    GuardResult step(std::uint8_t line_mask, bool motion_permitted,
                     bool script_finished);
    void reset();
private:
    bool escaping_ = false;
    bool fault_latched_ = false;
};

enum class ScriptPhase : std::uint8_t {
    IDLE, BRAKE, BACK, PIVOT, FORWARD, DONE, UNSUPPORTED, INVALID
};
struct RowResult {
    // Current primitive status while moving; DONE for completed row, INVALID
    // for invalid/unsupported row, IDLE before start. Terminal fallback is false.
    motion::Result motion;
    // Profile is meaningful in moving phases; brake overrides it elsewhere.
    governor::Profile profile = governor::Profile::EDGE_REVERSE;
    ScriptPhase phase = ScriptPhase::IDLE;
    bool brake = true; // Immediate governor braking in BRAKE and terminal phases.
    bool phase_changed = false; // Changes made by step only; start establishes initial phase.
    bool turn_timed_out = false; // One-call B7 timeout pulse, not replayed.
};
class RowExecutor {
public:
    // Execute an already-selected B4.2 row; this does not select B4.3 precedence.
    // Supported low-four-bit masks:1/9 FL,2/6 FR,4 RL,8 RR,C both rear,5/A side.
    // Other masks return false/UNSUPPORTED/zero (API coverage, not a recovery
    // policy). Unsupported mask classification precedes heading validation.
    // Supported rows require finite initial/last-known heading even without IMU.
    // Front/diagonal: brake TICK_US from start, reverse EDGE_BACK_MS at the
    // negative EDGE_BACK_DUTY, pivot away by EDGE_TURN_DEG. RR/RL: forward
    // EDGE_FWD_MS, inner left/right at EDGE_FWD_INNER_RATIO. Both rear: straight
    // forward for that duration. Side: pivot away EDGE_SIDE_TURN_DEG, then straight
    // forward. Every forward base is EDGE_BACK_DUTY (D-021).
    bool start(std::uint32_t t_us, std::uint8_t selected_mask,
               float heading_deg, bool imu_ok);
    // B4.2/D-044 explicit head-on entry: brake one complete TICK_US, then
    // heading-held reverse EDGE_BACK_LONG_MS at -EDGE_BACK_DUTY, then pivot
    // EDGE_TURN_FULL_DEG toward the caller-selected last-opponent side.
    // A valid direction and finite initial/last-known heading are required;
    // otherwise latch INVALID/zero. This overload neither selects a side from
    // sensor history nor changes start(mask)'s established supported-mask set.
    // All existing step timing, profiles, fallback and guard obligations apply.
    bool startHeadOn(std::uint32_t t_us, float heading_deg, bool imu_ok,
                     motion::Direction opponent_side);
    // B4.3/D-049 already-selected pushed-out maneuver: pivot in the explicit
    // direction by EDGE_SIDE_TURN_DEG at TURN_DUTY, then straight forward for
    // EDGE_FWD_MS at EDGE_BACK_DUTY. No initial brake/reverse. Finite initial
    // heading and a valid direction required; invalid entry latches INVALID.
    // Does not change start(mask)'s established supported set or select priority.
    bool startPushedOut(std::uint32_t t_us, float heading_deg, bool imu_ok,
                        motion::Direction direction);
    // Capture heading at each primitive entry, with B7 Straight correction and
    // Turn's existing tolerance/fallback/timeout; fixed bias uses TimedArc.
    // Pivots request TURN_DUTY/profile PIVOT; reverse EDGE_REVERSE; all forward
    // EDGE_FORWARD. BRAKE and terminals request zero with brake=true.
    // Done/timed-out primitives advance at this observation's time; never backdate
    // a new segment. Advance at most three phases/call. Capture one turn target,
    // never retarget; preserve any timeout pulse while entering the next phase.
    // Pivots use Turn::startRelative with the captured raw heading, preserving
    // B7's strict tolerance without rounding heading+angle through float first.
    // Healthy nonfinite current yaw latches INVALID/zero; unavailable current yaw
    // is ignored, retaining the last finite healthy heading for later phase entry.
    // Terminal results remain zero until start/reset. DONE only means this row
    // finished: Guard still requires all black, and all-white must inhibit it.
    // Caller owns edge/STOP preemption, replans and valid inward-heading recording
    // at actual escape exit. No synthetic heading or motion permission is supplied.
    // Consecutive calls <one uint32 micros wrap. No clock, I/O or allocation.
    RowResult step(std::uint32_t t_us, float heading_deg, bool imu_ok);
    void reset();
private:
    bool beginPhase(std::uint32_t t_us, ScriptPhase phase, bool imu_ok);
    bool advancePhase(std::uint32_t t_us, bool imu_ok);
    motion::Result runMotion(std::uint32_t t_us, float heading_deg, bool imu_ok);
    RowResult result(const motion::Result& motion) const;
    motion::Interval brake_interval_;
    motion::Turn turn_;
    motion::Straight straight_;
    motion::TimedArc arc_;
    ScriptPhase phase_ = ScriptPhase::IDLE;
    float last_heading_deg_ = 0.0F;
    float pivot_deg_ = 0.0F;
    motion::Direction bias_direction_ = motion::Direction::LEFT;
    bool front_row_ = false;
    bool biased_forward_ = false;
    bool head_on_ = false;
};

enum class EscapeFault : std::uint8_t {
    NONE, WHITE_PATTERN, REPLAN_LIMIT, PERMISSION_LOST, INVALID_CONTEXT
};
struct EscapeSample {
    std::uint32_t t_us = 0U;
    std::uint8_t line_mask = 0U;
    float heading_deg = 0.0F;
    bool imu_ok = false;
    bool motion_permitted = false;
    bool centered_front = false;
    float applied_duty_l = 0.0F;
    float applied_duty_r = 0.0F;
    motion::Direction opponent_side = motion::Direction::RIGHT;
};
struct EscapeResult {
    RowResult row;
    EscapeFault fault = EscapeFault::NONE;
    bool escape_required = false;
    bool inhibit_motion = true; // Veto only; false never grants motor permission.
    bool entered = false;
    bool exited = false;
    bool replanned = false;
    std::uint32_t replans = 0U;
    std::uint8_t selected_mask = 0U;
    bool pushed_out = false;
    motion::Direction pivot_direction = motion::Direction::RIGHT; // Meaningful in PIVOT.
    bool inward_valid = false; // Exit pulse only; no stale heading/timestamp refresh.
    float inward_heading_deg = 0.0F;
};
class Escape {
public:
    // B4/D-020/D-047..D-050/D-054 composition. Each call consumes ONE NEW,
    // confirmed line observation (low four bits); caller must not repeat stale
    // QTR data. This does not resolve physical acquisition timing/freshness.
    // Closed permission while inactive: zero/inhibited, no new line/context
    // fault. Revoking permission during an active episode latches PERMISSION_LOST;
    // neither repermission nor black clears it or resets its replan budget.
    // Any fault persists until reset. escape_required is false while permission
    // is closed, otherwise true while active/faulted. Reset must track Robot reset.
    //
    // With permission: 3/4 white bits first latch WHITE_PATTERN/zero/inhibited.
    // Initial persistent white enters immediately with zero replacements used.
    // Row selection: rear bit + current centered_front + BOTH previously applied
    // FINAL electrical duties >0 selects pushed-out. Single rear pivots away;
    // both rear pivots opposite opponent_side. Otherwise mask3 selects head-on
    // toward opponent_side; other nonzero supported masks use the B4.2 rows.
    // Caller supplies D-047/D-041 shared side memory, default RIGHT; selection
    // captures it. Do not retarget a row when later opponent context changes.
    //
    // On each active observation, compare new bits with the previous admitted
    // mask. During the phase present at CALL ENTRY, PIVOT replans only for bits
    // on its captured intended turning side (LEFT=FL/RL, RIGHT=FR/RR), regardless
    // of overshoot correction sign. Other active phases replan for any new bit.
    // Otherwise advance the row; DONE with persistent white also replans on this
    // observation. At most ONE replacement start/call. Allow EDGE_MAX_REPLANS
    // replacements; the next request latches REPLAN_LIMIT without starting motion.
    // Update the mask baseline on every admitted sample, including clears; never
    // reset it/budget merely on replacement. New rows/phases start at observed time.
    //
    // Exit only all-black AND row DONE; emit exited once, zero row, reset budget.
    // Emit inward_valid/current raw yaw only if that exit has healthy finite IMU;
    // otherwise false/zero. Caller owns retained history and its actual timestamp.
    // At initial row start heading must be finite even without IMU (last-known
    // coordinate). In active rows healthy nonfinite yaw faults; unavailable yaw
    // is ignored and replans use retained last valid heading. No synthetic yaw.
    // Validate BOTH duties as finite [-1,1] only at selection when rear+centered
    // consumes that predicate; validate opponent_side only for head-on or selected
    // both-rear pushed-out. Unused contexts ignored; fault masks/permission win.
    // Invalid consumed context/row latches INVALID_CONTEXT; no budget increment
    // for a failed replacement start. Fault/closed/idle/exit requests are zero,
    // brake=true; any fault row is INVALID even with permission closed. Otherwise
    // closed/idle is IDLE and actual exit is DONE. entered is the first permitted
    // nonzero-mask entry, including an immediate pattern/context/start fault;
    // replanned means a successful replacement start, not an attempted one.
    // Timeout pulse is retained when an old row finishes and is replaced/exited.
    // All motion requests still require governor + MotorGate; no I/O or allocation.
    EscapeResult step(const EscapeSample& sample);
    void reset();
private:
    bool startRow(const EscapeSample& sample, bool replacement);
    bool advanceRow(const EscapeSample& sample, std::uint8_t new_bits);
    bool needsReplan(std::uint8_t new_bits) const;
    void latchFault(EscapeFault fault);
    EscapeResult result(bool permitted) const;
    Guard guard_;
    RowExecutor row_;
    RowResult current_;
    EscapeFault fault_ = EscapeFault::NONE;
    float last_heading_deg_ = 0.0F;
    std::uint32_t replans_ = 0U;
    std::uint8_t previous_mask_ = 0U;
    std::uint8_t selected_mask_ = 0U;
    motion::Direction pivot_direction_ = motion::Direction::RIGHT;
    bool active_ = false;
    bool pushed_out_ = false;
};
} // namespace edge
