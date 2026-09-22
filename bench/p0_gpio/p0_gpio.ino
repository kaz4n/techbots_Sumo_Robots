// Measures internal LED GPIO calls and records digital readbacks during setup.
// Keeps a finite bare-board benchmark separate from robot GPIO and motor drivers.
// D-064 independent host tests and pinned passive readout verify raw records.
#include "src/config.h"
#include "src/gpio_capture.h"
#include <Arduino.h>

static_assert(MOTORS_ALLOWED == 0, "This P0 diagnostic must remain inert");
static_assert(config::P0_GPIO_PIN == LED_BUILTIN, "Installed builtin LED mapping changed");
static_assert(config::P0_GPIO_PIN == LED3_R, "Installed red LED mapping changed");
volatile p0::GpioCapture p0Gpio = {};

p0::GpioSample measureSample() {
    p0::GpioSample sample{};
    std::uint32_t start = micros();
    sample.overhead_us = micros() - start;
    start = micros();
    pinMode(config::P0_GPIO_PIN, OUTPUT);
    sample.pin_mode_us = micros() - start;
    start = micros();
    sample.low_level = digitalRead(config::P0_GPIO_PIN);
    sample.read_low_us = micros() - start;
    start = micros();
    digitalWrite(config::P0_GPIO_PIN, HIGH);
    sample.write_high_us = micros() - start;
    start = micros();
    sample.high_level = digitalRead(config::P0_GPIO_PIN);
    sample.read_high_us = micros() - start;
    start = micros();
    pinMode(config::P0_GPIO_PIN, OUTPUT);
    digitalWrite(config::P0_GPIO_PIN, HIGH);
    sample.pair_us = micros() - start;
    sample.pair_level = digitalRead(config::P0_GPIO_PIN);
    return sample;
}

void storeSample(std::uint32_t index, const p0::GpioSample& sample) {
    auto& destination = p0Gpio.samples[index];
    destination.overhead_us = sample.overhead_us;
    destination.pin_mode_us = sample.pin_mode_us;
    destination.write_high_us = sample.write_high_us;
    destination.read_low_us = sample.read_low_us;
    destination.read_high_us = sample.read_high_us;
    destination.pair_us = sample.pair_us;
    destination.low_level = sample.low_level;
    destination.high_level = sample.high_level;
    destination.pair_level = sample.pair_level;
    p0Gpio.completed = index + 1;
}

void finishMeasurement(bool success) {
    // Even a readback mismatch gets one final off attempt, without retrying.
    digitalWrite(config::P0_GPIO_PIN, HIGH);
    p0Gpio.final_level = digitalRead(config::P0_GPIO_PIN);
    p0Gpio.end_us = micros();
    p0Gpio.complete = success && p0Gpio.final_level == HIGH ? 1U : 0U;
}

void setup() {
    p0Gpio.version = 1;
    p0Gpio.ready = p0::gpioReady() ? 1U : 0U;
    if (p0Gpio.ready == 0) {
        return;
    }
    p0Gpio.start_us = micros();
    for (std::uint32_t i = 0; i < config::P0_GPIO_SAMPLES; ++i) {
        const p0::GpioSample sample = measureSample();
        storeSample(i, sample);
        if (sample.low_level != LOW || sample.high_level != HIGH || sample.pair_level != HIGH) {
            finishMeasurement(false);
            return;
        }
    }
    finishMeasurement(true);
}

void loop() {
    // The off-state and complete or failed raw record remain unchanged.
}
