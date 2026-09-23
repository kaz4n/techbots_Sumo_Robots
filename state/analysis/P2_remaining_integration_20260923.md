# Remaining P2 app service integration: read-only map

2026-09-23, Asia/Dubai. Baseline HEAD `2ded06aa6d8064ef9398bbc98aae785ca8e47f1d`.
The user has explicitly resumed; the coordinator owns D099/D100 target acceptance.
This report is a code/document inspection, not a decision, implementation, test
run, target acceptance or hardware observation. Only this file was authored.
Concurrent handoff/ledger/target-receipt work was observed and left untouched.

Read AGENTS, current handoff/PROGRESS, active P2 prompt, relevant FACTS and
DECISIONS, PLAN section 3, HARDWARE and BEHAVIOR B13/B15, and the scoped contracts
listed below. Today is the planned Wednesday P0 gate date, before the September
28 scope cut and October 1 freeze. D051/D075 permit P2 software progress; they do
not pass any gate. No relevant memory-registry entry was found. No board/network
action, source/test/ledger edit, upload, reset, motor action or test rerun occurred.

## Current implementation and evidence

| Requirement | Actual API/integration | Existing evidence and remaining boundary |
|---|---|---|
| One actual source/Robot/Gate/recorder lifetime | `Runtime` owns `Transaction`, source projection, `Calibration` and display. `Transaction` owns actual Robot, MotorGate and AttemptRecorder. `app.ino:16` calls `runtime.begin(SetupGrants{})`; line 21 calls `runtime.step()`. | D095/D096 contracts and validation. All setup grants remain false. The real app is not an upload-allowlisted inert sketch. D099/D100 current acceptance belongs to the coordinator. |
| Current IDLE log authority | `recorder::dump::Transfer::step(Context, RobotResult, const AttemptRecorder&)`, `recorder_dump.h:21-38`. The actual objects needed are available through `Runtime::transaction().report()` and `.recording()`. | D090 owner/receiver/native software has independent review PASS. No Transfer, native dump owner or callback is attached to `src/app`; the only `onRobotReset` there is Transaction's evidence interruption on failure. |
| Bounded native UART | `UnoQDumpPort::begin(SetupGrant)`, `ready()`, `port()`, `status()`, `dump_uart_unoq.h:11-27`. `Port` supplies bounded write/cancel. | D090 source/target audit already establishes the API basis; do not repeat generic Bridge research. Actual clean framing, ownership, Linux-loss cleanup, physical transmission and timing remain unqualified. |
| Local postmatch reset retaining evidence | Component APIs exist: `Transfer::onRobotReset`, `AttemptRecorder::onRobotReset`, `Robot::reset`, `MotorGate::reset`. | `tests/test_recorder_dump.cpp:26` proves a separate fixture composition. No app reset API or local reset gesture exists. The actual Runtime has an explicitly terminal STOP contract. |
| QTR calibration and threshold handover | `Runtime::postDecision`, `runtime_inputs.cpp:155`, calls actual `Calibration::step(D, RobotResult, exact decision snapshot)`; committed bank drives subsequent classification. | D089 and D096 independently tested actual pipeline/handover. Runtime report exposes the actual calibration result. Physical calibration is unproved. |
| Printable calibration snippet | `qtr_cal::formatConfig(const Report&, char*, size_t, size_t&)`, `qtr_cal_format.cpp:24`; only SUCCESS with valid nonzero-version bank succeeds. | `tests/test_qtr_cal.cpp:86,234` cover exact bank/order and atomic capacity boundaries. No app invocation or output transport exists. Existing formatter is not missing. |
| Receiver and CSV preservation | Existing `tools/dump_match.sh`/`.py`, `Parser.feed/finish`, `save_capture`, strict D090 wire protocol and D074 bundle validator. | D090 tests include actual C++ component pipeline roundtrip, hostile chunking, loss fields and atomic no-overwrite publication. This does not prove native app transmission. |

