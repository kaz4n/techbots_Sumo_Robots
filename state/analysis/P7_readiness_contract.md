# D138 proposal: informational pre-start display

2026-09-24 Asia/Dubai. Relevant original work: P7.2 pit READY and battery check,
B13 mode/fault/battery layout, D088/D108 display and D087 button qualification.
The continuation audit found implementable software missing despite deferred
hardware acceptance. D137's document-only checkpoint did not implement this gap.
This proposal needs coordinator adoption after separate design review; no human
physical acceptance or motor-run permission is inferred.

## Purpose and ownership

Preserve the exact actual START/hold/governor/MotorGate behavior. Add observations
of existing admission and genuine current application context, then display them.
Neither observation is an input to control or a new motion permission. Keep core
pure C++17 and bounded work; no allocation, clocks, I/O, new setup grant, pin,
tunable, profile, wire event or new transport. Existing default-off hardware
grants remain unchanged. No adapter/startup/deployment changes in this task.

Root owns interfaces, host integration, decisions and evidence. A worker owns
only countdown.cpp, fsm_robot.cpp, runtime_inputs.cpp and ui_display.cpp implementation. A separate
test author reads contract/public headers/test fixtures, not implementation;
freezes new tests before first implementation execution. Existing tests, including
all43protected code files, remain unchanged. Separate scoped source review follows.

## Public informational fields

Add `bool neutralStartArmed() const` to countdown::Buttons, Controller and
Lifecycle. Buttons reports its actual existing initialized, armed, unpressed,
stable-NONE and candidate-NONE state; Controller and Lifecycle only forward this
observation. It does not sample, mutate, debounce, include the Gate phase or
grant permission. D087's initial-neutral qualification alone is not enough:
after a qualified MODE, the real Buttons controller must also qualify NONE again.

Append `bool match_start_eligible = false` to fsm::RobotResult. This means the
current, fresh, explicit button observation is a qualified neutral observation
at which the ordinary match START route is available. It is not countdown::READY,
which still means post-hold permission. It is not proof that START occurred,
hardware is accepted, the target is healthy, a tick completed or motors may move.

Append to ui::DisplaySample:

- `bool start_status_available = false`: actual Runtime paired this display
  sample with its current decision/application context. Pure displaySample alone
  leaves it false; a caller cannot obtain runtime evidence from RobotInput/Result.
- `bool start_ready = false`: actual Runtime's informational predicate below.

Unbound samples (start_status_available=false) preserve every established D088/
D108 pixel and status, even if start_ready=true. No new public mutating API.
Add a private Runtime helper declaration only if needed to keep functions short.

## Core observation: reuse existing admission

Publish match_start_eligible from the actual `allow_start` used by runLifecycle;
do not introduce another gate or change that expression/call. Combine its true
value with the existing D087 current button facts: explicit mode, available and
new observation, NONE level, and the existing neutral/start_ready qualification,
plus the actual Lifecycle neutralStartArmed observation after its real step.
The final result must also be fresh, final IDLE in the match menu, Gate IDLE with
no release/GO/motion permission, zero/disabled intended outputs, no contract or
escape fault, and no RAW calibration/line handover/rearming state. The emitted
eligibility is false in every non-default bench/evidence profile (B4 stand,
P3 drive/turn/stop, P4 reactive/timing, P5 abort timing).

Re-evaluate each real step; clear on every passive/repeated/invalid-time/exhausted
call and reset. Never retain a previous true value as a current observation.
Qualification at the exact configured neutral debounce boundary is eligible;
one earlier distinct source observation is not. A current press is not neutral.
Every current MenuResult selection_changed or menu_toggled suppresses the metadata
for that step, including a short cycle between ordinary match modes.
After a menu transition or countdown cancellation, the first possible true result
is a subsequent admitted step whose existing allow_start was true. Keep legacy
nonexplicit button control behavior unchanged; its new metadata stays false.

Do not independently qualify/debounce buttons or change line admission. Current
white need not change core START routing; display all-clear conditions below
can withhold the indicator without changing actual control.

## Runtime observation: current actual owners

The current display projection remains at its original post-application point
inside S..C. Set start_status_available only for a fresh Robot result at the
current DECIDED Transaction with a nonzero matching token and genuine consumed,
valid applied receipt. Reuse the existing receipt checks as appropriate; never
accept an intended output in place of the actual receipt. Faulted/inconsistent
context yields no new status. This does not require completion C, which has not
happened yet; do not invent completed timing.

Set start_ready only when all of the following also hold:

- MOTORS_ALLOWED=1 and every non-default bench/evidence profile is disabled.
- Runtime RUNNING with fault NONE, not service-only, no pending service reset,
  initialization complete, and source cancellation has not occurred.
- Current Transaction fault NONE and actual MotorGate fault NONE (STOPPED is
  insufficient), matched actual feedback zero/disabled, and genuine inhibited
  IDLE/Gate-IDLE context with no release/GO/motion permission. Reuse the existing
  inhibitedIdle and receipt predicates without broadening their control meaning.
