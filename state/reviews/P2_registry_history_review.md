# Historical registry evidence review

**PASS — exact two-path test fix.** No open findings. Reused separate same-model reviewer; source inspection and private WSL execution only. No firmware or locked-test changes.

- **MAJOR, closed:** `tests/tooling/test_vbat.py:169` compared D110's historical before-image to the live registry with only the D110 insertion removed. Later approved D111 literals broke that historical assertion. `test_imu_heading_bench.py:177` had the same future coupling. The original D110 failure was independently reproduced.
- Exact byte-diff proof confirms only the two after-image input paths changed. Original count/removal/equality assertions, current `run_registry` calls and all negative controls remain byte-identical. Historical snapshots match their adoption hashes; no replacement baseline was created.
- Private corrected targeted methods passed. Six independently corrupted current values (D110 count and all five D111 values) each failed through the live18-check value assertion; both deliberately corrupted historical after-images failed their original byte-delta assertions.
- Both corrected methods also passed a clearly labelled synthetic future registry/config addition in a temporary copy. That simulation changes no repository source or adopted requirement.
- Evidence: `state/analysis/P2_registry_history_raw/reviewer/run_1790197999487220910.json` retains all11 commands, expected failures, snapshot hashes and initial copied-file hashes; final binding is `reviewer/final_review.json`.
- Earlier D110/D111 verdicts remain bound to their original source/test snapshots; this does not retroactively claim that the entire historical suite passes against every later registry.
