# D134 source-bound native compilation

2026-09-24, Asia/Dubai. Compile-only Linux work on the freshly inventoried bare
UNO Q (ADB serial `2629958581`). No upload, reset, MCU read, motor run, source
grant, peripheral operation or service change was performed. This is neither
physical acceptance nor a phase gate.

## Source and invocation

An immutable copy of `src`, `tools`, and `bench/reactive_timing` was captured
before D135 integration at Git HEAD `bf36abfb49f9577e8a0841eecde7562b8a41bdce`.
Its 134-file, 1,165,312-byte manifest is
[`source_snapshot_manifest.json`](P5_native_compile_raw/source_snapshot_manifest.json).
All 123 entries overlapping the completed D134 host freeze match exactly;
the remaining 11 are shell scripts, README files and `.gitkeep` placeholders.
See [`host_freeze_comparison.json`](P5_native_compile_raw/host_freeze_comparison.json).
Consequently these results do not include subsequent D135 changes.

The copied `tools/board_tool.py` and `tools/app_build_policy.py` are unchanged.
The scoped invocation adapter inserts only `--jobs 1` in board-side
`arduino-cli compile` commands. Actual remote commands and return codes are
retained in each `*_actual_remote_commands.jsonl`; the unchanged tool's receipt
commands omit this adapter argument. All original installed dependency/hash,
source admission, FQBN, profile and artifact checks remain active.

```text
python -B state/analysis/P5_native_compile_raw/compile_target.py app
python -B state/analysis/P5_native_compile_raw/compile_target.py reactive_timing
python -B state/analysis/P5_native_compile_raw/account_target.py app
python -B state/analysis/P5_native_compile_raw/account_target.py reactive_timing
```

The first two invoke the copied equivalent of `python tools/board_tool.py flash
app --compile-only` and `python tools/board_tool.py flash bench/reactive_timing
--compile-only`, respectively. Native compiles run serially with one compiler
job, default startup, `MATCH=0`, `MOTORS_ALLOWED=0`, and exact installed CLI
1.5.1 / core 1.0.0. The timing profile additionally uses existing
`SUMOX_P4_REACTIVE=1 SUMOX_TIMING_EVIDENCE=1`. No synthetic config overlay.

## Results

The app compiler, build policy and final ELF collection all returned zero.
Its checked receipt is `688cc7cf8a714bc5afe2411a975aa5fa`, staged source
`c598cad1b740b6dabc67a5dce63448e9b4b4cd5d080b8370a163da6a0b61e564`.
The compiler reports 176,116 program bytes and 257,320 dynamic payload bytes,
with 4,824 nominal bytes remaining. This excludes loader allocation overhead.

The retained loader model reports **conditional pristine-pool fit FAIL**:
262,176 peak bytes in the 262,144-byte pool, a **32-byte deficit**. Model
identity `1456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123`
is unchanged from `state/reviews/P2_bridge_dependency_review_raw/elf_review.py`.
The negative reported free-span/largest-payload values represent the deficit,
not an actual allocator observation. No repair was made to obtain a passing fit.

Reactive timing compiler, policy and checked ELF collection also returned zero.
Receipt `d2bc65c7e4bb46409a6fcd522acdb58f` binds staged source
`39605f3444b3510915ee1a847390a0aaf7ff05bba795e8d17143aed2edc7b6c8`,
final ELF `dbc68caa21b8a1f4d8bc641377abec9b86512acdde004dba685d24308cb8c1ce`.
It uses 166,444 program bytes and 252,548 dynamic payload bytes, with 9,596
nominal compiler bytes remaining. Its **conditional pristine-pool fit passes**:
257,128 modeled peak bytes, **5,016 free-span bytes** / 5,012 largest payload.
Runtime is 166,496 bytes. Actual reactive `routeNormal`/`checkStall` and timing
trace symbols are present; opener dispatch symbols are absent, and the strong
`__loopHook` is present. Full account and symbols:
[`reactive_timing/loader_account.json`](P5_native_compile_raw/reactive_timing/loader_account.json).
Both native compiler processes finished; no third build was run.

## Exact comparison with D128 default app

