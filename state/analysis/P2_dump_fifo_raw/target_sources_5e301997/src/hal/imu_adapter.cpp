// Maps checked estimator reports into D084 Robot evidence without acquisition.
// Preserves source identity and keeps absence distinct from measured zero.
// Independent adapter and complete estimator-to-Robot streams test this boundary.
#include "imu_adapter.h"
#include <cmath>

namespace imu {
namespace {
bool bounded(float value, float limit) {
    return std::isfinite(value) && std::fabs(value) <= limit;
}
bool zeroSensors(const Estimate& report) {
    return report.raw_gyro_z_dps == 0.0F && report.gyro_z_dps == 0.0F &&
           report.ax_g == 0.0F && report.ay_g == 0.0F;
}
bool zeroHeading(const Estimate& report) {
    return !report.heading_available && !report.heading_updated &&
        report.heading_deg == 0.0F && report.observation_us == 0U &&
        report.heading_age_us == 0U && zeroSensors(report);
}
bool empty(const Estimate& report) {
    return zeroHeading(report) && report.fault == HeadingFault::NONE &&
        report.acquisition_fault == SampleFault::NONE &&
        report.gyro_observation == Presence::ABSENT &&
        report.accel_observation == Presence::ABSENT && report.sequence == 0U;
}
bool ready(const Estimate& report) {
    if (report.fault != HeadingFault::NONE || report.acquisition_fault != SampleFault::NONE ||
        !report.heading_available || !std::isfinite(report.heading_deg) ||
        report.checked_us - report.observation_us != report.heading_age_us ||
        report.heading_age_us > config::IMU_HEADING_MAX_GAP_US) return false;
    if (!report.heading_updated)
        return report.gyro_observation == Presence::ABSENT &&
            report.accel_observation == Presence::ABSENT && zeroSensors(report);
    if (report.heading_age_us != 0U || report.gyro_observation != Presence::VALID ||
        !bounded(report.raw_gyro_z_dps, config::IMU_GYRO_RANGE_DPS) ||
        !bounded(report.gyro_z_dps, 2.0F * config::IMU_GYRO_RANGE_DPS)) return false;
    if (report.accel_observation == Presence::VALID)
        return bounded(report.ax_g, config::IMU_ACCEL_RANGE_G) &&
               bounded(report.ay_g, config::IMU_ACCEL_RANGE_G);
    return report.accel_observation == Presence::INVALID &&
           report.ax_g == 0.0F && report.ay_g == 0.0F;
}
bool valid(const Estimate& report) {
    if (!bounded(report.bias_dps, config::IMU_GYRO_RANGE_DPS)) return false;
    switch (report.state) {
    case HeadingState::NOT_STARTED:
        return empty(report) && report.checked_us == 0U && report.bias_dps == 0.0F;
    case HeadingState::WAITING: return empty(report);
    case HeadingState::READY: return ready(report);
    case HeadingState::FAULT:
        return report.fault > HeadingFault::NONE && report.fault <= HeadingFault::NUMERIC &&
            report.gyro_observation == Presence::INVALID &&
            report.accel_observation == Presence::INVALID && zeroHeading(report) &&
            (report.fault == HeadingFault::SOURCE ?
                (report.acquisition_fault > SampleFault::NONE &&
                 report.acquisition_fault <= SampleFault::SILENCE) :
                report.acquisition_fault == SampleFault::NONE);
    }
    return false;
}
core::ImuPresence presence(Presence value) {
    switch (value) {
    case Presence::ABSENT: return core::ImuPresence::ABSENT;
    case Presence::VALID: return core::ImuPresence::VALID;
    case Presence::INVALID: return core::ImuPresence::INVALID;
    }
    return core::ImuPresence::INVALID;
}
} // namespace

bool applyEstimate(fsm::RobotInput& input, const Estimate& report) {
    input.imu = {};
    input.imu.explicit_values = true;
    input.imu.contract_valid = valid(report);
    input.imu_ok = false;
    input.raw_heading_deg = input.raw_gyro_z_dps = input.ax_g = input.ay_g = 0.0F;
    input.previous_bias_dps = 0.0F;
    if (!input.imu.contract_valid) {
        input.imu.gyro = input.imu.accel = core::ImuPresence::INVALID;
        return false;
    }
    input.imu.gyro = presence(report.gyro_observation);
    input.imu.accel = presence(report.accel_observation);
    input.imu.heading_available = report.heading_available;
    input.imu.heading_updated = report.heading_updated;
    input.imu.checked_us = report.checked_us;
    input.imu.observation_us = report.observation_us;
    input.imu.sequence = report.sequence;
    input.imu_ok = report.heading_available;
    input.raw_heading_deg = report.heading_deg;
    input.raw_gyro_z_dps = report.raw_gyro_z_dps;
    input.ax_g = report.ax_g;
    input.ay_g = report.ay_g;
    input.previous_bias_dps = report.bias_dps;
    return true;
}
} // namespace imu
