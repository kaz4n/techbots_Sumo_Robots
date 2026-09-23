# D080 independent setup and decoder test author

2026-09-23, Asia/Dubai. Objective: verify the frozen D080 public setup and
coherent-decoder contract against actual `src/hal/imu.cpp`, with a direct
concrete-Bus substitute. No implementation source or private implementation
files were inspected; production bytes were compiled/copied/hashed opaquely.
Inputs were AGENTS.md, D080 contract/header/config, D080 decision and the
manufacturer-layout source audit. No board action, commit or old locked-test
change was performed by this author.

## Owned changes

- `tests/test_imu_setup.cpp`: 26 contract-derived C++ cases.
- `tests/support/imu_bus_fake.h/.cpp`: fixed-capacity scripted concrete Bus
  method definitions, timestamps and call trace; no native Bus linked here.
- `tests/tooling/test_imu_setup.py`: ten methods, 44 separately compiled
  configuration variants plus two actual inert probe builds, UBSan enabled
  with no recovery; eight mocked upload-mode refusals before transport lookup.
- `tests/tooling/test_p0_config.py`: exact twelve D080 defaults added to the
  explicit allowed declaration union; strict declaration equality and every
  earlier assertion retained, plus one exact value/type check.
- This author directory: command/output/hash receipts and execution wrapper.

## Final evidence

| Check | Result | Receipt |
|---|---|---|
| Strict linked compile | PASS exit0 | `host_1790150859013443908.json` |
| Scoped actual-source C++ | PASS 26/26 cases, 1,562,374 assertions, exit0 | `host_1790150864957293979.json` |
| Configuration variants | PASS eight methods, 44 compiled/executed variants, 22.784s, exit0 | `host_1790150887829034991.json` and its `variant_*.json` command receipts |
| Inert probe and upload refusal | PASS two added methods, two compiled/executed probes, eight upload-mode refusals, 0.733s, exit0 | `host_1790150979918306818.json` and four compiler/executable receipts |
| Exact config declarations/defaults | PASS thirteen methods, exit0 | `host_1790150821402223326.json` |

The scoped C++ filter skips one unrelated scaffold case; it skips no D080 case.
Root owns the final complete host/sanitizer suites, native target compile,
broader tooling and fresh review. The initial variant run of seven methods and
40 variants also passed; final run adds the four progress-advance-cap variants.
After fresh-review feedback identified missing execution evidence behind the
new probe's startup-test comment, two required probe methods were added and
executed separately without repeating the 44 variants. Each actual new probe
is linked with primitive zero-initialized Bus counters (no fixture reset),
covering dynamic constructors before main, setup and 10,000 loops under host
MATCH0/MOTORS0 and MATCH1/MOTORS1. Retained entry equals exercise and no Bus
calls or Setup transitions occur. All transport/match/startup upload argument
combinations are refused before target, remote or require_transport entry.

Coverage includes all 48 ordered Bus calls and full-byte readbacks; each wait
at one microsecond before and exactly at its write-completion/start anchor;
one Bus call per advance; no prestart/terminal/repeated-start I/O; every Bus
nonOK status at every transfer stage; malformed count/completion/cleanup/flags;
all eight bit mismatches on every register readback; all 256 motion-status
bytes; caller/transfer reversal and half-range timestamps; unsigned wrap;
zero-duration and 599us success versus 600us failure; every stage at the exact
absolute deadline and final completion just before/at/after it; frozen and
progressing cap boundaries; invalid profile and setup-only config separation;
all 65,536 signed words in every sensor position; individual/all rail bits,
scaling, axis placement and fully zeroed decode failure payloads.

Production SHA-256 throughout these runs:
`f38f0f2116f77534a9c812acd925c574d009fff8c3a521dd6af3c255f49e8a37`.
Final C++ test SHA-256:
`8e477b0c9fd68b6552bd6fc95489203df5e234f001acac611c83ed38bbc8f6d0`.

## Retained first failure and repair

`host_1790150656398057349.json` retains the initial test-only compiler failure:
doctest REQUIRE is forbidden by the existing `DOCTEST_CONFIG_NO_EXCEPTIONS`.
Only this author's new test fixture changed to explicit CHECK plus abort for
fatal sequence guards. Shared CMake flags, earlier tests and assertions were
not weakened. The first actual production execution then passed 23 cases and
1,549,570 assertions (`host_1790150701632644769.json`). Three additional boundary
regressions produce the final 26-case result above. No production repair was
requested or needed by these independent tests.

## Limits and next action

This is host software evidence. It does not establish sensor identity, physical
settling/rate/freshness, electrical timing, yaw, full-loop WCET, motor-run
authorization, app integration or any human phase gate. Root should combine
these frozen artifacts with final complete-suite, target and separate-review
results; no further test-author implementation work remains.
