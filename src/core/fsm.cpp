// Implements B9 front qualification/steering and bounded B10 defensive turns.
// Keeps request math and captured commands separate from motor authorization.
// Independent host tests cover table rows, capture, caps, deadlines and wrap.
#include "core/fsm.h"
#include "core/opp_fusion.h"
#include "config.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace fsm {
namespace {
static_assert(config::DEFEND_EVADE_FIRST == 0U,
              "Defensive evade requires its P4-backed implementation");
static_assert(config::DEFEND_TIMEOUT_MS <=
              std::numeric_limits<std::uint32_t>::max() / 1000U,
              "Defend duration must fit uint32 microseconds");

float normalizedHeading(float heading_deg) {
    if (!std::isfinite(heading_deg)) return heading_deg;
    double angle = std::fmod(static_cast<double>(heading_deg), 360.0);
    if (angle <= -180.0) angle += 360.0;
    if (angle > 180.0) angle -= 360.0;
    const float result = static_cast<float>(angle);
    return result <= -180.0F ? 180.0F : result;
}
} // namespace

FrontQualificationResult FrontQualification::observe(std::uint8_t effective_mask) {
    const auto view = opp_fusion::frontView(effective_mask);
    if (!view.centered) {
        centered_ticks_ = 0U;
    } else if (centered_ticks_ < config::ATTACK_ENTER_TICKS) {
        ++centered_ticks_;
    }
    return {view.detected, view.centered,
            view.centered && centered_ticks_ >= config::ATTACK_ENTER_TICKS};
}

void FrontQualification::reset() { centered_ticks_ = 0U; }

FrontDemand frontDemand(core::State state, std::uint8_t effective_mask, bool contact) {
    FrontDemand result;
    const auto view = opp_fusion::frontView(effective_mask);
    const bool attack = state == core::State::ATTACK;
    if (!view.detected || (state != core::State::TRACK && !attack) ||
        (attack && !view.centered)) return result;
    float base = config::TRACK_DUTY;
    float correction = config::K_TRACK_PER_DEG * view.bearing_deg;
    if (attack) {
        base = contact ? config::ATTACK_DUTY : config::ATTACK_APPROACH_DUTY;
        const float limit = std::min(config::TURN_MIN_DUTY, base);
        correction = std::clamp(correction, -limit, limit);
        result.profile = governor::Profile::ATTACK;
    } else if (std::fabs(view.bearing_deg) == 15.0F) {
        // These two discrete B5 rows receive the specifically approved pivot.
        correction += std::copysign(config::TURN_MIN_DUTY, view.bearing_deg);
    }
    result.duty_l = std::clamp(base + correction, -1.0F, 1.0F);
    result.duty_r = std::clamp(base - correction, -1.0F, 1.0F);
    result.valid = true;
    return result;
}

bool DefendTurn::start(std::uint32_t t_us, float heading_deg, float bearing_deg,
                       bool bearing_valid, bool imu_ok) {
    reset();
    if (!std::isfinite(heading_deg) || !bearing_valid ||
        !std::isfinite(bearing_deg) || bearing_deg <= -180.0F || bearing_deg > 180.0F) {
        finish(Intent::INVALID);
        return false;
    }
    // Reduce yaw before adding the bearing so extreme finite yaw keeps offsets.
    const float heading = normalizedHeading(heading_deg);
    const float target = normalizedHeading(heading + bearing_deg);
    if (!turn_.start(t_us, heading, target, config::TURN_DUTY, imu_ok)) {
        finish(Intent::INVALID);
        return false;
    }
    interval_.begin(t_us);
    active_ = true;
    return true;
}

DefendResult DefendTurn::finish(Intent intent) {
    active_ = false;
    intent_ = intent;
    DefendResult result;
    result.intent = intent;
    result.motion.status = intent == Intent::INVALID ? motion::Status::INVALID :
        intent == Intent::NONE ? motion::Status::IDLE : motion::Status::DONE;
    return result;
}

DefendResult DefendTurn::step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                             std::uint8_t confirmed_mask) {
    if (!active_) return finish(intent_);
    const auto mask = static_cast<std::uint8_t>(confirmed_mask & 0x7FU);
    if ((mask & 0x07U) != 0U) return finish(Intent::PERCEPTION);
    if (mask == 0U) return finish(Intent::SEARCH);
    interval_.advance(t_us);
    if (interval_.elapsed_us >= config::DEFEND_TIMEOUT_MS * 1000U) {
        DefendResult result = finish(Intent::SEARCH);
        result.defend_timed_out = true;
        return result;
    }
    DefendResult result;
    result.motion = turn_.step(t_us, normalizedHeading(heading_deg), imu_ok);
    if (result.motion.status == motion::Status::INVALID) return finish(Intent::INVALID);
    if (result.motion.status == motion::Status::TIMED_OUT && !turn_timeout_reported_) {
        result.turn_timed_out = true;
        turn_timeout_reported_ = true;
    }
    // B7 terminal zero remains latched while B10 waits for perception or timeout.
    return result;
}

void DefendTurn::reset() { *this = DefendTurn{}; }
} // namespace fsm
