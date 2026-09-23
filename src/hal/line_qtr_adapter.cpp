// Validates native RC brackets before admitting explicit line evidence to Robot.
// Keeps source identity and ambiguity separate from a measured white or black.
// Independent malformed-record, threshold and native-to-Robot tests cover this path.
#include "line_qtr_adapter.h"

namespace line_qtr {
namespace {
constexpr std::uint8_t ALL = 0x0FU;
bool emptyPad(const Pad& p) {
    return p.release_before_us == 0U && p.release_after_us == 0U &&
        p.last_high_before_us == 0U && p.first_low_after_us == 0U &&
        p.lower_us == 0U && p.upper_us == 0U;
}
bool emptyCleanup(const Cleanup& c) {
    if (c.attempted_mask != 0U || c.failed_mask != 0U || c.skipped_mask != 0U ||
        c.nonneutral_mask != 0U || c.started_us != 0U || c.completed_us != 0U ||
        c.deadline_exceeded) return false;
    for (const auto status : c.status) if (status != 0) return false;
    return true;
}
bool masksValid(const Snapshot& s) {
    const auto data = s.high_mask | s.low_mask | s.timeout_mask;
    return ((data | s.released_mask) & ~ALL) == 0U &&
        (s.low_mask & s.timeout_mask) == 0U &&
        (s.timeout_mask & ~s.high_mask) == 0U && (data & ~s.released_mask) == 0U;
}
bool emptyFrame(const Snapshot& s) {
    if (s.valid || s.sequence != 0U || s.started_us != 0U ||
        s.drive_completed_us != 0U || s.completed_us != 0U || s.advances != 0U ||
        s.max_service_gap_us != 0U || s.released_mask != 0U || s.high_mask != 0U ||
        s.low_mask != 0U || s.timeout_mask != 0U || !emptyCleanup(s.cleanup)) return false;
    for (unsigned i = 0U; i < 4U; ++i)
        if (!emptyPad(s.pad[i]) || s.status_by_pad[i] != 0) return false;
    return true;
}
// All offsets are admitted into a single short frame before any ordering check.
bool inside(const Snapshot& s, std::uint32_t time) {
    return time - s.started_us <= s.checked_us - s.started_us;
}
bool ordered(const Snapshot& s, std::uint32_t earlier, std::uint32_t later) {
    return inside(s, earlier) && inside(s, later) &&
        earlier - s.started_us <= later - s.started_us;
}
bool padValid(const Snapshot& s, unsigned i) {
    const auto bit = static_cast<std::uint8_t>(1U << i);
    const auto& p = s.pad[i];
    if (s.status_by_pad[i] != 0 && s.status_by_pad[i] != 1) return false;
    if ((s.released_mask & bit) == 0U)
        return emptyPad(p) && s.status_by_pad[i] == 0;
    const auto charge = p.release_before_us - s.drive_completed_us;
    if (!ordered(s, s.drive_completed_us, p.release_before_us) ||
        !ordered(s, p.release_before_us, p.release_after_us) ||
        charge < config::QTR_CHARGE_US + config::QTR_QUANTIZATION_US ||
        p.release_after_us - s.drive_completed_us >= config::QTR_CHARGE_MAX_US)
        return false;
    if (i != 0U && !ordered(s, s.pad[i - 1U].release_after_us, p.release_before_us))
        return false;
    if ((s.high_mask & bit) != 0U) {
        if (!ordered(s, s.pad[3].release_after_us, p.last_high_before_us)) return false;
        const auto elapsed = p.last_high_before_us - p.release_after_us;
        const auto lower = elapsed > config::QTR_QUANTIZATION_US ?
            elapsed - config::QTR_QUANTIZATION_US : 0U;
        if (p.lower_us != lower) return false;
    } else if (p.last_high_before_us != 0U || p.lower_us != 0U) return false;
    if ((s.low_mask & bit) != 0U) {
        const auto after = (s.high_mask & bit) != 0U ?
            p.last_high_before_us : s.pad[3].release_after_us;
        return ordered(s, after, p.first_low_after_us) &&
            static_cast<std::uint64_t>(p.first_low_after_us - p.release_before_us) +
                config::QTR_QUANTIZATION_US == p.upper_us && p.upper_us > p.lower_us;
    }
    if (p.first_low_after_us != 0U || p.upper_us != 0U) return false;
    if ((s.timeout_mask & bit) != 0U && p.lower_us < config::QTR_TIMEOUT_US) return false;
    return true;
}
bool frameValid(const Snapshot& s) {
    if (!masksValid(s) || s.checked_us - s.started_us >= config::QTR_FRAME_MAX_US ||
        !inside(s, s.drive_completed_us) || s.advances > config::QTR_MAX_ADVANCES ||
        s.max_service_gap_us > s.checked_us - s.started_us) return false;
    for (unsigned i = 0U; i < 4U; ++i) if (!padValid(s, i)) return false;
    return true;
}
bool complete(const Snapshot& s) {
    const auto& c = s.cleanup;
    if (s.status != Status::OK || !s.valid || s.released_mask != ALL ||
        (s.low_mask | s.timeout_mask) != ALL || s.advances == 0U || !frameValid(s) ||
        c.attempted_mask != ALL || c.failed_mask != 0U || c.skipped_mask != 0U ||
        c.nonneutral_mask != 0U || c.deadline_exceeded ||
        !ordered(s, c.started_us, c.completed_us) ||
        c.completed_us - c.started_us >= config::QTR_CLEANUP_MAX_US ||
        s.completed_us != c.completed_us || s.checked_us != s.completed_us) return false;
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto last = (s.low_mask & (1U << i)) != 0U ?
            s.pad[i].first_low_after_us : s.pad[i].last_high_before_us;
        if (c.status[i] != 0 || !ordered(s, last, c.started_us)) return false;
    }
    return true;
}
bool pending(const Snapshot& s) {
    if (s.phase == Phase::NOT_STARTED)
        return s.status == Status::NOT_INITIALIZED && s.checked_us == 0U && emptyFrame(s);
    if (s.phase == Phase::IDLE) return s.status == Status::OK && emptyFrame(s);
    if (s.status != Status::OK || s.valid || s.completed_us != 0U ||
        !emptyCleanup(s.cleanup) || !masksValid(s)) return false;
    for (const auto status : s.status_by_pad) if (status != 0 && status != 1) return false;
    if (s.phase == Phase::CHARGING)
        return s.released_mask == 0U;
    return s.phase == Phase::DISCHARGING && s.released_mask == ALL;
}
bool fault(const Snapshot& s) {
    return !s.valid && s.status >= Status::INVALID_CONFIG && s.status <= Status::CANCELLED;
}
Qualification classify(const Snapshot& s, const std::uint32_t* thresholds,
                       std::uint8_t& candidates) {
    candidates = 0U;
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto bit = static_cast<std::uint8_t>(1U << i);
        if ((s.low_mask & bit) != 0U && s.pad[i].upper_us <= thresholds[i])
            candidates |= bit;
        else if (s.pad[i].lower_us < thresholds[i]) return Qualification::AMBIGUOUS;
    }
    return Qualification::VALID;
}
} // namespace

