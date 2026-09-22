# P1 independent explicit head-on test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: protect the additive startHeadOn contract 8a6cc48 with new locked
tests only. Owned files are `tests/locked/test_edge_headon.cpp` and this report.
Sources: public edge/motion/governor headers, B4.2/B4.4/B7, D-020 through D-023,
D-044 and P1_headon_contract.md. AGENTS was read in this continuous session.
No implementation cpp, old locked test, config or shared build file was read for
implementation details or changed. No build or commit was run.

The 14 cases cover literal defaults; preservation of legacy start(mask3) as
UNSUPPORTED including high-bit variants; explicit-side mirrors; exact/adjacent
one-tick brake, 180 ms reverse and 160 degree pivot; per-entry heading capture;
strict five-degree tolerance with adjacent floats; 700 ms pivot timeout and
one-shot pulses; initial/mid-turn IMU loss and recovery; full 320 ms fallback;
original timeout despite late loss; delayed transitions; invalid capture/current
yaw; finite extreme headings; wrapped deadlines; and restart/reset into the
original 120 ms/120 degree front row without leaking head-on state.

Real Guard/Governor composition checks low-voltage reverse caps and pivot sign
reversal, immediate terminal braking, completion while white remaining in escape,
all-black completion, all-white latched inhibition and revoked permission.
The harness supplies permission; no row grants it.

Static handoff only: CHECK/CHECK_FALSE assertions; no test runner invoked.
Parent owns host/sanitizer verification and establishment of these new locked
tests. Established tests were not edited or reinterpreted. After establishment,
AGENTS locked-test protection applies to later changes.

Limits: selected last-opponent side is supplied explicitly; its history mapping
is not invented here. No full escape selection/replanning, real inward-heading
validation, MotorGate/EN behavior, hardware trajectory, scheduler timing or phase
gate is proved. Next action: parent reviews/runs the frozen suite and records
actual validation before committing it.
