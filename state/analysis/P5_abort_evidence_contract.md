# D135 P5.3 qualified-abort evidence contract

**ADOPTED for bounded software preparation under D051**,2026-09-24. The final
proposal c6314c04 is preserved in4dc72ac1 and passes separate same-model design
review. D134 regression remains in progress; implementation must wait for that
frozen-source validation to finish. Independent spec-only test preparation may
proceed in isolated draft files. Active software phase remains P5. This decision
does not establish native fit, a hardware grant, physical acceptance or a gate.
The proposed forms below are the adopted interface/semantic contract; no code
or execution follows merely from adoption.

## Scope and claim

Observe one qualified logical opener abort per actual accepted START attempt,
using the existing Robot -> MotorGate receipt -> AttemptRecorder path. Require
both same-observation reactive handover and conservative application completion
`A - D <= config::TICK_US`, inclusive. D is the existing decision-entry clock;
A is the matching MotorGate transaction-completion clock. At shipped settings
the bound is1000us. Preserve actual late values; do not stop measuring at1000us.

This measures qualified-observation routing and completion after decision entry.
It does not date physical box appearance, the first electrical transition,
internal branch execution, PWM edges or mechanical response. Qualification
happens during Robot computation after D, so A-D is a conservative upper bound
from that internal qualification. Same D on two markers means the same logical
observation, not zero CPU work. Source-read bounds explain the input's age but
are not the acceptance origin.25Hz frames and60fps video cannot prove this bound.

Actual10/10 physical trials per tested opener remain required by P5.3. M0,
synthetic and host timing are diagnostics only. D034/D134 still route current
front through ordinary centering qualification, side/rear to DEFEND_TURN and
no target to SEARCH. No immediate-ATTACK exception or motor authority is added.

## Exact opt-in profile and public observations

Propose compiler-wide `SUMOX_P5_ABORT_TIMING`, default0, integer0/1 only.
Value1 requires MATCH=0 and every existing B4/P3/P4/`SUMOX_TIMING_EVIDENCE`
profile0. MOTORS_ALLOWED remains its existing independent0/1 setting; dedicated
host fixtures exercise both values. D129's existing requirement that
SUMOX_TIMING_EVIDENCE requires P4 reactive stays unchanged.

The proposed named `bench/opener_timing` wrapper uses actual NativeSources,
UnoQPort and Runtime with empty SetupGrants, normal available-mode selection,
full hold and existing openers. Its sole checked native route is default startup,
compile-only with exactly:

`-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1`

Use the existing board_tool/app_build_policy path; reject uploads, MATCH,
Immediate, conflicting profiles and source-local overrides. Add no source key,
true grant or receipt exception. Physical M1 deployment/setup remains a later
identified authorized run; this M0 wrapper cannot supply it.

`RobotResult::OPENER_TIMING_PROFILE` reports this profile without storage.
Keep the existing TIMING_EVIDENCE_PROFILE meaning P4. Extend the conditional
OpponentReadWindow projection to either exclusive evidence profile, preserving
its existing valid/start/end fields and Runtime::opponentsFresh checks.

For P5 only, propose this per-call observational member on both `openers::Result`
and `FlankResult` (WaitResult already contains FlankResult):

```cpp
enum class AbortPhase : std::uint8_t {
    DIRECT = 0, PIVOT = 1, TRAVERSE = 2, TURN_IN = 3, WAIT_HOLD = 4
};
enum class AbortCause : std::uint8_t {
    NONE = 0, CURRENT_FRONT = 1, CURRENT_SIDE_OR_REAR = 2,
    SNAPSHOT_ONLY = 3, NATURAL_END = 4
};
struct AbortEvidence {
    AbortPhase phase = AbortPhase::DIRECT;
    AbortCause cause = AbortCause::NONE;
    std::uint8_t effective_mask = 0;
    bool snapshot_front_present = false;
};
// Result / FlankResult, only under SUMOX_P5_ABORT_TIMING:
AbortEvidence abort;
```

This is a pulse for the current call. Inactive, reset and repeated terminal
steps return cause NONE; duplicates cannot replay it. It never changes motion.
No public mode setter, generic observer callback or new controller is needed.

## Predicate capture and handover are independent observations

