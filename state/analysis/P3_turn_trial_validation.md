# D124 finite turn-trial helper validation

Implemented and host-tested on 24 September 2026, Asia/Dubai. This closes the
pure helper portion of P3 3.4; actual Robot/Runtime integration is next. No target
compilation, upload, physical angle measurement or phase acceptance occurred.

The independent author derived 23 tests from the public header and contract,
without reading implementation bodies. The accepted oracle is
`ab5547d2e0100b1aa501e2666c43068bc5bba9831f5a998c1beaed211ab5bbd1`;
implementation is `cc88727fa5a19117ceb88ad3c4b068ea4df815a8570f7d5c7b80c23ae4d3d62f`.
The contract clarifications preceded the freeze and first execution. Existing
motion primitives, B16 defaults and all 36 established locked files are unchanged.

Evidence and exact commands are in [P3_turn_trial_raw](P3_turn_trial_raw/).
`run_checks.py` verified ten frozen source/oracle hashes before each profile.
Normal and ASan/UBSan focused builds each passed 23 cases / 9,300 assertions.
Full host regression passed all six targets, with zero failed or skipped cases:

| Target | Cases | Assertions |
|---|---:|---:|
| Main | 1,519 | 50,427,846 |
| MotorGate enabled | 187 | 4,536,952 |
| B4 M0 / M1 | 18 / 18 | 200,690 / 200,641 |
| P3 DRIVE_TEST M0 / M1 | 27 / 27 | 248,475 / 231,229 |

The runtime config registry passed both tests. That legacy harness appended its
receipts to the historical P2 evidence file. After verifying the current file
began with the exact committed 36,566-byte prefix, only this run's 35,740-byte
suffix was relocated here as `registry_cases.jsonl`; the original prefix was
restored byte-for-byte. `registry_relocation.json` records hashes and lengths.
No historical evidence or test expectations were changed to obtain a pass.

The separate same-model reviewer inspected source and ran an independent
property oracle in normal and sanitizer builds, 1,309,352 checks each. Its
[review](../reviews/P3_turn_trial_review.md) and private evidence are separate
from the public author and implementation. These are software checks, not
measured heading accuracy, physical settling, fallback calibration or robot WCET.

The 500 ms brake interval is an explicit development request interval, not a
measurement. DONE and TIMED_OUT remain distinct. Exact left half-turns use a
coordinate reflection; STOP/edge/clock faults permanently cancel the one trial.
Next: connect the helper to the isolated P3 application profile, real source
admission, Governor, MotorGate, retained receipt and finite STOP lifecycle.
