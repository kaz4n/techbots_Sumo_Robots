// Implements B7 motion demands with the D-022/D-023 approved control rules.
// Bounds each primitive independently of future state arbitration and motor writes.
// Independent host tests check exact timing, IMU loss, mirroring and finite duties.
#include "motion.h"
#include "../config.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace motion {
namespace {
static_assert(config::TURN_MIN_DUTY >= 0.0F && config::TURN_MIN_DUTY <= 1.0F);
static_assert(config::K_TURN_PER_DEG > 0.0F && config::TURN_MS_PER_DEG > 0.0F);
static_assert(config::TURN_TIMEOUT_MS <=
              std::numeric_limits<std::uint32_t>::max() / 1000U);

bool validDuration(std::uint32_t duration_ms) {
    return duration_ms <= std::numeric_limits<std::uint32_t>::max() / 1000U;
}

double headingError(double target_deg, double current_deg) {
    // Keep relative coordinates and finite float inputs widened through the error.
    double error = std::fmod(target_deg - current_deg, 360.0);
    if (error <= -180.0) error += 360.0;
    if (error > 180.0) error -= 360.0;
    return error;
}

float boundedDuty(double duty) {
    return static_cast<float>(std::clamp(duty, -1.0, 1.0));
}
} // namespace

void Interval::begin(std::uint32_t t_us) {
    last_us = t_us;
    elapsed_us = 0;
}

void Interval::advance(std::uint32_t t_us) {
    elapsed_us += static_cast<std::uint32_t>(t_us - last_us);
    last_us = t_us;
}

bool Turn::start(std::uint32_t t_us, float heading_deg, float target_heading_deg,
                 float max_duty, bool imu_ok) {
    reset();
    if (!std::isfinite(heading_deg) || !std::isfinite(target_heading_deg) ||
        !std::isfinite(max_duty) || max_duty < config::TURN_MIN_DUTY || max_duty > 1.0F) {
        status_ = Status::INVALID;
        return false;
    }
    interval_.begin(t_us);
    target_heading_deg_ = target_heading_deg;
    error_deg_ = headingError(target_heading_deg, heading_deg);
    max_duty_ = max_duty;
    status_ = Status::ACTIVE;
    if (!imu_ok) beginFallback();
    return true;
}

bool Turn::startRelative(std::uint32_t t_us, float heading_deg, float relative_deg,
                         float max_duty, bool imu_ok) {
    reset();
    if (!std::isfinite(heading_deg) || !std::isfinite(relative_deg) ||
        relative_deg <= -180.0F || relative_deg > 180.0F) {
        status_ = Status::INVALID;
        return false;
    }
    if (!start(t_us, 0.0F, relative_deg, max_duty, imu_ok)) return false;
    origin_heading_deg_ = heading_deg;
    relative_ = true;
    return true;
}

void Turn::beginFallback() {
    fallback_ = true;
    fallback_elapsed_us_ = interval_.elapsed_us;
    fallback_duration_us_ = std::abs(error_deg_) * config::TURN_MS_PER_DEG * 1000.0;
}

Result Turn::step(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, fallback_};
    interval_.advance(t_us);
    if (interval_.elapsed_us >= config::TURN_TIMEOUT_MS * 1000U) {
        status_ = Status::TIMED_OUT;
    } else if (imu_ok && !std::isfinite(heading_deg)) {
        status_ = Status::INVALID;
    } else if (!fallback_ && imu_ok) {
        double observed_heading = heading_deg;
        if (relative_) {
            // Reduce each yaw first so huge finite observations retain their offsets.
            observed_heading = std::fmod(static_cast<double>(heading_deg), 360.0) -
                std::fmod(static_cast<double>(origin_heading_deg_), 360.0);
        }
        error_deg_ = headingError(target_heading_deg_, observed_heading);
        if (std::abs(error_deg_) < config::HEADING_TOL_DEG) status_ = Status::DONE;
    } else if (!fallback_) {
        beginFallback();
    }
    if (status_ == Status::ACTIVE && fallback_ &&
        static_cast<double>(interval_.elapsed_us - fallback_elapsed_us_) >= fallback_duration_us_) {
        status_ = Status::DONE;
    }
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, fallback_};
    const double magnitude = fallback_ ? max_duty_ :
        std::clamp(config::K_TURN_PER_DEG * std::abs(error_deg_),
                   static_cast<double>(config::TURN_MIN_DUTY),
                   static_cast<double>(max_duty_));
    const float duty = static_cast<float>(error_deg_ < 0.0 ? -magnitude : magnitude);
    return {duty, -duty, status_, fallback_};
}

void Turn::reset() { *this = Turn{}; }

