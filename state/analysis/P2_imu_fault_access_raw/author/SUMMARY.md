# D097 independent test-author evidence

2026-09-23 Asia/Dubai. Contract commit cf3dfe18462e5e888e09aa376c7bdbd2732dc1bf.
Objective: verify passive setup-fault retrieval and the actual NativeSources callback.
Authored from the frozen contract, public headers and existing test fixtures.
No production CPP was opened; the runner copied and compiled it as opaque bytes.
Only the five new test files below and this author evidence directory were changed.
Shared CMake, source, config, existing tests, locked tests and state ledgers were untouched.

Command from repository root:

```powershell
wsl -d Ubuntu -- python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/tests/tooling/test_imu_setup_failure.py
```

Final result: both Python tests pass; four UBSan/Werror executable runs pass.
MATCH=MOTORS_ALLOWED=0 and MATCH=MOTORS_ALLOWED=1 each run:

- Actual Acquirer/Setup: 7 cases, 31468 assertions.
- Actual NativeSources callback/provider substitutes: 1 case, 178 assertions.

Coverage includes exact public Sample/CoherentMotion fields, start rejection,
advanceSetup transport and time-order failures, every one of 48 setup operations,
canonical absence before/pending/ready/runtime-only fault/NO_NEW/observation,
const repeated retrieval, preserved setup/progress state and source counters,
unchanged legacy reads, pending mixed-API cancellation, async completion/sequence.
The callback test checks all value fields with distinguishable sentinel data,
getter-only invocation, ignored callback time, and no other provider/clock call.
Sentinel contents test callback forwarding, not physical validity of that payload.

First-run failure retained: the new mixed-API fixture initially scripted the
cancelMotion reply, but the established legacy collision seam obtains cancellation
from acquireMotion itself. Existing tests/test_imu_resume.cpp:215-224 and native
resume_cases.cc:298-313 establish that boundary. The new fixture alone was corrected
to inject the cancellation on acquireMotion and expect one acquire/no explicit
cancel call. No behavior assertion, existing test or implementation was weakened.
Original failures: command_1790178636651217011.json and command_1790178638090304721.json.
Final passes: command_1790178685550162072.json, command_1790178686242436613.json,
command_1790178687920358560.json and command_1790178689204021713.json.
Each command JSON records exact argv, return code, complete staged-source/test
SHA-256 manifest and raw stdout/stderr names/hashes. Raw streams remain alongside.

Frozen test SHA-256:

| File | SHA-256 |
|---|---|
| tests/test_imu_setup_failure.cpp | a70a57e4720215e6b5563f9854d2a197c01142932a22f6b6c5f56b8e52f57952 |
| tests/native_imu_setup_failure/check_sample.h | 6485caeb913aa1c7bc3d834dd2156f4ce1b2e9db1040442a0ede389ed3ebd3c4 |
| tests/native_imu_setup_failure/Arduino.h | 2c29d09f45e94ba0ccb0e3ea1940b9022dde2e4f9b199fd9c14d560828a55891 |
| tests/native_imu_setup_failure/callback_cases.cc | 251ddea62a2837b602714d6479c253429c7c1d999b0fe3e9e2e88a994b43cc34 |
| tests/tooling/test_imu_setup_failure.py | 9ea6f4955e64f43219caa0a619c971dd6a6dde91454b909498a1648a2f5dee7d |

Limits: these are host substitutes, not MCU execution, target capacity, WCET,
physical sensor evidence, a motor-run grant or a phase gate. Getter allocation
absence needs implementation review; this suite does not install allocation hooks.
Actual Acquirer tests have no native clock provider; callback clock calls are counted.
No board lookup, upload or hardware access occurred. No contract ambiguity remains.
Next action belongs to root: full normal/sanitized suites, same-app target dependency
and memory comparison, independent source review, then shared evidence/handoff update.
