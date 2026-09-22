# B13 logical mode/menu contract audit — 2026-09-23 Asia/Dubai

Status: public-contract audit only; recommendations below are not accepted policy
or implemented behavior. Coordinator chooses material changes under D-051 and
records them before publishing headers, tests and implementation. P1 host work
remains active under D-016; no phase gate, hardware fact or motor run is inferred.

Sources: AGENTS.md; BEHAVIOR B0/B1/B2/B3/B13/B14/B16 (B15 dump restriction also
checked); decisions D-018/D-019/D-035/D-051; public countdown.h/types.h/config.h;
P1_core_logic.md; current PROGRESS; P1_robot_interface_audit.md item 13. Header
inventory confirms no existing logical menu/service-selection contract. No
implementation `.cpp` was read. Only this new audit file is owned by this task.

## 1. Established requirements and current interface evidence

| Source | Established requirement / public contract |
|---|---|
| B13/B16 | Six match modes in numeric order: SIDESTEP_R, SIDESTEP_L, DIRECT, ARC_R, ARC_L, WAIT; MODE_DEFAULT=1 at boot. |
| B3/B13 | A short MODE press cycles the current item; short means strictly under 600 ms. A BTN_LONG_MS MODE press toggles the service menu; BTN_LONG_MS=1000 ms. |
| B13 | Service list: SENSOR_VIEW, QTR_CAL, DRIVE_TEST (P3), LOG_DUMP. START press/release starts the match countdown or invokes a service action. |
| B1/B2, D-018 | BOOT/IDLE/COUNTDOWN/STOPPED inhibit motors. Gated-state services and buttons still update before that inhibition. IDLE owns mode/menu/sensor view. |
| B3, D-019 | START needs a qualified NONE -> START -> NONE sequence; boot-held START cannot start. Full 5100 ms starts at the actual release-qualification call. MODE during COUNTDOWN cancels it. |
| D-035, countdown.h | StopHold observes logical BOTH in every state, including boot; qualify for 20 ms, then start a full 1000 ms at that call. Any observed non-BOTH cancels a pending hold. STOPPED persists until reset. |
| countdown.h | Buttons exposes start_release/mode_press and edge/qualification times. MODE includes BOTH. Controller owns Buttons/StopHold/Gate privately; its result exposes accepted gate events, not all raw qualified button events. |
| countdown.h | Controller/Lifecycle provide no start-routing selector. Lifecycle starts calibration services after an accepted match release. Passing a service START through this unchanged interface would also start the match gate. |
| types.h | Mode includes only the six match modes. Outputs has duties, motor enable and ui_state, but no selected item, service request or fault-display contract. |
| B14 | Low battery in IDLE warns without changing match behavior; watchdog returns to inhibited normal startup. IMU/stuck/calibration/tick warnings have separate evidence sources. |
| B15/R2/R3 | LOG_DUMP is IDLE-only and nonblocking; no service/Bridge response can become a motion command. |

## 2. Exact gaps and recommended choices

These choices deliberately distinguish UI requests from executing a calibration,
dump or P3 drive. They preserve the existing countdown/STOP rules and B16 values.

