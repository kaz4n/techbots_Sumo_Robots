// Reports one bounded export of a genuine completed QTR calibration bank.
// Keeps local acknowledgement separate from host receipt or physical validation.
// Independent D105 actual-Runtime and strict snippet tests verify this contract.
#pragma once
#include <cstdint>

namespace app {
enum class CalibrationOutputPhase : std::uint8_t {
    INACTIVE, ACTIVE, SENT_UNCONFIRMED, CANCELLED, REFUSED, FAILED
};
enum class CalibrationOutputReason : std::uint8_t {
    NONE, CONTEXT, RECEIPT, SOURCE, TIME_ORDER, TOKEN_ORDER, BANK_CHANGED,
    LINUX_UNAVAILABLE, FORMAT, PORT, STALL, TOTAL, RESET
};
struct CalibrationOutputReport {
    std::uint64_t token = 0U;
    std::uint32_t version = 0U;
    std::uint32_t bytes = 0U;
    CalibrationOutputPhase phase = CalibrationOutputPhase::INACTIVE;
    CalibrationOutputReason reason = CalibrationOutputReason::NONE;
};
} // namespace app
