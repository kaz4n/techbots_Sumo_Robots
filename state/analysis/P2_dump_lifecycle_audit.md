# P2 B8/B13/B15 dump lifecycle audit

Read-only source/spec audit, 2026-09-23 Asia/Dubai. Assigned scope: lifecycle,
retained evidence, current CLI, and required regressions. No hardware API audit,
board operation, source/test modification, decision adoption, or test execution.
The only authored file is this report. D051 permits the coordinator to adopt the
software choices below; recommendations here are not adopted policy or evidence
of implementation. The current date falls on PLAN section 3's Wednesday P0 gate
date; D075 separately permits active P2 software without passing physical gates.

## Finding

There is presently **no legal end-to-end dump path**. `LOG_DUMP` is a typed menu
intent, the recorder/CSV modules are usable components, `tools/logs.sh` receives
Monitor bytes, and `tools/dump_match.sh` is absent. The production app remains an
inert one-step compilation entry with an empty loop.

A SEALED recorder does not establish current IDLE. Ordinary completed motion
attempts terminate in STOPPED or inhibited EDGE_ESCAPE, and D035 requires a reset
before recovery. The existing **logical** `Robot::reset()` is sufficient to clear
runtime state back to BOOT while leaving an independently owned recorder alive;
the firmware has no local reset gesture/consumer implementing that route. An
MCU reset, reflash, process restart, or power cycle has no proved recorder-RAM
retention. Neither a dump request nor a timer may silently reset STOP.

## Verified source relationships

| Source | Observable contract/behavior |
|---|---|
| AGENTS R1/R2/R3/R4/R7 | Motor inhibition remains authoritative; MATCH Bridge traffic is dump-only in IDLE; control cannot wait for Linux; this work does not authorize a motor-capable upload/run. |
| BEHAVIOR B13/B15; D035/D057/D058 | Qualified local service START emits an intent only. STOP/fault wins. STOP remains latched until reset. Both local LOG_DUMP and a Linux dump request are permitted only in IDLE. |
| D051/D075 | Material engineering choices may be selected and recorded without another user question. This does not establish hardware facts, passed gates, or per-run motor permission. |
| `src/core/fsm.h:403`, `:426`, `:471` | RobotInput has no reset command; RobotResult has token/fresh, final output state, menu intent, gate, faults, frame identity, loss and timing. `stop_requested` explicitly means local safety stop. |
| `src/core/fsm_robot.cpp:76`, `:275`, `:870` | A distinct tick admits a new token; duplicates clear pulses. Robot runs lifecycle before final menu publication. Menu uses IDLE-at-entry and final STOP/fault inhibition. |
| `src/core/countdown.cpp:10`, `:435` | Gate cannot leave STOPPED through release/MODE/START. Menu emits no service intent outside IDLE-at-entry or with final inhibition; duplicate time emits no new request. |
| `src/hal/recorder.cpp:22`, `:89`, `:124` | Only a validated newer accepted match START clears the old attempt. Epoch/frame identity guards exclude prior frames and delayed receipt prefixes. |
| `src/hal/recorder.cpp:158`, `:177` | Reset notification preserves arrays and identity; active recording becomes INTERRUPTED. Token exhaustion has a separate one-shot interrupted envelope. |
| `src/hal/recorder_csv.h:31`, `.cpp:133` | Summary capture requires exclusive read access; it copies bounded metadata, not arrays. Formatting provides neither IDLE authority nor session identity. |
| `src/core/fsm_robot.cpp:915` | `Robot::reset()` clears runtime and pending evidence but preserves next token. It does not reset the external AttemptRecorder. |
| `bench/p2_recorder_memory/src/memory_probe.cpp:46` | Existing compile-only reset probe calls recorder notification before Robot reset. This is not an executed reset lifecycle. |
| `src/app/app.ino` | No scheduler, recorder ingestion, service consumer, transport, or reset consumer exists in the actual app entry. |

## Evidence ownership and immutability

The recorder is noncopyable and owns the single fixed frame/event arrays. It has
no public erase operation. Its const frame/event/summary access is not a lock or
snapshot: an accepted later match START can replace the entire attempt. Borrowed
frame pointers may not survive append/reset/destruction (`recorder_frames.h`).

RECORDING and DRAINING remain mutable. STOPPED, inhibited EDGE_ESCAPE, or a
COUNTDOWN-to-IDLE cancellation changes RECORDING to DRAINING. The next accepted
valid-state fresh result performs exactly one tail flush and enters SEALED.
That flush accepts only the stopping token's genuine prior frame. Missing/wrong
identity/unknown status remains missing evidence; CLAMPED/INVALID known statuses
are retained with their loss meaning. A malformed-state result does not seal.

SEALED and INTERRUPTED preserve the stored bytes/summary through ordinary later
results, service intents, rejected old identity, and reset notification. Their
private highest-seen result token can still advance. Only a validated accepted
new match START replaces their payload and epoch. EMPTY is clean but is not a
completed attempt. `incomplete()==false` does not imply a finished lifecycle.

