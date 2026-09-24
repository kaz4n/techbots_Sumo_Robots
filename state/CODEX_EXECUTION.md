# Current execution checklist - 2026-09-24 Asia/Dubai

**Active: P5 software.** D134 is host-complete/reviewed; D135 is implemented and
under final validation; D136 offline analysis contract is adopted. Physical gates
remain pending under D051/D075/D122 scheduling authority. PROGRESS.md is the
append-only phase/gate history. Do not rewrite its legacy bytes.

| Existing phase tasks | Software evidence | Remaining acceptance |
|---|---|---|
| P0 | Scripts, source/API checks, actual inert diagnostics | Electrical/pin verification and human gate |
| P1 | Core, properties, locked safety and review | Human EXPLAINED OK/GATE P1 PASS |
| P2 B1-B6/B8 | HAL, benches, actual Runtime and recorder; D118 inert app observed | Actual sensors/buttons/motors, PINMAP, dump transport, live stack/WCET |
| P2 B7 | Inhibition/receipt checks | Full reverse/R6 conflict, actual reversal |
| P3 3.1-3.7 | Drive/turn/stop profiles and countdown analyzer | Physical trials, tuning and gate |
| P4 4.1-4.7 | Reactive/timing profiles, target-loss analysis, bounded push, literal admission | Physical trials, current full-app native fit and gate |
| P5 5.1-5.5 | Six openers, D134 availability complete; D135 below | D136 analysis; actual opener/mirror/UI results and gate |
| P6/P7 | Pending original scope/schedule | Actual P4 gate by30Sep forP6, freeze/rehearsal/release evidence |

## Current D135 work

- [x] Reviewed contract, interfaces and independent original public/private freezes.
- [x] Production2d924f1f; new18 tooling methods PASS.
- [x] Preserve first failures; reviewed draft-oracle correction94a7bb5d.
      Production and42 established protected sources unchanged.
- [x] Full20 host targets PASS; private13 cases perM0/M1 PASS (full_retry2).
- [ ] Configured42-case M0/M1 normal and private checks.
- [ ] Normal/configured M0/M1 ASan/UBSan and private checks.
- [ ] Prior admission/regression, legacy layouts, eight copied-source fault probes.
- [x] Exact inert target compile and conditional model fit1328B (F149/4b1e701e).
      Wrapper omits full app dump owner; it does not fix default-app32B deficit.
- [ ] Final separate review and acceptance of new locked candidate.

Pipeline70124 serially owns the host compiler until its final receipt. Inspect
P5_abort_timing_raw/{full_retry2,configured_first,sanitizer_first,
configured_sanitizer_first}.json; a started log is not a result. Preserve656
frozen inputs until complete. Then run state-only run_tools.py admission and
regression, run_layouts.py layout_first and run_faults.py faults_first, serially.
Each runner records commands/status and cleans only its own completed scratch.
Fault injection changes copied implementation only; it is post-review probing.

## Next eligible work

1. Complete D135 checks/review against exact bytes; fix actual findings without
   weakening established tests. No repeated matrix absent a relevant change.
2. Inspect one authorized isolated default-fit native experiment. Do not adopt
   its three-file candidate until target layout/fit and unchanged host default/
   positive-window regressions plus independent review support it. See
   analysis/P5_default_fit_experiment.md; no upload is part of the experiment.
3. D136 contract and five decisions adopted; pure decode_cue seam clarified.
   Independent public/private drafts live under state. Freeze first, implement
   new offline companion only after D135 frozen validation ends. Do not alter
   CSV/D130 tools or manufacture physical eligibility/acceptance.
4. Finish P5 software acceptance packet, then recover next eligible original
   phase task under scheduling authority; P6 deadline condition remains binding.

Read analysis/P5_mode_availability_validation.md for completedD134; its matrices
and60+296 tooling checks need no rerun unless later changes affect them. Source
identity, host success, target compile, loader model, actual upload and physical
acceptance are distinct. Last MCU upload remains consumed D118defaultM0; no new
upload/reset during this resume. BareUNOQ currently reported connected alone.

Storage: C: about2.49GB at last check. Use /dev/shm and one host compiler,
archive compact receipts before releasing temporary builds. Keep checked ELFs,
unique evidence/source/userdata. Historical85.48MB and new1.70MB deletion batches
were rejected by automatic review; do not retry another route. STORAGE_LOG.md
records cleanup history. No persistent virtual disk or system paging changes.

Schedule: no actualP3 gate by end28Sep invokes reactive+SIDESTEP/DIRECT cut;
P6 requires actualP4 by30Sep and no stronger cut. Freeze1Oct21:00 Dubai;
rehearsal2Oct, competition3Oct. Never write a human gate or infer run permission.
