// Declares finite, timestamped capture of the existing battery-only native Reader.
// Keeps ADC permission explicit and preserves unfiltered samples without extra owners.
// D110 draft: independent cadence, chronology, capture and binding tests are pending.
#pragma once
#include "hal/power.h"
#include <cstdint>

namespace vbat {
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, COMPLETE, FAULT };
enum class Fault : std::uint8_t {
    NONE, PORT, CONFIG, SETUP, ADC, CONTRACT, SOURCE_ORDER, CLOCK
};
struct Port {
    void* context = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
    power::InitResult (*beginBattery)(void*) = nullptr;
    power::Sample (*readBattery)(void*) = nullptr;
};
struct Grants {
    bool exclusive_adc = false;
};
struct Timing {
    std::uint32_t calls = 0U;
    std::uint32_t measured_calls = 0U;
    std::uint32_t last_us = 0U;
    std::uint32_t maximum_us = 0U;
    bool last_valid = false;
};
struct Capture {
    power::Sample sample;
    std::uint32_t call_started_us = 0U; // S
    std::uint32_t call_returned_us = 0U; // A
    std::uint32_t poll_closed_us = 0U; // C
    std::uint32_t source_us = 0U;
    std::uint32_t read_us = 0U;
    std::uint32_t poll_us = 0U;
    std::uint32_t missed_before = 0U;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Fault fault = Fault::NONE;
    bool fresh = false;
    bool clock_fault = false;
    bool counter_saturated = false;
    bool sample_seen = false;
    bool last_read_accepted = false;
    power::InitResult setup;
    power::Sample sample; // Actual latest returned result, including failure.
    std::uint32_t captured_samples = 0U;
    std::uint32_t not_due = 0U;
    std::uint32_t missed_releases = 0U;
    Timing setup_timing, read_timing, poll_timing;
};
class Runner {
public:
    explicit Runner(const Port& port);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    bool poll(); // True only when one immutable record was published, including the last.
    const Report& report() const;
    std::uint32_t captureCapacity() const;
    std::uint32_t captureCount() const;
    const Capture* capture(std::uint32_t index) const; // Null for every unpublished index.
private:
    // Future implementation owns private helpers and fixed config-sized storage only.
    Port port_;
    Report report_;
};
} // namespace vbat
