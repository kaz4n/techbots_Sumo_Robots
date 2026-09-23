// Declares finite A1 raw-source capture with the existing pure decoder's diagnostics.
// Keeps ADC permission explicit and distinguishes recorded evidence from logical validity.
// D112 contract: independent contract, chronology and native-binding checks follow adoption.
#pragma once
#include "config.h"
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
    bool portsValid() const;
    void fail(Fault fault);
    void add(std::uint32_t& counter, std::uint32_t amount = 1U);
    void attempt(Timing& timing);
    void measure(Timing& timing, std::uint32_t elapsed_us);
    bool admitClock(std::uint32_t now_us);
    bool clock(std::uint32_t& now_us);
    bool close(std::uint32_t started_us, Timing& timing, std::uint32_t& closed_us);
    void examineSetup();
    void examineSample();
    void examineSource(std::uint32_t started_us, std::uint32_t returned_us);
    bool read(std::uint32_t started_us, std::uint32_t missed);
    void stage(std::uint32_t started_us, std::uint32_t returned_us, std::uint32_t missed);
    void publish(std::uint32_t closed_us);
    Port port_;
    Report report_;
    Capture captures_[config::UI_BENCH_SAMPLES > 0U ? config::UI_BENCH_SAMPLES : 1U]{};
    bool attempted_ = false;
    bool clock_seen_ = false;
    bool interval_active_ = false;
    bool source_seen_ = false;
    std::uint32_t last_clock_us_ = 0U;
    std::uint32_t interval_elapsed_us_ = 0U;
    std::uint32_t source_age_us_ = 0U;
};
} // namespace ui_bench
