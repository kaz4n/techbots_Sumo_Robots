# P2 application integration map - 2026-09-23

Read-only explorer plus coordinator source inspection while D091 readback runs.
No implementation or phase gate follows from this map. D051/D075 permit software.

src/app/app.ino remains an inert link scaffold: forcedMOTORS_ALLOWED0, one empty
BOOT step insetup and emptyloop. No actual scheduler/HAL/recorder owner exists.
The smallest next bounded change is an explicit whole-tick start/decision timing
contract, then a fixed transaction owner, then native acquisition scheduling.

## SC-AK: acquisition start versus decision time

- P2_imu_integration_contract.md lines34-36 requires decisiontime AFTER acquisition
  so checked/sensor timestamps are not future-dated or backdated.
- P1_robot_contract.md lines74-78 calls that same preceding t_us the whole-tick start.
- src/core/fsm_robot.cpp receiveTiming lines170-174 enforces execution_us equal to
  completed_us minus pending decisiontime; it therefore excludes prior acquisition.

Consequence: using decisiontime asstart undercounts actual wholeloop timing; using
acquisitionstart asdecision rejects correctly timed sensor metadata. D091's203us
synthetic runner maximum excludes sensor acquisition/wrapper and is not full WCET.

Options: A) Add explicitly opted-in acquisitionstart metadata to RobotInput/pending
receipt bookkeeping, preserving existing legacy defaults/tests; validate forward
wrap-safe start<=decision<=application<=completion<=next acquisition/decision and
count actual complete duration. B) Defer app integration. RecommendA underD051.
Freeze an exact public contract before edits; malformed timing alone remains
incomplete evidence, preserving existing motor fault/permission rules. Do not
change any established locked test. Add cases for start/decision distinction,
exact/adjacent duration boundaries, overlap, future/backward/half-range metadata,
wrap, duplicates, reset, GO/finalSTOP membership, actualGate feedback and recorded
frame/event maxima. This is software evidence, not calibration or physical WCET.

## Composition responsibilities after timing

- One nativeport outliving soleMotorGate; initialize inhibition first, apply each
  fresh result once, retain real feedback. src/hal/motors.h, motor_port_unoq.h.
- One power::Reader for A0/A1; sharedreset-only fault/arbitration. No current
  bounded battery-cache age contract: do not invent freshness for slower sampling.
- Opponent electricalrawmask passes once without extra polarity transform.
- AsyncQTR start/advance needs sub-tick cooperation:10uscharge must be serviced
  within100us; starts>=2000us, complete<=2500us. Once-per-tick is insufficient.
  Apply completedretainedframes through line_qtr_adapter; no duplicatefreshness.
- IMU cooperative setup/acquisition/estimator/adapter; continuousyaw stays unreset
  atGO and acceptedbias applies only afterRobot request.
- UI uses qualified A1 evidence, one native matrixowner and QTRcal overlays/banks;
  actualbuttonwindows remain unconfigured. DRIVE_TEST remains unavailable.
- RetainedAttemptRecorder lifetime: Robot->MotorGate->consume->Transfer. Pump only
  on valid currentIDLE authority and decisionage<TICK_US, with control priority.
- NativeUART needs cleanframing/exclusiveownership; no lazyloopbegin (ACK wait).
  Local-only reset/UI lifetime contract and QTR_CAL thresholdprinting remain open.
- Setup failures/unverifiedgrants stay inhibited. No assumed watchdog API.

Independent source-based ceilings already total IMU600+motor150+ADCpair100=950us,
before other work. Scheduler must explicitly solve resource/timing contention;
a host benchmark or simply summing averages cannot close R4. Physical wiring,
SC-A windows, SC-AJ calibratedtime and all humanphasegates remain pending.

Reusable test composition: test_recorder_dump/dump_fixture, qtr_cal_fixture and
handover/Gate cases, test_imu_integration, test_button_motor_gate, test_robot_events
and test_tick_statistics. Use new additive tests from frozenpublic contracts.

## Independent public-contract test audit (no implementation-body reads)

The separate test author inspected public headers/contracts and existing tests
only. No D092/interface was frozen. Before implementation choose timing opt-in
lifetime, treatment of malformed current start when bounding the previous receipt,
a common unsigned half-range chronology anchor and GO-tick membership. Recommend
including acquisition before the GO decision while preserving GO/hold timestamps.
Keep valid motor-application evidence independent of timing-only metadata errors.

New independent fixture required: existing Rig.at/timedReceipt explicitly measure
from the preceding decision and would hide the acquisition exclusion. Cover:

- Acquisition600us plus later work401us must count1001us, not401us.
- Equality and adjacent ordering boundaries;799/800/801 and999/1000/1001us. B14
  overrun stays strictly greater than1000us, distinct from R4 acceptance800us.
- Natural wrap at each boundary; half-range minus1/exact/plus1; reject ambiguous
  order without signed overflow. Validate completion<=nextstart equality.
- Wrong duration/futurestart/completion-before-application/overlap mark timing
  incomplete only. Wrong token/application order/duties retain motorfault rules.
- Countdown precedingGO excluded; GO and finalSTOP included once; STOP atGO
  suppresses GO; canceled countdown has no match-duration samples.
- Duplicate decisions ignore changed start/receipt; later fresh receipt consumes
  original token once. Reset discards pending timing and preserves token sequence.
- Valid warning timestamps use completion; invalid use detection; preserve event
  order across wrap. Frame maxima65535/65536 retain codec clamping metadata.
- Actual Robot->MotorGate(fake callbacks)->AttemptRecorder preserves application
  time, final deferred seal and counters. Include explicit fresh/retained IMU
  evidence betweenstart/decision; its source age remains decision-based.
