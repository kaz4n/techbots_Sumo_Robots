# Native recorder/dump bench: independent public-oracle preflight

2026-09-24 Asia/Dubai. Public declarations and adopted specifications only; no
implementation body reads, tests, build, board action, configuration change, or
ledger change. Reused independent author context, not a fresh or cross-model
review. The coordinator selected the full 200-second `bench/recorder` path during
this preflight; the shorter alternative below remains an explanatory comparison.
Today's Thursday24 schedule is P2 bench preparation; no human gate is inferred.

## Recommendation and composition

The full path is feasible through existing public APIs. Use one actual
`app::Transaction`, one existing `recorder::dump::Transfer`, and the existing
native `app::DumpPort` binding. The Transaction already owns the sole Robot,
MotorGate, AttemptRecorder, prior application receipt, and S/D/A/C accounting.
It prevents a new bench from duplicating receipt/tail/reset logic. Supply only
checked inert motor callbacks: no native motor owner, GPIO/PWM writes, physical
output claims, or fabricated successful applied receipt. Compile MATCH0 and
MOTORS_ALLOWED0. After GO, Robot may legitimately request motion; actual Gate
callbacks and feedback must remain disabled/zero because of M0.

Keep D091's `recorder_inert::Runner` unchanged. Its public API exposes a terminal
report and const retained source, but no live eligible Robot/menu transaction.
Its terminal STOP cannot authorize Transfer. Reusing that frozen runner would
require a new mutable ownership or lifecycle seam; the existing Transaction is
the smaller and more useful composition boundary.

The new default sketch should be disabled and perform no clock, motor-backend,
ready-pin, UART begin/readiness/write/cancel callbacks. Enabling a synthetic run
and supplying all four existing native SetupGrant predicates are distinct explicit
requirements. Origin is fixed to SYNTHETIC, not a caller-selectable claim. A new
identified upload/run and clean-framing preparation remain separate work.

## Synthetic observation policy

Use one actual admitted decision per due original 1kHz slot, never a catch-up
loop or fast-forwarded Robot timestamp. `Transaction::decideFrom` is preferable:
its public projection callback receives actual D, allowing truthful synthetic
logical source stamps without guessing the future decision time. Start/decision/
application/completion remain actual Transaction clock observations.

Before STOP, use fixed declared synthetic black lines (`QTR_TIMEOUT_US`), inactive
opponents (electrical inactive pattern from `OPP_ACTIVE_LOW_MASK`), finite nominal
battery (freeze an explicit literal such as11.1V in the new contract, not a
measured voltage), absent IMU, and the logical button schedule below. Inactive
opponents throughout are the smallest sufficient transport stimulus; a
center-front-after-GO scenario is unnecessary for B8 and adds unrelated behavior.
Absent IMU/calibration rejection warnings are actual synthetic scenario outcomes,
not faults to suppress or fabricate away. Keep actual recorded flags and events.

For the logical reset qualification, explicit `ButtonEvidence` can preserve D087
admission: explicit/contract-valid, presence VALID, chosen logical level, raw0,
monotonic sequence, and started/completed equal to actual projection D. Equal
source timestamps within one record are permitted; subsequent records advance.
These are explicitly synthetic logical samples with no ADC conversion claim and
no call to `decodeButtons` against unconfigured electrical windows. Preserve
their sequence and source continuity across the logical reset. Alternatively,
legacy logical button input needs its own explicitly weaker provenance statement;
the explicit synthetic source is the closer match to the existing logical guards.

Do not add physical native inputs merely to manufacture `initialization_complete`.
The contract should name it synthetic fixture readiness, with every chosen input
field frozen. The actual Robot must still admit those fields; invalid input must
retain actual fault/STOP evidence.

## Exact ideal-grid start, 200-second recording, STOP, and tail

The following is an independent zero-cost host-clock oracle, not a prediction of
native wall-clock timestamps. Let T=1000us, D=20000us, L=1000000us and
Q=D+4T=24000us from existing config. Let the first actual decision be time0, with
all S/D/A/C observations equal to that decision and one decision every T.
All intervals below are half-open; times in tables are milliseconds.

