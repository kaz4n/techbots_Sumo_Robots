# D085 asynchronous QTR acquisition and controller freshness

2026-09-23 Asia/Dubai, baseline4ada2cd. D051/D075 delegate these explicit software
choices; no physical handoff, wiring approval, measurement or gate is inferred.
The previous goal turn made PROGRESS: actual D084 implementation2c16023 and
independent host/target/review evidence4ada2cd. This task supplies the real native
QTR driver and its controller evidence path, not a second diagnostic framework.
Source basis: P2_qtr_native_audit.md and P2_qtr_native_raw/freshness_audit.md.

## Timing decision and limits

Keep TICK_US1000, QTR_CHARGE_US10, QTR_TIMEOUT_US1500 and every white threshold.
Replace the impossible every-tick complete RC acquisition with separately serviced
frames. Start no sooner than2000us after the previous start; never restart a busy
frame. Selected whole-frame budget2500us includes charge, acquisition and cleanup;
equality fails. An eligible caller rearms at the first service opportunity after
completion and the minimum start interval. This is a nominal400..500Hz candidate,
not a guaranteed cadence. The core still runs at1kHz and requires fresh opponent
inputs on each initialized tick. Source age6000us expires at equality.

New config constants centralize these development selections: QTR_INPUT_PINS copy
the unchanged2/4/7/8 proposals; QTR_QUANTIZATION_US1, QTR_START_PERIOD_US2000,
QTR_FRAME_MAX_US2500, QTR_CALL_MAX_US100, QTR_CLEANUP_MAX_US100,
QTR_CHARGE_MAX_US100, QTR_MAX_ADVANCES8192 and QTR_SAMPLE_MAX_AGE_US6000.
Charge release requires at least10+1 reported ticks after the last HIGH write;
the extra tick covers integer clock quantization. Charge age>=100 faults.
These are engineering guards, not measured hardware limits or changes to the
nominal10/1500 values. B2's original1600us complete-call acceptance is explicitly
superseded for this asynchronous method by bounded calls plus2500us complete
frames; physical color separation and complete-tick<800us remain required.

Each call does a fixed bank pass, never a1500us wait or an unbounded clock loop.
Check call elapsed after each native operation; >=100 faults. Fault cleanup has a
separate100us reporting budget and still attempts every safely owned pad once.
No software guard proves a preempted/native call's wall time. Frame time includes
cleanup, and a completed record is valid only when every relevant budget passes.
Every observed time increment must be<2^31; wrap is ordinary. Equal clock readings
are allowed. At most8192 active advance calls per frame; a successful completion
on the last allowed call wins, otherwise exhaustion faults. No later call resumes
a fault. With no service call, no background deadline enforcement is claimed.

## Actual native owner

line_qtr::Reader constructs without I/O, cannot copy, and has no destructor I/O.
begin(exclusive_pads) is setup-only, one attempt per instance. No grant means no
write. Preflight the whole metadata bank, device readiness and hardware guards
before claiming a boot-lifetime single-owner slot or issuing any configuration.
A second owner is rejected. Retain the claim after any post-claim failure; reset
requires actual firmware reset, not a public software reinitialize method.

Bind exact installed Arduino pin/port/bit mapping, dt_flags0 and supported masks.
Require GPIOA/B clocks enabled and resets clear before pad reads. Reject individual
locks and any selected EXTI mask/trigger/software/pending bits, enabled/pending/
active NVIC lines2/3/4/12, and enabled trace I/O. Capture selected EXTI source
nibbles, AFR nibbles and trace fields; reject subsequent changes. Do not alter
clocks, resets, EXTI/NVIC, debugger or another peripheral to pass admission.
The caller grant plus final-image exclusions is necessary: register consistency
alone cannot prove software exclusivity or absence of a debugger.

Granted initial INPUT/ANALOG are neutralizable. AF0 specifically on PB3/PB4 is
also a deliberate startup handoff; reject every other alternate/output state.
Preserve exact initial state for partial-begin cleanup eligibility. Native
GPIO_INPUT sets no-pull/input/push-pull/low-speed; AFR and ODR are not cleared.
Use checked GPIO_OUTPUT_HIGH for charging, which preloads HIGH before output.
After each configure require exact expected mode/type/pull/speed, unchanged AFR,
unlocked state and charge ODR HIGH. During charge, read back physical digital
HIGH on all four pads before release; a LOW is an explicit charge failure.

