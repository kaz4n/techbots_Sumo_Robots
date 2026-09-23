// Tests D096 decision-time projection against the frozen transaction contract.
// Makes actual D and callback admission observable without inspecting production.
// Existing D095 legacy tests remain unchanged and run beside these cases.
#include "fixtures/app_transaction_fixture.h"

namespace {
struct Projection {
    app_test::Port* port = nullptr;
    fsm::RobotInput input = app_test::input();
    unsigned calls = 0U, clocks_at_call = 0U, writes_at_call = 0U;
    std::uint32_t seen = 0U;
    static fsm::RobotInput project(void* context, std::uint32_t actual) {
        auto& p = *static_cast<Projection*>(context); ++p.calls; p.seen = actual;
        p.clocks_at_call = p.port->clocks; p.writes_at_call = p.port->operations;
        return p.input;
    }
    app::DecisionSource source() { return {this, project}; }
};
}

TEST_CASE("B0 B14 D096 projection is once at actual D before application and overrides caller receipts") {
    app_test::Rig rig; Projection p; p.port = &rig.port;
    p.input.t_us = 999999U; p.input.timing = {true, false, 0xFFFFFFFFU};
    p.input.previous = {true, 999U, 0x80000000U, true, 1.0F, 1.0F, true, 0U, 9U};
    rig.port.now = 100U; CHECK(rig.owner.open());
    rig.port.now = 137U; const auto writes = rig.port.operations;
    CHECK(rig.owner.decideFrom(p.source())); CHECK(p.calls == 1U); CHECK(p.seen == 137U);
    CHECK(p.writes_at_call == writes); CHECK(p.clocks_at_call >= 2U);
    CHECK(rig.owner.report().started_us == 100U); CHECK(rig.owner.report().decision_us == 137U);
    CHECK(rig.owner.report().robot.contract_faults == 0U);
    CHECK(rig.owner.report().applied.feedback.applied_us >= 137U);
    rig.port.now = 190U; CHECK(rig.owner.finish());
    CHECK(rig.owner.report().execution_us == 90U); CHECK(p.calls == 1U);
}

TEST_CASE("B0 D096 projection refuses prebegin missing callback duplicate phase and backward clocks") {
    for (unsigned mode = 0U; mode < 5U; ++mode) {
        app_test::Port port; app::Transaction transaction(port.port());
        Projection p; p.port = &port;
        if (mode != 0U) { CHECK(transaction.initialize()); port.now = 100U; CHECK(transaction.open()); }
        if (mode == 2U) { port.now = 200U; CHECK(transaction.decide(app_test::input())); }
        if (mode == 3U) port.now = 99U;
        if (mode == 4U) port.now = 100U + 0x80000000U;
        auto source = p.source(); if (mode == 1U) source.project = nullptr;
        CHECK_FALSE(transaction.decideFrom(source)); CHECK(p.calls == 0U);
        CHECK(transaction.report().phase == app::Phase::FAULT);
        CHECK(transaction.report().fault == (mode >= 3U ? app::Fault::CLOCK : app::Fault::ORDER));
        app_test::zero(port);
    }
}

TEST_CASE("B0 D096 duplicate actual D is rejected before pure callback") {
    app_test::Rig rig; Projection p; p.port = &rig.port;
    rig.cycle(100U, 110U, 110U); rig.port.now = 110U; CHECK(rig.owner.open());
    CHECK_FALSE(rig.owner.decideFrom(p.source())); CHECK(p.calls == 0U);
    CHECK(rig.owner.report().fault == app::Fault::CLOCK); app_test::zero(rig.port);
}

TEST_CASE("B0 B14 D096 projection accepts natural wrap and receives true decision not source age") {
    app_test::Rig rig; Projection p; p.port = &rig.port;
    rig.port.now = 0xFFFFFFF0U; CHECK(rig.owner.open());
    rig.port.now = 12U; CHECK(rig.owner.decideFrom(p.source()));
    CHECK(p.seen == 12U); rig.port.now = 34U; CHECK(rig.owner.finish());
    CHECK(rig.owner.report().execution_us == 50U);
}

TEST_CASE("B0 D096 byvalue and projected decisions preserve identical actual Robot results") {
    app_test::Rig legacy; app_test::Rig projected; Projection p; p.port = &projected.port;
    for (std::uint32_t i = 1U; i <= 20U; ++i) {
        const auto& old = legacy.cycle(i * 1000U, i * 1000U + 20U, i * 1000U + 50U);
        projected.port.now = i * 1000U; CHECK(projected.owner.open());
        projected.port.now += 20U; CHECK(projected.owner.decideFrom(p.source()));
        projected.port.now += 30U; CHECK(projected.owner.finish());
        const auto& now = projected.owner.report();
        CHECK(now.robot.token == old.robot.token); CHECK(now.robot.contract_faults == old.robot.contract_faults);
        CHECK(now.robot.outputs.ui_state == old.robot.outputs.ui_state);
        CHECK(now.execution_us == old.execution_us); CHECK(now.recorded == old.recorded);
    }
    CHECK(p.calls == 20U);
}

TEST_CASE("B0 D096 additive projection keeps legacy empty byvalue calls unambiguous") {
    app_test::Rig rig; rig.port.now = 1U; CHECK(rig.owner.open());
    CHECK(rig.owner.decide({})); CHECK(rig.owner.finish());
}

TEST_CASE("B14 D096 projection source clock rejection halts without consuming a Robot token") {
    app_test::Rig rig; Projection p; p.port = &rig.port;
    auto source = p.source(); source.clockAccepted = [](void*) { return false; };
    rig.port.now = 100U; CHECK(rig.owner.open()); rig.port.now = 150U;
    CHECK_FALSE(rig.owner.decideFrom(source)); CHECK(p.calls == 1U); CHECK(p.seen == 150U);
    CHECK(rig.owner.report().fault == app::Fault::CLOCK);
    CHECK_FALSE(rig.owner.report().decision_made); CHECK(rig.owner.report().robot.token == 0U);
    CHECK_FALSE(rig.owner.report().applied.consumed); app_test::zero(rig.port);
}

TEST_CASE("B14 D096 finishAfter rejects C behind genuine postwork or postwork behind Gate A") {
    for (unsigned mode = 0U; mode < 3U; ++mode) {
        app_test::Rig rig; rig.port.now = 100U; CHECK(rig.owner.open());
        rig.port.now = 200U; CHECK(rig.owner.decide(app_test::input()));
        rig.port.now = mode == 0U ? 299U : 400U;
        const auto last = mode == 0U ? 300U : (mode == 1U ? 199U : 200U + 0x80000000U);
        CHECK_FALSE(rig.owner.finishAfter(last)); CHECK(rig.owner.report().fault == app::Fault::CLOCK);
        CHECK_FALSE(rig.owner.report().finished); CHECK_FALSE(rig.owner.report().timing_valid);
        app_test::zero(rig.port);
    }
}

TEST_CASE("B14 D096 finishAfter accepts equality and genuine wrapped postwork") {
    for (auto base : {100U, 0xFFFFFF00U}) {
        app_test::Rig rig; rig.port.now = base; CHECK(rig.owner.open());
        rig.port.now = base + 20U; CHECK(rig.owner.decide(app_test::input()));
        rig.port.now = base + 400U; CHECK(rig.owner.finishAfter(base + 400U));
        CHECK(rig.owner.report().execution_us == 400U); CHECK(rig.owner.report().timing_valid);
    }
}
