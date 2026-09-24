# Independent D135 expectations, frozen before implementation-body inspection

Adopted source: D135 in 2aa0ac2e, P5_abort_evidence_contract.md. Reviewer read
pre-D135 public headers and existing app_transaction/robot_scenario/P4 timing
fixture patterns, not production .cpp bodies or another author's D135 tests.
The interrupted preparation wrote no files; the resumed preparation produced
this independent set. No executable or generated build products were created.

## Exact event and cue oracle

Event code 10; eight bytes: little-endian u32 timestamp, u8 type, u8 detail,
little-endian u16 value. P5 batch capacity 21, P4 26, ordinary 21.
Details 0/16/17/18/19/20/21/22/23/24/25 only. Header accepts exactly 0x0201 and
0x0205, with producer's compiled M choice. Read-start/read-end/applied/source/
receipt values exactly 1; handover states exactly 5/6/7; NOT_ABORT/INTERRUPTED
values exactly 1/2; HANDOVER_FAILED states 0..11. P4/default semantics unchanged.

Cue bits are mode[0:2], phase[3:5], cause[6:7], mask[8:14], snapshot[15].
Independent numeric acceptance, exhaustively compared over 65,536 words:

| Mode | Phase | Cause and mask |
|---|---|---|
|3|0|cause1 iff front bits nonzero; cause2 iff no front, any 0x78 bit, no snapshot|
|1,6|1,2,3|cause1 iff phase !=1 and front; cause2 iff 0x50 present and (phase1 or no front)|
|2|1,2,3|same as previous, outer 0x28|
|4,5|2,3|cause1 and front only|
|6|4|cause2 with any 0x78 bit, front allowed|

Snapshot is forbidden outside mode3; inside mode3 it is permitted with current
front only. All other modes/phases/causes/masks invalid. A valid mask does not
prove actual predicate capture, routing or available mode; those are separate.

Expected ordinal projections: success [0,16,17,18,19,20]; wrong handover
[0,16,17,18,25]; receipt failure [0,16,17,18,19,24]; pre-candidate terminal
[0,21|22|23]; captured-cue preemption [0,16,17,18,22]; exhausted pending handover
[0,16,17,18,19,22] with STOP_FAULT only. Every proper unfinished prefix remains
incomplete. Never sort by timestamps; source-read records can be appended later
than earlier decision-stamped ordinary events. Header immediately follows real
START_RELEASE at the same D, GO precedes post-GO cues/terminals. The read pair,
cue and route result are an adjacent TIMING suffix after current ordinary events.
Receipt closure precedes current-decision events and cannot be erased by STOP.

## Public-probe expectations

1. DIRECT saved-front-only is cause3; independent current front is cause1 even
   with saved front; no-front/no-snapshot side is cause2; natural timeout cause4.
   Detection wins a deadline tie. Pulse becomes NONE on repeated terminal/reset.
2. SIDESTEP front in PIVOT is ignored; outer+front is side cause there. Within
   one call, completed PIVOT followed by detected front publishes TRAVERSE phase.
   ARC PIVOT also ignores front; front after advancement qualifies TRAVERSE.
3. SIDESTEP inner side starts TURN_IN without qualified abort. A completed
   TURN_IN with only retained inner side is NATURAL_END despite side exit.
4. WAIT widening starts full SIDESTEP_R with no abort cue. A later outer abort
   carries its inner PIVOT phase; HOLD side carries WAIT_HOLD. Robot packing
   must preserve running WAIT, not rewrite it to SIDESTEP_R.
5. Genuine UI selection and START/hold are used; no mode/state setter. A DIRECT
   current-front cue at GO qualifies before any earlier enabled opener receipt.
   Current front enters TRACK with shipped threshold3 and no contact grant.
   SIDESTEP PIVOT side+front cause still routes TRACK under normal front priority.
6. Gate callback receipts retain full tokens and actual A. Both M variants may
   produce arithmetic diagnostics; only M1 enabled acknowledgement can emit
   ABORT_APPLIED for M1. Disabled/zero M0 is legitimate. Never infer EN from wire.
7. Delays999/1000/1001 remain exact, including natural wrap. First two meet
   inclusive logical bound, last fails arithmetic without being censored.
8. Invalid window, pre-epoch start, future end, reversed interval and half-range
   epoch produce INVALID_SOURCE without changing valid behavior routing. Invalid
   source outranks actual edge for the trace only; actual output remains edge.
9. Changed token high32 bits, missing duration, wrong execution duration and M1
   disabled acknowledgement fail once with INVALID_RECEIPT; later ticks do not
   repair/reopen. A valid prior receipt followed by current STOP closes success.
10. Actual Transaction stores Robot/Gate events. Abort after cue/handover cannot
    synthesize an applied event; retained recording is incomplete. A real next
    completed transaction receives and stores one matching applied event.
11. A full21 batch retains all old events; every attempted valid four-event
    suffix increments rejection (four), never overwrites/rolls back/retries.

## Explicit independent review or mutation obligations

Public Robot cannot directly create missing route, route token mismatch,
pending-tag mismatch, tag-without-RECEIPT, RECEIPT-without-tag, overwrite, or
uint64 exhaustion. Do not label them dynamically covered by ordinary success.
Use source review after this freeze and root-owned bounded isolated mutations
where feasible; source review alone must remain identified as such. No public
test seam or production setter is requested.

Require complementary evidence for actual Runtime opponentsFresh projection;
source T/Rs/Re/D and receipt T/D/A/C/nextT/nextD all below half-range; duplicate
observations; explicit-mode/start-invalid variants; quantization; natural and
snapshot Robot terminals; WAIT zero-duty and contact; pre-cue STOP/edge and final
preemption; reset/end tail; ring saturation/AttemptSummary loss propagation;
disabled modes; no retry; default/P4 exact layouts; profile/admission exclusions;
metadata-only noninterference and no extra persistent token/time/read owner.

Physical origin, PWM pins/mechanics, source-clock qualification, WCET, copied
ABI objects, stack/static RAM/ELF imports/loader and10/10 trials remain external
and unproved. Current model headroom is not a P5 native fit acceptance.

Execution plan: root includes private_spec_probes.cc with existing host sources
and tests includes, exclusive SUMOX_P5_ABORT_TIMING=1 MATCH=0 in both existing
M0 and M1 software variants, serially. Preserve first compiler/test failures
before any adjudication. Changes to this unexecuted draft after the freeze
require a separately retained delta and explanation, never silent oracle repair.
