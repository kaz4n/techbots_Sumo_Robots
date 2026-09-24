# P5.3 existing abort-test coverage map

Read-only source assessment,2026-09-24. This map names existing assertions;
it does **not** claim execution, passing results or physical abort performance.
Only this document is authored in this task. No production implementation body
was read, and no test, compiler or shared state ledger was modified or run.

Authority: `docs/BEHAVIOR.md` B2/B7/B12/B13/B15; adopted D033/D034/D055 and
D134; `docs/prompts/P5_openers.md` P5.3/D034 clarification; public
`openers.h`, `fsm.h`, `types.h`, `logframe.h` and `motors.h`. The proposed new
abort-evidence contract is not treated as adopted policy in this map.

## What counts as a distinction the new evidence must preserve

Current detection may abort an active opener only in the applicable phase.
An inner-side detection that starts TURN_IN is a phase transition, not an exit.
A completed turn can exit with a current target even without a detection abort.
DIRECT's saved countdown front can terminate it without any current front.
WAIT's ordered front cue starts its full SIDESTEP_R and is not an abort.
Natural expiry, STOP/fault and edge preemption are separate causes.

D034 maps **every** opener exit through current normal perception: front TRACK,
side/rear DEFEND_TURN, none SEARCH; three fresh centered observations are still
required for ATTACK. The exit observation counts as observation1. Therefore
neither final state nor `openers::Exit` alone identifies an abort cause:

- SIDESTEP PIVOT with front+outer can produce SIDE_OR_REAR_TARGET as its executor
  cause, then TRACK through D034's current-front priority.
- WAIT HOLD with front+side also exits for side priority but normal routing sees
  the current front. It is not evidence of a failed side-abort rule.
- DIRECT snapshot-only exit can route SEARCH or DEFEND_TURN from current data.
- WAIT natural deadline with front present can route TRACK even though the
  executor's exit was SEARCH. TRACK alone cannot certify a detection abort.
- A turn's natural completion with a remaining inner-side target can produce
  SIDE_OR_REAR_TARGET, indistinguishable by that enum from an outer-side abort.

## DIRECT: current detection, snapshot and natural completion

All names below are exact `TEST_CASE` strings in
[`tests/test_opener_direct.cpp`](../../tests/test_opener_direct.cpp).

| Existing test | Source-level expectation | Evidence distinction |
|---|---|---|
| `B2 B12 O2 DIRECT all 128 current masks prioritize front over side rear` (line164) | Starts with snapshot0; same-call current front exits FRONT_TARGET, else side/rear SIDE_OR_REAR_TARGET, none stays active. | Pure detection exit; exhaustive7-bit masks. |
| `B12 O2 DIRECT all 128 snapshots preserve only front exit eligibility` (line149) | Current0; saved front exits, saved side/rear alone does not; later deadline SEARCH. | Snapshot-only exit must not become a current-detection abort. |
| `B2 B12 O2 DIRECT every snapshot current pair obeys front priority` (line180) | All128x128 combinations; snapshot/current front beats current side/rear. | Existing Exit merges saved and live front causes. |
| `B2 B12 O2 DIRECT detection precedes completion at adjacent and delayed ticks` (line219) | Current front/side wins at399999,400000,400001 and500000us. | Detection-at-deadline remains detection precedence, not automatic timeout attribution. |
| `B12 O2 DIRECT saved front remains eligible on a delayed first step` (line234) | Saved front wins even after DIRECT duration, despite current side/rear. | Neither delayed first step nor elapsed timeout turns a snapshot into current detection. |
| `B12 O2 DIRECT 1 kHz timeline requests straight for exactly 400 ms` (line99) and `B0 B12 O2 DIRECT deadline includes exact adjacent microsecond boundaries` (line113) | No target, exact natural deadline; SEARCH/zero. | Negative abort controls. |
| `B12 O2 DIRECT all normal exits latch zero despite later detection and faults` (line241) | Later observations cannot change/replay terminal exit. | An evidence pulse must not be inferred anew from each retained exit result. |

Actual Robot coverage:

- [`test_robot.cpp:114`](../../tests/test_robot.cpp:114),
  `B5 B9 Robot needs three current centered observations after DIRECT exit`,
  includes current front at GO; asserts TRACK, TRACK, ATTACK, no contact and
  approach duty cap. Its `robot_scenario.h` fixture uses synthetic accepted
  application feedback, not MotorGate callbacks.
