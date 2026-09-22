// Retains an MPU6050 API probe and Wire1 binding without invoking either.
// Separates D-066 compile compatibility from runtime or sensor acceptance.
// Verified by independent host substitutes and the final target ELF.
#include "src/config.h"
#include "src/imu_probe.h"

static_assert(MOTORS_ALLOWED == 0, "This P0 compile probe must remain inert");

p0::ApiProbe volatile p0ImuProbe = nullptr;
TwoWire* volatile p0ImuBus = nullptr;

void setup() {
    p0ImuProbe = &p0::probeMpu;
    p0ImuBus = &Wire1;
}

void loop() {
}
