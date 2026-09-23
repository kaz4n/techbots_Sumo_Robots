# D111 independent author validation

2026-09-24 Asia/Dubai. PASS on the worker's unchanged first source freeze. No
implementation body was read. This is a reused separate author context using the
same model, not fresh repository or cross-model review. No production, old/locked
test, config, registry, shared ledger, board or build directory was edited here.

## Frozen inputs and history

- Original cases: `a9e9fce1b293a43c7b8631447da67cfa43c6b67c70fe877f058beb4cbc2f8e11`.
- Final cases: `ffc0a59640a5f82cb27fc09aff231aafc4c4fda46eca6f425019c6e3bcee1fed`.
- Unchanged harness: `bcc2b6da626d20e61603b9b91550ff4371f584f0bffce7679639b09d8be1407b`.
- Runner CPP: `6d3c6c5f5234d995689cc265c65de7848e2bc2dd6b8fa0748e6b2f1cec8ce61f`.
- Native CPP: `740054b0b81f75a6323c0c3a30a5e25f08908188788f1fbf1d482f2d1ae54a47`.
- Public/private Runner header: `bd63d529aa87ae907b00a6bcb62d502450ac577edd8e4651357ee9fea498d12a`.
- Sketch: `35829619175c459cda56e9bc1a6ffa6d6451d1d0c88b0ce77cdf28349aada80b`.

`freeze.json` and `frozen_*` retain the original pre-execution tests/contract.
`opaque_source_copy_1790197410355970436.json` binds all copied production inputs.
The original complete run passed on first execution, with no fixture correction
or production finding. Its commands/stdout/stderr are retained unchanged.

After that PASS, author self-review identified missing explicit initial-zero
Native startup counters. Root and separate reviewer approved one additive case
before the direct Native callback case. `startup_amendment.json` and `.diff`
prove removing only that insertion restores every original test byte. No existing
assertion or stimulus changed. `startup_amended_frozen_cases.cc` records the new
freeze before its execution; only affected Native selections were rerun. The
addition is inside TEST_NATIVE_BINDING and does not change the main/config paths.
`startup_source_identity.json` verifies original production hashes stayed identical.

## Executed results

Command: `python -m unittest tests.tooling.test_imu_heading_bench -v`.
Original run: exit0, 2 Python methods, 129.675s, 28 executable profiles and 61
isolated compile/run commands, plus the Windows-to-WSL wrapper command. All runtime
stderr was empty. Three deliberate flag-refusal compiles failed as expected.

| Profile | Cases | Assertions | Result |
|---|---:|---:|---|
| Full normal and ASan/UBSan, each | 31 | 1,342,660 | PASS |
| Original actual Native/default sketch, normal and sanitizer, each | 2 | 25 | PASS |
| 15 invalid config profiles, each under sanitizer | 3 | 170 | PASS |
| Actual Estimator invalid configuration | 3 | 158 | PASS |
| Short public calibration profile, normal and sanitizer, each | 1 | 87 | PASS |
| Five-poll limit, normal and sanitizer, each | 1 | 37 | PASS |
| Short valid trial, normal and sanitizer, each | 3 | 72,228 | PASS |
| Deadline minimum+1 and TICK/gap equality, each | 1 | 31 | PASS |
| Amended Native startup/default sketch, normal and sanitizer, each | 3 | 38 | PASS |

Targeted amendment command:
`wsl.exe --exec python3 state/analysis/P2_imu_heading_bench_raw/author/run_startup.py`.
It executes six additional isolated commands, all exit0, with unchanged production
inputs and no runtime stderr. The test verifies zero clock/Acquirer calls from
actual default globals, scoped Native construction/port/destruction and guarded
heap use, then the unchanged direct forwarding and setup/10000-loop cases.

Registry verification: exact five literal additions, all other bytes identical
to the preserved root before-image. One approved profile and five independently
wrong copied values run the unchanged nested 18 legacy assertions: 108 checks.
Each wrong value fails its original value assertion; no registry assertion was
changed. See `registry_delta_*.json` and `registry/registry_cases.jsonl`.

## Evidence and limits

`run1.txt`, `run1_summary.json`, `startup_run.txt`, `startup_summary.json` and all
timestamped command/config/source receipts retain complete results. `coverage.md`
records the frozen oracle and explicitly unexecuted saturation/sequence-wrap/
numeric-overflow/second-checkpoint-boundary defenses. Typical counters, natural
clock wrap, real default 60s software spans and 61 immutable checkpoints execute.
Actual Estimator/Services are linked; Acquirer is a counted public owner substitute
only for the binding profile. Existing native-driver and full-host regressions,
target/ELF/startup policy and physical acceptance remain separately owned. This
does not establish sensor generations, real mounting/stillness, calibrated clock,
drift/rotation accuracy, loaded RAM, whole-app WCET or a human phase gate.
