// Maps qualified sensor observations and integrates continuous planar yaw.
// Explicit presence, mounting and bounded gaps prevent stale data becoming motion.
// Independent analytic host tests and an inert target probe exercise this source.
#include "imu_heading.h"
#include "../config.h"
#include <cmath>
#include <limits>

namespace imu {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool configValid() {
    return config::IMU_HEADING_MAX_GAP_US > 0U &&
        config::IMU_HEADING_MAX_GAP_US < config::IMU_SILENCE_US &&
        config::IMU_SILENCE_US < HALF_RANGE;
}

bool biasValid(float bias) {
    return std::isfinite(bias) &&
        std::fabs(static_cast<double>(bias)) <= config::IMU_GYRO_RANGE_DPS;
}

bool mountingValid(const Mounting& mounting) {
    int axes[3] = {};
    int sign = 1;
    for (unsigned body = 0U; body < 3U; ++body) {
        const int encoded = mounting.body_axis[body];
        axes[body] = encoded < 0 ? -encoded : encoded;
        if (axes[body] < 1 || axes[body] > 3) return false;
        if (encoded < 0) sign = -sign;
    }
    unsigned inversions = 0U;
    for (unsigned a = 0U; a < 3U; ++a) {
        for (unsigned b = a + 1U; b < 3U; ++b) {
            if (axes[a] == axes[b]) return false;
            if (axes[a] > axes[b]) ++inversions;
        }
    }
    return (inversions % 2U == 0U ? sign : -sign) == 1;
}

unsigned sensorAxis(std::int8_t encoded) {
    const int axis = encoded;
    return static_cast<unsigned>((axis < 0 ? -axis : axis) - 1);
}

float mapped(const float* sensor, std::int8_t encoded) {
    const float value = sensor[sensorAxis(encoded)];
    return encoded < 0 ? -value : value;
}

bool sourceFaultKnown(SampleFault fault) {
    switch (fault) {
    case SampleFault::SETUP: case SampleFault::INVALID_CONFIG: case SampleFault::TIME_ORDER:
    case SampleFault::TRANSPORT: case SampleFault::RESPONSE: case SampleFault::SILENCE: return true;
    case SampleFault::NONE: return false;
    }
    return false;
}

bool payloadValid(const Sample& sample) {
    const auto& motion = sample.motion;
    const auto duration = motion.completed_us - motion.started_us;
    if (!motion.coherent || motion.status != DecodeStatus::OK ||
        motion.completed_us != sample.checked_us || duration >= HALF_RANGE ||
        duration >= config::IMU_I2C_TRANSFER_US || (motion.interrupt_status & 0xFEU) != 0U ||
        (motion.rail_mask & 0x80U) != 0U) return false;
    for (unsigned axis = 0U; axis < 3U; ++axis) {
        if (!std::isfinite(motion.gyro_dps[axis]) || !std::isfinite(motion.accel_g[axis]) ||
            std::fabs(static_cast<double>(motion.gyro_dps[axis])) > config::IMU_GYRO_RANGE_DPS ||
            std::fabs(static_cast<double>(motion.accel_g[axis])) > config::IMU_ACCEL_RANGE_G) return false;
    }
    return true;
}

bool floatRepresentable(double value) {
    return std::isfinite(value) &&
        std::fabs(value) <= static_cast<double>(std::numeric_limits<float>::max());
}
} // namespace

void Estimator::clear(HeadingState state) {
    result_ = Estimate{};
    result_.state = state;
    result_.bias_dps = bias_dps_;
    result_.sequence = sequence_;
    result_.checked_us = latest_us_;
}

Estimate Estimator::fail(HeadingFault fault, SampleFault source) {
    clear(HeadingState::FAULT);
    result_.fault = fault;
    result_.acquisition_fault = source;
    result_.gyro_observation = Presence::INVALID;
    result_.accel_observation = Presence::INVALID;
    return result_;
}

bool Estimator::begin(const Mounting& mounting, float initial_bias_dps) {
    if (attempted_) return result_.state != HeadingState::FAULT;
    attempted_ = true;
    if (!configValid()) { fail(HeadingFault::INVALID_CONFIG); return false; }
    if (!mounting.confirmed) { fail(HeadingFault::MOUNTING_UNCONFIRMED); return false; }
    if (!mountingValid(mounting)) { fail(HeadingFault::MOUNTING_INVALID); return false; }
    if (!biasValid(initial_bias_dps)) { fail(HeadingFault::BIAS); return false; }
    mounting_ = mounting;
    bias_dps_ = initial_bias_dps;
    clear(HeadingState::WAITING);
    return true;
}

bool Estimator::acceptTime(std::uint32_t now_us) {
    if (have_time_ && now_us - latest_us_ >= HALF_RANGE) {
        fail(HeadingFault::TIME_ORDER);
        return false;
    }
    latest_us_ = now_us;
    have_time_ = true;
    result_.checked_us = now_us;
    if (have_observation_ && now_us - observation_us_ > config::IMU_HEADING_MAX_GAP_US) {
        fail(HeadingFault::GAP);
        return false;
    }
    return true;
}

