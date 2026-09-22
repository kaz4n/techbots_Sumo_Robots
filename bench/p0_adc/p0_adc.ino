// Records first-use and subsequent analogRead costs during inert startup only.
// Stock ADC waits are unbounded, so this diagnostic never calls ADC from loop.
// D-063 host substitutes check records; passive target readout measures real calls.
#include "src/config.h"
#include "src/adc_capture.h"
#include <Arduino.h>

static_assert(MOTORS_ALLOWED == 0, "This P0 diagnostic must remain inert");
static_assert(config::P0_ADC_PIN == A0, "Installed A0 mapping changed");
volatile p0::AdcCapture p0Adc = {};

void setup() {
    p0Adc.version = 1;
    p0Adc.start_us = micros();
    for (std::uint32_t i = 0; i < config::P0_ADC_SAMPLES; ++i) {
        const std::uint32_t overheadStart = micros();
        const std::uint32_t overheadEnd = micros();
        const std::uint32_t start = micros();
        const std::int32_t value = analogRead(config::P0_ADC_PIN);
        const std::uint32_t end = micros();
        p0Adc.samples[i].overhead_us = overheadEnd - overheadStart;
        p0Adc.samples[i].elapsed_us = end - start;
        p0Adc.samples[i].value = value;
        // Publish only whole records; a stuck call leaves incomplete evidence.
        p0Adc.completed = i + 1;
    }
    p0Adc.end_us = micros();
    p0Adc.complete = 1;
}

void loop() {
    // Frozen RAM is read after setup; no runtime ADC, logging or output work.
}
