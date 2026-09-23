# D109 finite QTR raw capture bench

Adopted2026-09-24 under D051/D075 after scoped preflight. This does not activate hardware or
supersede D085/D089. Scope is the missing P2 B2 named `bench/qtr_raw`; source
basis is `P2_qtr_raw_design.md`, `P2_qtr_native_contract.md`, `line_qtr.h` and
`line_qtr_adapter.h`. Stable bounded RAM capture is sufficient for this software
increment. Physical surface provenance and a later readout tool remain separate.

## Ownership and public surface

Own one existing `line_qtr::Reader`, with direct bench-local callbacks. No Robot,
Runtime, MotorGate, calibration owner, UART, Bridge, matrix, IRQ owner, transport
protocol or other peripheral owner. Native construction, destruction and port
creation perform no I/O. Sketch asserts MATCH=0/MOTORS_ALLOWED=0 and begins with
`Grants{}`. No upload-policy change or pad grant is adopted here.

Public headers are `bench/qtr_raw/src/qtr_raw.h` and `qtr_raw_native.h`.
The coordinator adds `config::QTR_BENCH_FRAMES` as a uint32 count, default128,
after adoption. No existing acquisition limits, thresholds, pins or clock rules
change. Store exactly that many Snapshot slots for a positive capacity; no heap,
ring, overwrite, compression or discarded valid record. A zero-capacity build
may reserve one inaccessible dummy slot solely to avoid a zero-length C++ array;
reported capacity remains0 and enabled begin fails CONFIG before callbacks.
Target compilation/loader fit must establish that the selected capacity fits.

`captureCapacity()` always returns the configured capacity. `captureCount()`
equals `Report.captured_frames`. `capture(i)` returns a const pointer exactly
when i<count, otherwise nullptr. A published slot never changes until destruction,
including on stop/fault. Accessors perform no callback or state change. Native
Reader and Runner are noncopyable; caller owns their lifetimes. Private storage
and helpers may be added during implementation; this declaration-only draft does
not establish the final Runner size.

## Begin, passivity and command progression

Constructor copies Port without callbacks. Begin is one attempt. Repeat begin
returns false and changes nothing. False exclusive_pads takes precedence over
all other validation: DISABLED/true, no callback including clock. Enabled begin
requires all six nonnull callbacks before I/O, then positive capacity. Missing
callback is PORT, zero capacity CONFIG. Native begin receives true exactly once;
then report() is called exactly once. Begin succeeds only after accepted closing
C with statusOK, IDLE/OK and raw qualification ABSENT; its checked_us must lie
in S..A. No capture occurs in begin.

Every poll first clears fresh. Non-RUNNING polls return false with no callbacks
or other report changes. RUNNING polls are serviced each ordinary loop pass,
not on a1kHz grid: charge must be released after10+1us and before100us. One poll
does at most one start or one advance, plus one exceptional cancellation if
required below. There is no delay, busy wait, catch-up, retry or completion loop.

| Prior accepted Reader state | Callback(s) and accepted nonfault result |
|---|---|
| IDLE or COMPLETE | start(), then exactly one report(). OK requires CHARGING/OK/raw ABSENT and a new identity. NOT_DUE requires the entire prior snapshot unchanged member-for-member, with no start or capture publication. NOT_DUE is permitted only after an earlier accepted start. |
| CHARGING | advance() once; raw-ABSENT CHARGING or DISCHARGING, or raw-VALID COMPLETE. |
| DISCHARGING | advance() once; raw-ABSENT DISCHARGING or raw-VALID COMPLETE. |

Other nonfault command/phase combinations, including BUSY, ALREADY_STARTED,
NOT_INITIALIZED or FAULT_LATCHED in these admitted calls, are CONTRACT failures.
Native failure reports are handled below. Setup/start command statuses are
retained separately; they never replace the provider snapshot status. report()
is passive and is not called after advance()/cancel(), which already return it.

