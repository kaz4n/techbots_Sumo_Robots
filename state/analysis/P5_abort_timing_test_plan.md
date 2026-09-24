# D135 independent public-oracle draft plan

2026-09-24. Derived from the adopted `P5_abort_evidence_contract.md` at
2aa0ac2e, BEHAVIOR B2/B3/B4/B5/B6/B7/B12/B13/B15, D033/D034/D055/D134,
and public headers. P5.3's physical ten-trial requirement remains separate.
The four paused draft files are preserved by Git at bf36abfb. These new oracles have
not been compiled, imported or executed. Production implementation bodies were
not read. D134's frozen sources, existing tests/locks, headers, CMake, tools and
shared ledgers were not edited by this author.

## Draft inventory and expectations

After root released the D134 host barrier at d6a8319e, the drafts were moved
to the new test paths below; include paths alone changed during that transfer.
No redundant draft source copies remain. The new safety file remains unaccepted
pending review/validation. There are42 TEST_CASEs with configured buttons,40
otherwise, plus18 Python methods. Counts describe authored cases, not passes.

| File | Cases | Independent expectations |
|---|---:|---|
| `tests/fixtures/p5_abort_fixture.h` | helper | Public Robot, actual MotorGate and Transaction; separate T/read/D/A/C; literal cue table; exact timing suffix/order; public menu/START admission only |
| `tests/test_abort_codec.cc` |5| Profile/capacity constants; all65,536 cue words; all256 details with boundary values; exact8-byte little-endian wire; all four appends at21-event capacity |
| `tests/test_abort_openers.cc` |9|128x128 Direct snapshot/current combinations; all128 masks per available Flank phase and WAIT phase; same-call phase advance; front/outer priority; natural and primitive timeout distinction; deadline ties/wrap; reset/disabled/inactive pulses |
| `tests/test_abort_robot.cc` |15| Header adjacency; GO-time Direct; phase/mask handover with D034 centering; held effective target after raw clearing; true late snapshot negative/control; WAIT zero/cue/full Flank; actual receipt delays0/999/1000/1001/50000us; clock wrap; invalid source metadata with unchanged requests; full64-bit receipt mismatch and invalid duty/EN/chronology; duplicates/reset/missing tail |
| `tests/locked/test_abort_timing_safety.cc` |6| Exact full hold for every available mode; all15 white masks before candidate; STOP/source priority; real PWM quantization/EN; old valid receipt before new edge/STOP/source fault;10,000 fixed-seed bounded R1/R5 streams |
| `tests/test_abort_runtime.cc` |3| Empty SetupGrants remain inert; configured actual Runtime read interval equals one callback's start/end, real Transaction receipt time and recorder bytes; DIRECT and zero-duty WAIT candidates; partial/failed/out-of-epoch source refusal and no retry |
| `tests/test_abort_recording.cc` |4| Public synthetic envelope composition: partial batch retention/loss,4096-event ring overflow while frames continue, malformed count/invalid cue propagation, visible APPLIED never erases loss, unfinished/reset prefix stays incomplete |
| `tests/tooling/test_opener_timing_policy.py` |18| Exact checked wrapper/project/flags, both result/preflight validators, expanded recipe/artifact binding, old app/P4 admission, zero-I/O upload/MATCH/Immediate/foreign-run refusal, local profiles, no new upload key, empty grants/no source overrides, default/binary/exclusive profile and wrapper syntax probes |

The opcode/detail/cue expectations are literal contract values, not calls to a
production cue encoder. Exhaustive cue validation and opener behavior share an
independent spec table, never an implementation predicate. Actual Robot records
check both the cue and resulting state, plus their same-D timestamps; receipt
results must appear before current-decision events. Upper-token-bit corruption
preserves the low32 bits and must fail. Gate assertions compare the acknowledged
downward-quantized PWM with the governed request, including M0 physical zero.

The snapshot tests establish a confirmed target at release+5.000/5.001s, inside
D024's final300ms window. Replacement begins at5.060s and GO is5.100s. This avoids
the independently adjudicated D134 stale-snapshot fixture error. The wrap case
first measures only the fixture's menu/START schedule, then translates the full
timeline so candidate D is exactly0; read times cross the numerical wrap.

The safety draft retains B4's moving rear/side rows. It does not infer universal
braking from EDGE_ESCAPE. Brake/fault rows retain zero checks; other rows retain
the0.80 cap and exact actual Gate quantization. Existing frozen D134 oracles
already cover literal settled vectors and the B6 slew/reversal sequence.

## Build and review boundary

Root may integrate explicit dedicated M0/M1 targets using the existing
`B4_HOST_SOURCES` source list and its doctest main. Add the six `.cc` files above
and include directories `src`, `tests` and `host/third_party`.
This reuses actual core, app Runtime /
Transaction, Gate, UI, ADC, QTR/IMU adapters, recorder/CSV/dump sources; no extra
native hardware implementation, stub replacement or test setter is required.

