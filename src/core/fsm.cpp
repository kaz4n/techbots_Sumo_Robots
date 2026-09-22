// Implements B8 search, B9 front requests and bounded B10/B11 motion scripts.
// Keeps request math and captured commands separate from motor authorization.
// Independent host tests cover table rows, capture, caps, deadlines and wrap.
#include "fsm.h"
#include "opp_fusion.h"
#include "../config.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace fsm {
namespace {
static_assert(config::DEFEND_EVADE_FIRST == 0U,
              "Defensive evade requires its P4-backed implementation");
static_assert(config::DEFEND_TIMEOUT_MS <=
              std::numeric_limits<std::uint32_t>::max() / 1000U,
              "Defend duration must fit uint32 microseconds");
static_assert(config::RECENT_EDGE_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U);
static_assert(config::SEARCH_SCAN_DEG > 0U && config::TURN_MS_PER_DEG > 0.0F);

float normalizedHeading(float heading_deg) {
    if (!std::isfinite(heading_deg)) return heading_deg;
    double angle = std::fmod(static_cast<double>(heading_deg), 360.0);
    if (angle <= -180.0) angle += 360.0;
    if (angle > 180.0) angle -= 360.0;
    const float result = static_cast<float>(angle);
    return result <= -180.0F ? 180.0F : result;
}

bool validDirection(motion::Direction direction) {
    return direction == motion::Direction::LEFT || direction == motion::Direction::RIGHT;
}

bool runningSearch(SearchPhase phase) {
    return phase == SearchPhase::MEMORY_TURN || phase == SearchPhase::SCAN ||
           phase == SearchPhase::ADVANCE;
}

motion::Direction oppositeDirection(motion::Direction direction) {
    return direction == motion::Direction::RIGHT ? motion::Direction::LEFT :
                                                  motion::Direction::RIGHT;
}

} // namespace

FrontQualificationResult FrontQualification::observe(std::uint8_t effective_mask) {
    const auto view = opp_fusion::frontView(effective_mask);
    if (!view.centered) {
        centered_ticks_ = 0U;
    } else if (centered_ticks_ < config::ATTACK_ENTER_TICKS) {
        ++centered_ticks_;
    }
    return {view.detected, view.centered,
            view.centered && centered_ticks_ >= config::ATTACK_ENTER_TICKS};
}

void FrontQualification::reset() { centered_ticks_ = 0U; }

NormalResult NormalPerception::step(std::uint8_t effective_mask) {
    const auto front = qualification_.observe(effective_mask);
    NormalResult result;
    result.front_detected = front.front_detected;
    result.centered = front.centered;
    result.brake = front_active_ && !front.front_detected;
    if (front.front_detected) {
        result.state = front.attack_eligible ? core::State::ATTACK : core::State::TRACK;
    } else if ((effective_mask & 0x78U) != 0U) {
        result.state = core::State::DEFEND_TURN;
    }
    front_active_ = front.front_detected;
    return result;
}

void NormalPerception::reset() {
    qualification_.reset();
    front_active_ = false;
}

FrontDemand frontDemand(core::State state, std::uint8_t effective_mask, bool contact) {
    FrontDemand result;
    const auto view = opp_fusion::frontView(effective_mask);
    const bool attack = state == core::State::ATTACK;
    if (!view.detected || (state != core::State::TRACK && !attack) ||
        (attack && !view.centered)) return result;
    float base = config::TRACK_DUTY;
    float correction = config::K_TRACK_PER_DEG * view.bearing_deg;
    if (attack) {
        base = contact ? config::ATTACK_DUTY : config::ATTACK_APPROACH_DUTY;
        const float limit = std::min(config::TURN_MIN_DUTY, base);
        correction = std::clamp(correction, -limit, limit);
        result.profile = governor::Profile::ATTACK;
    } else if (std::fabs(view.bearing_deg) == 15.0F) {
        // These two discrete B5 rows receive the specifically approved pivot.
        correction += std::copysign(config::TURN_MIN_DUTY, view.bearing_deg);
    }
    result.duty_l = std::clamp(base + correction, -1.0F, 1.0F);
    result.duty_r = std::clamp(base - correction, -1.0F, 1.0F);
    result.valid = true;
    return result;
}

void SearchSide::observe(float relative_bearing_deg, bool valid) {
    if (!valid || !std::isfinite(relative_bearing_deg) || relative_bearing_deg <= -180.0F ||
        relative_bearing_deg > 180.0F || relative_bearing_deg == 0.0F) return;
    direction_ = relative_bearing_deg > 0.0F ? motion::Direction::RIGHT :
                                             motion::Direction::LEFT;
}