| Gap | Recommended deterministic contract; not yet policy |
|---|---|
| Undefined interval 600–999 ms | A MODE hold in [600,1000) ms does nothing. Do not reinterpret it as a short press. Exactly 600 ms is not short. |
| MODE duration anchor / long timing | Require qualified NONE -> MODE. Start duration at the actual MODE qualification call, after BTN_DEBOUNCE_MS; do not backdate delayed qualification. Long toggles once while exclusive MODE is still observed at elapsed >=BTN_LONG_MS. Add `MODE_SHORT_MS=600` to config.h as centralization of existing B13 text, with a tuning-log entry; change no B16 default. |
| Short press versus long release | A first observed NONE after qualified MODE freezes the duration and suppresses any pending long toggle. Emit short only after that NONE qualifies, if frozen duration <MODE_SHORT_MS and no long toggle already happened. A release observed exactly on the long deadline wins; no toggle and no short. |
| Interrupted release / button mixture | If NONE release qualification is interrupted, cancel the MODE gesture and require qualified NONE to rearm. START, BOTH or an invalid logical enum cancels/disarms MODE immediately; none becomes a menu action. This conservative lost-gesture behavior is a new choice, not an existing debounce requirement. |
| Boot-held MODE | Suppress all menu actions until an observed NONE has qualified, followed by a new MODE press. Held MODE must not silently enter services at boot. Boot-held BOTH still follows D-035; do not reuse MODE arming to disable StopHold. |
| Gesture context | Only a gesture begun and completed in IDLE within the same menu context is eligible. Leaving IDLE cancels it. A MODE press begun in COUNTDOWN cancels countdown at existing Buttons qualification, but its later release/long expiry cannot also cycle a mode or open services. Require a fresh qualified NONE before another UI gesture. |
| Long hold repeat / menu memory | One toggle per physical gesture; continuing to hold never retriggers. Match-mode selection survives service entry/exit. Every service entry selects SENSOR_VIEW; short MODE cycles the four services in listed order and wraps. Match short MODE cycles six numeric modes and wraps 6 -> 1. |
| Match mode ownership | Snapshot the selected match mode when Gate accepts START release. Freeze the running mode through COUNTDOWN and moving states. An IDLE cancellation retains selection but requires the normal fresh START sequence. Reset restores MODE_DEFAULT and exits services. |
| START routing | Match-view START may reach the match gate; service-view START emits one typed service-action request and cannot start the gate/calibration/GO. Always process real logical input for debounce, cancellation and BOTH STOP. Do not hide inputs by replacing START/BOTH with NONE. |
| STOP / simultaneous work | STOP or a latched inhibited fault takes precedence over menu events and service requests on that call. Clear transient UI requests and cancel pending gestures. Keep STOPPED latched through releases/menu input; reset follows ordinary boot defaults. |
| Outside IDLE | Ignore/disarm short/long selection and service actions in BOOT, COUNTDOWN, all moving states and STOPPED. Existing countdown MODE cancellation and global BOTH STOP still operate. A held gesture crossing back into IDLE cannot become a deferred action. |
| Service execution and completion | P1 emits an inert typed request; it does not run a blocking service or grant motion. SENSOR_VIEW may expose logical sensor values in IDLE. QTR_CAL/LOG_DUMP requests need explicit separate consumers and availability/status evidence. DRIVE_TEST remains unavailable to P1 motion; no direct transition from a service request to an energized DRIVE_TEST is authorized. |
| Service reset/exit | Leaving services or IDLE cancels any outstanding service request/selection activity; requests are one-call pulses, never queues. A future long-running consumer needs an explicit busy/cancel/complete contract before it can run. A consumer acknowledgement is not a start or motion command. |
| Invalid selection/input | Use enums distinct from core::Mode for services. Invalid requested/reset mode falls back to MODE_DEFAULT with an explicit diagnostic, or reject construction; coordinator must choose one. Recommend rejection at API boundary with inhibited normal defaults. Invalid button enums cancel UI gestures and never start/toggle. |
| Display/fault ownership | Return logical selected-mode/menu/item/request/status fields for HAL presentation; do not invent pixels, ADC thresholds, voltage validity, persistent calibration storage or fault evidence. Warnings are informational and cannot override STOP/countdown/edge inhibition. |

Rationale for the medium-hold no-op and interrupted-gesture cancellation: these
resolve unspecified inputs without accidentally changing the selected strategy
or entering services. The user can retry; no hidden delayed action remains.

## 3. Minimum composition contract before Robot integration

1. Add a pure bounded mode/menu helper with explicit logical button input, current
   state, timestamp and reset. Its output contains selected match mode, service
   menu/item, one-call selection/toggle/action pulses and diagnostic availability.
   It neither returns nonzero duty nor changes the Gate's phase.
2. Expose the already-qualified START event without resampling Buttons, and add
   an explicit match-start eligibility input to Controller/Lifecycle. Illustrative
   API additions are a read-only last-ButtonEvents result and `allow_match_start`
   defaulting true; these names/signatures are proposals, not existing APIs.
   The selector suppresses only the start_release command supplied to Gate. It
   must not suppress Buttons, StopHold, mode cancellation, external STOP or time.
   Default calls retain every existing public Controller/Lifecycle behavior.
3. Robot derives match-start eligibility from IDLE + match view, routes a service
   START to its typed request, and invokes Lifecycle exactly once. Mode/menu
   eligibility uses the state at call entry so a countdown cancellation cannot
   reclassify that same press as an IDLE menu gesture. Final STOP/fault precedence
   discards any simultaneous provisional UI action before publishing outputs.
4. Lock running mode on accepted Gate release, not on raw press or preview. The
   same release starts countdown services at its actual qualified timestamp.
   Services never supply a GO pulse or motion permission independently.
5. An immediate repeated timestamp produces no new gesture/action pulse and
   ignores changed data at that timestamp. Define this for the new helper only;
   do not silently change existing Controller semantics. All elapsed arithmetic
   must work across uint32 micros wrap; successive gaps are less than one wrap.
   Use bounded/saturating accumulated ages so an arbitrarily held button cannot
   wrap into a second action. No heap, I/O, blocking operation or unbounded loop.

The START-routing addition is an integration prerequisite. A menu layered only
over current Lifecycle output cannot retrospectively undo an accepted start;
resetting Controller on service entry would also erase safety state and is not
an acceptable substitute. Existing locked tests stay unchanged; add regressions.

## 4. Exact boundary and regression matrix for the proposed contract

Notation: D=BTN_DEBOUNCE_MS=20 ms, S=MODE_SHORT_MS=600 ms,
L=BTN_LONG_MS=1000 ms, H=COUNTDOWN_MS+COUNTDOWN_MARGIN_MS=5100 ms.
q is the actual MODE qualification call; r is first observed NONE for release;
u is the actual START release-qualification call. Include exact boundaries and
both 1 us and 1 ms adjacent samples; use regular, sparse and wrap-crossing calls.