| Item | D128 | Current D134 snapshot | Result |
|---|---|---|---|
| Final ELF SHA-256 prefix | `21b28ee366e77701` | `9cbde4dfb4b7b26e` | Different |
| ZSK SHA-256 prefix | `838487f5a5544a5c` | `b91c1aec39bfbc05` | Different |
| Packaged loader ELF SHA-256 prefix | `39d4a4fd47241663` | `39d4a4fd47241663` | Identical |
| Final ELF bytes | 176,040 | 176,116 | +76 |
| Copied `.text` payload bytes | 87,656 | 87,704 | +48 |
| Conditional peak bytes | 262,128 | 262,176 | +48 |
| Conditional free span bytes | 16 | -32 | -48 |

Other copied region accounting and global-symbol count are unchanged;
the actual app Runtime symbol remains 166,376 bytes. Nine function names have
changed raw function bytes/presence since D128, recorded in the full account.
These are cumulative source changes; this comparison alone does not assign
the growth to one intervening decision. Full hashes, checked dependency hashes,
region details and commands are in
[`app/receipt/verified.json`](P5_native_compile_raw/app/receipt/verified.json) and
[`app/loader_account.json`](P5_native_compile_raw/app/loader_account.json).

Offline symbol-size comparison accounts for the entire 48-byte text increase:

| Function | D128 bytes | D134 bytes | Increase |
|---|---|---|---|
| `Robot::startOpener()` | 112 | 124 | 12 |
| `Robot::step(const RobotInput&)` | 356 | 360 | 4 |
| `Robot::runEscape(...)` | 228 | 240 | 12 |
| `Escape::step(const EscapeSample&)` | 464 | 476 | 12 |
| `Escape::result(bool)` | 164 | 172 | 8 |

`Robot::checkStall` changes its signature but remains 436 bytes. The five
increases sum to exactly 48; there is no unexplained section-size remainder.
See [`D128_function_sizes.json`](P5_native_compile_raw/app/D128_function_sizes.json)
and the retained source diff. Source comparison identifies D134's required
availability guard in `startOpener`, and D131's added sample field/helper
arguments/episode representation in the other four functions. This maps source
changes to emitted function sizes without claiming individual instructions.

Smallest suggested repair scope: a separately reviewed **zero-window compile-time
specialization** of the D131 edge integration, preserving its previous boolean
active-state representation and avoiding unused widened helper/sample work when
`EDGE_PUSH_THROUGH_MS == 0`. Keep positive-window semantics and the D134
availability guard unchanged. The four D131-associated functions account for
36 bytes, so recovering their old sizes would leave only 4 conditional bytes
after the retained 12-byte guard. Recovery is a proposal, not a measured result
or adequate runtime margin; exact emitted code and both zero/positive behavior
would require independent validation. No config, capacity, source change or
additional compilation was performed for this recommendation.

## Evidence limits and retention

One checked final ELF is retained for each successful profile, together with
raw compiler status/output, policy receipts, staged source hashes, actual remote
commands and loader accounts. Compiler success is distinct from modeled fit;
modeled fit is distinct from actual loading, live free RAM, stack and full
800-us WCET. Historical D128 reactive free-span 6,512 bytes is not a measurement
of the current timing profile. A packaged loader hash does not identify flashed
loader bytes. No physical or human gate follows.

The immutable source snapshot remains needed to review the D134 build separately
from concurrent D135 changes. A cleanup preflight verified 243 local duplicate
staging/receipt files totaling 1,696,900 logical bytes under the exact owned
`source_snapshot/build` directory. All receipts had byte-identical retained
copies; staged source hashes matched the retained manifests and are reproducible
from the retained snapshot. Automatic policy rejected the explicit PowerShell
deletion (`blocked by policy`); no files were deleted and no retry was attempted.
The copies remain. See [`cleanup.json`](P5_native_compile_raw/cleanup.json);
the coordinator must append this meaningful blocked batch to STORAGE_LOG.md.
The unrelated historically denied 85MB cleanup was not retried. Checked target
artifacts and remote build directories remain retained.

The final [`evidence_index.json`](P5_native_compile_raw/evidence_index.json)
binds the retained native evidence files, including the original snapshot,
checked target artifacts and blocked duplicate copies. No source, config,
production tooling, tests or state ledgers were edited by this native-build task.
