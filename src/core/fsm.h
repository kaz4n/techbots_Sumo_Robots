// Defines bounded B10 defensive-turn requests for the future Robot arbiter.
// Keeps state deadlines and target exits separate from motor permission and I/O.
// Independent host tests cover capture, target priority, both deadlines and wrap.
#pragma once
#include "core/motion.h"
#include "core/governor.h"
#include "core/types.h"
#include <cstdint>

namespace fsm {
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
