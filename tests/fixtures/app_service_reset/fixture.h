// Supplies real D103 application epochs with scripted physical boundary callbacks.
// Keeps local button/source timing separate from Runtime-owned reset authority.
// Independent tests and strict stream roundtrip exercise the public owners only.
#pragma once
#include "../app_dump/fixture.h"
#include "hal/recorder_csv.h"
#include <string>

namespace service_reset_test {
constexpr std::uint16_t NONE = 50U, START = 1000U, MODE = 2000U, BOTH = 3000U;
struct Source : app_dump_test::Source {
    ui::Frame displayed;
    unsigned enable_setups = 0U, pwm_setups = 0U, highs = 0U, nonzero = 0U;
    unsigned line_setups = 0U, adc_setups = 0U, opp_setups = 0U;
    unsigned matrix_setups = 0U;
    std::uint32_t button_work = 5U;
    std::uint32_t button_delay = 0U;
    bool reverse_matrix = false;
    static Source& cast(void* c) { return *static_cast<Source*>(c); }
    static bool enableSetup(void* c) {
        ++cast(c).enable_setups; return Fake::enableSetup(c);
    }
    static bool pwmSetup(void* c, motors::Channel channel) {
        ++cast(c).pwm_setups; return Fake::pwmSetup(c, channel);
    }
    static bool enable(void* c, bool high) {
        auto& f = cast(c); if (high) ++f.highs;
        Fake::enable(c, high); return !f.reject_enable;
    }
    static bool pwm(void* c, motors::Channel channel, std::uint32_t period,
                    std::uint32_t pulse) {
        if (pulse != 0U) ++cast(c).nonzero;
        return Fake::pwm(c, channel, period, pulse);
    }
    static power::InitResult adcSetup(void* c) {
        ++cast(c).adc_setups; return Fake::adcSetup(c);
    }
    static power::ButtonSample button(void* c) {
        auto& f = cast(c); const auto saved = f.adc_work;
        f.now += f.button_delay;
        f.adc_work = f.button_work; const auto result = Fake::button(c);
        f.adc_work = saved; return result;
    }
    static opp_sensors::InitResult oppSetup(void* c) {
        ++cast(c).opp_setups; return Fake::oppSetup(c);
    }
    static line_qtr::Status lineSetup(void* c, bool exclusive) {
        ++cast(c).line_setups; return Fake::lineSetup(c, exclusive);
    }
    static ui::MatrixStatus matrixSetup(void* c, ui::MatrixGrant grant) {
        ++cast(c).matrix_setups; return Fake::matrixSetup(c, grant);
    }
    static ui::MatrixStatus matrix(void* c, std::uint32_t time, const ui::Frame& frame) {
        auto& f = cast(c); f.displayed = frame;
        const auto result = Fake::matrix(c, time, frame);
        if (f.reverse_matrix) f.now = time - 1U;
        return result;
    }
    motors::Port motorPort() {
        auto p = Fake::motorPort(); p.configureEnableLow = enableSetup;
        p.configurePwm = pwmSetup; p.writeEnable = enable; p.writePwm = pwm; return p;
    }
    power::InputPort adcPort() { return {this, adcSetup, Fake::battery, button, Fake::clock}; }
    app::SourcePort sourcePort() {
        auto p = Fake::sourcePort(); p.beginOpponents = oppSetup;
        p.beginLines = lineSetup; p.beginMatrix = matrixSetup; p.submitMatrix = matrix;
        return p;
    }
};
struct Rig {
    Source fake;
    app_dump_test::Sink sink{fake};
    app::Runtime owner{fake.motorPort(), fake.adcPort(), fake.sourcePort(), sink.port()};
    Rig() { sink.runtime = &owner; }
    bool begin(bool enabled = true, bool control = true, bool imu = false) {
        auto g = runtime_test::grants(control, imu); g.local_service_reset = enabled;
#ifndef APP_TEST_CONFIGURED_BUTTONS
        g.adc_pair = false;
#endif
        g.matrix_enabled = true; g.matrix = {true, true};
        g.dump_enabled = true; g.dump = {true, true, false, true};
        g.dump_origin = recorder::dump::Origin::SYNTHETIC;
        return owner.begin(g);
    }
    bool next(std::uint32_t late = 0U) {
        fake.now = owner.report().next_release_us + late; return owner.step();
    }
    bool run(unsigned ticks, std::uint16_t raw = NONE) {
        fake.button_raw = raw;
        for (unsigned i = 0U; i < ticks; ++i) if (!next()) return false;
        return true;
    }
    const fsm::RobotResult& robot() const { return owner.transaction().report().robot; }
    bool firstStop() {
        fake.button_raw = BOTH;
        for (unsigned i = 0U; i < 1100U; ++i) {
            if (!next()) return false;
            if (robot().outputs.ui_state == core::State::STOPPED) return true;
        }
        return false;
    }
    bool stopped(bool attempt = false, bool imu = false, bool enabled = true) {
        if (!begin(enabled, true, imu) || !run(35U)) return false;
        if (attempt && (!run(30U, START) || !run(30U) || !run(5110U))) return false;
        return firstStop() && next();
    }
    bool pending() {
        if (!run(30U) || !run(1040U, MODE)) return false;
        fake.button_raw = NONE;
        for (unsigned i = 0U; i < 40U; ++i) {
            if (!next()) return false;
            if (owner.report().service_reset_pending) return true;
        }
        return false;
    }
    bool reset(bool attempt = false, bool imu = false) {
        return stopped(attempt, imu) && pending() && next() && owner.report().service_only;
    }
    bool select(unsigned item) {
        if (!run(30U) || !run(1040U, MODE) || !run(30U)) return false;
        for (unsigned i = 0U; i < item; ++i)
            if (!run(30U, MODE) || !run(30U)) return false;
        return robot().menu.selection.service_menu;
    }
    bool request(countdown::Service service) {
        if (!run(30U, START)) return false;
        fake.button_raw = NONE;
        for (unsigned i = 0U; i < 30U; ++i) {
            if (!next()) return false;
            if (robot().menu.request == service) return true;
        }
        return false;
    }
    bool finishDump() {
        for (unsigned i = 0U; i < 20000U &&
             owner.report().dump.phase == recorder::dump::Phase::ACTIVE; ++i)
            if (!next()) return false;
        return owner.report().dump.phase == recorder::dump::Phase::SENT_UNCONFIRMED;
    }
};
inline bool append(std::string& output, recorder::csv::FormatResult r, const char* line) {
    if (r.status != recorder::csv::FormatStatus::OK) return false;
    output.append(line, r.size); return true;
}
inline bool csv(const recorder::AttemptRecorder& source, std::string& frames,
                std::string& events, std::string& summary) {
    char line[recorder::csv::MAX_LINE_BYTES];
    frames.clear(); events.clear(); summary.clear();
    if (!append(frames, recorder::csv::frameHeader(line, sizeof(line)), line) ||
        !append(events, recorder::csv::eventHeader(line, sizeof(line)), line) ||
        !append(summary, recorder::csv::summaryHeader(line, sizeof(line)), line)) return false;
    for (std::uint32_t i = 0U; i < source.frames().size(); ++i) {
        recorder::StoredFrame frame; if (!source.frames().read(i, frame)) return false;
        if (!append(frames, recorder::csv::frameRow(frame, i, line, sizeof(line)), line)) return false;
    }
    for (std::uint32_t i = 0U; i < source.events().size(); ++i) {
        const auto* event = source.events().at(i); if (event == nullptr) return false;
        if (!append(events, recorder::csv::eventRow(*event, i, line, sizeof(line)), line)) return false;
    }
    return append(summary, recorder::csv::summaryRow(recorder::csv::captureSummary(source),
        line, sizeof(line)), line);
}
} // namespace service_reset_test
