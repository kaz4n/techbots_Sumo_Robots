# SC-AO: P5.3 opener-abort evidence options

PROPOSED OPTIONS ONLY, 2026-09-24, during D134 validation. This read-only map
does not adopt a profile, timing definition, event schema or implementation.
Only this document changed; no tests, board actions or phase changes occurred.

## What the existing code can establish

P5.3 requires10/10 physical abort trials per tested opener, with handover within
one tick of its abort condition (`docs/prompts/P5_openers.md:18`). Under approved
D034/D134, handover means current front -> TRACK, then existing consecutive
centering before ATTACK; current side/rear -> DEFEND_TURN; no current target ->
SEARCH. An ATTACK request from an opener is not an exemption from qualification.

The firmware can identify a **qualified logical abort predicate on a particular
fresh observation**. It cannot date when a box physically entered a sensor's
field or when an electrical input first changed. Opponent reads are sequential;
the complete seven-channel read has a start/end interval, not seven individual
edge timestamps (`src/hal/opp_sensors.cpp:67-84`). Fusion normalizes polarity,
debounces, then applies stuck/phantom handling (`opp_fusion.cpp:31-59,361-392`).
OPP_SET_TICKS is2 and ATTACK_ENTER_TICKS is3 (`config.h:173,189`). Neither is a
physical-appearance timestamp, nor does a count of observations prove a fixed
elapsed duration when epochs are delayed or skipped.

Existing STATE_CHANGE events contain a decision timestamp and old/new state
(`fsm_robot.cpp:953`), but no opener cause, phase or matched output token.
There is no opener-phase event; REFLANK_PHASE describes a different behavior.
Periodic25Hz frames have millisecond timestamps and can miss a complete abort
transition.60fps video has about16.7ms between frames. Neither provides a1ms
stimulus-to-handover measurement; interpolating either would invent evidence.

## Exact hooks and currently available times

| Point | Existing source | Meaning and limitation |
|---|---|---|
| Tick acquisition start T | `app/transaction.cpp:47-55`, `fsm.h:412-416` | Actual Transaction opening clock, projected as explicit TickTiming.started_us. |
| Opponent read R_s/R_e | `hal/opp_sensors.h:13-20`, `runtime_inputs.cpp:38-49,129-133` | Actual complete GPIO acquisition bounds. Runtime admits only a valid seven-channel snapshot inside the current transaction; D129 conditionally forwards these bounds. |
| Qualified perception Q | `fsm_robot.cpp:278-290`, `opp_fusion.cpp:361-392` | Fresh Fusion observation and effective mask passed to the opener. The supplied timestamp is the decision epoch D; no new clock is read inside pure core. |
| Abort predicate | `openers.cpp:31-45,117-125,186-193,283-297` | Direct current-front/side branch, Flank detectExit at the phase actually evaluated, or Wait HOLD side/rear branch. These distinguish detection from script completion if observed at the branch, before terminal state erases the phase. |
| Actual reactive handover | `fsm_robot.cpp:567-579,581-599` | Direct clears opener_active_ and calls routeNormal(true); Flank/Wait go through acceptFlank and the same call. `routeNormal` selects current perception (`:632-646`) on this observation. |
| Final decision D/token | `transaction.cpp:58-103`, `fsm_robot.cpp:1033-1050` | D is sampled before Robot computation, not the wall-clock instant a branch finishes. After arbitration/governor, the final result and token identify the request whose receipt must be checked. |
| Applied completion A | `hal/motors.cpp:146-164,169-201` | MotorGate's clock after its bounded output transaction, with full64-bit token and acknowledged, quantized duties. This is software/native-API completion; it is not an independently scoped electrical PWM edge or mechanical reaction. |
| Epoch completion C | `app/transaction.cpp:122-151` | Post-work completion, full execution duration, and previous receipt for the next decision. Robot validates it through `fsm_robot.cpp:162-220`. |

Runtime's scheduler can skip overdue releases (`runtime.cpp:272-277,329-332`).
"Next observation" is therefore not synonymous with1000us. Preserve both the
epoch relationship and measured elapsed bounds. For an ordered accepted epoch:

`T <= R_s <= R_e <= D <= A <= C <= next T <= next D`

Use offsets from one common uint32 anchor, all below half range; do not sort
wrapped timestamps or accept pairwise plausible timestamps with contradictory
epochs. D129's receipt/source checks already provide this pattern.

