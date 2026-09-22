// Applies B5 debounce, bearing selection and memory, and contact qualification.
// Preserves observed target history while limiting contact to centered ATTACK.
// Independent host tests cover masks, recency, finite inputs and latch boundaries.
#include "opp_fusion.h"
#include "../config.h"
#include <cmath>

namespace opp_fusion {
FrontView frontView(std::uint8_t confirmed_mask) {
    switch (confirmed_mask & 0x07U) {
    case 0x01U: return {true, false, false, -15.0F};
    case 0x02U: return {true, true, false, 0.0F};
    case 0x03U: return {true, true, false, -6.0F};
    case 0x04U: return {true, false, false, 15.0F};
    case 0x05U: return {true, true, true, 0.0F};
    case 0x06U: return {true, true, false, 6.0F};
    case 0x07U: return {true, true, true, 0.0F};
    default: return {};
    }
}

std::uint8_t Debouncer::step(std::uint32_t t_us, std::uint8_t raw_mask) {
    const auto detected_mask = static_cast<std::uint8_t>(
        (raw_mask ^ config::OPP_ACTIVE_LOW_MASK) & 0x7FU);
    for (std::uint32_t i = 0U; i < 7U; ++i) {
        const auto bit = static_cast<std::uint8_t>(1U << i);
        const auto other_bits = static_cast<std::uint8_t>(~bit);
        if ((detected_mask & bit) != 0U) {
            if (detected_ticks_[i] < config::OPP_SET_TICKS) {
                ++detected_ticks_[i];
            }
            if (detected_ticks_[i] >= config::OPP_SET_TICKS) {
                confirmed_mask_ |= bit;
            }
            clearing_mask_ &= other_bits;
            continue;
        }
        detected_ticks_[i] = 0U;
        // A separate active bit keeps timestamp zero valid, including at wrap.
        if ((clearing_mask_ & bit) == 0U) {
            clear_since_us_[i] = t_us;
            clearing_mask_ |= bit;
        }
        const std::uint32_t clear_elapsed_us = t_us - clear_since_us_[i];
        if (clear_elapsed_us >= config::OPP_CLEAR_MS * 1000U) {
            confirmed_mask_ &= other_bits;
        }
    }
    return confirmed_mask_;
}

void Debouncer::reset() {
    for (std::uint32_t i = 0U; i < 7U; ++i) {
        detected_ticks_[i] = 0U;
        clear_since_us_[i] = 0U;
    }
    clearing_mask_ = 0U;
    confirmed_mask_ = 0U;
}

namespace {
BearingView selectBearing(std::uint8_t mask, const Memory& memory) {
    BearingView view;
    const FrontView front = frontView(mask);
    if (front.detected) {
        view.group = Group::FRONT;
        view.detected = view.bearing_valid = true;
        view.centered = front.centered;
        view.close = front.close;
        view.relative_deg = front.bearing_deg;
        return view;
    }
    const auto side = static_cast<std::uint8_t>(mask & 0x18U);
    const auto rear = static_cast<std::uint8_t>(mask & 0x60U);
    if (side == 0U && rear == 0U) {
        return view;
    }
    view.detected = view.bearing_valid = true;
    if (side != 0U) {
        view.group = Group::SIDE;
        view.conflict = side == 0x18U;
        view.relative_deg = side == 0x08U ? -90.0F : 90.0F;
    } else {
        view.group = Group::REAR;
        view.conflict = rear == 0x60U;
        view.relative_deg = rear == 0x20U ? -135.0F : 135.0F;
    }
    if (view.conflict) {
        view.bearing_valid = memory.valid;
        view.relative_deg = memory.valid ? memory.last_rel_bearing_deg : 0.0F;
    }
    return view;
}

float worldBearing(float heading_deg, float relative_deg) {
    // Reduce heading first so an extreme finite heading cannot swallow the
    // relative angle during addition or cause an input-dependent wrap loop.
    double angle = std::fmod(static_cast<double>(heading_deg), 360.0) +
                   static_cast<double>(relative_deg);
    if (angle > 180.0) {
        angle -= 360.0;
    } else if (angle <= -180.0) {
        angle += 360.0;
    }
    const float result = static_cast<float>(angle);
    // Rounding back to float can land on the excluded endpoint.
    return result <= -180.0F ? 180.0F : result;
}

std::uint32_t consecutiveContact(std::uint32_t previous, bool matches) {
    if (!matches) {
        return 0U;
    }
    return previous < config::CONTACT_TICKS ? previous + 1U : previous;
}

bool impactCue(float ax_g, float ay_g, bool imu_ok) {
    if (!imu_ok || !std::isfinite(ax_g) || !std::isfinite(ay_g)) {
        return false;
    }
    // Float inputs squared in double stay finite even at float's limits.
    const double ax = static_cast<double>(ax_g);
    const double ay = static_cast<double>(ay_g);
    return std::sqrt(ax * ax + ay * ay) >
           static_cast<double>(config::IMPACT_G);
}
} // namespace

void BearingMemory::rememberFrontSide(std::uint32_t t_us, std::uint8_t mask) {
    const auto rising = static_cast<std::uint8_t>(mask & ~previous_mask_ & 0x05U);
    previous_mask_ = mask;
    if ((rising & 0x01U) != 0U) {
        memory_.left_seen = true;
        memory_.left_seen_us = t_us;
    }
    if ((rising & 0x04U) != 0U) {
        memory_.right_seen = true;
        memory_.right_seen_us = t_us;
    }
    // A simultaneous pair records both observations without choosing a side.
    if (rising == 0x01U) {
        memory_.last_front_side = FrontSide::LEFT;
    } else if (rising == 0x04U) {
        memory_.last_front_side = FrontSide::RIGHT;
    }
}

BearingView BearingMemory::step(std::uint32_t t_us, std::uint8_t confirmed_mask,
                                float heading_deg) {
    const auto mask = static_cast<std::uint8_t>(confirmed_mask & 0x7FU);
    rememberFrontSide(t_us, mask);
    BearingView view = selectBearing(mask, memory_);
    if (!view.bearing_valid) {
        return view;
    }
    view.world_valid = std::isfinite(heading_deg);
    view.world_deg = view.world_valid ? worldBearing(heading_deg, view.relative_deg) :
                                       0.0F;
    memory_.valid = true;
    memory_.world_valid = view.world_valid;
    memory_.last_rel_bearing_deg = view.relative_deg;
    memory_.last_world_bearing_deg = view.world_deg;
    memory_.last_seen_us = t_us;
    return view;
}

const Memory& BearingMemory::memory() const {
    return memory_;
}

void BearingMemory::reset() {
    memory_ = {};
    previous_mask_ = 0U;
}

ContactResult Contact::step(core::State state, std::uint8_t confirmed_mask,
                            float ax_g, float ay_g, bool imu_ok) {
    const auto front_mask = static_cast<std::uint8_t>(confirmed_mask & 0x07U);
    all_front_ticks_ = consecutiveContact(all_front_ticks_, front_mask == 0x07U);
    straddle_ticks_ = consecutiveContact(straddle_ticks_, front_mask == 0x05U);
    ContactResult result;
    result.close_cue =
        (front_mask == 0x07U && all_front_ticks_ >= config::CONTACT_TICKS) ||
        (front_mask == 0x05U && straddle_ticks_ >= config::CONTACT_TICKS);
    result.impact_cue = impactCue(ax_g, ay_g, imu_ok);
    result.cue = result.close_cue || result.impact_cue;
    const bool eligible = state == core::State::ATTACK &&
                          frontView(confirmed_mask).centered;
    const bool previous_contact = contact_;
    contact_ = eligible && (contact_ || result.cue);
    result.contact = contact_;
    result.contact_started = contact_ && !previous_contact;
    return result;
}

void Contact::reset() {
    all_front_ticks_ = 0U;
    straddle_ticks_ = 0U;
    contact_ = false;
}
} // namespace opp_fusion
