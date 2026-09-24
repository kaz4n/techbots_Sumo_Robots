// Describes the isolated P3 stopping trial's observable request history.
// Separates approach timeout and escape interruption from physical distance evidence.
// Independent Robot/Runtime profile tests cover this contract and actual Gate writes.
#pragma once
#include "motion.h"
#include <cstdint>

namespace stop_trial {
enum class Phase : std::uint8_t { NOT_STARTED, APPROACH, BRAKE, COMPLETE, INTERRUPTED, FAULT };
enum class Reason : std::uint8_t { NONE, STOP, EDGE, NO_EDGE_TIMEOUT, INVALID_MOTION };
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Reason reason = Reason::NONE;
    motion::Status approach_status = motion::Status::IDLE;
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    std::uint32_t started_us = 0U;
    std::uint32_t approach_finished_us = 0U;
    std::uint32_t finished_us = 0U;
    bool started = false;
    bool approach_finished = false;
    bool finished = false;
    bool imu_fallback = false;
    bool fresh = false;
    bool phase_changed = false;
};
} // namespace stop_trial
