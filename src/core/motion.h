// Defines the B7 IMU-heading turn and stationary brake contracts.
// Provides bounded motion requests without choosing unresolved fallback semantics.
// Spec-derived host tests cover signs, exact completion, timeout and wraparound.
#pragma once
#include <cstdint>

namespace motion {
enum class Status : std::uint8_t { IDLE, ACTIVE, DONE, TIMED_OUT, INVALID };
struct Result {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    Status status = Status::IDLE;
};

class HeadingTurn {
public:
    // Closed-loop portion of turnTo only. Requires valid IMU heading at each
    // step. Accept finite target and max duty in [TURN_MIN_DUTY, 1]. Invalid
    // start/heading produces a latched INVALID zero request until start/reset.
    bool start(std::uint32_t t_us, float target_heading_deg, float max_duty);
    // Shortest signed error in (-180, 180]; positive error pivots right (+,-).
    // ACTIVE duty is clamp(K_TURN_PER_DEG*abs(error), TURN_MIN_DUTY, max_duty).
    // Strictly abs(error)<HEADING_TOL_DEG completes. At TURN_TIMEOUT_MS, timeout
    // takes precedence over heading completion. Terminal results stay zero.
    // Caller must choose fault fallback separately and pass demands to governor.
    Result step(std::uint32_t t_us, float heading_deg);
    void reset();
private:
    std::uint32_t started_us_ = 0;
    float target_heading_deg_ = 0.0F;
    float max_duty_ = 0.0F;
    Status status_ = Status::IDLE;
};

class Brake {
public:
    // Stationary B7 brake timer. duration_ms must fit a uint32 microsecond
    // interval (<=UINT32_MAX/1000). No voltage factor applies to stationary time.
    bool start(std::uint32_t t_us, std::uint32_t duration_ms);
    Result step(std::uint32_t t_us);
    void reset();
private:
    std::uint32_t started_us_ = 0;
    std::uint32_t duration_us_ = 0;
    Status status_ = Status::IDLE;
};
// These primitives do not grant motor permission. Brake requests zero while the
// caller retains enabled state only if countdown, fault and MotorGate allow it.
} // namespace motion
