# P1 independent logical Menu test author

Date: 2026-09-23, Asia/Dubai. P1 host-only under D-016.

Objective: protect D-058/public contract 3563a8f, B13 and the D-057 single-sampled
START routing composition while preserving B3/R1. Owned new files are
`tests/test_mode_menu.cpp`, `tests/locked/test_menu_routing.cpp` and this report.
The coordinator later authorized the one explicit contract-inventory addition
to unlocked `tests/tooling/test_p0_config.py` described below. All expectations
derive from public headers, specifications, approved decisions and the saved
mode/menu audit; no implementation cpp was read. No build, hardware operation or
commit was performed by this author.

The component suite has 25 cases. It covers default/reset/copy-only selection,
20 ms NONE and exclusive-MODE qualification at exact/adjacent boundaries,
600 ms strict short duration, 1000 ms long duration, delayed qualification,
first-NONE frozen duration, long-deadline release priority, no release cycle
after a long toggle, interrupted release and unqualified-press recovery.
Boot-held MODE/START/BOTH and invalid buttons remain disarmed until fresh NONE.
All 256 state encodings and fault combinations exercise rejection/retention;
nondefault mode and service-item retention are checked separately.

All six match modes and four service items are reached through gestures, without
an injected selection. Cases preserve match mode through services, reset the
item to SENSOR_VIEW on entry, retain the inactive item on exit, and distinguish
each typed request from actual execution. DRIVE_TEST alone is marked unavailable.
Request eligibility checks each state against every logical button plus invalid
input. Fresh NONE arming after a typed request has 19999/20000/20001 us cases.
Duplicate timestamps ignore changed input/state/fault and clear transient outputs.
Reset covers every gesture stage, long holds span multiple uint32 wraps without
repeat, and 128 fixed-seed wrapped gestures compare against independent literal
cycle/toggle/no-op transitions with explicit coverage of all four gesture classes.

The locked suite has 11 cases and calls production Lifecycle exactly once per
observation, then Menu with entry state, its genuine ButtonEvents snapshot and
final STOP/fault inhibition. Each real service START remains IDLE without match
release, calibration attempt, diagnostics from invalid prior bias, GO or heading
reset. Requests are one-shot; duplicates and later time cannot create deferred
countdown. Service exit requires a new START for a full 5.1 s hold. MODE cancel
before, exactly at and after the countdown deadline cannot also become an IDLE
menu action. Logical BOTH STOP remains live in match/service/countdown/moving
contexts; external STOP or final fault suppresses a simultaneous service request.
Wrapped request timestamps and fresh NONE arming are exercised in the real
composition. Running-mode capture is explicitly test-owned caller wiring.

The coordinator reported one stale tooling inventory failure in the initial
116-test run: `state/analysis/P1_menu_tooling_20260923.txt` preserves that receipt.
Static inspection confirmed BEHAVIOR_EXTRA_DEFAULTS omitted newly centralized
B13/D-058 MODE_SHORT_MS. Under the coordinator's bounded authorization, this
author added only `'MODE_SHORT_MS': 600` and its source comment. Existing loops
still enforce exact uint32 type/value and the complete declared-name set. All
76 B16 defaults, other inventory entries and all assertions remain unchanged;
there is no broad unknown-name allowance or framework change. This contract
addition is distinct from weakening a failed behavior expectation.

Static handoff: 25 component plus 11 new locked cases; CHECK/CHECK_FALSE only,
no throwing checks, trailing whitespace or diff-check errors; test/helper blocks
remain below 60 lines. The two new suites and narrow unlocked inventory amendment
are frozen for coordinator normal/sanitizer/tooling builds and independent review.
Runtime validation remains pending; preserve independent predicates on failure.
Once established, new locked cases inherit AGENTS human-approval protection.

Limits: the composition is a harness using real Menu/Lifecycle components, not
the full Robot, a service consumer or MotorGate. It does not prove A1 electrical
decoding, physical sensor freshness, actual bias/heading application, EN/PWM
writes, installed service availability, DRIVE_TEST motion, loop timing or a phase
gate. No motor authorization is inferred. Next action: coordinator runs/reviews
the frozen files and records measured evidence before committing.