- [`test_mode_availability.cc:201`](../../tests/test_mode_availability.cc:201),
  `B12 D034 D134 Robot DIRECT current front still requires three centered observations`,
  uses actual Robot+MotorGate, both logical button sources, current detection
  qualified at GO, and the three-observation/cap rule.
- [`test_mode_availability.cc:223`](../../tests/test_mode_availability.cc:223),
  `B12 D034 D134 Robot current side routes DEFEND while stale countdown front routes SEARCH`,
  covers every individual side/rear bit after DIRECT GO; separate genuine saved
  front with completed30ms clear before GO routes SEARCH. This is the explicit
  snapshot negative control; it does not yet assert an abort-evidence record.
- [`test_robot.cpp:217`](../../tests/test_robot.cpp:217),
  `B12 Robot natural DIRECT and WAIT expiration enter SEARCH at exact deadlines`,
  covers target-free natural completion at the Robot boundary.

At GO, DIRECT can start and exit on the same observation while the previously
committed state is COUNTDOWN. Requiring a prior OPENER state or an
OPENER->TRACK event would omit this valid case. Existing state-event expectations
do not define a dedicated detection-abort receipt for it.

## SIDESTEP and ARC: phase-specific aborts versus internal transitions

The exhaustive executor test
[`test_opener_flank.cpp:259`](../../tests/test_opener_flank.cpp:259),
`B2 B12 D033 all masks have phase-specific SIDESTEP and ARC priority`, covers
all128 masks in all3 phases for both mirrors of both families. Its literal
expected rules are:

| Family/phase | Detection-driven exit | Detection that does not exit |
|---|---|---|
| SIDESTEP PIVOT | Outer-side/rear; front ignored even when present with outer. | Front and inner; inner does not skip pivot. |
| SIDESTEP TRAVERSE | Front first, else outer-side/rear. | Inner starts fixed TURN_IN; no target continues250ms traverse. |
| SIDESTEP TURN_IN | Front first, else outer-side/rear. | Inner alone waits for turn completion. |
| ARC PIVOT | None. | All opponent masks ignored until phase advancement. |
| ARC TRAVERSE | Front. | Inner starts bearing-directed TURN_IN; outer alone does not abort. |
| ARC TURN_IN | Front. | Side/rear waits for turn completion; there is no SIDESTEP outer exception. |

Additional exact existing names in
[`test_opener_flank.cpp`](../../tests/test_opener_flank.cpp):

- Line307: `B2 B12 O1 O3 pivot completion rechecks the new phase front abort on the same tick`.
  Persistent front ignored in PIVOT becomes a valid abort on same-call TRAVERSE
  entry; the new evidence must not require a new raw rising edge at that instant.
- Line316: `B2 B12 D033 simultaneous front outer at pivot completion retains old phase priority`.
  SIDESTEP returns SIDE_OR_REAR_TARGET; ARC returns FRONT_TARGET after ignoring
  the old-phase mask and advancing. The old phase's priority cannot be replaced
  merely with the final phase or final Robot front state.
- Line325: `B12 O1 O3 pivot completion can start traverse and inner turn on one tick`.
  PIVOT->TRAVERSE->TURN_IN is not an opener exit.
- Line377: `B2 B12 O1 current front and outer abort precede the exact DRIVE deadline`.
  Front wins simultaneous front+outer at the250ms DRIVE completion boundary.
- Line446: `B12 O3 ARC inner triggers capture current selected bearing once`.
  The inner trigger starts a captured turn, not a detection abort/restart loop.
- Line431: `B12 O3 ARC completion turns toward a current outer target without inventing one`.
  At1500ms, outer target produces TURN_IN; absent target produces SEARCH.
- Line478: `B12 O3 ARC accepts canonical 180 bearing and front abort ignores unusable bearing`.
  Current front exits at the ARC deadline despite irrelevant invalid bearing.
- Line489: `B12 D034 TURN_IN completion uses current target after loss or reacquisition`.
  Current front, each side/rear and none determine terminal intent. This mixes
  detection-preemptive masks and completion-only masks; the returned enum alone
  does not distinguish them.
- Lines349/413/507: `B12 O1 DRIVE completes at 250 ms into a fixed 110 degree turn without a target`,
  `B7 B12 O3 ARC time limit is 1500 ms with exact adjacent delayed and tie cases`,
  and `B7 B12 O1 O3 TURN_IN timeout has exact deadline and one-call pulse`.
  These supply natural/internal-completion negative controls.

