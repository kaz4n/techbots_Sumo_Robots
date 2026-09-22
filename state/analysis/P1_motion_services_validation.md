# Motion, encoding and countdown services validation - 2026-09-22

Recovered clean baseline 683665b at18:42 Asia/Dubai. P1 host-only under D-016;
no gate or hardware acceptance inferred. Contracts preceded implementation:
0caaadb,71d2545,5bfcf70. Implementations: motion40c8c9c, codec ae3e9e7,
Services3cee6ae. Twenty-seven new locked cases; existing locked files untouched.
All76 B16 defaults preserved; five D-024 service constants added explicitly.

Actual validation:
- Isolated WSL g++13.3 C++17 object builds, -Wall -Wextra -Wpedantic -Wconversion
  -Wsign-conversion -Werror -fno-exceptions -fno-rtti: exit0 for each changed module.
- Initial tools/test_host.sh exit2: CAPTURE was passed two arguments; author
  split diagnostic macros, changing no assertions. P1_motion_codec_tests.txt.
  Retry exit0: P1_motion_codec_tests_retry.txt. Direct binary155cases/5,810,598
  assertions pass (P1_motion_codec_cases.txt). Two10,000-sample property sets
  each explicitly exercise5,000 healthy and5,000 unavailable-IMU samples.
- After Services, tools/test_host.sh and direct build/host/sumox26_tests exit0:
  182/182 cases,5,872,365 assertions, no failures/skips. Raw files:
  P1_countdown_services_tests.txt and P1_countdown_services_cases.txt.
- cmake --build build/host-sanitize --parallel2 then its direct binary: same
  182cases/5,872,365 assertions pass, build/run exit0, ASan/UBSan no diagnostics.
  Existing flags -fsanitize=address,undefined -fno-omit-frame-pointer retained.
  P1_countdown_services_sanitizer.txt. CMake regenerated for new sources/tests.
- Windows python -m unittest discover -s tests/tooling -p test_p0_config.py -v:
  8/8, exit0; P1_service_config_tests.txt.
- WSL python3 -m unittest discover -s tests/tooling -v:48/48, exit0;
  P1_motion_services_tools.txt. All transport calls use controlled substitutes.

Separate read-only review PASS: reviews/P1_motion_services_codex.md. It caught
and verified repairs to the maximum-duration wrap defect, seeded path imbalance
and stale contract description. No open findings in that scope. Inert manifest
approval binds only its17-file exact snapshots; future source changes invalidate it.

No target compile, board contact, upload/reset, motor run, measured calibration,
trajectory or WCET. Motion still needs scripts/FSM/governor/MotorGate integration;
Services needs production raw samples/start/cancel/bias/GO-heading wiring. Codec
has no recorder cadence/ring/dump. D-025 ALL_IN policy is not its implementation.
D-026/27/28 and subsequent fusion work are outside this182-case snapshot.
