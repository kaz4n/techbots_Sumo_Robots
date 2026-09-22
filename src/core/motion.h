// Defines B7 turn, straight, arc and stationary brake requests.
// Keeps approved D-022/D-023 motion math separate from governor and motor permission.
// Spec-derived host tests cover signs, exact deadlines, faults and time wrap.
#pragma once
#include <cstdint>

namespace motion {
enum class Status : std::uint8_t { IDLE, ACTIVE, DONE, TIMED_OUT, INVALID };
enum class Direction : std::uint8_t { LEFT, RIGHT };
struct Result {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    Status status = Status::IDLE;
    bool imu_fallback = false;
};

// Internal elapsed-time accumulator; caller supplies time, never reads a clock.
// Successive call gaps must be less than one complete uint32 microsecond wrap.
struct Interval {
    std::uint32_t last_us = 0;
    std::uint64_t elapsed_us = 0;
    void begin(std::uint32_t t_us);
    void advance(std::uint32_t t_us);
};

class Turn {
public:
    // Finite target/last-known heading; max duty in [TURN_MIN_DUTY,1]. Time
    // starts here. Initial error is the shortest angle in (-180,180].
    bool start(std::uint32_t t_us, float heading_deg, float target_heading_deg,
               float max_duty, bool imu_ok);
    // IMU: clamp(K_TURN_PER_DEG*abs(error), TURN_MIN_DUTY, max_duty), (+,-)
    // for clockwise. Strict abs(error)<HEADING_TOL_DEG completes. After loss,
    // latch fallback for this command: last valid remaining angle times
    // TURN_MS_PER_DEG, starting at the first unavailable tick, at max_duty.
    // Restoring IMU never restarts or extends this command. The original
    // TURN_TIMEOUT_MS deadline always applies and takes precedence at a tie.
    // With imu_ok=false, current heading is ignored (start still needs finite
    // last-known heading). Nonfinite healthy heading latches INVALID/zero.
    Result step(std::uint32_t t_us, float heading_deg, bool imu_ok);
    void reset();
private:
    void beginFallback();
    Interval interval_;
    std::uint64_t fallback_elapsed_us_ = 0;
    double fallback_duration_us_ = 0.0;
    float target_heading_deg_ = 0.0F;
    double error_deg_ = 0.0;
    float max_duty_ = 0.0F;
    Status status_ = Status::IDLE;
    bool fallback_ = false;
};

class Straight {
public:
    // Capture finite last-known heading at start; signed base duty in [-1,1].
    // Finite duration <= UINT32_MAX/1000 milliseconds; zero completes at once.
    bool start(std::uint32_t t_us, float heading_deg, float duty,
               std::uint32_t duration_ms);
    // D-022: shortest heading error * K_TURN_PER_DEG; correction capped at
    // min(TURN_MIN_DUTY,abs(base)). Left=base+correction, right=base-correction,
    // each clamped [-1,1] before governor. This also preserves reverse signs.
    // Unavailable IMU uses equal base requests and reports fallback; recovery
    // resumes the original reference without resetting time. Current heading
    // is ignored only while unavailable. Invalid healthy heading stops command.
    Result step(std::uint32_t t_us, float heading_deg, bool imu_ok);
    void reset();
private:
    Interval interval_;
    std::uint32_t duration_us_ = 0;
    float heading_deg_ = 0.0F;
    float duty_ = 0.0F;
    Status status_ = Status::IDLE;
};

class Arc {
public:
    // Forward arc: duty and inner_ratio in [0,1], positive finite sweep.
    // heading_deg is continuous accumulated yaw (not a wrapped bearing).
    // max_ms must fit uint32 microseconds. Start requires finite heading.
    bool start(std::uint32_t t_us, float heading_deg, Direction direction,
               float inner_ratio, float duty, float sweep_deg, std::uint32_t max_ms);
    // RIGHT: outer left=duty, inner right=duty*ratio; LEFT mirrors. Complete
    // when signed accumulated sweep >= target, otherwise timeout at max_ms.
    // Timeout wins ties. IMU unavailable skips sweep completion and relies on
    // the unchanged time bound, reporting fallback. No new timer on recovery.
    Result step(std::uint32_t t_us, float heading_deg, bool imu_ok);
    void reset();
private:
    Interval interval_;
    std::uint32_t duration_us_ = 0;
    float heading_deg_ = 0.0F;
    float sweep_deg_ = 0.0F;
    float duty_ = 0.0F;
    float inner_ratio_ = 0.0F;
    Direction direction_ = Direction::RIGHT;
    Status status_ = Status::IDLE;
};

class Brake {
public:
    // Stationary B7 brake; duration_ms must fit uint32 microseconds. No voltage
    // factor applies to time. Always zero request; exact duration yields DONE.
    bool start(std::uint32_t t_us, std::uint32_t duration_ms);
    Result step(std::uint32_t t_us);
    void reset();
private:
    Interval interval_;
    std::uint32_t duration_us_ = 0;
    Status status_ = Status::IDLE;
};

class TimedArc {
public:
    // B7/D-037 duration-only forward arc. No invented yaw target or IMU input.
    // Finite duty/ratio in [0,1], valid direction and duration fitting uint32
    // microseconds are required. Zero duration completes immediately.
    bool start(std::uint32_t t_us, Direction direction, float inner_ratio,
               float duty, std::uint32_t duration_ms);
    // RIGHT -> outer left=duty, inner right=duty*ratio; LEFT mirrors. DONE at
    // elapsed >= duration, latched zero until start/reset. No heading/voltage
    // affects timing. B11 uses the REFLANK_TURN governor profile downstream.
    Result step(std::uint32_t t_us);
    void reset();
private:
    Interval interval_;
    std::uint32_t duration_us_ = 0;
    float duty_ = 0.0F;
    float inner_ratio_ = 0.0F;
    Direction direction_ = Direction::RIGHT;
    Status status_ = Status::IDLE;
};
// Terminal statuses are latched zero until start/reset. Unsigned per-call deltas
// accumulate in uint64 so even the longest accepted duration cannot miss expiry
// across a start-relative wrap. Consecutive sample gaps must be <one uint32 wrap.
// These components never grant permission: requests pass through governor and
// MotorGate. D-023 keeps durations independent of voltage. No clock, I/O or heap.
} // namespace motion
