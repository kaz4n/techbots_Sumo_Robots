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
