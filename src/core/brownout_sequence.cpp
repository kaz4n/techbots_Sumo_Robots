// Counts the fixed D244 B7 electrical endpoint dwells from owned applied receipts.
// Keeps one finite attempt and preserves terminal evidence without motor authority.
// Independent contract fixtures cover full pairs, receipt boundaries and interruption.
#include "brownout_sequence.h"
#include "../config.h"
#include <cmath>

namespace brownout_sequence {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
constexpr std::uint32_t REACH_US = config::BROWNOUT_REACH_MS * 1000U;
constexpr std::uint32_t DWELL_US = config::BROWNOUT_DWELL_MS * 1000U;
bool active(Phase phase) { return phase == Phase::REACH || phase == Phase::DWELL; }
bool validDuty(float duty) { return std::isfinite(duty) && duty >= -1.0F && duty <= 1.0F; }
} // namespace

bool Sequence::start(std::uint32_t t_us) {
    if (report_.consumed) return false;
    report_.consumed = report_.started = true;
    report_.started_us = last_decision_us_ = t_us;
    selectLeg(t_us);
    return true;
}

bool Sequence::acceptReceipt(std::uint32_t t_us, const Receipt& receipt) {
    if (!receipt.valid || receipt.token == 0U || receipt.leg_index != report_.leg_index ||
        (report_.receipt_seen && receipt.token <= report_.last_receipt.token) ||
        !validDuty(receipt.duty_l) || !validDuty(receipt.duty_r) ||
        (!receipt.enabled && (receipt.duty_l != 0.0F || receipt.duty_r != 0.0F))) {
        terminate(Phase::ABORTED, Reason::APPLICATION, t_us);
        return false;
    }
    const auto gap = t_us - last_decision_us_;
    const auto applied_gap = report_.receipt_seen ?
        receipt.applied_us - report_.last_receipt.applied_us : receipt.applied_us - report_.started_us;
    if (receipt.applied_us - last_decision_us_ > gap || applied_gap >= HALF_RANGE) {
        terminate(Phase::ABORTED, Reason::CLOCK_ORDER, t_us);
        return false;
    }
    if (applied_gap > config::BROWNOUT_RECEIPT_MAX_GAP_US) {
        terminate(Phase::ABORTED, Reason::RECEIPT_GAP, t_us);
        return false;
    }
    report_.last_receipt = receipt;
    report_.receipt_seen = true;
    return true;
}

Report Sequence::step(std::uint32_t t_us, const Receipt& receipt) {
    if (!active(report_.phase) || t_us == last_decision_us_) return report_;
    const auto gap = t_us - last_decision_us_;
    if (gap >= HALF_RANGE) terminate(Phase::ABORTED, Reason::CLOCK_ORDER, t_us);
    else if (gap > config::BROWNOUT_RECEIPT_MAX_GAP_US)
        terminate(Phase::ABORTED, Reason::RECEIPT_GAP, t_us);
    if (!active(report_.phase) || !acceptReceipt(t_us, receipt)) return report_;
    last_decision_us_ = t_us;
    const bool full = receipt.enabled && receipt.duty_l == report_.duty_l &&
        receipt.duty_r == report_.duty_r;
    if (report_.phase == Phase::REACH) {
        if (full && receipt.applied_us - report_.leg_started_us < REACH_US) {
            report_.phase = Phase::DWELL;
            report_.endpoint_valid = true;
            report_.endpoint_started_us = report_.last_endpoint_us = receipt.applied_us;
        } else if (t_us - report_.leg_started_us >= REACH_US) {
            terminate(Phase::ABORTED, Reason::REACH_TIMEOUT, t_us);
        }
        return report_;
    }
    if (!full) terminate(Phase::ABORTED, Reason::ENDPOINT_LOST, t_us);
    else {
        report_.last_endpoint_us = receipt.applied_us;
        if (receipt.applied_us - report_.endpoint_started_us >= DWELL_US) completeLeg(t_us);
    }
    return report_;
}

void Sequence::selectLeg(std::uint32_t t_us) {
    report_.phase = Phase::REACH;
    report_.leg_started_us = t_us;
    report_.endpoint_valid = false;
    report_.endpoint_started_us = report_.last_endpoint_us = 0U;
    report_.duty_l = report_.duty_r = (report_.leg_index & 1U) == 0U ?
        config::BROWNOUT_FULL_DUTY : -config::BROWNOUT_FULL_DUTY;
}

void Sequence::completeLeg(std::uint32_t t_us) {
    ++report_.completed_legs;
    report_.completed_cycles = static_cast<std::uint8_t>(report_.completed_legs / 2U);
    report_.completed_endpoint_started_us = report_.endpoint_started_us;
    report_.completed_endpoint_last_us = report_.last_endpoint_us;
    if (report_.completed_cycles == config::BROWNOUT_CYCLES) {
        terminate(Phase::COMPLETE, Reason::NONE, t_us);
        return;
    }
    ++report_.leg_index;
    selectLeg(t_us);
}

bool Sequence::interrupt(Reason reason, std::uint32_t t_us) {
    if (reason == Reason::NONE || reason > Reason::RESET_REQUEST ||
        (!active(report_.phase) && !(report_.phase == Phase::NOT_STARTED &&
                                    reason == Reason::RESET_REQUEST))) return false;
    terminate(Phase::ABORTED, reason, t_us);
    return true;
}

void Sequence::terminate(Phase phase, Reason reason, std::uint32_t t_us) {
    report_.phase = phase;
    report_.reason = reason;
    report_.consumed = report_.terminal_valid = true;
    report_.terminal_us = t_us;
    report_.duty_l = report_.duty_r = 0.0F;
}
} // namespace brownout_sequence
