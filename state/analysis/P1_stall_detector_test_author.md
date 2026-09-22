# P1 stall detector test author — 2026-09-22

Objective: independently test B11.1/D-032 timer-or-deflection inference against
the public `stall.h` contract committed as `29779da`. Read the replacement
AGENTS instructions, B11.1, D-032's recorded actual user approval, relevant config
and public types. No implementation `.cpp` was opened. Work remains host-only.

Only new files `tests/test_stall_detector.cpp` and this report were authored.
Existing locked tests, configuration, shared state and other authors' edits were
preserved. No board, HAL or motor operation was attempted.

## Coverage

The 15 cases cover inert defaults; exact one-second qualification and level
results; strict positive/negative 25-degree boundaries using adjacent float
values; continuous yaw across multiple revolutions; both duties at adjacent
0.80/1.00 limits, negative/zero and nonfinite values; ATTACK/center/contact
qualification and all invalid state enum values; timer restart without losing
contact history; edge retention through failed qualification; fresh and inferred
contact resets, including an edge at the same tick as fresh contact; missing IMU
at contact start versus a missing current sample; D-025 suppression that preserves
diagnostics and history; delayed calls, uint32 and cumulative wraps; and reset.

A fixed-seed (`0xB111D032`) property set runs 500 traces of 128 calls. The test
oracle keeps an absolute 64-bit qualification-start timestamp and separate
contact-edge history, with no heading trigger. Fresh contacts, duty/centering
failures, suppression, edge observations and legal gaps up to UINT32_MAX are
mixed. It does not infer expected history from detector outputs.

## Evidence and limits

Authoring is ready for the coordinator's host build and independent review.
No full build or suite execution was run by this author. No scoped contradiction
or ambiguity was found in the committed interface.

`rg -c 'TEST_CASE' tests/test_stall_detector.cpp` reports 15 cases, and
`git diff --check` returned exit 0 at author handoff.

These tests are for inference from caller-supplied final duties, contact flags,
edge observations and continuous yaw. They cannot prove that actual sensors,
contact fusion, governor/FSM ordering or motor outputs supply those values.
No physical stall, re-flank maneuver, speed, safety-gate integration, target
timing or phase gate is proved by this standalone detector.

Next action: coordinator executes the complete host suite; independent reviewer
checks the implementation and evidence without weakening test predicates.