Recorded prior evidence, not rerun here: D090 scoped owner tests are 26 cases /
4,052 assertions; final review independently exercised native/receiver tooling and
reported no open scoped finding (`state/reviews/P2_dump_review.md`). D096 full
normal/sanitizer evidence is 1,411 main / 25,187,345 assertions and 173 enabled-Gate
/ 4,536,382 assertions; its configured Runtime tests exercise real STOP tail and
all eight calibration stages (`P2_app_runtime_validation.md`). Later D097/D100
receipts supersede counts/build status where applicable; none proves the absent
service wiring. No reason was found to rerun those unchanged tests for this map.

## Smallest eligible next integration seam

The narrow next **service attachment** is an optional Runtime-owned connection of
the existing `Transfer` to the existing native dump `Port`, rather than another
serializer, protocol or UART implementation. The exact reusable call boundary is:

```cpp
transfer.step({actual_now_us, transaction.report().decision_us,
               native_dump.ready(), declared_origin},
              transaction.report().robot, transaction.recording());
```

This illustrates existing APIs, not a new frozen signature or permission to run.
Freeze the app attachment contract under D051 before implementation. The natural
current code seam is after `Transaction::decideFrom` has performed
Robot -> Gate -> recorder and before `finishAfter` closes the actual epoch:
`Runtime::postDecision` (`runtime_inputs.cpp:155`) and `Runtime::step`
(`runtime.cpp:296`). Native initialization belongs to the existing Gate-first
setup lifetime, with explicit absent-by-default dump grants. Do not initiate it
from `step`, a menu request or a failed write.

Existing D090 obligations already determine the important interface inputs:

- Feed every actual decision to the transfer while active, including an unsafe
  transition; filtering out non-IDLE results would miss required cancellation.
  The transfer checks final IDLE, gate IDLE, zero outputs, no faults, current
  LOG_DUMP selection and a genuine fresh request itself.
- Supply actual decision time and current time; age must be strictly below
  `TICK_US` before writes. Preserve Robot freshness/token identity and source
  summary/epoch, origin declaration, loss fields and `SENT_UNCONFIRMED` semantics.
- Include readiness sampling, formatting, UART work and applicable cancellation
  in truthful app timing; no uncounted side loop. D090 permits between-tick
  pumping with a current result, but D096 currently specifies passive early
  calls and no work outside S..C. Any such pumping would require an explicit
  contract amendment and timing accounting; it is not already implemented.
- Define terminal app-abort cancellation without inventing a new Robot result.
  An active packet cannot be left pending when Runtime/Transaction becomes
  passive. The reset-specific notification already exists; its use/reason on a
  non-reset owner fault must be specified rather than silently relabeled.
- Native `cancel` permanently poisons that owner. A later service request or
  software reset must not reconstruct/reinitialize it or imply clean framing.

This attachment can be developed and tested with host ports while target work is
pending. It can verify actual-app admission/refusal/cancellation, but cannot by
itself produce a successful postmatch dump: the current app cannot return a
retained completed attempt to current IDLE. Do not label this bounded attachment
end-to-end B8 completion. The following reset contract is the dependency for that
full success path.

## Local reset is a distinct missing app policy

`P2_app_runtime_contract.md:200-218` explicitly ends a clean STOP after one real
tail in a Runtime that is passive forever until actual reboot. Source matches:
`Runtime::completeEpoch` selects STOPPED; `step` then returns before clock or ADC
reads. Existing `test_app_runtime.cpp:403-437` checks both real sealing and passive
later calls. A local button gesture cannot be detected through that loop as-is.
`Transaction` exposes initialize/open/decide/finish/abort and const reports only;
its FAULT lifetime is also permanently passive by D095.

The component dump fixture's `resetPreserving` performs transfer notification,
recorder notification, Robot reset, Gate reset, previous-feedback clear and a
new genuine tick (`tests/fixtures/dump_fixture.h:168`). It does not exercise
Runtime, native source owners, a physical button decoder, cancellation recovery
or a user-visible reset gesture. It must not be copied and claimed as app proof.

Concrete missing semantics to settle, not assumed requirements:

1. The actual local-only trigger and its fresh observation path after terminal
   STOP, including how it remains distinct from STOP/start/service gestures.
   No reset command exists in RobotInput; Linux capture is deliberately receive-only.
2. Which app terminal states are eligible for logical reset and whether the
   result is a service-only evidence state or a rearmed full control lifetime.
   D095 FAULT and D096 STOP passivity require visible amendment if changed.
3. Native source lifetime after deliberate cleanup. QTR `Reader::cancel` makes
   an active read a reset-only FAULT (`line_qtr.h:61`), and begin is one-shot.
   Runtime records `sources_cancelled_` permanently; pending IMU cancellation is
   likewise terminal. A Robot reset does not restore these owners. Reconstructing
   native objects does not prove resource ownership or clear hardware faults.
4. Ordering and failure handling for Gate inhibition/reset, prior feedback,
   monotonic Robot tokens, recorder preservation, source clocks/eras, readiness,
   heading/bias and calibration bank. `MotorGate::reset` clears its fault only
   after inhibition succeeds; it is not a harmless state assignment.
5. Retain SEALED evidence after a completed tail; if a reset interrupts active
   recording, preserve the existing INTERRUPTED/loss semantics. Physical reset,
   reflash and power loss do not guarantee RAM retention. `Calibration::reset`
   restores defaults/version zero, so retaining or clearing a committed bank
   across logical app reset cannot be selected accidentally.

D051 allows the coordinator to choose and record engineering policy without a
new user question. This report does not adopt a trigger, relax a reset-only fault,
change an established test, manufacture physical grants or authorize motors.

## Calibration printing is a distinct wire-format boundary

The real formatter emits exactly
`QTR_WHITE_US[4] = {123U, 234U, 345U, 456U}; // us\n` with the actual values.
Runtime already exposes the successful Report; only the delivery policy is absent.
D089 explicitly leaves delivery to permitted bench output/IDLE evidence transport
and grants no new MATCH Bridge traffic. R2 still permits only IDLE log dumping.

The existing D090 dump grammar contains only BEGIN, SH/SR, FH/FR, EH/ER and END;
its CRC/count/order parser rejects extra text, including bytes after END. Appending
the snippet to this stream or writing it concurrently through the same native
owner would break the established receiver/protocol. Native `Port` is exclusively
owned and requires identical offered bytes until a pending packet completes.
Freeze a permitted output context, trigger/once-per-version behavior, ownership,
partial-send/cancel semantics and receiver representation before connecting the
formatter. Neither SUCCESS nor its one-call committed pulse establishes transport
delivery; no automatic edit of config.h follows from a RAM bank or printed text.

## Boundaries to keep visible in the next handoff

- D099/D100 corrected-wrapper target default/Immediate/MATCH/library and ELF
  acceptance are coordinator work; this report makes no new verdict about them.
- Setup grants are evidence obligations, not self-verifying booleans. Native UART
  device_init has documented unbounded setup-only TEACK/REACK waits. Actual clean
  decoder framing is unproved; MCU reboot alone does not prove recovery, and a
  router restart can reset the MCU. No automatic restart/recovery is authorized.
- Loaded RAM and complete worst-case 800 us remain unqualified for the final app;
  adding services needs actual final-source target/memory/startup review and
  complete-duration evidence. The synthetic D091 retained-memory result is not
  native UART or physical sensor/motor proof.
- SC-A physical A1 circuit/windows, SC-AJ clock accuracy, assembled B1-B8,
  physical calibration, PINMAP/EXPLAINED acceptance and human gates remain open.
  Production default button windows and all setup grants remain unconfirmed.
- First useful implementation handoff: freeze the optional post-Gate dump
  attachment and terminal cancellation contract, author additive actual-Runtime
  tests from it, then implement. Separately adopt the local reset/source-lifetime
  policy before claiming a successful retained postmatch app dump. Keep calibration
  transport separate from the existing strict D090 stream until its format is
  explicitly defined. Existing protocol/native source research need not be redone.

## Follow-up: feasibility of a local service-only reset

