<!-- Examines bounded recorder evidence for P4 loss braking and later P5 aborts. -->
<!-- Separates supplied source/application timestamps from physical motion proof. -->
<!-- Read-only source analysis; no implementation, test execution or measurements. -->
# SC-AO timing evidence options

2026-09-24. Proposal for the coordinator to adopt or revise under D051; this is
not a public implementation contract, acceptance result or phase gate. Only this
analysis file was written. New D128 public oracle contents were not inspected.

## Recommendation

Implement a **P4-only, explicitly enabled timing-evidence slice first**, using
the existing eight-byte event records and recorder owner. Preserve the real
opponent acquisition interval, observe the actual normal-route loss brake, and
finish evidence only from its valid, full-token-matched application receipt.
Keep firmware profile0, established tests, frame format/rate/capacity, source
grants and motor permissions unchanged.

For the smallest first slice, adopt **one candidate per accepted attempt**. The
first eligible raw-front-clear starts it; success or exclusion closes it until
a new genuine attempt/reset. A transient clear is an excluded candidate, not a
reason to silently select a later favorable episode. This one-candidate scope
is a proposed engineering choice, not a pre-existing P4 requirement. It avoids
an episode queue, identifier rollover and raw-edge logging that could consume
4096 events in seconds. If repeated episodes are required instead, add an
explicit nonreused episode identifier and overflow policy in a later contract.

Do not add P5 trace code to the default target in this slice. The coordinator's
D128 compile evidence is P4 source `9ddaa2aa`, payload 251116 bytes, modeled peak
255632, free 6512. The current default ELF `21b28ee3` has payload 257272, modeled
peak 262128, free **16 bytes**. These supplied build results are not remeasured
here. Neither unconditional instrumentation nor a future instrumented P5 build
can assume fit. Configured Runtime paths can change the linked footprint too.

## What the current software actually observes

| Seam | Existing fact | Consequence |
|---|---|---|
| `src/hal/opp_sensors.h:15`, `.cpp:73` | Seven sequential GPIO reads have one `started_us` / `completed_us` interval, per-channel return statuses, and a full-valid mask. | There is no per-pin transition timestamp or proof that all pins were sampled simultaneously. |
| `src/app/runtime_inputs.cpp:38` | Runtime validates the entire read interval against the current Transaction start and decision, with a half-range clock bound. | These are usable real source boundaries. |
| `src/app/runtime_inputs.cpp:129`, `src/core/fsm.h:417` | Robot receives only raw mask and freshness; source boundaries are discarded. | A narrow conditional evidence field is needed; do not substitute tick start or decision time for acquisition time. |
| `src/core/opp_fusion.cpp:24`, `:361` | Debounce uses decision `t_us`; each bit's first observed clear anchors its 30 ms interval. A raw reassertion cancels that bit's clear interval. | Preserve this behavior. Do not change debounce to source time merely to improve a measurement. |
| `src/core/opp_fusion.cpp:379` | Order is debounce, stuck removal, contact cue, phantom filtering, then effective bearing. | Effective loss alone cannot establish raw target loss. |
| `src/core/fsm.cpp:59`, `src/core/fsm_robot.cpp` (`routeNormal`) | A previously active front becoming absent produces the actual normal brake; current side/rear can select DEFEND rather than SEARCH. | Instrument the actual brake result, not a reconstructed STATE_CHANGE predicate. |
| `src/core/fsm_robot.cpp` (`receive`, `validTimingReceipt`, `savePending`) | The pending request has a full 64-bit token; a next-tick receipt carries actual duties, enabled state and `applied_us`. | Match that exact request, and retain receipt time rather than its later arrival time. |
| `src/hal/motors.cpp:145`, `:170` | Gate timestamps after its output transaction; actual duties reflect PWM quantization and M0 inhibition. | This is an applied-zero receipt completion, not the first physical PWM/EN edge or stopped wheels. |
| `src/app/transaction.cpp:86`, `:115` | Gate application follows Robot; recorder consumes Robot before the current receipt is fed back. Completion validates S/D/A/C order. | A successful loss receipt normally becomes an event on the next observation. Missing tail evidence must remain missing. |
| `src/core/fsm_robot.cpp` (`prepareFrame`, `receiveFrame`, `publishEvents`) | Frames are 25 Hz, plus accepted-START/stopping frames; matched duties are filled later. STATE_CHANGE has decision time. | Neither the 35 ms applied-drop requirement nor a 1 ms abort handover is established by ordinary frames. |

The metric must be named **first observed all-front-raw-clear acquisition to
matched applied-zero receipt**. It cannot claim the time when the box physically
left the beam, the first asynchronous GPIO transition, or mechanical rest.
External instrumentation is needed if the intended criterion requires those
physical instants. No new instrument, wiring assumption or hardware run is
authorized by this recommendation.