Actual Robot tests
[`test_robot.cpp:182`](../../tests/test_robot.cpp:182),
`B12 D033 D034 Robot mirrored flank pivots ignore front until traverse`, and
[`test_mode_availability.cc:211`](../../tests/test_mode_availability.cc:211),
`B12 D034 D134 Robot flank pivot ignores front then hands over on traverse entry`,
cover both available mirrors, same-call front handover and later centered
qualification. The latter has actual MotorGate callbacks. They do not cover
the full executor phase/mask matrix at the Robot/evidence boundary.

## WAIT: HOLD aborts, cue, full delegated SIDESTEP

Exact names in [`tests/test_wait.cpp`](../../tests/test_wait.cpp):

| Test | Source-level expectation | Classification consequence |
|---|---|---|
| `B12 O4 WAIT all 256 initial masks brake or abort without unordered cues` (147) | Any current side/rear exits; front-only combinations hold. | HOLD side/rear is a genuine detection abort; initial simultaneous fronts are not a cue. |
| `B12 O4 side rear abort wins cue deadline and invalid healthy yaw` (281) | Exhaustive side-containing masks at the WAIT deadline, even invalid yaw, produce side exit and no cue. | Side cause takes precedence within this executor; global Robot source-fault priority remains separate. |
| `B12 O4 D055 cue window includes 300000us and excludes its next microsecond` (163) | Ordered FC then a new flank, inclusive300ms. | Cue starts activity; it does not terminate the opener. |
| `B12 O4 initial simultaneous fronts and preheld flanks cannot invent ordering` (179) | No cue from unqualified ordering. | Negative cue/abort evidence controls. |
| `B12 O4 valid ordered cue wins exact and delayed wait expiry observations` (257) | Cue at/beyond WAIT deadline while its FC window is valid starts full pivot. | Elapsed WAIT timeout alone does not classify the call as completion. |
| `B12 O4 initial front masks do not change the exact 2 second wait limit` (241) | HOLD front-only remains until natural SEARCH intent at2s. | Robot may subsequently route that natural exit to TRACK; not automatically an abort. |
| `B12 O4 delegated SIDESTEP phases retain every literal front and side priority` (385) | All256 masks in all3 delegated phases follow SIDESTEP_R priorities. | Delegated WAIT has an inner flank phase as well as outer WAIT state. |
| `B12 O4 both approach flank signs always select the complete RIGHT pivot` (371) | Both cue sides select RIGHT, then persistent front can exit at pivot completion. | No invented WAIT_L and no skipped pivot. |
| `B12 O4 delegated drive runs 250ms then fixed left 110 degree turn and hint` (415) | Complete target-free delegated script, exact tolerance/deadline checks. | Natural delegated completion is not a detection abort. |
| `B12 O4 delegated turn target is captured once and ignores later bearing payload` (442) | Remaining inner/rear at natural turn completion exits side. | Side exit enum does not identify outer-side preemption. |
| `B12 O4 D034 exit intent composes with fresh three-observation normal qualification` (647) | Pure WAIT + NormalPerception/frontDemand composition gives TRACK/TRACK/ATTACK. | Qualification coverage, but not whole Robot or actual Gate evidence. |

Actual Robot coverage: `B12 D055 Robot WAIT consumes ordered confirmed cue then complete right pivot`
([`test_robot.cpp:200`](../../tests/test_robot.cpp:200)) and
`B12 D055 D134 actual WAIT cue starts a full pivot before current front handover`
([`test_mode_availability.cc:237`](../../tests/test_mode_availability.cc:237)).
Both demonstrate the2-raw-observation confirmation and ordered cue, full pivot
and front routing. The D134 case additionally checks actual Gate and completed
TRACK/TRACK/ATTACK qualification. Neither is an exhaustive Robot HOLD-side/
delegated-phase abort matrix or an evidence-format test.

## Higher-priority edge, STOP and existing recorder coverage

- [`locked/test_robot_safety.cpp:71`](../../tests/locked/test_robot_safety.cpp:71):
  `R5 B4 actual Robot handles every line mask after GO and while persistent before GO`.
  Same-observation escape, exact pattern faults and EDGE metadata for default
  opener, using synthetic applied feedback.
- [`locked/test_mode_availability_safety.cc:102`](../../tests/locked/test_mode_availability_safety.cc:102):
  `B4 R5 D134 every nonblack mask preempts every available opener on its first observation`.
  Every available mode/mask at GO and after GO, real Gate, row-specific B4/B6
  requests and PWM. Its draft-oracle correction and original failure remain
  separately retained; this source map does not assert a validation result.
