// Defines B11.3 rolling re-flank admission and the approved D-025 ALL_IN timer.
// Bounds repeated maneuvers without granting motor duty or bypassing safety gates.
// Spec-derived host tests exercise capacity, exact deadlines, reset and time wrap.
#pragma once
#include "../config.h"
#include "types.h"
#include <cstdint>

namespace stall {
struct Sample {
    std::uint32_t t_us = 0;
    core::State state = core::State::IDLE;
    bool centered = false;
    bool contact = false;
    bool contact_started = false;
    bool edge_event = false;
    float duty_l = 0.0F; // Final electrical duties after governor, forward positive.
    float duty_r = 0.0F;
    float heading_deg = 0.0F; // Continuous yaw; never wrap the contact deflection.
    bool imu_ok = false;
    bool suppress = false; // D-025 ALL_IN: suppress result, retain actual history.
};
struct Detection {
    bool qualified = false;
    bool timer_trigger = false;
    bool deflection_trigger = false;
    bool stalled = false; // Level, not a one-shot recorder event.
};
class Detector {
public:
    // D-032: centered ATTACK contact, both finite forward final duties in
    // [STALL_MIN_DUTY,1], and no edge since contact qualify both trigger routes.
    // Continuous qualification >= STALL_MS OR valid |yaw-contact_yaw| strictly
    // > STALL_DEFLECT_DEG triggers. Failing qualification resets only its timer;
    // edge evidence persists for that contact. Fresh contact resets both histories.
    // Infer a contact start on entry if the caller omitted its rising flag.
    // Anchor deflection only if heading is finite/IMU-valid at contact start.
    // Missing current heading disables deflection only; timer remains usable.
    // Suppression leaves qualification/history intact; it vetoes stalled only.
    // No motion permission or duty output. STALL_USE_IMU must remain zero.
    // Successive call gaps must be less than one uint32 micros wrap.
    Detection step(const Sample& sample);
    void reset();
private:
    std::uint32_t last_us_ = 0;
    std::uint32_t qualified_us_ = 0;
    float contact_heading_deg_ = 0.0F;
    bool contact_active_ = false;
    bool anchor_valid_ = false;
    bool edge_since_contact_ = false;
    bool qualified_ = false;
};

struct LimitResult {
    bool allowed = false; // This call admitted and recorded a new re-flank.
    bool all_in_active = false; // Suppress stall output only, per D-025.
    bool all_in_started = false; // One-call notification, never a duty request.
    std::uint32_t attempts_in_window = 0;
};

class ReflankLimiter {
public:
    // Admit at most REFLANK_MAX_PER_10S starts in (now-window, now]. Accepted
    // starts count even if the maneuver is subsequently interrupted. At full
    // capacity, deny and start ALL_IN_MS suppression. Denied requests consume
    // no slots; requests while suppressed cannot extend its deadline. Once
    // suppression expires a new request reevaluates capacity normally.
    LimitResult request(std::uint32_t t_us);
    // Advance timers without asking to start a maneuver. No new ALL_IN period
    // is started by step(). At exactly either deadline the old period expires.
    // Time is caller supplied; successive call gaps must be < one uint32 wrap.
    // Expired history cannot reappear after later microsecond clock wraps.
    LimitResult step(std::uint32_t t_us);
    void reset();
private:
    void advance(std::uint32_t t_us);
    LimitResult result() const;
    std::uint32_t ages_us_[config::REFLANK_MAX_PER_10S] = {};
    std::uint32_t count_ = 0;
    std::uint32_t last_us_ = 0;
    std::uint32_t all_in_age_us_ = 0;
    bool clock_started_ = false;
    bool all_in_ = false;
};
} // namespace stall
