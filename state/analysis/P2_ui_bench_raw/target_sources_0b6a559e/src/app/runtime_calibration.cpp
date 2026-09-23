// Sends one exact snippet for each genuine ordinary Runtime calibration commit.
// Shares the existing output owner without retaining payload or retrying intent.
// Independent D105 actual-Runtime authority, transport and parser tests verify it.
#include "runtime.h"
#include <limits>

namespace app {
const CalibrationOutputReport& Runtime::calibrationOutput() const {
    static const CalibrationOutputReport inactive;
#if !MATCH
    if (calibrationOutputEnabled()) return calibration_output_;
#endif
    return inactive;
}

#if !MATCH
namespace {
using OutputPhase = CalibrationOutputPhase;
using OutputReason = CalibrationOutputReason;
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

std::uint32_t outputAge(std::uint32_t age, std::uint32_t delta) {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    return delta > maximum - age ? maximum : age + delta;
}

bool outputFailed(OutputReason reason) {
    return reason == OutputReason::TIME_ORDER || reason == OutputReason::TOKEN_ORDER ||
        reason == OutputReason::FORMAT || reason == OutputReason::PORT ||
        reason == OutputReason::STALL || reason == OutputReason::TOTAL;
}
} // namespace

bool Runtime::calibrationOutputEnabled() const {
    return grants_.dump_enabled && grants_.calibration_output_enabled;
}

void Runtime::endCalibrationOutput(OutputReason reason) {
    if (!calibrationOutputEnabled()) return;
    const bool active = calibration_output_.phase == OutputPhase::ACTIVE;
    const bool intent = calibration_output_.phase == OutputPhase::INACTIVE &&
        calibration_output_.version != 0U;
    if (!active && !intent) return;
    calibration_output_.phase = active ? (outputFailed(reason) ?
        OutputPhase::FAILED : OutputPhase::CANCELLED) : OutputPhase::REFUSED;
    calibration_output_.reason = reason;
    if (active && dump_port_.output.cancel)
        dump_port_.output.cancel(dump_port_.output.context);
}

CalibrationOutputReason Runtime::calibrationOutputOrder(std::uint32_t now_us) const {
    const auto& tick = transaction_.report();
    if (tick.robot.token == 0U || tick.robot.token == std::numeric_limits<std::uint64_t>::max())
        return OutputReason::TOKEN_ORDER;
    if (output_last_token_ != 0U) {
        if (tick.robot.token == output_last_token_) {
            if (tick.decision_us != output_decision_us_) return OutputReason::TOKEN_ORDER;
        } else {
            if (tick.robot.token < output_last_token_ || tick.robot.token - output_last_token_ != 1U)
                return OutputReason::TOKEN_ORDER;
            const auto elapsed = tick.decision_us - output_decision_us_;
            if (elapsed == 0U || elapsed >= HALF_RANGE) return OutputReason::TIME_ORDER;
        }
    }
    if (now_us - output_observed_us_ >= HALF_RANGE) return OutputReason::TIME_ORDER;
    const auto& bank = report_.calibration.thresholds;
    if (report_.calibration.phase != qtr_cal::Phase::SUCCESS ||
        report_.calibration.reason != qtr_cal::Reason::NONE ||
        !line_qtr::validThresholds(bank) || bank.version != output_bank_.version)
        return OutputReason::BANK_CHANGED;
    for (unsigned i = 0U; i < 4U; ++i)
        if (bank.white_us[i] != output_bank_.white_us[i]) return OutputReason::BANK_CHANGED;
    const auto delta = now_us - output_observed_us_;
    if (std::uint64_t{outputAge(output_total_us_, delta)} >=
        std::uint64_t{config::DUMP_TOTAL_MS} * 1000U) return OutputReason::TOTAL;
    if (std::uint64_t{outputAge(output_stall_us_, delta)} >=
        std::uint64_t{config::DUMP_STALL_MS} * 1000U) return OutputReason::STALL;
    return OutputReason::NONE;
}

CalibrationOutputReason Runtime::calibrationOutputIssue(std::uint32_t now_us) const {
    const auto& tick = transaction_.report();
    const auto& robot = tick.robot;
    if (!dumpReceiptValid() || tick.applied.fault != motors::Fault::NONE)
        return OutputReason::RECEIPT;
    if (report_.phase != RuntimePhase::RUNNING || report_.service_only || !inhibitedIdle(now_us) ||
        robot.contract_faults != 0U || robot.escape_fault != edge::EscapeFault::NONE ||
        !report_.raw_lines || !robot.menu.selection.service_menu ||
        robot.menu.selection.service != countdown::Service::QTR_CAL)
        return OutputReason::CONTEXT;
    const auto& buttons = decision_input_.buttons;
    const auto& line = decision_input_.line;
    if (!buttons.explicit_values || !buttons.contract_valid ||
        buttons.presence != core::ButtonPresence::VALID ||
        !decision_input_.opponent_fresh || !opponentsFresh(tick.decision_us) ||
        !line.explicit_values || !line.contract_valid || line.use != core::LineUse::CALIBRATION ||
        line.presence == core::LinePresence::INVALID) return OutputReason::SOURCE;
    return calibrationOutputOrder(now_us);
}

bool Runtime::prepareCalibrationOutput(bool committed) {
    if (!calibrationOutputEnabled()) return true;
    const auto version = report_.calibration.thresholds.version;
    const bool intent = committed && version > calibration_output_.version;
    if (intent) {
        endCalibrationOutput(OutputReason::BANK_CHANGED);
        calibration_output_ = {};
        calibration_output_.token = transaction_.report().robot.token;
        calibration_output_.version = version;
        output_bank_ = report_.calibration.thresholds;
        output_last_token_ = 0U;
        output_total_us_ = output_stall_us_ = 0U;
    }
    if (!intent && calibration_output_.phase != OutputPhase::ACTIVE) return true;
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    if (intent) output_observed_us_ = now;
    const auto issue = calibrationOutputIssue(now);
    if (issue != OutputReason::NONE) endCalibrationOutput(issue);
    return clock(now);
}

bool Runtime::writeCalibrationOutput(std::uint32_t now_us) {
    char snippet[qtr_cal::CONFIG_SNIPPET_CAPACITY];
    std::size_t size = 0U;
    if (qtr_cal::formatConfig(report_.calibration, snippet, sizeof(snippet), size) !=
        qtr_cal::FormatStatus::OK || size == 0U || calibration_output_.bytes >= size) {
        endCalibrationOutput(OutputReason::FORMAT);
        return clock(now_us);
    }
    if (!clock(now_us)) return false;
    const auto issue = calibrationOutputIssue(now_us);
    if (issue != OutputReason::NONE) {
        endCalibrationOutput(issue);
        return clock(now_us);
    }
    const auto remaining = size - calibration_output_.bytes;
    const auto offered = remaining < config::DUMP_PAYLOAD_BYTES ?
        remaining : config::DUMP_PAYLOAD_BYTES;
    const auto delta = now_us - output_observed_us_;
    output_total_us_ = outputAge(output_total_us_, delta);
    output_stall_us_ = outputAge(output_stall_us_, delta);
    output_observed_us_ = now_us;
    output_last_token_ = transaction_.report().robot.token;
    output_decision_us_ = transaction_.report().decision_us;
    calibration_output_.phase = OutputPhase::ACTIVE;
    // The Port borrows only for this call; a pending retry re-renders identical bytes.
    const auto result = dump_port_.output.write(dump_port_.output.context,
        snippet + calibration_output_.bytes, offered);
    const bool progressed = result.status == recorder::dump::WriteStatus::PROGRESS &&
        result.count > 0U && result.count <= offered;
    if (progressed) calibration_output_.bytes += static_cast<std::uint32_t>(result.count);
    // An acknowledged prefix remains evidence even if the following clock fails.
    if (!clock(now_us)) return false;
    if (progressed) {
        output_total_us_ = outputAge(output_total_us_, now_us - output_observed_us_);
        output_observed_us_ = now_us;
        output_stall_us_ = 0U;
        if (calibration_output_.bytes == size)
            calibration_output_.phase = OutputPhase::SENT_UNCONFIRMED;
    } else if (result.status != recorder::dump::WriteStatus::PENDING || result.count != 0U)
        endCalibrationOutput(OutputReason::PORT);
    return clock(now_us);
}

bool Runtime::serviceCalibrationOutput() {
    if (!calibrationOutputEnabled() || (calibration_output_.phase != OutputPhase::ACTIVE &&
        (calibration_output_.phase != OutputPhase::INACTIVE || calibration_output_.version == 0U)))
        return true;
    std::uint32_t now = 0U;
    if (!clock(now)) return false;
    auto issue = calibrationOutputIssue(now);
    if (issue == OutputReason::NONE && dump_.report().phase == recorder::dump::Phase::ACTIVE)
        issue = OutputReason::CONTEXT;
    if (issue == OutputReason::NONE && (report_.dump_setup != recorder::dump::NativeStatus::OK ||
        !dump_port_.ready || !dump_port_.output.write || !dump_port_.output.cancel))
        issue = OutputReason::PORT;
    if (issue != OutputReason::NONE) {
        endCalibrationOutput(issue);
        return clock(now);
    }
    const bool ready = dump_port_.ready(dump_port_.context);
    if (!clock(now)) return false;
    issue = calibrationOutputIssue(now);
    if (issue == OutputReason::NONE && !ready) issue = OutputReason::LINUX_UNAVAILABLE;
    if (issue != OutputReason::NONE) {
        endCalibrationOutput(issue);
        return clock(now);
    }
    if (output_last_token_ == transaction_.report().robot.token) return true;
    return writeCalibrationOutput(now);
}
#endif
} // namespace app