Read-only follow-up requested by the coordinator while it completes target
acceptance. No implementation, adopted decision or executed experiment follows.
The findings below narrow the required app contract; they do not reduce the final
P2/full-control scope. All four agent slots were occupied, so this inspection
remained local.

**Conditional answer:** existing component APIs can support a new service-only
app lifetime without reconstructing QTR, IMU, ADC, matrix, Gate or recorder.
There is no existing public Runtime/Transaction API that performs this transition.
With the unchanged Robot, that lifetime still needs actual fresh opponent GPIO
reads plus healthy A0/A1 evidence. ADC and matrix alone cannot honestly produce
initialized IDLE: `Robot::prepareInputs` (`fsm_robot.cpp:237`) latches STALE_SENSORS
on `opponent_fresh=false` and INVALID_CONTEXT on unavailable battery after init.
The existing opponent owner remains usable through `SourcePort::readOpponents`;
it is not canceled by Runtime's STOP cleanup. A service mode omitting opponent
reads would need a separate explicit core readiness contract, not invented
freshness or a synthetic all-clear mask.

### Reusable owner lifetimes

| Owner/API | What remains usable after a clean STOP tail | Limit that reset must preserve |
|---|---|---|
| `power::InputOwner::readButtons/readBatteryIfDue/applyButtons/applyBattery` | Runtime does not cancel ADC. The same healthy owner can keep making actual bounded A1 reads and due A0 reads; no second begin is needed. | No reset/recovery API. CONFIG/PORT/SETUP/ADC/CLOCK/SOURCE permanently suppress all future callbacks. An A0 fault also prevents A1; button gestures cannot recover it. |
| `power::Reader::readButtons/read` | Retained native pair profile and ownership support ongoing conversions. | Begin is one-shot. Retain both native and InputOwner sequence counters. Do not bypass InputOwner with direct A1 reads: its next expected sequence is exactly previous+1 modulo uint32. |
| `ui::decodeButtons` / `InputOwner::applyButtons` | Real A1 evidence can be decoded without advancing Robot or Menu, then later admitted by actual Robot decisions. | Decoder alone does not qualify a reset gesture. Unknown/overlapping/unconfigured windows cannot synthesize NONE. Current `BUTTON_WINDOWS_CONFIGURED=0` means no real-board gesture path is accepted yet. |
| `SourcePort::readOpponents` | Existing initialized GPIO owner can provide a real fresh snapshot each service epoch. | Preserve all seven status/mask/time checks. Missing or failed opponent evidence still stops unchanged Robot. |
| `UnoQMatrix::submit` | Existing initialized, healthy matrix owner can continue bounded rendering. | Do not call begin again or reconstruct it: boot ownership is global and never released. Keep actual forward app time; local matrix faults remain faults. |
| `Robot::reset` | Returns to BOOT with cleared logical admission/menu/STOP history while preserving `next_token_`. | Does not reset any HAL owner, recorder or app clock. First new tick must use real current input, not replay the final STOP input. Exhausted next-token zero remains exhausted. |
| `MotorGate::apply` with existing `fault()==STOPPED` | A valid fresh IDLE/zero command is consumed, executes `inhibit()`, and produces an acknowledged zero receipt if inhibition succeeds. STOPPED stays latched. | Requires the existing initialized Gate and working native output callbacks. Other Gate faults do not take this acknowledged STOPPED path. Never fabricate `applied_valid` after a failed inhibit. |
| `MotorGate::reset` | Can inhibit, clear fault/armed/hold/halt state, and keep native setup plus `last_token_`. | Clears the STOPPED latch, so it is unnecessary for service-only zero receipts and is a larger recovery choice. It is not full native source rearm or motor permission. |
| `AttemptRecorder::consume/onRobotReset` | Same recorder preserves SEALED bytes/summary through logical reset. Fresh IDLE tokens update its private token high-water and return OUTSIDE_ATTEMPT without changing retained summary. | Do not reconstruct it. Only a valid later accepted match START may erase the old epoch. Active/DRAINING interruption must retain existing INTERRUPTED semantics. |
| `Transfer::onRobotReset/step` and `UnoQDumpPort` | Inactive reset notification preserves transfer chronology/request high-water; later actual IDLE LOG_DUMP can start from the retained source. | An ACTIVE reset cancels and poisons the native owner. Preserve poison/global UART ownership; no new begin or implicit decoder recovery. |

