# Execution checklist: P1 host development, P0 acceptance pending

PROGRESS.md is the phase/gate authority. No gates passed; no motor-run authorization.

| Existing task | Status / dependency | Acceptance / evidence / next action |
|---|---|---|
| Kickoff migration | IMPLEMENTED | D-015, AGENTS addition, CODEX_HANDOFF, baseline 52b935e |
| P0 0.1 G1-G6 | SOURCE-REVIEWED | analysis/P0_G*.md; merged FACTS F-019–F-060; MPU6050 user-reported, installed/electrical acceptance pending |
| P0 0.2 scripts | IMPLEMENTED / SCRIPT-TESTED | 98d4524 adds read-only preflight and inert startup selection; 45/45 checks in P0_preflight_tests.txt; reviews/P0_preflight_codex.md PASS; real board result separate |
| P0 0.2 round trip/startup | HARDWARE-PENDING | SSH target, safe bare board, installed versions, matrix + counter, both startup times |
| P0 0.3 scaffold | HOST-TESTED | 7968434; exact 76 B16 defaults (corrected earlier 77 claim); CTest1/1; P0_host_tests_recovery.txt |
| P0 0.4 micro-benchmarks | PARTIAL / HARDWARE-PENDING | Inert RAM lateness capture and matrix sketch host-tested; real 60 s jitter/max/p99, GPIO/QTR/ADC and MPU6050 I2C still unmeasured |
| P0 0.5 pin map | BLOCKED | source inventory, physical checks, approved changes, PINMAP OK |
| P0 review/gate | GATE-PENDING | Scoped software review PASS (reviews/P0_recovery_codex.md); prepared P0_gate_request.md; physical evidence and human gate absent |

Protected conflicts: analysis/spec_conflicts.md. No recommendation is approved.
## Exact next task / dependencies

All currently executable P0 host recovery tasks are checked and saved. The user
cannot currently supply connection/setup details and identifies the IMU as
MPU6050. Keep intended connectivity as an assumption, not verified evidence.

1. When an SSH alias/user is supplied, run the read-only installed-board preflight
   with `bash tools/preflight.sh`, save its JSON to a new timestamped file and
   inspect CLI/core/board details/libraries/tools/listeners. Follow up separately
   on loader configuration/library source/router identity from P0_G4. No upload
   or reset is part of this inventory.
2. Before inert board upload, confirm physical isolation and exact source snapshot.
   Resolve SC-I explicitly before implementing the printed Monitor counter; the
   RAM counter does not satisfy the round-trip requirement. Measure startup modes
   and 0.4 timings using verified setup and record actual values.
   Immediate matrix uploads are separately blocked by F-061 until installed
   loader/matrix ownership is resolved. Exclude the boot logo and account for
   display delay when choosing a sketch-start observation method.
3. Identify the MPU6050 breakout/interface and address; use the specific tests in
   P0_G6. Do not adopt the inspected Adafruit read path or synchronous I2C fault
   path unchanged. No new driver, ODR, filter, wiring or INT pin is approved.
4. Finish 0.5 electrical/pin checks, obtain PINMAP OK, complete the full fresh gate
   review and wait for the human's GATE P0 PASS. P1 host development is now
   separately permitted by D-016; this does not satisfy P0 acceptance.

No circuit/timing/governor/arbitration/overflow recommendation in the conflict
register is approved. Obtain each protected decision before dependent work.

Manual work is ordered in docs/P0_MANUAL_CHECKLIST.md. The first reply only needs
isolation/connections, SSH setup, exact breakout/part identities and available
instruments. The blank P0_MEASUREMENTS_TEMPLATE.md is not measurement evidence.

## Current development track (D-016)

- P1 1.1: partial contracts for types/countdown/edge classifier/opponent debounce;
  commit these before separate spec-derived tests and implementation.
- P1 1.2/1.3: implement and independently test those unambiguous standalone
  components, including countdown boundaries, wraparound and 10,000 seeded input
  streams. Do not claim the complete R1 hardware or R5 arbitration proof.
- P1 remaining interfaces/behaviors: blocked where listed in spec_conflicts.md;
  governor and full FSM ordering questions are pending explicit human replies.
- P1 target compile, full test/table coverage, safety gate review, EXPLAINED OK and
  GATE P1 PASS remain pending. No P2 HAL work is authorized by D-016.
