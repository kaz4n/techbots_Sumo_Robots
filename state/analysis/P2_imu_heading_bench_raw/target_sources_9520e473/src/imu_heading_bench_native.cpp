// Forwards finite heading-bench operations to one existing native IMU Acquirer.
// Keeps construction passive and preserves the owner's setup, pending and cleanup evidence.
// Independent counted binding tests and checked target startup inspection cover this seam.
#include "imu_heading_bench_native.h"
#include <Arduino.h>

namespace imu_heading_bench {
Port Native::port() {
    return {this, &clockUs, &startSetup, &advanceSetup, &beginRead, &advanceRead, &cancelRead};
}
std::uint32_t Native::clockUs(void*) { return static_cast<std::uint32_t>(micros()); }
imu::SetupReport Native::startSetup(void* context, std::uint32_t now_us, bool power) {
    return static_cast<Native*>(context)->acquirer_.start(now_us, power);
}
imu::SetupReport Native::advanceSetup(void* context, std::uint32_t now_us) {
    return static_cast<Native*>(context)->acquirer_.advanceSetup(now_us);
}
imu::SampleProgress Native::beginRead(void* context, std::uint32_t now_us) {
    return static_cast<Native*>(context)->acquirer_.beginRead(now_us);
}
imu::SampleProgress Native::advanceRead(void* context, std::uint32_t now_us) {
    return static_cast<Native*>(context)->acquirer_.advanceRead(now_us);
}
imu::SampleProgress Native::cancelRead(void* context, std::uint32_t now_us) {
    return static_cast<Native*>(context)->acquirer_.cancelRead(now_us);
}
} // namespace imu_heading_bench
