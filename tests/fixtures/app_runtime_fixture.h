// Supplies typed D096 source traces using only frozen public contracts.
// Keeps synthetic physical grants and time separate from production hardware.
// Runtime tests and allocation probes share this fixed, bounded fixture.
#pragma once
#include "app/runtime.h"
#include "qtr_cal_fixture.h"
#include <array>
#include <cstdint>

namespace runtime_test {
enum class Call : std::uint8_t {
    ENABLE_SETUP, PWM_SETUP, ENABLE, PWM, SETTLE, ADC_SETUP, BUTTON, BATTERY,
    OPP_SETUP, OPP, LINE_SETUP, LINE_START, LINE_ADVANCE, LINE_CANCEL,
    IMU_SETUP, IMU_SETUP_ADVANCE, IMU_BEGIN, IMU_ADVANCE, IMU_CANCEL,
    IMU_FAILURE, MATRIX_SETUP, MATRIX
};
struct Entry { Call kind; std::uint32_t at; };
struct Fake {
    std::array<Entry, 32768> trace{};
    std::array<std::uint32_t, 4> pulses{};
    unsigned count = 0U, clocks = 0U, violations = 0U;
    unsigned buttons = 0U, batteries = 0U, opponents = 0U, matrices = 0U;
    unsigned line_starts = 0U, line_advances = 0U, line_cancels = 0U;
    unsigned imu_begins = 0U, imu_advances = 0U, imu_cancels = 0U;
    unsigned imu_setups = 0U, setup_advances = 0U, setup_failures = 0U;
    unsigned clock_reversal_countdown = 0U;
    std::uint32_t now = 10000U, clock_increment = 0U;
    std::uint32_t motor_work = 0U, settle_work = 0U, adc_work = 5U;
    std::uint32_t opponent_work = 5U, matrix_work = 7U, line_work = 20U;
    std::uint32_t line_lower = 400U, line_sequence = 0U, button_sequence = 0U;
    std::uint32_t active_line_lower = 400U;
    std::uint32_t imu_sequence = 0U, imu_last = 0U, imu_start = 0U;
    std::uint32_t imu_work = 5U, imu_complete_after = 3U;
    std::uint32_t opponent_shift = 0U;
    std::uint16_t button_raw = 50U;
    std::uint8_t opponent_mask = 0x78U;
    unsigned opponent_error = 0U;
    bool enabled = false, gate_ok = true, exclusive = false, power_grant = false;
    bool adc_failure = false, buttons_failure = false, freeze_buttons = false;
    bool qtr_never_release = false, qtr_no_start = false, qtr_fault = false;
    bool imu_pending = false, imu_no_new = false, imu_never_complete = false;
    bool imu_no_operation = false, setup_pending = false, setup_fault = false;
    bool imu_bad_payload = false;
    bool reverse_decision_clock = false;
    power::ButtonSample saved_button;
    line_qtr::Snapshot line;
    power::InitResult adc_result{power::Status::OK, power::Shutdown::NOT_ATTEMPTED, true};
    opp_sensors::InitResult opp_result{true, 0x7FU, {}};
    line_qtr::Status line_result = line_qtr::Status::OK;
    ui::MatrixStatus matrix_result = ui::MatrixStatus::INIT_UNCONFIRMED;
    static Fake& self(void* c) { return *static_cast<Fake*>(c); }
    void note(Call kind) {
        if (line.phase == line_qtr::Phase::CHARGING && kind != Call::LINE_ADVANCE &&
            kind != Call::LINE_CANCEL) ++violations;
        if (count < trace.size()) trace[count] = {kind, now};
        ++count;
    }
    unsigned seen(Call kind) const {
        unsigned total = 0U;
        for (unsigned i = 0U; i < count && i < trace.size(); ++i)
            if (trace[i].kind == kind) ++total;
        return total;
    }
    static std::uint32_t clock(void* c) {
        auto& f = self(c); ++f.clocks; const auto value = f.now;
        if (f.clock_reversal_countdown != 0U && --f.clock_reversal_countdown == 0U) return value - 1U;
        f.now += f.clock_increment; return value;
    }
    static bool enableSetup(void* c) {
        auto& f = self(c); f.note(Call::ENABLE_SETUP); f.now += f.motor_work;
        f.enabled = false; return f.gate_ok;
    }
    static bool pwmSetup(void* c, motors::Channel) {
        auto& f = self(c); f.note(Call::PWM_SETUP); f.now += f.motor_work; return true;
    }
    static bool enable(void* c, bool high) {
        auto& f = self(c); f.note(Call::ENABLE); f.now += f.motor_work;
        f.enabled = high; return true;
    }
    static bool pwm(void* c, motors::Channel channel, std::uint32_t, std::uint32_t pulse) {
        auto& f = self(c); f.note(Call::PWM); f.now += f.motor_work;
        f.pulses[static_cast<unsigned>(channel)] = pulse; return true;
    }
    static bool settle(void* c) {
        auto& f = self(c); f.note(Call::SETTLE); f.now += f.settle_work; return true;
    }
    static power::InitResult adcSetup(void* c) {
        auto& f = self(c); f.note(Call::ADC_SETUP); return f.adc_result;
    }
    static power::Sample battery(void* c) {
        auto& f = self(c); f.note(Call::BATTERY); ++f.batteries;
        const auto start = f.now; f.now += f.adc_work;
        if (f.adc_failure) return {power::Status::OVERRUN, power::Shutdown::DISABLED};
        constexpr std::uint16_t raw = 8192U;
        const float voltage = float(raw) / 16383.0F * config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
        return {power::Status::OK, power::Shutdown::NOT_ATTEMPTED, raw,
            start, f.now, voltage, true};
    }
    static power::ButtonSample button(void* c) {
        auto& f = self(c); f.note(Call::BUTTON); ++f.buttons;
        const auto start = f.now; f.now += f.adc_work;
        if (f.buttons_failure) return {power::Status::CONVERSION_TIMEOUT, power::Shutdown::DISABLED};
        if (f.freeze_buttons) return f.saved_button;
        f.saved_button = {power::Status::OK, power::Shutdown::NOT_ATTEMPTED,
            f.button_raw, start, f.now, ++f.button_sequence, true};
        return f.saved_button;
    }
    static opp_sensors::InitResult oppSetup(void* c) {
        auto& f = self(c); f.note(Call::OPP_SETUP); return f.opp_result;
    }
    static opp_sensors::Snapshot opp(void* c) {
        auto& f = self(c); f.note(Call::OPP); ++f.opponents;
        opp_sensors::Snapshot s; s.valid = true; s.valid_mask = 0x7FU;
        s.raw_mask = f.opponent_mask; s.started_us = f.now + f.opponent_shift;
        for (unsigned i = 0U; i < 7U; ++i) s.status[i] = (s.raw_mask >> i) & 1U;
        f.now += f.opponent_work; s.completed_us = f.now + f.opponent_shift;
        if (f.opponent_error == 1U) s.valid = false;
        if (f.opponent_error == 2U) s.valid_mask = 0x3FU;
        if (f.opponent_error == 3U) s.status[4] = -1;
        if (f.opponent_error == 4U) s.raw_mask = 0x80U;
        if (f.reverse_decision_clock) f.clock_reversal_countdown = 2U;
        return s;
    }
    static line_qtr::Status lineSetup(void* c, bool exclusive) {
        auto& f = self(c); f.note(Call::LINE_SETUP); f.exclusive = exclusive;
        f.line.phase = f.line_result == line_qtr::Status::OK ?
            line_qtr::Phase::IDLE : line_qtr::Phase::FAULT;
        f.line.status = f.line_result; return f.line_result;
    }
    static line_qtr::Status lineStart(void* c) {
        auto& f = self(c); f.note(Call::LINE_START); ++f.line_starts;
        if (f.line.phase == line_qtr::Phase::CHARGING ||
            f.line.phase == line_qtr::Phase::DISCHARGING) return line_qtr::Status::BUSY;
        if (f.qtr_no_start || (f.line_sequence != 0U &&
            f.now - f.line.started_us < 2000U)) return line_qtr::Status::NOT_DUE;
        f.line = {}; f.line.phase = line_qtr::Phase::CHARGING;
        f.active_line_lower = f.line_lower;
        f.line.status = line_qtr::Status::OK; f.line.sequence = ++f.line_sequence;
        f.line.started_us = f.now; f.line.drive_completed_us = ++f.now;
        return line_qtr::Status::OK;
    }
    static line_qtr::Snapshot lineAdvance(void* c) {
        auto& f = self(c); f.note(Call::LINE_ADVANCE); ++f.line_advances;
        const auto before = f.line.checked_us; f.now += f.line_work;
        ++f.line.advances; f.line.checked_us = f.now;
        if (before != 0U && f.now - before > f.line.max_service_gap_us)
            f.line.max_service_gap_us = f.now - before;
        if (f.qtr_fault) { f.line.phase = line_qtr::Phase::FAULT;
            f.line.status = line_qtr::Status::FRAME_DEADLINE; return f.line; }
        if (f.line.phase == line_qtr::Phase::CHARGING) {
            if (!f.qtr_never_release) { f.line.phase = line_qtr::Phase::DISCHARGING;
                f.line.released_mask = 15U; }
            return f.line;
        }
        if (f.now - f.line.started_us >= f.active_line_lower + 17U) {
            const auto gap = f.line.max_service_gap_us;
            const bool delayed = before != 0U && f.now - before > 100U;
            const auto lower = delayed ? std::min(f.active_line_lower, f.line.pad[0].lower_us) : f.active_line_lower;
            const auto upper = delayed ? f.now - f.line.started_us - 11U : f.active_line_lower + 3U;
            f.line = qtr_cal_test::frame(f.line.started_us, f.line.sequence,
                lower, upper);
            if (delayed) f.now = f.line.completed_us;
            f.line.max_service_gap_us = gap;
        } else for (auto& pad : f.line.pad) pad.lower_us = f.now - f.line.started_us - 15U;
        return f.line;
    }
    static line_qtr::Snapshot lineCancel(void* c) {
        auto& f = self(c); f.note(Call::LINE_CANCEL); ++f.line_cancels;
        f.line.phase = line_qtr::Phase::FAULT; f.line.status = line_qtr::Status::CANCELLED;
        f.line.valid = false; return f.line;
    }
    static line_qtr::Snapshot lines(void* c) { return self(c).line; }
    static imu::SetupReport imuSetup(void* c, std::uint32_t time, bool power) {
        auto& f = self(c); f.note(Call::IMU_SETUP); ++f.imu_setups; f.power_grant = power;
        imu::SetupReport r; r.started_us = r.observed_us = time;
        r.state = f.setup_pending ? imu::SetupState::IN_PROGRESS : imu::SetupState::PROFILE_READY;
        r.bus_status = imu::BusStatus::OK; return r;
    }
    static imu::SetupReport imuSetupAdvance(void* c, std::uint32_t time) {
        auto& f = self(c); f.note(Call::IMU_SETUP_ADVANCE); ++f.setup_advances;
        imu::SetupReport r; r.observed_us = time; r.advances = f.setup_advances;
        r.state = f.setup_fault ? imu::SetupState::FAULT : imu::SetupState::IN_PROGRESS;
        r.fault = f.setup_fault ? imu::SetupFault::TRANSPORT : imu::SetupFault::NONE;
        r.bus_status = f.setup_fault ? imu::BusStatus::NACK : imu::BusStatus::OK; return r;
    }
    static imu::SampleProgress imuBegin(void* c, std::uint32_t) {
        auto& f = self(c); f.note(Call::IMU_BEGIN); ++f.imu_begins;
        if (f.imu_no_operation) return {imu::AsyncState::FAULT, false, false, {}};
        f.imu_pending = true; f.imu_start = f.now;
        return {imu::AsyncState::PENDING, true, false, {}};
    }
    imu::Sample makeSample() {
        imu::Sample s; s.checked_us = now; s.sequence = imu_sequence;
        s.bus_status = imu::BusStatus::OK;
        if (imu_no_new) { s.state = imu::SampleState::NO_NEW; return s; }
        s.state = imu::SampleState::OBSERVATION; s.sequence = ++imu_sequence;
        s.had_previous_observation = imu_sequence != 1U;
        s.observation_gap_us = s.had_previous_observation ? now - imu_last : 0U;
        imu_last = now; s.motion.status = imu::DecodeStatus::OK;
        s.motion.coherent = !imu_bad_payload; s.motion.started_us = imu_start;
        s.motion.completed_us = now; s.motion.gyro_dps[2] = 2.0F;
        s.motion.accel_g[0] = 0.1F; s.motion.accel_g[1] = 0.2F; return s;
    }
    static imu::SampleProgress imuAdvance(void* c, std::uint32_t) {
        auto& f = self(c); f.note(Call::IMU_ADVANCE); ++f.imu_advances; f.now += f.imu_work;
        if (f.imu_never_complete || f.imu_advances % f.imu_complete_after != 0U)
            return {imu::AsyncState::PENDING, false, false, {}};
        f.imu_pending = false; return {imu::AsyncState::COMPLETE, false, true, f.makeSample()};
    }
    static imu::SampleProgress imuCancel(void* c, std::uint32_t) {
        auto& f = self(c); f.note(Call::IMU_CANCEL); ++f.imu_cancels; f.imu_pending = false;
        imu::Sample s; s.state = imu::SampleState::FAULT; s.fault = imu::SampleFault::TRANSPORT;
        s.bus_status = imu::BusStatus::CANCELLED;
        return {imu::AsyncState::FAULT, false, true, s};
    }
    static imu::Sample imuFailure(void* c, std::uint32_t) {
        auto& f = self(c); f.note(Call::IMU_FAILURE); ++f.setup_failures;
        imu::Sample s; s.state = imu::SampleState::FAULT; s.fault = imu::SampleFault::SETUP; return s;
    }
    static ui::MatrixStatus matrixSetup(void* c, ui::MatrixGrant) {
        auto& f = self(c); f.note(Call::MATRIX_SETUP); return f.matrix_result;
    }
    static ui::MatrixStatus matrix(void* c, std::uint32_t time, const ui::Frame&) {
        auto& f = self(c); f.note(Call::MATRIX); ++f.matrices;
        if (time != f.now) ++f.violations;
        f.now += f.matrix_work; return ui::MatrixStatus::SUBMITTED_UNCONFIRMED;
    }
    motors::Port motorPort() { return {this, enableSetup, pwmSetup, enable, pwm,
        settle, clock, {1000U, 1000U, 1000U, 1000U}}; }
    power::InputPort adcPort() { return {this, adcSetup, battery, button, clock}; }
    app::SourcePort sourcePort() { return {this, oppSetup, opp, lineSetup, lineStart,
        lineAdvance, lineCancel, lines, imuSetup, imuSetupAdvance, imuBegin,
        imuAdvance, imuCancel, imuFailure, matrixSetup, matrix}; }
};
inline app::SetupGrants grants(bool control = false, bool with_imu = false) {
    app::SetupGrants g; g.opponents = g.adc_pair = g.qtr_exclusive_pads = true;
    g.default_line_thresholds_confirmed = control; g.imu_enabled = with_imu;
    g.imu_power_confirmed = with_imu; g.mounting = {{1, 2, 3}, with_imu}; return g;
}
struct Rig {
    Fake fake;
    app::Runtime owner{fake.motorPort(), fake.adcPort(), fake.sourcePort()};
    bool begin(bool control = false, bool with_imu = false) {
        auto g = grants(control, with_imu);
#ifndef APP_TEST_CONFIGURED_BUTTONS
        // Unconfigured windows intentionally invalidate granted A1. Independent
        // multi-epoch source tests leave ADC absent; explicit ADC tests opt in.
        g.adc_pair = false;
#endif
        return owner.begin(g);
    }
    bool next() { fake.now = owner.report().next_release_us; return owner.step(); }
    void run(unsigned ticks, std::uint16_t raw = 50U) {
        fake.button_raw = raw;
        for (unsigned i = 0U; i < ticks; ++i) next();
    }
};
} // namespace runtime_test
