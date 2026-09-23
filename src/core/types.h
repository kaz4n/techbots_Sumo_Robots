// Defines the B0 values exchanged by pure decision modules.
// Keeps logical inputs independent of unverified pin assignments and ADC decoding.
// Host specification tests check inert defaults; later HAL tests must check real writes.
#pragma once
#include <cstdint>

namespace core {
enum class State : std::uint8_t {
    BOOT, IDLE, COUNTDOWN, OPENER, SEARCH, TRACK, ATTACK, DEFEND_TURN,
    EDGE_ESCAPE, REFLANK, STOPPED, DRIVE_TEST
};
enum class Mode : std::uint8_t {
    SIDESTEP_R = 1, SIDESTEP_L, DIRECT, ARC_R, ARC_L, WAIT
};
// Semantic input only: this does NOT assert that the A1 circuit can decode BOTH.
enum class ButtonLevel : std::uint8_t { NONE, START, MODE, BOTH };
enum class Event : std::uint8_t {
    START_RELEASE, GO, FIRST_NONZERO_DUTY, STATE_CHANGE, EDGE, CONTACT,
    STALL, REFLANK_PHASE, PHANTOM_SET, FAULT
};
// D084 pure evidence metadata. Values1..3 also identify B15 presence extensions.
enum class ImuPresence : std::uint8_t { ABSENT = 1, VALID = 2, INVALID = 3 };
struct ImuEvidence {
    bool explicit_values = false; // False preserves the existing imu_ok callers.
    bool contract_valid = true;
    ImuPresence gyro = ImuPresence::ABSENT;
    ImuPresence accel = ImuPresence::ABSENT;
    bool heading_available = false;
    bool heading_updated = false;
    std::uint32_t checked_us = 0;
    std::uint32_t observation_us = 0;
    std::uint32_t sequence = 0;
};
enum class LinePresence : std::uint8_t { ABSENT = 1, VALID = 2, INVALID = 3 };
struct LineEvidence {
    bool explicit_values = false; // Legacy uses observations_fresh plus raw times.
    bool contract_valid = true;
    LinePresence presence = LinePresence::ABSENT;
    std::uint32_t sequence = 0U;
    std::uint32_t started_us = 0U; // Earliest frame age, never delivery/cleanup time.
    std::uint32_t completed_us = 0U;
    std::uint8_t white_candidates = 0U; // Qualified intervals, before confirmation.
};
struct Inputs {
    std::uint32_t t_us = 0;
    std::uint8_t line_mask = 0;
    std::uint32_t line_raw_us[4] = {};
    std::uint8_t opp_raw_mask = 0;
    float heading_deg = 0.0F;
    float gyro_z_dps = 0.0F;
    float ax_g = 0.0F;
    float ay_g = 0.0F;
    bool imu_ok = false;
    float vbat_v = 0.0F;
    ButtonLevel button_level = ButtonLevel::NONE;
};
struct Outputs {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    bool motors_enabled = false;
    State ui_state = State::BOOT;
    // Recorder frame/event transport is deferred until the B15 contract is settled.
};
} // namespace core
