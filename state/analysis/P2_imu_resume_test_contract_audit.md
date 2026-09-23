# Independent public-spec audit: resumable runtime IMU

2026-09-23 Asia/Dubai. Baseline requested: `2f0981c`. Scope is a contract and
test-author audit only, under D051/D075. Only this new note was modified. No
production CPP body was read, no tests or hardware commands were run, and no
contract, config, old test, ledger, phase gate or implementation was changed.
The local date is Wednesday 23 September, matching the original PLAN schedule's
P0/P1 day; the active P2 software exception is documented, not a passed gate.

Sources: AGENTS.md, `.claude/agents/test-author.md`, current handoff/progress,
D079/D080/D081/D082/D084 public contracts and headers, the applicable DECISIONS,
FACTS, HARDWARE, BEHAVIOR B3/B14 and P2 prompt, and
`P2_app_schedule_dependencies.md`. Existing independent acquisition tests were
read for their established assertions. Implementation line references appearing
inside the dependency note were not followed. Native peripheral yield legality
is being checked independently; this audit makes no clock-stretch claim.

## Required invariants

- Preserve the synchronous public APIs, their legal idle-call semantics, all
  established assertions, setup's one-operation-per-advance lifecycle and the
  irreversible Bus claim. Runtime resume is a separate additive path on the
  actual owned Bus and Acquirer, not an app wrapper around a blocking call.
- Exactly one readiness read, complete STOP/idle/final checks, then at most one
  15-byte INT_STATUS/motion read. Readiness zero alone gives completed NO_NEW.
  A consumed readiness event cannot be retried after a failed/cancelled burst.
- One original 600 us exclusive wall-clock budget and 8192 shared poll budget
  span every phase and caller interleave. Equality rejects. One separate existing
  50 us/8192 cleanup allowance may run on the terminal path. No resume resets a
  start, counter, silence anchor or cleanup allowance.
- Partial bytes remain private. Pending has no Sample/Estimate observation,
  calibration reading, yaw increment, source-time refresh or accepted sequence.
- Faults remain terminal; lost ownership stays lost for cleanup purposes even
  if a later snapshot coincidentally matches. Cleanup remains local PE disable,
  not STOP synthesis, reset, recovery, line pulses, reenable or ownership release.
- Completed source/phase times remain actual bus observations. Caller resume or
  later delivery time cannot replace the successful final acquisition time.
  Diagnostic transfer completion still excludes cleanup; an outer D092 clock
  bracket must include cleanup and every executed advance.

## Minimal result and lifecycle proposal to freeze before tests

The following is a recommendation, not an adopted API. Exact spelling may differ.
Use a separate wrapper for `BusAcquisition` and for `Sample`, with a progress enum
`IDLE`, `PENDING`, `COMPLETE`, `REFUSED`. Only COMPLETE contains a result to consume.
All other states contain canonical empty/default payload. REFUSED reports a
separate reason such as ACTIVE; it must not look like a transport fault or sample.
This avoids extending SampleState and changing Estimator/adapter semantics.

Expose runtime begin/advance/cancel on both owners. A begin either starts one
operation or returns an immediate lifecycle/validation result. A second begin
while active returns REFUSED/ACTIVE without clock/native access, state mutation,
new deadline, hidden completion or cleanup. Advance while idle returns IDLE with
no access. A successful/failing/cancelled operation produces COMPLETE exactly
once; subsequent advance/cancel returns IDLE. A retained terminal fault can still
be returned by a later begin, as a new refused attempt, without native access;
it must not republish a prior successful sample. Define that distinction in the
frozen header rather than leaving callers to infer it from payload equality.

Completed success allows the next begin. Terminal transport/cancel/silence/time
fault does not. No destructor I/O or recovery API is added. The caller must finish
or explicitly cancel a pending operation before discarding its owner; destruction
cannot silently promise safe cancellation. There is no background watchdog:
deadline/silence expiry is observed only when the owner is called again.

Legacy methods while runtime work is active need explicit new-domain semantics:

| Collision | Recommended contract |
|---|---|
| Bus `begin()` | Preserve ALREADY_STARTED/no access; it cannot restart runtime work. |
| Bus malformed read/write | Preserve INVALID_REQUEST/no access without touching the active operation. |
| Bus supported read/write/readMotion/acquireMotion | Return a new nonterminal BUSY/ACTIVE refusal, zero bytes/count, incomplete, no native/time access; pending state and budget remain intact. |
| Acquirer `read(now)` while active | Prefer explicit terminal misuse: cancel once, return a newly named lifecycle/cancellation SampleFault, and latch. Existing Sample has no honest nonterminal BUSY representation. Do not return NOT_READY/NO_NEW, consume the hidden result, or run an implicit blocking drain. |
| Acquirer start/advanceSetup after profile-ready | Preserve D080/D081 existing no-op/report behavior, never reset runtime state. |

The Acquirer collision choice is deliberately different from Bus's typed refusal:
Sample is already the semantic source envelope. An alternative is a newly named
nonterminal refusal SampleState, but that requires an explicit D082/D084 amendment
and expands scope. The root must choose before test authoring; neither alternative
is inferred from the old API.

## Work bound, time and cancellation choices

Select a fixed public work unit per advance, ideally one finite state-machine
step with at most one checked native progress observation and at most one
associated transmit/receive/command action. No wait-until-ready loop and no loop
over all remaining bytes. The audit cannot freeze hardware-safe state splits;
the primary/installed-source audit must identify those boundaries first.
List the maximum script for each step, including admission/final acceptance.
One cleanup is the documented exception to the ordinary step, and retains its
existing separate bounded polling loop. A fixed operation count is not measured
microsecond WCET or permission to fit it inside QTR's release interval.

The frozen contract must state whether begin only arms/records its original
micros time or also performs the first bounded admission step. Either can be
tested; it must not postpone the deadline anchor until a later advance. Progress
must recheck elapsed time, ownership and native errors before issuing the next
command. Native progress becoming ready during a yield cannot excuse an expired
deadline. Exact poll accounting, including readiness, transition and final checks,
must be documented so a frozen-clock test can prove one total counter rather
than merely eventual failure.

Active cancel is terminal even before receiving a byte: return a distinct
CANCELLED cause, zero payload and the one cleanup result. Preserve already valid
readiness/motion-attempt diagnostics. It never emits success or NO_NEW. Idle and
post-terminal cancel do no native/time access and no repeated cleanup. Root must
freeze cancellation versus simultaneously observable native error/timeout
precedence; safest explicit choice is check monotonic/deadline/ownership/error
first, retain that causal failure, and otherwise report CANCELLED. Never invent
error flags that were not safely observed.

Acquirer begin and every active advance must validate caller half-range chronology
and observed silence, before allowing additional bus work. Private service time
may advance for these checks; it is not a new sample checked/source time. Keep
the D081 anchor at setup completion, then only accepted observation completion.
At observed elapsed >=20000 us, terminal SILENCE; a pending native operation
must be cancelled/cleaned once, not abandoned. A backward/ambiguous caller time
also terminally faults and ends active ownership without using that bad timestamp
as a validated checked time. If the accepted final bus time itself reaches20ms,
the result is SILENCE even when begin/resume caller time was still below20ms.
Retain actual native diagnostics from cancellation separately from the Acquirer
semantic cause. Freeze precedence where both600us expiry and20ms silence are
observable on the same resume; do not leave it dependent on implementation order.

Final response validation must compare Bus started_us with the original begin
call, not the later resume call. Require the accepted final time to follow all
validated active caller observations and lie inside the original interval.
Retain existing D081 phase/shape checks, sequence increment only after all checks,
and real observation-gap calculation. Unknown progress codes and malformed
pending/terminal envelopes are RESPONSE with terminal cleanup if still active.

## Pending delivery to heading and Robot

For this narrow slice, consume only COMPLETE Samples through Estimator exactly
once. Do not manufacture NO_NEW merely to age it; genuine NO_NEW requires a
completed readiness transaction. Estimator report() is a snapshot and calling it
does not age, integrate or create a measurement. The next real sample retains
D082's original <=2000 us continuity rule, including faults after longer gaps.