start() accepts only ready IDLE/COMPLETE and the minimum interval. BUSY/NOT_DUE
return status without replacing the saved report or generation. An accepted start
clears the old frame, advances uint32 generation (first1, wrap including0), records
start time, configures all four outputs HIGH and records the last-HIGH completion.
It returns CHARGING without waiting. advance() before release age11 performs no
write. On qualification it timestamps each individual INPUT release before/after,
then makes one read pass. Later advances make at most one read pass over unfinished
pads. Each read is bracketed with actual micros before/after; native values other
than0/1 fail explicitly. A completed pad is never sampled into a different frame.

Each pad retains release-before/after, last-HIGH-before, first-LOW-after and masks.
Before any HIGH observation the conservative duration lower bound is0. Thereafter
lower=max(0,last_HIGH_before-release_after-1); use widened arithmetic and admitted
forward times. First LOW gives exclusive upper=(first_LOW_after-release_before)+1.
These are sampled timing bounds under the RC discharge model, not an exact
hardware edge timestamp. Do not subtract observed overhead or silently clamp a
late LOW to1500. If a still-HIGH read yields lower>=1500, finish that pad as a
right-censored timeout with no finite upper bound. LOW takes precedence at a
single read, even when delivered after1500; preserve its actual interval.

Finish when all four pads have a LOW interval or qualified timeout. Restore INPUT
on every safely owned pad and verify neutral mode; only then publish COMPLETE.
Snapshot.valid means a complete bounded raw record, not a qualified color or
physical electrical acceptance. report() returns the same identity, not a new
measurement. start() may begin the next frame, leaving app/core history separate.
cancel() during an active frame cleans up then latches CANCELLED; idle/complete
cancel is a no-op. Any failure is reset-only and never republishes valid data.

Cleanup makes at most one checked INPUT attempt for each eligible pad, recording
attempted/failed/skipped/nonneutral masks and each native return status. Continue
eligible cleanup after an earlier error or elapsed cleanup-budget violation.
Global ownership loss means no blind writes. Per-pad eligibility accepts only
the captured old/requested states of that owner's attempted transition; never
an arbitrary alternate/output state. A partial configure may therefore require
explicit skipped/unconfirmed cleanup. No LOW expectation on floating inputs.

## Qualification and actual controller path

An adapter validates the complete raw record, then compares each interval with
its unchanged config threshold: upper<=threshold proves white; lower>=threshold
proves black. A bracket straddling the threshold, malformed timing or invalid
record must not become measured black. An ambiguous completed frame is INVALID
and causes reset-only inhibition; retain raw diagnostic evidence. Pending/idle
reports are ABSENT. They are not sensor faults by themselves and never renew
source age. A provider fault is INVALID. Source age starts at frame.started_us,
not cleanup or delivery. The adapter preserves all unrelated Robot inputs.

Explicit Robot line mode is selected on its first admitted tick and cannot switch
until reset. Separate opponent_fresh from line updates; legacy aggregate behavior
is preserved. VALID line evidence carries start/completion/generation/qualified
white candidates; validate known fields, forward times, bounded span/age and
strictly advancing source/generation. An identical replay is retained, not new;
conflicting identity, reversal, invalid provider/contract or unknown shape latches
LINE_CONTRACT. ABSENT retains accepted line state until its accumulated age reaches
6000us, then inhibits. Accumulate age across all decision intervals to prevent wrap
resurrection. No accepted line history at initialization_complete also inhibits.
Unavailable line state before initialization may wait in BOOT without a fault.