The Gate observation is important: `motors.cpp:165-201` explicitly permits
`Fault::STOPPED` through command validation, then calls `inhibit()` and sets
`feedback.applied_valid` from its real result. It does not require a Gate reset
for truthful inhibited IDLE receipts. `Transaction::applyDecision` accepts such
consumed, correctly tokened receipts; Robot checks their validity on the next
decision. Thus resetting **Robot only**, while retaining the stopped Gate, is an
existing-component alternative the coordinator can consider. This report does
not select it. If Gate reset is selected, test its return value/failure and ensure
the service lifetime still cannot issue a match release or enabled request.

### How unchanged Robot can reach actual service IDLE

After a genuine logical reset, a correctly timed first explicit input can reach
BOOT -> IDLE with these honest values:

- Fresh actual A1 evidence, healthy available battery, actual fresh opponent
  snapshot, and `initialization_complete` based on the newly defined **service**
  prerequisites rather than a claim that QTR/IMU control has restarted.
- Canonical explicit QTR `LineUse::CALIBRATION` with ABSENT evidence. Existing
  `prepareCalibrationLine` allows this in BOOT/IDLE, publishes no color and keeps
  `line_calibration_hold` / match-start inhibition active indefinitely. No fake
  raw frame, threshold bank or black classification is needed.
- Explicit unavailable IMU with canonical empty fields; missing IMU is already
  permitted at boot. Retain old source/shutdown diagnostics separately rather
  than republishing an old estimate as fresh or resetting the native Acquirer.

This is a feasible projection shape, not permission to hide an actual provider
fault. The new contract must distinguish intentionally excluded/stopped sources
from earlier real QTR/IMU faults and retain their diagnostics. D096 already treats
deliberate cleanup as diagnostic shutdown for its one tail, but does not authorize
an indefinite service-only projection. Its existing `project` initialization
prerequisites, `selectLineMode`, cancellation flags and post-STOP behavior must be
amended explicitly. In particular, a retained confirmed calibration bank currently
makes `selectLineMode` choose CONTROL in ordinary IDLE; a service lifetime must
not accidentally drop its inhibition when the menu leaves QTR_CAL or services.

Robot's real Menu then needs its ordinary fresh neutral qualification, long MODE
to enter services, three short MODE actions to reach LOG_DUMP, and a fresh START
press/release. No setter selects a service. BOOT entry cannot emit a menu action;
held-at-reset START cannot start/dump until fresh neutral rearming. Raw-mode
match-start inhibition does not suppress genuine service START events: Controller
still publishes button events while `allow_match_start=false`, and Menu consumes
the qualified release. Leaving services and pressing START must remain harmless
throughout the service-only lifetime. BOTH still invokes STOP; dump cancellation
and any second service-reset policy must be defined without bypassing that stop.

### Necessary explicit app-contract changes

1. **Post-tail observation and local reset authority.** D096 currently permits no
   clock, ADC or button work after its final tail. Define a bounded service/reset
   observation phase, actual local gesture, fresh-sample qualification and allowed
   entry reasons. Do not repurpose remote data, LOG_DUMP intent or mere elapsed
   time as reset authority. No gesture is selected by this report.
2. **Transaction transition.** Add a guarded owner operation at a completed IDLE
   transaction boundary; current private Robot/Gate cannot be reset through the
   public API. Define whether only a clean completed STOP tail qualifies, and
   separately handle D095 FAULT, unfinished epochs, failed motor receipts and
   exhausted token state. Calling `initialize` again is not a reset implementation.
