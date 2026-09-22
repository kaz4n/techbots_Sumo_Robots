// Defines the B12 O2 DIRECT opener as a pure motion/transition request.
// Keeps script timing separate from global arbitration, governor and motor gates.
// Independent host tests cover detections, snapshot use, deadlines and mirroring.
#pragma once
#include "core/motion.h"
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
} // namespace openers
