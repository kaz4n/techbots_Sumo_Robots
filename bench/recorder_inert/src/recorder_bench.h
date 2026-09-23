// Runs an explicitly synthetic B15 attempt against actual Robot/Gate/Recorder.
// Makes elapsed recording and loss evidence observable without peripheral writes.
// Independent contract tests exercise chronology, STOP sealing and retained CRC.
#pragma once
#include "hal/motors.h"
#include "hal/recorder.h"
#include <cstddef>
#include <cstdint>
namespace recorder_bench {
enum class Phase : std::uint32_t { BOOT, RUNNING, FINALIZING, CHECKSUM, FROZEN, FAILED };
enum class Failure : std::uint32_t {
    NONE, CLOCK, REENTRY, GATE, START_TIMEOUT, ROBOT, RECORDER, SEAL_TIMEOUT, CHECKSUM
};
struct ClockPort { void* context = nullptr; std::uint32_t (*now_us)(void*) = nullptr; };
// All words are uint32 little-endian on target; phase/failure hold the enums above.
// Timings cover the synthetic runner only, not full app/HAL/diagnostic overhead.
struct Report {
    std::uint32_t schema_version = 0U; // word 0
    std::uint32_t byte_size = 0U; // word 1
    std::uint32_t phase = 0U; // word 2
    std::uint32_t failure = 0U; // word 3
    std::uint32_t boot_us = 0U; // word 4
    std::uint32_t last_us = 0U; // word 5
    std::uint32_t release_us = 0U; // word 6
    std::uint32_t stop_us = 0U; // word 7
    std::uint32_t elapsed_us = 0U; // word 8
    std::uint32_t ticks = 0U; // word 9
    std::uint32_t missed_slots = 0U; // word 10
    std::uint32_t max_lateness_us = 0U; // word 11
    std::uint32_t max_step_us = 0U; // word 12
    std::uint32_t nonzero_pwm = 0U; // word 13
    std::uint32_t enabled_en = 0U; // word 14
    std::uint32_t configure_calls = 0U; // word 15
    std::uint32_t crc32 = 0U; // word 16
    std::uint32_t checksum_rows = 0U; // word 17
    std::uint32_t source_phase = 0U; // word 18
    std::uint32_t frame_count = 0U; // word 19
    std::uint32_t event_count = 0U; // word 20
    std::uint32_t epoch_lo = 0U; // word 21
    std::uint32_t epoch_hi = 0U; // word 22
    std::uint32_t last_frame_lo = 0U; // word 23
    std::uint32_t last_frame_hi = 0U; // word 24
    std::uint32_t mode = 0U; // word 25
    std::uint32_t observed_results = 0U; // word 26
    std::uint32_t missing_results = 0U; // word 27
    std::uint32_t rejected_results = 0U; // word 28
    std::uint32_t identity_rejected = 0U; // word 29
    std::uint32_t malformed_batches = 0U; // word 30
    std::uint32_t event_semantic_rejected = 0U; // word 31
    std::uint32_t upstream_event_rejected = 0U; // word 32
    std::uint32_t upstream_event_invalid = 0U; // word 33
    std::uint32_t source_regressions = 0U; // word 34
    std::uint32_t skipped_frames = 0U; // word 35
    std::uint32_t timing_ticks_lo = 0U; // word 36
    std::uint32_t timing_ticks_hi = 0U; // word 37
    std::uint32_t timing_overruns_lo = 0U; // word 38
    std::uint32_t timing_overruns_hi = 0U; // word 39
    std::uint32_t timing_max_us = 0U; // word 40
    std::uint32_t timing_saturated = 0U; // word 41
    std::uint32_t upstream_event_overflow = 0U; // word 42
    std::uint32_t timing_incomplete = 0U; // word 43
    std::uint32_t recording_incomplete = 0U; // word 44
    std::uint32_t go_seen = 0U; // word 45
    std::uint32_t final_frame_missing = 0U; // word 46
    std::uint32_t interrupted = 0U; // word 47
    std::uint32_t terminal_exhausted = 0U; // word 48
    std::uint32_t frame_overwritten = 0U; // word 49
    std::uint32_t frame_rejected_status = 0U; // word 50
    std::uint32_t frame_clamped = 0U; // word 51
    std::uint32_t frame_invalid = 0U; // word 52
    std::uint32_t event_overflow = 0U; // word 53
    std::uint32_t event_rejected = 0U; // word 54
    std::uint32_t incomplete = 0U; // word 55
    std::uint32_t robot_faults = 0U; // word 56
    std::uint32_t gate_fault = 0U; // word 57
    std::uint32_t reserved[6] = {};
};
static_assert(sizeof(Report) == 256U, "Frozen capture ABI");
struct StackSample {
    std::uint32_t valid = 0U;
    std::uint32_t region_start = 0U;
    std::uint32_t region_size = 0U;
    std::uint32_t region_delta = 0U;
    std::uint32_t minimum_sp = 0U;
    std::uint32_t samples = 0U;
    std::uint32_t sampled_headroom_bytes = 0U;
    std::uint32_t fault = 0U;
};
struct Diagnostics {
    std::uint32_t sequence_front = 0U;
    Report report;
    StackSample stack;
    std::uint32_t sequence_tail = 0U;
};
static_assert(sizeof(Diagnostics) == 296U, "Frozen sequence/stack capture ABI");
static_assert(offsetof(Diagnostics, sequence_tail) == 292U, "Frozen tail offset");
class Runner {
public:
    explicit Runner(const ClockPort& clock);
    // One begin for one run. Missing clock/reentry fails permanently.
    bool begin();
    // At most one tick or one retained CRC row; terminal calls are inert.
    void poll();
    const Report& report() const;
    const recorder::AttemptRecorder& source() const;
private:
    // Implementation-owned members follow; public API/report ABI remains frozen.
    static motors::Port motorPort(Runner*);
    static bool configureEnable(void*);
    static bool configurePwm(void*, motors::Channel);
    static bool writeEnable(void*, bool);
    static bool writePwm(void*, motors::Channel, std::uint32_t, std::uint32_t);
    static bool settle(void*);
    static std::uint32_t gateClock(void*);
    bool sampleClock(std::uint32_t&);
    bool terminal() const;
    void fail(Failure);
    bool deadlines(std::uint32_t);
    core::ButtonLevel button(std::uint32_t);
    fsm::RobotInput input(std::uint32_t);
    void tick(std::uint32_t);
    bool observe(const fsm::RobotResult&, const motors::Result&);
    void refresh();
    void refreshLoss();
    void checksum();
    void checksumBytes(const std::uint8_t*, std::size_t);
    ClockPort clock_;
    Report report_;
    fsm::Robot robot_;
    recorder::AttemptRecorder source_;
    motors::MotorGate gate_;
    fsm::PreviousTick previous_;
    std::uint64_t release_age_us_ = 0U;
    std::uint32_t latest_us_ = 0U, scheduled_us_ = 0U, stage_started_us_ = 0U;
    std::uint32_t crc_ = 0xFFFFFFFFU;
    std::size_t checksum_index_ = 0U;
    std::uint8_t button_stage_ = 0U;
    bool began_ = false, have_clock_ = false, stage_observed_ = false;
    bool released_ = false, go_seen_ = false;
};
} // namespace recorder_bench
