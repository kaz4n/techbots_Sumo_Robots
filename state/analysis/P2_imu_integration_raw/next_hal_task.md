# Next concrete P2 HAL task after D084

2026-09-23 Asia/Dubai. Read-only review of existing audits and current source;
no board access, new vendor research, implementation, contract or ledger change.
D051/D075 permit software work before physical acceptance. Older audit scheduling
restrictions predating D075 are historical, not a reason to stop eligible work.

## Recommendation

Freeze a narrow B2 contract, then implement actual `src/hal/line_qtr.h/.cpp`:
a checked native four-pad RC acquisition owner with finite `begin/start/advance`
operations and explicit acquisition identity, pending/completed/fault states.
Each advance performs fixed bounded work (at most one four-pad observation pass),
without waiting for the entire1500us interval. Keep the current pins and10/1500us
defaults. Use the established native GPIO dispatch and actual micros observations;
no generic transport/Port framework or second diagnostic logger is needed.

This is the smallest reusable missing acquisition implementation supported by
existing source evidence. It does **not** itself resolve SC-B or make its pending
or old results eligible for Robot. Tight-loop bench servicing can validate raw
acquisition software; a later runtime service schedule must separately satisfy
the capture precision and sample-delivery contract. Do not place a1500us blocking
read in the app or assume one advance per1ms is adequate.
The existing IMU transfer alone has a600us software budget (`src/config.h:50`),
so cooperative acquisition precision also depends on where other native work can
interrupt servicing; an async state machine by itself supplies no scheduling proof.

Current `src/hal` contains neither line_qtr nor ui. `src/app/app.ino:1,8,15,22`
remains the inert P1 target: MOTORS_ALLOWED0 assertion, BOOT-only step and empty
loop. `fsm::RobotInput` requires a new complete four-QTR/seven-opponent snapshot
(`src/core/fsm.h:405`); initialized Robot faults on its absence and does not sample
on a stale call (`src/core/fsm_robot.cpp:210,220`). Thus asynchronous acquisition
requires a later explicit core/scheduler freshness change, not a fabricated
`observations_fresh=true` on every control tick.

## Already-established source basis

- `P0_qtr_bare_contract_audit_20260923.md:84` binds FL/FR/RL/RR to
  D2/PB3, D4/PA12, D7/PB2, D8/PB4 on exported ready GPIOB/A objects. Its
  `:162` onward establishes finite configure/read/set/clear dispatch, neutral
  INPUT/no pulls, and Arduino OUTPUT's initial LOW. `:184` distinguishes finite
  paths from measured execution time. Arduino wrappers discard native errors;
  the new HAL must preserve native statuses, as current opponent HAL already
  does (`src/hal/opp_sensors.cpp:53,74`).
- The same audit `:120` covers PWM/CAN/USB/SWJ ownership exclusions; PB3/PB4
  initial debug modes are not neutral-input proof. Existing motor backend uses
  per-channel pinctrl (`src/hal/motor_port_unoq.cpp:278`), avoiding the known
  whole-TIM3-group PB4 claim, but final-image concurrent ownership remains a
  prerequisite. Do not silently disable a debug/peripheral owner or reset GPIO.
- Its `:197` establishes integer-us, modulo32 micros and the finite installed
  clock path; `:213` explains why delayMicroseconds(10) does not prove a10us
  charge. P0's explicit11-tick quantization guard is documented in
  `P0_qtr_contract.md:22`; adopting a production charge guard must be explicit.
- `P0_qtr_validation.md:109` records bare-pad totals1530..1536us and observed
  deadline intervals1500..1504us. These are setup-only diagnostic data, not real
  QTR discharge, cleanup verification, sensor freshness or complete-tick WCET.
  SC-B's1510us versus1ms/<800us conflict remains (`spec_conflicts.md:26`).

## Contract decisions needed before code

1. Define charge/release/observe/cleanup phases and permitted calls, including
   busy start, duplicate advance, cancellation, one-time publication/consumption,
   rearm eligibility, fault lifetime and counter wrap. Constructor must do no I/O.
   Reuse no prior acquisition's LOW bits or timestamps. Decide exactly which
   setup failures permit a retry; do not infer ownership from object existence.
2. Distinguish per-pad release time, first observed LOW, last observed HIGH,
   all-pad completion time, and censored/no-LOW timeout. Sequential release/read
   skew must remain visible. A delayed LOW observation is an upper bound on
   transition time, not an exact hardware capture. It must not masquerade as a
   measured black discharge merely because its timestamp exceeds300us.
