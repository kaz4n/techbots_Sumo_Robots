# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS.md is authoritative. Original goal ACTIVE/incomplete. P0/P1 gates still
pending; D-068 offline B8 and D-071 compile experiment are narrow selected tracks.
No app/Bridge runtime integration, physical acceptance or phase pass inferred.

| Existing phase task | Verified status/evidence | Remaining dependency |
|---|---|---|
| P0 G1-G6/tooling/scaffold | source/installed checks,335 current controlled tooling cases; FACTS | Physical electrical acceptance/PINMAP OK |
| P0 matrix/counter/timing | prior counters and60000scheduler samples; P0_counter_validation | Optical matrix/true cold startup checks |
| P0 ADC/GPIO/QTR | prior setup-only measurements; P0_*validation | Actual sensors/stock API hazards/full WCET |
| P0 G2/G6 probes | Actual compile-only source/ELF reviewed660eb08/b7bd0df | Runtime PWM/IRQ/I2C remains separate |
| P0 gate | GATE-PENDING; reviews/P0_gate_request | Original physical evidence/human GATE P0 PASS |
| P1 core1.1-1.6 |895corecases/10000Robotstreams/actual inert target compile reviewed | EXPLAINED OK/human GATE P1 PASS |
| P2 B8 frame/attempt storage | D069/070 f733c4e/193bd33;969hostcases normal+ASanUBSan reviewed | Target deployment/app/transport absent |
| P2 B8 memory experiment | D071 f351d20;245candidate+lockedcases/8451027 normal+ASanUBSan;335tools;target25compile226584B PASS | Production50unchanged; load/full-HAL/free-RAM/200s/dump/WCET pending |
| P2 remaining drivers/integration | NOT ACCEPTED/DEFERRED | Eligibility, hardware/API contracts and human gates |
| P3-P7 | UNFINISHED | Original dependencies/measurements/run approvals/gates |

Next: decide production cadence under D-051 using F090/091 and D071 actual
candidate evidence before source/config/B16/test changes.25Hz clears only this
image's size check; full-HAL/runtime/physical headroom remains unmeasured.
Use independent unlocked expectations and original locked regression runs.

SC-A buttons,SC-B QTR freshness,SC-I Bridge,SC-AG IMU and ADC/PWM hazards remain.
SC-AH default50Hz actualprobe356608B fails262144B. Candidate25 is226584B; its
source-derived pristine loaderpeak230072B is not measured freeRAM. Inherited
Bridge hook can block indefinitely; user setup/loop inertness does not fix it.

MCU last known uploaded inertQTR61d7a2d0/dcca300/default/MOTOR0 at03:00:13.327+04.
D071 performed Linux builds/read-only ELF capture only. Existingfiveguards remain
193bd33; no upload entry, locked/B16 change, motor permission or human gate.
No workers/commands remain running. Keep failure receipts and source hashes.

No scope cut due23September. Apply Sep28 cut if P3notpassed; retain Sep30 P6
eligibility and Oct1 21:00Dubai freeze,Oct2rehearsal/Oct3competition. No push/tag.
