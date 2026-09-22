// Measures neutral and diagnostic-pull-up four-pin acquisition during setup.
// Exercises actual finite GPIO polling without claiming attached QTR sensors.
// D-065 independent host tests and exact passive readout check frozen records.
#include "src/config.h"
#include "src/qtr_capture.h"
#include <Arduino.h>

static_assert(MOTORS_ALLOWED == 0, "This P0 diagnostic must remain inert");
static_assert(config::P0_QTR_PINS[0] == D2 && config::P0_QTR_PINS[1] == D4 &&
              config::P0_QTR_PINS[2] == D7 && config::P0_QTR_PINS[3] == D8,
              "Installed diagnostic header mapping changed");
volatile p0::QtrCapture p0Qtr = {};

bool duration(std::uint32_t& destination, std::uint32_t start, std::uint32_t end,
              p0::QtrSample& sample) {
    destination = end - start;
    if (destination < 0x80000000U) {
        return true;
    }
    sample.outcome = p0::QtrOutcome::CLOCK_FAULT;
    return false;
}

bool charge(p0::QtrSample& sample, std::uint32_t& boundary) {
    const std::uint32_t start = boundary;
    sample.outcome = p0::QtrOutcome::CHARGE_GUARD;
    for (std::uint32_t i = 0; i < config::P0_QTR_GUARD_POLLS; ++i) {
        boundary = micros();
        sample.charge_polls = i + 1U;
        if (!duration(sample.charge_us, start, boundary, sample)) {
            return false;
        }
        if (sample.charge_us >= config::QTR_CHARGE_US + config::P0_QTR_QUANTIZATION_US) {
            return true;
        }
    }
    return false;
}

void observe(p0::QtrSample& sample, std::uint32_t& boundary) {
    const std::uint32_t start = boundary;
    sample.outcome = p0::QtrOutcome::POLL_GUARD;
    for (std::uint32_t pass = 0; pass < config::P0_QTR_GUARD_POLLS; ++pass) {
        int levels[4]{};
        bool valid = true;
        for (std::uint32_t pin = 0; pin < 4U; ++pin) {
            levels[pin] = digitalRead(config::P0_QTR_PINS[pin]);
            valid = valid && (levels[pin] == LOW || levels[pin] == HIGH);
        }
        boundary = micros();
        sample.polls = pass + 1U;
        if (!duration(sample.observe_us, start, boundary, sample)) {
            return;
        }
        if (!valid) {
            sample.outcome = p0::QtrOutcome::BAD_LEVEL;
            return;
        }
        for (std::uint32_t pin = 0; pin < 4U; ++pin) {
            if (levels[pin] == LOW && (sample.low_mask & (1U << pin)) == 0U) {
                sample.low_mask |= 1U << pin;
                sample.first_low_us[pin] = sample.observe_us;
            }
        }
        if (sample.observe_us >= config::QTR_TIMEOUT_US) {
            sample.timeout_mask = 15U ^ sample.low_mask;
            sample.outcome = p0::QtrOutcome::DEADLINE;
            return;
        }
        if (sample.low_mask == 15U) {
            sample.outcome = p0::QtrOutcome::ALL_LOW;
            return;
        }
    }
}

void acquire(p0::QtrSample& sample, std::uint32_t start, std::uint32_t& boundary) {
    for (const auto pin : config::P0_QTR_PINS) {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
    }
    boundary = micros();
    if (!duration(sample.drive_us, start, boundary, sample) || !charge(sample, boundary)) {
        return;
    }
    const std::uint32_t release_start = boundary;
    for (const auto pin : config::P0_QTR_PINS) {
        pinMode(pin, sample.mode == 0U ? INPUT : INPUT_PULLUP);
    }
    boundary = micros();
    if (duration(sample.release_us, release_start, boundary, sample)) {
        observe(sample, boundary);
    }
}

p0::QtrSample measureSample(std::uint32_t mode) {
    p0::QtrSample sample{};
    sample.mode = mode;
    sample.outcome = p0::QtrOutcome::CLOCK_FAULT;
    for (auto& first : sample.first_low_us) {
        first = UINT32_MAX;
    }
    const std::uint32_t overhead_start = micros();
    const std::uint32_t overhead_end = micros();
    const bool valid_overhead = duration(sample.overhead_us, overhead_start, overhead_end, sample);
    const std::uint32_t start = micros();
    std::uint32_t boundary = start;
    if (valid_overhead) {
        acquire(sample, start, boundary);
    }
    // Every started sample gets exactly one neutral-input cleanup attempt per pad.
    for (const auto pin : config::P0_QTR_PINS) {
        pinMode(pin, INPUT);
        ++sample.cleanup_calls;
    }
    const std::uint32_t end = micros();
    duration(sample.cleanup_us, boundary, end, sample);
    duration(sample.total_us, start, end, sample);
    return sample;
}

void storeSample(std::uint32_t index, const p0::QtrSample& source) {
    auto& target = p0Qtr.samples[index];
    target.mode = source.mode;
    target.outcome = source.outcome;
    target.overhead_us = source.overhead_us;
    target.drive_us = source.drive_us;
    target.charge_us = source.charge_us;
    target.release_us = source.release_us;
    target.observe_us = source.observe_us;
    target.cleanup_us = source.cleanup_us;
    target.total_us = source.total_us;
    target.charge_polls = source.charge_polls;
    target.polls = source.polls;
    target.low_mask = source.low_mask;
    target.timeout_mask = source.timeout_mask;
    for (std::uint32_t pin = 0; pin < 4U; ++pin) {
        target.first_low_us[pin] = source.first_low_us[pin];
    }
    target.cleanup_calls = source.cleanup_calls;
    p0Qtr.completed = index + 1U;
}

void setup() {
    p0Qtr.version = 1;
    p0Qtr.ready_mask = p0::qtrReadyMask();
    if (p0Qtr.ready_mask != 3U) {
        return;
    }
    p0Qtr.start_us = micros();
    for (std::uint32_t i = 0; i < 2U * config::P0_QTR_SAMPLES_PER_MODE; ++i) {
        const auto sample = measureSample(i / config::P0_QTR_SAMPLES_PER_MODE);
        storeSample(i, sample);
        if (sample.outcome != p0::QtrOutcome::ALL_LOW &&
            sample.outcome != p0::QtrOutcome::DEADLINE) {
            return;
        }
    }
    const std::uint32_t end = micros();
    if (end - p0Qtr.start_us < 0x80000000U) {
        p0Qtr.end_us = end;
        p0Qtr.complete = 1U;
    }
}

void loop() {
    // Leave neutral inputs and the complete or failed record unchanged.
}
