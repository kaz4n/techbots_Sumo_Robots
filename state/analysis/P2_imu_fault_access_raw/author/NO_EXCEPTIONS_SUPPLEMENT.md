# D097 no-exceptions harness compatibility supplement

This supplement supersedes only the final test hashes/counts in SUMMARY.md.
All prior receipts and the original summary remain unchanged for traceability.

Root's first full normal/sanitized CMake builds failed because the new tests used
REQUIRE while repository flags select DOCTEST_CONFIG_NO_EXCEPTIONS. The isolated
runner had selected DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS and therefore
did not detect that integration mismatch. Root retains host_normal_01 and
host_sanitized_01 compiler failures; no production or shared build flag changed.

Correction: every new-test REQUIRE prerequisite uses CHECK with an explicit early
return. The ready/begin helper failures propagate through checked caller guards.
Every original assertion remains; six additional assertions check this propagation.
The callback checks both pointers and explicitly returns before any null call.
The runner now uses DOCTEST_CONFIG_NO_EXCEPTIONS, matching the repository build.
No production CPP or established test was read/changed to apply this correction.

Command from repository root:

```powershell
wsl -d Ubuntu -- python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/tests/tooling/test_imu_setup_failure.py
```

Result: both Python tests pass under UBSan/Werror and the normal no-exceptions flag.
For each of MATCH=MOTORS_ALLOWED=0 and MATCH=MOTORS_ALLOWED=1:

- Actual Acquirer/Setup: 7 cases, 31474 assertions, all pass.
- Actual NativeSources callback/provider substitutes: 1 case, 178 assertions, all pass.

Final callback run receipts: command_1790178956478617940.json and
command_1790178957134759174.json. Final Acquirer run receipts:
command_1790178958798724263.json and command_1790178960160252447.json.
Exact compile commands, staged hashes and raw output streams remain alongside.

Updated frozen SHA-256 (the other two test headers retain SUMMARY.md hashes):

| File | SHA-256 |
|---|---|
| tests/test_imu_setup_failure.cpp | 5670c777e63f4e12bc515770e4c5a680080b887bc51babf3cd6995b1afcf4971 |
| tests/native_imu_setup_failure/callback_cases.cc | a9b4131df075c93e4293be51efaaa599d34bea831233c8dac0be5b2dc83e1891 |
| tests/tooling/test_imu_setup_failure.py | 78f1de1dcb651ed7a49b28c52acaa689e424cdb04de4078791bbe2120f04b552 |

Scope and limitations in SUMMARY.md remain applicable. Root owns the full CMake
normal/sanitized reruns and final shared integration/evidence review.
