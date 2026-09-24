# Current execution checklist - 2026-09-24 Asia/Dubai

**P2 software active.** D051/D075 authorize this work before physical acceptance;
PROGRESS.md owns append-only phase/gate history. No human phase gate passed.
Historical snapshots are preserved in Git (`fbfb0f2e`), not current instructions.

| Existing phase task | Current evidence/status | First unfinished dependency/action |
|---|---|---|
| P0 | Tooling/source checks and inert board diagnostics recorded | Physical/pin/electrical acceptance; human gate |
| P1 | Reviewed core; meaningful host/property/locked tests | Human EXPLAINED OK and GATE P1 PASS |
| P2 B1/B2/B3/B5 | Native drivers and named opponent/QTR/IMU/power benches implemented, host-tested, target-compiled/reviewed | Actual polarity/ranges/colors/cadence/drift/voltage measurements |
| P2 B6 | ADC/decoder/menu/matrix software; D114 captured 128 raw samples captured | Actual A1 circuit/windows/BOTH and UI acceptance; raw floating ADC is not a button test |
| P2 B4 | MotorGate/native boundary and D115 setup/inhibit bench | D119 finite sequence below, then actual directional Robot/Runtime integration; physical stand trial later |
| P2 B7 | Existing inhibition/receipt safety, no full reversal evidence | B7 full reverse/R6 conflict and specific future powered run |
| P2 B8 / 2.3 / 2.4 | Recorder, app dump, calibration output, D116 full synthetic transport, D117 FIFO host/target checks | Native ownership/framing/delivery and actual physical acceptance |
| P2 2.1 / 2.2 | Runtime integration; D118 actual default/M0 load, sampled progress and retained heap | Full live-source five-minute timing/stack/RAM; existing restricted run is not complete WCET |
| P2 2.5 / gate | No physical acceptance claimed | Assembled weight/footprint, B1-B8 measured results, review and human GATE P2 PASS |
| P3-P7 | Not passed; original schedule/scope intact | Required gates and real physical evidence; do not simulate |

## D119 - current bounded implementation

Pure sequence complete; next task is real B4 integration below. Contract/public header/config adoption: `bf2c4524`,
[contract](analysis/P2_stand_sequence_contract.md).

- [x] Identify real directional B4 gap; keep DRIVE_TEST/locked defaults unchanged.
- [x] Adopt pure twelve-row request sequence and explicit 500 ms / 0.25 nominal defaults.
- [x] Freeze independent executable expectations before first implementation execution (amended oracle5e03938c; original retained).
- [x] Implement and pass independent 18-case normal/sanitizer, full 1,496 main + 187 Gate normal/sanitizer,12 reviewer profiles and config checks.
- [x] Separate source/host review PASS; exact checked default/M0 loadables match D118. See [validation](analysis/P2_stand_sequence_validation.md); final commit records this software/evidence.
- [ ] Adopt real Robot/Runtime integration, preserving full hold/source/edge/governor/Gate/receipt behavior; check target fit before acceptance.

The helper never energizes motors and is not a completed directional controller.
A recorded validation extension performed Linux compile-only and artifact checks; no upload, MCU operation or UART action. First registry launch failed
because noncanonical Python imports created a second unpatched module; canonical
imports then passed unchanged tests. Original output retained in D119 raw evidence.

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