| Decision times | Synthetic input | Required real outcome |
|---|---|---|
| [0,24) | NONE | First initialized Robot BOOT→IDLE; neutral qualification; recorder EMPTY |
| [24,48) | START | Qualified press at44; no accepted release/recording yet |
| [48,200068) | NONE | Accepted release R=68; COUNTDOWN with actual START_RELEASE; actual GO at R+5100=5168 |
| 200068 | Qualified local `stop_requested=true`, NONE | First actual STOP at R+200000; disabled/zero request and receipt; recorder DRAINING |
| 200069 | `stop_requested=false`, NONE | Real later STOPPED tail with matching prior receipt; recorder SEALED after final frame consumption |

Release anchoring comes from actual completed debounce, never raw release48.
The production bench must capture its observed release R and request STOP on the
first real due decision whose forward age reaches LOG_FRAME_WINDOW_MS. It must
not hardcode the example absolute times or claim a missed slot was executed.

For this ideal trace, independent arithmetic predicts:

- Epoch token69, initial frame relative t_ms0, final frame relative t_ms200000.
  Frames at0,40,...,200000: exactly5001, with STOP's final frame coalesced with
  the due frame, no overwrite, skipped frame, or synthetic fill.
- STOP token200069; tail token200070. Last frame token200069.
  Observed active recorder results200002, inclusive accepted START through tail.
- GO-through-STOP timing membership has194901 actual completed receipts. Under
  the zero-cost clock only, max/overrun counts are0. Real clocks must report their
  observed durations; zero is not an expected hardware duration.
- Retained events must contain exactly one accepted START_RELEASE, exactly one
  GO, actual state changes and warnings, and no FIRST_NONZERO_DUTY. Compare all
  emitted rows with the actual sealed source; do not invent a total event count
  without first specifying and independently deriving every behavior event.
- `go_seen=true`, `final_frame_missing=false`, `interrupted=false`, terminal
  exhaustion false, source SEALED. With the specified healthy synthetic input,
  admitted clock/receipts, and no loss, named loss counters and incomplete flags
  are false/zero. A calibration-rejected flag is not itself recorder loss.

Native scheduling can change these counts/times. Preserve actual missed slots,
lateness, frame/event counts, statuses and losses. A successful wire transfer is
not proof of a gap-free 200-second experiment.

## One logical reset after the real tail

Preserving the D103 logical gesture and actual Transaction predicates avoids a
change to either existing guard. It does **not** make synthetic inputs satisfy
the production Runtime's healthy physical ADC requirements. The new contract
must explicitly authorize this autonomous bench-only synthetic caller policy;
Runtime's physical local-service path and default grants remain unchanged.

Require both completed inhibited STOP epochs and source SEALED before beginning
the synthetic gesture. Continue one real Transaction per due slot, with Gate
STOPPED, consumed matching valid disabled/zero receipts, actual C, and no token
gaps hidden by fixture state. Let B=first decision after the tail; ideal
B=200070ms. Start new neutral qualification at B, not at an earlier countdown or
STOP observation.

| Relative to B | Input and required observation |
|---|---|
| [0,24) | Fresh NONE; neutral qualifies at20 |
| [24,1048) | Fresh MODE; press qualifies at44; hold starts at that actual qualification D; source MODE must reach1044 to observe the complete1000ms hold |
| [1048,1068] | Fresh NONE; release qualifies at1068; retain that source start, D/token, and the actual old fault facts as pending intent |
| 1069 | Only after prior successful C and a new successful open/S: verify pending age/continuity, notify Transfer of Robot reset, then call `resetStoppedRobotForService()` once before decide |

Ideal reset decision U=B+1069=201139ms, with source age1000us. The public D103
5000us inclusive pending-age and source-gap boundaries, forward chronology, and
decision continuity remain useful exact negative/adjacent test oracles. A release
at the hold deadline cancels; START/BOTH contamination, premature release,
replay/stale/absent/invalid evidence, failed C, bad receipt, and invalid reset
phase/history cannot create an intent or accepted reset.