## Raw validation, identity and capture

Store each actual returned snapshot unchanged in Report.snapshot and publish its
`validateRaw` result. ABSENT means pending, not an optical failure. VALID means
structurally complete raw evidence, not a classified color. Retain every interval,
source timestamp, status, mask and cleanup field. No scalar discharge substitute,
threshold comparison, bank change, fake black or exact1500us timeout is introduced.

The bench's single new Reader guarantees first accepted start sequence1 and
each later accepted start exactly previous+1 modulo uint32. This is intentionally
stricter than Robot's general consumer admission, which permits missing frames.
An accepted start must have advances0; started/drive-completed/checked lie in its
outer S..A bracket, with drive-completed forward from start. The new start must
be >=QTR_START_PERIOD_US after the preceding start and no earlier than its
completion. Use admitted chronology, not signed casts or isolated wrap aliases.

During a frame, sequence, started_us and drive_completed_us remain identical;
each advance result increments advances exactly once. Its checked_us lies in
that advance's S..A bracket. COMPLETE additionally has completed_us in S..A;
the shared validator owns all per-pad/cleanup structure and short-frame bounds.
Provider FAULT is diagnostic, so these successful-source checks do not qualify
its failed timing. A changed/replayed/skipped identity or inconsistent source
bracket is SOURCE_ORDER; malformed raw shape or command/phase is CONTRACT.

Only a valid COMPLETE reached through an admitted advance can append one frame.
Copy it into the next unpublished slot before closing C. Do not increment count,
set fresh, or expose that slot unless C is accepted. A failed C leaves the slot
inaccessible and preserves the preceding published count. After accepted C,
increment count once and set fresh=true; poll returns true. At capacity, switch
to COMPLETE before returning, without starting/cancelling another frame. The
final poll still returns true/fresh. Other RUNNING polls return false. The next
poll clears fresh but leaves terminal evidence/capture unchanged. No capture
overflow is possible because terminal COMPLETE forbids all subsequent I/O.

## Clock closure and timing scope

Normal enabled begin and each RUNNING poll use three actual observations:
S immediately before its native command, A immediately after command+report (or
the returned advance snapshot), and C after validation, tentative copy and ordinary
counter work. Only duration/count/fresh/terminal publication and return follow C.
There is no invented timestamp. Setup timing is S..C; start/advance timing is
S..A including report retrieval; poll timing is S..C. These are named source
scopes, not full invocation WCET, because closing publication/return are excluded.

Every consecutive observed delta must be<2^31, equality of clocks is allowed,
and ordinary uint32 time wrap is valid. Accumulate accepted deltas over an active
begin/poll bracket and since the last accepted start, including inter-poll gaps;
reaching half-range is CLOCK. Before the first start there is no source-era age.
On a new accepted start initialize source-era age at A to A-started_us, then add
subsequent accepted deltas; do not reset it to zero at delivery. This prevents
old source history from reviving after many individually valid clock increments.
Require source comparisons to lie within that admitted era and the S..A bracket.

Read A immediately, then evaluate raw/provider and command/identity failures
before evaluating A chronology; evaluate source bracket checks only after A is
admitted. The first fault remains primary. Any bad observed clock also latches
Report.clock_fault, even when a provider/contract fault was already primary.
Accepted C records the duration of a nonclock failure path too. An invalid A or
C forbids successful closure/capture and further wrapper clock callbacks for
that operation. Fault cleanup still runs as specified below. A bad S prevents
the scheduled command; it must not prevent cleanup of an already active frame.

Timing.calls counts actual native callback invocations for setup/start/advance/
cancel; Timing.poll.calls counts RUNNING poll entries, including bad S. Timed
measurement is published only for an admitted bracket. last_valid is cleared
when that timing category is attempted; a valid measurement increments
measured_calls and updates last_us/maximum_us. Invalid timing retains numeric
history with last_valid=false. Other timing categories remain unchanged. All
counters saturate at UINT32_MAX; an attempted overflow sets counter_saturated.
The count of published frames is bounded by capacity and never saturates early.

