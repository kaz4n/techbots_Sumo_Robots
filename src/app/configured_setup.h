// Maps explicit config declarations into the existing application setup grants.
// Leaves unverified defaults disabled and keeps each caller obligation independent.
// Spec-derived constant-expression and controlled entry tests verify D180.
#pragma once
#include "runtime.h"
#include "../config.h"

namespace app {
constexpr SetupGrants configuredSetupGrants() {
    SetupGrants grants{};
    grants.opponents = config::APP_GRANT_OPPONENTS != 0U;
    grants.adc_pair = config::APP_GRANT_ADC_PAIR != 0U;
    grants.qtr_exclusive_pads = config::APP_GRANT_QTR_EXCLUSIVE_PADS != 0U;
    grants.imu_enabled = config::APP_GRANT_IMU_ENABLED != 0U;
    grants.imu_power_confirmed = config::APP_GRANT_IMU_POWER_CONFIRMED != 0U;
    grants.mounting.confirmed = config::APP_GRANT_IMU_MOUNTING_CONFIRMED != 0U;
    for (unsigned axis = 0U; axis < 3U; ++axis)
        grants.mounting.body_axis[axis] = static_cast<std::int8_t>(config::APP_IMU_BODY_AXIS[axis]);
    grants.default_line_thresholds_confirmed = config::APP_GRANT_DEFAULT_LINE_THRESHOLDS != 0U;
    grants.matrix_enabled = config::APP_GRANT_MATRIX_ENABLED != 0U;
    grants.matrix.normal_startup = config::APP_GRANT_MATRIX_NORMAL_STARTUP != 0U;
    grants.matrix.exclusive_boot_owner = config::APP_GRANT_MATRIX_EXCLUSIVE_OWNER != 0U;
    grants.dump_enabled = config::APP_GRANT_DUMP_ENABLED != 0U;
    grants.dump.setup_phase = config::APP_GRANT_DUMP_SETUP_PHASE != 0U;
    grants.dump.exclusive_uart = config::APP_GRANT_DUMP_EXCLUSIVE_UART != 0U;
    grants.dump.ready_pin_owned = config::APP_GRANT_DUMP_READY_PIN_OWNED != 0U;
    grants.dump.framing_clean = config::APP_GRANT_DUMP_FRAMING_CLEAN != 0U;
    grants.dump.receive_stream = static_cast<recorder::dump::ReceiveStream>(config::APP_DUMP_RECEIVE_STREAM_ID);
    grants.dump.session = config::APP_DUMP_SESSION_ID;
    grants.dump_origin = static_cast<recorder::dump::Origin>(config::APP_DUMP_ORIGIN);
    grants.local_service_reset = config::APP_GRANT_LOCAL_SERVICE_RESET != 0U;
    grants.calibration_output_enabled = config::APP_GRANT_CALIBRATION_OUTPUT != 0U;
    return grants;
}
} // namespace app