The Transaction itself, not a supplied bool, checks ACQUIRING, unused reset,
two qualifying completed STOPPED decisions, exact actual STOPPED motor receipts,
non-exhausted source SEALED/EMPTY, and the original chronology. For this probe
require SEALED and nonzero epoch additionally, so EMPTY never becomes a dump.
Unexpected refusal after a claimed qualified intent is a terminal bench failure.
No Gate.reset/begin, reconstructed owner, native setup retry, or clock rebase.

On success retain actual one-step reset evidence even if later work fails. The
recording's arrays, metadata, counts and epoch remain unchanged; highest observed
tokens continue normally. Gate remains STOPPED, Robot's next token remains
monotonic, and the old previous receipt is cleared only by Transaction's real
reset. In the ideal trace the first post-reset token is201140.

## Permanent service-only menu and real LOG_DUMP request

Before the first post-reset input, permanently select canonical explicit
CALIBRATION/RAW ABSENT line evidence (version/candidates/identity/time0) and
canonical explicit unavailable IMU. This is D089/D103's inhibited service
projection, not synthetic black/healthy control evidence. Use fresh synthetic
buttons, opponents and valid battery for service readiness. Never switch back
to control lines, accept another match START, or reinterpret unavailable QTR as
black. Gate's independent STOPPED state also persists.

The real Robot starts BOOT→IDLE under this projection. Menu state resets to match
view/default mode; it cannot be injected. With U as first reset decision and the
same ideal clock:

| Relative to U | Button level | Required actual menu outcome |
|---|---|---|
| [0,24) | NONE | Fresh post-reset neutral arming; first entry is BOOT |
| [24,1048) | MODE | Qualify at44, toggle service menu at1044; SENSOR_VIEW |
| [1048,1072) | NONE | Release long gesture without cycling; neutral rearm |
| [1072,1096) | MODE | Qualified short press |
| [1096,1144) | NONE | QTR_CAL at1116, then conservative fresh neutral margin |
| [1144,1168) | MODE | Qualified short press |
| [1168,1216) | NONE | DRIVE_TEST at1188, then neutral margin |
| [1216,1240) | MODE | Qualified short press |
| [1240,1288) | NONE | LOG_DUMP at1260, then neutral margin |
| [1288,1312) | START | Service START qualifies; never a match start |
| [1312,onward) | NONE | Genuine LOG_DUMP request at1332; retain IDLE/LOG_DUMP selection during transfer |

Ideal request time202471ms/token202472; transfer session is that actual request
token, retained epoch69, origin SYNTHETIC. In real execution, use observed gesture
qualification anchors and real outputs; do not fabricate the ideal token/time.
Require raw-mode/hold flags and zero/disabled actual application throughout this
service lifetime. Selecting QTR_CAL/DRIVE_TEST does not execute either service;
only the subsequent real LOG_DUMP request starts transport. A fresh START with
match view selected remains inhibited by permanent RAW, not a new armed attempt.

A later second STOP uses canonical CONTROL+ABSENT for its real tail instead of
illegal RAW in STOPPED, then terminal passivity, with no second service reset.
Retain any actual LINE_CONTRACT diagnostic; do not erase it to report success.

## Transfer ordering and observable delivery oracles

For each due epoch use actual open/S → projection at D/Robot/Gate/recorder →
eligible service work → actual C. Feed Transfer the current actual result and
original D, the same const source object, origin SYNTHETIC, and current actual
clock/readiness. There is at most one Transfer step/write opportunity per epoch,
no between-tick pump, hidden second decision, catch-up, or sleep.

Mirror D101's receipt boundary: only an actual consumed matching valid inhibited
receipt can permit readiness sampling. Failed current receipt aborts active
Transfer and skips its step; do not relabel it Linux unavailability or fabricate
a next Robot result. Transfer receives other actual invalidating results so its
existing context/source/identity precedence remains in force. Bracket readiness
and transfer clocks and use `finishAfter(last_observation)` so all service work
belongs to S..C. A stale decision (age>=TICK_US) cannot write.

