# D083 adapter surface audit — no policy selected

2026-09-23 Asia/Dubai. Read-only inspection while D082 remains frozen. This maps
implementation surfaces and decisions that a later contract must resolve; it
changes no production/header/config/core/test/app/ledger file. B15 was independently
traced by a read-only explorer; its findings below are source observations.

## Minimal entry and compatibility surface

- `src/core/fsm.h:385` RobotInput is the actual composition input. Append an explicit
  IMU evidence envelope with a LEGACY/default mode, separate gyro/accel Presence,
  heading_available, heading_updated, observation_us, checked_us and accepted
  sequence (age may be derived). Use pure core types, not an include of HAL headers.
  Existing numeric fields remain raw continuous yaw, raw pre-bias body-Z gyro and
  body X/Y acceleration. The adapter maps `imu::Estimate` field-for-field.
- Preserve the existing bool APIs and aggregate positional initialization: append
  fields or add typed overloads; do not insert/reorder existing fields. LEGACY
  resolution must reproduce current imu_ok behavior and tick-time observations.
  Explicit metadata must not silently fall back to imu_ok if it is malformed.
  `src/core/types.h:21` Inputs is not the Robot entry and its IMU fields need not be
  expanded merely for this change; Lifecycle uses it only for tick/button routing
  (`src/core/countdown.cpp:219`). It can host pure shared metadata declarations.
- Freeze admission checks for enum/presence combinations, finite used values,
  sequence/duplicate handling and source timestamps before coding. In particular,
  define relation of Estimate.checked_us to RobotInput.t_us: an acquisition can
  finish after the scheduler's start observation. The app must not silently label
  a future completion as already observed or refresh age at decision time.

## Exact consumer and routing map

| Consumer / source | Needed separation / smallest change surface |
|---|---|
| Countdown `countdown.h:108`, `countdown.cpp:148,182,188`, `fsm_robot.cpp:270` | Add gyro observation Presence to ServiceSample and route raw pre-bias rate separately from heading health. ABSENT can skip only the sample-aggregation call; time, CAL_END, warnings, opponent snapshot and Controller/STOP must still progress. VALID samples preserve finite/min-count/spread rules; INVALID preserves D024 rejection. Legacy bool remains equivalent. Source-time versus control-tick calibration-window eligibility, including a completion before CAL_END delivered afterward, needs an explicit contract; current finish-before-sample boundary must not change accidentally. |
| Bias handoff `fsm_robot.cpp:283`, `countdown.h:181`, `fsm.h:396` | Existing once-only bias_update_requested/accepted_bias_dps is sufficient. Caller feeds it to Estimator.applyBias after the current estimate/Robot step, preserving future-increment-only semantics. Feed current estimator bias as previous_bias_dps only where the existing release contract consumes it. No new averaging or GO reset. |
| HeadingReference `fsm.h:20,35,52`, `fsm.cpp:529,541,571` | Separate usable bounded heading from a newly updated heading. Keep step tick time for duplicate suppression/GO arbitration; pass source observation time separately. Only actual new source evidence updates last_raw_deg_/last_raw_us_. Retained usable yaw may be projected without timestamp renewal. Add observation/update metadata to HeadingResult if consumers need it. GO's CURRENT_GO/LAST_KNOWN classification and first recovery with retained input require explicit selection; regardless, origin_t_us cannot be fabricated from the new tick. Existing origin/fault/nominal fallback behavior and unwrapped raw provider domain remain D059. |
| Motion/rows `motion.cpp:81,131,169`, `edge.cpp:198,230`, `fsm_robot.cpp:411,421,533,570,591` | These coordinate/control consumers need qualified heading availability, not gyro Presence. Routing availability avoids treating a benign NO_NEW as an IMU loss; their existing timers still use decision tick time. Retained coordinate use does not create new evidence or renew any origin timestamp. No primitive deadline/reference restart. |
| Fusion dispatcher `opp_fusion.h:195`, `opp_fusion.cpp:363`, `fsm_robot.cpp:221` | Append/route explicit evidence, then pass separate heading availability/update metadata and acceleration Presence to the consumers below. QTR/opponent observations_fresh stays independent (`fsm.h:388`, `fsm_robot.cpp:207`). Continue one electrical observation and one final contact commitment per tick. |
| Contact/impact `opp_fusion.h:93,109`, `opp_fusion.cpp:118,177,366` | Impact evidence uses only current VALID acceleration. ABSENT or INVALID yields no impact cue; visual close/straddle counters must still advance on current opponent data. A retained usable heading supplies no acceleration validity. Existing Contact bool may remain a legacy wrapper or be passed the resolved fresh-accel eligibility internally. |
| Stuck `opp_fusion.h:173`, `opp_fusion.cpp:296` | Split current opponent continuous-detection time from heading observations. Tick time advances detection age; fresh heading initializes/extends extrema. Retained availability can preserve existing evidence without claiming a new extrema sample. Actual unavailable/invalid heading still follows D031 candidate reset; latched faults survive. D083 must state candidate-start and declaration eligibility on a retained-only tick; substituting heading_updated for the existing bool everywhere would reset candidates on every NO_NEW. |
| Phantom `opp_fusion.h:124,141`, `opp_fusion.cpp:244,264,278` | Keep episode/contact/edge consumption and marker expiry on event tick time. Marker creation stores new directional evidence; masking compares current direction with existing evidence. These are separate eligibility decisions once heading may be retained. Add heading update/source-time metadata so D083 can select fresh-only creation and/or bounded-retained comparisons explicitly. Preserve consumed-edge behavior even when no eligible heading exists. If provenance is exposed, distinguish marker edge time from its heading-source time. |
| Bearing/world memory `opp_fusion.h:47,65`, `opp_fusion.cpp:157,164`, `fsm_robot.cpp:232` | Relative-bearing memory and front recency remain current opponent observations. World bearings combine that event with heading; current Memory has only opponent last_seen_us and Robot resets world_age_us at a bearing tick. If retained yaw is allowed for world projection, add separate heading-source time/age and define combined-evidence age; otherwise gate new world evidence on heading_updated while relative evidence continues. Do not label an old yaw source as newly measured merely because the opponent was sampled. |
| Escape/inward `edge.h:141,164,198`, `edge.cpp:402`, `fsm_robot.cpp:306,339` | Motion rows need heading availability; the exit's inward evidence has a different freshness requirement. Carry update/source time separately and return an inward source timestamp when a qualified exit records one. Robot currently resets inward_age_us to0 from current input; use the actual selected source age rather than refreshing retained yaw. D054/D059 disallow promoting cached/fallback heading to new inward measurement; allowing bounded retained exit evidence would need explicit provenance/eligibility language. Preserve QTR arbitration, permission and replan rules. |
| Stall `stall.h:10,35`, `stall.cpp:38,49,59`, `fsm_robot.cpp:615` | Keep contact/duty/edge qualification timer on every control tick. Contact-start heading anchor and current deflection comparison need independent heading evidence eligibility/source times. D032 anchors only at contact start; do not retrofit an anchor on later recovery. D083 must decide whether either comparison permits bounded retained heading. Missing angle evidence affects deflection only, not timer qualification or ALL_IN suppression. |

