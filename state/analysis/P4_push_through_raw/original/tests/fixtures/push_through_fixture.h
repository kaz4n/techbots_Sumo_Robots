// Supplies D131 timelines from public Robot, Escape and actual Gate contracts.
// Keeps line admission, electrical polarity and physical callbacks observable.
// New independent tests exercise the default and copied 20/100ms configurations.
#pragma once
#include "reactive_profile_fixture.h"
#include <limits>

namespace push_test {
using State = core::State;
using Button = core::ButtonLevel;
constexpr std::uint32_t WINDOW_US = config::EDGE_PUSH_THROUGH_MS * 1000U;
constexpr bool ENABLED = config::EDGE_PUSH_THROUGH_MS != 0U;
inline unsigned bits(unsigned value) {
    return (value & 1U) + ((value >> 1U) & 1U) +
           ((value >> 2U) & 1U) + ((value >> 3U) & 1U);
}
inline edge::EscapeSample sample(std::uint32_t time = 100000U, unsigned mask = 1U) {
    edge::EscapeSample s; s.t_us = time; s.line_mask = static_cast<std::uint8_t>(mask);
    s.motion_permitted = true; s.push_eligible = true; s.centered_front = true;
    return s;
}
inline void deferred(const edge::Escape& owner, const edge::EscapeResult& r) {
    CHECK(owner.pushThroughActive()); CHECK_FALSE(r.escape_required);
    CHECK_FALSE(r.inhibit_motion); CHECK_FALSE(r.entered); CHECK_FALSE(r.exited);
    CHECK_FALSE(r.replanned); CHECK_FALSE(r.inward_valid); CHECK(r.replans == 0U);
    CHECK(r.fault == edge::EscapeFault::NONE); CHECK(r.row.phase == edge::ScriptPhase::IDLE);
}
inline unsigned eventCount(const fsm::RobotResult& r, core::Event type) {
    return reactive_test::count(r, type);
}
inline unsigned edgeFlags(const fsm::RobotResult& r) {
    unsigned flags = 0U;
    for (unsigned i = 0U; i < r.events.count; ++i)
        if (r.events.entries[i].type == core::Event::EDGE) flags |= r.events.entries[i].detail;
    return flags;
}
inline void actualEntry(const edge::Escape& owner, const edge::EscapeResult& r,
                        unsigned mask) {
    CHECK_FALSE(owner.pushThroughActive()); CHECK(r.escape_required); CHECK(r.entered);
    CHECK_FALSE(r.replanned); CHECK(r.replans == 0U);
    CHECK_FALSE(r.inward_valid);
    if (bits(mask) >= 3U) { CHECK(r.fault == edge::EscapeFault::WHITE_PATTERN);
        CHECK(r.inhibit_motion); }
    else { CHECK(r.fault == edge::EscapeFault::NONE); CHECK(r.selected_mask == mask); }
}
struct Rig {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::RobotResult last;
    std::uint32_t now = 0U, source_time = 0U, sequence = 0U;
    unsigned mask = 0U;
    bool explicit_line = false, deliver = true, allow_gate_fault = false;
    explicit Rig(bool explicit_source = false) : explicit_line(explicit_source) {
        APP_REQUIRE(gate.begin()); port.clear();
        input.line.explicit_values = explicit_line; input.opponent_fresh = true;
    }
    void opponent(unsigned logical) {
        input.opp_raw_mask = static_cast<std::uint8_t>(logical ^ config::OPP_ACTIVE_LOW_MASK);
    }
    void white(unsigned value) { mask = value; }
    void lineAt(std::uint32_t time) {
        if (!explicit_line) {
            for (unsigned i = 0U; i < 4U; ++i)
                input.line_raw_us[i] = (mask & (1U << i)) ? 100U : 1000U;
            return;
        }
        input.line.presence = core::LinePresence::ABSENT;
        if (!deliver || (sequence != 0U && time - source_time < 2000U)) return;
        source_time = time; input.line.presence = core::LinePresence::VALID;
        input.line.sequence = ++sequence; input.line.started_us = time - 100U;
        input.line.completed_us = time - 1U;
        input.line.white_candidates = static_cast<std::uint8_t>(mask);
    }
    fsm::RobotResult at(std::uint32_t time, Button button = Button::NONE) {
        lineAt(time); input.t_us = time; input.button = button;
#if SUMOX_TIMING_EVIDENCE
        input.opponent_read = {true, time, time};
#endif
        last = robot.step(input); now = time;
        if (last.fresh) { port.now = time; input.previous = gate.apply(time, last).feedback;
            if (!allow_gate_fault) APP_REQUIRE(input.previous.applied_valid); }
        return last;
    }
    fsm::RobotResult next(std::uint32_t delta = 1000U) { return at(now + delta); }
    std::uint32_t release(std::uint32_t base = 0U) {
        at(base); at(base + 1000U); at(base + 21000U);
        at(base + 22000U, Button::START); at(base + 42000U, Button::START);
        at(base + 43000U); APP_REQUIRE(at(base + 63000U).lifecycle.gate.start_release);
        return now;
    }
    std::uint32_t go(std::uint32_t base = 0U) {
        const auto start = release(base); at(start + 1500000U); at(start + 1501000U);
        at(start + 4500000U); at(start + 5099999U);
        APP_REQUIRE(at(start + 5100000U).lifecycle.gate.go); return now;
    }
    std::uint32_t attack(bool contact = true, std::uint32_t base = 0U,
                         unsigned target = 2U) {
        opponent(target); const auto start = go(base);
        APP_REQUIRE(at(start + 1000U).outputs.ui_state == State::TRACK);
        APP_REQUIRE(at(start + 2000U).outputs.ui_state == State::TRACK);
        input.ax_g = contact ? 2.0F : 0.0F;
        APP_REQUIRE(at(start + 3000U).outputs.ui_state == State::ATTACK);
        APP_REQUIRE(last.contact == contact); input.ax_g = 0.0F;
        at(start + 53000U); return now;
    }
};
inline void stopped(const Rig& rig, const fsm::RobotResult& r) {
    CHECK_FALSE(r.outputs.motors_enabled); CHECK(r.outputs.duty_l == 0.0F);
    CHECK(r.outputs.duty_r == 0.0F); app_test::zero(rig.port);
}
inline void attacking(const Rig& rig, const fsm::RobotResult& r, unsigned mask) {
    CHECK(r.outputs.ui_state == State::ATTACK); CHECK(r.line_mask == mask);
    CHECK(r.outputs.motors_enabled); CHECK(r.contract_faults == 0U);
    CHECK(r.escape_fault == edge::EscapeFault::NONE);
    CHECK((edgeFlags(r) & (logframe::ENTERED | logframe::EXITED | logframe::REPLANNED)) == 0U);
    CHECK(rig.port.enabled == (MOTORS_ALLOWED != 0));
    if (!MOTORS_ALLOWED) app_test::zero(rig.port);
}
inline void escaped(const Rig& rig, const fsm::RobotResult& r, unsigned mask) {
    CHECK(r.outputs.ui_state == State::EDGE_ESCAPE); CHECK(r.line_mask == mask);
    CHECK_FALSE(r.contact); CHECK(eventCount(r, core::Event::REFLANK_PHASE) == 0U);
    if (mask <= 3U) { CHECK(r.outputs.duty_l == 0.0F); CHECK(r.outputs.duty_r == 0.0F);
        for (auto pulse : rig.port.pulses) CHECK(pulse == 0U); }
}
inline std::uint32_t freshContactAfterEscape(Rig& rig, std::uint32_t entered) {
    rig.input.imu_ok = false; rig.white(0U); rig.at(entered + 1000U);
    rig.at(entered + 121000U); const auto exit = rig.at(entered + 361000U);
    APP_REQUIRE(exit.outputs.ui_state == State::TRACK); rig.next();
    rig.input.imu_ok = true; rig.input.ax_g = 2.0F;
    APP_REQUIRE(rig.next().outputs.ui_state == State::ATTACK);
    APP_REQUIRE(rig.last.contact); rig.input.ax_g = 0.0F; rig.next(53000U); return rig.now;
}
inline void freshContactAfterReflank(Rig& rig, std::uint32_t entered) {
    rig.input.imu_ok = false; rig.at(entered + 150000U); rig.at(entered + 850000U);
    APP_REQUIRE(rig.at(entered + 1250000U).outputs.ui_state == State::TRACK);
    rig.next(); rig.input.imu_ok = true; rig.input.ax_g = 2.0F;
    APP_REQUIRE(rig.next().outputs.ui_state == State::ATTACK);
    APP_REQUIRE(rig.last.contact); rig.input.ax_g = 0.0F; rig.next(53000U);
}
struct RuntimeSource : service_reset_test::Source {
    unsigned white_mask = 0U;
    static line_qtr::Snapshot advance(void* c) {
        auto& f = *static_cast<RuntimeSource*>(c); auto s = Fake::lineAdvance(c);
        if (s.phase != line_qtr::Phase::COMPLETE) return s;
        const auto white = qtr_cal_test::frame(s.started_us, s.sequence, 100U, 103U);
        for (unsigned i = 0U; i < 4U; ++i)
            if (f.white_mask & (1U << i)) s.pad[i] = white.pad[i];
        f.line = s; return s;
    }
    app::SourcePort sourcePort() {
        auto p = Source::sourcePort(); p.advanceLines = advance; return p;
    }
};
struct RuntimeRig {
    RuntimeSource fake;
    app::Runtime owner{fake.motorPort(), fake.adcPort(), fake.sourcePort()};
    bool next() { fake.now = owner.report().next_release_us; return owner.step(); }
    bool run(unsigned ticks, std::uint16_t raw = service_reset_test::NONE) {
        fake.button_raw = raw;
        for (unsigned i = 0U; i < ticks; ++i) if (!next()) return false;
        return true;
    }
    const fsm::RobotResult& robot() const { return owner.transaction().report().robot; }
    void attack() {
        fake.opponent_mask = static_cast<std::uint8_t>(2U ^ config::OPP_ACTIVE_LOW_MASK);
        APP_REQUIRE(owner.begin(runtime_test::grants(true, false)));
        APP_REQUIRE(run(35U)); APP_REQUIRE(run(30U, service_reset_test::START));
        APP_REQUIRE(run(30U)); APP_REQUIRE(run(5160U));
        APP_REQUIRE(robot().outputs.ui_state == State::ATTACK);
    }
};
} // namespace push_test