## Fault and cancellation evidence

All faults are terminal and preserve published frames. Report.fault records the
first cause; later cleanup/clock evidence does not replace it. Report.snapshot
and qualification describe the command that was being processed. Cancellation
has separate Report.cancellation/cancel_qualification; never overwrite the
primary snapshot with cleanup output. No callback is reinitialized or retried.

Mark the provider possibly active before begin/start/advance invocation. Clear
that uncertainty only after a coherent accepted neutral IDLE/COMPLETE result,
unchanged NOT_DUE, or a raw-PROVIDER_FAULT snapshot. A known PROVIDER_FAULT has
already attempted its native cleanup: latch PROVIDER and issue no cancel, even
if its cleanup masks show failure. Raw INVALID/unknown FAULT does not establish
cleanup. Fault while possibly active invokes cancel exactly once; fault while
proven neutral does not. Mark cancellation attempted before entering its callback
and never recurse/retry, regardless of its result. Native cancellation is the
only cleanup path; the wrapper writes no pins.

Cancellation is bracketed by actual P/Q clocks if wrapper chronology is still
valid. Failure of P still permits the one cancel and suppresses Q. If an earlier
clock failed, perform cancel without further wrapper clocks and mark its timing
invalid. A valid P..Q publishes cancellation timing, including failed cleanup.
For a nonclock fault during a poll, cancellation precedes closing C, so valid
S..C includes cleanup. First-fault precedence remains unchanged; all returned
cleanup fields are retained even when malformed or chronologically unqualified.

`stop()` always clears fresh. Outside RUNNING it otherwise does nothing. From
RUNNING with a proven neutral Reader, enter STOPPED without callback. Otherwise
cancel once as above. With no earlier fault, STOPPED requires raw-PROVIDER_FAULT,
statusCANCELLED, unchanged active source identity, attempted_mask15, all other
cleanup masks0, all cleanup statuses0 and deadline_exceeded=false. A different
shape/identity is CONTRACT/SOURCE_ORDER; explicit unsuccessful cleanup is CLEANUP;
bad wrapper clock is CLOCK. An active stop does not append its incomplete frame.
With valid P/Q chronology, require cleanup start/end inside P..Q, cleanup span
below QTR_CLEANUP_MAX_US and checked_us==completed_us==cleanup.completed_us;
contradictory source timestamps are SOURCE_ORDER. Failed-clock cancellation
retains these fields as unqualified diagnostics and never clears CLOCK.
STOPPED means no further work and accepted reported cleanup, not physical proof.
No stop, failure, repeated begin or accessor resets the Reader or clears evidence.

## Required validation and limits

Independent expectations use this frozen contract/public API before implementation
execution. Separate author/implementer contexts may complete their files in parallel;
the author must not read implementation bodies and freezes executable tests before
their first run. Required cases: passive/default/repeated begin; missing
ports/zero capacity; command/phase/status transitions; shared raw validation;
first1/contiguous identity and immutable active identity; source brackets and
natural time wrap; aggregate half-range; NOT_DUE unchanged record; one append per
complete; capacity1 and normal128; valid final fresh pulse; bad closing C hiding
the tentative slot; stop/fault partial capture; known native fault versus malformed
fault cancellation; cancel-once and cleanup failure; first-fault/clock evidence;
timing scope/counters/saturation and stable accessors. A128-frame new Reader cannot
naturally wrap its sequence: no private seeding or impossible wrap-test promise.

Real native-binding tests prove direct delegation and exactly one Reader; actual
default sketch execution must make no callbacks. Strict normal/sanitizer host
checks, exact staged target/source/ELF startup/import/owner audit and conditional
loader fit remain required. Existing D085/D089/D106 and locked assertions stay
unchanged. No new transport framework or output work occurs during acquisition.