Compiler-wide profile: C++17, MATCH=0, SUMOX_P5_ABORT_TIMING=1,
MOTORS_ALLOWED=0 or1; B4_STAND, P3_DRIVE_TEST, P3_TURN_TRIAL, P3_STOP_TRIAL,
P4_REACTIVE and SUMOX_TIMING_EVIDENCE all0. Keep warnings-as-errors, no RTTI,
no exceptions, and DOCTEST_CONFIG_NO_EXCEPTIONS. These drafts intentionally
require the new adopted public AbortEvidence/AbortPhase/AbortCause members and
OPENER_TIMING_PROFILE declaration before they can compile.

Configured Runtime coverage requires `APP_TEST_CONFIGURED_BUTTONS` and an isolated
copied config with BUTTON_WINDOWS_CONFIGURED=1,
BUTTON_LOW_RAW={0,900,1900,2900}, BUTTON_HIGH_RAW={100,1100,2100,3100}.
This is the established synthetic fixture in `tests/tooling/test_app_runtime.py`,
not a physical button-window grant. Keep other shipped timing/governor values.
Run normal and sanitizer M0/M1; run all four D134 availability combinations in
copied configs to exercise disabled script pulses. Enabled choices use public
menu gestures, so no injected mode or fixed default selection is needed.

The18 Python methods prepare compiler-profile/wrapper syntax probes and exact
public policy admission checks; no compiler, import or method has run yet.
Root owns exact default/P4 ABI comparisons, unchanged protected regressions and
checked native compile/ELF/loader audit. Source-local checks use the established
sketch.yaml/yml refusal and the wrapper's absence of macro overrides. Root
explicitly confirmed that no broader new source-scan API is intended.
Old P4 assertions stay in their existing dedicated profiles; they are not
reinterpreted as P5 evidence. No new analyzer API or scoring framework is assumed.

## Honest coverage limits and remaining review responsibilities

- Public APIs cannot force an omitted/wrong routeNormal invocation, a different
  internal route token, corrupted Pending tag/attempt phase, unexpected private
  owner replacement, or Robot's UINT64 token exhaustion. Source review and
  bounded mutations in isolated copies must check these branches. In particular,
  omitted routing must yield HANDOVER_FAILED and lost ownership must never attach
  APPLIED to a later receipt. No public setter or private-layout hack is added.
- Final preemption after an already captured cue is specified, but ordinary
  public safety inputs preempt before opener evaluation. Its exact terminal
  prefix needs source review/isolated mutation unless a reviewer identifies a
  genuine public input path. The existing direct edge/STOP tests assert actual
  preemption and receipt-before-current-observation ordering without fabricating
  that intermediate private state.
- Contact cannot be injected independently of the ordinary opener/contact
  state rules. The tests exercise WAIT's real zero request and effective held
  perception, and impose no P4 raw-clear/contact/positive-wheel exclusion.
  Review must ensure no inappropriate D129 exclusion was copied into P5.
- Saturating an actual Robot's private event batch on the precise cue call has
  no public seam. The explicitly synthetic EventBatch/AttemptRecorder cases
  prove prefix/loss composition; actual Robot/Runtime cases independently prove
  representative producer suffixes and source/receipt ownership. Source review
  must verify that all specified appends are attempted and rejected records
  cannot reopen the candidate. Synthetic envelopes are not hardware provenance.
- Missing tail/reset/abort remain incomplete. A clean recording that is still
  RECORDING is unfinished; incomplete()==false alone is never a completed dump.
  Sparse Transaction timelines deliberately skip25Hz frames and assert visible
  skipped/incomplete status while separately requiring zero event loss. Dense
  actual Runtime cases check frame cadence and event integrity together.
- Native RAM/stack fit, physical clock accuracy, actual A1/QTR/IMU acceptance,
  motor authorization, live extraction and P5 physical10/10 trials remain open.
  M0 APPLIED records are diagnostics even when arithmetic is within1000us.

## Pre-freeze static corrections

The resumed drafts corrected an uncompiled `r.port` typo to `rig.port`, renamed
the codec boundary-value title so it does not claim all noncue values were
exhausted, anchored the wrap test at an actual numerical crossing, and replaced
the sparse-timeline globally-clean recording assumption with explicit D070
skipped-frame/incomplete checks. No execution failure or production repair
prompted these corrections. Original four-file draft provenance remains bf36abfb.

Next action: root/reviewer inspect and freeze exact hashes before any compilation
or implementation execution; accept the new safety candidates only through the
established new-lock process. No result or physical pass is claimed.

## First public execution adjudication and draft correction

