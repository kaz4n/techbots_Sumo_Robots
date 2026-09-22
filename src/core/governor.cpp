// Applies the approved B6 compensation, final caps and acceleration slew.
// Makes brake, inhibit, reversal and safety-cap reductions immediate.
// Independent host tests check electrical limits across voltage, time and faults.
#include "governor.h"
#include "../config.h"
#include <algorithm>
#include <cmath>

namespace governor {
namespace {
static_assert(config::SEARCH_DUTY_MAX < 1.0F && config::TURN_DUTY < 1.0F &&
              config::OPENER_DUTY_MAX < 1.0F && config::ATTACK_APPROACH_DUTY < 1.0F &&
              config::EDGE_BACK_DUTY < 1.0F && config::REFLANK_BACK_DUTY < 1.0F,
              "R6 reserves full duty for centered contact in ATTACK");
static_assert(config::VBAT_FILTER_MS > 0 && config::VBAT_MIN_COMP_V > 0.0F);

bool profileCap(const Request& request, float& cap) {
    switch (request.profile) {
    case Profile::SEARCH_FORWARD: cap = config::SEARCH_DUTY_MAX; break;
    case Profile::PIVOT: cap = config::TURN_DUTY; break;
    case Profile::OPENER: cap = config::OPENER_DUTY_MAX; break;
    case Profile::ATTACK:
        cap = request.centered && request.contact ? config::ATTACK_DUTY :
                                                   config::ATTACK_APPROACH_DUTY;
        break;
    case Profile::EDGE_REVERSE: cap = config::EDGE_BACK_DUTY; break;
    case Profile::EDGE_FORWARD: cap = config::EDGE_BACK_DUTY; break;
    case Profile::REFLANK_BACK: cap = config::REFLANK_BACK_DUTY; break;
    case Profile::REFLANK_TURN: cap = config::TURN_DUTY; break;
    default: return false;
    }
    cap = std::clamp(cap, 0.0F, 1.0F);
    return true;
}

float shape(float requested, float previous, float cap, double scale, float rise) {
    // Double intermediates prevent overflow even for finite invalid-scale inputs;
    // the physical output remains inside the same specified electrical envelope.
    const float target = static_cast<float>(std::clamp(
        static_cast<double>(requested) * scale, -static_cast<double>(cap),
        static_cast<double>(cap)));
    if ((target < 0.0F && previous > 0.0F) ||
        (target > 0.0F && previous < 0.0F)) {
        return 0.0F;
    }
    if (std::abs(target) <= std::abs(previous)) {
        return target;
    }
    return std::copysign(std::min(std::abs(target), std::abs(previous) + rise), target);
}
} // namespace

Result Governor::step(std::uint32_t t_us, const Request& request) {
    Result result;
    const std::uint32_t elapsed_us = initialized_ ? t_us - last_us_ : 0U;
    last_us_ = t_us;
    initialized_ = true;
    float cap = 0.0F;
    result.valid = std::isfinite(request.duty_l) && std::isfinite(request.duty_r) &&
                   std::isfinite(request.vbat_v) && profileCap(request, cap);
    if (result.valid) {
        if (!battery_initialized_) {
            filtered_vbat_v_ = request.vbat_v;
            battery_initialized_ = true;
        } else {
            const double alpha = static_cast<double>(elapsed_us) /
                (static_cast<double>(config::VBAT_FILTER_MS) * 1000.0 + elapsed_us);
            filtered_vbat_v_ = static_cast<float>(filtered_vbat_v_ + alpha *
                (static_cast<double>(request.vbat_v) - filtered_vbat_v_));
        }
    }
    result.filtered_vbat_v = filtered_vbat_v_;
    if (!result.valid || request.inhibited || request.brake) {
        last_l_ = last_r_ = 0.0F;
        return result;
    }
    const double scale = static_cast<double>(config::V_NOM_V) /
        std::max(filtered_vbat_v_, config::VBAT_MIN_COMP_V);
    const float rise = config::SLEW_DUTY_PER_MS *
        (static_cast<float>(elapsed_us) / 1000.0F);
    last_l_ = shape(request.duty_l, last_l_, cap, scale, rise);
    last_r_ = shape(request.duty_r, last_r_, cap, scale, rise);
    result.duty_l = last_l_;
    result.duty_r = last_r_;
    return result;
}

void Governor::reset() {
    *this = Governor{};
}
} // namespace governor
