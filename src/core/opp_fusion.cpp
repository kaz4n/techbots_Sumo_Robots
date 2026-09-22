// Applies B5 debounce, bearing memory, contact, phantom and stuck qualification.
// Preserves target history while rejecting bounded phantom and stuck detections.
// Independent host tests cover masks, history, finite inputs and exact boundaries.
#include "opp_fusion.h"
#include "../config.h"
#include <cmath>
#include <limits>

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

ContactCue Contact::observeCue(std::uint8_t confirmed_mask, float ax_g,
                               float ay_g, bool imu_ok) {
    const auto front_mask = static_cast<std::uint8_t>(confirmed_mask & 0x07U);
    all_front_ticks_ = consecutiveContact(all_front_ticks_, front_mask == 0x07U);
    straddle_ticks_ = consecutiveContact(straddle_ticks_, front_mask == 0x05U);
    ContactCue result;
    result.close_cue =
        (front_mask == 0x07U && all_front_ticks_ >= config::CONTACT_TICKS) ||
        (front_mask == 0x05U && straddle_ticks_ >= config::CONTACT_TICKS);
    result.impact_cue = impactCue(ax_g, ay_g, imu_ok);
    result.cue = result.close_cue || result.impact_cue;
    return result;
}

ContactResult Contact::commitLatch(core::State state, std::uint8_t effective_mask,
                                   const ContactCue& cue) {
    ContactResult result{cue.close_cue, cue.impact_cue, cue.cue, false, false};
    const bool eligible = state == core::State::ATTACK &&
                          frontView(effective_mask).centered;
    const bool previous_contact = contact_;
    contact_ = eligible && (contact_ || result.cue);
    result.contact = contact_;
    result.contact_started = contact_ && !previous_contact;
    return result;
}

ContactResult Contact::step(core::State state, std::uint8_t confirmed_mask,
                            float ax_g, float ay_g, bool imu_ok) {
    const ContactCue cue = observeCue(confirmed_mask, ax_g, ay_g, imu_ok);
    return commitLatch(state, confirmed_mask, cue);
}

void Contact::reset() {
    all_front_ticks_ = 0U;
    straddle_ticks_ = 0U;
    contact_ = false;
}

void PhantomFilter::advance(std::uint32_t t_us) {
    const std::uint32_t elapsed_us = clock_started_ ? t_us - last_us_ : 0U;
    last_us_ = t_us;
    clock_started_ = true;
    const std::uint64_t window_us =
        static_cast<std::uint64_t>(config::PHANTOM_WINDOW_MS) * 1000U;
    // The window is inclusive: one past its end preserves permanent expiry.
    if (episode_ && episode_age_us_ <= window_us) {
        episode_age_us_ += elapsed_us;
        if (episode_age_us_ > window_us) {
            episode_age_us_ = window_us + 1U;
        }
    }
    if (active_) {
        const std::uint64_t lifetime_us =
            static_cast<std::uint64_t>(config::PHANTOM_MS) * 1000U;
        marker_age_us_ += elapsed_us;
        if (marker_age_us_ >= lifetime_us) {
            marker_age_us_ = lifetime_us;
            active_ = false;
        }
    }
}

PhantomResult PhantomFilter::step(const PhantomSample& sample) {
    advance(sample.t_us);
    const auto mask = static_cast<std::uint8_t>(sample.confirmed_mask & 0x7FU);
    const FrontView front = frontView(mask);
    const bool front_only = front.detected && (mask & 0x78U) == 0U;
    const bool chasing = front_only && (sample.state == core::State::TRACK ||
                                        sample.state == core::State::ATTACK);
    if (!chasing) {
        episode_ = contacted_ = consumed_ = false;
        episode_age_us_ = 0U;
    } else if (!episode_) {
        episode_ = true;
        episode_age_us_ = 0U;
    }
    const bool heading_valid = sample.imu_ok && std::isfinite(sample.heading_deg);
    const float world_deg = heading_valid && front_only ?
        worldBearing(sample.heading_deg, front.bearing_deg) : 0.0F;
    PhantomResult result;
    if (chasing) {
        contacted_ = contacted_ || sample.contact_cue;
        if (sample.edge_event && !consumed_) {
            // Even an ineligible edge cannot be replayed later in this chase.
            consumed_ = true;
            const std::uint64_t window_us =
                static_cast<std::uint64_t>(config::PHANTOM_WINDOW_MS) * 1000U;
            if (!contacted_ && heading_valid && episode_age_us_ <= window_us) {
                marker_deg_ = world_deg;
                marker_age_us_ = 0U;
                active_ = true;
                result.phantom_set = true;
            }
        }
    }
    result.filtered_mask = mask;
    if (active_ && front_only && !front.close && heading_valid) {
        const float separation_deg = std::fabs(worldBearing(world_deg, -marker_deg_));
        if (separation_deg <= static_cast<float>(config::PHANTOM_MASK_DEG)) {
            result.filtered_mask = 0U;
        }
    }
    result.active = active_;
    result.world_deg = active_ ? marker_deg_ : 0.0F;
    return result;
}

