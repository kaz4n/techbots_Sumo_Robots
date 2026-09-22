// Defines B4 classification, persistent-edge guarding and specified row scripts.
// Separates bounded motion requests from unresolved selection and hardware writes.
// Locked host tests cover thresholds, rows, mirrors, timing and guard composition.
#pragma once
#include "core/motion.h"
#include "core/governor.h"
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
    motion::Result motion;
    governor::Profile profile = governor::Profile::EDGE_REVERSE;
    ScriptPhase phase = ScriptPhase::IDLE;
    bool brake = true; // Immediate governor braking in BRAKE and terminal phases.
    bool phase_changed = false;
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
    // Capture heading at each primitive entry, with B7 Straight correction and
    // Turn's existing tolerance/fallback/timeout; fixed bias uses TimedArc.
    // Pivots request TURN_DUTY/profile PIVOT; reverse EDGE_REVERSE; all forward
    // EDGE_FORWARD. BRAKE and terminals request zero with brake=true.
    // Done/timed-out primitives advance at this observation's time; never backdate
    // a new segment. Advance at most three phases/call. Capture one turn target,
    // never retarget; preserve any timeout pulse while entering the next phase.
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
};
} // namespace edge