`onRobotReset()` is a caller obligation before logical reset or end-of-stream.
It makes active states INTERRUPTED, retaining all bytes and loss counters; after
GO it also marks timing incomplete. It does not invent the unreceived final
frame, and a reset during DRAINING is interruption rather than SEALED completion.
The retained loss fields must be exported individually, not reduced to one flag.

## Minimal permitted ownership semantics to adopt

Use one synchronous bounded owner invoked after the current `Robot::step()` and
recorder ingestion. A callback or Linux reader must not directly reset Robot,
change menu selection, accept match START, change tunables, or write motor pins.
Only a bounded dump request reaches this owner. A boolean named `idle` supplied
independently of the current Robot transaction is insufficient authority.

Admission and each subsequent transfer step should require all of:

1. A current, newer admitted Robot result (nonzero token and fresh), with real
   final state IDLE, gate phase IDLE, no GO/accepted START, no contract or escape
   fault, motors disabled and both duties exactly zero. A duplicate/out-of-order
   result cannot replay an intent or advance a cursor. Current acquisition and
   actual MotorGate application remain scheduler obligations; outputs alone are
   not physical proof.
2. A fresh qualifying local `LOG_DUMP` intent or a bounded Linux dump request
   admitted while that IDLE transaction is current. A request made while moving,
   BOOT, COUNTDOWN, STOPPED, or faulted is rejected, not deferred until IDLE.
3. One nonempty retained epoch in SEALED or INTERRUPTED. RECORDING/DRAINING must
   finish/interruption must be explicit first. INTERRUPTED may be exported as
   interrupted evidence, never advertised as a completed recording. EMPTY should
   return an explicit no-attempt response rather than a successful match dump.
4. Exclusive synchronous access while capturing metadata and copying one row
   into bounded staging storage. Bind session identity to retained epoch, phase,
   counts and the exact captured summary. Verify identity before every read and
   enqueue. An exact field comparison avoids a checksum collision as authority.

No second payload-sized buffer is necessary. Preserve the existing single owner;
cache one formatted row/transport fragment with an explicit offset. Backpressure
cannot regenerate/skip/reorder a partly accepted row. A new accepted match START
or departure from IDLE cancels the session before another old row can be read or
submitted. Recorder replacement remains legal for the new attempt and must not
be blocked by a slow receiver. Data already emitted is only a partial session;
success needs a terminal completion record bound to that same session.

Logical resets also invalidate an active session even if the retained epoch and
bytes are unchanged. Keep a dump generation/session counter outside Robot reset,
or explicitly cancel as part of the reset transaction. Session identifiers must
not wrap into reuse; exhaustion should fail closed. Physical boot identity and
host provenance are a separate transfer-envelope choice. A RAM epoch token alone
cannot distinguish two physical boots.

## STOPPED to legal IDLE without discarding RAM

Recommended explicit local recovery sequence:

1. STOP continues to command actual inhibited outputs. A fresh local recovery
   request is qualified independently; it is not a LOG_DUMP or Linux command.
2. Where possible, run one further normal inhibited Robot tick with the genuine
   applied receipt for the stopping tick, and consume it so DRAINING becomes
   SEALED. Do not fabricate a receipt or await Linux. A missing receipt keeps
   existing incomplete/final-missing semantics. The stopping result and all
   final events must reach the recorder before clearing Robot state.
3. Cancel any dump session, call `AttemptRecorder::onRobotReset()`, then invoke
   the complete `Robot::reset()`. Preserve the recorder instance. Clear scheduler
   predecessor/receipt bookkeeping; never submit a stale pre-reset receipt as a
   new result's application. Keep the actual motor output inhibited throughout.
4. Follow ordinary BOOT/init again. Do not assign IDLE directly, manually clear
   the STOP latch alone, or assert fake initialization/sensor readiness. Existing
   freshness/application faults can prevent IDLE after reset and must remain
   authoritative. Reset clears menu selection/gesture state and does not replay
   a held START. Every later match still requires a fresh press/release and the
   full countdown.
5. Admit a separate fresh dump request only after a real IDLE result. Selection
   of LOG_DUMP may then use the existing B13 menu. The retained recording keeps
   its original mode even though the freshly reset menu selects MODE_DEFAULT.

The source supplies the reset primitive but **does not select the physical/local
trigger**. A minimal D051 choice is a fresh neutral-qualified, exclusive MODE
long hold while already stopped, interpreted as a full local software reset;
use source-qualified button evidence, existing debounce/hold values, one-shot
consumption, release-wins boundaries, stale/invalid/BOTH cancellation, and fresh
neutral after reboot. This must be explicitly added to B13/a decision before
implementation, since current MODE gestures are IDLE-only. Do not silently turn
the ordinary STOP release or a service START into reset. Whether inhibited
EDGE_ESCAPE uses the same local trigger or first requires local BOTH STOP must
also be selected; routing it through the existing STOP path is the smaller change.

There is one deliberate exception: if `next_token_` exhausted to zero,
`Robot::reset()` preserves zero and the next step remains TOKEN_EXHAUSTED/STOPPED.
That retained terminal attempt cannot become live-dump eligible through the
existing reset primitive. Refuse live export in this envelope; do not recycle
tokens or use a physical reset while claiming RAM preservation. Existing offline
inspection can still describe the retained interrupted evidence.

