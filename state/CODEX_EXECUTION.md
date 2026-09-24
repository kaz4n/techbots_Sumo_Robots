# Current execution checklist - 2026-09-24 Asia/Dubai

**P3 software active under D122.** The user's assumed physical acceptance permits
software scheduling only; missing physical results remain unmeasured. D051/D075
and D122 authorize software work before physical acceptance;
PROGRESS.md owns append-only phase/gate history. No human phase gate passed.
Historical snapshots are preserved in Git (`fbfb0f2e`), not current instructions.

| Existing phase task | Current evidence/status | First unfinished dependency/action |
|---|---|---|
| P0 | Tooling/source checks and inert board diagnostics recorded | Physical/pin/electrical acceptance; human gate |
| P1 | Reviewed core; meaningful host/property/locked tests | Human EXPLAINED OK and GATE P1 PASS |
| P2 B1/B2/B3/B5 | Native drivers and named opponent/QTR/IMU/power benches implemented, host-tested, target-compiled/reviewed | Actual polarity/ranges/colors/cadence/drift/voltage measurements |
| P2 B6 | ADC/decoder/menu/matrix software; D114 captured128raw samples | Actual A1 circuit/windows/BOTH and UI acceptance; raw floating ADC is not a button test |
| P2 B4 | D115 inhibition plus D119/D120 finite directional actual Robot/Runtime/Gate profile; host/sanitizer/target checks | Physical source/pin qualification and separately authorized stand trial |
| P2 B7 | Existing inhibition/receipt safety, no full reversal evidence | B7 full reverse/R6 conflict and specific future powered run |
| P2 B8 / 2.3 / 2.4 | Recorder, app dump, calibration output, D116 full synthetic transport, D117 FIFO host/target checks | Native ownership/framing/delivery and actual physical acceptance |
| P2 2.1 / 2.2 | Runtime integration; D118 actual default/M0 load, sampled progress and retained heap | Full live-source five-minute timing/stack/RAM; existing restricted run is not complete WCET |
| P2 2.5 / gate | No physical acceptance claimed | Assembled weight/footprint, B1-B8 measured results, review and human GATE P2 PASS |
| P3 | SOFTWARE-ACTIVE / ASSUMED-PHYSICAL prerequisite under D122 | D123 DRIVE_TEST implemented/host-tested/target-compiled; next finite 3.4 turn trial; original 3.1-3.7 measurements remain pending |
| P4-P7 | Not passed; original schedule/scope intact | Later software scheduling and real physical evidence; do not simulate |

## D119/D120 - completed directional software

Pure sequence completed in1c387810; integration contract/public adoptionf4a300c5.
[Integration validation](analysis/P2_stand_integration_validation.md) records exact
commands, original harness failures, source hashes and all target/evidence limits.

- [x] Identify real directional B4 gap; keep DRIVE_TEST/locked defaults unchanged.
- [x] Adopt pure twelve-row request sequence and explicit 500 ms / 0.25 nominal defaults.
- [x] Freeze independent executable expectations before first implementation execution (amended oracle5e03938c; original retained).
- [x] Implement and pass independent 18-case normal/sanitizer, full 1,496 main + 187 Gate normal/sanitizer,12 reviewer profiles and config checks.
- [x] Separate source/host review PASS; exact checked default/M0 loadables match D118. See [validation](analysis/P2_stand_sequence_validation.md); final commit records this software/evidence.
- [x] Actual conditional Robot/Runtime integration retains full hold/source/edge/governor/Gate/receipt behavior and one-run STOP/coast handling.
- [x] All4normal/sanitizer host targets; configured A1 fixture19cases eachM0/M1 in both profiles;54tooling methods and9private profile probes.
- [x] Checked default/M0 app bytes unchanged; dedicated inert motor_direction compiles and conditionally fits with13568bytes free span.

Software verification is distinct from physical direction, brake/coast, PWM and
kill-latency acceptance. No upload, MCU operation or UART action occurred in D120.
No motor-capable checked build/run route was enabled; original locked tests stay
unchanged, and new D120 locked oracle4546df24 is now established.

