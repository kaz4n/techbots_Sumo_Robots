// Implements B12 DIRECT, SIDESTEP/ARC and ordered WAIT scripts with B7 primitives.
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
    return turn_.startRelative(t_us, last_heading_deg_, relative_deg,
                               config::TURN_DUTY, imu_ok);
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
        return turn_.step(sample.t_us, sample.heading_deg, sample.imu_ok);
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

bool Wait::start(std::uint32_t t_us, float heading_deg) {
    reset();
    if (!std::isfinite(heading_deg)) {
        finish(Exit::INVALID);
        return false;
    }
    last_heading_deg_ = heading_deg;
    hold_interval_.begin(t_us);
    phase_ = WaitPhase::HOLD;
    current_.motion.status = motion::Status::ACTIVE;
    return true;
}

bool Wait::observeApproach(std::uint32_t t_us, std::uint8_t mask) {
    const bool fc = (mask & 0x02U) != 0U;
    const auto new_flank = static_cast<std::uint8_t>(mask & ~previous_mask_ & 0x05U);
    bool cue = false;
    if (!fc) {
        fc_episode_ = false;
    } else if (!fc_episode_) {
        fc_episode_ = true;
        approach_interval_.begin(t_us);
    } else {
        approach_interval_.advance(t_us);
        cue = new_flank != 0U && approach_interval_.elapsed_us <=
            static_cast<std::uint64_t>(config::APPROACH_WINDOW_MS) * 1000U;
    }
    previous_mask_ = mask;
    return cue;
}

void Wait::finish(Exit exit) {
    current_ = {};
    current_.exit = exit;
    const bool invalid = exit == Exit::INVALID;
    current_.phase = invalid ? Phase::INVALID : Phase::FINISHED;
    current_.motion.status = invalid ? motion::Status::INVALID : motion::Status::DONE;
    phase_ = invalid ? WaitPhase::INVALID : WaitPhase::FINISHED;
}

void Wait::runFlank(const Sample& sample) {
    current_ = flank_.step(sample);
    if (current_.exit != Exit::NONE) {
        phase_ = current_.exit == Exit::INVALID ? WaitPhase::INVALID : WaitPhase::FINISHED;
    }
}

WaitResult Wait::result() const {
    WaitResult output;
    output.flank = current_;
    output.phase = phase_;
    output.brake = phase_ != WaitPhase::FLANK || current_.motion.status != motion::Status::ACTIVE;
    return output;
}

WaitResult Wait::step(const Sample& sample) {
    const WaitPhase previous = phase_;
    bool cue = false;
    current_.phase_changed = false;
    current_.motion_timed_out = false;
    if (phase_ == WaitPhase::FLANK) {
        runFlank(sample);
    } else if (phase_ == WaitPhase::HOLD) {
        hold_interval_.advance(sample.t_us);
        const auto mask = static_cast<std::uint8_t>(sample.confirmed_mask & 0x7FU);
        if ((mask & 0x78U) != 0U) {
            finish(Exit::SIDE_OR_REAR_TARGET);
        } else if (sample.imu_ok && !std::isfinite(sample.heading_deg)) {
            finish(Exit::INVALID);
        } else {
            if (sample.imu_ok) last_heading_deg_ = sample.heading_deg;
            if (observeApproach(sample.t_us, mask)) {
                if (flank_.start(sample.t_us, last_heading_deg_, sample.imu_ok,
                                 core::Mode::SIDESTEP_R)) {
                    cue = true;
                    phase_ = WaitPhase::FLANK;
                    runFlank(sample);
                } else {
                    finish(Exit::INVALID);
                }
            } else if (hold_interval_.elapsed_us >=
                       static_cast<std::uint64_t>(config::WAIT_MAX_MS) * 1000U) {
                finish(Exit::SEARCH);
            }
        }
    }
    WaitResult output = result();
    output.phase_changed = previous != phase_;
    output.approach_cue = cue;
    return output;
}

void Wait::reset() { *this = Wait{}; }
} // namespace openers
