# D087 button routing source audit

2026-09-23 Asia/Dubai. Read-only audit of the D086 baseline for the coordinator's
button decoder/evidence work. This file is the only modified artifact. No source,
test, configuration, physical threshold, wiring or gate was changed. Date checked
with Get-Date; PLAN section3 originally scheduled P0 acceptance on23September;
D051/D075 permit this active P2 software work without granting a physical gate.

## Exact integration points

- `src/core/types.h:15-16,44-56`: ButtonLevel has only NONE/START/MODE/BOTH;
  Inputs has only button_level. Add explicit evidence append-only with a legacy
  default; do not reinterpret unavailable samples as NONE or any legal level.
- `src/core/fsm.h:402-423`: RobotInput similarly has only `button`; IMU and line
  evidence are existing append-only precedents. Actual Robot implementation is
  `src/core/fsm_robot.cpp`, not the older behavior helpers in `fsm.cpp`.
- `src/core/fsm_robot.cpp:76-98`: one admitted decision transaction calls sensor
  admission, lifecycle, escape/motion and finish. Admit button evidence before
  `runLifecycle`, and feed that single admission outcome to both lifecycle and
  the menu; do not independently advance/reinterpret decoder identity twice.
- `src/core/countdown.cpp:116-124`: Controller currently observes Buttons and
  StopHold every call, then advances Gate. Explicit missing/replayed observations
  must skip button evidence qualification, but Gate must still receive current
  decision time and genuine external STOP. This separation preserves D019 hold
  anchors and D057 active-countdown progress. A skipped Controller call would also
  incorrectly suspend Gate, cancel handling and STOP routing.
- `src/core/countdown.cpp:277-298`: Lifecycle constructs a new Inputs from the
  supplied logical level, so adding RobotInput evidence alone cannot reach
  Controller. Propagate the admission in this call boundary. Services still
  advance at decision time; a canceled/stopped pending attempt is canceled before
  the current sample is consumed. A late fault must not leave a false GO pulse.
- `src/core/fsm_robot.cpp:273-287`: match START is allowed only in IDLE-at-entry,
  initialized, fault-free and match view. Preserve this routing and snapshot
  running mode only in `beginAttempt` (`:256-267`). A service START must remain a
  consumed qualified snapshot rather than a deferred match release.
- `src/core/fsm_robot.cpp:867-871`: menu sees entry state plus final inhibition and
  the lifecycle snapshot. Carry explicit freshness/interruption here as well;
  otherwise it can qualify MODE or service requests from a cached level.

## Qualification and interruption pitfalls

- `countdown.cpp:39-73`: Buttons uses absolute candidate time and emits release
  after NONE qualifies. Passing a failure as NONE can produce START release.
  Merely omitting calls is also insufficient: the next fresh sample can span an
  unobserved interval. Admission needs an explicit bounded-continuity rule and an
  interruption path that clears pending press/release qualifications.
- `countdown.cpp:41-45`: first observed NONE immediately arms legacy Buttons;
  Menu instead requires a complete NONE debounce (`:371-389`). Preserve old
  callers exactly. Explicit boot/recovery policy must not accidentally turn a
  default NONE, absence, replay, or interrupted NONE into arming evidence. A reset
  followed by START remains boot-held and cannot release-start. Freeze whether
  explicit initial NONE also needs qualified continuity before implementation.
- `countdown.cpp:80-111`: StopHold accumulates elapsed call time in two stages;
  its full long hold starts at the actual debounce-qualification call, not the
  raw BOTH edge. Replayed BOTH must never advance either stage. A discontinuity
  should clear only pending stages; already STOPPED must survive interruption.
  Calling `StopHold::reset` indiscriminately loses this component's reset-only
  latch, even if Gate happens to retain a separate STOP latch.
- `countdown.cpp:316-325,347-421`: Menu accumulates observed call deltas, so skipping
  stale data alone still bridges gaps. Its private disarm preserves selection;
  public reset (`:425`) resets mode/view/item. Expose a bounded interruption
  operation or equivalent internal routing that preserves selection, clears the
  gesture/pulses and requires fresh NONE arming. Preserve release-at-long-deadline
  precedence and COUNTDOWN-at-entry cancellation semantics.
- `countdown.cpp:393-399`: duplicate decision timestamps return before observing
  changed menu data. `fsm_robot.cpp:76-81` similarly clears pulses and returns a
  cached result on a duplicate timestamp, before all sensor admission. Preserve
  this existing behavior; distinguish source replay/conflicting identity on a
  later decision from an already-ignored duplicate decision tick.
- Keep ADC start/completion, source sequence and decision timestamps separate.
  A fresh source can advance existing button qualification only on a fresh
  accepted decision; accepted release/STOP anchors remain the decision call, so
  delayed delivery never backdates the five-second hold or long-press interval.

## BOOT, fault and recovery hooks

- `fsm_robot.cpp:210-215`: initialization_complete latches initialized forever
  until reset, then requires fresh opponent/legacy observations and valid VBAT.
  Do not use observations_fresh to represent button absence: it governs different
  sensors and creates STALE_SENSORS. Explicit button BOOT waiting needs its own
  admission/availability condition and deliberate init-complete semantics.