## Current host mechanism

`tools/logs.sh` delegates to `board_tool.py logs`. That command establishes a
board-side loopback Monitor connection on port7500 over the configured transport,
then receives chunks of4096 bytes and forwards stdout. It sends no MCU input.
The initial socket connect uses10 seconds; subsequent reads have no timeout. It
has no attempt/session parsing, fixed destination files, summary collection,
completion proof, or durable bundle publication. It is a receive-only logger,
not the missing B15 dump command. `tools/validate_csv_bundle.py` performs local
read-only file checks and cannot establish common attempt or hardware origin.

No conclusions about Bridge/UART source boundedness are made here. That independent
audit must decide the real transport calls, inherited runtime path ownership and
per-tick submission bound before they can be invoked. F091/SC-AJ, full firmware
RAM/WCET, app integration, physical acceptance and human gates remain open.

## Exact choices still requiring a recorded software policy

- Full local reset trigger and its source-time qualification; allowed stopped
  states; receipt flush ordering and missing-receipt behavior; reset-generation
  invalidation. D035's reset-only rule itself does not need weakening.
- Dump admission API tied to current Robot results, Linux request parsing and
  expiry, local-versus-Linux collision behavior, duplicate request semantics and
  whether a service selection change cancels or merely continues a valid IDLE
  session. Recommended: one session, busy/reject duplicates, no queued requests.
- SEALED versus INTERRUPTED response labels, EMPTY refusal, exact session/build/
  boot identity, partial cancellation and terminal success envelope.
- Row/fragment work limit, partial-write acknowledgement, backpressure timeout,
  reconnect/retry policy and ownership of unsent bytes. State departure must win
  over retries. New tunables belong in config.h with units; structural limits
  should be distinguished from tuning values.
- Actual native transport availability/boundedness (separate agent), host output
  naming/atomic publication/provenance (coordinator), and later actual scheduler
  integration. None is proved by the existing formatter or this audit.

These are delegated engineering choices, not reasons to request physical sensor
connection, motor-run permission, or another routine design answer from the user.

## Required regression evidence

Preserve all existing locked tests. Existing direct coverage is in
`tests/locked/test_stop_hold.cpp` (especially reset/boot-held START at264),
`test_menu_routing.cpp` (service non-start, STOP/fault priority and no replay),
`test_robot_safety.cpp` (real Robot STOP latch/countdown), `tests/test_robot.cpp:313`
(monotonic reset token/stale predecessor), `tests/test_robot_events.cpp:263`
(final stopped receipt), `tests/test_attempt_recorder.cpp:789`, `:943`, `:967`,
`:1021` (tail/immutability/reset/exhaustion), and `test_recorder_csv.cpp:487`
(phase distinction). These were read, not re-executed for this audit.

New independent contract-derived tests should establish:

1. Real Robot + AttemptRecorder + service owner sequence: match, qualified STOP,
   actual disabled MotorGate receipt, tail SEALED, explicit local full reset,
   ordinary BOOT/init, new IDLE request, byte-identical original attempt export.
   Include interrupted/reset-before-tail and every known loss field/status.
2. All current states, final faults, output permissions/duties, lifecycle phases,
   absent/stale/replayed results and requests. In particular SEALED+STOPPED must
   emit zero transport calls, and canceled COUNTDOWN reaches IDLE before its tail
   is eligible. Linux/LOG_DUMP must never reset or produce a match release.
3. Reset gesture exact/adjacent deadlines, source age, duplicate time, wrap,
   release priority, boot-held input, invalid/stale/BOTH contamination and no
   accidental match or menu action. Reboot still requires the full START hold.
4. Before-each-fragment cancellation: new START and epoch replacement, departure
   from IDLE, fault/STOP, explicit reset with unchanged epoch, owner identity/
   summary mismatch, transport error and session-token exhaustion. No borrowed
   pointer escapes a tick and no old/new attempts form a successful mixed bundle.
5. Zero-byte/short/complete writes, disconnect before and within every row,
   stalls, duplicate ACK/request, timeout boundary and retry. Cursors advance
   exactly by acknowledged bytes; repeated backpressure cannot mutate evidence
   or monopolize a tick. Completion is emitted only after every declared byte.
6. EMPTY, SEALED incomplete=false/true and INTERRUPTED are separately reported;
   RECORDING/DRAINING rejected; UINT64 Robot-token exhaustion stays inhibited and
   not live-dumpable after reset. Reset never reuses a previous attempt identity.
7. Existing CSV literal/raw round trips and local bundle validation using a
   transport-produced fixture, preserving status/ordinal/insertion order and all
   loss metadata. Host truncation/corruption/session mismatch remains visibly
   partial/invalid; hashes alone cannot create hardware provenance.

Run scoped normal/sanitizer host suites, relevant existing tooling, compile-only
actual target path and a separate fresh read-only review after implementation.
Do not count a host model, software bound, or compile result as B8's200-second
physical no-gap dump/free-RAM measurement or a passed P2 gate.