motion::Direction SearchSide::direction() const { return direction_; }

void SearchSide::reset() { direction_ = motion::Direction::RIGHT; }

bool Search::start(std::uint32_t t_us, float heading_deg, bool imu_ok,
                    const SearchContext& context) {
    reset();
    phase_ = SearchPhase::INVALID;
    intent_ = Intent::INVALID;
    if (!std::isfinite(heading_deg) || !validDirection(context.last_side) ||
        (context.scan_hint_valid && !validDirection(context.scan_hint))) return false;
    const bool recent_world = context.world_valid && context.world_age_us <
        static_cast<std::uint64_t>(config::SEARCH_MEMORY_MS) * 1000U;
    if (recent_world && (!std::isfinite(context.world_bearing_deg) ||
        context.world_bearing_deg <= -180.0F || context.world_bearing_deg > 180.0F)) return false;
    const std::uint32_t inward_lifetime_us = config::RECENT_EDGE_MS * 1000U;
    if (context.inward_valid && context.inward_age_us < inward_lifetime_us) {
        if (!std::isfinite(context.inward_heading_deg)) return false;
        inward_remaining_us_ = inward_lifetime_us - static_cast<std::uint32_t>(context.inward_age_us);
        inward_heading_deg_ = context.inward_heading_deg;
    }
    last_us_ = t_us;
    last_heading_deg_ = heading_deg;
    scan_direction_ = context.last_side;
    const float heading = normalizedHeading(heading_deg);
    if (recent_world) {
        // Match B7's widened error before choosing a side near the 180-degree tie.
        double error = std::fmod(static_cast<double>(context.world_bearing_deg) - heading, 360.0);
        if (error <= -180.0) error += 360.0;
        if (error > 180.0) error -= 360.0;
        if (error != 0.0) scan_direction_ = error > 0.0 ? motion::Direction::RIGHT :
                                                                       motion::Direction::LEFT;
    }
    if (context.scan_hint_valid) scan_direction_ = context.scan_hint;
    if (recent_world) {
        if (!turn_.start(t_us, heading, context.world_bearing_deg, config::TURN_DUTY, imu_ok)) {
            return false;
        }
        phase_ = SearchPhase::MEMORY_TURN;
        intent_ = Intent::NONE;
        return true;
    }
    intent_ = Intent::NONE;
    return beginScan(t_us, imu_ok);
}

bool Search::beginScan(std::uint32_t t_us, bool imu_ok) {
    phase_ = SearchPhase::SCAN;
    scan_start_deg_ = last_heading_deg_;
    remaining_deg_ = static_cast<double>(config::SEARCH_SCAN_DEG);
    scan_fallback_ = !imu_ok;
    fallback_us_ = scan_fallback_ ? remaining_deg_ * config::TURN_MS_PER_DEG * 1000.0 : 0.0;
    scan_clock_.begin(t_us);
    return true;
}

bool Search::beginAdvance(std::uint32_t t_us) {
    const float reference = inward_remaining_us_ != 0U ? inward_heading_deg_ : last_heading_deg_;
    if (!straight_.start(t_us, reference, config::SEARCH_DUTY_MAX, config::SEARCH_ADVANCE_MS)) {
        phase_ = SearchPhase::INVALID;
        intent_ = Intent::INVALID;
        return false;
    }
    phase_ = SearchPhase::ADVANCE;
    return true;
}

motion::Result Search::runScan(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    if (!scan_fallback_ && imu_ok) {
        const double sign = scan_direction_ == motion::Direction::RIGHT ? 1.0 : -1.0;
        const double progress = sign * (static_cast<double>(heading_deg) - scan_start_deg_);
        const double sweep = static_cast<double>(config::SEARCH_SCAN_DEG);
        remaining_deg_ = std::clamp(sweep - progress, 0.0, sweep);
        if (progress >= sweep) return {0.0F, 0.0F, motion::Status::DONE, false};
    } else if (!scan_fallback_) {
        scan_fallback_ = true;
        fallback_us_ = remaining_deg_ * config::TURN_MS_PER_DEG * 1000.0;
        // The loss observation starts the fallback; previous valid scan time is irrelevant.
        scan_clock_.begin(t_us);
    }
    if (scan_fallback_) {
        scan_clock_.advance(t_us);
        if (static_cast<double>(scan_clock_.elapsed_us) >= fallback_us_) {
            return {0.0F, 0.0F, motion::Status::DONE, true};
        }
    }
    const float duty = scan_direction_ == motion::Direction::RIGHT ? config::SCAN_DUTY :
                                                                                -config::SCAN_DUTY;
    return {duty, -duty, motion::Status::ACTIVE, scan_fallback_};
}

