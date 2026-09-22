// Defines B11.3 rolling re-flank admission and the approved D-025 ALL_IN timer.
// Bounds repeated maneuvers without granting motor duty or bypassing safety gates.
// Spec-derived host tests exercise capacity, exact deadlines, reset and time wrap.
#pragma once
#include "config.h"
#include <cstdint>

namespace stall {
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
