// Defines the finite D244 B7 sequence using acknowledged electrical settings.
// Separates bench progress from countdown, safety arbitration and motor authority.
// The frozen B7 contract and independent host oracle define acceptance boundaries.
#pragma once
#include <cstdint>

namespace brownout_sequence {
enum class Phase : std::uint8_t { NOT_STARTED, REACH, DWELL, COMPLETE, ABORTED };
enum class Reason : std::uint8_t {
    NONE, STOP, EDGE, FAULT, APPLICATION, CLOCK_ORDER, RECEIPT_GAP,
    INHIBITED, REACH_TIMEOUT, ENDPOINT_LOST, RESET_REQUEST
};

struct Receipt {
    // The owner validates the pending command identity before forwarding this.
    bool valid = false;
    std::uint64_t token = 0U;
    std::uint8_t leg_index = 0U;
    std::uint32_t applied_us = 0U;
    bool enabled = false;
    float duty_l = 0.0F;
    float duty_r = 0.0F;
};

struct Report {
    Phase phase = Phase::NOT_STARTED;
    Reason reason = Reason::NONE; // First terminal abort reason; never replaced.
    std::uint8_t leg_index = 0U; // 0..39: even forward, odd reverse; retained terminally.
    std::uint8_t completed_legs = 0U;
    std::uint8_t completed_cycles = 0U; // One acknowledged forward/reverse pair.
    float duty_l = 0.0F; // Intent only; never application or wheel-motion evidence.
    float duty_r = 0.0F;
    bool consumed = false; // Start or a pre-start RESET_REQUEST consumes this instance.
    bool started = false; // Distinguishes a real sequence start from pre-start abort.
    std::uint32_t started_us = 0U;
    std::uint32_t leg_started_us = 0U;
    bool endpoint_valid = false; // Current leg's uninterrupted acknowledged dwell.
    std::uint32_t endpoint_started_us = 0U;
    std::uint32_t last_endpoint_us = 0U;
    // Valid when completed_legs != 0; retained across the next leg's reach phase.
    std::uint32_t completed_endpoint_started_us = 0U;
    std::uint32_t completed_endpoint_last_us = 0U;
    bool receipt_seen = false;
    Receipt last_receipt;
    bool terminal_valid = false;
    std::uint32_t terminal_us = 0U; // Decision/interrupt time, not claimed hardware uptime.
};

class Sequence {
public:
    // Owner must establish actual GO after the full countdown. No reset or rearm.
    bool start(std::uint32_t t_us);
    // Call only after current STOP, source/fault and edge safety arbitration.
    // A phase-tagged receipt can complete its own leg once, never the following leg.
    Report step(std::uint32_t t_us, const Receipt& receipt);
    // RESET_REQUEST alone can consume NOT_STARTED. All terminals are immutable.
    bool interrupt(Reason reason, std::uint32_t t_us);
    const Report& report() const { return report_; }
private:
    bool acceptReceipt(std::uint32_t t_us, const Receipt& receipt);
    void selectLeg(std::uint32_t t_us);
    void completeLeg(std::uint32_t t_us);
    void terminate(Phase phase, Reason reason, std::uint32_t t_us);
    Report report_;
    std::uint32_t last_decision_us_ = 0U;
};
} // namespace brownout_sequence