Freeze success only after a real completed C and actual Transfer
SENT_UNCONFIRMED/NONE. Preserve actual bytes/frames/events/CRC and native status.
Do not call abort/cancel merely to freeze a completed successful probe. On failure
retain first bench cause plus actual Transaction/native/Transfer reports, partial
counts and frozen source. Follow D101 motor-inhibition-before-transfer-abort
ordering; a bad clock must not manufacture successful C or a fake Robot STOP.
Terminal calls are passive and no retry/reinitialization follows native poison.

Wire oracles remain exactly D090: BEGIN/SH/SR/FH/FR/EH/ER/END ordering, literal
origin1, session=request token, epoch=accepted START token, one-line bounded
formatting, <=64 offered bytes/call, correct pending/partial progress, exact
CRC32 over pre-END bytes, retained row ordinal/order/status/loss, and no extra
rows. Host completion additionally needs a valid independent receiver END/CRC and
CSV bundle validation plus exact row comparison with the retained source.
SENT_UNCONFIRMED alone is never host delivery success.

## Minimal public seam and decisions needed before executable freeze

Prefer a single new bench owner taking a clock port and existing `app::DumpPort`,
internally creating the checked inert motor Port and Transaction. Public methods
can remain `begin(grants)`, `poll()`, and const accessors for the bench report,
Transaction report, retained source and Transfer report. The report needs actual
phase/first failure, setup/native outcome, accepted release/STOP/reset/request
identities, completed epochs/missed slots, callback rejection counts, and measured
duration scopes. No mutable Robot/Gate/recorder getter or result/token setter.

Freeze these exact choices in the new contract rather than leaving tests to guess:

1. Disabled begin return/phase and repeated-begin passivity; the recommended
   convention is successful DISABLED with zero callbacks, then immutable false
   on repeat. Missing callbacks or malformed config must fail before callbacks.
2. Actual scheduler baseline, skip/lateness accounting, checked modular clock
   order, equal-clock stall bound, per-stage progress/deadline failures, and what
   happens if a due poll crosses a scheduled gesture boundary. Timelines above
   are host ideal oracles; native stages must anchor to actual admitted evidence.
3. Whether initialization-complete is true on the first synthetic decision,
   explicit button source representation/sequence0 versus1, nominal voltage,
   inactive opponent policy, and canonical pre/post-reset IMU/line fields.
4. Initial setup order and grants: inert Transaction initialize and one native
   dump setup only when explicitly enabled. Existing native device_init has
   unbounded ACK waits; no elapsed measurement makes setup bounded. Readiness
   may be LOW at setup and is not receiver attachment/framing evidence.
5. Exact reset-gesture implementation boundary, source-age/continuity checks and
   first-fault precedence; no extraction or change to production Runtime is
   necessary. Freeze permanently service-only projection and actual report
   preservation. Keep later second-STOP handling explicit.
6. Logical reset and menu deadlines are bench policy, not new tunables smuggled
   outside config. Derive short guard intervals from current debounce/long/TICK
   constants or adopt a named config value. Existing DUMP_STALL_MS2000 and
   DUMP_TOTAL_MS300000 bound active Transfer, not pre-transfer stages.
7. Target memory/retained-source capture plan: this new Transaction+Transfer
   image needs its own exact source/ELF/loader/heap evidence. Previous D091
   capacity or D115 tiny image does not establish its fit or sampled free RAM.

## Short alternative and physical limits

The smallest lifecycle alternative accepts START at68ms, supplies MODE from72
through95ms, cancels at92ms, consumes the tail at93ms, and then reaches real
LOG_DUMP via menu gestures around1428ms. Ideal retention is two frames at relative
0/24ms, START plus IDLE→COUNTDOWN and COUNTDOWN→IDLE events, go_seen=false and no
match timing samples. It needs no logical reset and is suitable for a transport
unit scenario, but does not exercise the named200s B8 end state. The coordinator
therefore selected the full path above, not another short-only runner.