Root's preserved `P5_abort_timing_raw/normal_first.json`, `.txt` and
`normal_first_LastTest.log` report successful compilation but failing tests:
M0 37/40 cases passed with10 failed assertions; M1 33/40 passed with32 failed
assertions. Original oracles/source/failure provenance is retained in
b0540500/2d924f1f. Independent author, reviewer and root agreed that the failures
come from three assumptions in these still-unaccepted draft tests, not a
production change requirement. Root authorized only the bounded corrections below.

1. Both variants'10 failures required Fault::NONE on normal inhibited STOPPED
   receipts. `P2_motor_gate_contract.md` lines45,76-80 explicitly preserves the
   STOPPED latch with valid disabled receipts; existing locked
   `test_motor_gate.cpp` lines582,892 assert that behavior. The helper now takes
   an explicit expected fault, default NONE; only test scenarios that explicitly
   require STOPPED pass STOPPED. Token/EN/PWM checks remain, and consumed/valid
   receipt checks are explicit. No unrelated fault is accepted.
2. Four M1 failures assumed zero for DIRECT diagonal masks6/9. The unchanged
   stimulus confirms FC while preceding actual M1 wheel duties are both positive.
   B4.3/D049 and public `edge.h` lines187-190 therefore select pushed-out before
   ordinary B4.2 diagonal rows. M0 does not satisfy the actual-duty predicate.
   The test now captures prior actual feedback and governed request separately,
   checks the expected positive-duty qualifier and centered mask, and requires
   exact PUSHED_OUT flag equivalence below the unchanged three/four-white fault
   priority. Ordinary brake/fault zeros remain. Qualified pushed-out rows require
   away-pivot signs, reversal braking, same-direction B6 slew, exact settled
   +/-0.80 at40ms and actual Gate PWM quantization. Original stimuli and loops
   remain; the40ms observation adds a specified settled check.
3. Eighteen M1 failures required APPLIED at global event ordinal0. Observed
   event2/detail3 is the valid FIRST_NONZERO_DUTY extension of the same preceding
   receipt. D135 lines252-254 and `P1_robot_contract.md` line86 require receipt
   events before current-decision events, not APPLIED before other legitimate
   preceding-receipt extensions. The replacement helper admits only one ordered
   FIRST_NONZERO_DUTY and/or FAULT9 prefix. It checks actual receipt identity,
   permission, A timestamp, sign/magnitude, exact duty bits/bytes; FAULT9 requires
   documented nonzero bits0..2 and C timestamp, or current D for timing-incomplete.
   Successful APPLIED cannot use that invalid-timing prefix. Any current-decision
   event before the trace result fails. Unique result, counts, timestamp, value,
   full-token and no-retry expectations remain. The same invalid global-ordinal
   assumption is corrected in the new Runtime and invalid-receipt cases.

Only the new helper, new Robot/Runtime test files, new unaccepted safety test and
this plan changed. All42 established protected files and production remain
untouched by this author. No compilation or execution followed the correction;
root owns review/refreeze and the next run. Test-case counts remain40 normal /
42 configured and18 Python methods. This disposition preserves the first failure
and does not convert host timing or synthetic callbacks into physical evidence.

## Deferred legacy size/alignment regression runner

`P5_abort_timing_raw/run_layouts.py` is prepared for root's later serial run;
this author has not imported, compiled or executed it. It resolves the exact
pre-D135 commit `d6a8319e`, archives only `src`, checks every archive member's
path/type before extraction into an owned `/dev/shm` TemporaryDirectory, and
copies the current frozen source there with exact hashes. The generated probe
includes public headers and prints size/alignment only; no production body is
compiled or linked. Its compile-time profile assertions prevent a mislabeled
default, reactive, timing or P5 observation.

The planned matrix has 14 sequential header-only compilations: baseline/current
for default M0/M1, reactive M0/M1, and reactive-plus-timing M0/M1, then current
P5 M0/M1. Every one of 12 types must match size and alignment in each of the
six legacy comparisons (72 type pairs). The types are Direct, Flank, Wait,
Result, FlankResult, WaitResult, RobotInput, RobotResult, Robot, Transaction,
Runtime and EventBatch. P5's two measurements are separate observations with
no baseline-equivalence requirement. Size/alignment equality does not establish
member offsets, calling conventions, target RAM/stack fit or WCET.

The runner refuses existing output labels; root can later use
`TMPDIR=/dev/shm python3 state/analysis/P5_abort_timing_raw/run_layouts.py layout_first`.
The JSON/text receipts retain exact argv and compiler version, resolved revision,
archive/probe/runner/binary/output hashes, parsed measurements and comparisons,
frozen-input checks before/after, full source inventories once plus compact
after hashes/equality, and scratch size/release status. Temporary sources and
executables are removed by the context manager even after a failed check.
No older report, test, header, implementation or build file changes for this
preparation. Root owns the execution barrier and any resulting validation claim.
