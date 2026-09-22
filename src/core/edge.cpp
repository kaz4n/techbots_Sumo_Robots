// Classifies B4 white, guards persistent edges and executes selected escape rows.
// Keeps specified motion requests separate from row selection and motor permission.
// Locked host tests cover masks, guard composition, row timing and mirror symmetry.
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

float turnHeading(float heading_deg) {
    // Reduce before adding a relative turn so extreme finite yaw keeps the angle.
    double heading = std::fmod(static_cast<double>(heading_deg), 360.0);
    if (heading > 180.0) heading -= 360.0;
    if (heading <= -180.0) heading += 360.0;
    return static_cast<float>(heading);
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
                                  config::EDGE_BACK_MS);
        break;
    case ScriptPhase::PIVOT: {
        const float heading = turnHeading(last_heading_deg_);
        started = turn_.start(t_us, heading, heading + pivot_deg_,
                              config::TURN_DUTY, imu_ok);
        break;
    }
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
        return turn_.step(t_us, imu_ok ? turnHeading(heading_deg) : 0.0F, imu_ok);
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
} // namespace edge
