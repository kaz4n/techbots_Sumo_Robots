# D134 P5 mode availability independent scoped review

Verdict: PASS for the D134 scoped host software packet. No open BLOCKER, MAJOR or MINOR finding. This is not a phase-gate or hardware verdict.
Provenance: separate-context, same-model reviewer with prior P4/design context; not cross-model. Private expectations were frozen before new production/public test body reads. Coordinator executed frozen private probes; reviewer independently inspected receipts and adjudicated failures.
Scope: bounded menu, disabled direct starts, Robot inhibition, staged raw admission, historical IDs, all four flag pairs, default layouts and preserved MotorGate authority. Actual source review is retained in `P5_mode_availability_review_raw/source_review.md`.

## Findings and dispositions

- CLOSED MINOR, `tests/fixtures/mode_availability_fixture.h:109`: implicit brace assignment failed compilation. Typed `fsm::RobotResult{}` preserves aggregate defaults; syntax and full build now pass, with original failure retained.
- CLOSED MAJOR, `tests/locked/test_mode_availability_safety.cc:41`: new unaccepted draft incorrectly required zero for all white masks. B4 row-specific repair preserves first-observation priority, exact B6 transition/settled demands, fault inhibition and actual M0/M1 PWM receipts. Corrected 20 public cases pass under both motor profiles; all 41 prior protected sources remain byte-exact.
- CLOSED private-harness defect, `P5_mode_availability_review_raw/private_modes_first.cc:197`: original stale-snapshot setup omitted B3's final 300 ms sampling window. Setup-only repair proves saved front and current-mask preconditions, retaining all original routing/contact/no-ATTACK/cap assertions. Corrected six cases pass under M0/M1; original probe, manifest and first failure remain retained.
- CLOSED MAJOR, `host/CMakeLists.txt:228`: inherited timing-only D131 source was attached to timing-disabled ordinary targets. Moving unchanged assertions to existing timing targets restores the complete 18-target normal build; the positive20 supplement also passes all positive-only bodies. Earlier P4 final-build coverage was overstated because its full pass preceded that test addition; the historical correction remains retained.
- No source finding: menu work is bounded at six candidates; direct rejection and Robot's final inhibit preserve authority. No new object fields, runtime allocation, I/O or unbounded work. Tooling rejects malformed/partial/disabled-default raw definitions before legacy fallback; historical source approvals remain independent.

## Verified retained evidence

- `default11_full_retry2.json` / `LastTest.log`: full ordinary build and all 18 CTest targets PASS, including 20 D134 public cases per M0/M1. Private receipt: six cases and 6,532 assertions per motor profile, no failures/skips.
- Four ASan/UBSan pairs 11/00/01(default 6)/10(default 4): each passes 20 public and six private cases under M0/M1, no failures/skips or sanitizer diagnostics. All commands exit0 and scratch is released.
- `positive20_profile_sanitizer.json`: configured 20 ms, timing-enabled ASan/UBSan profile passes all 37 push cases and exactly five D131 timing cases per M0/M1. Its timing filter deliberately excludes 32 other cases per binary; complete legacy D129 remains covered by the separate zero-duration full suite. All eight command-output hashes, full log/runner hashes and copied-tree stability verified in `final_host_receipt_review.json`.
- `admission_first.json`: 60 methods PASS (26 D134, 32 D132, two registry); `regression_first.json`: 296 methods PASS, no failures/errors/skips. `python_first.json`: eight independent private methods PASS with external processes/network forbidden.
- `layout_first.json`: fixed cf35d0a8 baseline and final 11/00/01/10 under M0/M1 retain host sizeof/alignment: Menu 28/4, Flank 152/8, Wait 216/8, Robot 2640/8, Runtime 166624/8. All 22 commands pass; source unchanged and temporary scratch released. No target ABI/fit/WCET claim follows.
- `resume_binding.json` and final receipt review: all 649 combined and 523 core frozen entries match current bytes after execution; all 41 prior protected source files match original 425c8a97. No production/test/manifest changes were made by this reviewer during resume.

## Limits

Unchanged historical all-six assertions run on shipped 11. A future reduced-source release needs the explicit actual-profile additive checks plus an identified temporary all-six/default variant for unchanged legacy assertions; `tools/test_host.sh` alone is not a reduced-mode release runner. No assertion skipping or protected-test changes are approved.
Native compilation, target RAM/loaded fit, full-tick WCET, physical P5 trials, human gates and specific motor-run authorization remain pending. Host evidence establishes none of these.