- [`locked/test_robot_safety.cpp:44`](../../tests/locked/test_robot_safety.cpp:44):
  `R1 B13 Robot explicit STOP wins GO boundary and every later call`;
  line59 `R1 B13 Robot BOTH requires full qualification plus hold then latches STOP`.
- [`locked/test_mode_availability_safety.cc:123`](../../tests/locked/test_mode_availability_safety.cc:123):
  `B13 R1 R5 D134 STOP wins GO white and target ties and BOTH retains its full hold`.
  Every available mode and both button input styles, actual Gate, STOP/reset and
  simultaneous raw front/white at prospective GO. The injected target is not
  necessarily yet confirmed, so do not describe it as every confirmed-abort tie.
- [`test_robot_events.cpp:116`](../../tests/test_robot_events.cpp:116):
  `B15 Robot final arbitration suppresses provisional contact on STOP or edge`.
  Target-qualified normal ATTACK/contact boundary, not every opener phase.
- [`test_robot_events.cpp:28`](../../tests/test_robot_events.cpp:28):
  `B15 Robot START GO and state metadata preserve qualified source times`;
  line49 `B15 Robot persistent line at GO reports entered without invented new white`;
  line95 `B15 Robot receipt events precede current STOP across numeric timestamp wrap`.
  These cover established ordering/time/metadata, not a dedicated abort reason.

Public B15 frames occur at25Hz; a state frame alone cannot establish a1ms P5.3
abort bound. The public event enum/metadata currently has no dedicated opener
phase/cause classification. Existing FRAME/STATE_CHANGE/GO events are valuable
context but cannot disambiguate the causes listed above.

## Gaps to cover independently after an abort-evidence contract is adopted

1. **Cause identity rather than inference.** Define and test detection cause,
   captured mode, phase-at-observation/phase-after-advancement where relevant,
   admitted current mask and exact source/decision identity. Existing Exit/state
   values conflate detection, snapshot and natural completion. Encoding fields,
   timing origin and policy must come from the adopted contract, not this map.
2. **Actual Robot matrix.** Add public-input scenarios for SIDESTEP outer abort
   in PIVOT/TRAVERSE/TURN_IN, front priority in later phases, both mirrors;
   ARC front abort in TRAVERSE/TURN_IN, ignored outer targets, inner transition
   negative controls; WAIT HOLD-side and all delegated-phase equivalents.
   Preserve exact same-observation D034 routing and subsequent qualification.
3. **Priority ties.** Existing pure tests cover simultaneous front/outer at
   phase completion; actual Robot evidence needs SIDESTEP PIVOT front+outer and
   WAIT HOLD front+side classification without incorrectly demanding DEFEND when
   current front makes D034 choose TRACK. Test confirmed detection with edge,
   STOP and global source fault on the same call: higher-priority outcomes must
   not become successful opener-abort evidence.
4. **GO-time DIRECT.** Evidence must capture or deliberately classify a current
   detection on the same GO observation despite no prior committed OPENER state.
   Pair it with saved-front/no-current and saved-front/current-side controls.
5. **Negative completion controls.** Natural DIRECT/WAIT expiry; natural turn
   completion with inner-side target; ARC completion entering TURN_IN; WAIT cue
   and inner-side phase transitions; disabled/direct-invalid entry. Existing
   behavior checks do not assert absence of a future abort record.
6. **Exactly-once/lifetime.** New record pulses must not replay for terminal
   exits, duplicate decisions or repeated source evidence. Test reset/restart,
   attempt replacement and mode capture through the public button path, with
   wrapped timestamps and genuine valid source continuity. Existing general
   duplicate/event tests are not proof of a new evidence owner's lifecycle.
7. **Raw versus confirmed timing.** Current integration tests use truthful
   scripted fresh observations and OPP_SET_TICKS2. They establish same-decision
   routing from confirmed perception, not measured ADC/read-to-wheel latency.
   Any proposed latency metric must specify admitted source/decision endpoints,
   account for debounce, and keep application-receipt time distinct.
8. **Serialization and lost evidence.** Once specified, independently test the
   new wire/metadata validator, retained historical modes1..6, recorder event
   ordering, duplicate suppression and capacity/incompleteness behavior. A new
   record must not weaken old event validation or imply motor permission.
9. **Physical acceptance remains separate.** P5.3's10/10 physical trials,
   mirror10-degree criterion, actual safe geometry and actuator latency are not
   supplied by source coverage or any forthcoming host evidence tests.

These are gaps in explicit new-evidence assertions and integration breadth,
not findings that the extensively unit-tested opener behavior is incorrect.