- `fsm_line.cpp:45-83` is a concrete reference: mode is selected once, switching
  modes faults, source age is accumulated independently of delivery, and missing
  evidence can wait during BOOT but faults on initialization. Do not copy its
  retained-white policy into a button edge/hold consumer.
- `fsm_robot.cpp:286-287,312-315,664-705`: a new button contract fault recorded
  before Lifecycle follows existing external STOP routing, same-tick motor
  inhibition and disabled STOPPED state. It cannot recover from later healthy
  observations. `Robot::reset` (`:907-910`) clears runtime faults/evidence while
  preserving monotonic output token identity. MotorGate has a separate reset.
- `fsm.h:386-390`: current contract bits occupy1 through256, including
  LINE_CONTRACT256. Coordinator's proposed BUTTON_CONTRACT512 fits uint16.
  A fault must be surfaced even if cached valid level remains in a diagnostic.
- `fsm_robot.cpp:57-73`: duplicate-action clearing should include any new
  button-updated pulse; a retained availability/status is not a new observation.

## Recorder compatibility issue requiring an explicit decision

Existing LINE_CONTRACT256 cannot currently be recorded as canonical contract-fault
metadata. `logframe.cpp:177-188`, specifically184, accepts CORE_CONTRACT_FAULT only
for value1..255. `logframe.h:87-90` documents bits0..7. `fsm_robot.cpp:786-791`
reports new full uint16 fault bits once and marks them reported before append
failure; `:119-122` turns rejection into recording_incomplete. Therefore line256,
proposed button512, or combined masks containing them lose the intended fault
event under the existing validator.

The same semantic validator is applied again by
`src/hal/recorder.cpp:101-120` when an attempt owns events. Fixing only Robot's
append path is insufficient. `AttemptRecorder::observeSummary` (`:138-154`)
preserves recording_incomplete but does not retain the lost numeric fault reason.

**Established test conflict:** `tests/test_robot_events.cpp:425-442` explicitly
asserts that FAULT/detail7/value256 is invalid (literal at439); line417 accepts255.
This file is outside `tests/locked`, but it is an established assertion. No512
rejection was found. The coordinator must explicitly choose/version the metadata
extension or authorize a narrowly justified specification migration; silently
widening the validator cannot preserve this assertion. Preserve every locked test.
If D087 adopts known bits0..9, reject every bit outside0x03ff, preserve rejection of
zero, and retain tests of reserved values. Do not generically allow uint16 maxima.

No wire-size change is needed: `logframe.h:106-108` already stores event value as
uint16 in8bytes. `recorder_csv.cpp:184-193` writes the raw uint16 and all8bytes.
`tools/validate_csv_bundle.py:65-66,149-168` admits uint16 event values and checks
numeric fields against raw bytes, without interpreting this semantic fault mask.
That file should keep format integrity separate from semantic validation.

B15 frames do not store the contract mask: `fsm_robot.cpp:831-851` stores state,
sensor values, requested data finalized by actual feedback, and sensor/status
flags. STOPPED is visible in a final frame, but a frame cannot recover the lost
button/line fault cause. `:814-853` schedules a final stopping frame and stops the
attempt; do not assume events before START are retained by the attempt owner.
An event-mask-only extension need not change25byte frames,8byte events, CSV schema,
or21event capacity if it uses the existing combined contract-fault event.

## Actual MotorGate verification boundary

- `src/hal/motors.cpp:107-139`: gate independently observes accepted release,
  decision-time full hold, permission, faults and output shape. Explicit button
  failure should reach it as a real disabled RobotResult, not as invented motor
  feedback or a standalone assertion about Robot.outputs.
- `motors.cpp:142-162,165-196`: actual production MotorGate drives checked callback
  writes, zeros/inhibits on STOP and returns actual application receipt. In host
  tests fake the port callbacks, then feed this receipt to Robot's next call;
  this exercises EN/PWM zero writes while preserving application identity.
- `host/CMakeLists.txt:13-22` compiles production motors.cpp into the default
  MOTORS_ALLOWED0 suite. The separate host-only enabled target (`:33-48`) currently
  includes only locked/test_motor_gate.cpp. A new nonlocked button integration
  test must also be included in that enabled target if it is to demonstrate
  inhibition after actual host-simulated enable. It must remain unstaged firmware.
- `tests/locked/test_motor_gate.cpp:850-879,883-905` already demonstrates real
  Robot/Gate receipt pairing and both-component reset; use that pattern without
  changing the locked file. These software callbacks do not establish pin
  voltage, physical output, motor-run permission, or MCU timing.

## Required next evidence

Freeze the source-admission/continuity/expiry/reset/public API contract, including
the metadata compatibility choice, before independent tests. Tests need fresh
NONE/START/release, boot-held input, absent/invalid/ambiguous transitions, replay,
conflicting/reversed/wrapped identity, delayed delivery, exact continuity expiry,
STOP/menu fresh-only timing, preserved menu selection, same-tick fault inhibition,
fault/recorder preservation, and actual MotorGate callbacks in both host modes.
No new physical voltage windows or timers are selected by this audit. HARDWARE5.6
(`docs/HARDWARE.md:140-147`) gives identical nominal0V START/BOTH; SC-A remains open.
App scheduling, matrix adapter, MCU runtime/WCET and all physical gates remain
outside this source assessment.
