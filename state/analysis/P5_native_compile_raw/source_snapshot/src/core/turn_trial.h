// Defines one finite P3 turn trial using the existing B7 controller.
// Reflects coordinates for exact left half-turns without changing match behavior.
// Independent contract tests cover signed angles, timing, fallback and cancellation.
#pragma once
#include "motion.h"
#include <cstdint>

namespace turn_trial {
enum class Phase : std::uint8_t { NOT_STARTED, TURN, BRAKE, COMPLETE, INTERRUPTED, FAULT };
enum class Reason : std::uint8_t { NONE, STOP, EDGE, CLOCK_ORDER, INVALID_START, INVALID_HEADING };
struct Sample {
    std::uint32_t t_us = 0U;
    float heading_deg = 0.0F; // Actual caller yaw, never a synthetic IMU fault.
    bool imu_ok = false;
    bool edge_required = false;
    bool stop_requested = false;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Reason reason = Reason::NONE;
    motion::Status turn_status = motion::Status::IDLE;
    float signed_angle_deg = 0.0F;
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    std::uint32_t started_us = 0U;
    std::uint32_t turn_finished_us = 0U;
    std::uint32_t finished_us = 0U;
    bool imu_fallback = false;
    bool turn_finished = false;
    bool finished = false;
    bool fresh = false;
    bool phase_changed = false;
};
class Trial {
public:
    // Exact contract: state/analysis/P3_turn_trial_contract.md. One start attempt;
    // owner first establishes actual GO. This helper grants no motor permission.
    bool start(std::uint32_t t_us, float heading_deg, float signed_angle_deg, bool imu_ok);
    Report step(const Sample& sample);
    const Report& report() const { return report_; }
private:
    bool active() const;
    void terminate(Phase phase, Reason reason, std::uint32_t time);
    void advanceTurn(const Sample& sample);
    motion::Turn turn_;
    Report report_;
    std::uint32_t last_us_ = 0U;
    bool attempted_ = false;
    bool left_ = false;
};
} // namespace turn_trial
