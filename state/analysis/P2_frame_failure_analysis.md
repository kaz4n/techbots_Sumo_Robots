# Offline frame-buffer validation failure record

2026-09-23 Asia/Dubai, D-069 first normal and ASan/UBSan builds.
Both CMake configure commands exit0; both build commands exit2 before test
execution. Raw commands/statuses/stdout/stderr: P2_frame_validation_raw/normal*
and sanitizer*. Production source was not implicated by these diagnostics.

Cause: new independently authored tests used REQUIRE while the existing project
compiles with DOCTEST_CONFIG_NO_EXCEPTIONS. Doctest rejects REQUIRE at compile
time under that policy. The new test file is not locked. Author repair attempt1
uses the existing CHECK plus explicit guard pattern, preserving the assertions,
expected values and safe pointer use. No existing test or exception/build policy
is changed. First failing artifacts stay intact; retry gets distinct filenames.

Repair attempt1 compiled successfully. Full normal and ASan/UBSan runs each pass
920 cases /17,033,806 assertions, zero failures/skips. No production fix needed.

The first complete tooling run executed317 tests in131.757s, with one failure:
its closed config declaration set had not yet added D-069's two explicit names.
This is a separate expectation-update issue, not the doctest compile failure.
The independent author added only LOG_FRAME_WINDOW_MS=200000 and derived uint64
LOG_FRAME_CAPACITY to the nonlocked allowlist/type/default checks. All76 B16
values and assertions remain unchanged; capacity/endpoints are tested in C++.
Fresh reviewer approved that exact diff and independently passed8 config checks.
Full tooling repair attempt1 uses separate tooling_retry1 receipts.
