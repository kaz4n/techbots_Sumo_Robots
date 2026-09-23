// Maps qualified MPU observations and integrates continuous planar yaw.
// Separates fresh gyro/acceleration evidence from retained bounded-age heading.
// Independent analytic host tests and an inert target probe validate this layer.
#pragma once
#include "imu_acquisition.h"
#include <cstdint>

namespace imu {
struct Mounting {
    // Body X forward, Y right, Z down. +/-1,2,3 select signed sensor X,Y,Z.
    // A proper signed permutation is required; zeros are explicitly unconfigured.
    std::int8_t body_axis[3] = {};
    bool confirmed = false; // Caller evidence, never established by this class.
};
enum class Presence : std::uint8_t { ABSENT, VALID, INVALID };
enum class HeadingState : std::uint8_t { NOT_STARTED, WAITING, READY, FAULT };
enum class HeadingFault : std::uint8_t {
    NONE, INVALID_CONFIG, MOUNTING_UNCONFIRMED, MOUNTING_INVALID, BIAS,
    SOURCE, INPUT, TIME_ORDER, SEQUENCE, GAP, SATURATION, NUMERIC
};
struct Estimate {
    HeadingState state = HeadingState::NOT_STARTED;
    HeadingFault fault = HeadingFault::NONE;
    SampleFault acquisition_fault = SampleFault::NONE;
    Presence gyro_observation = Presence::ABSENT;
    Presence accel_observation = Presence::ABSENT;
    bool heading_available = false;
    bool heading_updated = false;
    float heading_deg = 0.0F; // Unwrapped; zero at first accepted observation only.
    float raw_gyro_z_dps = 0.0F; // Body coordinates, before bias; fresh only.
    float gyro_z_dps = 0.0F; // After bias; fresh only.
    float ax_g = 0.0F;
    float ay_g = 0.0F;
    float bias_dps = 0.0F; // Configuration state, not a sensor observation.
    std::uint32_t checked_us = 0U;
    std::uint32_t observation_us = 0U; // Retained time does not refresh on NO_NEW.
    std::uint32_t sequence = 0U;
    std::uint32_t heading_age_us = 0U;
};
class Estimator {
public:
    Estimator() = default;
    Estimator(const Estimator&) = delete;
    Estimator& operator=(const Estimator&) = delete;
    // One-shot configuration. No default physical map, I/O, clock or GO reset.
    bool begin(const Mounting& mounting, float initial_bias_dps);
    // Consume each Acquirer result once, from its first accepted observation.
    // NO_NEW never integrates or publishes cached gyro/acceleration as fresh.
    Estimate observe(const Sample& sample);
    // Valid updates affect the next increment; existing yaw never jumps.
    bool applyBias(float accepted_bias_dps);
    Estimate report() const { return result_; } // Snapshot, not another observation.
private:
    Estimate fail(HeadingFault fault, SampleFault source = SampleFault::NONE);
    void clear(HeadingState state);
    bool acceptTime(std::uint32_t now_us);
    bool validateObservation(const Sample& sample);
    Estimate publish(const Sample& sample);
    Mounting mounting_{};
    Estimate result_{};
    bool attempted_ = false;
    bool profile_seen_ = false;
    bool have_time_ = false;
    bool have_observation_ = false;
    std::uint32_t latest_us_ = 0U;
    std::uint32_t observation_us_ = 0U;
    std::uint32_t sequence_ = 0U;
    double yaw_deg_ = 0.0;
    float previous_raw_dps_ = 0.0F;
    float bias_dps_ = 0.0F;
};
} // namespace imu