Capture CURRENT_* at the actual production abort-predicate branch, **before**
terminal phase mutation/return and before Robot routing. Preserve the effective
mask consumed there and phase at that evaluation. Do not re-run Fusion, the
opener or its decision rules. Existing hooks are Direct::step current detection,
Flank::step immediately after detectExit returns a detection, and Wait::step's
HOLD side/rear branch (`openers.cpp:31-45,186-193,283-297`).

Direct FRONT_TARGET from saved front alone is SNAPSHOT_ONLY; current front
qualifying independently is CURRENT_FRONT even if the snapshot also has front.
Natural completion, including a terminal timeout without a detection, is
NATURAL_END even when currentTarget returns FRONT_TARGET/SIDE_OR_REAR_TARGET.
A primitive timeout that continues the opener is not NATURAL_END. Current
detection winning a deadline tie retains CURRENT_*. Invalid scripts produce
the existing fault, never a qualified cue.

Flank can advance phases in one call. Record the phase where its predicate
became true, not the initial or terminal phase. SIDESTEP PIVOT ignores front
but can abort on outer side/rear; DRIVE/TURN_IN gives front D033 priority. ARC
PIVOT ignores detections; inner-side traversal cues start TURN_IN, not reactive
handover. WAIT's D055 widening cue starts complete SIDESTEP_R and is not an
abort. Its eventual inner Flank abort retains running mode WAIT and inner phase.

Robot first captures the cue/token from the returned evidence, independently
of the result.exit test. Its existing Direct branch or acceptFlank then records
whether it actually invoked routeNormal(true) for that same request token
(`fsm_robot.cpp:567-599`). After final arbitration/governor, compare that fact
and actual final state to normal routing from the cue's effective mask. Never
emit a successful handover merely because a cue was emitted.

Front priority in normal routing still applies even when the triggering cause
was side/rear in a phase that ignored front. For shipped ATTACK_ENTER_TICKS=3,
a current-front handover is TRACK; without front, the qualified side/rear
handover is DEFEND_TURN. If a separately source-bound configuration permits
ATTACK on the first centered observation, accept it only when existing normal
qualification actually permits it. Do not change the threshold to obtain a
trace. SEARCH is a valid snapshot/natural exit, not a CURRENT_* success here.

Missing routing, an incorrect final state, or a different request token emits
HANDOVER_FAILED on this decision. Do not downgrade these to NOT_EXERCISED or
wait for a later favorable route. Predicate-capture-only instrumentation cannot
independently prove its own predicate implementation; the published mask/phase
must satisfy the independent table below, and frozen behavioral tests must
cover missed predicates. A run with no qualified cue can never pass P5.3.

## Attempt lifetime, source chronology and priority

Header is emitted immediately after actual START_RELEASE at that timestamp.
Clear trace state at accepted START and reset; wait for real GO/permission, then
observe only the current opener. One qualified candidate or terminal diagnostic
consumes the attempt's trace. Never reopen or silently retry. A fresh current
DIRECT cue on GO is permitted; no prior OPENER/positive-duty receipt is required.
WAIT HOLD zero duty and genuine contact are not blanket exclusions.

Every candidate needs fresh admitted perception and the existing valid complete
OpponentReadWindow in explicit TickTiming. For its epoch T/read R_s,R_e/decision D:

`0 <= R_s-T <= R_e-T <= D-T < 0x80000000`

Use unsigned common-anchor offsets; also require a valid preceding pending
receipt's completion <= current T, through existing explicit chronology checks.
The actual Runtime supplies these values; direct tests must supply them honestly.
No synthetic timing fallback or backdated source interval is allowed.

During post-GO waiting or qualification, evidence classification priority is:
invalid/stale source or ambiguous chronology -> INVALID_SOURCE; actual edge
preemption/escape fault -> INTERRUPTED(EDGE); STOP/contract fault/lost permission
-> INTERRUPTED(STOP_FAULT). These are evidence dispositions only; existing B2
already determines outputs. Snapshot-only and natural terminal exits then emit
NOT_ABORT. Do not add raw-white/contact/phantom policies from D129: this trace
observes actual B12 effective perception and actual preemption, not P4 approach.