motion::Result Search::runMotion(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    switch (phase_) {
    case SearchPhase::MEMORY_TURN:
        return turn_.step(t_us, imu_ok ? normalizedHeading(heading_deg) : 0.0F, imu_ok);
    case SearchPhase::SCAN: return runScan(t_us, heading_deg, imu_ok);
    case SearchPhase::ADVANCE: return straight_.step(t_us, heading_deg, imu_ok);
    default: return {};
    }
}

bool Search::advancePhase(std::uint32_t t_us, bool imu_ok) {
    switch (phase_) {
    case SearchPhase::MEMORY_TURN: return beginScan(t_us, imu_ok);
    case SearchPhase::SCAN: return beginAdvance(t_us);
    case SearchPhase::ADVANCE:
        scan_direction_ = scan_direction_ == motion::Direction::RIGHT ?
            motion::Direction::LEFT : motion::Direction::RIGHT;
        return beginScan(t_us, imu_ok);
    default:
        phase_ = SearchPhase::INVALID;
        intent_ = Intent::INVALID;
        return false;
    }
}

SearchResult Search::result(const motion::Result& motion) const {
    SearchResult output;
    output.motion = motion;
    output.profile = phase_ == SearchPhase::ADVANCE ? governor::Profile::SEARCH_FORWARD :
                                                    governor::Profile::PIVOT;
    output.intent = intent_;
    output.phase = phase_;
    output.scan_direction = scan_direction_;
    if (!runningSearch(phase_)) {
        const motion::Status status = phase_ == SearchPhase::FINISHED ? motion::Status::DONE :
            (phase_ == SearchPhase::INVALID ? motion::Status::INVALID : motion::Status::IDLE);
        output.motion = {0.0F, 0.0F, status, false};
    }
    return output;
}

SearchResult Search::step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                          std::uint8_t effective_mask) {
    if (!runningSearch(phase_)) return result({});
    const SearchPhase previous_phase = phase_;
    motion::Result demand;
    bool timed_out = false;
    if ((effective_mask & 0x7FU) != 0U) {
        phase_ = SearchPhase::FINISHED;
        intent_ = Intent::PERCEPTION;
    } else if (imu_ok && !std::isfinite(heading_deg)) {
        phase_ = SearchPhase::INVALID;
        intent_ = Intent::INVALID;
    } else {
        const std::uint32_t elapsed_us = t_us - last_us_;
        last_us_ = t_us;
        inward_remaining_us_ -= std::min(inward_remaining_us_, elapsed_us);
        if (imu_ok) last_heading_deg_ = heading_deg;
        for (std::uint32_t phases = 0U; phases < 3U; ++phases) {
            demand = runMotion(t_us, heading_deg, imu_ok);
            if (demand.status == motion::Status::INVALID) {
                phase_ = SearchPhase::INVALID;
                intent_ = Intent::INVALID;
                break;
            }
            if (demand.status != motion::Status::DONE &&
                demand.status != motion::Status::TIMED_OUT) break;
            timed_out = timed_out || demand.status == motion::Status::TIMED_OUT;
            if (!advancePhase(t_us, imu_ok)) break;
        }
    }
    SearchResult output = result(demand);
    output.phase_changed = phase_ != previous_phase;
    output.turn_timed_out = timed_out;
    return output;
}

void Search::reset() { *this = Search{}; }

SwingChoice chooseSwing(const SwingContext& context) {
    if (context.edge_side_valid && context.edge_age_us <
        static_cast<std::uint64_t>(config::RECENT_EDGE_MS) * 1000U) {
        if (!validDirection(context.edge_side)) return {};
        return {oppositeDirection(context.edge_side), true};
    }
    if (context.front_left_seen != context.front_right_seen) {
        return {context.front_left_seen ? motion::Direction::RIGHT : motion::Direction::LEFT,
                true};
    }
    if (context.front_left_seen && context.front_left_age_us != context.front_right_age_us) {
        return {context.front_left_age_us > context.front_right_age_us ?
                motion::Direction::LEFT : motion::Direction::RIGHT, true};
    }
    if (!context.previous_swing_valid) return {motion::Direction::RIGHT, true};
    if (!validDirection(context.previous_swing)) return {};
    return {oppositeDirection(context.previous_swing), true};
}

