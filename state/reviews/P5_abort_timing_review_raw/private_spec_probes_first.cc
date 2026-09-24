// Probes D135 qualified-abort evidence through adopted public contracts.
// Numeric wire expectations and stimuli were authored before implementation review.
// Root executes these frozen doctest cases later in serial P5 M0 and M1 builds.
#include "fixtures/app_transaction_fixture.h"
#include "core/openers.h"
#include <array>
#include <cstdint>
#include <initializer_list>

#if !SUMOX_P5_ABORT_TIMING
#error "Private D135 probes require the exclusive P5 profile"
#endif

namespace private_d135 {
using Button = core::ButtonLevel;
using Mode = core::Mode;
using State = core::State;

// Intentionally use adopted numeric wire codes, not a production timing enum.
bool qualified(std::uint16_t word) {
    const unsigned mode = word & 7U, phase = (word >> 3U) & 7U;
    const unsigned cause = (word >> 6U) & 3U, mask = (word >> 8U) & 127U;
    const bool snapshot = (word & 32768U) != 0U, front = (mask & 7U) != 0U;
    if (mode == 3U && phase == 0U)
        return (cause == 1U && front) ||
            (cause == 2U && !front && (mask & 120U) != 0U && !snapshot);
    if (snapshot) return false;
    if (mode == 6U && phase == 4U)
        return cause == 2U && (mask & 120U) != 0U;
    if ((mode == 4U || mode == 5U) && (phase == 2U || phase == 3U))
        return cause == 1U && front;
    if ((mode == 1U || mode == 2U || mode == 6U) && phase >= 1U && phase <= 3U) {
        const unsigned outer = mode == 2U ? 40U : 80U;
        return (cause == 1U && phase != 1U && front) ||
            (cause == 2U && (mask & outer) != 0U && (phase == 1U || !front));
    }
    return false;
}

std::uint16_t cue(unsigned mode, unsigned phase, unsigned cause, unsigned mask,
                  bool snapshot = false) {
    return static_cast<std::uint16_t>(mode | (phase << 3U) | (cause << 6U) |
                                     (mask << 8U) | (snapshot ? 32768U : 0U));
}
logframe::EventInput wire(unsigned detail, unsigned value, std::uint32_t time = 0U) {
    return {time, static_cast<core::Event>(10U), static_cast<std::uint8_t>(detail),
            static_cast<std::uint16_t>(value)};
}
unsigned count(const fsm::RobotResult& r, unsigned detail) {
    unsigned result = 0U;
    for (unsigned i = 0; i < r.events.count; ++i)
        if (static_cast<unsigned>(r.events.entries[i].type) == 10U &&
            r.events.entries[i].detail == detail) ++result;
    return result;
}
logframe::EventInput event(const fsm::RobotResult& r, unsigned detail) {
    APP_REQUIRE(count(r, detail) == 1U);
    for (unsigned i = 0; i < r.events.count; ++i)
        if (static_cast<unsigned>(r.events.entries[i].type) == 10U &&
            r.events.entries[i].detail == detail) return r.events.entries[i];
    return {};
}
unsigned traceCount(const fsm::RobotResult& r) {
    unsigned result = 0U;
    for (unsigned i = 0; i < r.events.count; ++i)
        result += static_cast<unsigned>(r.events.entries[i].type) == 10U ? 1U : 0U;
    return result;
}
void suffix(const fsm::RobotResult& r, const std::initializer_list<unsigned>& details) {
    APP_REQUIRE(r.events.count >= details.size());
    unsigned index = r.events.count - static_cast<unsigned>(details.size());
    for (const auto detail : details) {
        CHECK(static_cast<unsigned>(r.events.entries[index].type) == 10U);
        CHECK(r.events.entries[index++].detail == detail);
    }
}

// This fixture uses genuine Robot decisions and MotorGate callback receipts.
// Port clocks and sensor observations are synthetic host stimuli, not hardware.
struct Rig {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::PreviousTick previous;
    fsm::RobotResult last;
    std::uint32_t now = 0U;
    Rig() {
        APP_REQUIRE(gate.begin()); port.clear();
        input.timing.explicit_start = true; input.timing.start_valid = true;
    }
    void opponent(unsigned mask) { input.opp_raw_mask = static_cast<std::uint8_t>(mask ^ 120U); }
    fsm::RobotInput at(std::uint32_t time, Button button = Button::NONE) const {
        auto sample = input; sample.t_us = time; sample.button = button;
        sample.previous = previous; sample.timing.started_us = time;
        sample.opponent_read = {true, time, time}; return sample;
    }
    fsm::RobotResult submit(fsm::RobotInput sample, std::uint32_t application_delay = 0U) {
        auto result = robot.step(sample);
        if (!result.fresh) return result;
        last = result; now = sample.t_us;
        CHECK_FALSE(result.events.overflowed); CHECK(result.events.rejected == 0U);
        CHECK(result.events.invalid_metadata == 0U); CHECK(result.events.count <= 21U);
        port.clear(now + application_delay);
        const auto applied = gate.apply(now, result);
        APP_REQUIRE(applied.consumed); APP_REQUIRE(applied.feedback.applied_valid);
        previous = applied.feedback; previous.duration_valid = true;
        previous.completed_us = previous.applied_us;
        previous.execution_us = previous.completed_us - sample.timing.started_us;
        return result;
    }
    fsm::RobotResult step(std::uint32_t time, Button button = Button::NONE) {
        return submit(at(time, button));
    }
    std::uint32_t select(Mode mode, std::uint32_t base = 0U) {
        step(base); step(base + 1000U); step(base + 21000U);
        for (unsigned n = 0U; last.menu.selection.mode != mode && n < 6U; ++n) {
            const auto t = now + 1000U;
            step(t, Button::MODE); step(t + 20000U, Button::MODE);
            step(t + 21000U); APP_REQUIRE(step(t + 41000U).menu.selection_changed);
        }
        APP_REQUIRE(last.menu.selection.mode == mode); return now;
    }
    std::uint32_t release(Mode mode, std::uint32_t base = 0U) {
        const auto t = select(mode, base) + 1000U;
        step(t, Button::START); step(t + 20000U, Button::START);
        step(t + 21000U); const auto r = step(t + 41000U);
        APP_REQUIRE(r.lifecycle.gate.start_release);
        const auto h = event(r, 0U);
        CHECK(h.t_us == now); CHECK(h.value == (MOTORS_ALLOWED ? 517U : 513U));
        unsigned index = 0U;
        while (index < r.events.count && r.events.entries[index].type != core::Event::START_RELEASE) ++index;
        APP_REQUIRE(index + 1U < r.events.count);
        CHECK(r.events.entries[index + 1U].detail == 0U);
        CHECK(static_cast<unsigned>(r.events.entries[index + 1U].type) == 10U);
        return now;
    }
    std::uint32_t beforeGo(Mode mode, unsigned mask = 0U, std::uint32_t base = 0U) {
        const auto r = release(mode, base);
        step(r + 1500000U); step(r + 1501000U);
        opponent(mask); step(r + 4500000U); step(r + 5099000U);
        APP_REQUIRE(!last.outputs.motors_enabled);
        CHECK(last.outputs.duty_l == 0.0F); CHECK(last.outputs.duty_r == 0.0F);
        return r + 5100000U;
    }
};

TEST_CASE("D135 private B12 exact numeric metadata table") {
    CHECK(fsm::RobotResult::OPENER_TIMING_PROFILE);
    CHECK_FALSE(fsm::RobotResult::TIMING_EVIDENCE_PROFILE);
    CHECK(logframe::ROBOT_EVENT_CAPACITY == 21U); CHECK(logframe::EVENT_BYTES == 8U);
    for (unsigned word = 0U; word < 65536U; ++word)
        CHECK(logframe::validEventMetadata(wire(18U, word)) == qualified(static_cast<std::uint16_t>(word)));
    for (unsigned value = 0U; value < 65536U; ++value) {
        CHECK(logframe::validEventMetadata(wire(0U, value)) == (value == 513U || value == 517U));
        for (unsigned detail : {16U, 17U, 20U, 23U, 24U})
            CHECK(logframe::validEventMetadata(wire(detail, value)) == (value == 1U));
        CHECK(logframe::validEventMetadata(wire(19U, value)) == (value >= 5U && value <= 7U));
        for (unsigned detail : {21U, 22U})
            CHECK(logframe::validEventMetadata(wire(detail, value)) == (value == 1U || value == 2U));
        CHECK(logframe::validEventMetadata(wire(25U, value)) == (value <= 11U));
    }
    for (unsigned detail = 1U; detail < 256U; ++detail)
        if (detail < 16U || detail > 25U)
            for (unsigned value : {0U, 1U, 2U, 513U, 517U, 65535U})
                CHECK_FALSE(logframe::validEventMetadata(wire(detail, value)));
    logframe::EventBytes bytes;
    APP_REQUIRE(logframe::packEvent(wire(18U, 0x8243U, 0x12345678U), bytes) == logframe::PackStatus::OK);
    const std::uint8_t expected[8] = {0x78U, 0x56U, 0x34U, 0x12U, 10U, 18U, 0x43U, 0x82U};
    for (unsigned i = 0U; i < 8U; ++i) CHECK(bytes.data[i] == expected[i]);
}

TEST_CASE("D135 private B12 DIRECT pulse distinguishes snapshot current and natural") {
    openers::Direct direct;
    APP_REQUIRE(direct.start(100U, 0.0F, 2U));
    auto r = direct.step(101U, 0.0F, true, 0U);
    CHECK(static_cast<unsigned>(r.abort.cause) == 3U); CHECK(r.abort.snapshot_front_present);
    CHECK(static_cast<unsigned>(direct.step(102U, 0.0F, true, 2U).abort.cause) == 0U);
    direct.reset(); CHECK(static_cast<unsigned>(direct.step(103U, 0.0F, true, 2U).abort.cause) == 0U);
    APP_REQUIRE(direct.start(100U, 0.0F, 2U));
    r = direct.step(400100U, 0.0F, true, 0x92U);
    CHECK(static_cast<unsigned>(r.abort.cause) == 1U); CHECK(r.abort.effective_mask == 18U);
    CHECK(static_cast<unsigned>(r.abort.phase) == 0U); CHECK(r.abort.snapshot_front_present);
    APP_REQUIRE(direct.start(100U, 0.0F, 0U));
    r = direct.step(400100U, 0.0F, true, 16U);
    CHECK(static_cast<unsigned>(r.abort.cause) == 2U); CHECK_FALSE(r.abort.snapshot_front_present);
    APP_REQUIRE(direct.start(100U, 0.0F, 0U));
    r = direct.step(400100U, 0.0F, true, 0U);
    CHECK(static_cast<unsigned>(r.abort.cause) == 4U); CHECK(r.exit == openers::Exit::SEARCH);
}

TEST_CASE("D135 private B12 phase at actual predicate and mirrored outer priority") {
    for (const auto mode : {Mode::SIDESTEP_R, Mode::SIDESTEP_L, Mode::ARC_R, Mode::ARC_L}) {
        if (!core::modeAvailable(mode)) continue;
        openers::Flank flank; const bool right = mode == Mode::SIDESTEP_R || mode == Mode::ARC_R;
        const bool arc = mode == Mode::ARC_R || mode == Mode::ARC_L;
        APP_REQUIRE(flank.start(100U, 0.0F, true, mode));
        openers::Sample s; s.t_us = 101U; s.imu_ok = true; s.confirmed_mask = 2U;
        auto r = flank.step(s); CHECK(r.exit == openers::Exit::NONE);
        CHECK(static_cast<unsigned>(r.abort.cause) == 0U);
        s.t_us = 102U; s.heading_deg = (arc ? 80.0F : 50.0F) * (right ? 1.0F : -1.0F);
        r = flank.step(s); CHECK(r.exit == openers::Exit::FRONT_TARGET);
        CHECK(static_cast<unsigned>(r.abort.phase) == 2U); CHECK(static_cast<unsigned>(r.abort.cause) == 1U);
        CHECK_FALSE(r.abort.snapshot_front_present); CHECK(r.abort.effective_mask == 2U);
        CHECK(static_cast<unsigned>(flank.step(s).abort.cause) == 0U);
        if (!arc) {
            APP_REQUIRE(flank.start(100U, 0.0F, true, mode));
            s.t_us = 101U; s.heading_deg = 0.0F; s.confirmed_mask = right ? 18U : 10U;
            r = flank.step(s); CHECK(r.exit == openers::Exit::SIDE_OR_REAR_TARGET);
            CHECK(static_cast<unsigned>(r.abort.phase) == 1U); CHECK(static_cast<unsigned>(r.abort.cause) == 2U);
        }
    }
}

TEST_CASE("D135 private B12 natural target exit is not an abort predicate") {
    openers::Flank flank; APP_REQUIRE(flank.start(0U, 0.0F, true, Mode::SIDESTEP_R));
    openers::Sample s; s.t_us = 1000U; s.imu_ok = true; s.heading_deg = 50.0F;
    APP_REQUIRE(flank.step(s).phase == openers::Phase::TRAVERSE);
    s.t_us = 2000U; s.confirmed_mask = 8U;
    APP_REQUIRE(flank.step(s).phase == openers::Phase::TURN_IN);
    s.t_us = 3000U; s.heading_deg = -60.0F;
    const auto r = flank.step(s);
    CHECK(r.exit == openers::Exit::SIDE_OR_REAR_TARGET);
    CHECK(static_cast<unsigned>(r.abort.phase) == 3U); CHECK(static_cast<unsigned>(r.abort.cause) == 4U);
}

TEST_CASE("D135 private B12 WAIT widening is not abort and inner phase survives") {
    if (!core::modeAvailable(Mode::WAIT)) return;
    openers::Wait wait; APP_REQUIRE(wait.start(0U, 0.0F));
    openers::Sample s; s.t_us = 1000U; s.imu_ok = true; s.confirmed_mask = 2U;
    auto r = wait.step(s); CHECK(r.phase == openers::WaitPhase::HOLD);
    CHECK(static_cast<unsigned>(r.flank.abort.cause) == 0U);
    s.t_us = 2000U; s.confirmed_mask = 3U; r = wait.step(s);
    CHECK(r.approach_cue); CHECK(r.phase == openers::WaitPhase::FLANK);
    CHECK(static_cast<unsigned>(r.flank.abort.cause) == 0U);
    s.t_us = 3000U; s.confirmed_mask = 19U; r = wait.step(s);
    CHECK(static_cast<unsigned>(r.flank.abort.cause) == 2U);
    CHECK(static_cast<unsigned>(r.flank.abort.phase) == 1U);
    APP_REQUIRE(wait.start(0U, 0.0F)); s.t_us = 1000U; s.confirmed_mask = 18U; r = wait.step(s);
    CHECK(static_cast<unsigned>(r.flank.abort.cause) == 2U);
    CHECK(static_cast<unsigned>(r.flank.abort.phase) == 4U);
}

TEST_CASE("D135 private B12 real Gate DIRECT GO cue and retained 999 1000 1001 latency") {
    for (unsigned delay : {999U, 1000U, 1001U}) for (auto base : {0U, 0xFFFF0000U}) {
        Rig rig; const auto d = rig.beforeGo(Mode::DIRECT, 2U, base);
        const auto r = rig.submit(rig.at(d), delay);
        APP_REQUIRE(r.lifecycle.gate.go); APP_REQUIRE(r.opponent_mask == 2U);
        CHECK(r.outputs.ui_state == State::TRACK); CHECK_FALSE(r.contact);
        suffix(r, {16U, 17U, 18U, 19U});
        CHECK(event(r, 16U).t_us == d); CHECK(event(r, 17U).t_us == d);
        CHECK(event(r, 18U).t_us == d); CHECK(event(r, 18U).value == cue(3U, 0U, 1U, 2U, true));
        CHECK(event(r, 19U).t_us == d); CHECK(event(r, 19U).value == 5U);
        CHECK(count(r, 20U) == 0U);
        const auto closed = rig.step(d + delay + 1000U);
        const auto a = event(closed, 20U);
        CHECK(a.t_us == d + delay); CHECK(a.value == 1U); CHECK(a.t_us - d == delay);
        CHECK(traceCount(closed) == 1U);
        CHECK(count(rig.step(d + delay + 2000U), 20U) == 0U);
    }
}

TEST_CASE("D135 private B12 side predicate with coexisting front routes TRACK") {
    Rig rig; const auto d = rig.beforeGo(Mode::SIDESTEP_R, 18U);
    const auto r = rig.step(d); APP_REQUIRE(r.lifecycle.gate.go);
    CHECK(r.outputs.ui_state == State::TRACK); CHECK(r.opponent_mask == 18U);
    CHECK(event(r, 18U).value == cue(1U, 1U, 2U, 18U));
    CHECK(event(r, 19U).value == 5U); CHECK_FALSE(r.contact);
    CHECK(count(rig.step(d + 1000U), 20U) == 1U);
}

TEST_CASE("D135 private B12 source invalidity terminates once without changing routing") {
    for (unsigned kind = 0U; kind < 5U; ++kind) {
        Rig rig; const auto d = rig.beforeGo(Mode::DIRECT, 2U);
        auto sample = rig.at(d); sample.timing.started_us = d - 200U;
        sample.opponent_read = {true, d - 150U, d - 120U};
        if (kind == 0U) sample.opponent_read.valid = false;
        if (kind == 1U) sample.opponent_read.started_us = d - 201U;
        if (kind == 2U) sample.opponent_read.completed_us = d + 1U;
        if (kind == 3U) sample.opponent_read.started_us = d - 119U;
        if (kind == 4U) sample.timing.started_us = d - 0x80000000U;
        const auto r = rig.submit(sample);
        CHECK(r.outputs.ui_state == State::TRACK); CHECK(r.opponent_mask == 2U);
        CHECK(traceCount(r) == 1U); CHECK(event(r, 23U).t_us == d); CHECK(event(r, 23U).value == 1U);
        CHECK(traceCount(rig.step(d + 1000U)) == 0U);
        CHECK(traceCount(rig.step(d + 2000U)) == 0U);
    }
}

TEST_CASE("D135 private B12 full token duration and enabled receipt cannot be repaired") {
    for (unsigned fault = 0U; fault < 4U; ++fault) {
        Rig rig; const auto d = rig.beforeGo(Mode::DIRECT, 2U); rig.step(d);
        APP_REQUIRE(count(rig.last, 19U) == 1U);
        if (fault == 0U) rig.previous.token ^= (std::uint64_t{1} << 32U);
        if (fault == 1U) rig.previous.duration_valid = false;
        if (fault == 2U) ++rig.previous.execution_us;
        if (fault == 3U) {
            rig.previous.motors_enabled = false; rig.previous.duty_l = 0.0F; rig.previous.duty_r = 0.0F;
        }
        const auto r = rig.step(d + 1000U);
        if (fault == 3U && !MOTORS_ALLOWED) CHECK(count(r, 20U) == 1U);
        else { CHECK(count(r, 20U) == 0U); CHECK(event(r, 24U).value == 1U); }
        CHECK(traceCount(rig.step(d + 2000U)) == 0U);
    }
}

TEST_CASE("D135 private B12 previous receipt closes before current STOP") {
    Rig rig; const auto d = rig.beforeGo(Mode::DIRECT, 2U); rig.step(d);
    auto sample = rig.at(d + 1000U); sample.stop_requested = true;
    const auto r = rig.submit(sample);
    CHECK(r.outputs.ui_state == State::STOPPED); CHECK_FALSE(r.outputs.motors_enabled);
    CHECK(event(r, 20U).t_us == d); CHECK(count(r, 22U) == 0U);
    APP_REQUIRE(r.events.count != 0U);
    CHECK(static_cast<unsigned>(r.events.entries[0].type) == 10U); CHECK(r.events.entries[0].detail == 20U);
}

TEST_CASE("D135 private B12 source priority over actual edge and no later retry") {
    Rig rig; const auto d = rig.beforeGo(Mode::DIRECT, 2U);
    auto sample = rig.at(d); sample.opponent_read.valid = false; sample.line_raw_us[0] = 100U;
    const auto r = rig.submit(sample);
    CHECK(r.outputs.ui_state == State::EDGE_ESCAPE); CHECK(count(r, 23U) == 1U);
    CHECK(count(r, 18U) == 0U); CHECK(count(r, 22U) == 0U);
    CHECK(traceCount(rig.step(d + 1000U)) == 0U);
}

TEST_CASE("D135 private B12 actual Transaction owns receipt recording and aborted tail") {
    for (bool abort_tail : {false, true}) {
        app_test::Rig rig;
        auto at = [&](std::uint32_t d, Button button = Button::NONE) -> const app::TransactionReport& {
            rig.source.opponent_read = {true, d, d}; return rig.tick(d, button);
        };
        at(0U); at(1000U); at(21000U);
        for (unsigned m = 0U; m < 2U; ++m) {
            const auto t = 22000U + m * 42000U;
            at(t, Button::MODE); at(t + 20000U, Button::MODE); at(t + 21000U); at(t + 41000U);
        }
        APP_REQUIRE(rig.owner.report().robot.menu.selection.mode == Mode::DIRECT);
        at(106000U, Button::START); at(126000U, Button::START); at(127000U);
        APP_REQUIRE(at(147000U).robot.lifecycle.gate.start_release);
        at(1647000U); at(1648000U); rig.source.opp_raw_mask = 122U;
        at(4647000U); at(5246000U); const auto d = 5247000U;
        APP_REQUIRE(at(d).robot.lifecycle.gate.go);
        APP_REQUIRE(count(rig.owner.report().robot, 19U) == 1U);
        if (abort_tail) rig.owner.abort(); else at(d + 1000U);
        unsigned applied = 0U, headers = 0U;
        const auto& buffer = rig.owner.recording().events();
        for (std::size_t i = 0U; i < buffer.size(); ++i) {
            const auto* e = buffer.at(i); APP_REQUIRE(e != nullptr);
            if (e->data[4] == 10U) { applied += e->data[5] == 20U; headers += e->data[5] == 0U; }
        }
        CHECK(headers == 1U); CHECK(applied == (abort_tail ? 0U : 1U));
        if (abort_tail) { CHECK(rig.owner.recording().incomplete()); CHECK(rig.owner.report().fault == app::Fault::ABORTED); }
    }
}

TEST_CASE("D135 private B15 bounded batch retains prefix and counts every rejected suffix") {
    logframe::EventBatch batch;
    for (unsigned i = 0U; i < 21U; ++i) APP_REQUIRE(logframe::appendEvent(batch, wire(16U, 1U, i)));
    for (unsigned detail : {16U, 17U, 18U, 19U}) {
        const unsigned value = detail == 18U ? cue(3U, 0U, 1U, 2U) : detail == 19U ? 5U : 1U;
        CHECK_FALSE(logframe::appendEvent(batch, wire(detail, value, 100U)));
    }
    CHECK(batch.count == 21U); CHECK(batch.overflowed); CHECK(batch.rejected == 4U);
    CHECK(batch.invalid_metadata == 0U);
    for (unsigned i = 0U; i < 21U; ++i) { CHECK(batch.entries[i].t_us == i); CHECK(batch.entries[i].detail == 16U); }
}
} // namespace private_d135
