# Locked expectation conflicts with approved D-035 — 2026-09-22

Status: proposed locked-test amendment; NOT applied, human approval required by
AGENTS.md R1. No assertion has been weakened, removed or skipped. Implementation
already honors accepted D-035; do not revert logical STOP merely to make this green.

Evidence: `wsl -d Ubuntu -- bash tools/test_host.sh`, exit8, receipt
P1_flank_stop_build_initial.txt.348 cases:347 pass,1 fails with6 assertions.
The exact case is tests/locked/test_countdown_integration.cpp:205,
"B3 Controller qualified MODE cancels at GO deadline and requires a new hold".
Its BOTH branch qualifies BOTH at the GO boundary (cancels countdown correctly),
then holds it for another5.1seconds but expects IDLE. It subsequently expects a
fresh START without reset. D-035 requires STOPPED and reset-only recovery.
The normal MODE branch's old behavior remains valid.

Concrete requested edit: replace ONLY that case with the following. Preserve all
existing initial cancellation/full-hold checks and the MODE branch. BOTH instead
asserts STOPPED, rejects release/START while stopped, then explicitly resets before
reusing the unchanged fresh full-hold checks. New tests/locked/test_stop_hold.cpp
separately covers12 STOP cases including10000 seeded episodes; it cannot resolve
this established contradictory expectation by itself.

```cpp
TEST_CASE("B3 Controller qualified MODE cancels at GO deadline and requires a new hold") {
    for (auto mode : {ButtonLevel::MODE, ButtonLevel::BOTH}) {
        ControllerRunner runner;
        const auto release = startHold(runner);
        runner.now_us = release + HOLD_US - DEBOUNCE_US;
        checkBlocked(runner.sample(mode), Phase::HOLDING);
        checkBlocked(runner.after(DEBOUNCE_US - 1U, mode), Phase::HOLDING);
        checkBlocked(runner.after(1U, mode), Phase::IDLE);
        CHECK(runner.go_pulses == 0U);
        if (mode == ButtonLevel::BOTH) {
            checkBlocked(runner.after(HOLD_US, mode), Phase::STOPPED);
            checkBlocked(runner.after(1000U), Phase::STOPPED);
            checkBlocked(runner.after(DEBOUNCE_US), Phase::STOPPED);
            checkBlocked(runner.after(HOLD_US, ButtonLevel::START), Phase::STOPPED);
            checkBlocked(runner.after(DEBOUNCE_US), Phase::STOPPED);
            CHECK_FALSE(runner.last.start_release);
            CHECK(runner.go_pulses == 0U);
            runner.controller.reset();
        } else {
            checkBlocked(runner.after(HOLD_US, mode), Phase::IDLE);
            runner.after(1000U);
            runner.after(DEBOUNCE_US);
        }
        startHold(runner);
        checkBlocked(runner.after(HOLD_US - 1U), Phase::HOLDING);
        CHECK(runner.after(1U).go);
    }
}
```

This is a human-controlled specification synchronization, not a repair attempt
that changes production safety behavior. No other established locked case is in
scope. Upon explicit approval, record a new ADR, apply exactly this edit, run the
complete suite and sanitizers, and have the separate reviewer inspect the diff.

2026-09-22 update: user explicitly replied "Approve the single-case locked-test
amendment". D-039 records approval. The exact replacement above is now applied;
no other established locked case changed. Validation and review follow, with the
initial failure receipt retained as history.