RawQualification validateRaw(const Snapshot& snapshot) {
    switch (snapshot.phase) {
    case Phase::NOT_STARTED: case Phase::IDLE: case Phase::CHARGING: case Phase::DISCHARGING:
        return pending(snapshot) ? RawQualification::ABSENT : RawQualification::INVALID;
    case Phase::FAULT:
        return fault(snapshot) ? RawQualification::PROVIDER_FAULT : RawQualification::INVALID;
    case Phase::COMPLETE:
        return complete(snapshot) ? RawQualification::VALID : RawQualification::INVALID;
    default: return RawQualification::INVALID;
    }
}

bool validThresholds(const Thresholds& thresholds) {
    for (const auto value : thresholds.white_us)
        if (value == 0U || value > config::QTR_TIMEOUT_US) return false;
    return true;
}

namespace {
void identity(core::LineEvidence& line, const Snapshot& snapshot) {
    line.sequence = snapshot.sequence;
    line.started_us = snapshot.started_us;
    line.completed_us = snapshot.completed_us;
}
Qualification applyControl(fsm::RobotInput& input, const Snapshot& snapshot,
                           const std::uint32_t* thresholds, std::uint32_t version) {
    input.line = {};
    input.line.explicit_values = true;
    input.line.presence = core::LinePresence::INVALID;
    input.line.threshold_version = version;
    const auto raw = validateRaw(snapshot);
    input.line.contract_valid = raw != RawQualification::INVALID;
    if (raw == RawQualification::ABSENT) {
        input.line.presence = core::LinePresence::ABSENT;
        return Qualification::ABSENT;
    }
    if (raw != RawQualification::VALID) return Qualification::INVALID;
    std::uint8_t candidates = 0U;
    const auto qualified = classify(snapshot, thresholds, candidates);
    if (qualified != Qualification::VALID) return qualified;
    input.line.presence = core::LinePresence::VALID;
    identity(input.line, snapshot);
    input.line.white_candidates = candidates;
    return qualified;
}
} // namespace

Qualification applySnapshot(fsm::RobotInput& input, const Snapshot& snapshot) {
    return applyControl(input, snapshot, config::QTR_WHITE_US, 0U);
}
Qualification applySnapshot(fsm::RobotInput& input, const Snapshot& snapshot,
                            const Thresholds& thresholds) {
    if (!validThresholds(thresholds)) {
        input.line = {};
        input.line.explicit_values = true;
        input.line.contract_valid = false;
        input.line.presence = core::LinePresence::INVALID;
        input.line.threshold_version = thresholds.version;
        return Qualification::INVALID;
    }
    return applyControl(input, snapshot, thresholds.white_us, thresholds.version);
}
RawQualification applyRawSnapshot(fsm::RobotInput& input, const Snapshot& snapshot) {
    input.line = {};
    input.line.explicit_values = true;
    input.line.use = core::LineUse::CALIBRATION;
    input.line.presence = core::LinePresence::INVALID;
    const auto raw = validateRaw(snapshot);
    input.line.contract_valid = raw != RawQualification::INVALID;
    if (raw == RawQualification::ABSENT) input.line.presence = core::LinePresence::ABSENT;
    if (raw == RawQualification::VALID) {
        input.line.presence = core::LinePresence::VALID;
        identity(input.line, snapshot);
    }
    return raw;
}
} // namespace line_qtr
