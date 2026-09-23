// Checks D089 calibration display against independently transcribed literal pixels.
// Covers every stage, integer progress boundary and unchanged hidden overlays.
// Host renderer calls use synthetic reports and make no display hardware claim.
#include "doctest.h"
#include "hal/ui_display.h"
#include <cstring>
#include <initializer_list>

namespace {
void glyph(ui::Frame& expected, unsigned x, const unsigned* rows, unsigned width) {
    for (unsigned y = 0U; y < 5U; ++y)
        for (unsigned column = 0U; column < width; ++column)
            expected.pixels[(y + 1U) * 13U + x + column] =
                (rows[y] & (1U << (width - column - 1U))) != 0U ? 7U : 0U;
}

ui::DisplaySample screen(ui::CalibrationScreen selected) {
    ui::DisplaySample s;
    s.state = core::State::IDLE;
    s.service_menu = true;
    s.service = countdown::Service::QTR_CAL;
    s.calibration_screen = selected;
    return s;
}

ui::Frame expectedBase() {
    ui::Frame expected;
    for (unsigned x = 0U; x < 13U; x += 2U) expected.pixels[7U * 13U + x] = 7U;
    return expected;
}
} // namespace

TEST_CASE("B13 D089 all stage digits colors and progress pixels are literal") {
    const unsigned digits[4][5] = {{2,6,2,2,7},{7,1,7,4,7},{7,1,7,1,7},{5,5,7,1,1}};
    const unsigned white[5] = {31,31,31,31,31};
    const unsigned black[5] = {31,17,17,17,31};
    for (auto phase : {ui::CalibrationScreen::WAITING, ui::CalibrationScreen::COLLECTING}) {
        for (unsigned stage = 0U; stage < 8U; ++stage) {
            for (std::uint32_t count = 0U; count <= config::QTR_CAL_SAMPLES; ++count) {
                auto sample = screen(phase);
                sample.calibration_stage = static_cast<std::uint8_t>(stage);
                sample.calibration_samples = count;
                auto expected = expectedBase();
                glyph(expected, 0U, digits[stage / 2U], 3U);
                glyph(expected, 4U, (stage & 1U) == 0U ? white : black, 5U);
                for (unsigned x = 0U; x < 13U; ++x)
                    expected.pixels[6U * 13U + x] = (phase == ui::CalibrationScreen::WAITING ?
                        x == 6U : x < count * 13U / config::QTR_CAL_SAMPLES) ? 7U : 0U;
                ui::Frame actual;
                std::memset(actual.pixels, 255, sizeof(actual.pixels));
                CHECK(ui::render(sample, actual) == ui::RenderStatus::OK);
                CHECK(std::memcmp(expected.pixels, actual.pixels, sizeof(actual.pixels)) == 0);
            }
        }
    }
}

TEST_CASE("B13 D089 terminal glyphs preserve fault and battery pixels") {
    const unsigned c[5] = {7,4,4,4,7};
    const unsigned e[5] = {7,4,6,4,7};
    const unsigned check[5] = {0,1,18,12,0};
    const unsigned cross[5] = {17,10,4,10,17};
    for (auto phase : {ui::CalibrationScreen::SUCCESS, ui::CalibrationScreen::REJECTED,
                       ui::CalibrationScreen::CANCELLED}) {
        auto sample = screen(phase);
        sample.faults = ui::CONTRACT_FAULT;
        sample.battery_available = true;
        sample.battery_v = config::UI_BATTERY_FULL_V;
        ui::Frame expected;
        expected.pixels[12] = 7U;
        glyph(expected, 0U, phase == ui::CalibrationScreen::REJECTED ? e : c, 3U);
        glyph(expected, 4U, phase == ui::CalibrationScreen::SUCCESS ? check : cross, 5U);
        glyph(expected, 10U, e, 3U);
        for (unsigned x = 0U; x < 13U; ++x) {
            expected.pixels[7U * 13U + x] = 7U;
            if (phase == ui::CalibrationScreen::SUCCESS) expected.pixels[6U * 13U + x] = 7U;
        }
        ui::Frame actual;
        CHECK(ui::render(sample, actual) == ui::RenderStatus::OK);
        CHECK(std::memcmp(expected.pixels, actual.pixels, sizeof(actual.pixels)) == 0);
    }
}

TEST_CASE("B13 D089 hidden overlays are inert but malformed fields remain invalid") {
    for (unsigned hidden = 0U; hidden < 3U; ++hidden) {
        auto sample = screen(ui::CalibrationScreen::SELECTION);
        if (hidden == 0U) sample.state = core::State::BOOT;
        if (hidden == 1U) sample.service_menu = false;
        if (hidden == 2U) sample.service = countdown::Service::LOG_DUMP;
        ui::Frame baseline, overlay;
        CHECK(ui::render(sample, baseline) == ui::RenderStatus::OK);
        sample.calibration_screen = ui::CalibrationScreen::COLLECTING;
        sample.calibration_stage = 7U;
        sample.calibration_samples = config::QTR_CAL_SAMPLES;
        CHECK(ui::render(sample, overlay) == ui::RenderStatus::OK);
        CHECK(std::memcmp(baseline.pixels, overlay.pixels, sizeof(overlay.pixels)) == 0);
        sample.calibration_stage = 8U;
        CHECK(ui::render(sample, overlay) == ui::RenderStatus::INVALID);
        sample.calibration_stage = 0U;
        sample.calibration_samples = config::QTR_CAL_SAMPLES + 1U;
        CHECK(ui::render(sample, overlay) == ui::RenderStatus::INVALID);
        sample.calibration_samples = 0U;
        sample.calibration_screen = static_cast<ui::CalibrationScreen>(255U);
        CHECK(ui::render(sample, overlay) == ui::RenderStatus::INVALID);
    }
}

TEST_CASE("B13 D089 actual report mapping copies only calibration display fields") {
    const qtr_cal::Phase phases[] = {qtr_cal::Phase::INACTIVE, qtr_cal::Phase::WAITING,
        qtr_cal::Phase::COLLECTING, qtr_cal::Phase::SUCCESS, qtr_cal::Phase::REJECTED,
        qtr_cal::Phase::CANCELLED};
    for (unsigned i = 0U; i < 6U; ++i) {
        auto sample = screen(ui::CalibrationScreen::SELECTION);
        sample.t_us = 12345U;
        sample.faults = ui::LOW_BATTERY;
        sample.opponent_mask = 73U;
        qtr_cal::Report report;
        report.phase = phases[i];
        report.stage = 7U;
        report.samples = config::QTR_CAL_SAMPLES;
        ui::applyCalibration(sample, report);
        CHECK(sample.calibration_screen == static_cast<ui::CalibrationScreen>(i));
        CHECK(sample.calibration_stage == 7U);
        CHECK(sample.calibration_samples == config::QTR_CAL_SAMPLES);
        CHECK(sample.t_us == 12345U);
        CHECK(sample.faults == ui::LOW_BATTERY);
        CHECK(sample.opponent_mask == 73U);
        CHECK(sample.service == countdown::Service::QTR_CAL);
    }
}
