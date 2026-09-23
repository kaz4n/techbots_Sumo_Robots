# D089 preparation: QTR_CAL IDLE admission and threshold handover

2026-09-23 Asia/Dubai. Read-only source analysis against the D088 checkout;
`Get-Date` returned `2026-09-23T15:46:27.6639198+04:00` during this audit.
PLAN section 3 schedules P0/P1 today and P2 bench work on 24-26 September;
D075 permits current P2 software work before hardware acceptance. The only
owned modification is this analysis file. No test was run, production/test file
changed, MCU contacted, physical fact established or phase gate passed here.
Recommendations below are not adopted decisions. Root owns D089's final public
contract and the calibration consumer/raw-bank design independently.

## Exact current path and why the first intent can be unreachable

1. `src/core/fsm_robot.cpp:77`, `Robot::step`, first suppresses duplicate decision
   timestamps and clears action pulses through `clearActions` (`:57`). A new tick
   runs `admit`, `receive`, `advanceHistories`, `prepareImu`, **`prepareLine`**,
   `prepareButtons`, `prepareInputs`, `sampleSensors`, `runLifecycle`, `runEscape`,
   motion/governor, warnings, then `finish`. No menu decision precedes line admission.
2. `src/hal/line_qtr_adapter.cpp:83`, `complete`, validates a structurally valid
   bounded native raw record. `classify` (`:113`) compares it with config defaults.
   `applySnapshot` (`:125`) maps both optical ambiguity and known native provider
   failure to `LinePresence::INVALID` with `contract_valid=true`. Thus that pair
   cannot distinguish an allowable raw optical interval from a native fault.
3. `src/core/fsm_line.cpp:45`, `Robot::prepareLine`, fixes legacy/explicit mode
   on the first admitted tick. `admitLine` (`:23`) rejects INVALID. `prepareLine`
   also rejects missing/expired accepted line history on an initialized tick or
   the first `initialization_complete` tick. Both routes latch LINE_CONTRACT.
4. `src/core/fsm_robot.cpp:275`, `runLifecycle`, sends any contract fault into
   Lifecycle's STOP input. Match `allow_start` uses IDLE-at-entry, initialized,
   fault-free and non-service selection. The final fault path selects STOPPED.
5. `src/core/fsm_robot.cpp:871`, `finish`, calls `Menu::stepObserved` exactly once,
   using original entry state, existing button timing, and actual Lifecycle
   `buttonEvents().start_release`. Final fault, STOPPED or escape fault inhibits
   the menu. `src/core/countdown.cpp:437`, `Menu::stepObserved`, emits QTR_CAL only
   for current IDLE-at-entry, noninhibited, fresh qualified START release with
   raw logical NONE and the service selected. It consumes rather than queues it.

Consequently, admitting raw observations only after the first QTR_CAL request is
too late: normal startup/navigation or repositioning can cross the old threshold,
latch LINE_CONTRACT, stop Robot and suppress that first request. Resetting Robot
afterwards would erase safety history and is not a permissible implicit repair.

## Smallest explicit boundary to freeze

Use one additive, opt-in calibration-preparation input/step option, defaulting to
ordinary behavior. Keep it distinct from a START request. It expresses that the
caller is deliberately running a motor-inhibited calibration workflow; it never
means that the operator selected a service or requested a sample. Exact type and
names belong to the final public contract. An enum makes unsupported modes easier
to reject than several independent booleans.

- Permit initial entry only from BOOT or IDLE with no existing contract fault,
  STOP latch or escape fault. Include the first BOOT-to-IDLE initialized tick;
  otherwise startup's absent/ambiguous old-threshold line still prevents entry.
  Reject an attempt to enter from COUNTDOWN/motion/STOPPED. An entry rejection
  must never downgrade or clear the original fault. Do not permit mode changes
  from legacy to explicit line representation without the existing real reset.
- Permit actual long-MODE navigation into the service menu and short-MODE
  selection of QTR_CAL while this option is active. The default menu starts in
  match view and entering services selects SENSOR_VIEW, so requiring QTR_CAL
  to be selected on initial raw-only entry creates the same reachability defect.
