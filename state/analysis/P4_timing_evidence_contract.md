<!-- Defines D129's bounded P4 target-loss timing evidence. -->
<!-- Keeps source/application observations distinct from physical acceptance. -->
<!-- Independent profile tests and source-bound target review verify this contract. -->
# D129 P4 target-loss trace contract

2026-09-24, selected under D051 and D128. This adopts the P4-only recommendation
in P4_timing_evidence_options.md, with the exact refinements below. No motion,
debounce, source grant, pin, tuning, physical acceptance or phase gate changes.

## Build and public seam

`SUMOX_TIMING_EVIDENCE` is compiler-wide, integer0/1, default0; value1 requires
`SUMOX_P4_REACTIVE=1`. Existing default and D128 profiles remain unchanged.
`RobotResult::TIMING_EVIDENCE_PROFILE` identifies it without object storage.
Only in this profile, `fsm::OpponentReadWindow { bool valid=false;
uint32_t started_us=0, completed_us=0; }` and `RobotInput::opponent_read` carry
the existing validated complete seven-channel acquisition interval. Runtime
copies it only when opponentsFresh accepts the actual Snapshot. No new read,
clock, sequence or fallback timestamp. Direct callers must provide it explicitly.
Trace validation additionally requires explicit valid TickTiming and offsets
0<=read_start<=read_end<=decision from that tick's start, all below half range.
Legacy inputs without explicit source/tick timing remain motion-compatible but
cannot qualify timing evidence. A direct caller using observations_fresh and
legacy line data may qualify when it supplies explicit valid tick/source timing;
explicit LineEvidence is not an additional trace requirement. Actual admitted
sensor freshness remains required, not merely opponent_read.valid.
While ARMED/OBSERVING, the preceding receipt must also supply valid explicit
S/D/A/C epoch chronology and duration_valid, so the current tick start cannot
precede its completion. Failure closes INVALID_SOURCE_TIME independently of
approach eligibility. Pure application-identity faults with valid time retain
STOP_FAULT precedence; the expected loss-receipt phase uses INVALID_RECEIPT.

`bench/reactive_timing` uses the same actual Runtime/NativeSources/UnoQPort,
empty grants and checked inert M0 build route as reactive_test; exact flags add
SUMOX_TIMING_EVIDENCE=1. No upload key or motor-capable checked route is added.
Compile-only remains compile-only. Existing profiles and established tests stay
at option0. Dedicated M0/M1 host targets and new tests exercise the trace.

## Lifetime and precedence

One candidate maximum per actual accepted START attempt. Reset/next accepted
START clears trace state. Emit HEADER immediately after START_RELEASE; all other
current-decision trace events are a suffix after old events. Receipt completion
is emitted during existing receive, before current sampling/events. Duplicate
Robot timestamps retain no-pulse behavior. Never replay or retry a closed trial.

After real GO, arm only on valid fresh source evidence, current selected ATTACK
approach without committed contact, both raw and effective front present, and
a genuine immediately preceding ATTACK/no-contact receipt with EN enabled and
both actual duties >0. That receipt must pass existing full identity/duty checks
and explicit S/D/A/C timing with duration_valid. Record its prior committed
contact separately from the newly committed contact; requested duty is no proof.

The first later valid fresh all-raw-front-clear observation consumes the sole
candidate. Logical raw front is `(opp_raw_mask ^ OPP_ACTIVE_LOW_MASK) & 7`.
Retain S/E exactly, emit adjacent START/END records, and recheck the immediately
preceding receipt's ATTACK/no-contact/enabled/both-positive conditions at onset.
If those have ceased to hold, close EXCLUDED_NO_APPROACH after the pair. Do not
move the origin to a later favorable clear. M0 real Gate zeros cannot arm.

While armed or observing a candidate, evaluate current exclusions in this order:
invalid/stale/incomplete source or ambiguous common-anchor time (10), actual
edge preemption/escape fault (8), STOP/contract fault/lost permission (9), front
stuck fault or actual phantom removal of front bits (6), contact or unrelated
route other than ATTACK/TRACK/eligible loss SEARCH/DEFEND (7). In an active
candidate, any raw front reassertion then closes TRANSIENT (5). An armed trial
can close before its source pair; such an exclusion is diagnostic, never a pass.
Side/rear stuck alone and an inactive/nonmasking phantom marker do not exclude.
Staggered debounce may enter TRACK without canceling. Trace errors never modify
outputs, counters, source qualification, behavior state, or governor permission.

