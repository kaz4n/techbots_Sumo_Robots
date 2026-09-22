// Defines B12 DIRECT and mirrored SIDESTEP/ARC motion and transition requests.
// Keeps script timing separate from global arbitration, governor and motor gates.
// Independent host tests cover detections, snapshot use, deadlines and mirroring.
#pragma once
#include "motion.h"
#include "governor.h"
#include "types.h"
#include <cstdint>

namespace openers {
// These are requests to the future FSM, not assignments of Robot state. The FSM
// must still enforce edge priority, centering/contact rules and motor permission.
enum class Exit : std::uint8_t { NONE, FRONT_TARGET, SIDE_OR_REAR_TARGET, SEARCH, INVALID };
struct Result {
    motion::Result motion;
    Exit exit = Exit::NONE;
};

class Direct {
public:
    // Capture finite last-known heading and time once. Start a DIRECT_MS straight
    // at OPENER_DUTY_MAX; only low seven snapshot bits are retained. Snapshot
    // front bits can end this opener on its first step, but snapshot side/rear
    // bits alone cannot. Starting/resetting returns no motor permission.
    bool start(std::uint32_t t_us, float heading_deg, std::uint8_t countdown_snapshot);
    // Confirmed CURRENT front detection or a saved front snapshot -> FRONT_TARGET;
    // otherwise CURRENT side/rear -> SIDE_OR_REAR_TARGET; deadline -> SEARCH.
    // Detections take precedence at the deadline, with front over side/rear (B2).
    // Every exit is latched and requests zero duty. While active, use approved
    // B7 straight/fallback semantics; pass all demands through OPENER governor.
    // Do not call this to bypass an escape/STOP/gate: the FSM owns preemption.
    Result step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                std::uint8_t confirmed_opp_mask);
    void reset();
private:
    motion::Straight straight_;
    Exit exit_ = Exit::NONE;
    std::uint8_t snapshot_ = 0;
    bool active_ = false;
};

enum class Phase : std::uint8_t { IDLE, PIVOT, TRAVERSE, TURN_IN, FINISHED, INVALID };
struct Sample {
    std::uint32_t t_us = 0;
    float heading_deg = 0.0F; // Continuous yaw, or caller's last-known finite yaw.
    bool imu_ok = false;
    std::uint8_t confirmed_mask = 0; // Current effective perception; high bit ignored.
    float bearing_deg = 0.0F; // Current B5 selected relative bearing, (-180,180].
    bool bearing_valid = false;
};
struct FlankResult {
    motion::Result motion;
    governor::Profile profile = governor::Profile::OPENER;
    Exit exit = Exit::NONE;
    Phase phase = Phase::IDLE;
    bool phase_changed = false;
    bool motion_timed_out = false; // Per-call pulse for any B7 timeout completion.
    bool scan_hint_valid = false; // Only SIDESTEP finishing into SEARCH supplies it.
    motion::Direction scan_direction = motion::Direction::LEFT;
};
class Flank {
public:
    // Only SIDESTEP_R/L and ARC_R/L are accepted. Capture finite initial heading.
    // Config-backed definitions share PIVOT -> TRAVERSE -> TURN_IN, mirrored once.
    // PIVOT uses relative +/-SS_PIVOT_DEG or +/-ARC_PIVOT_DEG at TURN_DUTY.
    bool start(std::uint32_t t_us, float heading_deg, bool imu_ok, core::Mode mode);
    // SIDESTEP: PIVOT ignores front/inner, outer side/rear exits (D-033).
    // DRIVE/TURN_IN front exits first, then outer exits. DRIVE inner side/rear
    // starts TURN_IN; otherwise SS_DRIVE_MS straight at OPENER_DUTY_MAX completes
    // into fixed relative -/+SS_TURNIN_DEG even with no current detection.
    // ARC: PIVOT ignores opponent detections. Arc turns toward the inner side
    // at ARC_DUTY/ARC_RATIO for ARC_SWEEP_DEG or ARC_MAX_MS. During ARC/TURN_IN,
    // front exits immediately. ARC inner side/rear starts bearing-directed TURN_IN;
    // completion also turns toward a current valid target, or SEARCH if none.
    // ARC has no SIDESTEP outer-side exception. No target invents a bearing:
    // required but missing/nonfinite/out-of-range bearing yields INVALID/zero.
    // TURN_IN captures one target at phase entry, never restarts/retargets. On
    // completion use current front/side-rear/none exit (D-034). SIDESTEP SEARCH
    // supplies inner-side scan hint; ARC SEARCH has no explicit hint.
    // Evaluate detections before motion completion. Advance at most three phases
    // per call; re-evaluate the new phase's aborts on the same tick. Each new
    // primitive starts at this call's time, never retrospectively. DONE/TIMED_OUT
    // advance; preserve a timeout pulse. Terminal exits latch zero until restart.
    // Use B7 fallback without deadline extensions; unavailable current yaw uses
    // the last observed finite heading at phase entry, never a fabricated yaw.
    // Pivot/turn-in use governor PIVOT (0.80 cap); DRIVE/ARC use OPENER (0.85).
    // Return the selected profile; caller must govern and preempt for edge/STOP.
    // Successive calls <one uint32 wrap; no permission, I/O, clock or allocation.
    FlankResult step(const Sample& sample);
    void reset();
private:
    struct Definition {
        float pivot_deg;
        float traverse_duty;
        std::uint32_t traverse_ms;
        float turn_in_deg; // Fixed for SIDESTEP; unused for bearing-directed ARC.
        bool arc;
    };
    const Definition& definition() const;
    bool beginTurn(std::uint32_t t_us, float relative_deg, bool imu_ok);
    bool beginTraverse(std::uint32_t t_us);
    bool beginTurnIn(const Sample& sample);
    Exit detectExit(std::uint8_t mask) const;
    Exit currentTarget(std::uint8_t mask) const;
    void finish(Exit exit);
    motion::Result runMotion(const Sample& sample);
    bool advancePhase(const Sample& sample);
    FlankResult result() const;
    motion::Turn turn_;
    motion::Straight straight_;
    motion::Arc arc_;
    Phase phase_ = Phase::IDLE;
    Exit exit_ = Exit::NONE;
    bool arc_mode_ = false;
    float mirror_ = 1.0F;
    float last_heading_deg_ = 0.0F;
};
} // namespace openers