- Suppress **match** `allow_start` from the first opted-in tick and throughout
  handover, even while the menu still shows a match item or the user exits
  services. Keep the actual Controller/StopHold, button evidence admission,
  receipt validation, unrelated fault checks and single Menu call running.
  A calibration-only entry must leave no retained READY/GO authority.
- Publish explicit raw-only/unavailable line diagnostics: `line_available=false`
  and `line_updated=false`. Never send an ambiguous interval through legacy
  `line_raw_us`, assign fake black, call `publishLine(0)`, or present a cleared
  mask as a new observation. Preserve source identity separately from color.
  D088's `displaySample` already respects `line_available` for unknown sensors.
- Give raw admission a distinct validated result from the shared raw validator.
  A blanket exemption for `INVALID` is unsafe because it also covers provider
  failure. Malformed metadata, native provider/cleanup failure, conflicting or
  reversed identity, invalid source span/age and mode mixing remain faults.
  Pending/ABSENT may wait without becoming measured color; collection deadlines
  belong to the consumer. Do not claim old raw data remain fresh while waiting.
- Raw-only handling must preserve every pre-existing fault bit and STOP latch.
  `Robot::receive` (`fsm_robot.cpp:133`), `prepareInputs` (`:212`) and
  `prepareButtons` (`fsm_buttons.cpp:61`) remain authoritative: calibration is
  no exemption from actual disabled receipts, opponent freshness, battery
  validity, heading validity, button continuity or qualified STOP.

This needs a small explicit branch around line admission and match-start
eligibility, plus a persistent handover-inhibition state. It does not require a
second Robot, a second menu, a generic service router or a second debounce path.
Ordinary callers that never request it continue through the exact D085 rules.

## Transaction order and later threshold activation

The calibration consumer should run **after** the actual Robot result, so it can
require a fresh unconsumed token, final IDLE, disabled/zero requested outputs,
no contract/escape fault, active service menu/QTR_CAL selection and the genuine
`menu.request==QTR_CAL` pulse. The raw-only preparation option itself starts no
capture. Same-tick STOP/fault/menu exit wins before collecting/committing. The
consumer must not invoke `Menu::stepObserved` or `Lifecycle` a second time.

Suggested call order for the future owner:

1. Service the existing Reader and pass its unchanged Snapshot through the
   shared raw validator. Produce either raw-only evidence or qualified color
   evidence from one explicitly selected bank; do not run two native acquisitions.
2. Step Robot once with the caller's explicit workflow request, actual raw/line
   evidence, other fresh inputs and previous actual MotorGate receipt.
3. Step the bounded QTR_CAL consumer once using that final Robot result and the
   same raw Snapshot/validated evidence. It may advance capture or publish one
   atomically committed RAM bank; it cannot revise this tick's Robot result.
4. Apply the current Robot request through the existing MotorGate and retain its
   actual receipt. A zero request still needs acknowledged application evidence.

An atomic bank commit is distinct from activation for motion. On raw-only entry,
invalidate only qualified color/confirmation/warning readiness for subsequent
handover; do not clear `faults_`, Lifecycle, Escape faults, button history, source
ordering, token high-water or application receipts. `Classifier::reset` in
`src/core/edge.cpp:45` is the narrow color-counter primitive; `Robot::reset`
(`fsm_robot.cpp:913`) is deliberately much broader and must not be used.

Latch motor/match-start inhibition when raw-only preparation begins. Ending the
caller's request or leaving QTR_CAL must not itself restore normal readiness.
Requalify in IDLE using an explicitly identified committed bank and a **later
acquisition**, with source start after the commit/handover boundary and advancing
sequence/time relative to the retained raw history. A cached last capture frame
reclassified under new thresholds is not a new frame. Preserve the old raw record.
Reject a changed bank under an unchanged classified identity. Rebuild classifier
confirmation only from distinct qualified post-handover frames; QTR_CONFIRM_TICKS
must remain effective when configured above its current default of one.

