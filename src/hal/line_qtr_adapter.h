// Qualifies complete native RC intervals for explicit Robot line admission.
// Preserves ambiguous and absent readings without inventing a measured black value.
// Independent interval and actual native-to-Robot tests validate this pure mapping.
#pragma once
#include "line_qtr.h"
#include "../core/fsm.h"

namespace line_qtr {
enum class Qualification : std::uint8_t { ABSENT, VALID, AMBIGUOUS, INVALID };
enum class RawQualification : std::uint8_t { ABSENT, VALID, PROVIDER_FAULT, INVALID };
struct Thresholds {
    std::uint32_t white_us[4] = {config::QTR_WHITE_US[0], config::QTR_WHITE_US[1],
        config::QTR_WHITE_US[2], config::QTR_WHITE_US[3]};
    std::uint32_t version = 0U;
};
// Structural native evidence only; never compares a color threshold or decision age.
RawQualification validateRaw(const Snapshot& snapshot);
bool validThresholds(const Thresholds& thresholds); // Each value in1..QTR_TIMEOUT_US.
// Never acquires, changes decision time or alters unrelated RobotInput fields.
// Provider fault/ambiguity maps INVALID presence; malformed records also clear
// contract_valid. NOT_STARTED/IDLE/active pending states map ABSENT, never fresh.
Qualification applySnapshot(fsm::RobotInput& input, const Snapshot& snapshot);
// Checked RAM profile; unrelated RobotInput fields are preserved.
Qualification applySnapshot(fsm::RobotInput& input, const Snapshot& snapshot,
                            const Thresholds& thresholds);
// RAW never fabricates candidates; Robot accepts it only in inhibited BOOT/IDLE.
RawQualification applyRawSnapshot(fsm::RobotInput& input, const Snapshot& snapshot);
} // namespace line_qtr
