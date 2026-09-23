// Scripts runtime acquisition replies independently of the native bus implementation.
// Reuses the D080 setup substitute while preserving its existing behavior.
// D081 actual Acquirer tests control every time, phase and status field explicitly.
#pragma once
#include "imu_bus_fake.h"

namespace imu_acq_fake {
struct Script {
    imu::BusAcquisition reply{};
    unsigned calls = 0U;
};
extern Script script;
void reset();
void seedSetup();
std::uint32_t setupTime(unsigned index, std::uint32_t start, std::uint32_t last);
imu::BusAcquisition observation(std::uint32_t start, std::uint32_t duration = 100U);
imu::BusAcquisition noNew(std::uint32_t start, std::uint32_t duration = 20U);
} // namespace imu_acq_fake
