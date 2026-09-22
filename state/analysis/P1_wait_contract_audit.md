# P1 WAIT contract audit - recommendation only

Date: 2026-09-22, Asia/Dubai. Read-only contract audit; this file records a
recommendation, not a decision, implementation, test pass or physical claim.
D-051 delegates remaining engineering choices to the coordinator without a new
human question. The coordinator should record the selected material behavior
before implementation. Bare-board work currently has priority over WAIT.

Sources inspected: BEHAVIOR B12 O1/O4 and its D-033/D-034 text, PLAN section 6.2,
the existing WAIT/SIDESTEP config defaults and public `src/core/openers.h`.
No opener implementation was read.

## Recommended resolution of SC-G

After the approach cue, run the complete existing SIDESTEP_R through its Flank
API, including the initial +50-degree pivot. Literal O4 instead skips the pivot
and starts straight ahead at the existing heading. Moreover, the widening cue
contains a front detection, so the established DRIVE front-abort can immediately
terminate that literal sequence before it traverses. A complete SIDESTEP_R
matches PLAN 6.2's evasive intent while preserving D-033/D-034 priorities.

Tradeoff: the initial pivot adds response time. Reusing this software sequence
does not prove sufficient lateral displacement or successful charger evasion;
that remains a later physical test. If front detection remains at pivot
completion, preserve the established immediate front exit rather than forcing
a lateral traverse or ignoring the target.

## Proposed precise behavior

- HOLD requests immediate brake/zero for up to WAIT_MAX_MS (2000 ms). Consume
  fresh effective confirmed observations; ignore high bits. A countdown snapshot,
  impact cue or old contact latch does not substitute for widening evidence.
- First observed FC starts one episode at that observation's supplied time.
  Require continuous confirmed FC and, on a later fresh observation, a newly
  rising FL15 or FR15 within inclusive APPROACH_WINDOW_MS (300 ms).
- Simultaneous initial FC-plus-flank assertion is not an ordered cue. A flank
  already held when FC appears does not qualify, but another newly rising flank
  may. Either or both eligible rises select the same fixed RIGHT sidestep.
- FC clearing cancels the episode. An expired episode cannot rearm merely
  because FC remains high; a new FC episode is required. Do not continually
  refresh the anchor on held FC. Timing applies to confirmed observations,
  not invented raw edge times hidden by debounce.
- While holding, external gate/STOP/edge preempts first; current side/rear abort
  wins next; a valid approach cue wins next; WAIT deadline follows. Thus a valid
  cue or side/rear detection wins a deadline tie. Front presence alone keeps
  waiting. This priority proposal needs explicit coordinator recording.
- On the cue, start Flank as SIDESTEP_R at the observed time/current or last-known
  finite heading, then immediately evaluate its first step. End WAIT timing;
  forward the existing phase priorities, fallback, timeout pulses, governor
  profile and scan hint. Do not restart from another cue or backdate the pivot.
- Every terminal requests zero and D-034 current-perception routing. Front still
  present at WAIT expiry selects TRACK with fresh normal qualification; no target
  selects SEARCH. A side/rear abort reason does not bypass normal current front
  priority, contact clearing or final governor/safety checks.

Smallest API addition: a Wait wrapper owning hold/cue timing and one existing
Flank, accepting Sample and exposing HOLD/FLANK/terminal stage plus brake and
forwarded flank result. Preserve existing Flank mode acceptance and established
tests. Healthy/unavailable-heading behavior should remain consistent with the
public motion contracts; never invent a measured yaw or target bearing.

## Regression matrix for the future contract

| Area | Required boundaries |
|---|---|
| Cue | FC then FL/FR/both; simultaneous first assertion; pre-held flank; FC interruption/reacquisition |
| Window | 299999/300000/300001 us; continuous-FC expiry; no rolling anchor refresh |
| Priority | Cue plus side/rear; cue at WAIT deadline; side/rear at deadline; front-only deadline |
| Delegation | Right pivot first; D-033 front/outer priorities; inherited turn-in/scan hint; no cue restart |
| Lifecycle | Reset/restart; terminal retention; delayed calls/wrap; finite/unavailable heading |
| Composition | HOLD cancels prior duty immediately; governor caps; edge/STOP veto; fresh qualification/contact |

Next action: coordinator chooses and records the contract under D-051, then
commits public interfaces before independent tests and implementation. This audit
does not mark SC-G resolved or authorize any motor run or phase gate.