| Case | Required observation/result |
|---|---|
| Boot/reset defaults | Mode 1, match view, no request, duties zero/EN false; watchdog startup has the same inhibited UI defaults. |
| Mode cycle | Six clean short gestures produce 1->2->3->4->5->6->1; one step per qualified release, no step on initial press. |
| Press debounce | MODE at D-1 us/D-1 ms: no qualified gesture. MODE at D: q begins, no selection/toggle. First delayed call at D+7 ms anchors q there. |
| Boot-held MODE | Hold longer than D+L and release: no action. Only subsequent qualified NONE->MODE->NONE is eligible. |
| Short boundary | r-q=S-1 us and S-1 ms: exactly one increment at qualified NONE release. r-q=S, S+1 us, L-1 us and L-1 ms: no action. |
| Release debounce | At r+D-1 us and r+D-1 ms: no short pulse; at actual qualifying call >=r+D: one short pulse, regardless of elapsed time since q then. |
| Interrupted release | NONE for D-1 us then MODE: cancel entire gesture, no later long/short action until a new qualified NONE and new MODE press. |
| Long boundary | Continuous exclusive MODE at q+L-1 us/q+L-1 ms: no toggle. At q+L: one toggle. Holding through q+2L and a full micros wrap: no repeat. |
| Release on long deadline | First NONE at q+L cancels long; subsequent qualified release causes no short. First NONE after a previously fired long also causes no short. |
| Sparse long calls | Continuous observed MODE next called at q+L+7 ms: one toggle on that call; no backdated pulse. An observed NONE on that call wins instead. |
| Service cycle | Long enters SENSOR_VIEW; four short gestures cycle all services and wrap; long exits and restores prior match selection. Re-entry begins at SENSOR_VIEW. |
| BOTH contamination | MODE->BOTH or START->MODE or invalid enum produces no menu action. BOTH still qualifies D then full L and latches STOP in every state, including boot/services. |
| BOTH cancellation | Non-BOTH at STOP deadline cancels pending STOP exactly as current D-035. MODE UI cannot reinterpret that release as a short or long action. |
| Match START | Qualified clean START release at u enters COUNTDOWN and snapshots mode; permission remains false at u+H-1 us/u+H-1 ms, GO at u+H absent stronger inhibition. |
| Service START | Each service item emits one request at qualified START release, stays IDLE/EN false/duties zero, no match start_release/GO, no calibration attempt. Repeat release/cached tick gives no second request. |
| Service boot-held START | Held through boot/menu entry does not request a service or match. Release then a fresh qualified press/release is required. |
| Countdown MODE | Qualified MODE before GO, on GO deadline, and before a sparse overdue call cancels to IDLE. Holding that cancel press past L never toggles menu; release never cycles selection. |
| Countdown STOP | BOTH -> STOP while holding cancels countdown/calibration and suppresses GO. Remaining hold/service flags cannot resume it. |
| Moving-state MODE | Every moving state ignores short/long selection; current running mode unchanged. Both-held STOP remains live. Re-entry to IDLE cannot replay a held gesture. |
| Fault/STOP tie | STOP/fault and possible menu toggle/service request on the same tick: no action published, motors inhibited. Release/new gestures cannot recover STOPPED. |
| Service DRIVE_TEST | Request is explicitly unavailable/inert in P1; never enters energized DRIVE_TEST and never bypasses the five-second gate. Later P3 implementation needs its own accepted contract and authorization. |
| Service consumers absent/busy | No consumer, rejected request, unknown availability or delayed completion cannot stall a tick, start a match or grant permission. No repeated request is queued automatically. |
| Timestamp protocol | Duplicate timestamp after a toggle/release/request clears pulses; changed data is ignored. Reset allows a new first timestamp but requires normal boot arming. |
| Reset during gesture/action | Reset at press/release/long/STOP/service stages clears pending UI activity and restores defaults; held START/MODE remain ignored, held BOTH can freshly STOP. |
| Wrap / long lifetime | Re-run debounce, S/L/H boundaries straddling uint32 wrap; long holds spanning more than one wrap with bounded successive calls do not retrigger. |
| Warning-only behavior | Low-battery/IMU/stuck/calibration display flags cannot cycle mode, toggle services, START, grant duty or clear a latch. At VBAT_WARN_V equality, B14's strict-under condition is false when supplied valid voltage evidence. |

## 5. Explicit remaining limits and next action

This audit does not define A1 voltage bands/BOTH decoding, matrix glyphs/battery
bar mapping, QTR calibration measurement/persistence, service transport, physical
button bounce timing, P3 DRIVE_TEST motion or human motor-run permission. Those
remain separate contracts/evidence; none should be guessed to complete B13.
Fault icons also need explicit producer validity and lifetimes. Existing Inputs
does not by itself prove fresh valid battery samples or hardware reset cause.

Coordinator next: select/revise the recommendations, append the material decision,
amend B13 visibly, commit minimal public interfaces, and commission independent
tests from that contract. No code/test/shared-ledger edit, build, hardware action
or commit occurred in this audit. Full B13 execution and P1 gate remain unproved.