bool Estimator::validateObservation(const Sample& sample) {
    const auto gap = have_observation_ ? latest_us_ - observation_us_ : 0U;
    if (sample.sequence != sequence_ + 1U ||
        sample.had_previous_observation != have_observation_ || sample.observation_gap_us != gap) {
        fail(HeadingFault::SEQUENCE);
        return false;
    }
    if (have_observation_ && gap == 0U) { fail(HeadingFault::TIME_ORDER); return false; }
    if (!payloadValid(sample)) { fail(HeadingFault::INPUT); return false; }
    const auto yaw_rail = 1U << (4U + sensorAxis(mounting_.body_axis[2]));
    if ((sample.motion.rail_mask & yaw_rail) != 0U) {
        fail(HeadingFault::SATURATION);
        return false;
    }
    return true;
}

Estimate Estimator::publish(const Sample& sample) {
    const float raw = mapped(sample.motion.gyro_dps, mounting_.body_axis[2]);
    const double corrected = static_cast<double>(raw) - bias_dps_;
    const auto gap = have_observation_ ? latest_us_ - observation_us_ : 0U;
    const double increment = have_observation_ ?
        (0.5 * (static_cast<double>(previous_raw_dps_) + raw) - bias_dps_) * gap / 1000000.0 : 0.0;
    const double yaw = have_observation_ ? yaw_deg_ + increment : 0.0;
    if (!std::isfinite(increment) || !floatRepresentable(yaw) || !floatRepresentable(corrected))
        return fail(HeadingFault::NUMERIC);
    result_.state = HeadingState::READY;
    result_.gyro_observation = Presence::VALID;
    result_.heading_available = true;
    result_.heading_updated = true;
    result_.heading_deg = static_cast<float>(yaw);
    result_.raw_gyro_z_dps = raw;
    result_.gyro_z_dps = static_cast<float>(corrected);
    const auto horizontal_rails = (1U << sensorAxis(mounting_.body_axis[0])) |
                                  (1U << sensorAxis(mounting_.body_axis[1]));
    result_.accel_observation = (sample.motion.rail_mask & horizontal_rails) != 0U ?
        Presence::INVALID : Presence::VALID;
    if (result_.accel_observation == Presence::VALID) {
        result_.ax_g = mapped(sample.motion.accel_g, mounting_.body_axis[0]);
        result_.ay_g = mapped(sample.motion.accel_g, mounting_.body_axis[1]);
    }
    sequence_ = sample.sequence;
    observation_us_ = latest_us_;
    yaw_deg_ = yaw;
    previous_raw_dps_ = raw;
    have_observation_ = true;
    result_.sequence = sequence_;
    result_.observation_us = observation_us_;
    return result_;
}

Estimate Estimator::observe(const Sample& sample) {
    if (!attempted_ || result_.state == HeadingState::FAULT) return result_;
    clear(HeadingState::WAITING);
    if (sample.state == SampleState::NOT_READY)
        return profile_seen_ ? fail(HeadingFault::INPUT) : result_;
    if (sample.state == SampleState::FAULT)
        return sourceFaultKnown(sample.fault) ? fail(HeadingFault::SOURCE, sample.fault) :
            fail(HeadingFault::INPUT);
    if (sample.state != SampleState::NO_NEW && sample.state != SampleState::OBSERVATION)
        return fail(HeadingFault::INPUT);
    if (sample.fault != SampleFault::NONE || sample.bus_status != BusStatus::OK ||
        sample.cleanup != BusCleanup::NOT_ATTEMPTED || sample.error_flags != 0U)
        return fail(HeadingFault::INPUT);
    profile_seen_ = true;
    if (!acceptTime(sample.checked_us)) return result_;
    if (sample.state == SampleState::NO_NEW) {
        if (sample.sequence != sequence_) return fail(HeadingFault::SEQUENCE);
        if (sample.motion.coherent || sample.had_previous_observation || sample.observation_gap_us != 0U)
            return fail(HeadingFault::INPUT);
        if (have_observation_) {
            result_.state = HeadingState::READY;
            result_.heading_deg = static_cast<float>(yaw_deg_);
            result_.observation_us = observation_us_;
            result_.heading_age_us = latest_us_ - observation_us_;
            result_.heading_available = true;
        }
        return result_;
    }
    if (!validateObservation(sample)) return result_;
    return publish(sample);
}

bool Estimator::applyBias(float accepted_bias_dps) {
    if (!attempted_ || result_.state == HeadingState::FAULT) return false;
    if (!biasValid(accepted_bias_dps)) { fail(HeadingFault::BIAS); return false; }
    bias_dps_ = accepted_bias_dps;
    result_.bias_dps = bias_dps_;
    return true;
}
} // namespace imu