3. **Ordering and evidence.** Revoke an active Transfer before any reset/source
   mutation; preserve or truthfully interrupt the recorder; keep genuine final
   tail receipts. Reset logical Robot and clear previous application feedback so
   it cannot attach to a post-reset result. Retain Robot next-token, Gate last-token,
   recorder token high-water and source object identity. Retain app/native clock
   chronology; no micros-zero rebase or native object reconstruction is needed.
4. **Retained source timing.** Use the same InputOwner for reset observation and
   service decisions. Preserve exact A1 sequence, real conversion brackets and
   A0 source ages. Once Robot is active, its A1 inter-observation/decision gap must
   stay at most 5,000 us; replay never advances gestures. Keep InputOwner/app
   observations less than half uint32 range apart. A long unobserved wait cannot
   be cured by resetting a clock anchor. Expired healthy battery can be refreshed
   by a real due A0 read; ADC faults cannot be refreshed or reset away.
5. **Permanent service inhibition and availability.** Declare which actual source
   prerequisites admit service IDLE, how QTR/IMU stay excluded with diagnostics
   retained, and which requests are unavailable. No QTR/IMU begin/start/advance,
   calibration capture or full-control rearm follows from a service reset.
   Preserve the committed calibration bank for inspection unless a separately
   explicit policy changes it; `Calibration::reset` would erase it. Do not imply
   that an unavailable service action ran just because Menu emitted an intent.
6. **Actual output and transport failures.** Feed actual inhibited Gate receipts
   and current clocks into normal Transaction accounting. A failed current inhibit
   cannot certify safe service output; define immediate service/transfer failure
   handling without awaiting a fabricated later Robot decision. Preserve native
   UART poison and initialization restrictions. All added work needs complete
   execution timing and final-source memory/link review.

### Additive test boundaries for that contract

Tests should compose actual Runtime/Transaction/Robot/Gate/recorder plus scripted
native-source boundaries, not copy only the old direct-component reset fixture:

- Clean STOP -> real final tail -> retained SEALED attempt -> locally qualified
  service transition -> genuine BOOT/IDLE/menu/LOG_DUMP -> unchanged bytes/summary,
  exact stream and independent receiver validation. Check zero enable/nonzero
  writes with both `MOTORS_ALLOWED` settings.
- Retained STOPPED Gate receipts versus explicit Gate-reset variant; every inhibit
  failure, prior IO/PORT/TOKEN fault, transaction FAULT, unfinished tail, token
  exhaustion, duplicate reset and reset during a native pending dump packet.
- A1 reads use one unchanged native/InputOwner sequence across STOP and reset,
  including natural wrap; no second begin or hidden caller. Cover unavailable
  configuration, unknown/overlapping windows, stale/duplicate evidence, 5,000 us
  adjacent boundaries, clock reversal/half-range, held reset buttons and fresh
  neutral/menu rearming. A0 fault must prevent A1 recovery and stale voltage use.
- Assert no QTR/IMU acquisition/setup/reconstruction after entering service mode;
  preserve cleanup/provider faults, old bank and source diagnostics. Genuine
  opponent failure must prevent unchanged Robot service IDLE. Matrix remains
  the original owner; failure never certifies display or motor availability.
- Leaving the service menu, every match-mode START, DRIVE_TEST/QTR_CAL requests,
  repeated BOTH STOP, and all menu reset paths cannot begin a new match/erase the
  retained attempt or restart motion in the service-only lifetime.
- New actual decision tokens/time and Gate receipts remain ordered across natural
  clock wrap and reset; retained recorder summary/loss/source identity stay
  stable during inactive consumes and active Transfer checks. Do not count a
  logical reset as a hardware reset-cause observation.

Complete app rearm is not currently supported by the existing owner APIs after
all possible STOP cancellations: QTR and active IMU cancellation are terminal,
ADC faults are shared/reset-only, matrix/UART use boot lifetime claims, and no
coordinated restart exists. A service-only recovery contract can add useful
retained-evidence access without claiming or replacing eventual full application
rearm, physical acceptance or the original project scope. It remains physically
blocked by unverified A1 circuitry/windows and grants even if its host tests pass.
