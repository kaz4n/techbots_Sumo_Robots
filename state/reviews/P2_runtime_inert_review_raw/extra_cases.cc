// Adds reviewer-only setup-clock and real halt-report checks to copied fixtures.
// Uses public actual Runtime evidence without private owner mutation.
// Appended only inside an isolated review copy; established tests stay unchanged.

TEST_CASE("B14 D104 reviewer every setup clock after baseline rejects regression") {
    Clock control;
    Runner baseline(control.port());
    CHECK(baseline.begin());
    CHECK(control.calls > 1U);
    for (std::uint64_t index = 2U; index <= control.calls; ++index) {
        Clock clock;
        clock.inject_call = index;
        clock.inject_delta = 0xfffffffeU;
        Runner runner(clock.port());
        CHECK_FALSE(runner.begin());
        CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
        CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::CLOCK));
        CHECK(runner.report().epochs == 0U);
        CHECK(runner.report().clock_calls == clock.calls);
        terminalPassive(runner, clock);
    }
}

TEST_CASE("B14 D104 reviewer failure reports latest actual Gate halt when present") {
    Clock control;
    Runner baseline(control.port());
    CHECK(baseline.begin());
    due(baseline, control);
    const auto before = control.calls;
    due(baseline, control);
    const auto observations = control.calls - before;
    std::uint32_t actual_halts = 0U;
    for (std::uint64_t index = 2U; index <= observations; ++index) {
        Clock clock;
        Runner runner(clock.port());
        CHECK(runner.begin());
        due(runner, clock);
        clock.now = runner.runtime().report().next_release_us;
        clock.inject_call = clock.calls + index;
        clock.inject_delta = 0xfffffffeU;
        poll(runner, clock);
        const auto& tx = runner.runtime().transaction().report();
        CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
        const auto latest = tx.halt.fresh ? tx.halt.fault : tx.applied.fault;
        CHECK(runner.report().gate_fault == static_cast<std::uint32_t>(latest));
        if (tx.halt.fresh) ++actual_halts;
        CHECK(runner.report().last_s_us == tx.started_us);
        CHECK(runner.report().last_d_us == tx.decision_us);
        CHECK(runner.report().last_c_us == tx.completed_us);
        terminalPassive(runner, clock);
    }
    CHECK(actual_halts > 0U);
}

TEST_CASE("B14 D104 reviewer actual closing observation at overall deadline cannot freeze success") {
    Clock clock;
    Runner runner(clock.port());
    CHECK(runner.begin());
    const auto before = clock.calls;
    due(runner, clock);
    const auto observations = clock.calls - before;
    for (std::uint32_t index = 1U; index < MIN_EPOCHS + 2U && running(runner); ++index) {
        const auto next = runner.runtime().report().next_release_us;
        if (static_cast<std::uint32_t>(next - runner.report().boot_us) >= WINDOW_US) break;
        due(runner, clock);
    }
    CHECK(running(runner));
    const auto next = runner.runtime().report().next_release_us;
    const auto ordinary_close = next + static_cast<std::uint32_t>(observations - 1U);
    clock.inject_call = clock.calls + observations;
    clock.inject_delta = runner.report().boot_us + WINDOW_US + GUARD_US - ordinary_close;
    due(runner, clock);
    const auto& tx = runner.runtime().transaction().report();
    CHECK(tx.finished);
    CHECK(tx.timing_valid);
    CHECK(static_cast<std::uint32_t>(tx.completed_us - runner.report().boot_us) < WINDOW_US + GUARD_US);
    CHECK(runner.runtime().report().phase == app::RuntimePhase::RUNNING);
    CHECK(runner.report().elapsed_us == WINDOW_US + GUARD_US);
    CHECK(runner.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::DEADLINE));
    terminalPassive(runner, clock);
}
