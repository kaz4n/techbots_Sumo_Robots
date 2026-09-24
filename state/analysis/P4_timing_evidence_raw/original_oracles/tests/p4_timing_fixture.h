// Supplies D129 public Robot, Transaction and Gate timing observations.
// Separates explicitly synthetic receipts from actual Gate callback receipts.
// Independent M0/M1 cases use genuine local START gestures and explicit clocks.
#pragma once
#include "fixtures/app_transaction_fixture.h"
#include "fixtures/app_service_reset/fixture.h"
#include <array>
#include <cmath>
#include <limits>

namespace p4_time {
using Detail = logframe::TimingDetail;
using State = core::State;
using Button = core::ButtonLevel;
inline unsigned count(const fsm::RobotResult& r, int detail = -1) {
    unsigned n = 0U;
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == core::Event::TIMING &&
            (detail < 0 || r.events.entries[i].detail == detail)) ++n;
    return n;
}
inline unsigned count(const fsm::RobotResult& r, Detail d) {
    return count(r, static_cast<int>(d));
}
inline logframe::EventInput event(const fsm::RobotResult& r, Detail d) {
    APP_REQUIRE(count(r, d) == 1U);
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == core::Event::TIMING &&
            r.events.entries[i].detail == static_cast<unsigned>(d)) return r.events.entries[i];
    return {};
}
inline void terminal(const fsm::RobotResult& r, Detail d, std::uint32_t time) {
    CHECK(count(r) == 1U); const auto e = event(r, d);
    CHECK(e.t_us == time); CHECK(e.value == 1U);
    APP_REQUIRE(r.events.count != 0U);
    CHECK(r.events.entries[r.events.count - 1U].type == core::Event::TIMING);
}
inline void pair(const fsm::RobotResult& r, std::uint32_t start, std::uint32_t end) {
    CHECK(event(r, Detail::LOSS_READ_START).t_us == start);
    CHECK(event(r, Detail::LOSS_READ_END).t_us == end);
    unsigned index = 0U;
    while (index < r.events.count && r.events.entries[index].type != core::Event::TIMING) ++index;
    APP_REQUIRE(index + 1U < r.events.count);
    CHECK(r.events.entries[index].detail == 1U); CHECK(r.events.entries[index + 1U].detail == 2U);
    for (unsigned i = index; i < r.events.count; ++i) CHECK(r.events.entries[i].type == core::Event::TIMING);
}
inline motors::Port gatePort(app_test::Port& port, bool coarse) {
    auto result = port.port();
    if (coarse) for (auto& period : result.period_cycles) period = 1U;
    return result;
}
struct Rig {
    app_test::Port port;
    motors::MotorGate gate;
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::PreviousTick previous;
    fsm::RobotResult last;
    std::array<logframe::EventInput, 32> trace{};
    unsigned trace_size = 0U;
    std::uint32_t now = 0U;
    bool real_gate = false, source_window = true;
    explicit Rig(bool actual_gate = false, bool coarse = false)
        : gate(gatePort(port, coarse)), real_gate(actual_gate) {
        input.timing.explicit_start = true; input.timing.start_valid = true;
        if (real_gate) APP_REQUIRE(gate.begin());
    }
    void opponent(unsigned mask) { input.opp_raw_mask = static_cast<std::uint8_t>(mask ^ 0x78U); }
    void white(unsigned mask) {
        for (unsigned i = 0U; i < 4U; ++i) input.line_raw_us[i] = mask & (1U << i) ? 100U : 1000U;
    }
    fsm::RobotInput at(std::uint32_t decision, std::uint32_t acquisition = 0U) const {
        auto value = input; value.t_us = decision; value.previous = previous;
        value.timing.started_us = decision - acquisition;
        value.opponent_read = {source_window, decision - acquisition, decision}; return value;
    }
    fsm::RobotResult submit(fsm::RobotInput value, std::uint32_t apply_delay = 0U,
                            std::uint32_t complete_delay = 0U) {
        const auto r = robot.step(value); if (!r.fresh) return r;
        last = r; now = value.t_us; APP_REQUIRE(r.events.count <= 26U);
        CHECK_FALSE(r.events.overflowed); CHECK(r.events.invalid_metadata == 0U);
        for (unsigned i = 0U; i < r.events.count; ++i) if (r.events.entries[i].type == core::Event::TIMING) {
            APP_REQUIRE(trace_size < trace.size()); trace[trace_size++] = r.events.entries[i];
        }
        if (real_gate) {
            port.now = now + apply_delay; const auto applied = gate.apply(now, r);
            APP_REQUIRE(applied.consumed); APP_REQUIRE(applied.feedback.applied_valid);
            previous = applied.feedback;
        } else {
            // Synthetic application receipts exercise contract validation only.
            previous = {}; previous.applied_valid = true; previous.token = r.token;
            previous.applied_us = now + apply_delay; previous.motors_enabled = r.outputs.motors_enabled;
            previous.duty_l = r.outputs.duty_l; previous.duty_r = r.outputs.duty_r;
        }
        previous.duration_valid = true; previous.completed_us = now + complete_delay;
        previous.execution_us = previous.completed_us - value.timing.started_us;
        return r;
    }
    fsm::RobotResult step(std::uint32_t time, Button button = Button::NONE) {
        auto value = at(time); value.button = button; return submit(value);
    }
    std::uint32_t release(std::uint32_t base = 0U) {
        step(base); step(base + 1000U); step(base + 21000U);
        step(base + 22000U, Button::START); step(base + 42000U, Button::START);
        step(base + 43000U); APP_REQUIRE(step(base + 63000U).lifecycle.gate.start_release);
        return base + 63000U;
    }
    std::uint32_t go(std::uint32_t base = 0U) {
        const auto r = release(base); step(r + 1500000U); step(r + 1501000U);
        step(r + 4500000U); step(r + 5099999U);
        APP_REQUIRE(step(r + 5100000U).lifecycle.gate.go); return now;
    }
    std::uint32_t approach(std::uint32_t base = 0U, unsigned front = 2U) {
        opponent(front); const auto g = go(base);
        APP_REQUIRE(step(g + 1000U).outputs.ui_state == State::TRACK);
        APP_REQUIRE(step(g + 2000U).outputs.ui_state == State::TRACK);
        APP_REQUIRE(step(g + 3000U).outputs.ui_state == State::ATTACK);
        step(g + 4000U); step(g + 53000U);
        APP_REQUIRE(!last.contact); APP_REQUIRE(last.outputs.duty_l > 0.0F && last.outputs.duty_r > 0.0F);
        return now;
    }
    std::uint32_t onset(unsigned residual = 0U) {
        opponent(residual); auto value = at(now + 1000U, 200U);
        value.opponent_read = {true, value.t_us - 150U, value.t_us - 120U}; submit(value); return now;
    }
    std::uint32_t brake(std::uint32_t loss, std::uint32_t apply_delay = 0U,
                        std::uint32_t complete_delay = 0U) {
        const auto d = loss + 30000U; submit(at(d), apply_delay, complete_delay);
        APP_REQUIRE(last.outputs.duty_l == 0.0F && last.outputs.duty_r == 0.0F); return d;
    }
};
struct TxRig : app_test::Rig {
    std::uint32_t now = 0U;
    void opponent(unsigned mask) { source.opp_raw_mask = static_cast<std::uint8_t>(mask ^ 0x78U); }
    const app::TransactionReport& at(std::uint32_t time, Button button = Button::NONE) {
        now = time; source.opponent_read = {true, time, time}; return tick(time, button);
    }
    std::uint32_t release(std::uint32_t base = 0U) {
        at(base); at(base + 1000U); at(base + 21000U);
        at(base + 22000U, Button::START); at(base + 42000U, Button::START);
        at(base + 43000U); APP_REQUIRE(at(base + 63000U).robot.lifecycle.gate.start_release);
        return now;
    }
    std::uint32_t approach(std::uint32_t base = 0U) {
        opponent(2U); const auto r = release(base);
        at(r + 1500000U); at(r + 1501000U); at(r + 4500000U); at(r + 5099999U);
        APP_REQUIRE(at(r + 5100000U).robot.lifecycle.gate.go);
        const auto g = now; at(g + 1000U); at(g + 2000U); at(g + 3000U); at(g + 4000U);
        APP_REQUIRE(at(g + 53000U).robot.outputs.ui_state == State::ATTACK); return now;
    }
};
inline unsigned stored(const recorder::AttemptRecorder& source, Detail detail) {
    unsigned n = 0U;
    for (std::size_t i = 0U; i < source.events().size(); ++i) {
        const auto* e = source.events().at(i); APP_REQUIRE(e != nullptr);
        if (e->data[4] == 10U && e->data[5] == static_cast<unsigned>(detail)) ++n;
    }
    return n;
}
} // namespace p4_time
