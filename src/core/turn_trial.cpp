// Implements one finite P3 turn trial with the unchanged B7 Turn controller.
// Reflects left-trial coordinates and preserves observed braking without motor authority.
// Independent host tests cover exact angles, safety cancellation, time and IMU faults.
#include "turn_trial.h"
#include "../config.h"
#include <cmath>

namespace turn_trial {
namespace {
constexpr std::uint32_t CLOCK_HALF_RANGE_US = 0x80000000U;
constexpr std::uint64_t BRAKE_DURATION_US =
    static_cast<std::uint64_t>(config::TURN_TRIAL_BRAKE_MS) * 1000U;
static_assert(BRAKE_DURATION_US > 0U && BRAKE_DURATION_US < CLOCK_HALF_RANGE_US,
              "Observed brake interval must fit below clock half range");
static_assert(config::TURN_DUTY >= config::TURN_MIN_DUTY && config::TURN_DUTY <= 1.0F,
              "Turn trial must use a valid existing Turn duty");

bool acceptedAngle(float angle_deg) {
    return angle_deg == -180.0F || angle_deg == -90.0F ||
           angle_deg == 90.0F || angle_deg == 180.0F;
}
} // namespace

bool Trial::start(std::uint32_t t_us, float heading_deg, float signed_angle_deg,
                  bool imu_ok) {
    if (attempted_) return false;
    attempted_ = true;
    report_.fresh = true;
    if (!std::isfinite(heading_deg) || !acceptedAngle(signed_angle_deg)) {
        terminate(Phase::FAULT, Reason::INVALID_START, t_us);
        return false;
    }

    left_ = signed_angle_deg < 0.0F;
    const float reflected_heading = left_ ? -heading_deg : heading_deg;
    if (!turn_.startRelative(t_us, reflected_heading, std::abs(signed_angle_deg),
                             config::TURN_DUTY, imu_ok)) {
        terminate(Phase::FAULT, Reason::INVALID_START, t_us);
        return false;
    }
    last_us_ = t_us;
    report_.started_us = t_us;
    report_.signed_angle_deg = signed_angle_deg;
    report_.phase = Phase::TURN;
    report_.phase_changed = true;
    advanceTurn({t_us, heading_deg, imu_ok, false, false});
    return true;
}

bool Trial::active() const {
    return report_.phase == Phase::TURN || report_.phase == Phase::BRAKE;
}

void Trial::terminate(Phase phase, Reason reason, std::uint32_t time) {
    report_.phase = phase;
    report_.reason = reason;
    report_.duty_l = 0.0F;
    report_.duty_r = 0.0F;
    report_.finished = true;
    report_.finished_us = time;
    report_.phase_changed = true;
}

void Trial::advanceTurn(const Sample& sample) {
    const float reflected_heading = left_ ? -sample.heading_deg : sample.heading_deg;
    const motion::Result result = turn_.step(sample.t_us, reflected_heading, sample.imu_ok);
    report_.turn_status = result.status;
    report_.imu_fallback = result.imu_fallback;
    report_.duty_l = left_ ? result.duty_r : result.duty_l;
    report_.duty_r = left_ ? result.duty_l : result.duty_r;
    if (result.status == motion::Status::INVALID) {
        terminate(Phase::FAULT, Reason::INVALID_HEADING, sample.t_us);
    } else if (result.status == motion::Status::DONE ||
               result.status == motion::Status::TIMED_OUT) {
        // Completion is observed now; a delayed call cannot spend the brake interval.
        report_.phase = Phase::BRAKE;
        report_.turn_finished = true;
        report_.turn_finished_us = sample.t_us;
        report_.phase_changed = true;
    }
}

Report Trial::step(const Sample& sample) {
    report_.fresh = false;
    report_.phase_changed = false;
    if (!active() || sample.t_us == last_us_) return report_;

    const std::uint32_t delta_us = sample.t_us - last_us_;
    last_us_ = sample.t_us;
    report_.fresh = true;
    if (delta_us >= CLOCK_HALF_RANGE_US) {
        terminate(Phase::FAULT, Reason::CLOCK_ORDER, sample.t_us);
    } else if (sample.stop_requested) {
        terminate(Phase::INTERRUPTED, Reason::STOP, sample.t_us);
    } else if (sample.edge_required) {
        terminate(Phase::INTERRUPTED, Reason::EDGE, sample.t_us);
    } else if (report_.phase == Phase::TURN) {
        advanceTurn(sample);
    } else if (sample.t_us - report_.turn_finished_us >= BRAKE_DURATION_US) {
        terminate(Phase::COMPLETE, Reason::NONE, sample.t_us);
    }
    return report_;
}
} // namespace turn_trial
