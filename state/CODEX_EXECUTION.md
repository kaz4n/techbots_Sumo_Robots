# Current execution checklist - 2026-09-24 Asia/Dubai

**Active: P4 software under D128; D129 host validation/review complete; native validation pending.**
D051/D075/D122 permit software scheduling before physical acceptance. Assumptions
are not measurements, human gates or run permissions. PROGRESS.md is the
append-only phase/gate history; historical checkpoints remain in Git.

| Existing task | Software evidence | Outstanding acceptance/dependency |
|---|---|---|
| P0 | Scripts, source/tool checks, recorded inert board diagnostics | Physical electrical/pin acceptance and human gate |
| P1 | Reviewed core, host/property and locked safety tests | Human EXPLAINED OK and GATE P1 PASS |
| P2 B1-B6 | Native drivers, named benches, calibration/UI and actual Runtime integration | Real sensor, motor, ladder/BOTH and pin qualification; fresh run permission |
| P2 B7 | Inhibition/receipt safety exists | Full reverse/R6 conflict and actual reversal trial |
| P2 B8/2.1-2.4 | Recorder/dump software, D118 actual inert app observation | Native transport ownership/framing, full-source WCET/live memory/stack and physical acceptance |
| P2 2.5 | Software packet retained | Assembled size/weight, actual B1-B8 results and human gate |
| P3 3.1-3.7 | D123 drive, D125 turn, D126 stop profiles; D127 countdown analyzer | Physical trials, evidence-backed tuning and GATE P3 PASS |
| P4 4.1-4.7 | D128 reactive profile, D129 timing trace host-tested/reviewed | Offline loss analyzer; bounded positive push-through software; all real trials/gate |
| P5 | Existing core openers and tests | Eligible phase software review and physical opener evidence |
| P6/P7 | Pending; original scope/schedule retained | P6 actual P4 gate by30Sep, freeze/rehearsal/match evidence; no inferred release tag |

## D129 current checks

- [x] Contract, conditional interfaces and independent original oracle frozen.
- [x] Chronology MAJOR reproduced, fixed, unchanged private regression passes.
- [x] All14 normal targets; new30-case M0/M1 normal/sanitizer and32-case
      configured-button normal/sanitizer pass.
- [x] Separate8-case M0/M1 review probes and six old host layouts pass.
- [x] Two unchanged config registry methods pass;39 old locked files unchanged.
- [x]149tooling methods PASS after one independently corrected new draft
      syntax assumption; original failure/oracle retained. No production change.
- [x] Final scoped review PASS; newlocked e384e7fb accepted and protected.
- [x] Local completion commit includes this checkpoint and its bound evidence.
- [ ] Exact board-side inert compile/default-byte compatibility/native fit;
      fresh ADB inventory has no board. Prepared runners are not execution proof.

Evidence: analysis/P4_timing_evidence_validation.md and its raw directory;
reviews/P4_timing_evidence_review.md. Earlier WSL-interrupted runs remain retained.
No D129 upload/reset/motor action or physical result occurred.

## Next eligible tasks

1. Adopt proposed analysis/P4_loss_analysis_contract.md, then independently author
   and implement the read-only D130 interval analyzer. No fabricated trial data.
2. Address P4.4 bounded push-through implementation before any positive tuning;
   current EDGE_PUSH_THROUGH_MS stays0. Use the original B9.4/R5 contract.
3. Use analysis/P4_software_acceptance_packet.md for deferred physical4.1-4.7.

Storage cleanup43319eec removed only inspected disposable files and losslessly
compressed state; all21145 preexisting evidence hashes matched. Keep build/scratch
in /dev/shm, archive receipts in the same run, execute heavy jobs serially, check
free space, and preserve persistent WSL/Docker disks and checked target artifacts.

Deadline rules: actual P3 gate absent at end28Sep invokes scope cut; P6 needs actual
P4 gate by30Sep; code freeze1Oct21:00 Dubai. No human gate is authored by an agent.
