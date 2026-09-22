// Retains PWM and interrupt API probes without invoking any peripheral API.
// Keeps P0 compile compatibility separate from hardware or motor qualification.
// Checked by independent host substitutes and exact target ELF review.
#include "src/config.h"
#include "src/api_probe.h"

static_assert(MOTORS_ALLOWED == 0, "This P0 compile probe must remain inert");

p0::PwmProbe volatile p0PwmProbe = nullptr;
p0::AnalogProbe volatile p0AnalogProbe = nullptr;
p0::InterruptProbe volatile p0InterruptProbe = nullptr;

void setup() {
    p0PwmProbe = &p0::probePwm;
    p0AnalogProbe = &p0::probeAnalog;
    p0InterruptProbe = &p0::probeInterrupt;
}

void loop() {
}