bool Reflank::start(std::uint32_t t_us, float heading_deg, bool /*imu_ok*/,
                    motion::Direction direction) {
    reset();
    stage_ = Stage::INVALID;
    if (!std::isfinite(heading_deg) || !validDirection(direction)) return false;
    if (!back_.start(t_us, heading_deg, -config::REFLANK_BACK_DUTY,
                     config::REFLANK_BACK_MS)) return false;
    last_heading_deg_ = heading_deg;
    direction_ = direction;
    stage_ = Stage::BACK;
    return true;
}

bool Reflank::beginSwing(std::uint32_t t_us, bool imu_ok) {
    const float pivot = static_cast<float>(config::REFLANK_PIVOT_DEG) *
                        (direction_ == motion::Direction::RIGHT ? 1.0F : -1.0F);
    if (!turn_.startRelative(t_us, last_heading_deg_, pivot, config::TURN_DUTY, imu_ok)) {
        stage_ = Stage::INVALID;
        return false;
    }
    stage_ = Stage::PIVOT;
    return true;
}

bool Reflank::beginTurnIn(std::uint32_t t_us, bool imu_ok, float bearing_deg, bool valid) {
    if (!valid || !std::isfinite(bearing_deg) || bearing_deg <= -180.0F || bearing_deg > 180.0F) {
        stage_ = Stage::INVALID;
        return false;
    }
    if (!turn_.startRelative(t_us, last_heading_deg_, bearing_deg, config::TURN_DUTY, imu_ok)) {
        stage_ = Stage::INVALID;
        return false;
    }
    stage_ = Stage::TURN_IN;
    return true;
}

motion::Result Reflank::runMotion(std::uint32_t t_us, float heading_deg, bool imu_ok) {
    switch (stage_) {
    case Stage::BACK: return back_.step(t_us, heading_deg, imu_ok);
    case Stage::PIVOT: case Stage::TURN_IN:
        return turn_.step(t_us, heading_deg, imu_ok);
    case Stage::ARC: return arc_.step(t_us);
    default: return {};
    }
}

bool Reflank::advanceStage(std::uint32_t t_us, bool imu_ok) {
    switch (stage_) {
    case Stage::BACK: return beginSwing(t_us, imu_ok);
    case Stage::PIVOT:
        if (!arc_.start(t_us, oppositeDirection(direction_), config::REFLANK_ARC_RATIO,
                         config::TURN_DUTY, config::REFLANK_ARC_MS)) {
            stage_ = Stage::INVALID;
            return false;
        }
        stage_ = Stage::ARC;
        return true;
    case Stage::ARC: case Stage::TURN_IN:
        stage_ = Stage::FINISHED;
        return true;
    default:
        stage_ = Stage::INVALID;
        return false;
    }
}

ReflankResult Reflank::result(const motion::Result& motion) const {
    ReflankResult output;
    output.direction = direction_;
    output.motion = motion;
    switch (stage_) {
    case Stage::BACK:
        output.phase = ReflankPhase::BACK;
        output.profile = governor::Profile::REFLANK_BACK;
        return output;
    case Stage::PIVOT: case Stage::ARC:
        output.phase = ReflankPhase::SWING;
        return output;
    case Stage::TURN_IN:
        output.phase = ReflankPhase::TURN_IN;
        return output;
    case Stage::FINISHED:
        output.phase = ReflankPhase::FINISHED;
        output.intent = Intent::PERCEPTION;
        output.motion = {0.0F, 0.0F, motion::Status::DONE, false};
        return output;
    case Stage::INVALID:
        output.phase = ReflankPhase::INVALID;
        output.intent = Intent::INVALID;
        output.motion = {0.0F, 0.0F, motion::Status::INVALID, false};
        return output;
    default:
        output.motion = {};
        return output;
    }
}

