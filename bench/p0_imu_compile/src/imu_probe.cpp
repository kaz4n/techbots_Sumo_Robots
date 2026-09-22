// Compiles the selected MPU6050 APIs in a retained, never-invoked function.
// Keeps prospective settings as arguments without adopting runtime tunables.
// Verified by target compilation and disassembly; tests must never call it.
#include "imu_probe.h"

namespace p0 {

__attribute__((noinline))
bool probeMpu(TwoWire& wire, uint8_t address, mpu6050_gyro_range_t range,
              uint8_t divisor, mpu6050_bandwidth_t bandwidth,
              sensors_event_t& accel, sensors_event_t& gyro,
              sensors_event_t& temperature) {
    Adafruit_MPU6050 mpu;
    if (!mpu.begin(address, &wire)) {
        return false;
    }
    mpu.setGyroRange(range);
    mpu.setSampleRateDivisor(divisor);
    mpu.setFilterBandwidth(bandwidth);
    return mpu.getEvent(&accel, &gyro, &temperature);
}

}  // namespace p0
