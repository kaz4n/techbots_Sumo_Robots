// Defines separate neutral and diagnostic-pull-up QTR-style timing records.
// Retains actual GPIO observations without claiming attached sensor measurements.
// D-065 independent host tests and passive target readout verify this layout.
#pragma once
#include "config.h"
#include <cstdint>

namespace p0 {
enum class QtrOutcome : std::uint32_t {
    ALL_LOW = 1, DEADLINE = 2, CHARGE_GUARD = 3, POLL_GUARD = 4,
    CLOCK_FAULT = 5, BAD_LEVEL = 6
};
struct QtrSample {
    std::uint32_t mode; // 0 neutral INPUT; 1 diagnostic-only INPUT_PULLUP
    QtrOutcome outcome;
    std::uint32_t overhead_us;
    std::uint32_t drive_us;
    std::uint32_t charge_us;
    std::uint32_t release_us;
    std::uint32_t observe_us;
    std::uint32_t cleanup_us;
    std::uint32_t total_us;
    std::uint32_t charge_polls;
    std::uint32_t polls;
    std::uint32_t low_mask;
    std::uint32_t timeout_mask;
    std::uint32_t first_low_us[4]; // UINT32_MAX means never observed LOW
    std::uint32_t cleanup_calls; // attempted INPUT calls; wrappers discard errors
};
struct QtrCapture {
    std::uint32_t version;
    std::uint32_t ready_mask; // bit0 GPIOA, bit1 GPIOB
    std::uint32_t complete; // acquisition finished, not proof of valid stimulus
    std::uint32_t completed;
    std::uint32_t start_us;
    std::uint32_t end_us;
    QtrSample samples[2U * config::P0_QTR_SAMPLES_PER_MODE];
};
std::uint32_t qtrReadyMask();
static_assert(sizeof(QtrSample) == 72, "QTR sample layout changed");
static_assert(sizeof(QtrCapture) == 14424, "QTR capture layout changed");
} // namespace p0

extern volatile p0::QtrCapture p0Qtr;
