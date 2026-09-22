# P1 countdown and edge integration test author — 2026-09-22

Objective: independently encode D-019 and D-020 in new locked host tests.
Authority: the P1 host-only exception D-016; no board operation or gate closure.
Local date was checked as 2026-09-22, the first day in PLAN section 3.

## Authorship and modified files

Read AGENTS.md, `.claude/agents/test-author.md`, the P1 prompt, the active state
checkpoint, D-017 through D-020, BEHAVIOR B0/B2/B3/B4/B6, and public headers.
No `src/core/*.cpp` implementation was opened. Existing locked tests and the
existing countdown test helper were read for doctest conventions, not changed.

Only these new files are owned by this author:

- `tests/locked/test_countdown_integration.cpp`: 10 cases.
- `tests/locked/test_edge_guard.cpp`: 10 cases.
- `state/analysis/P1_integration_test_author.md`: this evidence report.

## Coverage

Controller cases exercise actual logical button levels through Buttons and Gate:
exact press/release qualification, adjacent microsecond and millisecond boundaries,
the full hold after qualification, rejection at raw-edge-plus-hold time, interrupted
press/release bounce, boot-held START, reset from partial press/holding/ready/STOP,
qualified MODE and BOTH cancellation at the GO deadline, external STOP priority
and retention, missed qualifying ticks without backdating, micros wraparound,
duplicate START cycles, and single release/GO pulses. A fixed seed `0xD0195100`
generates 10,000 complete START bounce/boot-held streams, including delayed release
qualification and wraparound, with an independent unwrapped expected deadline.

Guard cases exercise all 16 masks before and after permission, all-white retention
through black samples and permission closure, explicit reset, clear/finished
ordering, simultaneous clear-and-finished exit, persistent white after completion,
re-entry, and low-four-bit masking. They explicitly require the default zero
push-through configuration.

A test-owned 1 kHz ScenarioRunner composes Controller -> Guard -> Governor and
records each latest module result, final duty, and release/GO pulse counts. It
runs every line mask across the countdown and exact GO tick. All-white at GO
produces an inhibited governor request and zero final duties; an all-white fault
also removes previously nonzero duty immediately and stays inhibited on black.
A STOP-plus-white scenario verifies that permission closure takes priority.

## Evidence and limitations

- `wsl -d Ubuntu -- g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -DDOCTEST_CONFIG_NO_EXCEPTIONS -I src -isystem host/third_party -fsyntax-only tests/locked/test_countdown_integration.cpp tests/locked/test_edge_guard.cpp`: exit 0.
- `rg -c 'TEST_CASE'` on the two new files: 10 cases each, 20 total.
- `git diff --check`: exit 0 after authorship.
- Full host execution: delegated to the independent reviewer; pending at handoff.

No ambiguous scoped predicate or contradiction was found. No existing locked
test, implementation, configuration, or shared ledger was modified by this author.
There is no full Robot FSM, ADC acquisition, escape script/direction, positive
push-through-window, motor-enable pin, PWM write, target compile, motor run, or
physical timing proof in these tests. The test harness is explicit logical wiring;
its zero-duty result is not evidence that the future app/HAL uses that wiring.

Next action: independent reviewer inspects the new tests and runs the complete
host suite once against the concurrently implemented Controller and Guard.

Coordinator execution update: the fresh reviewer subsequently ran the suite:
97/97 cases, 5,214,158 assertions, CTest 1/1, exit 0. Separate ASan/UBSan execution
also passed. See P1_integration_validation.md and reviews/P1_integration_codex.md.
The author's pending status above records the earlier handoff, not the final result.