Full physical B2 still needs safe electrical/pad handoff and labeled black,
white-border and brown-line captures with actual cadence, intervals and cleanup.
Compiler/host/source timing is not physical timing or full-app R4 proof. New
No source/target/physical success follows merely from this adopted contract.

## Frozen observable clarifications before test authoring

- NOT_DUE also requires elapsed from the preceding start to S strictly below
  QTR_START_PERIOD_US. S..A may straddle the boundary because the native internal
  observation is not separately supplied. A late NOT_DUE is CONTRACT.
  For changed NOT_DUE evidence, invalid raw/changed phase/late status takes
  CONTRACT precedence; changed sequence/start/drive/completion/advance identity
  is SOURCE_ORDER; any other structurally valid payload change is CONTRACT.
- Clear possible-active uncertainty for neutral IDLE/COMPLETE only after raw,
  command, identity and accepted A/source-bracket checks, before C. A bad C after
  that coherent neutral result needs no cancel; bad A/identity still does.
  Raw PROVIDER_FAULT suppresses cancellation even with bad A, as above.
- Ordinary command result precedence: raw INVALID gives CONTRACT, raw
  PROVIDER_FAULT gives PROVIDER, then command/phase CONTRACT, identity
  SOURCE_ORDER, then A chronology. Source bracket checks follow an accepted A.
  Always latch clock_fault for a rejected observation even when not primary.
- Any rejected S/A/P/Q/C suppresses every remaining wrapper clock observation
  in that operation, including outer C after bad cancellation P/Q. The one
  necessary native cleanup callback still runs. No apparent measured closure
  follows a known failed wrapper clock.
- Timing start/advance last_valid clears only when its callback is actually
  invoked; a bad S changes poll timing only. Accepted S..A source measurement
  survives bad C; setup timing requires accepted S..C.
  Accepted S..A is measured even for a provider/semantic failure; invalid A
  suppresses it. not_due counts every actual start() return NOT_DUE, including
  a subsequently rejected record, late status or bad A/C. It is an observation
  counter, not a count of accepted native commands.
- Active-stop cancellation precedence: malformed raw/wrong phase is CONTRACT;
  changed source identity is SOURCE_ORDER; explicit unsuccessful cleanup is
  CLEANUP (including native status CLEANUP); otherwise a non-CANCELLED status
  is CONTRACT. Evaluate these before Q chronology, then evaluate source brackets
  only after Q is admitted. Preserve the first fault and independent clock flag.
- The existing native Reader owns charge/frame/advance guards. Do not duplicate
  them on structurally ABSENT pending records; wrapper-owned chronology/identity
  rules and shared raw validation remain required.
- Execute ordinary count/capture boundaries; source-review saturation branches
  and disclose that billions of polls are not executed. No private counter seeds,
  const_cast of Runner state or invented saturation measurement is permitted.
- Native-binding tests may replace Reader method definitions with counted fake
  owners that maintain their own declared result_. This tests the real new
  binding, not real GPIO. It does not permit editing Runner private state.
- The existing unlocked P0 registry gets only the additive literal approved
  QTR_BENCH_FRAMES=128 expectation. Preserve all assertions and other values;
  the existing D106 wrapper must still execute the18 checks, with an additional
  deliberate wrong-capacity profile rejected by the original value assertion.

## Exact target build route

Extend only the existing checked native policy's literal project allowlist with
qtr_raw.ino and route bench/qtr_raw there. Permit inert default/Immediate compile
profiles; reject MATCH, uploads and sketch.yaml/yml (including dangling symlinks)
before transport. Keep every D100/D107 dependency/property/result/artifact check
and existing project constraint. No inert manifest entry is added. Root-authored
fixture tests and separate reviewer execution cover the routing addition; label
their authorship accurately. A full generic build is unnecessary after D107's
documented inherited-Bridge finding. Actual checked artifacts still need review.
