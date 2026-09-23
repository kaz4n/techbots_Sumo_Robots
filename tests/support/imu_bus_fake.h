// Scripts the concrete MPU6050 Bus boundary for D080 setup tests.
// Keeps the independent register recipe and caller clock outside production code.
// Actual Setup and decoder link against these methods in host tests only.
#pragma once
#include "hal/imu_bus_unoq.h"
#include <cstddef>
#include <cstdint>

namespace imu_fake {
enum class Kind : std::uint8_t { BEGIN, READ, WRITE, MOTION };
struct Request {
    Kind kind = Kind::BEGIN;
    imu::Register reg = imu::Register::IDENTITY;
    std::uint8_t value = 0U;
};
struct Reply {
    imu::BusInit init{imu::BusStatus::OK, imu::BusCleanup::NOT_ATTEMPTED, true};
    imu::BusTransfer transfer{};
    std::uint32_t start_offset_us = 7U;
    std::uint32_t duration_us = 31U;
};
inline constexpr std::size_t CAPACITY = 64U;
struct Script {
    Reply replies[CAPACITY]{};
    Request calls[CAPACITY]{};
    std::uint32_t call_us[CAPACITY]{};
    std::uint32_t completed_us[CAPACITY]{};
    std::size_t count = 0U;
    std::uint32_t now_us = 0U;
    bool overflow = false;
};
extern Script script;
void reset();
} // namespace imu_fake
