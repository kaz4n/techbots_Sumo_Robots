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

Protected conflicts: analysis/spec_conflicts.md. SC-C and SC-D1 are approved by
D-017/D-018; the other recommendations remain unapproved.
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

No circuit/acquisition/escape/ALL_IN/overflow recommendation is approved. D-017
resolves final governor caps and D-018 resolves services-before-gate ordering.
Obtain each remaining protected decision before dependent work.

Manual work is ordered in docs/P0_MANUAL_CHECKLIST.md. The first reply only needs
isolation/connections, SSH setup, exact breakout/part identities and available
instruments. The blank P0_MEASUREMENTS_TEMPLATE.md is not measurement evidence.

## Current development track (D-016) — 2026-09-22 18:10 Asia/Dubai

| Existing P1 task | Status | Evidence / dependency |
|---|---|---|
| 1.1 interfaces | PARTIAL | types/countdown/edge/opp_fusion/governor committed before implementation/tests; other interfaces await relevant contracts |
| 1.2 B3 Gate and logical Buttons | IMPLEMENTED / HOST-TESTED | a37b1c5; 19 locked cases; raw/qualified timestamp wiring and other B3 services pending SC-J/K |
| 1.2 B4.1 classifier | IMPLEMENTED / HOST-TESTED | e30d4c2; 6 locked cases/all16masks; fresh-observation API only, acquisition/escape pending |
| 1.2 B5.1 and B5.2 front rows | IMPLEMENTED / HOST-TESTED | 2c2f55e; 12 debounce +10 front table cases; full fusion pending |
| 1.2 B6 governor | IMPLEMENTED / HOST-TESTED | 0742bd9; 29 cases; D-017 final caps/slew; target-loss FSM brake/profile integration pending |
| 1.3 properties | PARTIAL | 10,000 Gate streams +10,000 separate Buttons streams; front-table symmetry; full R1 output/MotorGate and R5/openers/escape properties remain pending |
| 1.4 architecture | PARTIAL | docs/ARCHITECTURE.md describes actual standalone components and Gate; complete Robot FSM still absent |
| 1.5 target compile | HARDWARE-PENDING | No connected board/SSH target; never reported compiled |
| 1.6 safety review | SCOPED PEER PASS / GATE-PENDING | reviews/P1_components_codex.md; reused separate context after thread limit, not fresh full gate review |

Aggregate: 77 host cases, 3,457,564 assertions pass; ASan/UBSan pass; 46 tooling
checks pass. Evidence committed in 7cddb1a and summarized in P1_validation.md.
Numeric case count does not complete P1's all-table coverage or physical/gate criteria.

Exact next task: collect the pending SC-J release-anchor and SC-D2 persistent/
all-white decisions, record each approved choice, then define the smallest affected
integration/escape contract and new independent tests. Resolve SC-K before full
countdown services, SC-M before forward escape duty, and SC-L before the affected
fusion stages. D-018's ordering is approved but the full FSM is not implemented.
Do not edit the now-established locked files without human-approved ADR; add new
tests when extending coverage. No P2 HAL work is authorized by D-016.

P0 hardware work resumes separately when available through the checklist above.
P1 still needs full core/table coverage, target compile, genuinely fresh gate
review, EXPLAINED OK and the human GATE P1 PASS. No phase gate has passed.
