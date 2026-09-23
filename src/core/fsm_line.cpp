// Admits D085 line frames independently of the one-kilohertz opponent stream.
// Keeps retained edge levels authoritative without repeating confirmation or replans.
// Independent frame-order, expiry, countdown and escape tests cover this path.
#include "fsm.h"
#include <limits>

namespace fsm {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
bool sameFrame(const core::LineEvidence& a, const core::LineEvidence& b) {
    return a.sequence == b.sequence && a.started_us == b.started_us &&
           a.completed_us == b.completed_us && a.white_candidates == b.white_candidates &&
           a.threshold_version == b.threshold_version && a.use == b.use;
}
} // namespace

void Robot::publishLine(std::uint8_t white_candidates) {
    result_.line_mask = classifier_.observeMask(white_candidates);
    tick_.new_white = static_cast<std::uint8_t>(result_.line_mask & ~previous_line_);
    previous_line_ = result_.line_mask;
    result_.line_updated = true;
}

bool Robot::admitLine(const RobotInput& input) {
    const auto& line = input.line;
    if (line.presence == core::LinePresence::ABSENT) return true;
    if (line.presence != core::LinePresence::VALID || (line.white_candidates & 0xF0U) != 0U ||
        line.completed_us - line.started_us >= config::QTR_FRAME_MAX_US ||
        input.t_us - line.completed_us >= HALF_RANGE ||
        input.t_us - line.started_us >= config::QTR_SAMPLE_MAX_AGE_US) return false;
    if (line_seen_) {
        if (sameFrame(line, line_history_)) return true;
        const auto elapsed = line.started_us - line_history_.started_us;
        const auto sequence = line.sequence - line_history_.sequence;
        if (elapsed < config::QTR_START_PERIOD_US || elapsed >= HALF_RANGE ||
            line.started_us - line_history_.completed_us >= HALF_RANGE ||
            sequence == 0U || sequence >= HALF_RANGE) return false;
    }
    line_seen_ = true;
    line_history_ = line;
    line_age_us_ = input.t_us - line.started_us;
    publishLine(line.white_candidates);
    return true;
}

void Robot::advanceLineHistories() {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    line_age_us_ = maximum - line_age_us_ < tick_.delta_us ? maximum :
                   line_age_us_ + tick_.delta_us;
    const auto long_maximum = std::numeric_limits<std::uint64_t>::max();
    line_raw_boundary_age_us_ = long_maximum - line_raw_boundary_age_us_ < tick_.delta_us ?
        long_maximum : line_raw_boundary_age_us_ + tick_.delta_us;
    line_rearm_age_us_ = long_maximum - line_rearm_age_us_ < tick_.delta_us ?
        long_maximum : line_rearm_age_us_ + tick_.delta_us;
}

void Robot::prepareLine(const RobotInput& input) {
    advanceLineHistories();
    tick_.line_start_inhibited = line_calibration_hold_ || line_start_rearming_;
    if (!line_mode_chosen_) {
        line_mode_chosen_ = true;
        explicit_line_mode_ = input.line.explicit_values;
    }
    if (!input.line.contract_valid || input.line.explicit_values != explicit_line_mode_ ||
        (input.line.use != core::LineUse::CONTROL && input.line.use != core::LineUse::CALIBRATION) ||
        (!explicit_line_mode_ && input.line.use != core::LineUse::CONTROL)) {
        faults_ |= LINE_CONTRACT;
        result_.line_available = false;
        result_.line_raw_mode = false;
        return;
    }
    if (input.line.use == core::LineUse::CALIBRATION || line_calibration_hold_) {
        prepareCalibrationLine(input);
        return;
    }
    result_.line_raw_mode = false;
    if (input.line.threshold_version != line_threshold_version_) faults_ |= LINE_CONTRACT;
    if (!explicit_line_mode_) {
        result_.line_available = input.observations_fresh;
        if (!input.observations_fresh) return;
        result_.line_mask = classifier_.observe(input.line_raw_us);
        tick_.new_white = static_cast<std::uint8_t>(result_.line_mask & ~previous_line_);
        previous_line_ = result_.line_mask;
        result_.line_updated = true;
        result_.line_source_us = input.t_us;
        result_.line_age_us = 0U;
        return;
    }
    if (line_seen_ && line_age_us_ >= config::QTR_SAMPLE_MAX_AGE_US) {
        resetLineReadiness();
    }
    const bool admitted = admitLine(input);
    if (!admitted) faults_ |= LINE_CONTRACT;
    result_.line_source_us = line_seen_ ? line_history_.started_us : 0U;
    result_.line_sequence = line_seen_ ? line_history_.sequence : 0U;
    result_.line_age_us = line_seen_ ? line_age_us_ : 0U;
    result_.line_available = admitted && line_seen_ &&
                            line_age_us_ < config::QTR_SAMPLE_MAX_AGE_US;
    if ((initialized_ || input.initialization_complete) && !result_.line_available)
        faults_ |= LINE_CONTRACT;
}
} // namespace fsm