Two claims must remain distinct. A Q marker and handover in the same Robot
result prove same-observation routing, with both stamped D; they do not imply
zero CPU latency. The matching A adds a conservative application-completion
measurement. `[A-R_e, A-R_s]` bounds age from that acquisition, not physical
appearance. `A-D` bounds work after decision entry; logical qualification occurs
during that work. Root must adopt how these support the original one-tick
criterion; do not silently turn it into a different physical-response promise.

## Options and bounded recommendation

1. **Keep only existing events and qualify physical timing externally.** No
   firmware/RAM changes. Host tests retain same-observation routing evidence.
   A suitably identified external instrument could measure electrical signals
   and output application, but no suitable setup or source-to-clock binding is
   currently established. Electrical appearance includes debounce latency,
   unlike the qualified abort predicate; that distinction must be resolved.
   Existing25Hz logs and60fps video alone leave P5.3 timing unproved.

2. **Reuse the existing recorder/event/receipt path for one P5 abort candidate
   per accepted START attempt (recommended software preparation).** Add only
   opt-in observational capture of the actual abort branch and final routed
   request, with the existing read window and next matched MotorGate receipt.
   Retain the first qualified candidate, including failed/incomplete outcomes;
   no retry or selection of a later favorable exit within that attempt. No
   continuous logger, second recorder, new motor path, duplicate sensor read,
   second Fusion/opener/governor call, or new clock in core is needed.

   D129 already uses Event::TIMING=10, fixed8-byte events, accepted-attempt
   headers, source pairs, full-token pending checks and explicit incomplete/
   excluded outcomes. Its current profile is **P4 reactive only**, where
   openers do not run (`P4_timing_evidence_contract.md:6-13`), and its loss-trace
   grammar cannot describe P5. Preserve that profile/grammar exactly. A distinct
   opt-in P5 interpretation/profile/header and narrow metadata admission would
   need a new adopted contract and independent tests. Do not merely enable
   current D129 or relabel its LOSS_* records. Reuse the actual app/Runtime and
   existing checked build/receiver paths; no new deployment authority follows.

3. **Store only one fixed RAM trial receipt and read it after the run.** This
   avoids an event-codec extension but requires a separately pinned passive
   capture binding and evidence lifecycle. Existing MEM-AP collectors are
   source/artifact-specific, not permission for arbitrary addresses/runs.
   It also separates evidence from the existing attempt/loss ownership. This
   is not preferable while the existing event path already carries the needed
   timestamps and receipt result; do not create a second capture system now.

Option2 should first be a small contract for the producer's evidence semantics;
offline analysis can reuse current CSV validation and record order. The present
`tools/analyze_target_loss.py:197-200,276-287` deliberately accepts D129's exact
header/details and35000us loss bound. It must never score P5 records as P4 loss
trials. Do not add a generic telemetry/analyzer framework to bridge that gap.

## Cause and phase details that the candidate must retain

- Observe qualification before recording successful handover. Merely emitting
  a marker after routeNormal and subtracting two identical D timestamps would
  be circular; it cannot reveal an omitted or delayed handover. The candidate
  must survive to report missing/late/wrong routing instead of silently becoming
  "not exercised". Use the actual production predicate once, not a second
  strategy evaluator with potentially different rules.
- An Exit enum alone is insufficient. Direct's FRONT_TARGET may come only from
  its saved countdown snapshot. Flank's currentTarget after normal completion
  can return the same FRONT_TARGET/SIDE_OR_REAR_TARGET values as detectExit.
  Record detection cause separately from snapshot-only, natural completion,
  timeout and invalid-script paths. A snapshot-only exit remains correct D034
  behavior but cannot timestamp the new physical path stimulus.
- Capture **phase at the predicate evaluation**, not just phase at step entry
  or the terminal FINISHED phase. Flank may advance through up to three phases
  in one call. PIVOT can finish and TRAVERSE can legitimately detect a front
  target on that same observation. A held effective detection can first become
  an abort because the phase changed; do not invent a new electrical onset.
- SIDESTEP PIVOT ignores front but permits the outer-side/rear abort. Its
  DRIVE/TURN_IN front has D033 priority over outer detection. ARC PIVOT ignores
  opponent detections; its inner-side cue starts TURN_IN rather than reactive
  handover. WAIT's ordered widening cue starts full SIDESTEP_R under D055; that
  cue is not itself an opener exit. WAIT HOLD side/rear does exit; its later
  Flank exit must retain running mode WAIT and the inner phase. These cases are
  existing B12 semantics, not new rejection policies.
