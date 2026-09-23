# Execution checklist - 2026-09-23 Asia/Dubai

PROGRESS.md is authoritative. Original goal ACTIVE/incomplete. P0/P1 gates pending;
D-068/070/071/072/073 select narrow offline B8 storage/compile/formatting work.
No app/Bridge integration, physical acceptance or phase pass inferred.

| Existing phase task | Verified status/evidence | Remaining dependency |
|---|---|---|
| P0 G1-G6/tooling/scaffold | source/installed checks;340current controlledtools;FACTS | Physical electrical acceptance/PINMAP OK |
| P0 matrix/counter/timing | prior counters/60000scheduler samples;P0_counter_validation | Optical matrix/true cold startup |
| P0 ADC/GPIO/QTR | setup-only measurements;P0_*validation | Actual sensors/stock API hazards/full WCET |
| P0 G2/G6 probes | compile-only source/ELF reviewed660eb08/b7bd0df | Runtime PWM/IRQ/I2C separate |
| P0 gate | GATE-PENDING;reviews/P0_gate_request | Physical evidence/human GATE P0 PASS |
| P1 core1.1-1.6 |895corecases/10000Robotstreams;inert target compile reviewed | EXPLAINED OK/human GATE P1 PASS |
| P2 B8 frame/attempt storage | D069/070 f733c4e/193bd33 reviewed | Runtime integration/transport absent |
| P2 B8 rate/memory | D072 9acc0cc;975hostcases normal+sanitizer;340tools;current25Hz target probe226584B | Load/fullHAL/freeRAM/200s/dump/WCET |
| P2 B8 offline CSV | D073 ea2d6b0;993hostcases/16989315assertions normal+sanitizer,340tools;fresh review PASS | No target/runtime/dump integration |
| P2 remaining drivers/integration | NOT ACCEPTED/DEFERRED | Eligibility/API/physical/human gates |
| P3-P7 | UNFINISHED | Original dependencies/measurements/run approvals/gates |

Next: D073 formatting is complete. Read P2_csv_next_task_audit.md; select a
narrow contract for host-only local CSV evidence validation before code. Preserve
raw values/loss and distinguish local integrity from recording completion and
unknown session/provenance. No live transport/dump_match.sh, current IDLE inference
or phase bypass. No command/worker continues in the background.

SC-A buttons,SC-B QTR freshness,SC-I Bridge,SC-AG IMU and ADC/PWM hazards remain.
SC-AH production rate choice resolved25Hz; full deployment still open. Compiler
35560B difference/conditional230072B loaderpeak are not measuredfreeRAM.
Inherited Bridge hook can block indefinitely; inert user code does not fix it.

Last known MCU inertQTR61d7a2d0/dcca300/default/MOTOR0 at03:00:13.327+04.
D071/072 performed Linux compile/read-only capture only. Five existingguard hashes
updated inea2d6b0 after exact source review; same five keys and authority.
D072 target226584B is not a target build of subsequent D073 source.
No STAND OK/RING OK, phase pass, push or tag.

No scope cut due23September. Apply Sep28 cut if P3notpassed; retain Sep30 P6
eligibility and Oct1 21:00Dubai freeze,Oct2rehearsal/Oct3competition.
