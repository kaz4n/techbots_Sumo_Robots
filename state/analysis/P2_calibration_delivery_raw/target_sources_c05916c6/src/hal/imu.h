// Checks MPU6050 setup and decodes coherent motion in sensor coordinates.
// Keeps configured transport data separate from freshness, bias and robot yaw.
// Independent scripted-bus host tests and an inert target probe test this layer.
#pragma once
#include "imu_bus_unoq.h"
#include <cstdint>

namespace imu {
enum class SetupState : std::uint8_t { NOT_STARTED, IN_PROGRESS, PROFILE_READY, FAULT };
enum class SetupFault : std::uint8_t {
    NONE, POWER_UNCONFIRMED, INVALID_CONFIG, TIME_ORDER, DEADLINE,
    ADVANCE_LIMIT, REQUEST_LIMIT, TRANSPORT, RESPONSE, IDENTITY, READBACK, STATUS
};
struct SetupReport {
    SetupState state = SetupState::NOT_STARTED;
    SetupFault fault = SetupFault::NONE;
    BusStatus bus_status = BusStatus::NOT_INITIALIZED;
    BusCleanup cleanup = BusCleanup::NOT_ATTEMPTED;
    std::uint32_t error_flags = 0U;
    std::uint32_t started_us = 0U;
    std::uint32_t observed_us = 0U;
    std::uint32_t advances = 0U;
    std::uint32_t requests = 0U;
};
class Setup {
public:
    explicit Setup(Bus& bus) : bus_(bus) {}
    Setup(const Setup&) = delete;
    Setup& operator=(const Setup&) = delete;
    // Arms once with a caller-established power-valid observation; performs no I/O.
    // Repeated start preserves the first lifecycle, including any terminal fault.
    SetupReport start(std::uint32_t now_us, bool power_confirmed);
    // At most one bounded Bus operation per call; all waits return immediately.
    // Caller time shares the Bus micros() domain, in forward half-range order.
    SetupReport advance(std::uint32_t now_us);
    SetupReport report() const { return report_; }
private:
    SetupReport fail(SetupFault fault);
    bool acceptTime(std::uint32_t now_us);
    bool acceptTransfer(const BusTransfer& transfer, std::uint8_t count,
                        std::uint32_t call_us);
    Bus& bus_;
    SetupReport report_{};
    std::uint32_t wait_started_us_ = 0U;
    std::uint8_t step_ = 0U;
};

enum class DecodeStatus : std::uint8_t { OK, INVALID_CONFIG, TRANSPORT, RESPONSE, STATUS };
struct CoherentMotion {
    DecodeStatus status = DecodeStatus::RESPONSE;
    std::int32_t accel_raw[3] = {};
    std::int32_t gyro_raw[3] = {};
    std::int32_t temperature_raw = 0;
    float accel_g[3] = {};
    float gyro_dps[3] = {};
    std::uint32_t started_us = 0U;
    std::uint32_t completed_us = 0U;
    std::uint8_t interrupt_status = 0U;
    std::uint8_t rail_mask = 0U; // bits0..2 accel,3 temperature,4..6 gyro.
    bool coherent = false;
};
// Pure fixed-profile byte decode. No new-generation, sensor-health or robot-axis
// claim: callers must qualify those separately. Failure zeros all payload fields.
CoherentMotion decodeMotion(const BusTransfer& transfer);
} // namespace imu
