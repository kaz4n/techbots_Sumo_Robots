// Holds the documented BEHAVIOR.md B16 development defaults.
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
// D076 copies HARDWARE3 proposals for compile-only HAL development, not approval.
inline constexpr std::uint32_t OPP_INPUT_PINS[7] = {11U, 12U, 13U, 16U, 17U, 18U, 19U};
// D077 names unchanged HARDWARE3 proposals; no PINMAP or waveform approval.
inline constexpr std::uint32_t MOTOR_PWM_PINS[4] = {3U, 5U, 6U, 9U};
inline constexpr std::uint32_t MOTOR_ENABLE_PIN = 10U;
// New D077 development carrier/settle limits, not measured timing or B16 tuning.
inline constexpr std::uint32_t MOTOR_PWM_HZ = 10000U; // Hz
inline constexpr std::uint32_t MOTOR_PWM_SETTLE_US = 150U; // us, whole settle pass
inline constexpr std::uint32_t MOTOR_PWM_SETTLE_MAX_POLLS = 4096U; // count-name exception
// D078 native ADC development bounds and unchanged HARDWARE2/3 proposal.
// Nominal scaling is not measured divider/reference calibration or PINMAP OK.
inline constexpr std::uint32_t VBAT_INPUT_PIN = 14U; // A0 / PA4 / ADC1 channel9
inline constexpr float VBAT_ADC_REFERENCE_V = 3.3F; // nominal V
inline constexpr float VBAT_DIVIDER_RATIO = 122.0F / 22.0F; // dimensionless exception
inline constexpr std::uint32_t VBAT_ADC_REGULATOR_US = 100U;
inline constexpr std::uint32_t VBAT_ADC_CALIBRATION_US = 5000U;
inline constexpr std::uint32_t VBAT_ADC_POST_CAL_US = 2U;
inline constexpr std::uint32_t VBAT_ADC_ENABLE_US = 100U;
inline constexpr std::uint32_t VBAT_ADC_CONVERSION_US = 100U;
inline constexpr std::uint32_t VBAT_ADC_SHUTDOWN_US = 100U;
inline constexpr std::uint32_t VBAT_ADC_SETUP_MAX_POLLS = 65536U; // count exception
inline constexpr std::uint32_t VBAT_ADC_READ_MAX_POLLS = 4096U; // count exception
// D079 installed Qwiic route and conditional native timing; not PINMAP approval.
// Address remains a development selection until the actual AD0 strap is checked.
inline constexpr std::uint32_t IMU_I2C_ADDRESS = 0x68U; // 7-bit address exception
inline constexpr std::uint32_t IMU_I2C_GPIO_PORT = 3U; // port D, zero-based exception
inline constexpr std::uint32_t IMU_I2C_SCL_PIN = 12U; // installed PD12
inline constexpr std::uint32_t IMU_I2C_SDA_PIN = 13U; // installed PD13
inline constexpr std::uint32_t IMU_I2C_AF = 4U; // installed alternate-function exception
inline constexpr std::uint32_t IMU_I2C_TIMINGR = 0x40EB202CU; // register-value exception
inline constexpr std::uint32_t IMU_I2C_SETUP_US = 100U;
inline constexpr std::uint32_t IMU_I2C_TRANSFER_US = 600U;
inline constexpr std::uint32_t IMU_I2C_CLEANUP_US = 50U;
inline constexpr std::uint32_t IMU_I2C_MAX_POLLS = 8192U; // count exception
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
inline constexpr std::uint32_t LOG_HZ = 25U; // Hz; D-072 B15 low-memory fallback
inline constexpr std::uint32_t BTN_DEBOUNCE_MS = 20U; // ms
inline constexpr std::uint32_t BTN_LONG_MS = 1000U; // ms
inline constexpr std::uint32_t MODE_SHORT_MS = 600U; // ms; existing B13 strict short-press bound
inline constexpr std::uint32_t MODE_DEFAULT = 1U; // mode
// B6 specifies a 1 s battery filter outside its B16 table; unchanged spec value.
inline constexpr std::uint32_t VBAT_FILTER_MS = 1000U; // ms, B6
inline constexpr std::uint32_t REFLANK_WINDOW_MS = 10000U; // ms, B11.3 rolling window
inline constexpr std::uint32_t LOG_EVENT_CAPACITY = 4096U; // events, B15/D-028
inline constexpr std::uint32_t LOG_FRAME_WINDOW_MS = 200000U; // ms, B15 minimum window
// D-069 includes the initial frame and a coalesced or off-cadence final frame.
inline constexpr std::uint64_t LOG_FRAME_CAPACITY =
    (static_cast<std::uint64_t>(LOG_FRAME_WINDOW_MS) * LOG_HZ + 999U) / 1000U + 1U;
inline constexpr float EDGE_FWD_INNER_RATIO = 0.70F; // ratio, B4.2/D-021
inline constexpr std::uint32_t EDGE_SIDE_TURN_DEG = 45U; // deg, B4.2 side row/B4.3
inline constexpr std::uint32_t TICK_OVERRUN_PERCENT = 1U; // percent, B14 warning threshold
inline constexpr std::uint32_t RECENT_EDGE_MS = 5000U; // ms, B8/B11 inward/side history
inline constexpr std::uint32_t SEARCH_SCAN_DEG = 360U; // deg, B8 full directed sweep
// B3 service boundaries and the human-approved D-024 minimum sample count.
inline constexpr std::uint32_t CAL_START_MS = 1500U; // ms after qualified release
inline constexpr std::uint32_t CAL_END_MS = 4500U; // ms, exclusive sample endpoint
inline constexpr std::uint32_t CAL_MIN_SAMPLES = 2U; // samples, D-024
inline constexpr std::uint32_t COUNTDOWN_LINE_WARN_MS = 1000U; // ms before GO
inline constexpr std::uint32_t COUNTDOWN_SNAPSHOT_MS = 300U; // ms before GO
// P0 diagnostic-only defaults; no behavior tuning or proposed pin assignments.
inline constexpr std::uint32_t P0_SCROLL_MS = 100U;
inline constexpr std::uint32_t P0_COUNTER_MS = 1000U;
inline constexpr std::uint32_t P0_MONITOR_TIMEOUT_US = 100000U; // D-062 diagnostic only
inline constexpr std::uint32_t P0_MONITOR_BAUD_BPS = 115200U; // validate installed link, never reconfigure
inline constexpr std::uint32_t P0_JITTER_SAMPLES = 60000U;
inline constexpr std::uint32_t P0_JITTER_HISTOGRAM_US = 1000U;
inline constexpr std::uint32_t P0_ADC_SAMPLES = 1000U; // D-063 startup-only calls
inline constexpr std::uint32_t P0_ADC_PIN = 14U; // installed A0; diagnostic only, not PINMAP OK
inline constexpr std::uint32_t P0_GPIO_SAMPLES = 400U; // D-064 fixed RAM diagnostic
inline constexpr std::uint32_t P0_GPIO_PIN = 50U; // installed LED_BUILTIN/LED3_R, not D13
inline constexpr std::uint32_t P0_QTR_SAMPLES_PER_MODE = 100U; // D-065 diagnostic datasets
inline constexpr std::uint32_t P0_QTR_GUARD_POLLS = 4096U; // finite charge/observation guard
inline constexpr std::uint32_t P0_QTR_PINS[4] = {2U, 4U, 7U, 8U}; // installed D2/D4/D7/D8; no PINMAP approval
inline constexpr std::uint32_t P0_QTR_QUANTIZATION_US = 1U; // additional clock tick after requested charge
} // namespace config
