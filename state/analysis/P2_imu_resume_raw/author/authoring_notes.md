# D094 independent author receipts

Production CPP was copied/compiled/hashed as opaque bytes and never opened by
the test author. Contract/header/specification expectations are the test oracle.
Existing test sources and fixtures were not edited.

Initial test-author corrections retained in this record:

- Pure tests initially used doctest REQUIRE under the project's
  DOCTEST_CONFIG_NO_EXCEPTIONS setting, plus by-value range loops diagnosed by
  -Werror. Replaced only those new harness constructs with `must(CHECK+abort)`
  and const references; assertions and production code were unchanged. The
  implementation worker retained that early compiler output separately.
- Initial native run:18 cases,17 passed,1 failed. Frozen-clock shared-budget test
  expected `start_count==3`; fixture command admission had already acknowledged
  that third START, so changing only `start_after=-1` permitted the fourth START.
  Corrected the test stimulus to wait for fourth START and disable byte progress,
  retaining the same8192 total-poll, cross-transaction, frozen-time and one-cleanup
  expectations. Original failing command JSON is preserved in this directory.
- A new author test originally used
  `p.state=static_cast<AsyncState>(77U); p.started=true; p.completed=false;`
  with native NACK and expected TRANSPORT. Other new tests used an unknown state
  with default NOT_INITIALIZED and expected RESPONSE plus cancellation. Root
  explicitly clarified that only known COMPLETE/FAULT states certify terminal
  envelopes; unknown/IDLE states require RESPONSE plus cancellation regardless
  of status. Corrected the terminal-precedence stimulus to known FAULT while
  retaining malformed pulses/time. Added a separate unknown/IDLE plus NACK case
  requiring RESPONSE and cancellation. This fixes conflicting new test
  interpretations; no established test or acceptance criterion was weakened.
- Strengthened the pure wrap test so runtime begin is0xfffffff0 rather than
  wrapping during setup only. The source completion itself now crosses uint32.

First auxiliary checks passed:44 established native cases/932 parent assertions,
actual inert probe1case/13assertions in each motor macro mode, and all8 mocked
upload-refusal combinations. Process-isolated native summaries count parent
assertions; child assertions are enforced by the existing isolation listener.

JSON files retain exact staged/test hashes, subprocess arguments, status and
complete text-mode stdout/stderr. They are not overwritten by reruns. Newline
normalization from subprocess text=True is explicitly recorded in each receipt.

Final independent tests frozen after the explicit state-precedence clarification:

- `tests/test_imu_resume.cpp`:22cases/17259assertions PASS in each
  MOTORS_ALLOWED=0 and1 build, actual Setup/Acquirer/Estimator/Robot under UBSan.
- `tests/native_imu_bus/resume_cases.cc`:21cases/728 parent assertions PASS,
  including26 pause positions,4 hardware errors at each pause, normal progress
  flags excluded from cancellation diagnostics, unexpected protocol bits retained,
  lost-owner cleanup suppression and event disappearance before mutation.
-44 established native cases/932 parent assertions PASS with async source linked.
- Actual retained probe:1case/13assertions per mode,10000 inert loops. Final
  rerun against root's state-precedence correction is recorded after the initial
  two probe results, to retain exact current source evidence.
- All8 mocked upload combinations refuse before target/transport lookup.

These checks exercise software interfaces and host models only. They do not
measure sensor rate, electrical stretching, axes, real QTR service, native step
time, complete800us, or physical/human acceptance. No board command or commit was
performed by this author. Root owns full normal/sanitizer/target/review closure.