Once the new qualified line state is available, clear only handover inhibition;
do not clear a safety fault. At minimum the requalifying tick must still suppress
match START, and subsequent match START must be a new qualified press/release.
A held or already-qualified START from preparation must not spill into countdown.
Final contract should choose and test a fresh NONE rearming interval or a narrowly
scoped gesture-cancellation boundary; it must not reset a latched STOP. If
requalification remains absent/ambiguous, stay explicitly motor-inhibited; known
native/malformed/ordering faults remain faulted. Changing the bank or retrying
calibration is no fault recovery. Explicit default-bank requalification is needed
after cancellation too, even when no calibration bank was committed.

## Established assertions to preserve unchanged

| File and test entry | Binding constraint |
|---|---|
| `tests/locked/test_menu_routing.cpp:133` | Every genuine service START stays IDLE without match gyro calibration, heading reset or motion. |
| Same file `:153`, `:166`, `:183`, `:319`, `:332` | No replay/deferred GO; fresh NONE before MODE; exit followed by a new match release gets the complete hold; each new service intent is genuine; wrap remains valid. |
| Same file `:235`, `:259`, `:279`, `:292` | Countdown cancel is not a menu gesture; final STOP/fault suppresses request without queueing; logical BOTH remains live in every context. |
| `tests/locked/test_countdown.cpp:200`, `:243`; `test_countdown_integration.cpp:234`; `test_countdown_lifecycle.cpp:249` | Literal five-second minimum/full configured hold; reset-only STOP; STOP wins on GO and before service sampling. |
| `tests/locked/test_edge_guard.cpp:104`, `:113`, `:177`, `:191`, `:215` | No new edge fault before GO; existing all-white fault remains reset-only; persistent white matters on exact GO; STOP outranks edge. |
| `tests/locked/test_edge_escape.cpp:525`, `:545` | Permission loss does not erase existing escape faults/budget; an existing line fault survives closed permission. |
| `tests/locked/test_motor_gate.cpp:499`, `:514`, `:573`, `:598`, `:652`, `:849` | IDLE consumes old release authority; a later match needs a full new hold; STOP recovery is reset-only; reset preserves token identity; every inhibited state/fault gates motors; actual Robot receipts are used. |

Also preserve these nonlocked production regressions unchanged:
`tests/test_qtr_integration.cpp:33,37,41,46,52,59,80` (expiry/initialized absence,
replay, immutable representation, source admission, retained-white GO and
configurable confirmation); `tests/test_qtr_adapter.cpp:26,38,43,51` (ambiguity,
malformed raw records, exact bounds and pending absence); `tests/test_robot.cpp:87,
288,313,332,372,387` (service intents, duplicates, reset identity, receipts, stale
sensors and battery); `tests/test_button_routing.cpp:112,231,240,254,309,355,364`
(button faults/mode, arming, full hold, genuine services, STOP and receipt priority).

New independent D089 cases should start with valid raw intervals ambiguous under
the old defaults on the first initialized tick, navigate the real Menu, and
deliver the first and subsequent QTR_CAL requests without fake black. They should
also exercise pre-existing LINE_CONTRACT/STOP refusal, requested entry while
moving/counting down, STOP/fault on capture completion, cancellation/handover,
cached-frame/new-bank rejection, replay/source wrap, configurable confirmation,
fresh post-handover START and actual MotorGate zero receipts. The current locked
menu harness composes Lifecycle and Menu rather than the full Robot, so passing
it alone cannot establish the new Robot admission boundary.

## Scope limits and next action

This is a source-derived recommendation, not implemented or test-validated D089.
It establishes no optical separation, A1 windows/START-BOTH distinction, physical
pin order, native timing, full-tick WCET, app integration, transport/printing or
motor-run permission. The inert app remains a separate unfinished integration.
Root should freeze the chosen admission/handover public contract and record the
material D089 choice before independent implementation and spec-derived tests.
