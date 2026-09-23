// Supplies D089 protocol records and an actual adapter/Robot/MotorGate pipeline.
// Expectations come from frozen public contracts, never implementation bodies.
// Synthetic intervals and callback writes prove software behavior only.
#pragma once
#include "hal/qtr_cal.h"
#include "hal/motors.h"
#include <algorithm>
#include <cstdint>

// Fatal preconditions without exceptions, matching the repository's host mode.
#define QTR_REQUIRE(condition) do { const bool qtr_required = (condition); \
    CHECK(qtr_required); if (!qtr_required) return; } while (false)
#define QTR_REQUIRE_FALSE(condition) QTR_REQUIRE(!(condition))

namespace qtr_cal_test {
inline line_qtr::Snapshot frame(std::uint32_t start, std::uint32_t sequence,
                                std::uint32_t lower = 800U, std::uint32_t upper = 803U,
                                std::uint8_t censored = 0U) {
    line_qtr::Snapshot s;
    s.phase = line_qtr::Phase::COMPLETE;
    s.status = line_qtr::Status::OK;
    s.valid = true;
    s.sequence = sequence;
    s.started_us = start;
    s.drive_completed_us = start + 1U;
    s.advances = 2U;
    s.released_mask = 15U;
    s.timeout_mask = censored;
    s.low_mask = static_cast<std::uint8_t>(15U & ~censored);
    std::uint32_t span = 14U;
    for (unsigned i = 0U; i < 4U; ++i) {
        const bool timeout = (censored & (1U << i)) != 0U;
        s.status_by_pad[i] = timeout ? 1 : 0;
        auto& pad = s.pad[i];
        pad.release_before_us = pad.release_after_us = start + 12U;
        pad.lower_us = timeout ? std::max(lower, config::QTR_TIMEOUT_US) : lower;
        if (pad.lower_us != 0U) {
            s.high_mask |= static_cast<std::uint8_t>(1U << i);
            pad.last_high_before_us = start + 13U + pad.lower_us;
        }
        if (!timeout) {
            pad.upper_us = upper;
            pad.first_low_after_us = start + 11U + upper;
        }
        span = std::max(span, timeout ? 15U + pad.lower_us : 13U + upper);
    }
    s.cleanup.attempted_mask = 15U;
    s.cleanup.started_us = start + span;
    s.completed_us = s.checked_us = s.cleanup.completed_us = start + span + 1U;
    return s;
}

inline fsm::RobotResult eligible(std::uint64_t token, bool request = false) {
    fsm::RobotResult result;
    result.fresh = true;
    result.token = token;
    result.outputs.ui_state = core::State::IDLE;
    result.line_raw_mode = result.line_calibration_hold = true;
    result.menu.selection.service_menu = true;
    result.menu.selection.service = countdown::Service::QTR_CAL;
    if (request) result.menu.request = countdown::Service::QTR_CAL;
    return result;
}

struct Protocol {
    qtr_cal::Calibration owner;
    std::uint32_t now = 10000U;
    std::uint32_t sequence = 0U;
    std::uint64_t token = 0U;
    qtr_cal::Report report;
    qtr_cal::Report step(const line_qtr::Snapshot& s = {}, bool request = false) {
        report = owner.step(now, eligible(++token, request), s);
        return report;
    }
    qtr_cal::Report sample(std::uint32_t lower, std::uint32_t upper,
                           std::uint8_t censored = 0U) {
        now += config::QTR_START_PERIOD_US;
        const auto s = frame(now - 1700U, ++sequence, lower, upper, censored);
        return step(s);
    }
    qtr_cal::Report batch(std::uint32_t lower, std::uint32_t upper,
                          std::uint8_t censored = 0U) {
        for (std::uint32_t n = 0U; n < config::QTR_CAL_SAMPLES; ++n)
            sample(lower, upper, censored);
        return report;
    }
    qtr_cal::Report complete(std::uint32_t white = 200U, std::uint32_t black = 800U,
                             bool censored_black = false) {
        for (unsigned stage = 0U; stage < 8U; ++stage) {
            ++now;
            step({}, true);
            if ((stage & 1U) == 0U) batch(white >= 3U ? white - 3U : 0U, white);
            else batch(black, black + 3U, censored_black ? 15U : 0U);
        }
        return report;
    }
};

struct Writes {
    std::uint32_t now = 0U;
    std::uint32_t nonzero = 0U;
    std::uint32_t enabled = 0U;
    bool en = false;
    static bool configure(void*) { return true; }
    static bool pwmConfigure(void*, motors::Channel) { return true; }
    static bool enable(void* context, bool value) {
        auto& self = *static_cast<Writes*>(context);
        self.en = value;
        if (value) ++self.enabled;
        return true;
    }
    static bool pwm(void* context, motors::Channel, std::uint32_t, std::uint32_t pulse) {
        if (pulse != 0U) ++static_cast<Writes*>(context)->nonzero;
        return true;
    }
    static std::uint32_t clock(void* context) { return static_cast<Writes*>(context)->now; }
    motors::Port port() {
        return {this, configure, pwmConfigure, enable, pwm, configure, clock,
                {1000U, 1000U, 1000U, 1000U}};
    }
};

struct Pipeline {
    Writes writes;
    motors::MotorGate gate{writes.port()};
    fsm::Robot robot;
    qtr_cal::Calibration calibration;
    fsm::RobotInput input;
    fsm::RobotResult result;
    qtr_cal::Report report;
    line_qtr::Snapshot snapshot;
    std::uint32_t now = 10000U;
    std::uint32_t sequence = 0U;
    bool raw = true;
    bool explicit_buttons = false;
    unsigned requests = 0U;
    Pipeline() {
        input.initialization_complete = true;
        input.opponent_fresh = true;
        // B5 electrical inactive levels: JS200XF low and MZ80 high.
        input.opp_raw_mask = static_cast<std::uint8_t>(config::OPP_ACTIVE_LOW_MASK);
        input.vbat_valid = true;
        input.vbat_v = 12.5F;
        gate.begin();
    }
    fsm::RobotResult tick(core::ButtonLevel level = core::ButtonLevel::NONE,
                           std::uint32_t delta = 1000U, bool fresh_line = false,
                           std::uint32_t lower = 800U, std::uint32_t upper = 803U) {
        now += delta;
        snapshot = fresh_line ? frame(now - 1700U, ++sequence, lower, upper) : line_qtr::Snapshot{};
        return apply(level);
    }
    fsm::RobotResult apply(core::ButtonLevel level = core::ButtonLevel::NONE) {
        input.t_us = writes.now = now;
        input.button = level;
        if (explicit_buttons) input.buttons = {true, true, core::ButtonPresence::VALID,
            level, static_cast<std::uint16_t>(level), now, now - 1U, now};
        if (raw) line_qtr::applyRawSnapshot(input, snapshot);
        else line_qtr::applySnapshot(input, snapshot, calibration.thresholds());
        result = robot.step(input);
        if (result.menu.request == countdown::Service::QTR_CAL) ++requests;
        input.previous = gate.apply(now, result).feedback;
        report = calibration.step(now, result, snapshot);
        return result;
    }
    void hold(core::ButtonLevel level, std::uint32_t duration, bool fresh_line = false) {
        for (std::uint32_t age = 0U; age < duration; age += 2000U)
            tick(level, 2000U, fresh_line);
    }
    void selectCalibration() {
        hold(core::ButtonLevel::NONE, 24000U);
        tick(core::ButtonLevel::MODE);
        hold(core::ButtonLevel::MODE, (config::BTN_DEBOUNCE_MS + config::BTN_LONG_MS + 4U) * 1000U);
        hold(core::ButtonLevel::NONE, 24000U);
        hold(core::ButtonLevel::MODE, 24000U);
        hold(core::ButtonLevel::NONE, 24000U);
    }
    void requestStage() {
        hold(core::ButtonLevel::START, 24000U);
        hold(core::ButtonLevel::NONE, 24000U);
    }
    void captureStage(unsigned stage) {
        requestStage();
        for (std::uint32_t n = 0U; n < config::QTR_CAL_SAMPLES; ++n)
            tick(core::ButtonLevel::NONE, 2000U, true,
                 (stage & 1U) == 0U ? 197U : 800U, (stage & 1U) == 0U ? 200U : 803U);
    }
    void completeCalibration() {
        selectCalibration();
        for (unsigned stage = 0U; stage < 8U; ++stage) captureStage(stage);
    }
    void requalify() {
        raw = false;
        for (std::uint32_t i = 0U; i < config::QTR_CONFIRM_TICKS; ++i)
            tick(core::ButtonLevel::NONE, 2000U, true);
    }
    void leaveServiceMenu() {
        hold(core::ButtonLevel::NONE, 24000U, true);
        hold(core::ButtonLevel::MODE, (config::BTN_DEBOUNCE_MS + config::BTN_LONG_MS + 6U) * 1000U, true);
        hold(core::ButtonLevel::NONE, 24000U, true);
    }
};
} // namespace qtr_cal_test
