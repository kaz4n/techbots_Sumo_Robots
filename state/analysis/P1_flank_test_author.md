# P1 B12 O1/O3 independent flank opener test authorship

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016; no gate acceptance.
Objective: independently specify mirrored SIDESTEP/ARC phase behavior and the
D-033 phase-priority and D-034 current-perception exit contracts.

Owned files:
- tests/test_opener_flank.cpp: 35 new doctest cases.
- state/analysis/P1_flank_test_author.md: this report.

Sources read: current AGENTS.md and .claude/agents/test-author.md, PROGRESS.md,
PLAN.md section 3, BEHAVIOR.md B0/B2/B6/B7/B12 O1/O3 with D-033/D-034 amendments,
DECISIONS.md D-033/D-034, config.h and public openers.h/motion.h/governor.h
contracts committed as ad0efb0. No src/core/*.cpp implementation was opened.
No existing test, locked test, header, tunable or another author's file changed.
The local date remains Tuesday 22 September; D-016 allows these host tasks while
P0 hardware acceptance and every human phase gate remain pending.

Arbitration coverage: all 128 masks in each of PIVOT/TRAVERSE/TURN_IN for all
four modes. SIDESTEP's PIVOT outer abort and DRIVE/TURN_IN front priority are
distinct from ARC's rules. Inner triggers, simultaneous front/outer/inner
observations, ignored high bits, pivot-to-traverse front abort on the same tick,
old-phase outer priority and same-tick traversal-to-turn transitions are covered.
Tests interpret all exits as zero-duty intents, not a grant of ATTACK or motors.

Motion coverage: relative 50/80 degree pivots, mirrored 0.80 duty, strict five
degree tolerance, exact/adjacent/delayed 700 ms timeout and its one-call pulse,
timeout/completion ties, angle-times-two-ms missing-IMU fallback and no extension
of the original turn deadline after IMU loss. SIDESTEP captures the actual DRIVE
entry heading with D-022 correction, runs 250 ms, then captures a fixed relative
110 degree turn even without detection. ARC uses 0.70 outer duty and 0.45 inner
ratio, requires 200 signed continuous degrees or 1500 ms, and rejects opposite
sweep as completion. New phases begin at their invocation time after delays.

Target/fault coverage: ARC captures current selected bearing once and does not
retarget, can start a turn toward an outer target on ARC completion, and never
creates a target from a bearing alone. Missing/nonfinite/out-of-range required
bearings stop the command; the canonical positive 180 degree endpoint is valid.
TURN_IN completion uses current front/side/rear/none after loss or reacquisition.
Only SIDESTEP SEARCH has the mirrored inner-side scan hint. All active phases
reject healthy nonfinite yaw; unavailable yaw at entry reuses previously healthy
finite yaw. ARC IMU recovery preserves its original sweep anchor. Extreme finite
headings assert finite bounded duties rather than precision at float maximum.
All 256 mode values, reset/restart, terminal zero latches and micros wrap appear.

Governor composition: the real returned PIVOT/OPENER profile feeds the real
Governor at 9, 11.1 and 12.6 V. Both compensated side magnitudes meet their 0.80
or 0.85 final caps even when centered/contact are supplied. This does not prove
the future Robot's profile routing or hardware permission.

Property coverage: 10,000 xorshift32 seeded mirrored sequences, each constructed
from a selected family/phase and followed through additional observations.
Explicit counters require every logical mask, all six family/phase combinations,
and finite healthy / unavailable NaN / healthy-invalid NaN variants. Independent
PRNG replay counted 59-105 occurrences per mask, phase cells
[1628,1653,1678]/[1678,1692,1671], and validity counts [3304,3293,3403].
All behavioral comparisons include exit/phase/profile, phase/timeout pulses,
motion status/fallback, reflected duties, bounded finite outputs and scan hints.

Ambiguities: no new policy invented within the committed contract. The tests use
NaN unavailable samples to verify previous-yaw reuse; they do not impose an extra
meaning on a finite caller-supplied value explicitly marked imu_ok=false.

Validation at handoff: 35 cases counted; CHECK/CHECK_FALSE assertions only;
no shared compilation or test run by this author. Coordinator owns normal and
sanitizer results, separate review and the final evidence receipt.
Limits: no Robot/ScenarioRunner integration, edge arbitration, contact lifetime,
motor permission, physical travel, target build or MCU tick timing is proved.
Next action: coordinator runs unchanged cases and resolves findings against the
specification before recording final validation in state/.
