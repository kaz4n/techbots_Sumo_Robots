// Classifies B4 white and composes bounded escape rows, replans and fault inhibition.
// Keeps approved recovery policy and motion requests separate from hardware permission.
// Locked host tests cover masks, selection, row timing, replanning and mirror symmetry.
#include "edge.h"
#include "../config.h"
#include <cmath>

namespace edge {
ForwardDemand forwardDemand(ForwardBias bias) {
    const float outer = config::EDGE_BACK_DUTY;
    const float inner = outer * config::EDGE_FWD_INNER_RATIO;
    switch (bias) {
    case ForwardBias::NONE: return {outer, outer, true};
    case ForwardBias::LEFT: return {inner, outer, true};
    case ForwardBias::RIGHT: return {outer, inner, true};
    default: return {};
    }
}

std::uint8_t Classifier::observe(const std::uint32_t (&raw_us)[4]) {
    std::uint8_t white_mask = 0U;
    for (std::uint32_t i = 0U; i < 4U; ++i) {
        if (raw_us[i] >= config::QTR_WHITE_US[i]) {
            consecutive_[i] = 0U;
            continue;
        }
        // Saturation lets a continuously white corner remain confirmed forever.
        if (consecutive_[i] < config::QTR_CONFIRM_TICKS) {
            ++consecutive_[i];
        }
        if (consecutive_[i] >= config::QTR_CONFIRM_TICKS) {
            white_mask |= static_cast<std::uint8_t>(1U << i);
        }
    }
    return white_mask;
}

void Classifier::reset() {
    for (auto& count : consecutive_) {
        count = 0U;
    }
}

GuardResult Guard::step(std::uint8_t line_mask, bool motion_permitted,
                        bool script_finished) {
    static_assert(config::EDGE_PUSH_THROUGH_MS == 0U,
                  "Implement and test bounded push-through before enabling it");
    if (!motion_permitted) {
        return {false, fault_latched_, true};
    }
    const std::uint8_t white = line_mask & 0x0FU;
    if (white == 0x0FU) {
        fault_latched_ = true;
    }
    if (fault_latched_) {
        escaping_ = true;
        return {true, true, true};
    }
    if (white != 0U) {
        escaping_ = true;
    } else if (script_finished) {
        escaping_ = false;
    }
    return {escaping_, false, false};
}

void Guard::reset() {
    *this = Guard{};
}

namespace {
bool runningPhase(ScriptPhase phase) {
    return phase == ScriptPhase::BRAKE || phase == ScriptPhase::BACK ||
           phase == ScriptPhase::PIVOT || phase == ScriptPhase::FORWARD;
}

bool validDirection(motion::Direction direction) {
    return direction == motion::Direction::LEFT || direction == motion::Direction::RIGHT;
}

bool validAppliedDuty(float duty) {
    return std::isfinite(duty) && duty >= -1.0F && duty <= 1.0F;
}

bool faultPattern(std::uint8_t mask) {
    std::uint32_t count = 0U;
    for (std::uint32_t bit = 0U; bit < 4U; ++bit) count += (mask >> bit) & 1U;
    return count >= 3U;
}
} // namespace

bool RowExecutor::start(std::uint32_t t_us, std::uint8_t selected_mask,
                        float heading_deg, bool imu_ok) {
    reset();
    const auto mask = static_cast<std::uint8_t>(selected_mask & 0x0FU);
    switch (mask) {
    case 0x01U: case 0x02U: case 0x06U: case 0x09U:
        front_row_ = true;
        pivot_deg_ = static_cast<float>(config::EDGE_TURN_DEG) *
                     ((mask & 0x01U) != 0U ? 1.0F : -1.0F);
        break;
    case 0x04U: case 0x08U:
        biased_forward_ = true;
        bias_direction_ = mask == 0x04U ? motion::Direction::RIGHT :
                                         motion::Direction::LEFT;
        break;
    case 0x05U: case 0x0AU:
        pivot_deg_ = static_cast<float>(config::EDGE_SIDE_TURN_DEG) *
                     (mask == 0x05U ? 1.0F : -1.0F);
        break;
    case 0x0CU:
        break;
    default:
        phase_ = ScriptPhase::UNSUPPORTED;
        return false;
    }
    if (!std::isfinite(heading_deg)) {
        phase_ = ScriptPhase::INVALID;
        return false;
    }
    last_heading_deg_ = heading_deg;
    const ScriptPhase first = front_row_ ? ScriptPhase::BRAKE :
        (pivot_deg_ != 0.0F ? ScriptPhase::PIVOT : ScriptPhase::FORWARD);
    return beginPhase(t_us, first, imu_ok);
}

bool RowExecutor::beginPhase(std::uint32_t t_us, ScriptPhase phase, bool imu_ok) {
    phase_ = phase;
    bool started = true;
    switch (phase) {
    case ScriptPhase::BRAKE:
        brake_interval_.begin(t_us);
        break;
    case ScriptPhase::BACK:
        started = straight_.start(t_us, last_heading_deg_, -config::EDGE_BACK_DUTY,
                                  head_on_ ? config::EDGE_BACK_LONG_MS : config::EDGE_BACK_MS);
        break;
    case ScriptPhase::PIVOT:
        started = turn_.startRelative(t_us, last_heading_deg_, pivot_deg_,
                                      config::TURN_DUTY, imu_ok);
        break;
    case ScriptPhase::FORWARD:
        started = biased_forward_ ? arc_.start(t_us, bias_direction_,
            config::EDGE_FWD_INNER_RATIO, config::EDGE_BACK_DUTY, config::EDGE_FWD_MS) :
            straight_.start(t_us, last_heading_deg_, config::EDGE_BACK_DUTY,
                            config::EDGE_FWD_MS);
        break;
    case ScriptPhase::DONE:
        break;
    default:
        started = false;
        break;
    }
    if (!started) phase_ = ScriptPhase::INVALID;
    return started;
}

bool RowExecutor::startHeadOn(std::uint32_t t_us, float heading_deg, bool imu_ok,
                             motion::Direction opponent_side) {
    reset();
    phase_ = ScriptPhase::INVALID;
    if (!std::isfinite(heading_deg) ||
        (opponent_side != motion::Direction::LEFT &&
         opponent_side != motion::Direction::RIGHT)) return false;
    head_on_ = true;
    front_row_ = true;
    last_heading_deg_ = heading_deg;
    pivot_deg_ = static_cast<float>(config::EDGE_TURN_FULL_DEG) *
        (opponent_side == motion::Direction::RIGHT ? 1.0F : -1.0F);
    return beginPhase(t_us, ScriptPhase::BRAKE, imu_ok);
}

bool RowExecutor::startPushedOut(std::uint32_t t_us, float heading_deg, bool imu_ok,
                                motion::Direction direction) {
    reset();
    phase_ = ScriptPhase::INVALID;
    if (!std::isfinite(heading_deg) || !validDirection(direction)) return false;
    last_heading_deg_ = heading_deg;
    pivot_deg_ = static_cast<float>(config::EDGE_SIDE_TURN_DEG) *
        (direction == motion::Direction::RIGHT ? 1.0F : -1.0F);
    return beginPhase(t_us, ScriptPhase::PIVOT, imu_ok);
}

bool RowExecutor::advancePhase(std::uint32_t t_us, bool imu_ok) {
    switch (phase_) {
    case ScriptPhase::BRAKE: return beginPhase(t_us, ScriptPhase::BACK, imu_ok);
    case ScriptPhase::BACK: return beginPhase(t_us, ScriptPhase::PIVOT, imu_ok);
    case ScriptPhase::PIVOT:
        return beginPhase(t_us, front_row_ ? ScriptPhase::DONE : ScriptPhase::FORWARD,
                          imu_ok);
    case ScriptPhase::FORWARD: return beginPhase(t_us, ScriptPhase::DONE, imu_ok);
    default:
        phase_ = ScriptPhase::INVALID;
        return false;
    }
}

motion::Result RowExecutor::runMotion(std::uint32_t t_us, float heading_deg,
                                      bool imu_ok) {
    switch (phase_) {
    case ScriptPhase::BRAKE:
        brake_interval_.advance(t_us);
        return {0.0F, 0.0F, brake_interval_.elapsed_us >= config::TICK_US ?
                motion::Status::DONE : motion::Status::ACTIVE, false};
    case ScriptPhase::BACK:
        return straight_.step(t_us, heading_deg, imu_ok);
    case ScriptPhase::PIVOT:
        return turn_.step(t_us, heading_deg, imu_ok);
    case ScriptPhase::FORWARD:
        return biased_forward_ ? arc_.step(t_us) : straight_.step(t_us, heading_deg, imu_ok);
    default: return {};
    }
}

RowResult RowExecutor::result(const motion::Result& motion) const {
    RowResult row;
    row.phase = phase_;
    row.motion = motion;
    row.brake = !runningPhase(phase_) || phase_ == ScriptPhase::BRAKE;
    if (phase_ == ScriptPhase::PIVOT) row.profile = governor::Profile::PIVOT;
    if (phase_ == ScriptPhase::FORWARD) row.profile = governor::Profile::EDGE_FORWARD;
    if (!runningPhase(phase_)) {
        const motion::Status status = phase_ == ScriptPhase::DONE ? motion::Status::DONE :
            (phase_ == ScriptPhase::IDLE ? motion::Status::IDLE : motion::Status::INVALID);
        row.motion = {0.0F, 0.0F, status, false};
    }
    return row;
}

RowResult RowExecutor::step(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    if (!runningPhase(phase_)) return result({});
    const ScriptPhase previous_phase = phase_;
    motion::Result demand;
    bool timed_out = false;
    if (imu_ok && !std::isfinite(heading_deg)) {
        phase_ = ScriptPhase::INVALID;
    } else {
        if (imu_ok) last_heading_deg_ = heading_deg;
        // A row has at most three primitives; no delayed call backdates a phase.
        for (std::uint32_t phases = 0U; phases < 3U; ++phases) {
            demand = runMotion(t_us, heading_deg, imu_ok);
            if (demand.status == motion::Status::INVALID) {
                phase_ = ScriptPhase::INVALID;
                break;
            }
            if (demand.status != motion::Status::DONE &&
                demand.status != motion::Status::TIMED_OUT) break;
            timed_out = timed_out || demand.status == motion::Status::TIMED_OUT;
            if (!advancePhase(t_us, imu_ok) || !runningPhase(phase_)) break;
        }
    }
    RowResult row = result(demand);
    row.phase_changed = phase_ != previous_phase;
    row.turn_timed_out = timed_out;
    return row;
}

void RowExecutor::reset() {
    *this = RowExecutor{};
}

bool Escape::startRow(const EscapeSample& sample, bool replacement) {
    const auto mask = static_cast<std::uint8_t>(sample.line_mask & 0x0FU);
    const auto rear = static_cast<std::uint8_t>(mask & 0x0CU);
    if (!replacement) {
        if (!std::isfinite(sample.heading_deg)) {
            latchFault(EscapeFault::INVALID_CONTEXT);
            return false;
        }
        last_heading_deg_ = sample.heading_deg;
    }
    bool pushed = false;
    if (rear != 0U && sample.centered_front) {
        if (!validAppliedDuty(sample.applied_duty_l) || !validAppliedDuty(sample.applied_duty_r)) {
            latchFault(EscapeFault::INVALID_CONTEXT);
            return false;
        }
        pushed = sample.applied_duty_l > 0.0F && sample.applied_duty_r > 0.0F;
    }
    if ((mask == 0x03U || (pushed && rear == 0x0CU)) && !validDirection(sample.opponent_side)) {
        latchFault(EscapeFault::INVALID_CONTEXT);
        return false;
    }
    motion::Direction direction = (mask & 0x01U) != 0U ?
        motion::Direction::RIGHT : motion::Direction::LEFT;
    if (mask == 0x03U) direction = sample.opponent_side;
    if (pushed) {
        direction = rear == 0x04U || (rear == 0x0CU && sample.opponent_side == motion::Direction::LEFT) ?
            motion::Direction::RIGHT : motion::Direction::LEFT;
    }
    const bool started = pushed ? row_.startPushedOut(sample.t_us, last_heading_deg_, sample.imu_ok, direction) :
        (mask == 0x03U ? row_.startHeadOn(sample.t_us, last_heading_deg_, sample.imu_ok, direction) :
                        row_.start(sample.t_us, mask, last_heading_deg_, sample.imu_ok));
    if (!started) {
        latchFault(EscapeFault::INVALID_CONTEXT);
        return false;
    }
    const bool timed_out = current_.turn_timed_out;
    current_ = row_.step(sample.t_us, sample.heading_deg, sample.imu_ok);
    current_.turn_timed_out = current_.turn_timed_out || timed_out;
    if (current_.motion.status == motion::Status::INVALID) {
        latchFault(EscapeFault::INVALID_CONTEXT);
        return false;
    }
    selected_mask_ = mask;
    pushed_out_ = pushed;
    pivot_direction_ = direction;
    active_ = true;
    if (replacement) ++replans_;
    return true;
}

bool Escape::needsReplan(std::uint8_t new_bits) const {
    if (current_.phase == ScriptPhase::PIVOT) {
        const std::uint8_t turning_side = pivot_direction_ == motion::Direction::LEFT ? 0x05U : 0x0AU;
        return (new_bits & turning_side) != 0U;
    }
    return runningPhase(current_.phase) && new_bits != 0U;
}

bool Escape::advanceRow(const EscapeSample& sample, std::uint8_t new_bits) {
    if (sample.imu_ok && !std::isfinite(sample.heading_deg)) {
        latchFault(EscapeFault::INVALID_CONTEXT);
        return false;
    }
    if (sample.imu_ok) last_heading_deg_ = sample.heading_deg;
    // New bits use the entry phase, before this observation advances a primitive.
    bool replacement = needsReplan(new_bits);
    if (!replacement) {
        current_ = row_.step(sample.t_us, sample.heading_deg, sample.imu_ok);
        if (current_.motion.status == motion::Status::INVALID) {
            latchFault(EscapeFault::INVALID_CONTEXT);
            return false;
        }
        replacement = current_.phase == ScriptPhase::DONE && (sample.line_mask & 0x0FU) != 0U;
    }
    if (!replacement) return false;
    if (replans_ >= config::EDGE_MAX_REPLANS) {
        latchFault(EscapeFault::REPLAN_LIMIT);
        return false;
    }
    return startRow(sample, true);
}

void Escape::latchFault(EscapeFault fault) {
    if (fault_ == EscapeFault::NONE) fault_ = fault;
    active_ = true;
    const bool timed_out = current_.turn_timed_out;
    const bool changed = current_.phase != ScriptPhase::INVALID;
    current_ = RowResult{};
    current_.phase = ScriptPhase::INVALID;
    current_.motion.status = motion::Status::INVALID;
    current_.phase_changed = changed;
    current_.turn_timed_out = timed_out;
}

EscapeResult Escape::result(bool permitted) const {
    EscapeResult out;
    out.row = !permitted && fault_ == EscapeFault::NONE ? RowResult{} : current_;
    out.fault = fault_;
    out.escape_required = permitted && active_;
    out.inhibit_motion = !permitted || fault_ != EscapeFault::NONE;
    out.replans = replans_;
    out.selected_mask = selected_mask_;
    out.pushed_out = pushed_out_;
    out.pivot_direction = pivot_direction_;
    return out;
}

EscapeResult Escape::step(const EscapeSample& sample) {
    current_.phase_changed = false;
    current_.turn_timed_out = false;
    if (!sample.motion_permitted) {
        if (active_ && fault_ == EscapeFault::NONE) latchFault(EscapeFault::PERMISSION_LOST);
        guard_.step(sample.line_mask, false, false);
        return result(false);
    }
    if (fault_ != EscapeFault::NONE) return result(true);
    const auto mask = static_cast<std::uint8_t>(sample.line_mask & 0x0FU);
    const auto new_bits = static_cast<std::uint8_t>(mask & ~previous_mask_);
    const bool entered = !active_ && mask != 0U;
    bool replanned = false;
    if (faultPattern(mask)) {
        latchFault(EscapeFault::WHITE_PATTERN);
    } else if (!active_) {
        current_ = RowResult{};
        if (mask != 0U) startRow(sample, false);
    } else {
        replanned = advanceRow(sample, new_bits);
    }
    previous_mask_ = mask;
    const GuardResult guarded = guard_.step(mask, true, current_.phase == ScriptPhase::DONE);
    const bool exited = active_ && fault_ == EscapeFault::NONE && !guarded.escape_required;
    if (exited) {
        active_ = false;
        replans_ = 0U;
    }
    EscapeResult out = result(true);
    out.entered = entered;
    out.exited = exited;
    out.replanned = replanned;
    if (exited && sample.imu_ok && std::isfinite(sample.heading_deg)) {
        out.inward_valid = true;
        out.inward_heading_deg = sample.heading_deg;
    }
    return out;
}

void Escape::reset() {
    *this = Escape{};
}
} // namespace edge
