// Renders B3/B13/B14 into a fixed row-major 8x13 grayscale frame.
// Keeps display choices separate from sensor evidence and motor permission.
// Independent literal pixels, boundaries and Robot mapping tests cover D088.
#pragma once
#include "../core/fsm.h"
#include "qtr_cal.h"
#include <cstdint>

namespace ui {
inline constexpr unsigned FRAME_ROWS = 8U;
inline constexpr unsigned FRAME_COLS = 13U;
inline constexpr unsigned FRAME_BYTES = FRAME_ROWS * FRAME_COLS;
struct Frame { std::uint8_t pixels[FRAME_BYTES] = {}; };
enum DisplayFault : std::uint8_t {
    IMU_UNAVAILABLE = 1U, OPP_STUCK = 2U, QTR_STUCK = 4U, LOW_BATTERY = 8U,
    CAL_REJECTED = 16U, LINE_WARNING = 32U, CONTRACT_FAULT = 64U
};
enum class CalibrationScreen : std::uint8_t {
    SELECTION, WAITING, COLLECTING, SUCCESS, REJECTED, CANCELLED
};
struct DisplaySample {
    std::uint32_t t_us = 0U;
    core::State state = core::State::BOOT;
    core::Mode mode = core::Mode::SIDESTEP_R;
    bool service_menu = false;
    countdown::Service service = countdown::Service::SENSOR_VIEW;
    std::uint32_t release_us = 0U;
    bool battery_available = false;
    float battery_v = 0.0F;
    bool opponents_available = false;
    bool lines_available = false;
    std::uint8_t opponent_mask = 0U;
    std::uint8_t line_mask = 0U;
    std::uint8_t faults = 0U;
    CalibrationScreen calibration_screen = CalibrationScreen::SELECTION;
    std::uint8_t calibration_stage = 0U;
    std::uint32_t calibration_samples = 0U;
    bool service_unavailable = false; // D103 display projection only, not a fault.
};
enum class RenderStatus : std::uint8_t { OK, INVALID };
// Pure, complete overwrite; exact glyphs/layout in P2_matrix_contract.md.
RenderStatus render(const DisplaySample& sample, Frame& frame);
// Caller pairs the actual current input with its Robot result. No cached-result
// refresh: !result.fresh produces unavailable sensors/battery and CONTRACT_FAULT.
DisplaySample displaySample(const fsm::RobotInput& input, const fsm::RobotResult& result);
void applyCalibration(DisplaySample& sample, const qtr_cal::Report& report);
} // namespace ui
