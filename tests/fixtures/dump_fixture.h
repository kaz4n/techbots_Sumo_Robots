// Supplies independent D090 protocol sources and the real B13/B15 control pipeline.
// Keeps host-only trace allocation outside production owners and preserves RAM.
// Used by dump unit tests and the executable byte-stream parser round trip.
#pragma once
#include "hal/recorder_dump.h"
#include "hal/motors.h"
#include <algorithm>
#include <cstdint>
#include <limits>
#include <string>
#include <vector>

namespace dump_test {
namespace dump = recorder::dump;
struct Sink {
    std::string bytes;
    std::vector<std::string> offered;
    std::size_t limit = 64U;
    dump::WriteStatus status = dump::WriteStatus::PROGRESS;
    std::size_t bad_count = 0U;
    unsigned cancels = 0U;
    static dump::WriteResult write(void* context, const char* data, std::size_t size) {
        auto& self = *static_cast<Sink*>(context);
        self.offered.emplace_back(data, size);
        if (self.status != dump::WriteStatus::PROGRESS)
            return {self.status, self.bad_count};
        const auto count = self.bad_count != 0U ? self.bad_count : std::min(self.limit, size);
        if (count <= size) self.bytes.append(data, count);
        return {self.status, count};
    }
    static void cancel(void* context) { ++static_cast<Sink*>(context)->cancels; }
    dump::Port port() { return {this, write, cancel}; }
};

inline fsm::RobotResult eligible(std::uint64_t token, bool request = false) {
    fsm::RobotResult result;
    result.token = token;
    result.fresh = true;
    result.outputs.ui_state = core::State::IDLE;
    result.menu.selection.service_menu = true;
    result.menu.selection.service = countdown::Service::LOG_DUMP;
    if (request) result.menu.request = countdown::Service::LOG_DUMP;
    return result;
}
inline void begin(recorder::AttemptRecorder& source, std::uint64_t token = 1U) {
    auto result = eligible(token);
    result.outputs.ui_state = core::State::COUNTDOWN;
    result.lifecycle.gate.start_release = true;
    result.lifecycle.gate.release_us = 1234U;
    result.events.count = 1U;
    result.events.entries[0] = {1234U, core::Event::START_RELEASE, 1U, 0U};
    source.consume(result);
}
inline void storedFrame(fsm::RobotResult& result, std::uint64_t previous,
                        std::uint8_t state, logframe::PackStatus status) {
    result.frame_ready = true;
    result.frame_token = previous;
    result.frame_status = status;
    result.frame = {};
    result.frame.data[4] = state;
    result.frame.data[5] = 1U;
}
inline void sealed(recorder::AttemptRecorder& source, bool invalid = false) {
    begin(source);
    auto stop = eligible(2U);
    stop.outputs.ui_state = core::State::STOPPED;
    storedFrame(stop, 1U, 2U, invalid ? logframe::PackStatus::CLAMPED : logframe::PackStatus::OK);
    source.consume(stop);
    auto tail = eligible(3U);
    tail.outputs.ui_state = core::State::STOPPED;
    storedFrame(tail, 2U, 10U, invalid ? logframe::PackStatus::INVALID : logframe::PackStatus::OK);
    source.consume(tail);
}
inline std::uint32_t crc(const std::string& bytes) {
    std::uint32_t value = 0xFFFFFFFFU;
    for (const unsigned char byte : bytes) {
        value ^= byte;
        for (unsigned bit = 0U; bit < 8U; ++bit)
            value = (value >> 1U) ^ ((value & 1U) != 0U ? 0xEDB88320U : 0U);
    }
    return value ^ 0xFFFFFFFFU;
}
struct Protocol {
    recorder::AttemptRecorder source;
    Sink sink;
    dump::Transfer transfer{sink.port()};
    dump::Context context{10000U, 10000U, true, dump::Origin::SYNTHETIC};
    fsm::RobotResult result = eligible(10U, true);
    dump::Report report;
    Protocol() { sealed(source); }
    dump::Report step() { report = transfer.step(context, result, source); return report; }
    dump::Report next(std::uint32_t delta = 100U, bool new_tick = true) {
        context.now_us += delta;
        if (new_tick) { ++result.token; context.decision_us = context.now_us; }
        result.menu.request = countdown::Service::NONE;
        return step();
    }
    bool finish(unsigned bound = 10000U) {
        if (transfer.report().phase == dump::Phase::IDLE) step();
        for (unsigned i = 0U; i < bound && transfer.report().phase == dump::Phase::ACTIVE; ++i) next();
        report = transfer.report();
        return report.phase == dump::Phase::SENT_UNCONFIRMED;
    }
};

struct Writes {
    std::uint32_t now = 0U;
    unsigned enabled = 0U, nonzero = 0U;
    static bool configure(void*) { return true; }
    static bool configurePwm(void*, motors::Channel) { return true; }
    static bool enable(void* context, bool on) {
        if (on) ++static_cast<Writes*>(context)->enabled;
        return true;
    }
    static bool pwm(void* context, motors::Channel, std::uint32_t, std::uint32_t pulse) {
        if (pulse != 0U) ++static_cast<Writes*>(context)->nonzero;
        return true;
    }
    static std::uint32_t clock(void* context) { return static_cast<Writes*>(context)->now; }
    motors::Port port() {
        return {this, configure, configurePwm, enable, pwm, configure, clock,
                {1000U, 1000U, 1000U, 1000U}};
    }
};
struct Pipeline {
    Writes writes;
    motors::MotorGate gate{writes.port()};
    fsm::Robot robot;
    recorder::AttemptRecorder source;
    Sink sink;
    dump::Transfer transfer{sink.port()};
    fsm::RobotInput input;
    fsm::RobotResult result;
    dump::Report report;
    std::uint32_t now = 10000U;
    unsigned requests = 0U;
    Pipeline() {
        input.initialization_complete = true;
        input.observations_fresh = true;
        input.opp_raw_mask = static_cast<std::uint8_t>(config::OPP_ACTIVE_LOW_MASK);
        for (auto& value : input.line_raw_us) value = 1000U;
        input.vbat_valid = true;
        input.vbat_v = 12.5F;
        gate.begin();
    }
    void tick(core::ButtonLevel level = core::ButtonLevel::NONE) {
        now += config::TICK_US;
        input.t_us = writes.now = now;
        input.button = level;
        result = robot.step(input);
        input.previous = gate.apply(now, result).feedback;
        input.previous.duration_valid = true;
        input.previous.completed_us = now + 10U;
        input.previous.execution_us = 10U;
        source.consume(result);
        report = transfer.step({now, now, true, dump::Origin::SYNTHETIC}, result, source);
        if (result.menu.request == countdown::Service::LOG_DUMP) ++requests;
    }
    void hold(core::ButtonLevel level, unsigned milliseconds) {
        for (unsigned n = 0U; n < milliseconds; ++n) tick(level);
    }
    void startAttempt() {
        hold(core::ButtonLevel::NONE, config::BTN_DEBOUNCE_MS + 3U);
        hold(core::ButtonLevel::START, config::BTN_DEBOUNCE_MS + 3U);
        hold(core::ButtonLevel::NONE, config::BTN_DEBOUNCE_MS + 3U);
    }
    void sealByStop() { input.stop_requested = true; tick(); tick(); input.stop_requested = false; }
    void resetPreserving() {
        transfer.onRobotReset();
        source.onRobotReset();
        robot.reset();
        gate.reset();
        input.previous = {};
        tick();
    }
    void selectDump() {
        hold(core::ButtonLevel::NONE, config::BTN_DEBOUNCE_MS + 3U);
        hold(core::ButtonLevel::MODE, config::BTN_DEBOUNCE_MS + config::BTN_LONG_MS + 3U);
        hold(core::ButtonLevel::NONE, config::BTN_DEBOUNCE_MS + 3U);
        for (unsigned n = 0U; n < 3U; ++n) {
            hold(core::ButtonLevel::MODE, config::BTN_DEBOUNCE_MS + 3U);
            hold(core::ButtonLevel::NONE, config::BTN_DEBOUNCE_MS + 3U);
        }
    }
    void requestDump() {
        hold(core::ButtonLevel::START, config::BTN_DEBOUNCE_MS + 3U);
        hold(core::ButtonLevel::NONE, config::BTN_DEBOUNCE_MS + 3U);
    }
    bool finish() {
        for (unsigned n = 0U; n < 10000U && report.phase == dump::Phase::ACTIVE; ++n) tick();
        return report.phase == dump::Phase::SENT_UNCONFIRMED;
    }
};
} // namespace dump_test
