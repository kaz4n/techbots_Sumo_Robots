// Declares never-invoked installed PWM and interrupt compatibility probes.
// Separates header/link evidence from pin operation and runtime safety.
// Tested by independent D-067 host substitutes and exact target ELF inspection.
#pragma once

#include <Arduino.h>
#include <zephyrPinctrl.h>
#include <zephyr/drivers/pwm.h>
#include <stddef.h>
#include <stdint.h>

namespace p0 {

using PwmProbe = int (*)(const pwm_dt_spec*, size_t, uint32_t, uint32_t, uint64_t*);
using AnalogProbe = int (*)(pin_size_t, int, int);
using InterruptProbe = int (*)(pin_size_t, void (*)(), PinStatus);

int probePwm(const pwm_dt_spec* spec, size_t state_pin_index, uint32_t period_ns,
             uint32_t pulse_ns, uint64_t* cycles_per_sec);
int probeAnalog(pin_size_t pin, int value, int resolution_bits);
int probeInterrupt(pin_size_t pin, void (*callback)(), PinStatus mode);

}  // namespace p0

extern p0::PwmProbe volatile p0PwmProbe;
extern p0::AnalogProbe volatile p0AnalogProbe;
extern p0::InterruptProbe volatile p0InterruptProbe;
