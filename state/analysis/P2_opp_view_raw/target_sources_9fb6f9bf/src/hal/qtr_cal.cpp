// Collects bounded B13 raw interval batches and publishes one complete RAM bank.
// Actual inhibited Robot intents own captures; retained evidence cannot renew age.
// Independent D089 lifecycle, interval and real-pipeline tests cover this owner.
#include "qtr_cal.h"
#include <limits>

namespace qtr_cal {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
std::uint32_t addAge(std::uint32_t age, std::uint32_t elapsed) {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    return maximum - age < elapsed ? maximum : age + elapsed;
}
bool active(Phase phase) {
    return phase == Phase::WAITING || phase == Phase::COLLECTING;
}
bool validConfig() {
    const auto deadline = static_cast<std::uint64_t>(config::QTR_CAL_CAPTURE_MS) * 1000U;
    return config::QTR_CAL_SAMPLES >= 1U && config::QTR_CAL_SAMPLES <= 256U &&
        deadline > 0U && deadline < HALF_RANGE;
}
bool samePad(const line_qtr::Pad& a, const line_qtr::Pad& b) {
    return a.release_before_us == b.release_before_us &&
        a.release_after_us == b.release_after_us &&
        a.last_high_before_us == b.last_high_before_us &&
        a.first_low_after_us == b.first_low_after_us &&
        a.lower_us == b.lower_us && a.upper_us == b.upper_us;
}
bool sameCleanup(const line_qtr::Cleanup& a, const line_qtr::Cleanup& b) {
    if (a.attempted_mask != b.attempted_mask || a.failed_mask != b.failed_mask ||
        a.skipped_mask != b.skipped_mask || a.nonneutral_mask != b.nonneutral_mask ||
        a.started_us != b.started_us || a.completed_us != b.completed_us ||
        a.deadline_exceeded != b.deadline_exceeded) return false;
    for (unsigned i = 0U; i < 4U; ++i) if (a.status[i] != b.status[i]) return false;
    return true;
}
bool sameSnapshot(const line_qtr::Snapshot& a, const line_qtr::Snapshot& b) {
    if (a.phase != b.phase || a.status != b.status || a.valid != b.valid ||
        a.sequence != b.sequence || a.started_us != b.started_us ||
        a.drive_completed_us != b.drive_completed_us || a.checked_us != b.checked_us ||
        a.completed_us != b.completed_us || a.advances != b.advances ||
        a.max_service_gap_us != b.max_service_gap_us ||
        a.released_mask != b.released_mask || a.high_mask != b.high_mask ||
        a.low_mask != b.low_mask || a.timeout_mask != b.timeout_mask ||
        !sameCleanup(a.cleanup, b.cleanup)) return false;
    for (unsigned i = 0U; i < 4U; ++i)
        if (a.status_by_pad[i] != b.status_by_pad[i] || !samePad(a.pad[i], b.pad[i]))
            return false;
    return true;
}
} // namespace

bool Calibration::eligible(const fsm::RobotResult& robot) const {
    return robot.outputs.ui_state == core::State::IDLE &&
        !robot.outputs.motors_enabled && robot.outputs.duty_l == 0.0F &&
        robot.outputs.duty_r == 0.0F && robot.contract_faults == 0U &&
        robot.escape_fault == edge::EscapeFault::NONE && robot.line_raw_mode &&
        robot.menu.selection.service_menu &&
        robot.menu.selection.service == countdown::Service::QTR_CAL;
}

void Calibration::reject(Reason reason) {
    report_.phase = Phase::REJECTED;
    report_.reason = reason;
    report_.completed_us = last_us_;
}

void Calibration::start(std::uint32_t t_us) {
    if (report_.phase != Phase::WAITING) {
        const auto bank = report_.thresholds;
        report_ = {};
        report_.thresholds = bank;
        candidate_ = bank;
        if (source_seen_) {
            report_.last_source_us = previous_.started_us;
            report_.last_sequence = previous_.sequence;
        }
    }
    report_.phase = Phase::COLLECTING;
    report_.reason = Reason::NONE;
    report_.capture_started_us = t_us;
    report_.completed_us = 0U;
    report_.samples = 0U;
    capture_age_us_ = 0U;
    if (!validConfig() || !line_qtr::validThresholds(report_.thresholds))
        reject(Reason::INVALID_CONFIG);
}

