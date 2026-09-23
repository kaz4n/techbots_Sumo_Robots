// Owns checked MPU6050 setup and publishes only qualified new observations.
// Separates no-new data and terminal silence/transport faults from cached samples.
// Independent native and scripted-bus tests plus an inert probe test this boundary.
#pragma once
#include "imu.h"
#include <cstdint>

namespace imu {
enum class SampleState : std::uint8_t { NOT_READY, NO_NEW, OBSERVATION, FAULT };
enum class SampleFault : std::uint8_t {
    NONE, SETUP, INVALID_CONFIG, TIME_ORDER, TRANSPORT, RESPONSE, SILENCE
};
struct Sample {
    SampleState state = SampleState::NOT_READY;
    SampleFault fault = SampleFault::NONE;
    CoherentMotion motion{}; // Empty unless state==OBSERVATION; no cached publication.
    BusStatus bus_status = BusStatus::NOT_INITIALIZED;
    BusCleanup cleanup = BusCleanup::NOT_ATTEMPTED;
    std::uint32_t error_flags = 0U;
    std::uint32_t sequence = 0U; // Accepted observations modulo2^32, not sensor generations.
    std::uint32_t checked_us = 0U;
    std::uint32_t readiness_completed_us = 0U;
    std::uint32_t motion_started_us = 0U;
    std::uint32_t observation_gap_us = 0U; // Prior accepted completion to this completion.
    bool had_previous_observation = false;
};
class Acquirer {
public:
    Acquirer() = default;
    Acquirer(const Acquirer&) = delete;
    Acquirer& operator=(const Acquirer&) = delete;
    SetupReport start(std::uint32_t now_us, bool power_confirmed);
    SetupReport advanceSetup(std::uint32_t now_us);
    SetupReport setupReport() const { return setup_.report(); }
    // Caller time shares Bus micros() domain. No I/O before PROFILE_READY or after fault.
    // NO_NEW advances no sample sequence, calibration value or yaw integration.
    Sample read(std::uint32_t now_us);
private:
    Sample fail(SampleFault fault, std::uint32_t observed_us);
    bool acceptTime(std::uint32_t now_us);
    bool acceptAcquisition(const BusAcquisition& acquisition, std::uint32_t call_us);
    Bus bus_{};
    Setup setup_{bus_};
    Sample result_{};
    bool armed_ = false;
    bool faulted_ = false;
    bool have_observation_ = false;
    std::uint32_t latest_us_ = 0U;
    std::uint32_t last_observation_us_ = 0U;
    std::uint32_t sequence_ = 0U;
};
} // namespace imu