3. Freeze maximum service gap/charge lateness, whole-operation and cleanup
   deadlines, count bounds for frozen clocks, exact equality/overshoot precedence,
   and ignored/late-call behavior. Values are engineering decisions in config,
   not facts provided by the old4096-poll diagnostic. Fixed work per advance
   does not guarantee the interval between calls or physical charge timing.
4. Publish raw timing/uncertainty and per-pin status with validity independent of
   color classification. Recommend preserving HIGH-to-LOW observation brackets
   and a distinct timeout mask; freeze whether insufficiently resolved brackets
   reject the snapshot. The current scalar raw-time core interface cannot express
   uncertainty, so do not add an implicit core adapter or silently choose white/
   black values for missing/ambiguous channels in this increment.
5. Validate the whole pin bank/device metadata before writes; use checked native
   statuses, explicit neutral no-pull restoration and bounded all-four cleanup
   attempts after a partially started operation while ownership remains valid.
   Freeze the ownership-loss exit separately; do not write blindly after loss.
   The installed direction getter
   is NULL and GPIO_GET_CONFIG disabled (`P0_qtr_bare_contract_audit:115`): source
   calls/return0 do not prove physical final pad state. A stronger direct-register
   readback/ownership predicate needs a narrow binding to the already-saved CMSIS
   headers and saved driver source, not an invented generic query.

The first four items are missing contract choices, not reasons for repeating
board inventory. The fifth has existing checked-dispatch evidence; only any
additional promised readback/clock/pad guards need their exact saved-source
derivation before they enter the contract.

## Why not jump directly to IRQ capture or UI input

`P0_irq_installed_contract_20260923.md:104,110,187,198` already proves that
Arduino attach hides errors, detach leaves hardware ownership/pending state,
native configuration does not clear old pending bits before enable, and disable
does not alone remove callbacks/clear pending/disable NVIC. `:166,174` says the
pending query is NULL and internal interrupt helpers lack established LLEXT
exports. EXTI3/12/2/4 mapping is feasible, but callbacks are software timestamps,
not capture hardware; latency, coalescing and release-to-arm loss remain.
An IRQ implementation requires a separately frozen race/ownership/rearm/pending
policy and source-proved atomicity/cleanup path. Reusing attach/detach is not an
already-audited solution. The proposed cooperative driver avoids selecting that
larger architecture merely to claim SC-B closed.

UI input is not the smaller independent driver. `P2_next_hal_audit.md:23,31`
and `docs/HARDWARE.md:140` establish A1/PA5/ADC1 channel10 and START/BOTH's identical
grounded voltage (SC-A, `spec_conflicts.md:25`). Current power Reader owns ADC1
for A0/channel9 only (`src/hal/power.h:28`, `power.cpp:30,123,266`), with persistent
claim and exact mode guards. A second ui ADC owner is invalid. Raw A1 sampling
would require a deliberate single-owner channel-switch contract, admission,
settling/sequence checks and power-driver regression before a decoder. No software
threshold can supply the absent electrical BOTH distinction; do not change wiring
or the approved logical STOP behavior under an implementation assumption.

A bounded matrix-only output driver is a genuine parallel alternative after a
small display-content/rate/startup contract. Existing `P0_G1.md:53,65` supports
fixed104-byte draw and warns about bitmap conversion and blocking playSequence;
matrix refresh has a10us ISR and must enter whole-image timing analysis. This
does not implement START/MODE acquisition or complete B6. It is lower priority
than the missing edge acquisition path, and adds no reason to delay that work.

## Required independent evidence and limits

Compile actual native source against installed-shaped controlled GPIO/clock
headers. Cover all4 pad maps and all16 LOW combinations; no-write malformed-bank/
unready-owner admission; every configure/write/read failure; charge and release
ordering; immediate/late/partial LOW; censored timeout versus successful data;
service-gap uncertainty; equality/overshoot; frozen/reversed/half-range/wrapped
clocks; busy/cancel/rearm/reset; old-generation rejection; all-four cleanup after
each partial stage; no allocator or constructor/startup I/O. Inert target probe
retains the real driver, upload remains refused, final ELF/imports are reviewed.
Preserve existing locked/core tests and run ordinary/native driver regressions.

Actual black/white/brown separation, voltage/transient safety, sensor response,
sampling cadence, IRQ latency if later selected, matrix/IMU contention, hold safety
in the integrated application,5-minute full-tick WCET and human gates remain
physical/integration work. The hold is5100ms by current configuration; no
acquisition proposal changes its approved timing. Global SC-AJ/F091 clock
limitations remain. No app scheduler, motor run or phase-completion claim follows.