ReflankResult Reflank::step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                           std::uint8_t effective_mask, bool contact_cue,
                           float bearing_deg, bool bearing_valid) {
    if (stage_ == Stage::IDLE || stage_ == Stage::FINISHED || stage_ == Stage::INVALID) return result({});
    const auto mask = static_cast<std::uint8_t>(effective_mask & 0x7FU);
    const bool front = (mask & 0x07U) != 0U;
    if (stage_ == Stage::TURN_IN && front) {
        stage_ = Stage::FINISHED;
        return result({});
    }
    if (imu_ok && !std::isfinite(heading_deg)) {
        stage_ = Stage::INVALID;
        return result({});
    }
    if (imu_ok) last_heading_deg_ = heading_deg;
    const std::uint8_t inner = direction_ == motion::Direction::RIGHT ? 0x28U : 0x50U;
    ReflankResult entries;
    motion::Result demand;
    for (std::uint32_t visits = 0U; visits < 4U; ++visits) {
        if (stage_ == Stage::TURN_IN && front) {
            stage_ = Stage::FINISHED;
            break;
        }
        if (stage_ == Stage::BACK && front && contact_cue) {
            entries.entered_swing = beginSwing(t_us, imu_ok);
            if (!entries.entered_swing) break;
            continue;
        }
        if ((stage_ == Stage::PIVOT || stage_ == Stage::ARC) && (mask & inner) != 0U) {
            entries.entered_turn_in = beginTurnIn(t_us, imu_ok, bearing_deg, bearing_valid);
            if (!entries.entered_turn_in) break;
            continue;
        }
        demand = runMotion(t_us, heading_deg, imu_ok);
        if (demand.status == motion::Status::INVALID) {
            stage_ = Stage::INVALID;
            break;
        }
        if (demand.status != motion::Status::DONE && demand.status != motion::Status::TIMED_OUT) break;
        entries.turn_timed_out = entries.turn_timed_out || demand.status == motion::Status::TIMED_OUT;
        const bool leaving_back = stage_ == Stage::BACK;
        if (!advanceStage(t_us, imu_ok)) break;
        entries.entered_swing = entries.entered_swing || leaving_back;
        if (stage_ == Stage::FINISHED) break;
    }
    ReflankResult output = result(demand);
    output.entered_swing = entries.entered_swing;
    output.entered_turn_in = entries.entered_turn_in;
    output.turn_timed_out = entries.turn_timed_out;
    return output;
}

void Reflank::reset() { *this = Reflank{}; }

bool DefendTurn::start(std::uint32_t t_us, float heading_deg, float bearing_deg,
                       bool bearing_valid, bool imu_ok) {
    reset();
    if (!std::isfinite(heading_deg) || !bearing_valid ||
        !std::isfinite(bearing_deg) || bearing_deg <= -180.0F || bearing_deg > 180.0F) {
        finish(Intent::INVALID);
        return false;
    }
    // Reduce yaw before adding the bearing so extreme finite yaw keeps offsets.
    const float heading = normalizedHeading(heading_deg);
    const float target = normalizedHeading(heading + bearing_deg);
    if (!turn_.start(t_us, heading, target, config::TURN_DUTY, imu_ok)) {
        finish(Intent::INVALID);
        return false;
    }
    interval_.begin(t_us);
    active_ = true;
    return true;
}

DefendResult DefendTurn::finish(Intent intent) {
    active_ = false;
    intent_ = intent;
    DefendResult result;
    result.intent = intent;
    result.motion.status = intent == Intent::INVALID ? motion::Status::INVALID :
        intent == Intent::NONE ? motion::Status::IDLE : motion::Status::DONE;
    return result;
}

DefendResult DefendTurn::step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                             std::uint8_t confirmed_mask) {
    if (!active_) return finish(intent_);
    const auto mask = static_cast<std::uint8_t>(confirmed_mask & 0x7FU);
    if ((mask & 0x07U) != 0U) return finish(Intent::PERCEPTION);
    if (mask == 0U) return finish(Intent::SEARCH);
    interval_.advance(t_us);
    if (interval_.elapsed_us >= config::DEFEND_TIMEOUT_MS * 1000U) {
        DefendResult result = finish(Intent::SEARCH);
        result.defend_timed_out = true;
        return result;
    }
    DefendResult result;
    result.motion = turn_.step(t_us, normalizedHeading(heading_deg), imu_ok);
    if (result.motion.status == motion::Status::INVALID) return finish(Intent::INVALID);
    if (result.motion.status == motion::Status::TIMED_OUT && !turn_timeout_reported_) {
        result.turn_timed_out = true;
        turn_timeout_reported_ = true;
    }
    // B7 terminal zero remains latched while B10 waits for perception or timeout.
    return result;
}

void DefendTurn::reset() { *this = DefendTurn{}; }
} // namespace fsm
