// Qualifies complete native RC intervals for explicit Robot line admission.
// Preserves ambiguous and absent readings without inventing a measured black value.
// Independent interval and actual native-to-Robot tests validate this pure mapping.
#pragma once
#include "line_qtr.h"
#include "../core/fsm.h"

namespace line_qtr {
enum class Qualification : std::uint8_t { ABSENT, VALID, AMBIGUOUS, INVALID };
// Never acquires, changes decision time or alters unrelated RobotInput fields.
// Provider fault/ambiguity maps INVALID presence; malformed records also clear
// contract_valid. NOT_STARTED/IDLE/active pending states map ABSENT, never fresh.
Qualification applySnapshot(fsm::RobotInput& input, const Snapshot& snapshot);
} // namespace line_qtr