Only a distinct accepted line frame advances QTR_CONFIRM_TICKS (default remains1).
An expired retained interval breaks confirmation even before initialization;
retain identity history for ordering, but reset its classification counters.
Retained confirmed white preserves edge priority, including white already present
at GO. Opponent Fusion/debounce/contact still see each fresh1kHz opponent sample.
Escape phase timers advance each control tick, but retained line evidence cannot
consume a replan, update the new-white baseline or cause all-black escape exit.
Fault masks retain priority even while retained; entry at GO may use qualified
retained white. A fresh black frame plus completed script is needed for exit.
Countdown line-warning input is supplied only for a newly admitted frame whose
started_us and delivery are both in the original final warning window; old-source
white delivered inside the window cannot latch it. Warning lifetime/deadlines
stay unchanged. A fresh black frame delivered on the tick the row reaches DONE
is sufficient for exit even if acquisition began before DONE; a black frame from
an earlier decision remains retained and cannot exit until another fresh frame.
QTR_STUCK qualification starts on current valid
white and ages with pivot time while that bounded line state remains valid.
Frame recording remains a state snapshot with its25-byte layout unchanged; do not
claim that every recorded line mask came from a new electrical acquisition.

The native driver, adapter and Robot path need independent spec-derived tests,
actual native-source substitutes, full host/sanitizer regression, inert target
compilation and fresh review. Preserve every established locked assertion. The
future scheduler must service acquisition/rearm and solve serialized600us IMU +
150us motor settle +100us ADC budgeting; these maxima cannot be asserted to fit
800us. Async QTR alone does not solve that scheduling problem, physical brown/
white separation, clock SC-AJ, inherited F091 or human phase acceptance.

## Additive public consumer contract

Core LineEvidence defaults to legacy. In explicit mode, opponent_fresh is the
independent opponent flag and observations_fresh/line_raw_us are ignored. INVALID
presence or contract_valid=false latches LINE_CONTRACT even before initialization.
ABSENT ignores its unused source/mask fields; retained state is internally owned.
The first valid sequence may be any uint32. Later distinct frames advance both
sequence and start, by1..2^31-1; start spacing>=2000 and next start>=previous
completion. Sequence gaps are unconsumed reports, not invented frames. Completion
must be forward from start with span<2500, decision forward from completion and
age<6000. Exact start/completion/sequence/white-mask replay does not update the
classifier or age. Partial/conflicting identity rejects. Rejected input never
replaces history. Reset clears mode/history, preserving existing token rules.
RobotResult exposes line_available/updated/source_us/age_us/sequence; duplicate
decision timestamps clear only update/action pulses without admitting new input.

Reader snapshots use high_mask for a HIGH observed after release (not charge
verification), low_mask for a first LOW interval and timeout_mask for qualified
right censorship. Pending NOT_STARTED must be its default record; successful IDLE
has no frame/cleanup/masks and statusOK, while checked_us may record setup. Pending
CHARGING/DISCHARGING must have statusOK, validfalse and no cleanup/completion;
CHARGING has no released/data masks, DISCHARGING released_mask15. Per-pad native
read status may be0/1, configuration success0. High/low/timeout masks are low4bits,
low and timeout disjoint, timeout a subset of high, and data a subset of released.
FAULT has validfalse and a known terminal fault status; diagnostic failed timing
is not required to be a valid interval. Command statuses BUSY/NOT_DUE/etc are not
published as a provider fault or as successful pending status.

Adapter COMPLETE requires statusOK/validtrue, released15, disjoint low|timeout15,
known masks, exact lower/upper derivation, all source/drive/release/read/cleanup
times forward inside the frame, charge hold>=11 and release age<100. Timeout
requires high evidence/lower>=1500/upper0/no LOW timestamp. No-HIGH LOW interval
requires last_high0/lower0. First-LOW interval has nonzero exclusive upper. Every
cleanup attempt must succeed: attempted15, other masks0, statuses0, deadlinefalse,
cleanup duration<100 and completed_us==cleanup.completed_us==checked_us. Advances
are1..8192. No max-service-gap value is claimed as measured physical ISR latency.
Classify each complete pad as white when upper<=threshold, black when lower>=
threshold, otherwise AMBIGUOUS; a timeout is black only by its actual lower bound.
Pending maps ABSENT only after its structural validation; malformed/unknown
phase/status/payload maps INVALID with contract_validfalse. Valid provider fault
or ambiguous raw frame maps INVALID with contract_validtrue. All unrelated inputs
and actual source fields are preserved only for qualified VALID evidence.
Pending interval/time fields are diagnostic and are not qualified or forwarded;
their structural validation covers the specified phase/status/valid/cleanup/mask
shape and native statuses0/1. Only COMPLETE timing intervals are qualified.
