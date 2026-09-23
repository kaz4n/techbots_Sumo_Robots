// Proves D095 ownership with actual Robot, MotorGate and AttemptRecorder instances.
// Independent clocks distinguish acquisition, decision, application and completion.
// Host tests cover both motor macros, source provenance and an actual 200s simulation.
#include "fixtures/app_transaction_fixture.h"
#include <type_traits>
namespace {
using app_test::Rig;
using app_test::Port;
void terminal(app::Transaction& owner, Port& port, app::Fault fault) {
    CHECK(owner.report().phase == app::Phase::FAULT); CHECK(owner.report().fault == fault);
    CHECK_FALSE(owner.previous().applied_valid); CHECK_FALSE(owner.previous().duration_valid);
    CHECK_FALSE(owner.report().applied.feedback.applied_valid);
    CHECK_FALSE(owner.report().applied.feedback.duration_valid);
    port.clear(); CHECK_FALSE(owner.initialize()); CHECK_FALSE(owner.open());
    CHECK_FALSE(owner.decide(app_test::input())); CHECK_FALSE(owner.finish()); owner.abort();
    CHECK(owner.report().fault == fault); CHECK(port.count == 0U);
}
}
TEST_CASE("B0 D095 owner construction inspection and destruction perform no I O") {
    Port port;
    { app::Transaction owner(port.port()); CHECK(port.count == 0U);
      CHECK(owner.report().phase == app::Phase::NOT_INITIALIZED);
      CHECK(owner.report().fault == app::Fault::NONE);
      CHECK(owner.recording().phase() == recorder::AttemptPhase::EMPTY);
      CHECK_FALSE(owner.previous().applied_valid); CHECK(port.count == 0U); }
    CHECK(port.count == 0U);
    static_assert(!std::is_copy_constructible<app::Transaction>::value, "one fixed owner");
}
TEST_CASE("B0 B3 D095 initialize performs Gate setup first and only once") {
    Port port; app::Transaction owner(port.port()); APP_REQUIRE(owner.initialize());
    APP_REQUIRE(port.count != 0U); CHECK(port.calls[0].kind == app_test::Kind::CONFIG_ENABLE);
    CHECK(port.calls[1].kind == app_test::Kind::ENABLE); CHECK_FALSE(port.calls[1].high);
    CHECK(owner.report().phase == app::Phase::IDLE); port.clear();
    APP_REQUIRE(owner.initialize()); CHECK(port.count == 0U); app_test::zero(port);
}
TEST_CASE("B0 D095 setup failure is terminal without an additional halt pass") {
    Port expected; expected.fail_at = 1; motors::MotorGate gate(expected.port());
    CHECK_FALSE(gate.begin()); const auto count = expected.count;
    Port port; port.fail_at = 1; app::Transaction owner(port.port());
    CHECK_FALSE(owner.initialize()); CHECK(port.count == count);
    CHECK(owner.report().fault == app::Fault::SETUP); CHECK_FALSE(owner.report().halt.attempted);
    terminal(owner, port, app::Fault::SETUP);
}
TEST_CASE("B0 D095 every wrong phase terminates without creating a decision") {
    for (unsigned scenario = 0U; scenario < 8U; ++scenario) {
        CAPTURE(scenario); Port port; app::Transaction owner(port.port());
        if (scenario >= 3U) APP_REQUIRE(owner.initialize());
        if (scenario >= 5U) { port.now = 10U; APP_REQUIRE(owner.open()); }
        if (scenario >= 7U) APP_REQUIRE(owner.decide(app_test::input()));
        port.clear(20U);
        if (scenario == 0U || scenario == 5U || scenario == 7U) CHECK_FALSE(owner.open());
        if (scenario == 1U || scenario == 3U) CHECK_FALSE(owner.decide(app_test::input()));
        if (scenario == 2U || scenario == 4U || scenario == 6U) CHECK_FALSE(owner.finish());
        CHECK(owner.report().halt.attempted == (scenario >= 3U));
        CHECK(port.settles == (scenario >= 3U ? 1U : 0U));
        terminal(owner, port, app::Fault::ORDER);
    }
}
TEST_CASE("B14 D092 D095 owns true start decision receipt and completion") {
    Rig rig;
    rig.source.t_us = 4000000000U; rig.source.timing = {false, false, 777U};
    rig.source.previous = {true, 999U, 900U, true, 1.0F, 1.0F, true, 999U, 99U};
    rig.port.clear(100U); APP_REQUIRE(rig.owner.open()); rig.port.now = 700U;
    rig.port.work_us = 2U; rig.port.settle_us = 31U;
    APP_REQUIRE(rig.owner.decide(rig.source));
    const auto report = rig.owner.report();
    CHECK(report.started_us == 100U); CHECK(report.decision_us == 700U);
    CHECK(report.applied.feedback.applied_us == 743U);
    CHECK(report.robot.contract_faults == 0U); CHECK(report.robot.token == 1U);
    CHECK(report.decision_made); CHECK_FALSE(report.finished);
    CHECK_FALSE(report.timing_valid); CHECK(rig.port.settles == 1U);
    rig.port.now = 1101U; APP_REQUIRE(rig.owner.finish());
    CHECK(rig.owner.report().execution_us == 1001U); CHECK(rig.owner.report().timing_valid);
    CHECK(rig.owner.previous().execution_us == 1001U);
    CHECK(rig.owner.previous().completed_us == 1101U);
    CHECK(rig.owner.previous().token == 1U); CHECK(rig.owner.previous().applied_us == 743U);
    rig.port.work_us = rig.port.settle_us = 0U;
    const auto next = rig.cycle(1200U, 1300U, 1350U);
    CHECK(next.robot.contract_faults == 0U); CHECK(next.robot.token == 2U);
    CHECK(next.fault == app::Fault::NONE); CHECK_FALSE(next.robot.timing_incomplete);
}
TEST_CASE("B14 D095 complete timing accepts equality natural wrap and wide ordered duration") {
    const std::uint32_t starts[] = {42U, 0xffffff00U, 1U};
    const std::uint32_t decisions[] = {42U, 0xffffff20U, 2U};
    const std::uint32_t completions[] = {42U, 0x20U, 0x80000000U};
    for (unsigned i = 0; i < 3U; ++i) {
        Rig rig; const auto r = rig.cycle(starts[i], decisions[i], completions[i]);
        CHECK(r.timing_valid); CHECK(r.execution_us == completions[i] - starts[i]);
        CHECK(r.finished); CHECK(r.phase == app::Phase::IDLE);
    }
}
TEST_CASE("B14 D095 invalid decision clock halts before Robot or Gate apply") {
    const std::uint32_t deltas[] = {0xffffffffU, 0x80000000U, 0x80000001U};
    for (auto delta : deltas) {
        Rig rig; rig.port.now = 100U; APP_REQUIRE(rig.owner.open());
        rig.port.clear(100U + delta); CHECK_FALSE(rig.owner.decide(rig.source));
        CHECK_FALSE(rig.owner.report().decision_made); CHECK(rig.owner.report().robot.token == 0U);
        CHECK(rig.port.settles == 1U); terminal(rig.owner, rig.port, app::Fault::CLOCK);
    }
}
TEST_CASE("B14 D095 duplicate decision clock cannot reapply cached motor output") {
    Rig rig; rig.tick(10U); APP_REQUIRE(rig.owner.open()); rig.port.clear(10U);
    CHECK_FALSE(rig.owner.decide(rig.source)); CHECK(rig.port.settles == 1U);
    CHECK(rig.owner.previous().token == 1U); terminal(rig.owner, rig.port, app::Fault::CLOCK);
}
TEST_CASE("B14 D095 next acquisition cannot precede previous completion") {
    for (auto next : {99U, 0x80000064U, 0x80000065U}) {
        Rig rig; rig.cycle(0U, 20U, 100U); rig.port.now = next;
        CHECK_FALSE(rig.owner.open()); terminal(rig.owner, rig.port, app::Fault::CLOCK);
    }
    Rig rig; rig.cycle(0U, 20U, 100U); rig.port.now = 100U;
    APP_REQUIRE(rig.owner.open()); rig.port.now = 101U;
    APP_REQUIRE(rig.owner.decide(rig.source)); APP_REQUIRE(rig.owner.finish());
}
TEST_CASE("B14 D095 finish rejects reversed and aggregate half range clock") {
    for (unsigned scenario = 0; scenario < 3U; ++scenario) {
        Rig rig; rig.port.now = 100U; APP_REQUIRE(rig.owner.open());
        rig.port.now = 101U; APP_REQUIRE(rig.owner.decide(rig.source));
        rig.port.now = scenario == 0 ? 100U : 100U + 0x80000000U + (scenario - 1U);
        CHECK_FALSE(rig.owner.finish()); CHECK_FALSE(rig.owner.report().finished);
        CHECK_FALSE(rig.owner.report().timing_valid);
        const auto fault = app::Fault::CLOCK;
        CHECK(rig.owner.report().fault == fault); terminal(rig.owner, rig.port, fault);
    }
}
TEST_CASE("B14 D095 application time must lie after decision and before completion") {
    for (auto application : {109U, 121U, 0x80000064U}) {
        Rig rig; rig.port.clear(); rig.port.scripted = 6U;
        rig.port.clock_script = {100U, 110U, application, 120U, 121U, 122U};
        APP_REQUIRE(rig.owner.open()); APP_REQUIRE(rig.owner.decide(rig.source));
        CHECK_FALSE(rig.owner.finish()); CHECK(rig.owner.report().applied.feedback.applied_us == application);
        CHECK_FALSE(rig.owner.report().timing_valid);
        terminal(rig.owner, rig.port, app::Fault::RECEIPT);
    }
}
TEST_CASE("B3 D095 ordinary Gate IO failure remains real feedback not app ownership fault") {
    Rig rig; rig.port.now = 100U; APP_REQUIRE(rig.owner.open()); rig.port.clear(120U);
    rig.port.fail_at = 6U; rig.port.settle_us = 40U;
    APP_REQUIRE(rig.owner.decide(rig.source)); CHECK(rig.port.settles == 2U);
    CHECK(rig.owner.report().applied.fault == motors::Fault::IO);
    CHECK_FALSE(rig.owner.report().applied.feedback.applied_valid);
    rig.port.now = 250U; APP_REQUIRE(rig.owner.finish());
    CHECK(rig.owner.previous().execution_us == 150U); CHECK(rig.owner.previous().duration_valid);
    CHECK_FALSE(rig.owner.previous().applied_valid); CHECK(rig.owner.report().fault == app::Fault::NONE);
    rig.port.clear(); const auto later = rig.cycle(1000U, 1010U, 1100U);
    CHECK(later.robot.outputs.ui_state == core::State::STOPPED);
    CHECK(later.robot.contract_faults != 0U); CHECK(later.fault == app::Fault::NONE);
}
TEST_CASE("B3 D095 abort invalidates receipt without rewriting its actual duty or token") {
    Rig rig; const auto go = rig.go(); rig.tick(go + 1000U);
    const auto before = rig.owner.previous(); const auto token = before.token;
    rig.port.clear(go + 1010U); rig.owner.abort();
    CHECK(rig.owner.previous().token == token); CHECK(rig.owner.previous().applied_us == before.applied_us);
    CHECK(rig.owner.previous().duty_l == before.duty_l); CHECK(rig.owner.previous().duty_r == before.duty_r);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::INTERRUPTED);
    CHECK(rig.owner.recording().summary().interrupted); CHECK(rig.owner.recording().summary().timing_incomplete);
    CHECK(rig.port.settles == 1U); app_test::zero(rig.port);
    terminal(rig.owner, rig.port, app::Fault::ABORTED);
}
TEST_CASE("B15 D095 abort preserves acquired evidence in each active owner phase") {
    for (unsigned phase = 0; phase < 3U; ++phase) {
        Rig rig; const auto release = rig.release();
        if (phase > 0) { rig.port.now = release + 1000U; APP_REQUIRE(rig.owner.open()); }
        if (phase > 1) APP_REQUIRE(rig.owner.decide(rig.source));
        const auto frames = rig.owner.recording().frames().size();
        const auto events = rig.owner.recording().events().size();
        rig.owner.abort(); CHECK(rig.owner.recording().frames().size() == frames);
        CHECK(rig.owner.recording().events().size() == events);
        CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::INTERRUPTED);
        terminal(rig.owner, rig.port, app::Fault::ABORTED);
    }
}
TEST_CASE("B3 D095 actual port never energizes before the complete release hold") {
    for (auto base : {0U, 0xfff00000U}) {
        Rig rig; const auto release = rig.release(base); rig.port.clear();
        for (auto age : {1U, 4999999U, 5000000U, 5099999U}) {
            const auto report = rig.tick(release + age);
            CHECK(report.robot.outputs.ui_state == core::State::COUNTDOWN);
            CHECK_FALSE(report.applied.feedback.motors_enabled); app_test::zero(rig.port);
        }
        CHECK(rig.port.highs == 0U); CHECK(rig.port.nonzero == 0U);
        const auto go = rig.tick(release + 5100000U);
        CHECK(go.robot.lifecycle.gate.go); CHECK(go.applied.feedback.applied_valid);
        CHECK(go.applied.feedback.motors_enabled == (MOTORS_ALLOWED != 0));
        rig.source.stop_requested = true; const auto stop = rig.tick(release + 5101000U);
        CHECK(stop.robot.outputs.ui_state == core::State::STOPPED); app_test::zero(rig.port);
    }
}
TEST_CASE("B14 D095 799 800 1000 and 1001 durations retain logging only policy") {
    for (auto duration : {799U, 800U, 801U, 999U, 1000U, 1001U}) {
        Rig rig; const auto go = rig.go();
        rig.cycle(go + 1000U, go + 1010U, go + 1000U + duration);
        const auto next = rig.tick(go + 3000U);
        CHECK(next.fault == app::Fault::NONE); CHECK(next.robot.contract_faults == 0U);
        CHECK(next.robot.outputs.ui_state != core::State::STOPPED);
        CHECK(next.robot.ticks.max_us == duration);
        CHECK(next.robot.ticks.overruns == (duration > 1000U ? 1U : 0U));
        CHECK_FALSE(next.robot.timing_incomplete); CHECK_FALSE(next.halt.attempted);
    }
}
TEST_CASE("B14 D095 true acquisition source age survives caller time override") {
    for (auto age : {2000U, 2001U}) {
        Rig rig; rig.source.imu.explicit_values = true;
        rig.source.imu.heading_available = true; rig.source.imu.heading_updated = true;
        rig.source.imu.gyro = core::ImuPresence::VALID;
        rig.source.imu.accel = core::ImuPresence::VALID;
        rig.source.imu.checked_us = 100U; rig.source.imu.observation_us = 100U;
        rig.source.imu.sequence = 1U; rig.source.t_us = 100U;
        const auto report = rig.cycle(90U, 100U + age, 101U + age);
        CHECK(report.decision_us == 100U + age);
        CHECK((report.robot.contract_faults != 0U) == (age > 2000U));
        CHECK(report.fault == app::Fault::NONE);
    }
}
TEST_CASE("B15 D095 STOP needs a real later epoch for deferred final receipt and sealing") {
    Rig rig; const auto release = rig.release();
    for (std::uint32_t i = 1U; i <= 5100U; ++i) rig.tick(release + i * 1000U);
    const auto go = release + 5100000U; rig.source.stop_requested = true;
    const auto stop = rig.cycle(go + 1000U, go + 1010U, go + 1450U);
    CHECK(stop.robot.outputs.ui_state == core::State::STOPPED);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::DRAINING);
    const auto count = rig.owner.recording().summary().ticks.ticks;
    const auto stopped_token = stop.robot.token; rig.source.stop_requested = false;
    const auto tail = rig.cycle(go + 2000U, go + 2010U, go + 2110U);
    CHECK(tail.robot.frame_ready); CHECK(tail.robot.frame_token == stopped_token);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK(rig.owner.recording().summary().ticks.ticks == count + 1U);
    CHECK(rig.owner.recording().summary().ticks.max_us == 450U);
    CHECK_FALSE(rig.owner.recording().summary().final_frame_missing);
    CHECK_FALSE(rig.owner.recording().incomplete());
    const auto frames = rig.owner.recording().frames().size();
    rig.owner.abort(); CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK(rig.owner.recording().frames().size() == frames);
}
TEST_CASE("B15 D095 real 200 second simulated one kHz pipeline retains exact final evidence") {
    Rig rig; const auto release = rig.release();
    for (std::uint32_t index = 1U; index <= 200000U; ++index) {
        const auto start = release + index * 1000U;
        rig.source.stop_requested = index == 200000U;
        rig.cycle(start, start + 20U, start + 130U);
    }
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::DRAINING);
    rig.source.stop_requested = false;
    const auto tail = rig.cycle(release + 200001000U, release + 200001020U, release + 200001130U);
    const auto& storage = rig.owner.recording();
    CHECK(tail.robot.contract_faults == 0U); CHECK(storage.phase() == recorder::AttemptPhase::SEALED);
    CHECK(storage.frames().size() == 5001U); CHECK(storage.summary().ticks.ticks == 194901U);
    CHECK(storage.summary().ticks.overruns == 0U); CHECK(storage.summary().ticks.max_us == 130U);
    CHECK_FALSE(storage.incomplete()); CHECK(storage.summary().missing_results == 0U);
    unsigned starts = 0U, goes = 0U, first_nonzero = 0U;
    for (std::size_t i = 0; i < storage.events().size(); ++i) {
        const auto* event = storage.events().at(i); APP_REQUIRE(event != nullptr);
        if (event->data[4] == static_cast<unsigned>(core::Event::START_RELEASE)) {
            ++starts; CHECK(app_test::u32(event->data) == release);
        }
        if (event->data[4] == static_cast<unsigned>(core::Event::GO)) {
            ++goes; CHECK(app_test::u32(event->data) == release + 5100020U);
        }
        if (event->data[4] == static_cast<unsigned>(core::Event::FIRST_NONZERO_DUTY)) ++first_nonzero;
    }
    CHECK(starts == 1U); CHECK(goes == 1U); CHECK(first_nonzero == (MOTORS_ALLOWED ? 1U : 0U));
}
