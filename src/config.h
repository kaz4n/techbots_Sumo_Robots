// Holds the unchanged BEHAVIOR.md B16 defaults.
// Centralizes tunables without asserting that proposed hardware pins are verified.
// P0 scaffold compiles this header; behavior and target tests follow their gates.
#pragma once
#include <cstdint>

#ifndef MATCH
#define MATCH 0
#endif
#ifndef MOTORS_ALLOWED
#define MOTORS_ALLOWED 0
#endif
static_assert(MATCH == 0 || MATCH == 1, "MATCH must be 0 or 1");
static_assert(MOTORS_ALLOWED == 0 || MOTORS_ALLOWED == 1, "MOTORS_ALLOWED must be 0 or 1");

namespace config {
// Names follow B16 verbatim, including its count/ratio/gain naming exceptions.
// Pin assignments await P0 source verification and human PINMAP OK.
inline constexpr std::uint32_t COUNTDOWN_MS = 5000U; // ms
inline constexpr std::uint32_t COUNTDOWN_MARGIN_MS = 100U; // ms
inline constexpr std::uint32_t TICK_US = 1000U; // us
inline constexpr std::uint32_t QTR_CHARGE_US = 10U; // us
inline constexpr std::uint32_t QTR_TIMEOUT_US = 1500U; // us
inline constexpr std::uint32_t QTR_WHITE_US[4] = {300U, 300U, 300U, 300U};
inline constexpr std::uint32_t QTR_CONFIRM_TICKS = 1U; // ticks
inline constexpr std::uint32_t QTR_STUCK_MS = 1500U; // ms
inline constexpr std::uint32_t OPP_ACTIVE_LOW_MASK = 0x78U; // bits
inline constexpr std::uint32_t OPP_SET_TICKS = 2U; // ticks
inline constexpr std::uint32_t OPP_CLEAR_MS = 30U; // ms
inline constexpr std::uint32_t OPP_STUCK_MS = 5000U; // ms
inline constexpr float CAL_MAX_SPREAD_DPS = 2.0F; // dps
inline constexpr float SEARCH_DUTY_MAX = 0.30F; // duty
inline constexpr float SCAN_DUTY = 0.45F; // duty
inline constexpr float TURN_DUTY = 0.80F; // duty
inline constexpr float TURN_MIN_DUTY = 0.25F; // duty
inline constexpr float K_TURN_PER_DEG = 0.02F; // duty/deg
inline constexpr std::uint32_t HEADING_TOL_DEG = 5U; // deg
inline constexpr std::uint32_t TURN_TIMEOUT_MS = 700U; // ms
inline constexpr float TURN_MS_PER_DEG = 2.0F; // ms/deg
inline constexpr std::uint32_t SEARCH_MEMORY_MS = 3000U; // ms
inline constexpr std::uint32_t SEARCH_ADVANCE_MS = 300U; // ms
inline constexpr float TRACK_DUTY = 0.45F; // duty
inline constexpr float K_TRACK_PER_DEG = 0.02F; // duty/deg
inline constexpr std::uint32_t ATTACK_ENTER_TICKS = 3U; // ticks
inline constexpr float ATTACK_APPROACH_DUTY = 0.60F; // duty
inline constexpr float ATTACK_DUTY = 1.00F; // duty
inline constexpr std::uint32_t CONTACT_TICKS = 20U; // ticks
inline constexpr float IMPACT_G = 1.5F; // g
inline constexpr float SLEW_DUTY_PER_MS = 0.02F; // duty/ms
inline constexpr float V_NOM_V = 11.1F; // V
inline constexpr float VBAT_MIN_COMP_V = 9.0F; // V
inline constexpr float VBAT_WARN_V = 10.8F; // V
inline constexpr float EDGE_BACK_DUTY = 0.80F; // duty
inline constexpr std::uint32_t EDGE_BACK_MS = 120U; // ms
inline constexpr std::uint32_t EDGE_BACK_LONG_MS = 180U; // ms
inline constexpr std::uint32_t EDGE_TURN_DEG = 120U; // deg
inline constexpr std::uint32_t EDGE_TURN_FULL_DEG = 160U; // deg
inline constexpr std::uint32_t EDGE_FWD_MS = 200U; // ms
inline constexpr std::uint32_t EDGE_MAX_REPLANS = 3U; // count
inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS = 0U; // ms
inline constexpr std::uint32_t PHANTOM_WINDOW_MS = 1500U; // ms
inline constexpr std::uint32_t PHANTOM_MS = 3000U; // ms
inline constexpr std::uint32_t PHANTOM_MASK_DEG = 25U; // deg
inline constexpr std::uint32_t STALL_MS = 1000U; // ms
inline constexpr float STALL_MIN_DUTY = 0.80F; // duty
inline constexpr std::uint32_t STALL_DEFLECT_DEG = 25U; // deg
inline constexpr std::uint32_t STALL_USE_IMU = 0U; // flag
inline constexpr float STALL_MIN_DISP_M = 0.10F; // m
inline constexpr std::uint32_t REFLANK_BACK_MS = 150U; // ms
inline constexpr float REFLANK_BACK_DUTY = 0.80F; // duty
inline constexpr std::uint32_t REFLANK_PIVOT_DEG = 60U; // deg
inline constexpr std::uint32_t REFLANK_ARC_MS = 400U; // ms
inline constexpr float REFLANK_ARC_RATIO = 0.40F; // ratio
inline constexpr std::uint32_t REFLANK_MAX_PER_10S = 2U; // count
inline constexpr std::uint32_t ALL_IN_MS = 1500U; // ms
inline constexpr std::uint32_t DEFEND_TIMEOUT_MS = 800U; // ms
inline constexpr std::uint32_t DEFEND_EVADE_FIRST = 0U; // flag
inline constexpr std::uint32_t EVADE_MS = 200U; // ms
inline constexpr float OPENER_DUTY_MAX = 0.85F; // duty
inline constexpr std::uint32_t SS_PIVOT_DEG = 50U; // deg
inline constexpr std::uint32_t SS_DRIVE_MS = 250U; // ms
inline constexpr std::uint32_t SS_TURNIN_DEG = 110U; // deg
inline constexpr std::uint32_t DIRECT_MS = 400U; // ms
inline constexpr std::uint32_t ARC_PIVOT_DEG = 80U; // deg
inline constexpr float ARC_RATIO = 0.45F; // ratio
inline constexpr float ARC_DUTY = 0.70F; // duty
inline constexpr std::uint32_t ARC_SWEEP_DEG = 200U; // deg
inline constexpr std::uint32_t ARC_MAX_MS = 1500U; // ms
inline constexpr std::uint32_t WAIT_MAX_MS = 2000U; // ms
inline constexpr std::uint32_t APPROACH_WINDOW_MS = 300U; // ms
inline constexpr std::uint32_t LOG_HZ = 50U; // Hz
inline constexpr std::uint32_t BTN_DEBOUNCE_MS = 20U; // ms
inline constexpr std::uint32_t BTN_LONG_MS = 1000U; // ms
inline constexpr std::uint32_t MODE_DEFAULT = 1U; // mode
// P0 diagnostic-only defaults; no behavior tuning or proposed pin assignments.
inline constexpr std::uint32_t P0_SCROLL_MS = 100U;
inline constexpr std::uint32_t P0_COUNTER_MS = 1000U;
inline constexpr std::uint32_t P0_JITTER_SAMPLES = 60000U;
inline constexpr std::uint32_t P0_JITTER_HISTOGRAM_US = 1000U;
} // namespace config
