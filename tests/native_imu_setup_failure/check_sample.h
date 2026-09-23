// Compares every public Sample field without depending on object padding.
// Ensures passive evidence and canonical absence preserve the full public value.
// Shared by the actual Acquirer and actual native callback tests for D097.
#pragma once
#include "doctest.h"
#include "hal/imu_acquisition.h"

namespace setup_failure_test {
inline void sameSample(const imu::Sample& a, const imu::Sample& b) {
    CHECK(a.state == b.state); CHECK(a.fault == b.fault);
    CHECK(a.bus_status == b.bus_status); CHECK(a.cleanup == b.cleanup);
    CHECK(a.error_flags == b.error_flags); CHECK(a.sequence == b.sequence);
    CHECK(a.checked_us == b.checked_us);
    CHECK(a.readiness_completed_us == b.readiness_completed_us);
    CHECK(a.motion_started_us == b.motion_started_us);
    CHECK(a.observation_gap_us == b.observation_gap_us);
    CHECK(a.had_previous_observation == b.had_previous_observation);
    CHECK(a.motion.status == b.motion.status);
    CHECK(a.motion.temperature_raw == b.motion.temperature_raw);
    CHECK(a.motion.started_us == b.motion.started_us);
    CHECK(a.motion.completed_us == b.motion.completed_us);
    CHECK(a.motion.interrupt_status == b.motion.interrupt_status);
    CHECK(a.motion.rail_mask == b.motion.rail_mask);
    CHECK(a.motion.coherent == b.motion.coherent);
    for (unsigned i = 0U; i < 3U; ++i) {
        CHECK(a.motion.accel_raw[i] == b.motion.accel_raw[i]);
        CHECK(a.motion.gyro_raw[i] == b.motion.gyro_raw[i]);
        CHECK(a.motion.accel_g[i] == b.motion.accel_g[i]);
        CHECK(a.motion.gyro_dps[i] == b.motion.gyro_dps[i]);
    }
}
} // namespace setup_failure_test