## Candidate P4 observation and lifecycle contract

1. Begin evidence membership at the actual accepted START and emit one version
   marker after START_RELEASE, so AttemptRecorder retains it. Arm only after
   real GO and an eligible ATTACK approach observation: no committed contact,
   a current effective front target, a raw front detection, and a validated
   preceding receipt with EN enabled and both actual duties strictly positive.
   M0/synthetic zeros cannot establish an approach. Do not arm from a snapshot,
   unconfirmed raw assertion, frame duty byte or requested/governed duty alone.
2. The first subsequent fresh, complete acquisition with logical raw front
   mask zero starts the sole candidate. Logical mask is exactly
   `(opp_raw_mask ^ OPP_ACTIVE_LOW_MASK) & 0x07`. Retain its actual read-start and
   read-end timestamps. At this raw-clear observation, recheck the genuine
   immediately preceding full-token-matched receipt: it must belong to ATTACK,
   have EN enabled and both actual duties strictly positive, with no committed
   contact. An earlier nonzero receipt that merely armed the feature is not
   sufficient. Do not invent a later onset if all fronts had already been clear
   before arming. Source time zero and natural wrap are valid.
3. Every subsequent admitted sample must keep all three raw fronts clear.
   Reassertion of any raw front cancels as TRANSIENT, even if debounce would
   retain the old effective target. Partial clear before the first all-clear
   sample is not the candidate origin. TRACK caused by staggered front-bit
   debounce completion may occur during the candidate and does not itself
   cancel the original approach-loss measurement.
4. Front stuck removal or phantom suppression cannot substitute for debounce
   loss. Exclude if a front fault is already present at onset, is newly declared
   during the candidate, or front bits are being removed by phantom filtering.
   Side/rear stuck bits alone need not exclude it. Require unsuppressed confirmed
   front zero at the actual normal loss-brake decision. A retained phantom
   marker that does not mask the current front is not, by itself, a cancellation.
5. Contact acquisition, an unrelated route such as REFLANK, actual edge
   preemption, STOP, owner fault or lost permission closes an active candidate
   as excluded/interrupted, never as successful loss braking. Evaluate these
   causes ahead of declaring the current loss-brake decision. Preserve all R5
   escape work and R6 behavior; evidence failures must not steer the robot.
6. Capture the actual normal-route `NormalResult.brake` caused by front loss.
   Its final selected state can be SEARCH or DEFEND_TURN. Only after final
   arbitration/governing remains valid and requests zero with brake may that
   request's full token become the expected zero-receipt token. A brake due to
   edge-exit deferral, WAIT, STOP, inhibition or quantization is ineligible.
7. On the next receipt, use the existing full identity and duty checks plus
   valid explicit S/D/A/C timing. Require `receipt.token == pending.token ==
   expected_loss_token`, exact finite left/right zero, and EN enabled for the
   normal brake. Emit with `receipt.applied_us`. Disabled zero is diagnostic
   inhibition, not this successful approach-to-brake measurement. Wrong token,
   malformed/late/future timing, missing receipt or invalid duties never create
   an applied-zero event. Do not wait for or borrow a later request's zero.
8. Receipt processing precedes current sampling: a valid completed prior brake
   may finish evidence before a new tick's edge/STOP/reassertion. Conversely,
   safety already selected on the brake-request tick excludes it. This preserves
   actual chronological ownership instead of retrospectively changing a result.
9. Same-timestamp Robot duplicates retain the existing no-pulse behavior and
   cannot arm, re-anchor or close evidence. Stale/partial opponent sources cancel
   active evidence. Require every relevant unsigned delta from one common
   anchor to be below `0x80000000`; backward/ambiguous clocks are invalid, not
   large measured delays. Runtime/Transaction already enforce such chronology;
   direct host callers must not bypass evidence-specific validation.
10. Reset, Transaction abort or missing final drain may leave no cancel event.
    Preserve the owner interruption/loss status and classify the open candidate
    INCOMPLETE. Never synthesize a final receipt or closure marker. A candidate
    still open beyond 35 ms is not a measured zero-delay failure merely because
    its terminal event is missing; an eventual valid late zero provides a
    measured failure. A separate nonzero-after-deadline witness is optional
    future work, not necessary for the first slice.

The extra source fields should describe supplied evidence only. Runtime copies
them solely from its existing validated opponent Snapshot, using the current
Transaction as identity; no new HAL clock calls, reads, sequence generator or
change to Fusion's debounce timing is needed. Legacy direct Robot callers with
no source interval remain behavior-compatible but cannot produce qualified
source-to-receipt timing evidence.