Capture actual `NormalResult.brake` caused by front loss, excluding deferred
edge exit or other forced brakes. Require confirmed unsuppressed front zero and
final valid SEARCH/DEFEND selection, brake request, enabled permission and exact
zero governed duties. Retain its complete64-bit request token only after final
arbitration/governor succeeds. Emit LOSS_BRAKE_DECISION at D. No reconstructed
state-change trigger and no truncation of the expected token.

The immediately following receipt either completes with LOSS_ZERO_APPLIED at
actual A or closes INVALID_RECEIPT at the receipt-observation decision. Require
full expected token==pending token==receipt token, existing duty/application
checks, explicit valid S/D/A/C with duration_valid, enabled EN and exact finite
zero duties. Also S<=E<=D<=A<=current decision, all offsets from S below half
range. Do not borrow a later zero. A valid prior receipt completes before a new
tick's edge/STOP/reassertion; those cannot retroactively erase it. Missing tail,
reset/Transaction abort may leave an open candidate: report incomplete offline,
never synthesize a completion. Actual late valid zero remains a measured delay;
no artificial35ms cutoff or retry.

Token exhaustion processes a prior receipt first using the same checks; then
an armed/open trace closes INTERRUPTED_STOP_FAULT in the terminal result without
starting a new candidate. No terminal success may be retroactively canceled.

## Wire format and bounded cost

Only this profile accepts `core::Event::TIMING=10`; codes0..9 unchanged. The
eight-byte encoding and CSV schema stay unchanged. Default codec still rejects
10..255. `logframe::TimingDetail` has the following explicit values:

| detail | name | time | value |
|---:|---|---|---:|
|0|HEADER|accepted START decision|0x0101 M0 or0x0105 M1|
|1|LOSS_READ_START|S|1|
|2|LOSS_READ_END|E|1|
|3|LOSS_BRAKE_DECISION|D|1|
|4|LOSS_ZERO_APPLIED|A|1|
|5|EXCLUDED_TRANSIENT|current decision|1|
|6|EXCLUDED_FILTER|current decision|1|
|7|EXCLUDED_CONTACT_ROUTE|current decision|1|
|8|INTERRUPTED_EDGE|current decision|1|
|9|INTERRUPTED_STOP_FAULT|current decision|1|
|10|INVALID_SOURCE_TIME|current decision|1|
|11|INVALID_RECEIPT|receipt observation decision|1|
|12|EXCLUDED_NO_APPROACH|current decision|1|

Header metadata accepts either exact version/profile value when validating a
record; a producer emits its own compiled M value. All other known subtypes
require value1; all unknown/reserved combinations rejected by metadata validation
(validEventMetadata/appendEvent). packEvent retains its existing enum-only check. Wire ID1 is not a
transaction token. Source timestamps can precede earlier-in-ordinal decision
events; preserve ordinal order and pair named fields, never numeric time sort.

Instrumented ROBOT_EVENT_CAPACITY=26, default21. Review the conservative source
bound (at most22legacy plus4trace), including all11 current fault categories;
retain explicit batch rejection/loss accounting even if the bound is violated.
At most5 trace records per attempt: header, pair, decision, receipt/rejection;
or fewer for exclusions. Recorder remains first4096 and25Hz/200s, no reduction.
EventBatch holds EventInput objects (actual padding must be measured); eight-byte
wire cost does not imply eight-byte in-memory cost. Measure all conditional
layout/native loader consequences. Default known modeled free16bytes forbids
unconditional growth; P4 previously had6512bytes conditional modeled span.

## Interpretation and validation

Metric is first observed all-front-raw-clear acquisition to matched applied-zero
receipt completion, interval[A-E,A-S]. It proves neither physical box-removal
instant nor first electrical transition nor mechanical rest. At current defaults
bound=35000us inclusive: PASS upper<=bound, FAIL lower>bound, INDETERMINATE straddle.
Missing required/closed/lossfree evidence INCOMPLETE; exclusions EXCLUDED; header
only NOT_EXERCISED; no header NOT_RECORDED; contradictory grammar/time INVALID.
M0/synthetic arithmetic never physical acceptance. Offline analyzer follows as a
separate task using unchanged CSV validator and hash-bound rereads.

Independent spec/public-header tests precede implementation execution. Cover
normal/search and side/defend loss, exact timestamps, wrap, full64-bit mismatch,
stale/partial/backward/half-range source, explicit timing/receipt failures,
quantization/M0, transient/no retry, contact/filter/edge/STOP, staggered debounce,
duplicates, missing tail, new attempts/reset, actual Runtime source projection,
codec metadata/batch/ring overflow, and unchanged prior profiles/locked tests.
No existing locked assertion may change. Target compile and loader fit are
separate evidence; live RAM/stack/full-source WCET and physicalP4.2 stay pending.