For future app composition, a pending tick can explicitly carry ABSENT/unavailable
through D084 while retaining internal source history. Bounded retained heading
is also possible only from an already admitted source with its original checked,
observation, sequence and yaw, canonical zero fresh gyro/accel, and updated=false;
Robot still validates current decision age and accumulated age. Re-presenting an
unchanged fresh report is suppressed by Robot only if that exact identity was
already admitted. It is unsafe to assume this after a dropped delivery. Select
one explicit app-owner policy later; this driver slice must not silently mutate
Estimator or forge checked_us to solve app scheduling.

## Independent additive test matrix

Native tests can reuse existing public fixture operations in new files only;
Acquirer tests should link actual Setup/Acquirer to a separately scripted Bus.
No production implementation is a test oracle. Keep old fixture assertions and
established test sources unchanged; add helpers or separate executables as needed.

1. **Lifecycle:** constructor/destructor inert; pre-init/pre-profile calls;
   idle advance/cancel; first begin; duplicate begin; each legacy collision;
   success then new begin; exactly one terminal delivery; fault/no-I/O latch;
   consumed irreversible boot claim survives cancellation and destruction.
2. **Bounded protocol:** hold every supported native wait state unready, call
   one advance, and assert it returns with the documented finite operation bound.
   Resume across every TXIS/TC/RXNE/STOP boundary; first STOP-clear/idle must
   precede second admission, bytes/status/order and final RXNE+STOP stay exact.
3. **Truthfulness:** every pending/idle/refused result has no payload/new sample;
   readiness0 returns exactly one NO_NEW and no motion; status1 with equal
   numeric data still produces distinct accepted observations; second status0/1
   gives exactly one observation, every other status bit faults with diagnostics.
4. **Global budgets:** externally advance fixture time between service calls;
   success at599us, fault at600/601us, including uint32 wrap and between the two
   transactions; no restart after duplicate begin. Frozen time with many advances
   reaches one total8192 limit across both phases; no byte/step counter restart.
5. **Faults after yield:** inject every established native error, unexpected flag,
   ownership loss, stale event, missing STOP, excess byte and ignored command at
   all newly exposed boundaries. No later command after observed failure; correct
   error priority, zero payload, one cleanup, no reacquisition after owner loss.
6. **Cancel:** cancel at every yield phase, including after readiness consumed,
   all bytes staged and before final acceptance. One disable attempt; cleanup
  49us succeeds/50us unconfirmed, frozen cleanup count bound, ownership lost
  means no write. Repeated cancel/advance/legacy fault calls cannot clean twice.
7. **Acquirer silence/time:** begin/advance/final completion at19999/20000/20001us
   from setup and last accepted source, NO_NEW does not extend anchor; backwards,
   half-range and wrap; pending semantic abort cancels once; selected fault
  precedence; retained sequence/last validated time and all failed motion zero.
8. **Acquirer response integrity:** malformed progress/state/status/phase/count,
   partial terminal bytes, changing start across resumes, final time before last
   validated call, delayed result delivery. The original begin is the transfer
  admission anchor; a later advance does not become the source start or sample.
9. **Heading/Robot composition:** completed Sample consumed once; many pending
  advances create no extra bias reading/integration/impact evidence. Source time
  and sequence unchanged while pending; next accepted source preserves actual
  gap;2000us continuity allowed/2001us fault; delayed Robot age cannot be refreshed.
10. **Interleaved schedule demonstration:** scripted QTR charge release in
  [11,100)us while IMU remains pending, then resume to the same acquisition result.
  Every advance/QTR call/cleanup lies inside an actual D092 S..C receipt; elapsed
  interleaved time counts toward600us. This proves only software ordering, not
  physical QTR classification, native step WCET, full800us or healthy800Hz.

Also retain both host motor configurations, no-allocation checks, inert probe
startup and upload-refusal checks, actual target compile/source/ELF receipts and
fresh independent review. None is a sensor run, physical synchronization proof,
clock qualification, schedule acceptance or human gate.

## Freeze checklist / next action

Root selects and records exact progress envelope/terminal-delivery rule, begin
work/anchor, native step/poll accounting, busy/legacy collision semantics,
cancellation cause and precedence, active20ms/time-abort cleanup ownership,
malformed-progress handling, and scope of any pending heading projection. Then
freeze public headers/contract before independent tests. The primary source
review must first support the selected yield boundaries. This note is evidence
of an audit only; none of these recommended new policies is yet implemented or
approved as a frozen D094 contract.