## Small conditional wire extension

Prefer one conditional new explicit event code `TIMING = 10`, enabled only in
the instrumented P4 build. Codes 0..9 retain their exact values and semantics.
The following subtype allocation is a concrete option, not yet adopted:

| detail | Name | Timestamp | value |
|---:|---|---|---:|
| 0 | HEADER | accepted START decision | `0x0101` P4/M0 or `0x0105` P4/M1 |
| 1 | LOSS_READ_START | first all-clear read `started_us` | 1 |
| 2 | LOSS_READ_END | same read `completed_us` | 1 |
| 3 | LOSS_BRAKE_DECISION | actual final valid loss-brake decision | 1 |
| 4 | LOSS_ZERO_APPLIED | matching actual `applied_us` | 1 |
| 5 | EXCLUDED_TRANSIENT | reassertion decision | 1 |
| 6 | EXCLUDED_FILTER | relevant stuck/phantom exclusion decision | 1 |
| 7 | EXCLUDED_CONTACT_ROUTE | contact/unrelated-route decision | 1 |
| 8 | INTERRUPTED_EDGE | edge preemption decision | 1 |
| 9 | INTERRUPTED_STOP_FAULT | STOP/owner-fault decision | 1 |
| 10 | INVALID_SOURCE_TIME | observed source/time rejection | 1 |
| 11 | INVALID_RECEIPT | receipt rejection observation | 1 |

Header high byte is metadata version 1. Low bits are P4 capability bit0 and
MOTORS_ALLOWED bit2; other bits are zero in this slice. The remaining records
use candidate 1, unique within the retained attempt. These wire identifiers do
not replace the full 64-bit pending token inside Robot. No token truncation is
allowed at the matching boundary. Explicit source windows and known subtypes
must be validated before append; unknown/reserved combinations fail semantics.

Preserve existing event ordering and add a specified deterministic timing
suffix for current decision events. Receipt evidence is emitted during the
existing previous-receipt stage, before current decision events. A source
window can therefore appear after a decision event with a later numeric time;
ordinal order remains authoritative, and analyzers pair named fields rather
than sorting uint32 timestamps. Keep the source-window pair adjacent and in
START/END order. No emitted pulse is replayed after terminal closure.

The default-off option should initially be conditional on P4 only, either
directly on `SUMOX_P4_REACTIVE` if every P4 build is to carry it, or via a
compiler-wide `SUMOX_TIMING_EVIDENCE` switch that requires that profile. The
latter keeps the already accepted D128 build independently reproducible.
Recommend the explicit switch, with exact checked inert flags and no upload
key. P5 enablement and its metadata capability bit would be a separate adoption.

An unconditional/global metadata-version update is possible, but changes the
default codec acceptance domain and could add default target code/data. It
needs explicit compatibility/fit work and offers no advantage for this first
P4 measurement slice. Do not overload FAULT, FIRST_NONZERO, STATE_CHANGE or
reserved frame flags to avoid declaring the extension.

## Offline interpretation and budget

Let S/E be the validated read window, D the brake decision and A the matched
zero receipt. Validate `S <= E <= D <= A` using unsigned offsets from S, all
below half range. Report both `A-S` and `A-E`; do not replace them with one
invented raw observation instant. The requested full bound is
`OPP_CLEAR_MS * 1000 + 5000`, currently **35000 us inclusive**.

- PASS when `A-S <= 35000`: the conservative source-window upper bound passes.
- FAIL when `A-E > 35000`: even the latest source-window endpoint is too late.
- INDETERMINATE when the interval straddles the threshold. Report the interval.
- INCOMPLETE when required events/closure or loss-free ownership are missing.
- EXCLUDED for an explicit transient/filter/contact/safety cancellation; this
  contributes no passing run. Header without candidate means NOT_EXERCISED.
- Missing header means NOT_RECORDED/unsupported, never a pass. Contradictory
  pairs, duplicates, ordering, unknown metadata or impossible chronology mean
  INVALID. M0 or host-generated event arithmetic is not physical acceptance.

Qualification also requires the existing CSV format/owner consistency checks,
sealed loss-free attempt, declared closure and exact file binding. Reuse the
existing validator; it intentionally accepts unknown numeric event bytes and
does not enforce event semantics (`validate_csv_bundle.py:154`). The CSV schema
and eight-byte raw event representation need not change. A later narrow
analyzer should validate this extension and safely bind any reread to the
validated hash/byte/row snapshot, following D127's approach. It must not treat
local hashes or a supplied manifest as proof of common hardware origin.