Once routing succeeds, tag the existing Pending transaction as this attempt's
abort handover. Pending already retains the **full64-bit** token, D, T, timing
validity and final request (`fsm.h:568-582`); do not copy these into a second
trace. The tag is set only while savePending captures the exact same token
whose cue and actual route were compared, and cannot attach to a later request.
The immediately following receipt must:

- Match receipt token to that tagged Pending's full token and pass
  existing application/duty/EN validation. Retain legitimate PWM quantization;
  P5 neither requires zero duty nor treats requested duty as applied evidence.
- Have duration_valid and valid explicit T/D/A/C chronology; require
  `T <= R_s <= R_e <= D <= A <= C <= next T <= next D`, offsets below half range,
  and execution_us == C-T. Existing pending request must still identify this
  handover. Its earlier read interval has already passed the same T-to-D check;
  do not retain or reconstruct another read interval for this receipt. In M1,
  acknowledged EN=true is a mandatory producer condition for ABORT_APPLIED;
  EN=false always emits INVALID_RECEIPT. This check cannot be deferred to an
  offline physical-qualification rule because the wire does not carry EN.
  An M0 disabled/zero Gate receipt may close a diagnostic trace only.

The pending tag and attempt RECEIPT phase are a coupled state: neither alone
permits success. receive must consume/close them before existing pending.valid
is cleared or another savePending can replace its owner. A missing/mismatched
tag, unexpected overwrite or lost pending owner is incomplete/invalid evidence,
never permission to associate the next receipt. Failure emits INVALID_RECEIPT;
no later receipt may repair it. Success records
actual A, including delays greater than TICK_US. Receive/close the previous
receipt before current-tick sampling/preemption, as Robot already does; later
edge/STOP cannot erase a completed measurement. Reset, Transaction abort or
missing tail leaves incomplete evidence unless an existing observed terminal
can truthfully emit a diagnostic. Token exhaustion processes the prior receipt
first, then closes any uncompleted post-GO trace as STOP_FAULT without success.
No fake application acknowledgement is generated by halt, reset or the trace.

## Exact compact event grammar

Reuse Event::TIMING numeric10 and existing8-byte EventInput wire encoding only
when either exclusive evidence profile is enabled. Default rejects10 as before.
P4's metadata/header acceptance remains byte-for-byte unchanged. P5 metadata
accepts only the following table; unknown details/values are rejected. Existing
codes0..9, recorder buffers, CSV schema and transport bytes are unchanged.

| Detail | Meaning | Timestamp | Value |
|---:|---|---|---|
|0|P5_HEADER|accepted START D|0x0201 for M0,0x0205 for M1|
|16|ABORT_READ_START|R_s|1|
|17|ABORT_READ_END|R_e|1|
|18|ABORT_QUALIFIED|D|packed cue below|
|19|ABORT_HANDOVER|same D|actual state5 TRACK,6 ATTACK or7 DEFEND_TURN|
|20|ABORT_APPLIED|A|1|
|21|NOT_ABORT|current D|1 snapshot-only,2 natural terminal end|
|22|INTERRUPTED|current D|1 actual edge/escape fault,2 STOP/fault/lost permission|
|23|INVALID_SOURCE|current D|1|
|24|INVALID_RECEIPT|receipt-observation D|1|
|25|HANDOVER_FAILED|cue D|actual final state code0..11|

P5_HEADER identifies this exact grammar, not a D129 version upgrade. Codec
validation in a P5 build may accept either exact M variant for reading, but the
producer emits its own compiled M. P5_BUILD rejects P4 detail/header combinations;
P4_BUILD still rejects P5 combinations. General CSV validation preserves raw
unknown codes, as before; it does not certify P5 semantics. D130's target-loss
analyzer keeps rejecting P5 headers/details instead of scoring them as loss data.

QUALIFIED packs all16 value bits: mode in bits0..2; AbortPhase in3..5;
CURRENT_FRONT=1 or CURRENT_SIDE_OR_REAR=2 in6..7; effective7-bit mask in8..14;
snapshot_front_present in15. Mode must equal the attempt's captured1..6 ID.
The independent metadata table is:

| Running mode / phase | Permitted CURRENT_* cause |
|---|---|
|DIRECT / DIRECT|Front if mask&7 !=0; side/rear only if front==0, mask&0x78 !=0 and snapshot flag false. Snapshot flag otherwise allowed only with current front.|
|SIDESTEP_R / PIVOT,TRAVERSE,TURN_IN|Front only outside PIVOT with mask&7 !=0; side/rear if mask&0x50 !=0 and either PIVOT or no front.|
|SIDESTEP_L / PIVOT,TRAVERSE,TURN_IN|Same rule, outer mask0x28.|
|ARC_R or ARC_L / TRAVERSE,TURN_IN|Current front only, mask&7 !=0.|
|WAIT / WAIT_HOLD|Side/rear if mask&0x78 !=0; front may coexist.|
|WAIT / PIVOT,TRAVERSE,TURN_IN|Same as SIDESTEP_R, preserving running mode6.|

Snapshot flag is false outside DIRECT; every unlisted combination is invalid.
This table validates evidence, not a second motion-policy execution. Availability
still comes from D134 and is checked against the source-bound trial config.

Ignoring ordinary non-TIMING events but preserving their ordinal positions:

- Success: `[0,16,17,18,19,20]`.
- Missing/wrong handover: `[0,16,17,18,25]`.
- Receipt failure: `[0,16,17,18,19,24]`.
- Pre-candidate terminal: `[0,21]`, `[0,22]` or `[0,23]`.
- Final preemption after a captured cue: `[0,16,17,18,22]`.
- Token exhaustion after a handover without valid closure:
  `[0,16,17,18,19,22]`, only STOP_FAULT.
- A valid unfinished prefix is INCOMPLETE, never implicitly successful.

Header must immediately follow START_RELEASE with matching timestamp; GO must
precede cue/terminal post-GO records. Snapshot/natural/priority diagnostics are
not qualified trials. Emit read pair, cue and handover/failure as an adjacent
TIMING suffix after ordinary current-decision events. Receipt result is emitted
during existing receive, before current events. Acquisition times may precede
earlier decision-stamped ordinals: never reorder records by raw timestamp.
Value1 is a single-candidate wire marker, not a truncated token. The wire carries
R_s, R_e, D and A; it omits T, C, next T, full64-bit token and acknowledged EN.
Full epoch chronology, transaction identity and M1 enabled application are
producer-enforced and supported by source-bound tests. They cannot independently
be reconstructed from this event stream. Keep that evidence limitation explicit.

## Bounded storage and noninterference

At most six trace records per attempt:48 raw wire bytes, with no per-tick stream.
Keep P5 ROBOT_EVENT_CAPACITY at the existing default21; P4 alone retains26.
There can be four new events in a qualification decision. The conservative
legacy bound plus those events does not prove universal loss-free fit at21.
Accept that bounded evidence limitation explicitly: use unchanged appendEvent
prefix retention, rejection/invalid counters, recorder loss propagation and
offline disqualification. Never overwrite old events, prioritize a successful
trace over ordinary events, roll back a partial suffix, defer/retry rejected
records or silently reopen the attempt. Attempt every specified append so loss
remains counted; a visible success suffix does not override any attempt loss.
Receipt events retain their specified chronology and may share a batch with
later ordinary events. Independent tests must prove both loss-free representative
abort batches and adversarial saturated batches that remain nonqualifying.

Use existing Pending ownership as specified above, plus a conditional attempt
phase and pending handover tag. No separate persistent token/timestamp copy is
needed for P5. Keep cause/phase result pulses and any current-tick route marker
conditional. Mutually exclusive P4/P5 tracing must not create two trace owners.
Do not overlay live opener state or recorder payload/status/counters: the
opener, pending request and recorder can coexist in this profile. Only reuse
storage whose lifetimes are demonstrably exclusive, with independent ownership
tests; that is not permission for a new storage framework or aliasing trick.
Do not add a second recorder, increase4096 event capacity, reduce5001 frame
capacity or change25Hz cadence. Default and existing P4 object layouts and
public behavior must remain unchanged.