void PhantomFilter::reset() {
    last_us_ = 0U;
    episode_age_us_ = marker_age_us_ = 0U;
    marker_deg_ = 0.0F;
    clock_started_ = episode_ = contacted_ = consumed_ = active_ = false;
}

StuckResult StuckFilter::step(std::uint32_t t_us, std::uint8_t confirmed_mask,
                             float heading_deg, bool imu_ok) {
    const auto mask = static_cast<std::uint8_t>(confirmed_mask & 0x7FU);
    const std::uint32_t elapsed_us = clock_started_ ? t_us - last_us_ : 0U;
    last_us_ = t_us;
    clock_started_ = true;
    const std::uint32_t required_us = config::OPP_STUCK_MS * 1000U;
    const bool heading_valid = imu_ok && std::isfinite(heading_deg);
    StuckResult result;
    for (std::uint32_t i = 0U; i < 7U; ++i) {
        const auto bit = static_cast<std::uint8_t>(1U << i);
        if ((faults_ & bit) != 0U) {
            continue;
        }
        Candidate& candidate = candidates_[i];
        if ((mask & bit) == 0U || !heading_valid) {
            candidate = {};
            continue;
        }
        if (!candidate.active) {
            candidate = {0U, heading_deg, heading_deg, true};
        } else {
            // Saturate time so a late sweep still qualifies after many wraps.
            candidate.age_us = elapsed_us >= required_us - candidate.age_us ?
                required_us : candidate.age_us + elapsed_us;
            if (heading_deg < candidate.min_deg) {
                candidate.min_deg = heading_deg;
            }
            if (heading_deg > candidate.max_deg) {
                candidate.max_deg = heading_deg;
            }
        }
        const double span_deg = static_cast<double>(candidate.max_deg) -
                                static_cast<double>(candidate.min_deg);
        if (candidate.age_us >= required_us && span_deg > 360.0) {
            faults_ |= bit;
            result.new_fault_mask |= bit;
        }
    }
    result.filtered_mask = static_cast<std::uint8_t>(mask & ~faults_);
    result.fault_mask = faults_;
    return result;
}

void StuckFilter::reset() {
    for (auto& candidate : candidates_) {
        candidate = {};
    }
    last_us_ = 0U;
    faults_ = 0U;
    clock_started_ = false;
}

FusionObservation Fusion::observe(const FusionSample& sample) {
    if (observed_ && sample.t_us == observed_us_) {
        FusionObservation cached = observation_;
        cached.fresh = false;
        cached.stuck.new_fault_mask = 0U;
        cached.phantom.phantom_set = false;
        return cached;
    }
    if (pending_) {
        // A skipped commitment cannot carry an older contact into a new tick.
        contact_.commitLatch(core::State::IDLE, 0U, {});
    }
    observed_us_ = sample.t_us;
    observed_ = pending_ = true;
    observation_.confirmed_mask = debounce_.step(sample.t_us, sample.raw_mask);
    observation_.stuck = stuck_.step(sample.t_us, observation_.confirmed_mask,
                                     sample.heading_deg, sample.imu_ok);
    observation_.cue = contact_.observeCue(observation_.stuck.filtered_mask,
                                           sample.ax_g, sample.ay_g, sample.imu_ok);
    observation_.phantom = phantom_.step({sample.t_us, sample.prior_state,
        observation_.stuck.filtered_mask, sample.heading_deg, sample.imu_ok,
        sample.edge_event, observation_.cue.cue});
    // BearingMemory accepts a finite yaw as evidence; reject stale unavailable yaw.
    const float heading_deg = sample.imu_ok ? sample.heading_deg :
        std::numeric_limits<float>::quiet_NaN();
    observation_.bearing = bearing_.step(sample.t_us,
        observation_.phantom.filtered_mask, heading_deg);
    observation_.fresh = true;
    return observation_;
}

ContactCommit Fusion::commit(core::State selected_state) {
    if (!pending_) {
        contact_.commitLatch(core::State::IDLE, 0U, {});
        return {};
    }
    pending_ = false;
    return {contact_.commitLatch(selected_state, observation_.phantom.filtered_mask,
                                 observation_.cue), true};
}

const Memory& Fusion::memory() const {
    return bearing_.memory();
}

void Fusion::reset() {
    debounce_.reset();
    stuck_.reset();
    contact_.reset();
    phantom_.reset();
    bearing_.reset();
    observation_ = {};
    observed_us_ = 0U;
    observed_ = pending_ = false;
}
} // namespace opp_fusion
