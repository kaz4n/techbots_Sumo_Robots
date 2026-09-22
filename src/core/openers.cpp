// Implements B12 DIRECT and mirrored SIDESTEP/ARC scripts with B7 primitives.
// Reports transition intents so global arbitration retains all safety authority.
// Independent host tests check phases, priorities, timing, snapshots and mirrors.
#include "openers.h"
#include "../config.h"
#include <cmath>

namespace openers {
namespace {
Result terminal(Exit exit) {
    Result result;
    result.exit = exit;
    result.motion.status = exit == Exit::INVALID ? motion::Status::INVALID :
                           exit == Exit::NONE ? motion::Status::IDLE : motion::Status::DONE;
    return result;
}

float normalizedHeading(float heading_deg) {
    if (!std::isfinite(heading_deg)) return heading_deg;
    double angle = std::fmod(static_cast<double>(heading_deg), 360.0);
    if (angle <= -180.0) angle += 360.0;
    if (angle > 180.0) angle -= 360.0;
    const float result = static_cast<float>(angle);
    return result <= -180.0F ? 180.0F : result;
}

std::uint8_t innerMask(float mirror) {
    return mirror > 0.0F ? 0x28U : 0x50U;
}
} // namespace

bool Direct::start(std::uint32_t t_us, float heading_deg,
                   std::uint8_t countdown_snapshot) {
    active_ = straight_.start(t_us, heading_deg, config::OPENER_DUTY_MAX, config::DIRECT_MS);
    exit_ = active_ ? Exit::NONE : Exit::INVALID;
    snapshot_ = static_cast<std::uint8_t>(countdown_snapshot & 0x7FU);
    return active_;
}

Result Direct::step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                    std::uint8_t confirmed_opp_mask) {
    if (!active_) return terminal(exit_);
    if (((confirmed_opp_mask | snapshot_) & 0x07U) != 0U) {
        exit_ = Exit::FRONT_TARGET;
    } else if ((confirmed_opp_mask & 0x78U) != 0U) {
        exit_ = Exit::SIDE_OR_REAR_TARGET;
    }
    snapshot_ = 0U;
    if (exit_ != Exit::NONE) {
        active_ = false;
        return terminal(exit_);
    }
    Result result;
    result.motion = straight_.step(t_us, heading_deg, imu_ok);
    if (result.motion.status == motion::Status::DONE) exit_ = Exit::SEARCH;
    if (result.motion.status == motion::Status::INVALID) exit_ = Exit::INVALID;
    result.exit = exit_;
    active_ = exit_ == Exit::NONE;
    return result;
}

void Direct::reset() { *this = Direct{}; }

const Flank::Definition& Flank::definition() const {
    static constexpr Definition definitions[] = {
        {static_cast<float>(config::SS_PIVOT_DEG), config::OPENER_DUTY_MAX,
         config::SS_DRIVE_MS, static_cast<float>(config::SS_TURNIN_DEG), false},
        {static_cast<float>(config::ARC_PIVOT_DEG), config::ARC_DUTY,
         config::ARC_MAX_MS, 0.0F, true}
    };
    return definitions[arc_mode_ ? 1U : 0U];
}

bool Flank::start(std::uint32_t t_us, float heading_deg, bool imu_ok,
                   core::Mode mode) {
    reset();
    if (!std::isfinite(heading_deg) ||
        (mode != core::Mode::SIDESTEP_R && mode != core::Mode::SIDESTEP_L &&
         mode != core::Mode::ARC_R && mode != core::Mode::ARC_L)) {
        finish(Exit::INVALID);
        return false;
    }
    arc_mode_ = mode == core::Mode::ARC_R || mode == core::Mode::ARC_L;
    mirror_ = mode == core::Mode::SIDESTEP_L || mode == core::Mode::ARC_L ? -1.0F : 1.0F;
    last_heading_deg_ = heading_deg;
    if (!beginTurn(t_us, mirror_ * definition().pivot_deg, imu_ok)) {
        finish(Exit::INVALID);
        return false;
    }
    phase_ = Phase::PIVOT;
    return true;
}

bool Flank::beginTurn(std::uint32_t t_us, float relative_deg, bool imu_ok) {
    // Normalize first: adding a small offset to a huge finite yaw loses it.
    const float heading = normalizedHeading(last_heading_deg_);
    const float target = normalizedHeading(heading + relative_deg);
    return turn_.start(t_us, heading, target, config::TURN_DUTY, imu_ok);
}

bool Flank::beginTraverse(std::uint32_t t_us) {
    const Definition& script = definition();
    const auto inner = mirror_ > 0.0F ? motion::Direction::LEFT : motion::Direction::RIGHT;
    const bool started = script.arc ?
        arc_.start(t_us, last_heading_deg_, inner, config::ARC_RATIO,
                   script.traverse_duty, static_cast<float>(config::ARC_SWEEP_DEG),
                   script.traverse_ms) :
        straight_.start(t_us, last_heading_deg_, script.traverse_duty, script.traverse_ms);
    if (started) phase_ = Phase::TRAVERSE;
    return started;
}