- Preserve raw/confirmed/effective distinctions sufficient to explain the
  selected predicate; the opener consumes current effective perception. Do not
  change eligibility to a new raw-mask rule. Root must decide the minimal
  diagnostic metadata before fixing a wire grammar. A small conditional cause/
  phase result from the actual branch may be needed: today's public results
  erase that distinction. No such interface has been adopted in this map.
- Do not copy D129's ATTACK/no-contact/both-positive-wheel admission. DIRECT can
  exit on the GO observation before any OPENER receipt; WAIT can validly hold
  zero duty. Contact is not a blanket P5 exclusion. Those P4 approach conditions
  would manufacture additional P5 requirements.

## Attempt, priority, token and receipt continuity

Use the real accepted START release, GO, captured mode and AttemptRecorder
epoch; bind each physical trial to source/config/artifact, compiled profile,
M0/M1 and setup evidence. Header metadata and local hashes are declarations or
software identities, not proof of hardware origin. No arming before the actual
GO/permission path; a genuine current-source GO abort must remain representable.

Actual edge preemption/escape fault, STOP, lost permission and contract fault
must retain their existing priority (`fsm_robot.cpp:488-517`). They are excluded
or invalid abort-timing evidence, never successes or motion overrides. Natural
completion and snapshot-only exit are separate diagnostics. Incomplete/stale
source or malformed chronology cannot become a zero-delay pass. Do not import
extra contact, raw-white or filter policies merely because D129 uses them;
base classification on actual B2/B12 behavior and the target-loss/P5 distinction.

At final arbitration, retain the complete64-bit request token and final routed
state. The immediately following receipt must match that token and the existing
pending request, pass the existing duty/EN/application checks, and contain valid
explicit T/D/A/C timing with duration_valid. Preserve legitimate hardware duty
quantization. P5 handover is not necessarily a brake or zero output, so D129's
exact-zero predicate is unsuitable. A later unrelated receipt cannot repair a
missing/mismatched one. A wire candidate ID is not a truncated transaction token.

Complete the prior receipt before evaluating new-tick edge/STOP, as Robot
already does. Later preemption cannot erase a completed valid measurement.
Reset, Transaction abort, missing tail, token exhaustion, duplicates, recorder
loss and malformed batches must retain their existing explicit incomplete/
invalid handling. No changed receipt may attach to a reset/new-attempt candidate.
M0 and synthetic receipts may exercise the machinery but never satisfy physical
P5.3, even if their calculated elapsed time is small.

## Data/RAM cost and evidence still required

The useful record set is small: one attempt header; read start/end; qualified
cause/phase; final routed decision; matched application or terminal diagnostic.
That illustrative six-record success costs48 wire bytes per attempt, before
CSV/framing; additional mask metadata could require another record. This is a
cost sketch, not an adopted grammar or capacity proof. Existing event capacity
remains4096; do not grow the long-lived recorder or reduce frames to make room.

Pending state needs a full64-bit token, a few uint32 timestamps and compact
phase/cause/status. D129's current TimingTrace has one token, three timestamps
and one enum (`fsm.h:616-622`). Reuse mutually exclusive profile storage where
possible; actual padding, copied RobotInput/RobotResult/Transaction objects,
EventBatch capacity and stack must all be measured. Eight-byte wire encoding
does not establish the whole RAM delta. Count worst-case legacy plus trace
events on the same tick before selecting a bounded batch size; keep explicit
overflow accounting. Default builds must acquire no trace fields/cost.

Historical default native modeled headroom was only16 bytes. P4's earlier
6512-byte margin excludes openers and cannot qualify a P5 profile. D129+
target fit is itself pending. A P5 trace requires fresh checked target/loader,
loaded RAM/stack and full-source timing evidence; host sizeof or success alone
cannot establish any of these. Instrumentation must not change arbitration or
claim its overhead is free.

After adoption, independently freeze tests for actual Runtime projection,
production predicate/cause, same-epoch and delayed/missing handover, complete
token/receipt continuity, wraps, ignored-phase detections, snapshots, normal
completion, WAIT cue, edge/STOP, M0, overflow and missing tails before execution.
Then retain10 actual physical abort trials per tested opener, including original
failed/excluded/incomplete runs and the required later interpretation. Do not
silently replace inconvenient attempts or treat ten host scenarios as ten
physical trials. Any physical-appearance/electrical-response claim still needs
its separately identified measurement; qualified-cue evidence has a narrower
meaning. Root decides the next contract after D134.