D120 software/evidence commit:1c2389c9. D121 preserves R6 and the original B7
criterion, leaving B7 BLOCKED/NOT ACCEPTED; no low-duty substitute or new stress
controller is selected. [P2 acceptance packet](analysis/P2_software_acceptance_packet.md)
maps every original task to evidence and remaining acceptance, with a fresh
separate readiness review: scoped PASS/no new software finding, full P2 FAIL
with P2-ACCEPT-1..5 open. No further functional P2 software task is currently
established by those requirements. First eligible next action is a supported
review finding or new physical/native prerequisite, not a repeated build/probe.
Historical D121 scheduling stop is superseded by D122's explicit user instruction.
Physical/gate evidence stays pending; proceed with P3 software now.

## Board and blockers

Current last-observed MCU is unchanged D118 default/M0 app e820c0e1; both run
claims consumed. See [actual validation](analysis/P2_app_default_actual_validation.md),
F147 and `fbfb0f2e`: sampled RUNNING/NONE,4,500 free / 4,364 largest,513 us stored maximum,
initialization false / optional grants false. No fresh MCU observation in D119.

Native UART prerequisite remains blocked: [follow-up](analysis/P2_native_dump_prerequisite_followup.md).
Current access cannot inventory privileged holders; last-close/cancel/reopen and
clean framing remain unproved. Do not retry known failed sudo or set missing grants.
User requests only the bare UNO Q for now. Sensors, PINMAP, motor runs, physical
acceptance and human gates remain pending; no extra hardware request is made.

## D123 — P3 DRIVE_TEST software completed

[Validation](analysis/P3_drive_test_validation.md) records all six normal/sanitizer
targets, configured28-case M0/M1,93tooling methods,20private profiles and4private
Runtime cases perM0/M1. New accepted locked oracle5bde7967 is protected; original
unaccepted draft/failure and exact correction retained. All35oldlockedfiles intact.
Actual checked P3M0 compiles with10624byte conditional loader span; defaultM0
compiles with16byte span and differs from prior image by8bytes. No upload/MCU action.
Next: P3 3.4 finite single-turn trial preparation, exact±90/±180 using explicit
coordinate reflection forLEFT; preserve existing Turn/defaulttie. 3.3 stopping
measurement needs common origin and first maximum forward excursion, not final
rest after reverse escape. No real physical results or gates have been invented.


D124 update: the pure finite P3 3.4 turn helper is implemented and host-tested.
Read state/analysis/P3_turn_trial_validation.md and its separate review.
23 focused cases pass normally and with sanitizers; all six host targets pass
(main1519). All36 established locked files are unchanged. Next eligible task is
actual turn-trial Robot/Runtime/Governor/MotorGate integration, not another helper
rerun. No target build, MCU action or physical acceptance in this slice.


## D125 current checkpoint - supersedes prior next-task notes

- [x] Finite3.4trial actual Robot/Runtime/Governor/Gate implementation.
- [x] Independent public28/29-case profiles, allsignedangles, normal/sanitizer, realGatewrites and permanentservice-only inhibition.
- [x] All8normaltargets,107tooling+2registry,4privatecases perM0/M1;36oldlocked exact.
- [x] Checked inerttarget compiled; defaultbinaryexactD123; no MCU action.
- [ ] Next P3 3.3 finite stoppingprofile; SC-AN measurementreference policy before cap inference.

See analysis/P3_turn_integration_validation.md and separate review for receipts,
newacceptedlocked7d6c5193, retaineddraftfailure and actualremainingphysicalwork.


## D126 current checkpoint - supersedes prior next-task notes

- [x] Finite stopping trial through actual Straight/Governor/Gate and full escape.
- [x] All10normal targets, new30-case M0/M1 sanitizer/all5duties, configured31-case normal/sanitizer.
- [x]121tooling+2registry,4privatecases eachM0/M1;37priorlocked unchanged.
- [x] Checked inert target compiled; default binary exact D125; no MCU action.
- [ ] D127 P3.1 countdown-event analyzer: contract adopted; implementation and independent oracle in progress.

See analysis/P3_stop_trial_validation.md and separate review. Accepted locked
01213382 is protected. Physical P3.1-3.7 and human gate remain pending.
