// Defines the finite P2 B4 directional request sequence without motor authority.
// Keeps bench timing and cancellation pure until actual Robot integration.
// Independent contract tests cover literal phases, wrap, gaps and terminal states.
#pragma once
#include <cstdint>

namespace stand_sequence {
enum class Phase : std::uint8_t { NOT_STARTED, DRIVE, BRAKE, COAST, COMPLETE, INTERRUPTED, FAULT };
enum class Reason : std::uint8_t { NONE, STOP, EDGE, CLOCK_ORDER, CLOCK_GAP };
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Reason reason = Reason::NONE;
    std::uint8_t segment = 0U;
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    bool fresh = false;
    bool phase_changed = false;
};
class Sequence {
public:
    // Pure request planning only; owner must first establish actual qualified GO.
    // One accepted start per instance; no restart or motor permission is provided.
    bool start(std::uint32_t t_us);
    // Exact priority/time/pulse rules: state/analysis/P2_stand_sequence_contract.md.
    Report step(std::uint32_t t_us, bool edge_required = false, bool stop_requested = false);
    // D120 owner safety cancellation; STOP/EDGE only while active. No clock advance.
    // Rejection is passive, including pulses; accepted cancellation is fresh.
    bool interrupt(Reason reason);
    const Report& report() const { return report_; }
private:
    void selectSegment();
    void terminate(Phase phase, Reason reason);
    Report report_;
    std::uint32_t last_us_ = 0U;
    std::uint32_t entered_us_ = 0U;
    bool started_ = false;
};
} // namespace stand_sequence
