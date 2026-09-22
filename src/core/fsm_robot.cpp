// Composes B0-B15 into the D-060 production Robot transaction.
// Keeps gate, edge and final contact authority separate from physical receipts.
// Independent Robot scenarios test boundaries, fault priority and recorder evidence.
#include "fsm.h"
#include <cmath>
#include <limits>

namespace fsm {
namespace {
constexpr std::uint64_t FRAME_PERIOD_US = 1000000ULL / config::LOG_HZ;
constexpr std::uint64_t FRAME_EPOCH_US = (1ULL << 32U) * 1000ULL;
static_assert(config::LOG_HZ > 0U && 1000000U % config::LOG_HZ == 0U);
static_assert(config::EDGE_MAX_REPLANS <= 255U);
static_assert(config::REFLANK_MAX_PER_10S <= 65535U);
static_assert(config::QTR_STUCK_MS < std::numeric_limits<std::uint32_t>::max() / 1000U);

std::uint32_t ageTo(std::uint32_t age, std::uint32_t delta, std::uint32_t limit) {
    const auto sum = static_cast<std::uint64_t>(age) + delta;
    return sum < limit ? static_cast<std::uint32_t>(sum) : limit;
}

std::uint64_t ageForever(std::uint64_t age, std::uint32_t delta) {
    const auto maximum = std::numeric_limits<std::uint64_t>::max();
    return maximum - age < delta ? maximum : age + delta;
}

bool moving(core::State state) {
    return state >= core::State::OPENER && state <= core::State::REFLANK;
}

bool validDuty(float duty) { return std::isfinite(duty) && duty >= -1.0F && duty <= 1.0F; }

bool allowedWheel(float actual, float requested) {
    return validDuty(actual) && (actual == 0.0F ||
        (actual > 0.0F && requested > 0.0F && actual <= requested) ||
        (actual < 0.0F && requested < 0.0F && actual >= requested));
}

bool validProfile(governor::Profile profile) {
    switch (profile) {
    case governor::Profile::SEARCH_FORWARD: case governor::Profile::PIVOT:
    case governor::Profile::OPENER: case governor::Profile::ATTACK:
    case governor::Profile::EDGE_REVERSE: case governor::Profile::REFLANK_BACK:
    case governor::Profile::REFLANK_TURN: case governor::Profile::EDGE_FORWARD:
        return true;
    }
    return false;
}

std::uint16_t dutyBytes(float left, float right) {
    const auto l = static_cast<std::int32_t>(std::round(static_cast<double>(left) * 127.0));
    const auto r = static_cast<std::int32_t>(std::round(static_cast<double>(right) * 127.0));
    return static_cast<std::uint16_t>(static_cast<std::uint8_t>(l)) |
           static_cast<std::uint16_t>(static_cast<std::uint8_t>(r) << 8U);
}

void clearActions(RobotResult& result) {
    result.fresh = false;
    result.lifecycle.gate.start_release = false;
    result.lifecycle.gate.go = false;
    result.lifecycle.heading_reset_requested = false;
    result.heading.origin_changed = false;
    result.menu.selection_changed = false;
    result.menu.menu_toggled = false;
    result.menu.request = countdown::Service::NONE;
    result.menu.request_unavailable = false;
    result.bias_update_requested = false;
    result.events = logframe::EventBatch{};
    result.frame_ready = false;
    result.frame_token = 0;
}
} // namespace

RobotResult Robot::step(const RobotInput& input) {
    if (observed_ && input.t_us == last_us_) {
        RobotResult duplicate = result_;
        clearActions(duplicate);
        return duplicate;
    }
    if (next_token_ == 0U) return exhaust(input);
    admit(input);
    receive(input);
    advanceHistories();
    prepareInputs(input);
    sampleSensors(input);
    runLifecycle(input);
    runEscape(input);
    routeMotion(input);
    checkStall();
    prepareFinalRequest();
    commitAndGovern(input);
    updateWarnings(input);
    finish(input);
    return result_;
}

void Robot::admit(const RobotInput& input) {
    clearActions(result_);
    tick_ = {};
    tick_.entry = state_;
    tick_.selected = state_;
    tick_.t_us = input.t_us;
    tick_.delta_us = observed_ ? input.t_us - last_us_ : 0U;
    tick_.request.brake = true;
    if (!observed_ && input.reset_cause == ResetCause::WATCHDOG)
        markFault(logframe::FaultCode::RESET_CAUSE, 1U);
    last_us_ = input.t_us;
    observed_ = true;
    result_.fresh = true;
    result_.token = next_token_;
    next_token_ = next_token_ == std::numeric_limits<std::uint64_t>::max() ? 0U : next_token_ + 1U;
}

void Robot::emit(std::uint32_t t_us, core::Event type, std::uint8_t detail,
                 std::uint16_t value) {
    if (!logframe::appendEvent(result_.events, {t_us, type, detail, value}))
        recording_incomplete_ = true;
}

void Robot::markFault(logframe::FaultCode code, std::uint16_t value) {
    const auto index = static_cast<std::uint8_t>(code);
    tick_.fault_events |= static_cast<std::uint16_t>(1U << index);
    tick_.fault_values[index] |= value;
}

void Robot::receive(const RobotInput& input) {
    if (!pending_.valid) return;
    const auto& receipt = input.previous;
    const std::uint32_t gap = input.t_us - pending_.t_us;
    const bool identity_time = receipt.applied_valid && receipt.token == pending_.token &&
        receipt.applied_us - pending_.t_us <= gap;
    const bool applied = identity_time &&
        (!receipt.motors_enabled || pending_.requested.motors_enabled) &&
        (receipt.motors_enabled || (receipt.duty_l == 0.0F && receipt.duty_r == 0.0F)) &&
        allowedWheel(receipt.duty_l, pending_.requested.duty_l) &&
        allowedWheel(receipt.duty_r, pending_.requested.duty_r);
    if (!applied) faults_ |= APPLICATION_CONTRACT;
    if (applied) {
        tick_.applied_enabled = receipt.motors_enabled;
        tick_.applied_l = receipt.duty_l;
        tick_.applied_r = receipt.duty_r;
        if (pending_.after_go && !first_nonzero_ && receipt.motors_enabled &&
            (receipt.duty_l != 0.0F || receipt.duty_r != 0.0F)) {
            const auto mask = static_cast<std::uint8_t>((receipt.duty_l != 0.0F ? 1U : 0U) |
                                                      (receipt.duty_r != 0.0F ? 2U : 0U));
            emit(receipt.applied_us, core::Event::FIRST_NONZERO_DUTY, mask,
                 dutyBytes(receipt.duty_l, receipt.duty_r));
            first_nonzero_ = true;
        }
    }
    receiveTiming(input, identity_time);
    receiveFrame(receipt, applied);
    pending_.valid = false;
}

void Robot::receiveTiming(const RobotInput& input, bool identity_time_valid) {
    if (!pending_.match_tick) return;
    const auto& receipt = input.previous;
    const bool before_rate = logframe::overrunRateExceeded(statistics_);
    const bool before_saturated = statistics_.saturated;
    const bool before_incomplete = timing_incomplete_;
    const std::uint32_t applied_offset = receipt.applied_us - pending_.t_us;
    const std::uint32_t completed_offset = receipt.completed_us - pending_.t_us;
    const bool valid = identity_time_valid && receipt.duration_valid &&
        completed_offset >= applied_offset && completed_offset <= input.t_us - pending_.t_us &&
        receipt.execution_us == completed_offset;
    if (valid) logframe::observeTick(statistics_, receipt.execution_us);
    else timing_incomplete_ = true;
    const std::uint16_t flags = static_cast<std::uint16_t>(
        (!before_rate && logframe::overrunRateExceeded(statistics_) ? 1U : 0U) |
        (!before_saturated && statistics_.saturated ? 2U : 0U) |
        (!before_incomplete && timing_incomplete_ ? 4U : 0U));
    if (flags != 0U) emit(valid ? receipt.completed_us : input.t_us, core::Event::FAULT,
                         static_cast<std::uint8_t>(logframe::FaultCode::TICK_STATISTICS), flags);
}

void Robot::receiveFrame(const PreviousTick& receipt, bool applied_valid) {
    if (!pending_.frame_due) return;
    if (!applied_valid) {
        skipped_frames_ = logframe::saturatingIncrement(skipped_frames_);
        recording_incomplete_ = true;
        return;
    }
    pending_.frame.duty_l = receipt.duty_l;
    pending_.frame.duty_r = receipt.duty_r;
    pending_.frame.tick_max_us = statistics_.max_us;
    result_.frame_status = logframe::packFrame(pending_.frame, result_.frame);
    result_.frame_ready = true;
    result_.frame_token = pending_.token;
    if (result_.frame_status != logframe::PackStatus::OK) recording_incomplete_ = true;
}

void Robot::advanceHistories() {
    world_age_us_ = ageTo(world_age_us_, tick_.delta_us, config::SEARCH_MEMORY_MS * 1000U);
    inward_age_us_ = ageTo(inward_age_us_, tick_.delta_us, config::RECENT_EDGE_MS * 1000U);
    edge_age_us_ = ageTo(edge_age_us_, tick_.delta_us, config::RECENT_EDGE_MS * 1000U);
    for (unsigned i = 0; i < 2U; ++i)
        front_age_us_[i] = ageForever(front_age_us_[i], tick_.delta_us);
    if (recording_) {
        record_elapsed_us_ = (record_elapsed_us_ + tick_.delta_us) % FRAME_EPOCH_US;
        frame_age_us_ += tick_.delta_us;
    }
}

void Robot::prepareInputs(const RobotInput& input) {
    initialized_ = initialized_ || input.initialization_complete;
    if (initialized_ && !input.observations_fresh) faults_ |= STALE_SENSORS;
    if (initialized_ && (!input.vbat_valid || !std::isfinite(input.vbat_v)))
        faults_ |= INVALID_CONTEXT;
    if (input.imu_ok && !std::isfinite(input.raw_heading_deg)) faults_ |= HEADING_CONTRACT;
    if (input.imu_ok && result_.heading.match_started &&
        result_.heading.origin != HeadingOrigin::NOMINAL_PENDING &&
        !heading_.projectHeading(input.raw_heading_deg).valid) faults_ |= HEADING_CONTRACT;
}

void Robot::sampleSensors(const RobotInput& input) {
    if (!input.observations_fresh) return;
    result_.line_mask = classifier_.observe(input.line_raw_us);
    tick_.new_white = static_cast<std::uint8_t>(result_.line_mask & ~previous_line_);
    previous_line_ = result_.line_mask;
    tick_.observation = fusion_.observe({input.t_us, input.opp_raw_mask, tick_.entry,
        input.raw_heading_deg, input.ax_g, input.ay_g, input.imu_ok, tick_.new_white != 0U});
    tick_.sampled = tick_.observation.fresh;
    if (!tick_.sampled && initialized_) faults_ |= STALE_SENSORS;
    result_.opponent_mask = tick_.observation.phantom.filtered_mask;
    result_.opponent_fault_mask = tick_.observation.stuck.fault_mask;
    if (tick_.observation.stuck.new_fault_mask != 0U)
        markFault(logframe::FaultCode::OPPONENT_STUCK, tick_.observation.stuck.new_fault_mask);
    if (tick_.sampled) rememberObservation();
}

void Robot::rememberObservation() {
    const auto& bearing = tick_.observation.bearing;
    side_.observe(bearing.relative_deg, bearing.bearing_valid);
    if (bearing.detected && bearing.bearing_valid) {
        world_seen_ = true;
        world_age_us_ = 0;
    }
    const auto front = static_cast<std::uint8_t>(result_.opponent_mask & 5U);
    const auto rising = static_cast<std::uint8_t>(front & ~previous_front_);
    for (unsigned i = 0; i < 2U; ++i) {
        if ((rising & (i == 0U ? 1U : 4U)) != 0U) {
            front_seen_[i] = true;
            front_age_us_[i] = 0;
        }
    }
    previous_front_ = front;
}

void Robot::beginAttempt() {
    running_mode_ = menu_.selection().mode;
    statistics_ = {};
    skipped_frames_ = 0;
    timing_incomplete_ = false;
    recording_incomplete_ = false;
    calibration_reported_ = false;
    bias_reported_ = false;
    recording_ = true;
    timing_active_ = false;
    attempt_go_ = false;
    first_nonzero_ = false;
    record_elapsed_us_ = 0;
    frame_age_us_ = 0;
    tick_.frame_immediate = true;
}

void Robot::runLifecycle(const RobotInput& input) {
    const bool allow_start = tick_.entry == core::State::IDLE && initialized_ &&
        faults_ == 0U && !menu_.selection().service_menu;
    const countdown::ServiceSample sample{input.t_us, input.raw_gyro_z_dps, input.imu_ok,
        result_.line_mask, tick_.sampled ? tick_.observation.confirmed_mask : std::uint8_t{0}};
    result_.lifecycle = lifecycle_.step(sample, input.button, input.previous_bias_dps,
                                        input.stop_requested || faults_ != 0U, allow_start);
    if (result_.lifecycle.gate.start_release) beginAttempt();
    const auto& services = result_.lifecycle.services;
    if (!calibration_reported_ &&
        (services.calibration_rejected || result_.lifecycle.service_start_failed)) {
        markFault(logframe::FaultCode::CALIBRATION, static_cast<std::uint16_t>(
            (services.calibration_rejected ? 1U : 0U) |
            (result_.lifecycle.service_start_failed ? 2U : 0U)));
        calibration_reported_ = true;
    }
    if (services.calibration_finished && !services.calibration_rejected && !bias_reported_) {
        result_.bias_update_requested = true;
        result_.accepted_bias_dps = services.bias_dps;
        bias_reported_ = true;
    }
    result_.heading = heading_.step(input.t_us, input.raw_heading_deg, input.imu_ok,
                                    result_.lifecycle.gate.go);
    if (result_.heading.fault) faults_ |= HEADING_CONTRACT;
    if (result_.lifecycle.gate.go) {
        attempt_go_ = true;
        timing_active_ = true;
    }
    tick_.permission = initialized_ && result_.lifecycle.gate.motion_permitted && faults_ == 0U;
    if (faults_ != 0U || result_.lifecycle.gate.phase == countdown::Phase::STOPPED)
        tick_.selected = core::State::STOPPED;
    else if (!initialized_) tick_.selected = core::State::BOOT;
    else if (result_.lifecycle.gate.phase == countdown::Phase::HOLDING)
        tick_.selected = core::State::COUNTDOWN;
    else if (result_.lifecycle.gate.phase == countdown::Phase::IDLE)
        tick_.selected = core::State::IDLE;
    tick_.limit = limiter_.step(input.t_us);
}

void Robot::runEscape(const RobotInput& input) {
    if (!tick_.sampled) return;
    const edge::EscapeSample sample{input.t_us, result_.line_mask,
        result_.heading.heading_deg, result_.heading.imu_ok, tick_.permission,
        tick_.observation.bearing.centered, tick_.applied_l, tick_.applied_r, side_.direction()};
    tick_.escape = escape_.step(sample);
    result_.escape_fault = tick_.escape.fault;
    if (tick_.escape.fault != edge::EscapeFault::NONE &&
        reported_escape_fault_ == edge::EscapeFault::NONE) {
        std::uint16_t reason = 0;
        switch (tick_.escape.fault) {
        case edge::EscapeFault::WHITE_PATTERN: reason = 1; break;
        case edge::EscapeFault::REPLAN_LIMIT: reason = 2; break;
        case edge::EscapeFault::PERMISSION_LOST: reason = 3; break;
        case edge::EscapeFault::INVALID_CONTEXT: reason = 4; break;
        case edge::EscapeFault::NONE: break;
        }
        markFault(logframe::FaultCode::ESCAPE_FAULT, reason);
        reported_escape_fault_ = tick_.escape.fault;
    }
    rememberEscape(input);
}

void Robot::rememberEscape(const RobotInput& input) {
    if (tick_.escape.entered) escape_sides_ = 0;
    if (tick_.escape.escape_required) {
        if ((result_.line_mask & 5U) != 0U) escape_sides_ |= 1U;
        if ((result_.line_mask & 10U) != 0U) escape_sides_ |= 2U;
    }
    if (!tick_.escape.exited) return;
    edge_side_valid_ = escape_sides_ == 1U || escape_sides_ == 2U;
    edge_side_ = escape_sides_ == 1U ? motion::Direction::LEFT : motion::Direction::RIGHT;
    edge_age_us_ = 0;
    if (tick_.escape.inward_valid && input.imu_ok && std::isfinite(input.raw_heading_deg)) {
        inward_valid_ = true;
        inward_raw_deg_ = input.raw_heading_deg;
        inward_age_us_ = 0;
    }
}

void Robot::cancelMotion() {
    normal_.reset();
    search_.reset();
    defend_.reset();
    reflank_.reset();
    direct_.reset();
    flank_.reset();
    wait_.reset();
    normal_active_ = false;
    search_active_ = false;
    defend_active_ = false;
    defend_pending_ = false;
    opener_active_ = false;
    reflank_active_ = false;
    scan_hint_valid_ = false;
}

void Robot::routeMotion(const RobotInput& input) {
    if (!tick_.permission) {
        cancelMotion();
        return;
    }
    if (tick_.escape.escape_required || tick_.escape.fault != edge::EscapeFault::NONE) {
        cancelMotion();
        tick_.selected = core::State::EDGE_ESCAPE;
        if (tick_.escape.fault == edge::EscapeFault::NONE)
            acceptMotion(tick_.escape.row.motion, tick_.escape.row.profile, tick_.escape.row.brake);
        if (tick_.escape.row.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 1U);
        return;
    }
    if (tick_.escape.exited) {
        cancelMotion();
        routeNormal(true, true);
        return;
    }
    if (result_.lifecycle.gate.go) startOpener();
    if (faults_ != 0U) return;
    if (reflank_active_) runReflank();
    else if (opener_active_) runOpener(input);
    else routeNormal(!normal_active_);
}

void Robot::acceptMotion(const motion::Result& result, governor::Profile profile, bool brake) {
    const bool active = result.status == motion::Status::ACTIVE;
    const bool terminal = result.status == motion::Status::DONE || result.status == motion::Status::TIMED_OUT;
    if ((!active && !terminal) || !validDuty(result.duty_l) || !validDuty(result.duty_r) ||
        (terminal && (result.duty_l != 0.0F || result.duty_r != 0.0F))) {
        faults_ |= SCRIPT_RESULT;
        return;
    }
    tick_.request.duty_l = result.duty_l;
    tick_.request.duty_r = result.duty_r;
    tick_.request.profile = profile;
    tick_.request.brake = brake || !active;
}

void Robot::startOpener() {
    cancelMotion();
    bool started = false;
    if (running_mode_ == core::Mode::DIRECT) {
        started = direct_.start(tick_.t_us, result_.heading.heading_deg,
                                 result_.lifecycle.services.opponent_snapshot);
    } else if (running_mode_ == core::Mode::WAIT) {
        started = wait_.start(tick_.t_us, result_.heading.heading_deg);
    } else {
        started = flank_.start(tick_.t_us, result_.heading.heading_deg,
                                result_.heading.imu_ok, running_mode_);
    }
    if (!started) faults_ |= SCRIPT_START;
    opener_active_ = started;
    tick_.selected = core::State::OPENER;
}

openers::Sample Robot::openerSample() const {
    const auto& bearing = tick_.observation.bearing;
    return {tick_.t_us, result_.heading.heading_deg, result_.heading.imu_ok,
            result_.opponent_mask, bearing.relative_deg, bearing.bearing_valid};
}

void Robot::acceptFlank(const openers::FlankResult& result, bool brake) {
    acceptMotion(result.motion, result.profile, brake);
    if (result.motion_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 16U);
    if (result.exit == openers::Exit::INVALID) faults_ |= SCRIPT_RESULT;
    if (result.exit != openers::Exit::NONE && result.exit != openers::Exit::INVALID) {
        if (result.scan_hint_valid) {
            scan_hint_ = result.scan_direction;
            scan_hint_valid_ = true;
        }
        opener_active_ = false;
        routeNormal(true);
    }
}

void Robot::runOpener(const RobotInput&) {
    tick_.selected = core::State::OPENER;
    if (running_mode_ == core::Mode::DIRECT) {
        const auto result = direct_.step(tick_.t_us, result_.heading.heading_deg,
                                          result_.heading.imu_ok, result_.opponent_mask);
        acceptMotion(result.motion, governor::Profile::OPENER);
        if (result.exit == openers::Exit::INVALID) faults_ |= SCRIPT_RESULT;
        if (result.exit != openers::Exit::NONE && result.exit != openers::Exit::INVALID) {
            opener_active_ = false;
            routeNormal(true);
        }
    } else if (running_mode_ == core::Mode::WAIT) {
        const auto result = wait_.step(openerSample());
        acceptFlank(result.flank, result.brake);
    } else {
        const auto result = flank_.step(openerSample());
        acceptFlank(result, false);
    }
}

SearchContext Robot::searchContext() const {
    SearchContext context;
    context.last_side = side_.direction();
    const auto& memory = fusion_.memory();
    const auto world = heading_.projectWorld(memory.last_world_bearing_deg);
    context.world_valid = world_seen_ && memory.world_valid && world.valid;
    context.world_bearing_deg = world.heading_deg;
    context.world_age_us = world_age_us_;
    context.scan_hint_valid = scan_hint_valid_;
    context.scan_hint = scan_hint_;
    const auto inward = heading_.projectHeading(inward_raw_deg_);
    context.inward_valid = inward_valid_ && inward.valid;
    context.inward_heading_deg = inward.heading_deg;
    context.inward_age_us = inward_age_us_;
    return context;
}

SwingContext Robot::swingContext() const {
    SwingContext context;
    context.edge_side_valid = edge_side_valid_;
    context.edge_side = edge_side_;
    context.edge_age_us = edge_age_us_;
    context.front_left_seen = front_seen_[0];
    context.front_right_seen = front_seen_[1];
    context.front_left_age_us = front_age_us_[0];
    context.front_right_age_us = front_age_us_[1];
    context.previous_swing_valid = previous_swing_valid_;
    context.previous_swing = previous_swing_;
    return context;
}

void Robot::routeNormal(bool reset, bool defer) {
    if (reset || !normal_active_) {
        normal_.reset();
        search_.reset();
        defend_.reset();
        search_active_ = false;
        defend_active_ = false;
        defend_pending_ = false;
    }
    normal_active_ = true;
    const auto selected = normal_.step(result_.opponent_mask);
    tick_.selected = selected.state;
    if (tick_.selected == core::State::DEFEND_TURN && !defend_active_ &&
        !tick_.observation.bearing.bearing_valid && !defend_pending_) {
        defend_pending_ = true;
        defend_pending_age_us_ = 0;
        defend_pending_last_us_ = tick_.t_us;
    }
    if (tick_.selected != core::State::SEARCH) {
        search_active_ = false;
        search_.reset();
        scan_hint_valid_ = false;
    }
    if (tick_.selected != core::State::DEFEND_TURN) {
        defend_active_ = false;
        defend_pending_ = false;
        defend_.reset();
    }
    tick_.forced_brake = tick_.forced_brake || defer || selected.brake;
    if (tick_.forced_brake) {
        tick_.request.duty_l = tick_.request.duty_r = 0.0F;
        tick_.request.brake = true;
        return;
    }
    runNormalExecutor();
}

void Robot::runSearch() {
    if (!search_active_) {
        search_active_ = search_.start(tick_.t_us, result_.heading.heading_deg,
                                       result_.heading.imu_ok, searchContext());
        if (!search_active_) { faults_ |= SCRIPT_START; return; }
    }
    const auto result = search_.step(tick_.t_us, result_.heading.heading_deg,
                                      result_.heading.imu_ok, result_.opponent_mask);
    acceptMotion(result.motion, result.profile);
    if (result.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 4U);
    if (result.phase == SearchPhase::SCAN || result.phase == SearchPhase::ADVANCE)
        scan_hint_valid_ = false;
    if (result.intent == Intent::INVALID) faults_ |= SCRIPT_RESULT;
    if (result.intent != Intent::NONE) search_active_ = false;
}

void Robot::runNormalExecutor() {
    if (tick_.selected == core::State::SEARCH) runSearch();
    else if (tick_.selected == core::State::DEFEND_TURN) runDefend();
}

void Robot::runDefend() {
    if (defend_pending_) {
        defend_pending_age_us_ = ageTo(defend_pending_age_us_,
            tick_.t_us - defend_pending_last_us_, config::DEFEND_TIMEOUT_MS * 1000U);
        defend_pending_last_us_ = tick_.t_us;
        if (defend_pending_age_us_ >= config::DEFEND_TIMEOUT_MS * 1000U) {
            finishDefend();
            return;
        }
    }
    const auto& bearing = tick_.observation.bearing;
    if (!defend_active_) {
        if (!bearing.bearing_valid) {
            tick_.request.duty_l = tick_.request.duty_r = 0.0F;
            tick_.request.brake = true;
            return;
        }
        defend_active_ = defend_.start(tick_.t_us, result_.heading.heading_deg,
            bearing.relative_deg, bearing.bearing_valid, result_.heading.imu_ok);
        if (!defend_active_) { faults_ |= SCRIPT_START; return; }
    }
    const auto result = defend_.step(tick_.t_us, result_.heading.heading_deg,
                                      result_.heading.imu_ok, result_.opponent_mask);
    acceptMotion(result.motion, governor::Profile::PIVOT);
    if (result.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 8U);
    if (result.intent == Intent::INVALID) faults_ |= SCRIPT_RESULT;
    if (result.intent == Intent::SEARCH) finishDefend();
}

void Robot::finishDefend() {
    defend_active_ = false;
    defend_pending_ = false;
    normal_.reset();
    search_.reset();
    search_active_ = false;
    tick_.selected = core::State::SEARCH;
    // One bounded destination entry; its target exit waits for next tick.
    runSearch();
}

void Robot::runReflank() {
    tick_.selected = core::State::REFLANK;
    const auto& bearing = tick_.observation.bearing;
    const auto result = reflank_.step(tick_.t_us, result_.heading.heading_deg,
        result_.heading.imu_ok, result_.opponent_mask, tick_.observation.cue.cue,
        bearing.relative_deg, bearing.bearing_valid);
    acceptMotion(result.motion, result.profile);
    tick_.reflank_direction = result.direction;
    if (result.entered_swing) {
        tick_.reflank_entries |= 2U;
        previous_swing_ = result.direction;
        previous_swing_valid_ = true;
    }
    if (result.entered_turn_in) tick_.reflank_entries |= 4U;
    if (result.turn_timed_out) markFault(logframe::FaultCode::TURN_TIMEOUT, 2U);
    if (result.intent == Intent::INVALID) faults_ |= SCRIPT_RESULT;
    if (result.intent == Intent::PERCEPTION || result.intent == Intent::SEARCH) {
        reflank_active_ = false;
        routeNormal(true);
    }
}

void Robot::checkStall() {
    opp_fusion::ContactCommit preview;
    if (tick_.sampled && tick_.selected == core::State::ATTACK && faults_ == 0U)
        preview = fusion_.preview(core::State::ATTACK);
    stall::Sample sample;
    sample.t_us = tick_.t_us;
    sample.state = faults_ == 0U ? tick_.selected : core::State::STOPPED;
    sample.centered = tick_.observation.bearing.centered;
    sample.contact = preview.valid && preview.result.contact;
    sample.contact_started = preview.valid && preview.result.contact_started;
    sample.edge_event = tick_.new_white != 0U;
    sample.duty_l = tick_.applied_l;
    sample.duty_r = tick_.applied_r;
    sample.heading_deg = result_.heading.heading_deg;
    sample.imu_ok = result_.heading.imu_ok;
    sample.suppress = tick_.limit.all_in_active;
    tick_.stall = detector_.step(sample);
    if (!tick_.stall.stalled || !tick_.permission || faults_ != 0U) return;
    tick_.stall_selected = true;
    tick_.limit = limiter_.request(tick_.t_us);
    if (!tick_.limit.allowed) return;
    const auto choice = chooseSwing(swingContext());
    if (!choice.valid) { faults_ |= INVALID_CONTEXT; return; }
    reflank_active_ = reflank_.start(tick_.t_us, result_.heading.heading_deg,
                                    result_.heading.imu_ok, choice.direction);
    if (!reflank_active_) { faults_ |= SCRIPT_START; return; }
    normal_.reset();
    normal_active_ = false;
    search_active_ = defend_active_ = false;
    scan_hint_valid_ = false;
    detector_.reset();
    tick_.reflank_entries |= 1U;
    tick_.reflank_direction = choice.direction;
    runReflank();
}

void Robot::prepareFinalRequest() {
    if (tick_.selected == core::State::TRACK || tick_.selected == core::State::ATTACK) {
        const auto preview = tick_.sampled ? fusion_.preview(tick_.selected) : opp_fusion::ContactCommit{};
        const auto demand = frontDemand(tick_.selected, result_.opponent_mask,
                                         preview.valid && preview.result.contact);
        if (!preview.valid || !demand.valid) faults_ |= INVALID_CONTEXT;
        tick_.request.duty_l = demand.duty_l;
        tick_.request.duty_r = demand.duty_r;
        tick_.request.profile = demand.profile;
        tick_.request.brake = false;
    }
    if (!validDuty(tick_.request.duty_l) || !validDuty(tick_.request.duty_r) ||
        !validProfile(tick_.request.profile)) faults_ |= GOVERNOR_CONTRACT;
    if (faults_ != 0U) tick_.selected = core::State::STOPPED;
    tick_.request.inhibited = !tick_.permission || faults_ != 0U ||
        !moving(tick_.selected) || result_.escape_fault != edge::EscapeFault::NONE;
    if (tick_.forced_brake || tick_.request.inhibited) {
        tick_.request.duty_l = tick_.request.duty_r = 0.0F;
        tick_.request.brake = true;
    }
}

void Robot::commitAndGovern(const RobotInput& input) {
    if (tick_.sampled) tick_.contact = fusion_.commit(tick_.selected);
    if (tick_.sampled && !tick_.contact.valid) {
        // Missing commitment already clears the component latch; publish no authority.
        faults_ |= INVALID_CONTEXT;
        tick_.request.inhibited = true;
    }
    tick_.request.centered = tick_.observation.bearing.centered;
    tick_.request.contact = tick_.contact.valid && tick_.contact.result.contact;
    tick_.request.vbat_v = input.vbat_valid ? input.vbat_v : std::numeric_limits<float>::quiet_NaN();
    const auto governed = governor_.step(input.t_us, tick_.request);
    const bool expected_invalid_voltage = tick_.request.inhibited &&
        !std::isfinite(tick_.request.vbat_v);
    const bool unexpected = (!governed.valid && !expected_invalid_voltage) ||
        !validDuty(governed.duty_l) || !validDuty(governed.duty_r);
    if (unexpected) faults_ |= GOVERNOR_CONTRACT;
    result_.outputs.motors_enabled = !tick_.request.inhibited && !unexpected &&
        tick_.contact.valid && faults_ == 0U;
    result_.outputs.duty_l = result_.outputs.motors_enabled ? governed.duty_l : 0.0F;
    result_.outputs.duty_r = result_.outputs.motors_enabled ? governed.duty_r : 0.0F;
    result_.outputs.ui_state = tick_.selected;
    result_.contact = tick_.contact.valid && tick_.contact.result.contact;
}

void Robot::updateQtrWarnings() {
    const bool pivot = tick_.sampled && tick_.applied_enabled &&
        ((tick_.applied_l > 0.0F && tick_.applied_r < 0.0F) ||
         (tick_.applied_l < 0.0F && tick_.applied_r > 0.0F));
    std::uint8_t newly_warned = 0;
    for (unsigned i = 0; i < 4U; ++i) {
        const auto bit = static_cast<std::uint8_t>(1U << i);
        if (!pivot || (result_.line_mask & bit) == 0U) {
            qtr_active_ &= static_cast<std::uint8_t>(~bit);
            qtr_warning_ &= static_cast<std::uint8_t>(~bit);
            qtr_age_us_[i] = 0;
        } else if ((qtr_active_ & bit) == 0U) {
            qtr_active_ |= bit;
            qtr_age_us_[i] = 0;
        } else {
            qtr_age_us_[i] = ageTo(qtr_age_us_[i], tick_.delta_us,
                                    config::QTR_STUCK_MS * 1000U + 1U);
            if (qtr_age_us_[i] > config::QTR_STUCK_MS * 1000U && (qtr_warning_ & bit) == 0U) {
                newly_warned |= bit;
                qtr_warning_ |= bit;
            }
        }
    }
    if (newly_warned != 0U) markFault(logframe::FaultCode::QTR_STUCK_WARNING, newly_warned);
}

void Robot::updateWarnings(const RobotInput& input) {
    if (initialized_) {
        if (!input.imu_ok && (!imu_reported_ || imu_available_))
            markFault(logframe::FaultCode::IMU_UNAVAILABLE);
        imu_reported_ = true;
        imu_available_ = input.imu_ok;
    }
    if (input.vbat_valid && std::isfinite(input.vbat_v)) {
        if (input.vbat_v >= config::VBAT_WARN_V) low_battery_ = false;
        else if (tick_.selected == core::State::IDLE && !low_battery_) {
            low_battery_ = true;
            markFault(logframe::FaultCode::LOW_BATTERY);
        }
    }
    updateQtrWarnings();
}

void Robot::publishEdge() {
    std::uint8_t detail = 0U;
    if (tick_.new_white != 0U) detail |= logframe::NEW_WHITE;
    if (tick_.escape.entered) detail |= logframe::ENTERED;
    if (tick_.escape.replanned) detail |= logframe::REPLANNED;
    if (tick_.escape.exited) detail |= logframe::EXITED;
    if (tick_.escape.pushed_out && (tick_.escape.entered || tick_.escape.replanned))
        detail |= logframe::PUSHED_OUT;
    if (detail == 0U) return;
    const auto value = static_cast<std::uint16_t>(result_.line_mask |
        (tick_.new_white << 4U) | (tick_.escape.replans << 8U));
    emit(tick_.t_us, core::Event::EDGE, detail, value);
}

void Robot::publishPhantom() {
    if (!tick_.sampled || !tick_.observation.phantom.phantom_set) return;
    const auto projected = heading_.projectWorld(tick_.observation.phantom.world_deg);
    if (!projected.valid) {
        result_.events.invalid_metadata = logframe::saturatingIncrement(result_.events.invalid_metadata);
        recording_incomplete_ = true;
        return;
    }
    auto value = static_cast<std::int32_t>(std::round(static_cast<double>(projected.heading_deg) * 100.0));
    if (value == -18000) value = 18000;
    emit(tick_.t_us, core::Event::PHANTOM_SET, 0U, static_cast<std::uint16_t>(value));
}

void Robot::publishEvents() {
    const auto mode = static_cast<std::uint8_t>(running_mode_);
    if (result_.lifecycle.gate.start_release) emit(tick_.t_us, core::Event::START_RELEASE, mode);
    if (result_.lifecycle.gate.go) emit(tick_.t_us, core::Event::GO, mode);
    publishEdge();
    publishPhantom();
    const auto new_faults = static_cast<std::uint16_t>(faults_ & ~reported_faults_);
    if (new_faults != 0U) markFault(logframe::FaultCode::CORE_CONTRACT_FAULT, new_faults);
    reported_faults_ |= faults_;
    for (std::uint8_t code = 1U; code <= 10U; ++code) {
        if (code != 9U && (tick_.fault_events & (1U << code)) != 0U)
            emit(tick_.t_us, core::Event::FAULT, code, tick_.fault_values[code]);
    }
    if (tick_.stall_selected) {
        const auto detail = static_cast<std::uint8_t>((tick_.stall.timer_trigger ? 1U : 0U) |
            (tick_.stall.deflection_trigger ? 2U : 0U) | (tick_.limit.allowed ? 4U : 0U) |
            (tick_.limit.all_in_started ? 8U : 0U));
        emit(tick_.t_us, core::Event::STALL, detail,
             static_cast<std::uint16_t>(tick_.limit.attempts_in_window));
    }
    if (tick_.entry != state_) emit(tick_.t_us, core::Event::STATE_CHANGE,
        static_cast<std::uint8_t>(tick_.entry), static_cast<std::uint16_t>(state_));
    if (tick_.contact.valid && tick_.contact.result.contact_started) {
        const auto detail = static_cast<std::uint8_t>((tick_.contact.result.close_cue ? 1U : 0U) |
                                                    (tick_.contact.result.impact_cue ? 2U : 0U));
        emit(tick_.t_us, core::Event::CONTACT, detail, result_.opponent_mask);
    }
    for (std::uint8_t phase = 1U; phase <= 3U; ++phase) {
        if ((tick_.reflank_entries & (1U << (phase - 1U))) != 0U)
            emit(tick_.t_us, core::Event::REFLANK_PHASE, phase,
                 tick_.reflank_direction == motion::Direction::RIGHT ? 1U : 2U);
    }
}

void Robot::prepareFrame(const RobotInput& input) {
    if (!recording_) return;
    const bool stopping = state_ == core::State::STOPPED ||
        (state_ == core::State::EDGE_ESCAPE && result_.escape_fault != edge::EscapeFault::NONE) ||
        (tick_.entry == core::State::COUNTDOWN && state_ == core::State::IDLE);
    const std::uint64_t periods = frame_age_us_ / FRAME_PERIOD_US;
    const bool due = tick_.frame_immediate || periods != 0U || stopping;
    if (periods != 0U) {
        const auto skipped = periods - 1U;
        const auto sum = static_cast<std::uint64_t>(skipped_frames_) + skipped;
        skipped_frames_ = sum > std::numeric_limits<std::uint32_t>::max() ?
            std::numeric_limits<std::uint32_t>::max() : static_cast<std::uint32_t>(sum);
        if (skipped != 0U) recording_incomplete_ = true;
        frame_age_us_ %= FRAME_PERIOD_US;
    }
    if (due) {
        pending_.frame_due = true;
        auto& frame = pending_.frame;
        frame.t_ms = static_cast<std::uint32_t>(record_elapsed_us_ / 1000U);
        frame.state = state_;
        frame.mode = running_mode_;
        frame.line_mask = result_.line_mask;
        frame.opp_mask = result_.opponent_mask;
        frame.heading_deg = attempt_go_ ? result_.heading.heading_deg : input.raw_heading_deg;
        frame.gyro_z_dps = input.raw_gyro_z_dps;
        frame.ax_g = input.ax_g;
        frame.ay_g = input.ay_g;
        frame.vbat_v = input.vbat_valid ? input.vbat_v : std::numeric_limits<float>::quiet_NaN();
        const bool imu = attempt_go_ ? result_.heading.imu_ok :
            input.imu_ok && std::isfinite(input.raw_heading_deg);
        if (imu) frame.flags |= logframe::IMU_OK;
        if (tick_.observation.phantom.active) frame.flags |= logframe::PHANTOM_ACTIVE;
        if (result_.opponent_fault_mask != 0U) frame.flags |= logframe::STUCK;
        if (result_.lifecycle.services.calibration_rejected) frame.flags |= logframe::CAL_REJECTED;
    }
    if (stopping) recording_ = timing_active_ = false;
}

void Robot::savePending(const RobotInput& input) {
    pending_ = {};
    pending_.valid = true;
    pending_.token = result_.token;
    pending_.t_us = input.t_us;
    pending_.requested = result_.outputs;
    pending_.after_go = attempt_go_;
    pending_.match_tick = timing_active_;
    prepareFrame(input);
}

void Robot::finish(const RobotInput& input) {
    state_ = tick_.selected;
    result_.menu = menu_.step({input.t_us, input.button, tick_.entry,
        faults_ != 0U || state_ == core::State::STOPPED || result_.escape_fault != edge::EscapeFault::NONE,
        lifecycle_.buttonEvents().start_release});
    result_.running_mode = running_mode_;
    result_.contract_faults = faults_;
    result_.qtr_warning_mask = qtr_warning_;
    result_.low_battery = low_battery_;
    result_.all_in = tick_.limit.all_in_active;
    publishEvents();
    savePending(input);
    result_.skipped_frames = skipped_frames_;
    result_.ticks = statistics_;
    result_.timing_incomplete = timing_incomplete_;
    result_.recording_incomplete = recording_incomplete_;
}

RobotResult Robot::exhaust(const RobotInput& input) {
    clearActions(result_);
    tick_ = {};
    tick_.t_us = input.t_us;
    tick_.entry = state_;
    receive(input);
    faults_ |= TOKEN_EXHAUSTED;
    tick_.selected = state_ = core::State::STOPPED;
    result_.outputs = {};
    result_.outputs.ui_state = state_;
    result_.contact = false;
    result_.token = 0;
    result_.contract_faults = faults_;
    publishEvents();
    result_.ticks = statistics_;
    result_.skipped_frames = skipped_frames_;
    result_.timing_incomplete = timing_incomplete_;
    result_.recording_incomplete = recording_incomplete_;
    last_us_ = input.t_us;
    return result_;
}

void Robot::reset() {
    const auto next = next_token_;
    *this = Robot{};
    next_token_ = next;
}
} // namespace fsm
