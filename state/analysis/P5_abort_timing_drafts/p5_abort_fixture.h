// Supplies independent D135 public Robot, Transaction and actual MotorGate observations.
// Keeps acquisition, decision, application and completion clocks distinct in host traces.
// Draft tests use only admitted public inputs; malformed receipts are explicitly altered evidence.
#pragma once
#include "fixtures/app_transaction_fixture.h"
#include "core/openers.h"
#include <array>
#include <cmath>
#include <initializer_list>
#include <limits>

static_assert(SUMOX_P5_ABORT_TIMING == 1, "D135 draft requires its exclusive profile");

namespace p5_abort {
using Mode = core::Mode;
using State = core::State;
using Button = core::ButtonLevel;
using Phase = openers::AbortPhase;
using Cause = openers::AbortCause;
constexpr auto TIMING = static_cast<core::Event>(10U);
enum Detail : unsigned { HEADER = 0U, READ_START = 16U, READ_END = 17U,
    QUALIFIED = 18U, HANDOVER = 19U, APPLIED = 20U, NOT_ABORT = 21U,
    INTERRUPTED = 22U, INVALID_SOURCE = 23U, INVALID_RECEIPT = 24U, HANDOVER_FAILED = 25U };
inline unsigned count(const fsm::RobotResult& r, unsigned detail = 256U) {
    unsigned n = 0U;
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == TIMING &&
            (detail == 256U || r.events.entries[i].detail == detail)) ++n;
    return n;
}
inline logframe::EventInput event(const fsm::RobotResult& r, unsigned detail) {
    APP_REQUIRE(count(r, detail) == 1U);
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == TIMING && r.events.entries[i].detail == detail)
            return r.events.entries[i];
    return {};
}
inline std::uint16_t cue(unsigned mode, unsigned phase, unsigned cause,
                         unsigned mask, bool snapshot = false) {
    return static_cast<std::uint16_t>(mode | (phase << 3U) | (cause << 6U) |
                                      (mask << 8U) | (snapshot ? 0x8000U : 0U));
}
inline bool permittedCue(unsigned mode, unsigned phase, unsigned cause,
                          unsigned mask, bool snapshot) {
    const bool front = (mask & 7U) != 0U;
    if (mode == 3U && phase == 0U)
        return (cause == 1U && front) ||
            (cause == 2U && !front && (mask & 0x78U) != 0U && !snapshot);
    if (snapshot) return false;
    if (mode == 6U && phase == 4U) return cause == 2U && (mask & 0x78U) != 0U;
    if (mode == 4U || mode == 5U)
        return (phase == 2U || phase == 3U) && cause == 1U && front;
    if ((mode != 1U && mode != 2U && mode != 6U) || phase < 1U || phase > 3U)
        return false;
    const unsigned outer = mode == 2U ? 0x28U : 0x50U;
    return (cause == 1U && phase != 1U && front) ||
        (cause == 2U && (mask & outer) != 0U && (phase == 1U || !front));
}
inline openers::Sample sample(std::uint32_t t, unsigned mask = 0U, float yaw = 0.0F,
                              bool healthy = true, float bearing = -90.0F) {
    openers::Sample s; s.t_us = t; s.confirmed_mask = static_cast<std::uint8_t>(mask);
    s.heading_deg = yaw; s.imu_ok = healthy; s.bearing_valid = true; s.bearing_deg = bearing;
    return s;
}
inline void pulse(const openers::AbortEvidence& evidence, Phase phase, Cause cause,
                   unsigned mask, bool snapshot = false) {
    CHECK(evidence.phase == phase); CHECK(evidence.cause == cause);
    CHECK(evidence.effective_mask == mask); CHECK(evidence.snapshot_front_present == snapshot);
}
inline void suffix(const fsm::RobotResult& r, std::initializer_list<unsigned> details) {
    CHECK(count(r) == details.size()); unsigned first = 0U;
    while (first < r.events.count && r.events.entries[first].type != TIMING) ++first;
    APP_REQUIRE(first + details.size() == r.events.count);
    for (auto detail : details) {
        CHECK(r.events.entries[first].type == TIMING);
        CHECK(r.events.entries[first++].detail == detail);
    }
}
inline void terminal(const fsm::RobotResult& r, unsigned detail, unsigned value, std::uint32_t d) {
    suffix(r, {detail}); const auto e = event(r, detail);
    CHECK(e.t_us == d); CHECK(e.value == value);
}
struct Rig {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::PreviousTick previous;
    fsm::RobotResult last;
    motors::Result applied;
    std::array<logframe::EventInput, 64> trace{};
    unsigned trace_size = 0U;
    std::uint32_t now = 0U;
    Rig() { APP_REQUIRE(gate.begin()); port.clear(); }
    void opponent(unsigned mask) { input.opp_raw_mask = static_cast<std::uint8_t>(mask ^ 0x78U); }
    void white(unsigned mask) {
        for (unsigned i = 0U; i < 4U; ++i) input.line_raw_us[i] = mask & (1U << i) ? 100U : 1000U;
    }
    fsm::RobotInput at(std::uint32_t d, std::uint32_t acquisition = 0U) const {
        auto value = input; value.t_us = d; value.previous = previous;
        value.timing.explicit_start = true; value.timing.start_valid = true;
        value.timing.started_us = d - acquisition;
        value.opponent_read = {true, d - acquisition, d}; return value;
    }
    fsm::RobotResult submit(fsm::RobotInput value, std::uint32_t apply_delay = 0U,
                            std::uint32_t complete_delay = 0U) {
        const auto result = robot.step(value); if (!result.fresh) return result;
        now = value.t_us; last = result;
        for (unsigned i = 0U; i < result.events.count; ++i) if (result.events.entries[i].type == TIMING) {
            APP_REQUIRE(trace_size < trace.size()); trace[trace_size++] = result.events.entries[i];
        }
        port.now = now + apply_delay; applied = gate.apply(now, result);
        APP_REQUIRE(applied.consumed); APP_REQUIRE(applied.feedback.applied_valid);
        previous = applied.feedback; previous.duration_valid = true;
        previous.completed_us = now + complete_delay;
        previous.execution_us = previous.completed_us - value.timing.started_us;
        return result;
    }
    fsm::RobotResult step(std::uint32_t d, Button button = Button::NONE) {
        auto value = at(d); value.button = button; return submit(value);
    }
    fsm::RobotResult next(std::uint32_t delta = 1000U, Button button = Button::NONE) {
        return step(now + delta, button);
    }
    void prime(std::uint32_t base = 0U) {
        step(base); next(); next(20000U); APP_REQUIRE(last.outputs.ui_state == State::IDLE);
    }
    void shortMode() {
        next(1000U, Button::MODE); next(20000U, Button::MODE); next(); next(20000U);
    }
    void select(Mode mode) {
        APP_REQUIRE(core::modeAvailable(mode));
        for (unsigned i = 0U; i < 6U && last.menu.selection.mode != mode; ++i) shortMode();
        APP_REQUIRE(last.menu.selection.mode == mode);
    }
    std::uint32_t release(Mode mode = Mode::DIRECT, std::uint32_t base = 0U) {
        prime(base); select(mode); next(1000U, Button::START); next(20000U, Button::START);
        next(); next(20000U); APP_REQUIRE(last.lifecycle.gate.start_release); return now;
    }
    void services(std::uint32_t release) {
        step(release + 1500000U); next(); step(release + 4500000U);
    }
    std::uint32_t go(Mode mode = Mode::DIRECT, std::uint32_t base = 0U) {
        const auto released = release(mode, base); services(released);
        step(released + 5099999U); step(released + 5100000U);
        APP_REQUIRE(last.lifecycle.gate.go); return now;
    }
    fsm::RobotInput frontCandidate(unsigned mask = 2U) {
        opponent(mask); next(); auto value = at(now + 1000U, 200U);
        value.opponent_read = {true, value.t_us - 150U, value.t_us - 120U}; return value;
    }
    void reset() {
        robot.reset(); APP_REQUIRE(gate.reset()); input = app_test::input(); previous = {};
        last = fsm::RobotResult{}; trace_size = 0U; port.clear();
    }
};
inline void qualified(const Rig& rig, const fsm::RobotResult& r, unsigned mode,
                      unsigned phase, unsigned cause, unsigned mask, State state,
                      std::uint32_t read_start, std::uint32_t read_end, bool snapshot = false) {
    suffix(r, {READ_START, READ_END, QUALIFIED, HANDOVER});
    CHECK(event(r, READ_START).t_us == read_start); CHECK(event(r, READ_END).t_us == read_end);
    CHECK(event(r, READ_START).value == 1U); CHECK(event(r, READ_END).value == 1U);
    CHECK(event(r, QUALIFIED).t_us == rig.now);
    CHECK(event(r, QUALIFIED).value == cue(mode, phase, cause, mask, snapshot));
    CHECK(event(r, HANDOVER).t_us == rig.now);
    CHECK(event(r, HANDOVER).value == static_cast<unsigned>(state));
    CHECK(r.outputs.ui_state == state); CHECK(r.contract_faults == 0U);
    CHECK_FALSE(r.events.overflowed); CHECK(r.events.rejected == 0U);
    CHECK(r.events.invalid_metadata == 0U); CHECK(rig.trace_size == 5U);
}
struct TxRig : app_test::Rig {
    std::uint32_t now = 0U;
    void opponent(unsigned mask) { source.opp_raw_mask = static_cast<std::uint8_t>(mask ^ 0x78U); }
    const app::TransactionReport& at(std::uint32_t d, Button button = Button::NONE) {
        now = d; source.opponent_read = {true, d, d}; return tick(d, button);
    }
    void next(std::uint32_t delta = 1000U, Button button = Button::NONE) { at(now + delta, button); }
    void shortMode() {
        next(1000U, Button::MODE); next(20000U, Button::MODE); next(); next(20000U);
    }
    std::uint32_t go(Mode mode = Mode::DIRECT) {
        at(0U); next(); next(20000U);
        for (unsigned i = 0U; i < 6U && owner.report().robot.menu.selection.mode != mode; ++i) shortMode();
        APP_REQUIRE(owner.report().robot.menu.selection.mode == mode);
        next(1000U, Button::START); next(20000U, Button::START); next(); next(20000U);
        const auto released = now; APP_REQUIRE(owner.report().robot.lifecycle.gate.start_release);
        at(released + 1500000U); next(); at(released + 4500000U); at(released + 5100000U);
        APP_REQUIRE(owner.report().robot.lifecycle.gate.go); return now;
    }
};
inline unsigned stored(const recorder::AttemptRecorder& recording, unsigned detail) {
    unsigned count = 0U;
    for (std::size_t i = 0U; i < recording.events().size(); ++i) {
        const auto* e = recording.events().at(i); APP_REQUIRE(e != nullptr);
        if (e->data[4] == 10U && e->data[5] == detail) ++count;
    }
    return count;
}
} // namespace p5_abort
