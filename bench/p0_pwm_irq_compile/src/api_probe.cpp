// Compiles installed PWM and interrupt APIs inside never-invoked functions.
// Exposes real linked paths without adopting pins, timings or runtime semantics.
// Checked by target compilation and disassembly; tests never invoke these probes.
#include "api_probe.h"

#include <errno.h>

namespace p0 {

__attribute__((noinline))
int probePwm(const pwm_dt_spec* spec, size_t state_pin_index, uint32_t period_ns,
             uint32_t pulse_ns, uint64_t* cycles_per_sec) {
    if (spec == nullptr || cycles_per_sec == nullptr) {
        return -EINVAL;
    }
    const int initialized = zephyr::arduino::init_dev_apply_channel_pinctrl(
        spec->dev, state_pin_index);
    if (initialized != 0) {
        return initialized;
    }
    if (!pwm_is_ready_dt(spec)) {
        return -ENODEV;
    }
    const int measured = pwm_get_cycles_per_sec(spec->dev, spec->channel,
                                                cycles_per_sec);
    if (measured != 0) {
        return measured;
    }
    return pwm_set_dt(spec, period_ns, pulse_ns);
}

__attribute__((noinline))
int probeAnalog(pin_size_t pin, int value, int resolution_bits) {
    analogWriteResolution(resolution_bits);
    analogWrite(pin, value);
    return analogWriteResolution();
}

__attribute__((noinline))
int probeInterrupt(pin_size_t pin, void (*callback)(), PinStatus mode) {
    const int mapped = digitalPinToInterrupt(pin);
    attachInterrupt(pin, callback, mode);
    detachInterrupt(pin);
    return mapped;
}

}  // namespace p0
