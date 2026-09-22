// Declares the never-invoked MPU6050 compile compatibility probe.
// Exposes exact API types and inert address anchors for D-066 evidence.
// Tested by contract-derived host substitutes and exact target ELF inspection.
#pragma once

#include <Adafruit_MPU6050.h>
#include <Wire.h>
#include <stdint.h>

namespace p0 {

using ApiProbe = bool (*)(TwoWire&, uint8_t, mpu6050_gyro_range_t, uint8_t,
                         mpu6050_bandwidth_t, sensors_event_t&, sensors_event_t&,
                         sensors_event_t&);

bool probeMpu(TwoWire& wire, uint8_t address, mpu6050_gyro_range_t range,
              uint8_t divisor, mpu6050_bandwidth_t bandwidth,
              sensors_event_t& accel, sensors_event_t& gyro,
              sensors_event_t& temperature);

}  // namespace p0

extern p0::ApiProbe volatile p0ImuProbe;
extern TwoWire* volatile p0ImuBus;