The fixed event buffer stays first4096 (32768 payload bytes), with all current
overflow/rejection/incomplete handling. One candidate adds a header, a read
pair and either decision+receipt or one cancellation: at most five records per
attempt. A receipt-invalid end following a decision also totals five. Count
extra per-result sources conservatively; source pair plus decision/cancellation
can add three events, and receipt capture can add one. Do not assume free batch
slots just because typical ticks are sparse.

The original 21-entry capacity argument in
`P1_robot_event_contract_audit.md` counted ten FAULT categories. Current code has
eleven including EXTENDED_CORE_CONTRACT. Revisit actual mutual exclusions;
the old arithmetic alone is not a new capacity proof. A simple provisional
instrumented-only upper bound is 22 legacy + 4 timing = 26 entries; alternatively
prove a tighter bound before choosing it. Keep default 21 unchanged. Five added
eight-byte entries cost 40 bytes per EventBatch, with at least Robot's retained
result and TransactionReport copies, plus stack/call copies. The one-candidate
state and conditional source fields add further bytes. Measure native linked
storage, loadable peak and stack/WCET consequences; no fit is asserted here.

## P5 reuse, deferred

P5 needs the actual phase-specific abort-condition observation and final
handover decision, not an applied-zero receipt. A target exit can legitimately
handover to TRACK under D034; literal immediate ATTACK would violate the
existing three-observation qualification. Preserve D034 and report normal
handover latency separately from eventual ATTACK acquisition.

Current helper `Exit::FRONT_TARGET` / `SIDE_OR_REAR_TARGET` is insufficient to
reconstruct why an exit happened: DIRECT may use a saved snapshot; Flank may
complete a primitive and return a current target; WAIT delegates phases; one
Flank call can enter a new phase and then evaluate its guard. Instrument the
actual accepted abort branch with a one-call condition/reason/phase pulse and
forward it through WAIT. Do not duplicate the guards in Robot or infer an abort
from a final state transition. Existing tests at `test_opener_flank.cpp:259`,
`:307`, `:316`, `:377`, `test_opener_direct.cpp:149`, `:219`, and
`test_wait.cpp:281`, `:385`, `:647` provide reusable literal semantics.

A later same-code extension could reserve detail32=current-front abort,
33=current-side/outer abort, 34=snapshot-only exit, and 40=normal handover.
Condition payload can pack low7 effective mask plus explicit evaluated phase
in the high byte; handover payload is the actual public destination state.
Accepted START/mode and the one opener per attempt supply scope. Record current
condition observation time and final committed handover decision independently;
even a GO-time opener that never appears as committed OPENER needs the handover
marker. Snapshot-only exits, normal deadlines, internal TURN_IN transitions,
WAIT approach cues, invalid primitives and edge/STOP preemptions are separate
outcomes, not successful P5 obstacle-abort trials.

For an eligible current-condition pair, report exact decision delay; <=1000 us
is the proposed one-tick time threshold under the current 1 kHz schedule. The
implementation currently hands over in the same Robot observation, so its
decision-to-decision delay should be zero. Also expose whether a later distinct
observation was involved if that behavior ever changes. Missing condition or
handover does not prove a measured failure. This is software observation timing,
not time from the unrecorded physical obstacle arrival. Native P5 memory
feasibility, exact subtype adoption and its independent oracle remain pending.

## Compatibility and next bounded task

Established `tests/test_logframe.cpp:376` explicitly accepts codes0..9 and
rejects10..255. `tests/robot_scenario.h:28` hardcodes batch <=21 and is used by
protected `tests/locked/test_robot_safety.cpp`. Recorder tests also use literal
21-entry cases (`test_attempt_recorder.cpp:596`). Keep their profile0 behavior
and files unchanged; add separate instrumented tests/fixtures. Existing raw
CSV/validator tests intentionally preserve unknown event codes, so no relaxation
is needed there. The eight-byte event layout, first4096 policy, receipt checks,
old event ordering and default frame cadence remain protected behavior.

Next slice: adopt the P4 reference metric, one-candidate lifetime, conditional
wire grammar and batch bound; publish the narrow source-evidence interface;
freeze independently authored source/receipt/metadata tests before execution.
Implement only P4 conditional evidence and exact checked inert build support.
Test transient/reassertion, staggered debounce, filter-caused loss, contact,
edge/STOP/fault, stale/partial sources, duplicate timestamps, natural wrap,
half-range rejection, full-token mismatch, M0 quantization, delayed receipt,
missing drain, event overflow and untouched profile0. Compile both inert and
configured paths and account for the supplied memory limits. A later offline
analyzer and separate P5 feasibility slice can follow. No physical run, tuning
change, default optimization, capacity reduction or phase gate follows here.