The historical default had only16 modeled bytes; P4's old6512-byte margin
excluded openers and cannot qualify P5. Even this reduced design adds source
window/input copies and conditional pulse/tag/phase fields, so native fit must
be treated as unresolved and may fail. Do not describe the instrumentation as
target-ready merely because host behavior is correct. An adoption can authorize
bounded software preparation while explicitly retaining this target-realization
limitation. Before claiming a deployable native artifact, report measured ABI
padding, all copied RobotInput/RobotResult/Transaction instances, static RAM,
stack allowance, ELF/imports and loader fit. If it does not fit without changing
the fixed capacities/semantics, report the exact deficit and seek a separate
bounded storage decision; do not silently trade away B15/B16 or ordinary openers.

Trace failure may affect its own diagnostic/loss status only. It must not change
source admission, phase progression, routing, timing gains, contact, stall,
Governor, MotorGate, physical grants or startup. No allocation, new I/O/clock,
unbounded loop or second evaluation of a behavior. With identical behavior inputs
and receipts, enabling the trace or changing only its read-window metadata must
not change outputs. Real source/receipt failures retain their existing safety
effect independently of the trace.

## Acceptance, independent tests and unresolved external dependencies

An offline interpretation must bind the CSV attempt/ordinal stream to its exact
source/config/profile and validate the wire endpoint timestamps, ordinal grammar,
mode/cue table, owner closure and loss counters. It can check R_s <= R_e <= D <= A
using unsigned offsets from R_s below half range, and equal qualified/handover D.
The full T/R_s/R_e/D/A/C/next-T chronology, same-token route/receipt identity and
M1 EN check are producer-enforced, source-bound claims; offline analysis cannot
reconstruct the omitted fields or independently prove those claims. COMPLETE
has wire-derived elapsed `(A-D)`. Report arithmetic PASS if <=TICK_US and FAIL
if greater; HANDOVER_FAILED is a logical FAIL. Unknown grammar/wire time is
INVALID; excluded, missing, interrupted or loss-bearing evidence cannot qualify.
Do not infer TICK_US/ATTACK_ENTER_TICKS from today's config for historical data.
M0 may retain arithmetic diagnostics but is never physical PASS.

Freeze independently authored public-header/spec tests before implementation
execution, including:

1. Exact default/P4 layouts, flag exclusions, profile/header constants, unchanged
   D129 metadata/grammar, copied-config identities and compile-only/upload guards.
2. Every permitted mode/phase/cause combination and rejected combinations;
   phase advancement within a call, ignored PIVOT front, held effective targets,
   snapshot-only versus current-front, front/outer ties, natural completions,
   detection/deadline ties, WAIT cue versus its later abort, disabled modes.
3. Actual Robot/Runtime read-window projection, GO-time DIRECT, WAIT zero duty,
   current front/side precedence, D034 centered qualification and unchanged motor
   requests. Cue without route, wrong state and wrong token cannot pass.
4. Full64-bit identity mismatch, PWM quantization, M0/M1, 999/1000/1001us,
   valid late application, wraps/half-range/contradictory epochs, stale/partial
   reads, tagged-Pending/phase coupling and replacement prevention, duplicate
   calls, missing tail, reset, Transaction abort and exhaustion.
5. Edge/STOP before cue, final preemption, valid prior receipt before new-tick
   interruption, all allowed terminal prefixes, malformed batches/ring overflow,
   recording loss and no retry. No P4 no-contact/positive-wheel/zero-duty rule.
6. Independent normal/sanitizer configured host tests, unchanged protected/default
   regressions, source review and checked native M0 compile/loader audit. Verify
   actual profile RAM/stack/full-tick timing separately when hardware is available.

This producer contract does not introduce a new analyzer CLI/framework. A small
P5 grammar/elapsed interpreter using the existing CSV validator may be specified
as the next bounded task; D130's P4 analyzer is not silently repurposed. Retain
all physical trial attempts and original failures/exclusions; no favorable
replacement or ten-host-case substitute satisfies physical10/10.

**Unresolved outside adoption:** the exact physical source/grant/M1 deployment
and clock-qualification evidence, live recorder extraction, target fit and
actual trials remain pending. This proposal deliberately has no upload/run
grant. If later acceptance requires latency from physical appearance or an
electrical transition, that is a different externally measured origin and must
be specified separately; it is not supplied by this logical-abort contract.
The profile, grammar and logical elapsed metric are now the adopted software
contract; target realization and physical acceptance remain explicitly pending.