Even full success is a 200-second **synthetic** MCU-recording/delivery experiment,
not sensor or assembled-robot B8 acceptance. The existing clean-framing,
exclusive-UART, actual router reopen, receiver attachment, immutable installed
identity, native setup limitation, cancellation poison and exact upload-review
obligations in `P2_native_dump_bare_feasibility.md` remain. No current boolean may
claim these prerequisites have been met. D113 CONNECTED is TCP-only and its
router-registration field remains UNKNOWN. No inbound MCU command, remote motion,
hidden daemon restart/reset, or hardware qualification follows from this proposal.

Sources: public `bench/recorder_inert/src/recorder_bench.h`, `app/transaction.h`,
`app/dump_port.h`, `core/fsm.h`, `core/countdown.h`, `core/types.h`,
`hal/recorder.h`, `hal/recorder_csv.h`, `hal/recorder_dump.h`,
`hal/dump_uart_unoq.h`, current config; adopted P1 Robot, D070 recorder, D090
dump/native, D091 recorder-bench, D092 timing, D095 Transaction, D101 dump,
D103 service reset, D087 button routing, D089 QTR calibration contracts;
BEHAVIOR B3/B13/B15 and P2 B8. No implementation execution verifies the numerical
oracle yet; the next step is adoption and separately frozen independent tests.

## Coordinator draft alignment and native throughput qualification

The subsequent D116 draft chooses existing `V_NOM_V` (11.1V) and FC detection
after an actually observed GO, matching the earlier D091 scenario instead of
the simpler all-inactive recommendation above. It accepts NONE-2G intervals
between short MODE presses and reset on the next S immediately after actual
qualified reset release. The ideal lifecycle/frame/timing counts above are
unchanged by the opponent choice, but complete event contents must follow that
chosen scenario. Runner exposes actual setup NativeStatus only; live status
belongs to the external native owner because app::DumpPort has no status callback.
`bench/recorder/src/recorder_transport.h` now supplies a declaration-only public
proposal with const actual-owner evidence and no implementation body.

One native-throughput question requires source/target review before calling the
full positive physical transfer feasible with one write opportunity per1ms.
From the public CSV schema,5001 small-field FR rows with a six-digit session,
relative times0..200000 by40ms, and explicit absent-IMU flags require about531k
payload bytes. Each roughly106-byte row requires two <=64-byte packets, adding
about150k MessagePack bytes under the existing15-byte native packet prefix.
Headers, summary and events add further bytes. This arithmetic is a sizing
estimate, not an executed stream or throughput measurement.

The public native contract stops immediately on TXE-low and limits a call to80us;
STEP_BYTES8 is a ceiling, not eight-byte progress. With the pinned FIFO-disabled
115200 route, a native source audit should determine whether a call can submit
only1–2 bytes before returning. If at most2 bytes per1ms epoch is the effective
bound, the frame rows alone exceed300s, so the unchanged DUMP_TOTAL_MS deadline
would prevent the full native positive case. A host callback acknowledging64
bytes cannot resolve this question. The coordinator has been asked to obtain
the separate native review before treating the restrictive one-call cadence as
a sufficient end-to-end design; no timing default is changed by this preflight.

Final public prefreeze review: D116 draft
`912434c45bda6d71900f2dc624f12f19197c3071efcd74f9f567857dcb7e3d19`
and declaration header
`b43ed24532254ae829f991da55a3081ae654fbe0fbc399497e8b7a6c5a9cf62e`
are consistent for independent authoring. The draft explicitly selects disabled
begin=false/DISABLED (superseding the earlier successful-disabled recommendation),
PORT→GRANT→CONFIG validation, first synthetic sequence1, final setup sample as
equal-poll baseline, D101 inhibited-IDLE readiness, and actual S/D/A/C evidence
through the const Transaction. It resolves cleanup by aborting without invented
C, and names CLOCK versus DEADLINE for reverse versus forward context expiry.
The derived post-setup budget is502633000us with current constants; admission
and final-C equality expire. It retains the full-length positive host pipeline
and a slow-progress TOTAL-failure profile with actual payload/packet accounting.
Native positive throughput remains explicitly unresolved. No executable test or
implementation body was read/run to establish this public-interface review.
