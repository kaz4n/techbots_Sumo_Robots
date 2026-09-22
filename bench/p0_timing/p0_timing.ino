// Collects one minute of bare scheduler lateness in a fixed RAM histogram.
// Prepares P0 timing measurement without touching GPIO, Bridge or motors.
// Host syntax checked; real timing and debugger readout remain hardware-pending.
#include "src/config.h"
#include <Arduino.h>

static_assert(MOTORS_ALLOWED == 0, "This P0 diagnostic must remain inert");
volatile std::uint32_t p0Samples = 0;
volatile std::uint32_t p0MaxLateUs = 0;
volatile std::uint32_t p0OverPeriod = 0;
volatile std::uint32_t p0Histogram[config::P0_JITTER_HISTOGRAM_US + 1] = {};
std::uint32_t lastTickUs = 0;

void setup() {
    lastTickUs = micros();
}

void loop() {
    if (p0Samples >= config::P0_JITTER_SAMPLES) {
        return;
    }
    const std::uint32_t now = micros();
    const std::uint32_t elapsed = now - lastTickUs;
    if (elapsed < config::TICK_US) {
        return;
    }
    const std::uint32_t lateness = elapsed - config::TICK_US;
    // Do not hide missed periods behind a burst of catch-up samples.
    lastTickUs += config::TICK_US;
    if (lateness >= config::TICK_US) {
        ++p0OverPeriod;
        lastTickUs = now;
    }
    if (lateness > p0MaxLateUs) {
        p0MaxLateUs = lateness;
    }
    const std::uint32_t bin = lateness < config::P0_JITTER_HISTOGRAM_US ?
        lateness : config::P0_JITTER_HISTOGRAM_US;
    ++p0Histogram[bin];
    ++p0Samples;
}