bool Calibration::admit(std::uint32_t t_us, const line_qtr::Snapshot& snapshot) {
    const auto qualification = line_qtr::validateRaw(snapshot);
    if (qualification == line_qtr::RawQualification::ABSENT) return false;
    if (qualification == line_qtr::RawQualification::PROVIDER_FAULT) {
        reject(Reason::PROVIDER_FAULT);
        return false;
    }
    if (qualification != line_qtr::RawQualification::VALID) {
        reject(Reason::INVALID_RAW);
        return false;
    }
    if (source_seen_ && source_age_us_ >= HALF_RANGE) {
        reject(Reason::SOURCE_ORDER);
        return false;
    }
    const auto age = t_us - snapshot.started_us;
    if (t_us - snapshot.completed_us >= HALF_RANGE ||
        age >= config::QTR_SAMPLE_MAX_AGE_US) {
        reject(Reason::STALE);
        return false;
    }
    if (source_seen_) {
        if (sameSnapshot(snapshot, previous_)) {
            if (source_age_us_ >= config::QTR_SAMPLE_MAX_AGE_US) reject(Reason::STALE);
            return false;
        }
        if (snapshot.sequence == previous_.sequence ||
            snapshot.started_us == previous_.started_us) {
            reject(Reason::CONFLICTING_REPLAY);
            return false;
        }
        const auto elapsed = snapshot.started_us - previous_.started_us;
        const auto sequence = snapshot.sequence - previous_.sequence;
        if (elapsed < config::QTR_START_PERIOD_US || elapsed >= HALF_RANGE ||
            snapshot.started_us - previous_.completed_us >= HALF_RANGE ||
            sequence >= HALF_RANGE || elapsed > source_age_us_ ||
            source_age_us_ - elapsed != age) {
            reject(Reason::SOURCE_ORDER);
            return false;
        }
    }
    previous_ = snapshot;
    source_seen_ = true;
    source_age_us_ = age;
    report_.last_source_us = snapshot.started_us;
    report_.last_sequence = snapshot.sequence;
    return true;
}

void Calibration::collect(std::uint32_t t_us, const line_qtr::Snapshot& snapshot) {
    // Ages share the current admitted decision, so this remains sound through wrap.
    if (source_age_us_ > capture_age_us_) return;
    const auto sensor = static_cast<unsigned>(report_.stage / 2U);
    auto& evidence = report_.sensors[sensor];
    const auto& pad = snapshot.pad[sensor];
    if ((report_.stage & 1U) == 0U) {
        if ((snapshot.low_mask & (1U << sensor)) == 0U) {
            reject(Reason::CENSORED_WHITE);
            return;
        }
        if (pad.upper_us > evidence.white_upper_us) evidence.white_upper_us = pad.upper_us;
        ++evidence.white_count;
    } else {
        if (evidence.black_count == 0U || pad.lower_us < evidence.black_lower_us)
            evidence.black_lower_us = pad.lower_us;
        ++evidence.black_count;
        if ((snapshot.timeout_mask & (1U << sensor)) != 0U) ++evidence.black_censored;
    }
    ++report_.samples;
    if (report_.samples == config::QTR_CAL_SAMPLES) finishStage(t_us);
}

void Calibration::finishStage(std::uint32_t t_us) {
    if ((report_.stage & 1U) != 0U) {
        const auto sensor = static_cast<unsigned>(report_.stage / 2U);
        const auto& evidence = report_.sensors[sensor];
        const auto upper = evidence.black_lower_us < config::QTR_TIMEOUT_US ?
            evidence.black_lower_us : config::QTR_TIMEOUT_US;
        if (evidence.white_upper_us == 0U || evidence.white_upper_us >= upper) {
            reject(Reason::NO_SEPARATION);
            return;
        }
        candidate_.white_us[sensor] = evidence.white_upper_us +
            (upper - evidence.white_upper_us) / 2U;
    }
    report_.completed_us = t_us;
    if (report_.stage != 7U) {
        ++report_.stage;
        report_.samples = 0U;
        report_.phase = Phase::WAITING;
        return;
    }
    if (report_.thresholds.version == std::numeric_limits<std::uint32_t>::max()) {
        reject(Reason::VERSION_EXHAUSTED);
        return;
    }
    candidate_.version = report_.thresholds.version + 1U;
    report_.thresholds = candidate_;
    report_.phase = Phase::SUCCESS;
    report_.committed = true;
}

Report Calibration::step(std::uint32_t t_us, const fsm::RobotResult& robot,
                         const line_qtr::Snapshot& snapshot) {
    report_.committed = false;
    if (!robot.fresh || (observed_ && robot.token == last_token_)) return report_;
    if (robot.token == 0U || robot.token < last_token_) {
        reject(Reason::TOKEN_ORDER);
        return report_;
    }
    last_token_ = robot.token;
    const auto elapsed = observed_ ? t_us - last_us_ : 0U;
    if (elapsed >= HALF_RANGE) {
        reject(Reason::TIME_ORDER);
        return report_;
    }
    last_us_ = t_us;
    observed_ = true;
    capture_age_us_ = addAge(capture_age_us_, elapsed);
    source_age_us_ = addAge(source_age_us_, elapsed);
    if (!eligible(robot)) {
        if (active(report_.phase)) {
            report_.phase = Phase::CANCELLED;
            report_.reason = Reason::CONTEXT;
            report_.completed_us = t_us;
        }
        return report_;
    }
    if (robot.menu.request == countdown::Service::QTR_CAL &&
        report_.phase != Phase::COLLECTING) start(t_us);
    if (!active(report_.phase)) return report_;
    if (report_.phase == Phase::COLLECTING &&
        capture_age_us_ >= static_cast<std::uint64_t>(config::QTR_CAL_CAPTURE_MS) * 1000U) {
        reject(Reason::DEADLINE);
        return report_;
    }
    if (admit(t_us, snapshot) && report_.phase == Phase::COLLECTING)
        collect(t_us, snapshot);
    return report_;
}

void Calibration::reset() {
    report_ = {};
    candidate_ = {};
    previous_ = {};
    last_token_ = 0U;
    last_us_ = capture_age_us_ = source_age_us_ = 0U;
    observed_ = source_seen_ = false;
}
} // namespace qtr_cal
