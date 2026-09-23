// Admits D089 raw-only QTR preparation and qualified threshold handover.
// Keeps source, STOP and receipt history while rebuilding only color and START readiness.
// Independent B13 pipeline tests cover raw faults, later frames and the full fresh hold.
#include "fsm.h"

namespace fsm {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool sameSource(const core::LineEvidence& a, const core::LineEvidence& b) {
    return a.sequence == b.sequence && a.started_us == b.started_us &&
           a.completed_us == b.completed_us;
}
} // namespace

void Robot::resetLineReadiness() {
    classifier_.reset();
    previous_line_ = 0U;
    line_qualified_frames_ = 0U;
    qtr_active_ = qtr_warning_ = 0U;
    for (auto& age : qtr_age_us_) age = 0U;
}

bool Robot::admitCalibrationLine(const RobotInput& input, bool& distinct) {
    const auto& line = input.line;
    const bool raw = line.use == core::LineUse::CALIBRATION;
    if (raw && (line.white_candidates != 0U || line.threshold_version != 0U)) return false;
    if (!raw && line.threshold_version < line_threshold_version_) return false;
    if (line.presence == core::LinePresence::ABSENT) return true;
    if (line.presence != core::LinePresence::VALID || (line.white_candidates & 0xF0U) != 0U ||
        line.completed_us - line.started_us >= config::QTR_FRAME_MAX_US ||
        input.t_us - line.completed_us >= HALF_RANGE ||
        input.t_us - line.started_us >= config::QTR_SAMPLE_MAX_AGE_US) return false;
    // Long absence preserves inhibition, but cannot establish the era of a
    // presented source whose modular time could describe an unseen old frame.
    if ((line_seen_ && line_age_us_ >= HALF_RANGE) ||
        (!raw && line_raw_boundary_age_us_ >= HALF_RANGE)) return false;
    if (line_seen_) {
        if (sameSource(line, line_history_)) {
            if (line_age_us_ >= config::QTR_SAMPLE_MAX_AGE_US) return false;
            // A single representation change consumes the retained source without
            // claiming a new observation or adopting its threshold version.
            if (line.use == line_history_.use &&
                (line.white_candidates != line_history_.white_candidates ||
                 line.threshold_version != line_history_.threshold_version)) return false;
            line_history_ = line;
            return true;
        }
        const auto elapsed = line.started_us - line_history_.started_us;
        const auto sequence = line.sequence - line_history_.sequence;
        if (elapsed < config::QTR_START_PERIOD_US || elapsed >= HALF_RANGE ||
            elapsed > line_age_us_ || line_age_us_ - elapsed != input.t_us - line.started_us ||
            line.started_us - line_history_.completed_us >= HALF_RANGE ||
            sequence == 0U || sequence >= HALF_RANGE) return false;
    }
    line_seen_ = true;
    line_history_ = line;
    line_age_us_ = input.t_us - line.started_us;
    distinct = true;
    return true;
}

void Robot::qualifyCalibrationLine(const RobotInput& input, bool distinct) {
    if (!distinct || static_cast<std::uint64_t>(line_age_us_) >= line_raw_boundary_age_us_)
        return;
    if (input.line.threshold_version != line_threshold_version_) {
        resetLineReadiness();
        line_threshold_version_ = input.line.threshold_version;
    }
    const auto mask = classifier_.observeMask(input.line.white_candidates);
    if (line_qualified_frames_ < config::QTR_CONFIRM_TICKS) ++line_qualified_frames_;
    if (line_qualified_frames_ < config::QTR_CONFIRM_TICKS) return;
    result_.line_mask = mask;
    tick_.new_white = static_cast<std::uint8_t>(mask & ~previous_line_);
    previous_line_ = mask;
    result_.line_updated = true;
    result_.line_available = true;
    line_calibration_hold_ = false;
    line_start_rearming_ = true;
    line_neutral_pending_ = false;
    line_rearm_age_us_ = 0U;
}

void Robot::prepareCalibrationLine(const RobotInput& input) {
    const bool raw = input.line.use == core::LineUse::CALIBRATION;
    const bool was_raw = result_.line_raw_mode;
    result_.line_raw_mode = false;
    result_.line_available = result_.line_updated = false;
    result_.line_mask = 0U;
    tick_.line_start_inhibited = true;
    if (raw && ((tick_.entry != core::State::BOOT && tick_.entry != core::State::IDLE) ||
        faults_ != 0U || result_.escape_fault != edge::EscapeFault::NONE ||
        result_.lifecycle.gate.phase == countdown::Phase::STOPPED)) {
        faults_ |= LINE_CONTRACT;
        return;
    }
    if ((raw && !was_raw) ||
        (line_seen_ && line_age_us_ >= config::QTR_SAMPLE_MAX_AGE_US)) resetLineReadiness();
    bool distinct = false;
    const bool admitted = admitCalibrationLine(input, distinct);
    if (!admitted) faults_ |= LINE_CONTRACT;
    if (raw && admitted) {
        line_calibration_hold_ = true;
        line_raw_boundary_age_us_ = 0U;
        line_start_rearming_ = line_neutral_pending_ = false;
        result_.line_raw_mode = true;
    } else if (!raw && admitted && faults_ == 0U) qualifyCalibrationLine(input, distinct);
    result_.line_source_us = line_seen_ ? line_history_.started_us : 0U;
    result_.line_sequence = line_seen_ ? line_history_.sequence : 0U;
    result_.line_age_us = line_seen_ ? line_age_us_ : 0U;
    result_.line_threshold_version = line_threshold_version_;
    result_.line_calibration_hold = line_calibration_hold_;
}

void Robot::prepareLineStart(const RobotInput& input) {
    result_.line_start_rearming = line_start_rearming_;
    if (!line_start_rearming_) return;
    // start_ready resets only Buttons; restart would also interrupt a live BOTH
    // hold, so this handover must never assert that broader restart signal.
    button_timing_.start_ready = false;
    if (!button_timing_.fresh || faults_ != 0U) return;
    const auto source_age = explicit_button_mode_ ? result_.button_age_us : 0U;
    if (static_cast<std::uint64_t>(source_age) >= line_rearm_age_us_) return;
    if (input.button != core::ButtonLevel::NONE) {
        line_neutral_pending_ = false;
        return;
    }
    if (!line_neutral_pending_) {
        line_neutral_pending_ = true;
        line_neutral_since_us_ = button_timing_.observation_us;
    } else if (button_timing_.observation_us - line_neutral_since_us_ >=
               config::BTN_DEBOUNCE_MS * 1000U) {
        line_start_rearming_ = false;
        result_.line_start_rearming = false;
        // The lifecycle sees this fresh NONE once to initialize Buttons. The
        // tick's separate inhibit still prevents accepting a match release.
        button_timing_.start_ready = true;
    }
}
} // namespace fsm
