// Maps one native A1 result into explicit button evidence without debouncing.
// Unconfigured, unknown and overlapping raw windows never synthesize a release.
// Independent profile-variant and actual Robot/MotorGate tests verify this mapping.
#pragma once
#include "power.h"
#include "../core/fsm.h"

namespace ui {
enum class ButtonQualification : std::uint8_t {
    ABSENT, VALID, UNCONFIGURED, UNKNOWN, AMBIGUOUS, INVALID
};
struct ButtonDecode {
    ButtonQualification qualification = ButtonQualification::ABSENT;
    core::ButtonEvidence evidence;
    std::uint8_t candidate_mask = 0U; // NONE/START/MODE/BOTH bits0..3.
};
ButtonDecode decodeButtons(const power::ButtonSample& sample);
// Sets only input.buttons; decision time and all other inputs remain caller-owned.
ButtonQualification applyButtons(fsm::RobotInput& input, const power::ButtonSample& sample);
} // namespace ui
