<!-- Records independently derived D129 oracle scope before execution. -->
<!-- Separates public contract tests from native and physical qualification. -->
<!-- Root freezes hashes, retains first-run receipts and adjudicates new drafts. -->
# D129 independent timing-evidence test plan

2026-09-24. Authored from the adopted D129 contract, D092 timing contract,
BEHAVIOR B3-B6/B9/B14-B15, P4 prompt, public headers and previously established
test fixtures. No production implementation bodies or new worker output were
read. No test/build/implementation execution was performed by this author.
The new safety file is an unaccepted draft until independent review and first
execution; none of the 39 established locked files was edited.

## Files and intended runs

- `tests/p4_timing_fixture.h`: genuine ordinary-menu START, explicit tick/source
  clocks, fixed trace capture, synthetic receipts clearly labeled, and separate
  actual Transaction/MotorGate paths. No private-state access or token seeding.
- `tests/test_timing_evidence.cc`: 21 public Robot/codec cases.
- `tests/locked/test_timing_evidence_safety.cc`: nine baseline safety cases and
  two additional `APP_TEST_CONFIGURED_BUTTONS` Runtime cases.
- `tests/tooling/test_reactive_timing.py`: 14 independent mocked policy methods.
- This plan records scope and limits; freeze hashes are returned separately.

Run the dedicated timing-evidence M0 and M1 host targets under normal and
sanitizer builds, then the configured-button overlay for both M values. This
gives 30 named baseline cases per target, 32 with the configured overlay.
Run all 14 tooling methods in WSL, including the real dangling-symlink fixture
prerequisite. Mocked transport must never contact a board. Run established host
and policy regressions without editing their expectations. Root owns execution,
raw receipts, configuration compile probes, native build and layout evidence.

## Contract coverage

| Area | Independent observations/assertions |
|---|---|
| Identity and grammar | Conditional timing profile; event10, detail0..12; both exact header variants; unknown/reserved metadata; literal eight-byte wire fixture; enum-only packing retained |
| Bounds and retention | Batch26 fixed prefix; separate invalid metadata/rejected overflow; first4096 event retention across wrap; 25Hz/200s constants unchanged; successful trace exactly five records |
| Admission | Genuine release and header adjacency; cancellation and next accepted START; actual full5100ms hold, including wrap; literal SEARCH at GO; preceding TRACK cannot qualify an early ATTACK loss |
| Acquisition origin | Logical active-low masking; exact first all-clear S/E; adjacent source pair, suffix ordering; zero source timestamp; natural wrap; no favorable later replacement |
| Loss behavior | SEARCH plus side/rear DEFEND exits; exact30ms debounce boundary; staggered front deassertion with intermediate TRACK; precise brake D and application A |
| Actual application | Real Transaction/Gate callback duration, token, zero pulses and EN; M0 no arming; deliberately coarse valid PWM period quantizes positive requests to zero and cannot qualify |
| Single candidate | Any raw front reassertion closes transient; no retry; prior approach cessation preserves original pair plus exclusion12; missing tail and reset never fabricate completion; duplicate timestamps neither replay nor consume |
| Source/time rejection | Invalid window, before-tick/reversed/future source, invalid tick start, half-range ambiguity, stale observations and actual Runtime partial snapshot; armed and observing continuity reject backdated start, missing/wrong duration and reversed completion |
| Exclusions | Every nonzero edge mask both before and after source pair; STOP/application fault/contact before first clear; invalid-source priority over simultaneous STOP/edge; genuine front stuck; side-only stuck exemption; real phantom creation followed by masking vs nonmasking |
| Receipt validation | Full high32-bit token mismatch, invalid application, EN off, nonzero/NaN duty, missing/wrong duration, early application, reversed completion, backdated/invalid current tick; immediate failure11 and no borrowed later zero |
| Receipt precedence | A valid prior zero completes before current edge, STOP or raw reassertion; late valid zero is retained without an artificial35ms cutoff |
| Actual owner | Transaction abort retains incomplete tail; duplicate-clock admission failure creates no Robot event and preserves prior token; configured Runtime projects exact one seven-channel acquisition, with no extra read; postfault D103 service-only reset cannot create a second header or rearm |
| Tooling | Exact four flags in C/C++ and expanded recipes; inert default compile only; no upload key; wrong project/flag/startup/upload/library/result rejection; profile files including dangling symlinks rejected before I/O; checked failure has no fallback; old app and uninstrumented reactive routes remain accepted |

## Oracle decisions settled before freeze

Legacy line/IMU input is intentionally exercised with `observations_fresh=true`
and explicit valid TickTiming/opponent-read interval. This is contract-valid;
explicit LineEvidence is not a hidden requirement. Missing explicit timing or
source interval remains motion-compatible and cannot qualify evidence.

Current exclusions occur before source-pair emission. Only an otherwise valid
first clear whose immediately prior approach receipt has ceased to qualify
emits the pair followed by EXCLUDED_NO_APPROACH. A receipt completion is observed
before current sampling, so its timing event need not be a current-event suffix.

During ARMED/OBSERVING, D092 receipt chronology is part of source qualification:
current acquisition cannot predate preceding completion, even when the current
opponent interval remains after the candidate anchor. These timing-only faults
close INVALID_SOURCE_TIME without changing motion. At pending brake receipt,
the same timing rejection is INVALID_RECEIPT. Pure application/identity faults
with valid timing close INTERRUPTED_STOP_FAULT while armed/observing.

Adjacent one-microsecond debounce checks use zero-width acquisition/application
intervals. Nonzero source windows occur with sufficient inter-tick spacing;
all intentionally malformed schedules are explicit rejection cases.

## Limits and next evidence

These tests prove public software behavior on supplied observations. Synthetic
positive receipts in M0 exercise Robot validation and are never physical proof.
Actual Gate tests use fake electrical callbacks and synthetic grants; their
acknowledgments do not measure pins, wheel motion, braking distance or WCET.

Public finite runs cannot naturally reach a pending token above2^32 or token
exhaustion. The high32-bit mismatch rejection is tested; storage of the full
expected token and the exhaustion receive-before-terminal path require separate
source review. No private-state injection is used to pretend those paths were
reached. Event bound derivation, default ABI non-growth, actual EventInput
padding, native loader span/free RAM and full-source timing require independent
review/build/measurement. Default-off codec rejection and established behavior
compatibility are owned by the unchanged regression suite and compile probes.

The offline timing analyzer is a later task. No CSV interval pass/fail verdict,
hardware-origin claim, physical P4.2 acceptance, human phase gate or motor-run
authorization follows from this draft. Freeze first, then preserve every
actual failure before deciding whether implementation or a new unaccepted
oracle needs correction.
