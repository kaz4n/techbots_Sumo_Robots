// Renders mode, countdown, sensor and fault information without changing control.
// Uses fixed glyphs and explicit unknown markers so missing data stays visible.
// Independent B3/B13/B14 fixtures verify every pixel and admission boundary.
#include "ui_display.h"
#include "../config.h"
#include <cmath>

namespace ui {
namespace {
static_assert(config::COUNTDOWN_MS > 0U && config::COUNTDOWN_MS <= 9000U);
static_assert((static_cast<std::uint64_t>(config::COUNTDOWN_MS) +
               config::COUNTDOWN_MARGIN_MS) * 1000U < 0x80000000U);
static_assert(config::UI_FAULT_PAGE_MS > 0U);
static_assert(config::UI_BATTERY_EMPTY_V >= 0.0F &&
              config::UI_BATTERY_FULL_V > config::UI_BATTERY_EMPTY_V);
constexpr std::uint8_t DIGITS[10][5] = {
    {7,5,7,5,7}, {2,6,2,2,7}, {7,1,7,4,7}, {7,1,7,1,7}, {5,5,7,1,1},
    {7,4,7,1,7}, {7,4,7,5,7}, {7,1,1,1,1}, {7,5,7,5,7}, {7,5,7,1,7}
};
constexpr std::uint8_t B[5] = {6,5,6,5,6}, S[5] = {7,4,7,1,7};
constexpr std::uint8_t E[5] = {7,4,6,4,7}, D[5] = {6,5,5,5,6};
constexpr std::uint8_t C[5] = {7,4,4,4,7}, L[5] = {4,4,4,4,7};
constexpr std::uint8_t FAULTS[7][5] = {
    {7,2,2,2,7}, {7,4,7,1,7}, {7,5,7,3,1}, {4,4,4,4,7},
    {7,4,4,4,7}, {5,5,5,7,5}, {7,4,6,4,7}
};
constexpr std::uint8_t RIGHT[5] = {4,2,31,2,4}, UP[5] = {4,14,21,4,4};
constexpr std::uint8_t ARC[5] = {0,14,17,2,7}, PAUSE[5] = {10,10,10,10,10};
constexpr std::uint8_t HOURGLASS[5] = {31,17,10,4,31};
constexpr std::uint8_t CROSS[5] = {17,10,4,10,17};
constexpr std::uint8_t CHECKER[5] = {21,10,21,10,21}, DOWN[5] = {4,4,21,14,4};

void glyph(Frame& frame, unsigned x, const std::uint8_t* rows,
           unsigned width, bool mirror = false) {
    for (unsigned y = 0U; y < 5U; ++y) {
        for (unsigned col = 0U; col < width; ++col) {
            const unsigned bit = mirror ? col : width - col - 1U;
            frame.pixels[(y + 1U) * FRAME_COLS + x + col] =
                (rows[y] & (1U << bit)) != 0U ? 7U : 0U;
        }
    }
}

void battery(Frame& frame, bool available, float voltage) {
    const double empty = config::UI_BATTERY_EMPTY_V;
    const double range = static_cast<double>(config::UI_BATTERY_FULL_V) - empty;
    for (unsigned col = 0U; col < FRAME_COLS; ++col) {
        const bool lit = available ? static_cast<double>(voltage) >=
            empty + range * (col + 1U) / FRAME_COLS : col % 2U == 0U;
        frame.pixels[7U * FRAME_COLS + col] = lit ? 7U : 0U;
    }
}

void faults(Frame& frame, std::uint8_t mask, std::uint32_t t_us) {
    unsigned count = 0U;
    for (unsigned bit = 0U; bit < 7U; ++bit) {
        if ((mask & (1U << bit)) != 0U) {
            frame.pixels[bit * 2U] = 7U;
            ++count;
        }
    }
    if (count == 0U) return;
    unsigned index = (t_us / 1000U / config::UI_FAULT_PAGE_MS) % count;
    for (unsigned bit = 0U; bit < 7U; ++bit) {
        if ((mask & (1U << bit)) == 0U) continue;
        if (index == 0U) { glyph(frame, 10U, FAULTS[bit], 3U); return; }
        --index;
    }
}

bool valid(const DisplaySample& sample) {
    const auto mode = static_cast<unsigned>(sample.mode);
    const auto service = static_cast<unsigned>(sample.service);
    return static_cast<unsigned>(sample.state) <= static_cast<unsigned>(core::State::DRIVE_TEST) &&
        mode >= 1U && mode <= 6U && service <= 4U &&
        (!sample.service_menu || service != 0U) && sample.opponent_mask <= 0x7FU &&
        sample.line_mask <= 0x0FU && sample.faults <= 0x7FU &&
        static_cast<unsigned>(sample.calibration_screen) <=
            static_cast<unsigned>(CalibrationScreen::CANCELLED) &&
        sample.calibration_stage <= 7U && sample.calibration_samples <= config::QTR_CAL_SAMPLES &&
        (!sample.battery_available || (std::isfinite(sample.battery_v) && sample.battery_v >= 0.0F));
}

RenderStatus invalid(Frame& frame) {
    frame = {};
    glyph(frame, 0U, E, 3U);
    glyph(frame, 4U, CROSS, 5U);
    for (unsigned bit = 0U; bit < 7U; ++bit) frame.pixels[bit * 2U] = 7U;
    battery(frame, false, 0.0F);
    return RenderStatus::INVALID;
}

void sensors(Frame& frame, const DisplaySample& sample) {
    constexpr unsigned OPP[7][2] = {{4,1},{2,1},{6,1},{0,3},{8,3},{2,5},{6,5}};
    constexpr unsigned LINE[4][2] = {{0,1},{8,1},{0,5},{8,5}};
    for (unsigned bit = 0U; bit < 7U; ++bit)
        frame.pixels[OPP[bit][1] * FRAME_COLS + OPP[bit][0]] =
            !sample.opponents_available ? 3U : (sample.opponent_mask & (1U << bit)) ? 7U : 0U;
    for (unsigned bit = 0U; bit < 4U; ++bit)
        frame.pixels[LINE[bit][1] * FRAME_COLS + LINE[bit][0]] =
            !sample.lines_available ? 3U : (sample.line_mask & (1U << bit)) ? 7U : 0U;
    constexpr std::uint8_t OUTLINE[3] = {2,7,5};
    for (unsigned y = 0U; y < 3U; ++y)
        for (unsigned x = 0U; x < 3U; ++x)
            frame.pixels[(y + 2U) * FRAME_COLS + x + 3U] =
                (OUTLINE[y] & (4U >> x)) ? 7U : 0U;
}

void mode(Frame& frame, core::Mode selected) {
    glyph(frame, 0U, DIGITS[static_cast<unsigned>(selected)], 3U);
    switch (selected) {
    case core::Mode::SIDESTEP_R: glyph(frame, 4U, RIGHT, 5U); break;
    case core::Mode::SIDESTEP_L: glyph(frame, 4U, RIGHT, 5U, true); break;
    case core::Mode::DIRECT: glyph(frame, 4U, UP, 5U); break;
    case core::Mode::ARC_R: glyph(frame, 4U, ARC, 5U); break;
    case core::Mode::ARC_L: glyph(frame, 4U, ARC, 5U, true); break;
    case core::Mode::WAIT: glyph(frame, 4U, PAUSE, 5U); break;
    }
}

void calibration(Frame& frame, const DisplaySample& sample) {
    const auto screen = sample.calibration_screen;
    constexpr std::uint8_t WHITE[5] = {31,31,31,31,31};
    constexpr std::uint8_t BLACK[5] = {31,17,17,17,31};
    constexpr std::uint8_t CHECK[5] = {0,1,18,12,0};
    if (screen == CalibrationScreen::SELECTION) {
        glyph(frame, 0U, C, 3U); glyph(frame, 4U, CHECKER, 5U);
    } else if (screen == CalibrationScreen::WAITING || screen == CalibrationScreen::COLLECTING) {
        glyph(frame, 0U, DIGITS[sample.calibration_stage / 2U + 1U], 3U);
        glyph(frame, 4U, sample.calibration_stage % 2U == 0U ? WHITE : BLACK, 5U);
        const unsigned count = config::QTR_CAL_SAMPLES > 0U ?
            sample.calibration_samples * FRAME_COLS / config::QTR_CAL_SAMPLES : 0U;
        for (unsigned col = 0U; col < FRAME_COLS; ++col)
            frame.pixels[6U * FRAME_COLS + col] =
                (screen == CalibrationScreen::WAITING ? col == 6U : col < count) ? 7U : 0U;
    } else {
        glyph(frame, 0U, screen == CalibrationScreen::REJECTED ? E : C, 3U);
        glyph(frame, 4U, screen == CalibrationScreen::SUCCESS ? CHECK : CROSS, 5U);
        if (screen == CalibrationScreen::SUCCESS)
            for (unsigned col = 0U; col < FRAME_COLS; ++col)
                frame.pixels[6U * FRAME_COLS + col] = 7U;
    }
}

void service(Frame& frame, const DisplaySample& sample) {
    switch (sample.service) {
    case countdown::Service::SENSOR_VIEW: sensors(frame, sample); break;
    case countdown::Service::QTR_CAL:
        calibration(frame, sample); break;
    case countdown::Service::DRIVE_TEST:
        glyph(frame, 0U, D, 3U); glyph(frame, 4U, CROSS, 5U); break;
    case countdown::Service::LOG_DUMP:
        glyph(frame, 0U, L, 3U); glyph(frame, 4U, DOWN, 5U); break;
    default: break;
    }
}
} // namespace

RenderStatus render(const DisplaySample& sample, Frame& frame) {
    frame = {};
    if (!valid(sample)) return invalid(frame);
    const auto state = sample.state;
    if (state == core::State::BOOT) {
        glyph(frame, 0U, B, 3U); glyph(frame, 4U, HOURGLASS, 5U);
    } else if (state == core::State::STOPPED || state == core::State::DRIVE_TEST) {
        glyph(frame, 0U, state == core::State::STOPPED ? S : D, 3U);
        glyph(frame, 4U, CROSS, 5U);
    } else if (state == core::State::COUNTDOWN) {
        const std::uint32_t elapsed = sample.t_us - sample.release_us;
        if (elapsed >= (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U)
            return invalid(frame);
        const std::uint32_t nominal = config::COUNTDOWN_MS * 1000U;
        const unsigned digit = elapsed >= nominal ? 1U : (nominal - elapsed + 999999U) / 1000000U;
        glyph(frame, 0U, DIGITS[digit], 3U); glyph(frame, 4U, HOURGLASS, 5U);
    } else if (state == core::State::IDLE && sample.service_menu) {
        service(frame, sample);
    } else {
        mode(frame, sample.mode);
    }
    battery(frame, sample.battery_available, sample.battery_v);
    faults(frame, sample.faults, sample.t_us);
    return RenderStatus::OK;
}

DisplaySample displaySample(const fsm::RobotInput& input, const fsm::RobotResult& result) {
    DisplaySample sample;
    sample.t_us = input.t_us;
    sample.state = result.outputs.ui_state;
    sample.mode = sample.state == core::State::IDLE ? result.menu.selection.mode : result.running_mode;
    sample.service_menu = result.menu.selection.service_menu;
    sample.service = result.menu.selection.service;
    sample.release_us = result.lifecycle.gate.release_us;
    sample.battery_available = result.fresh && input.vbat_valid;
    sample.battery_v = input.vbat_v;
    sample.opponents_available = result.fresh && (result.contract_faults & fsm::STALE_SENSORS) == 0U &&
        (input.line.explicit_values ? input.opponent_fresh : input.observations_fresh);
    sample.lines_available = result.fresh && result.line_available;
    sample.opponent_mask = result.opponent_mask;
    sample.line_mask = result.line_mask;
    if (!result.imu_available) sample.faults |= IMU_UNAVAILABLE;
    if (result.opponent_fault_mask != 0U) sample.faults |= OPP_STUCK;
    if (result.qtr_warning_mask != 0U) sample.faults |= QTR_STUCK;
    if (result.low_battery) sample.faults |= LOW_BATTERY;
    if (result.lifecycle.services.calibration_rejected) sample.faults |= CAL_REJECTED;
    if (result.lifecycle.services.line_warning) sample.faults |= LINE_WARNING;
    if (!result.fresh || result.contract_faults != 0U || result.escape_fault != edge::EscapeFault::NONE)
        sample.faults |= CONTRACT_FAULT;
    return sample;
}
void applyCalibration(DisplaySample& sample, const qtr_cal::Report& report) {
    switch (report.phase) {
    case qtr_cal::Phase::INACTIVE: sample.calibration_screen = CalibrationScreen::SELECTION; break;
    case qtr_cal::Phase::WAITING: sample.calibration_screen = CalibrationScreen::WAITING; break;
    case qtr_cal::Phase::COLLECTING: sample.calibration_screen = CalibrationScreen::COLLECTING; break;
    case qtr_cal::Phase::SUCCESS: sample.calibration_screen = CalibrationScreen::SUCCESS; break;
    case qtr_cal::Phase::REJECTED: sample.calibration_screen = CalibrationScreen::REJECTED; break;
    case qtr_cal::Phase::CANCELLED: sample.calibration_screen = CalibrationScreen::CANCELLED; break;
    default: sample.calibration_screen = static_cast<CalibrationScreen>(255U); break;
    }
    sample.calibration_stage = report.stage;
    sample.calibration_samples = report.samples;
}
} // namespace ui
