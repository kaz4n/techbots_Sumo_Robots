// Implements the bounded B10 defensive turn and current-target exit requests.
// Keeps its captured B7 command separate from the defensive-state deadline.
// Independent host tests cover capture, target priority, timeout pulses and wrap.
#include "core/fsm.h"
#include "config.h"
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
