// Implements B11.3 rolling re-flank admission and the D-025 ALL_IN interval.
// Keeps bounded maneuver history without granting duty or motor permission.
// Independent host tests cover rolling limits, suppression, reset and clock wrap.
#include "core/stall.h"
#include <limits>
#include <algorithm>
#include <cmath>

namespace stall {
namespace {
static_assert(config::STALL_USE_IMU == 0U,
              "Displacement refinement requires P4 evidence and implementation");
static_assert(config::STALL_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U,
              "Stall interval must fit microseconds");
static_assert(config::REFLANK_MAX_PER_10S > 0U, "Re-flank capacity must be positive");
static_assert(config::REFLANK_WINDOW_MS > 0U &&
              config::REFLANK_WINDOW_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U,
              "Re-flank window must fit microseconds");
static_assert(config::ALL_IN_MS > 0U &&
              config::ALL_IN_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U,
              "ALL_IN interval must fit microseconds");
constexpr std::uint32_t WINDOW_US = config::REFLANK_WINDOW_MS * 1000U;
constexpr std::uint32_t ALL_IN_US = config::ALL_IN_MS * 1000U;
constexpr std::uint32_t STALL_US = config::STALL_MS * 1000U;

bool qualifiedDuty(float duty) {
    return std::isfinite(duty) && duty >= config::STALL_MIN_DUTY && duty <= 1.0F;
}
} // namespace

Detection Detector::step(const Sample& sample) {
    if (sample.state != core::State::ATTACK || !sample.contact) {
        reset();
        return {};
    }
    if (!contact_active_ || sample.contact_started) {
        contact_active_ = true;
        anchor_valid_ = sample.imu_ok && std::isfinite(sample.heading_deg);
        contact_heading_deg_ = anchor_valid_ ? sample.heading_deg : 0.0F;
        edge_since_contact_ = false;
        qualified_ = false;
        qualified_us_ = 0U;
        last_us_ = sample.t_us;
    }
    edge_since_contact_ = edge_since_contact_ || sample.edge_event;
    Detection result;
    result.qualified = sample.centered && !edge_since_contact_ && qualifiedDuty(sample.duty_l) &&
                       qualifiedDuty(sample.duty_r);
    const std::uint32_t delta = sample.t_us - last_us_;
    if (result.qualified && qualified_) {
        const auto elapsed = static_cast<std::uint64_t>(qualified_us_) + delta;
        qualified_us_ = static_cast<std::uint32_t>(std::min<std::uint64_t>(elapsed, STALL_US));
    } else {
        qualified_us_ = 0U;
    }
    qualified_ = result.qualified;
    last_us_ = sample.t_us;
    result.timer_trigger = qualified_ && qualified_us_ >= STALL_US;
    result.deflection_trigger = qualified_ && anchor_valid_ && sample.imu_ok &&
        std::isfinite(sample.heading_deg) &&
        std::abs(static_cast<double>(sample.heading_deg) - contact_heading_deg_) >
            config::STALL_DEFLECT_DEG;
    result.stalled = !sample.suppress && (result.timer_trigger || result.deflection_trigger);
    return result;
}

void Detector::reset() { *this = Detector{}; }

void ReflankLimiter::advance(std::uint32_t t_us) {
    const std::uint32_t delta_us = clock_started_ ? t_us - last_us_ : 0U;
    last_us_ = t_us;
    clock_started_ = true;
    std::uint32_t retained = 0;
    for (std::uint32_t i = 0; i < count_; ++i) {
        const auto age = static_cast<std::uint64_t>(ages_us_[i]) + delta_us;
        if (age < WINDOW_US) {
            ages_us_[retained++] = static_cast<std::uint32_t>(age);
        }
    }
    count_ = retained;
    if (all_in_) {
        const auto age = static_cast<std::uint64_t>(all_in_age_us_) + delta_us;
        all_in_ = age < ALL_IN_US;
        all_in_age_us_ = all_in_ ? static_cast<std::uint32_t>(age) : 0U;
    }
}

LimitResult ReflankLimiter::result() const {
    LimitResult view;
    view.all_in_active = all_in_;
    view.attempts_in_window = count_;
    return view;
}

LimitResult ReflankLimiter::request(std::uint32_t t_us) {
    advance(t_us);
    if (all_in_) return result();
    if (count_ < config::REFLANK_MAX_PER_10S) {
        ages_us_[count_++] = 0U;
        auto view = result();
        view.allowed = true;
        return view;
    }
    all_in_ = true;
    all_in_age_us_ = 0U;
    auto view = result();
    view.all_in_started = true;
    return view;
}

LimitResult ReflankLimiter::step(std::uint32_t t_us) {
    advance(t_us);
    return result();
}

void ReflankLimiter::reset() { *this = ReflankLimiter{}; }
} // namespace stall
