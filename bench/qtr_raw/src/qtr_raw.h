// Declares a finite capture of complete native QTR timing evidence.
// Keeps pad grants explicit and captured records immutable without other I/O owners.
// Tested through independent D109 lifecycle, chronology, capture and binding cases.
#pragma once
#include "hal/line_qtr_adapter.h"
#include <cstdint>

namespace qtr_raw {
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, COMPLETE, STOPPED, FAULT };
enum class Fault : std::uint8_t {
    NONE, PORT, CONFIG, CLOCK, CONTRACT, SOURCE_ORDER, PROVIDER, CLEANUP
};
struct Port {
    void* context = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
    line_qtr::Status (*begin)(void*, bool exclusive_pads) = nullptr;
    line_qtr::Status (*start)(void*) = nullptr;
    line_qtr::Snapshot (*report)(void*) = nullptr;
    line_qtr::Snapshot (*advance)(void*) = nullptr;
    line_qtr::Snapshot (*cancel)(void*) = nullptr;
};
struct Grants {
    bool exclusive_pads = false;
};
struct Timing {
    std::uint32_t calls = 0U;
    std::uint32_t measured_calls = 0U;
    std::uint32_t last_us = 0U;
    std::uint32_t maximum_us = 0U;
    bool last_valid = false;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Fault fault = Fault::NONE;
    bool fresh = false;
    bool counter_saturated = false;
    bool clock_fault = false;
    bool cancel_attempted = false;
    line_qtr::Status setup_status = line_qtr::Status::NOT_INITIALIZED;
    line_qtr::Status start_status = line_qtr::Status::NOT_INITIALIZED;
    line_qtr::RawQualification qualification = line_qtr::RawQualification::ABSENT;
    line_qtr::RawQualification cancel_qualification = line_qtr::RawQualification::ABSENT;
    line_qtr::Snapshot snapshot;
    line_qtr::Snapshot cancellation;
    std::uint32_t captured_frames = 0U;
    std::uint32_t not_due = 0U;
    Timing setup, start, advance, cancel, poll;
};
class Runner {
public:
    explicit Runner(const Port& port);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    bool poll(); // True only when one frame was appended, including the final frame.
    void stop();
    const Report& report() const;
    std::uint32_t captureCapacity() const;
    std::uint32_t captureCount() const;
    // Published slots remain unchanged until destruction; unpublished indices return null.
    const line_qtr::Snapshot* capture(std::uint32_t index) const;
private:
    // Implementation may add private helpers/state and fixed config-sized storage only.
    Port port_;
    Report report_;
};
} // namespace qtr_raw
