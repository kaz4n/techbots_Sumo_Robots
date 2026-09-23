# Historical registry evidence review

Reused separate same-model reviewer; source inspection and private execution only. No firmware or locked-test changes authorized here.

- **MAJOR, reproduced test coupling:** `tests/tooling/test_vbat.py:169` compares D110's historical before-image to the live registry with only the D110 insertion removed. The later approved D111 literals therefore fail the old byte-delta assertion. `test_imu_heading_bench.py:177` has the same future coupling.
- Proposed fix is appropriate: each historical byte-delta check reads its already-recorded immutable after-image. Its original count/removal/equality assertions remain unchanged. The unchanged `run_registry` calls and negative controls continue checking the live registry/configuration.
- Existing D110/D111 after-image hashes are recorded at adoption; no new baseline or expectation is being manufactured. Final two-line diff, snapshot identity and private live-value negative controls remain pending.
- Earlier D110/D111 verdicts remain bound to their original source/test snapshots; this does not retroactively claim that the entire historical suite passes against every later registry.
