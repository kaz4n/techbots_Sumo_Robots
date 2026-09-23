// Admits D084 explicit IMU evidence once per Robot decision.
// Keeps retained yaw useful without repeating measurements or refreshing their age.
// Independent integration tests cover source identity, wrap, replay and inhibition.
#include "fsm.h"
#include <cmath>
#include <limits>

namespace fsm {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
bool known(core::ImuPresence presence) {
    return presence == core::ImuPresence::ABSENT || presence == core::ImuPresence::VALID ||
           presence == core::ImuPresence::INVALID;
}
bool bounded(float value, float limit) {
    return std::isfinite(value) && std::fabs(value) <= limit;
}
void clearMeasurements(RobotInput& input) {
    input.raw_gyro_z_dps = input.ax_g = input.ay_g = 0.0F;
}
} // namespace

void Robot::prepareImu(RobotInput& input) {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    imu_history_age_us_ = maximum - imu_history_age_us_ < tick_.delta_us ? maximum :
        imu_history_age_us_ + tick_.delta_us;
    if (!imu_mode_chosen_) {
        imu_mode_chosen_ = true;
        explicit_imu_mode_ = input.imu.explicit_values;
    }
    if (!input.imu.contract_valid || input.imu.explicit_values != explicit_imu_mode_ ||
        (explicit_imu_mode_ && !admitImu(input))) {
        faults_ |= HEADING_CONTRACT;
        invalidateImu(input);
    }
}

void Robot::invalidateImu(RobotInput& input) {
    input.imu = {};
    input.imu.explicit_values = true;
    input.imu.contract_valid = false;
    input.imu.gyro = input.imu.accel = core::ImuPresence::INVALID;
    input.imu_ok = false;
    input.raw_heading_deg = 0.0F;
    clearMeasurements(input);
}

bool Robot::admitImu(RobotInput& input) {
    auto& evidence = input.imu;
    if (!evidence.contract_valid || !known(evidence.gyro) || !known(evidence.accel))
        return false;
    if (!evidence.heading_available) {
        if (evidence.heading_updated || evidence.gyro != evidence.accel ||
            evidence.gyro == core::ImuPresence::VALID) return false;
        input.imu_ok = false;
        input.raw_heading_deg = 0.0F;
        clearMeasurements(input);
        evidence.checked_us = evidence.observation_us = evidence.sequence = 0U;
        return true;
    }
    if (!std::isfinite(input.raw_heading_deg) ||
        input.t_us - evidence.checked_us >= HALF_RANGE ||
        evidence.checked_us - evidence.observation_us >= HALF_RANGE ||
        input.t_us - evidence.observation_us > config::IMU_HEADING_MAX_GAP_US ||
        (imu_checked_ && evidence.checked_us - last_imu_checked_us_ >= HALF_RANGE))
        return false;
    if (!admitImuHeading(input)) return false;
    imu_checked_ = true;
    last_imu_checked_us_ = evidence.checked_us;
    input.imu_ok = true;
    return true;
}

bool Robot::admitImuHeading(RobotInput& input) {
    auto& evidence = input.imu;
    if (evidence.heading_updated) {
        if (evidence.gyro != core::ImuPresence::VALID ||
            (evidence.accel != core::ImuPresence::VALID &&
             evidence.accel != core::ImuPresence::INVALID) ||
            evidence.observation_us != evidence.checked_us ||
            !bounded(input.raw_gyro_z_dps, config::IMU_GYRO_RANGE_DPS)) return false;
        if (evidence.accel == core::ImuPresence::VALID) {
            if (!bounded(input.ax_g, config::IMU_ACCEL_RANGE_G) ||
                !bounded(input.ay_g, config::IMU_ACCEL_RANGE_G)) return false;
        } else input.ax_g = input.ay_g = 0.0F;
        if (!imu_history_.valid) { rememberImu(input); return true; }
        const auto source_delta = evidence.observation_us - imu_history_.evidence.observation_us;
        const auto sequence_delta = evidence.sequence - imu_history_.evidence.sequence;
        if (source_delta != 0U && source_delta < HALF_RANGE &&
            sequence_delta != 0U && sequence_delta < HALF_RANGE) {
            rememberImu(input);
            return true;
        }
        if (source_delta != 0U || sequence_delta != 0U || !sameImuPayload(input))
            return false;
        evidence.heading_updated = false;
        evidence.gyro = evidence.accel = core::ImuPresence::ABSENT;
    }
    if (evidence.gyro != core::ImuPresence::ABSENT ||
        evidence.accel != core::ImuPresence::ABSENT || !imu_history_.valid ||
        evidence.observation_us != imu_history_.evidence.observation_us ||
        evidence.sequence != imu_history_.evidence.sequence ||
        input.raw_heading_deg != imu_history_.heading_deg ||
        imu_history_age_us_ > config::IMU_HEADING_MAX_GAP_US) return false;
    clearMeasurements(input);
    return true;
}

bool Robot::sameImuPayload(const RobotInput& input) const {
    return input.raw_heading_deg == imu_history_.heading_deg &&
        input.raw_gyro_z_dps == imu_history_.gyro_dps &&
        input.imu.accel == imu_history_.evidence.accel &&
        (input.imu.accel != core::ImuPresence::VALID ||
         (input.ax_g == imu_history_.ax_g && input.ay_g == imu_history_.ay_g));
}

void Robot::rememberImu(const RobotInput& input) {
    imu_history_ = {input.imu, input.raw_heading_deg, input.raw_gyro_z_dps,
                    input.ax_g, input.ay_g, true};
    imu_history_age_us_ = input.t_us - input.imu.observation_us;
}
} // namespace fsm
