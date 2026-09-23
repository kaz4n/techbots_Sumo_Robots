// Declares finite A1 raw-source capture with the existing pure decoder's diagnostics.
// Keeps ADC permission explicit and distinguishes recorded evidence from logical validity.
// D112 contract: independent contract, chronology and native-binding checks follow adoption.
#pragma once
#include "hal/power.h"
#include "hal/ui.h"
#include <cstdint>

namespace ui_bench {
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, COMPLETE, FAULT };
enum class Fault : std::uint8_t {
    NONE, PORT, CONFIG, SETUP, ADC, CONTRACT, SOURCE_ORDER, CLOCK
};
struct Port {
    void* context = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
    power::InitResult (*beginButtons)(void*) = nullptr;
    power::ButtonSample (*readButtons)(void*) = nullptr;
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
    power::ButtonSample sample;
    ui::ButtonDecode decoded;
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
    bool last_read_accepted = false; // Raw-source capture acceptance, not logical qualification.
    bool decode_matches_sample = false; // False after an actual read with rejected A.
    power::InitResult setup;
    power::ButtonSample sample;
    ui::ButtonDecode decoded; // Latest actually delivered decode; bad A preserves older output.
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
    bool poll(); // True only on publication, including the final immutable record.
    const Report& report() const;
    std::uint32_t captureCapacity() const;
    std::uint32_t captureCount() const;
    const Capture* capture(std::uint32_t index) const;
private:
    // Implementation helpers and fixed storage are assigned to the implementation worker.
};
} // namespace ui_bench