Source times must travel beside event times, not replace them. HeadingReference's
history/origin, inward capture and optional world evidence need actual observation
provenance; button/hold, line/opponent debounce, phantom windows, continuous stuck
qualification, stall timers and motion deadlines retain their current tick clocks.
`fsm_robot.cpp:194` already ages world/inward evidence; new capture must initialize
those ages truthfully rather than blindly0. Retained projections (`fsm.cpp:584,590`)
must not refresh source evidence. No extra HAL clock is needed in core.

## B15 representation and compatibility

- `fsm_robot.cpp:819` copies yaw/raw gyro/ax/ay; `:826` sets only IMU_OK from heading
  availability. A NO_NEW can therefore look like measured zero gyro/acceleration.
  Capture presence at the same decision as values; pending frames are serialized
  later with application receipts (`fsm_robot.cpp:177,187`). Do not sample presence
  from the receipt tick. Preserve the raw pre-bias gyro meaning.
- `src/core/logframe.h:34` fixes25bytes and four low flag bits. `logframe.cpp:54`
  rejects flags above0x0F; `:98` writes all numeric IMU fields unconditionally.
  NaN is not a valid absence code: it invalidates/zeros the entire frame (`:87`).
- Four spare flag bits can represent independent three-state gyro/accel presence
  without payload growth. Exact encoding/legacy meaning/version identification,
  canonical absent/invalid numeric placeholders and heading-update representation
  or derivation are D083 decisions, not selected here. Old frames with spare bits0
  must not acquire an invented new presence claim. Measured zero must remain distinct.
- `hal/recorder_frames.cpp:9` stores bytes/status without interpretation. A flag-only
  extension preserves capacity; changing25byte size reopens memory qualification.
  `hal/recorder_csv.cpp:153` exports raw flags/numeric offsets, schema1 is named at
  `recorder_csv.h:12`. `tools/validate_csv_bundle.py:59,149` accepts all u8 flags and
  checks raw/numeric agreement; it intentionally does not enforce semantic masks
  (`state/analysis/P2_csv_bundle_contract.md:44`). Preserve that evidence distinction.

## Test and locked-boundary implications

Keep every existing locked test unchanged. Append defaults/legacy wrappers must
preserve locked `test_countdown_services.cpp`, `test_countdown_lifecycle.cpp`,
`test_start_routing.cpp`, `test_menu_routing.cpp`, `test_edge_escape.cpp` and
`test_robot_safety.cpp`, plus all R1/R5/MotorGate tests. Add ordinary D083 tests for
explicit Presence, truthful observation times, retained control heading versus new
evidence, all source/decision-time boundaries, malformed metadata and delayed
frame capture. Preserve D024 window/min-count/invalid-read semantics and D059
GO/last-known/pending-origin behavior under legacy input.

Relevant ordinary regression files: test_heading_reference.cpp, test_opp_filters.cpp,
test_stall_detector.cpp, test_robot.cpp, test_robot_events.cpp and test_search.cpp.
B15 contract changes require deliberate new expectations in ordinary
`tests/test_logframe.cpp:306` (currently enumerates all256 flags and rejects>15),
while retaining legacy vectors. `test_robot_events.cpp:151,191` covers delayed
capture/pre-post-GO and invalid frames; `test_recorder_csv.cpp:286` preserves schema/
unknown raw codes; `tests/tooling/test_csv_bundle.py:311` covers schema/raw agreement.
No direct B15 assertions were found in locked tests by the bounded search; shared
Robot behavior still requires their unchanged regression run. No app integration,
physical acceptance, sensor-rate or full-tick timing claim follows this audit.