- Current Robot match_start_eligible, selected match menu and enabled mode;
  classified available line data, no RAW/calibration/handover/rearming flags;
  fresh opponents and button observation. The genuine owners already enforce
  chronology/age; never refresh a timestamp or infer absent evidence as black.

Use the current already-observed clock for existing age predicates, not a new
clock call or an invented future time. start_ready is still only a candidate;
the renderer's current battery/line/fault checks below decide whether R appears.
M0 Runtime may expose current battery status but never supplies start_ready=true.
The pure renderer is configuration-independent: synthetic direct samples may
supply true in either host build and are tested against the same literal pixels.
This task must not change decisionInput, Robot outputs, recorder records,
source grants, control timing anchors or any native write order.

## Exact display extension

Only when start_status_available=true, state=IDLE and service_menu=false:

1. Row6,column12 (zero-based) is the exact battery threshold indicator:
   unavailable=0, available finite voltage strictly below VBAT_WARN_V=3,
   available voltage at or above VBAT_WARN_V=7. Compare the original float value
   directly; do not round to the13-step battery bar or use latched LOW_BATTERY.
   Existing invalid-input handling still applies for malformed available values.
2. Draw pre-start `R` in the right3x5 region x10,y1..5 only if start_ready=true,
   battery available and >=VBAT_WARN_V, opponents_available and lines_available,
   line_mask=0, and faults=0. R's literal row masks are [6,5,6,5,5]. It is visible
   only on even `(t_us / 1000 / UI_FAULT_PAGE_MS) % 2`; odd pages leave the region
   blank. Reuse the existing500ms display-page constant without changing it.

The live blinking R is the defined READY symbol for this proposed P7 procedure;
a static glyph alone is not readiness. It preserves the B13 mode digit/icon and
all13battery pixels. It adds no GO indication and has no relation to the existing
countdown::Phase::READY. Battery marker remains at its current threshold state
on both blink pages. All other row6 pixels remain their original values.

No extension in service views, BOOT/COUNTDOWN/STOPPED/motion states, or invalid
frames. Fault icons and exact existing sensor/calibration layouts retain priority.
No READY indication when any diagnostic fault is present, including permitted
IMU fallback; this is a conservative all-clear display, not a new start veto.
The low-battery control/warning policy stays unchanged.

## Explicit limits preserved

This observation is a current decision/application snapshot before C, not proof
of tick completion, future sensor health or measured electrical inhibition.
Runtime terminal failure may leave the last physical frame. No fault-path matrix
write, forced throttle bypass or claimed blanking is added. A frozen R cannot
complete a continuing blink cycle; the eventual operating procedure requires
observing live alternation rather than accepting one frame. MCU/native timing,
optical visibility and failure behavior still need real qualification.

Current UnoQMatrix normal-startup/exclusive-owner requirement conflicts with
MATCH's Immediate startup. Leave that deployment boundary unresolved; this work
does not enable the native matrix, alter startup, or claim a working MATCH display.
Keep source grants/button windows and physical calibration pending. The marker
reports the accepted voltage value, not calibrated accuracy or a hardware gate.
SC-AP remains open for native/physical readiness, rearming and log preservation.

## Required verification

New independent tests cover literal full-frame differences, every state/menu,
all fault bits, unbound compatibility, threshold equality and nextafter values,
unavailable/malformed voltage, blink boundaries and uint32wrap. Prove battery
marker is independent of the historical LOW_BATTERY latch and has no effect on
the original13pixel bar, fault priority, service/calibration screens or outputs.

Core tests use actual Robot and source-qualified explicit buttons: before/at
debounce, current presses, replay/stale/malformed observations, startup/reset,
RAW/classified handover, service transitions, cancellation, STOP/fault, wrap and
each relevant profile. No test infers readiness from initialized IDLE alone.

Actual Runtime/Transaction/MotorGate tests capture submitted frames with controlled
existing ports and configured synthetic button windows; M0 and M1, positive
qualified sources, current receipt faults, service-only lifetime, unknown battery
and nearest valid raw ADC samples straddling VBAT_WARN_V, plus stale sources.
Preserve the D093 raw-to-voltage relation: if equality is not representable by
an integer ADC value, test equality/nextafter in the pure renderer, not with a
fabricated native value. Preserve exact runtime outputs, full hold
and actual zero/disabled application when the informational symbol is present.
Synthetic observations stay explicitly host evidence, never physical acceptance.

Run meaningful focused normal/sanitizer tests, relevant established regressions
and final full host coverage. Source/ABI size and checked MATCH compile-only
qualification are required before claiming target compilation; the previous
1584B conditional span is not new-fit proof. Do not disguise this legitimate
feature build as another unadopted memory-fix candidate or infer default fit.
Independent scoped review and precise preserved first-failure receipts precede
software closure. No upload, reset, motor run or human phase gate belongs here.