bool Straight::start(std::uint32_t t_us, float heading_deg, float duty,
                     std::uint32_t duration_ms) {
    reset();
    if (!std::isfinite(heading_deg) || !std::isfinite(duty) ||
        duty < -1.0F || duty > 1.0F || !validDuration(duration_ms)) {
        status_ = Status::INVALID;
        return false;
    }
    interval_.begin(t_us);
    duration_us_ = duration_ms * 1000U;
    heading_deg_ = heading_deg;
    duty_ = duty;
    status_ = Status::ACTIVE;
    return true;
}

Result Straight::step(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, false};
    interval_.advance(t_us);
    if (interval_.elapsed_us >= duration_us_) {
        status_ = Status::DONE;
    } else if (imu_ok && !std::isfinite(heading_deg)) {
        status_ = Status::INVALID;
    }
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, !imu_ok};
    const double limit = std::min(config::TURN_MIN_DUTY, std::abs(duty_));
    const double correction = imu_ok ? std::clamp(
        config::K_TURN_PER_DEG * headingError(heading_deg_, heading_deg), -limit, limit) : 0.0;
    return {boundedDuty(duty_ + correction), boundedDuty(duty_ - correction), status_, !imu_ok};
}

void Straight::reset() { *this = Straight{}; }

bool Arc::start(std::uint32_t t_us, float heading_deg, Direction direction,
                float inner_ratio, float duty, float sweep_deg, std::uint32_t max_ms) {
    reset();
    if (!std::isfinite(heading_deg) || !std::isfinite(inner_ratio) || !std::isfinite(duty) ||
        !std::isfinite(sweep_deg) || sweep_deg <= 0.0F ||
        inner_ratio < 0.0F || inner_ratio > 1.0F || duty < 0.0F || duty > 1.0F ||
        (direction != Direction::LEFT && direction != Direction::RIGHT) || !validDuration(max_ms)) {
        status_ = Status::INVALID;
        return false;
    }
    interval_.begin(t_us);
    duration_us_ = max_ms * 1000U;
    heading_deg_ = heading_deg;
    sweep_deg_ = sweep_deg;
    duty_ = duty;
    inner_ratio_ = inner_ratio;
    direction_ = direction;
    status_ = Status::ACTIVE;
    return true;
}

Result Arc::step(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, false};
    interval_.advance(t_us);
    if (interval_.elapsed_us >= duration_us_) {
        status_ = Status::TIMED_OUT;
    } else if (imu_ok) {
        if (!std::isfinite(heading_deg)) {
            status_ = Status::INVALID;
        } else {
            const double sign = direction_ == Direction::RIGHT ? 1.0 : -1.0;
            const double swept = sign * (static_cast<double>(heading_deg) - heading_deg_);
            if (swept >= sweep_deg_) status_ = Status::DONE;
        }
    }
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, !imu_ok};
    const float inner = duty_ * inner_ratio_;
    if (direction_ == Direction::LEFT) return {inner, duty_, status_, !imu_ok};
    return {duty_, inner, status_, !imu_ok};
}

void Arc::reset() { *this = Arc{}; }

bool Brake::start(std::uint32_t t_us, std::uint32_t duration_ms) {
    reset();
    if (!validDuration(duration_ms)) {
        status_ = Status::INVALID;
        return false;
    }
    interval_.begin(t_us);
    duration_us_ = duration_ms * 1000U;
    status_ = Status::ACTIVE;
    return true;
}

Result Brake::step(std::uint32_t t_us) {
    if (status_ == Status::ACTIVE) {
        interval_.advance(t_us);
        if (interval_.elapsed_us >= duration_us_) status_ = Status::DONE;
    }
    return {0.0F, 0.0F, status_, false};
}

void Brake::reset() { *this = Brake{}; }

bool TimedArc::start(std::uint32_t t_us, Direction direction, float inner_ratio,
                     float duty, std::uint32_t duration_ms) {
    reset();
    if (!std::isfinite(inner_ratio) || !std::isfinite(duty) ||
        inner_ratio < 0.0F || inner_ratio > 1.0F || duty < 0.0F || duty > 1.0F ||
        (direction != Direction::LEFT && direction != Direction::RIGHT) ||
        !validDuration(duration_ms)) {
        status_ = Status::INVALID;
        return false;
    }
    interval_.begin(t_us);
    duration_us_ = duration_ms * 1000U;
    duty_ = duty;
    inner_ratio_ = inner_ratio;
    direction_ = direction;
    status_ = duration_us_ == 0U ? Status::DONE : Status::ACTIVE;
    return true;
}

Result TimedArc::step(std::uint32_t t_us) {
    if (status_ != Status::ACTIVE) return {0.0F, 0.0F, status_, false};
    interval_.advance(t_us);
    if (interval_.elapsed_us >= duration_us_) {
        status_ = Status::DONE;
        return {0.0F, 0.0F, status_, false};
    }
    const float inner = duty_ * inner_ratio_;
    if (direction_ == Direction::LEFT) return {inner, duty_, status_, false};
    return {duty_, inner, status_, false};
}

void TimedArc::reset() { *this = TimedArc{}; }
} // namespace motion
