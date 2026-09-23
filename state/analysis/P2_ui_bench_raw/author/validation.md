# D112 independent author validation

2026-09-24 Asia/Dubai. PASS on first execution against the corrected worker source
freeze. No test amendment, fixture correction or production finding was needed.
No implementation body was read. This reuses the separate same-model author
context and adapted existing D110 test fixtures; it is not fresh repository or
cross-model review. Only the two new tests and authorized author artifacts were
written. No old/locked test, production, config, registry, shared ledger or hardware
was changed by this author task.

## Frozen identity

- Cases: `0bf8fd656423114d35be2fc4589d726751888e512698030222ad8f71709b2bd3`.
- Harness: `6fe512682214029421949f144f8adf2891e3b30531a2514a1c18de886cdae1b8`.
- Contract: `2adfd43546f2deba17ff852352d1c6b5c1c3f98bb32e7e75042bea0227bc00a2`.
- Runner CPP: `bc2def36d611f534112288dfca538ab36d51aff58d73c7e5e09eb1f0d9a7e70d`.
- Native CPP: `a9bd1c4d71cb167a94953194435857c88823ffd755db89d80ed9dccb6a2381d0`.
- Runner header: `881eceb27b8eb54654777529b50c8df49597a2303352f11f9b34695310e7094e`.
- Sketch: `be6dd812eac69d4d1df49a4bbc04378d799604a065ef27abdf22212b03a09139`.
- Actual decoder CPP linked opaquely: `cfda5ea3077b28325425e45bee0dc54fb95803ab826ee4e098348a359ed4a3e8`.

`freeze.json` and `frozen_*` retain the pre-execution originals, including the
literal saved-sample/sample_seen-before-A clarification. Final test hashes are
identical to that freeze. `opaque_source_copy_1790198483889430215.json` binds all
isolated source bytes; no source from the superseded first implementation freeze
was executed by these tests. No CPP-derived expected value was used.

## Results

Command: `python -m unittest tests.tooling.test_ui_bench -v`.
Exit0; 2 Python methods in123.118s. Thirty executable profiles, 65 isolated
compile/run commands plus the Windows-to-WSL wrapper command. All binary runtime
stderr was empty. Three deliberate forbidden-flag compiles refused as expected.

| Profile | Cases | Assertions | Result |
|---|---:|---:|---|
| Full normal and ASan/UBSan, each | 35 | 21,759 | PASS |
| Actual Native/default startup and10000 loops, normal and sanitizer, each | 2 | 27 | PASS |
| Capacity1 normal and sanitizer, each | 25 | 3,153 | PASS |
| Capacity0 normal and sanitizer, each | 3 | 60 | PASS |
| Four invalid wrapper config profiles, each | 3 | 60 | PASS |
| Two native-only config prerequisite profiles, each | 1 | 16 | PASS |
| Four configured windows, all16384 raw codes, normal and sanitizer, each | 1 | 278,704 | PASS |
| Overlapping windows, all16384 raw codes, normal and sanitizer, each | 1 | 278,656 | PASS |
| Six malformed decoder config profiles, each | 1 | 15 | PASS |
| Public missed-counter exact max/overflow, normal and sanitizer, each | 1 | 38 | PASS |
| Aggregate source age via early polls, normal and sanitizer, each | 1 | 24 | PASS |
| Conversion-period equality and decoder age minimum, each | 1 | 10 | PASS |

Native startup checks are present from the original executable freeze, with zero
initial clock/Reader counters, scoped constructor/port/destructor and guarded
heap assertions before any direct callback. Native profile selection explicitly
names those two binding cases, so similarly named fake-provider cases do not
inflate the reported native count.

Registry: historical before/after images prove exactly the approved UI_BENCH_SAMPLES
128 literal line was added and every other byte preserved. Current live registry
checks still use the unchanged original18 assertions. The approved profile, three
existing D096 wrong-value profiles, and the copied UI capacity129 profile produce
5x18=90 checks; each wrong value is rejected by the original value assertion.
This separates historical delta evidence from later additive live-registry changes.

## Evidence and limits

`run1.txt`, `run1_summary.json`, timestamped command/config/test/source receipts,
`registry_amendment_check_*.json` and `registry/registry_cases.jsonl` preserve the
complete run. `coverage.md` records the original oracle and limits. Actual
decode/evidence members, failed-read provenance, before-A visibility, C publication,
all128 immutable captures, natural wrap and reachable missed-count saturation
execute without private state seeding. First-sequence1 wrap within128 records and
other enormous counter paths are not claimed. Exact-once pure decoder invocation
requires structural source review in addition to output equality.

Counted Reader substitutions execute the actual new Native binding and sketch;
they do not establish native ADC register/ownership/cleanup behavior. Existing
native-driver/full-host regressions and route/target/ELF/startup/loader checks are
coordinator/reviewer-owned. Synthetic windows are not proposed electrical
thresholds. Physical START/BOTH distinction, settling/accuracy, clock/timing,
gesture/display composition, loaded RAM, whole-app WCET and human gates remain
outside this evidence.