bool Flank::beginTurnIn(const Sample& sample) {
    float relative_deg = -mirror_ * definition().turn_in_deg;
    if (arc_mode_) {
        if (!sample.bearing_valid || !std::isfinite(sample.bearing_deg) ||
            sample.bearing_deg <= -180.0F || sample.bearing_deg > 180.0F) {
            return false;
        }
        relative_deg = sample.bearing_deg;
    }
    const bool started = beginTurn(sample.t_us, relative_deg, sample.imu_ok);
    if (started) phase_ = Phase::TURN_IN;
    return started;
}

Exit Flank::detectExit(std::uint8_t mask) const {
    if (phase_ != Phase::PIVOT && (mask & 0x07U) != 0U) {
        return Exit::FRONT_TARGET;
    }
    const auto outer_mask = innerMask(-mirror_);
    if (!arc_mode_ && (mask & outer_mask) != 0U) {
        return Exit::SIDE_OR_REAR_TARGET;
    }
    return Exit::NONE;
}

Exit Flank::currentTarget(std::uint8_t mask) const {
    if ((mask & 0x07U) != 0U) return Exit::FRONT_TARGET;
    if ((mask & 0x78U) != 0U) return Exit::SIDE_OR_REAR_TARGET;
    return Exit::SEARCH;
}

void Flank::finish(Exit exit) {
    exit_ = exit;
    phase_ = exit == Exit::INVALID ? Phase::INVALID : Phase::FINISHED;
}

motion::Result Flank::runMotion(const Sample& sample) {
    if (phase_ == Phase::PIVOT || phase_ == Phase::TURN_IN) {
        return turn_.step(sample.t_us, normalizedHeading(sample.heading_deg), sample.imu_ok);
    }
    if (arc_mode_) {
        return arc_.step(sample.t_us, sample.heading_deg, sample.imu_ok);
    }
    return straight_.step(sample.t_us, sample.heading_deg, sample.imu_ok);
}

bool Flank::advancePhase(const Sample& sample) {
    if (phase_ == Phase::PIVOT) return beginTraverse(sample.t_us);
    if (phase_ == Phase::TRAVERSE) {
        if (arc_mode_ && (sample.confirmed_mask & 0x7FU) == 0U) {
            finish(Exit::SEARCH);
            return true;
        }
        return beginTurnIn(sample);
    }
    finish(currentTarget(sample.confirmed_mask));
    return true;
}

FlankResult Flank::result() const {
    FlankResult output;
    output.motion = terminal(exit_).motion;
    output.exit = exit_;
    output.phase = phase_;
    if (phase_ == Phase::PIVOT || phase_ == Phase::TURN_IN) {
        output.profile = governor::Profile::PIVOT;
    }
    output.scan_hint_valid = !arc_mode_ && exit_ == Exit::SEARCH;
    output.scan_direction = mirror_ > 0.0F ? motion::Direction::LEFT : motion::Direction::RIGHT;
    return output;
}

FlankResult Flank::step(const Sample& sample) {
    if (phase_ == Phase::IDLE || phase_ == Phase::FINISHED || phase_ == Phase::INVALID) {
        return result();
    }
    if (sample.imu_ok && std::isfinite(sample.heading_deg)) {
        last_heading_deg_ = sample.heading_deg;
    }
    const Phase initial_phase = phase_;
    bool timed_out = false;
    motion::Result demand;
    // Monotonic phases permit at most PIVOT, TRAVERSE, TURN_IN in one call.
    for (std::uint32_t visit = 0U; visit < 3U; ++visit) {
        const Exit detected = detectExit(sample.confirmed_mask);
        if (detected != Exit::NONE) {
            finish(detected);
            break;
        }
        if (phase_ == Phase::TRAVERSE && (sample.confirmed_mask & innerMask(mirror_)) != 0U) {
            if (!beginTurnIn(sample)) {
                finish(Exit::INVALID);
                break;
            }
            continue;
        }
        demand = runMotion(sample);
        if (demand.status == motion::Status::INVALID) {
            finish(Exit::INVALID);
            break;
        }
        if (demand.status != motion::Status::DONE && demand.status != motion::Status::TIMED_OUT) {
            break;
        }
        timed_out = timed_out || demand.status == motion::Status::TIMED_OUT;
        if (!advancePhase(sample)) finish(Exit::INVALID);
        if (phase_ == Phase::FINISHED || phase_ == Phase::INVALID) break;
    }
    FlankResult output = result();
    if (exit_ == Exit::NONE) output.motion = demand;
    output.phase_changed = phase_ != initial_phase;
    output.motion_timed_out = timed_out;
    return output;
}

void Flank::reset() { *this = Flank{}; }
} // namespace openers
