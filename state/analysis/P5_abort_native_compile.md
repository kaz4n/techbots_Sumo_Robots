# D135 opener timing: exact native compile and ABI

2026-09-24, Asia/Dubai. **Compile/policy PASS; conditional loader fit PASS** for
the exact inert `bench/opener_timing` profile below. This does not establish
deployability, live RAM/stack, full-tick WCET, source/clock qualification,
physical P5.3 acceptance, extraction or a human gate. No upload, reset, MCU read,
target attachment, motor/peripheral operation, source grant or service change.

## Source and actual command

Production inputs match implementation commit `2d924f1f`; the clean 134-file
working-byte manifest was captured at later evidence HEAD
`8234afd75da27a58ade980999c0c0ac78f46f5de`. `git diff 2d924f1f HEAD -- src tools
bench/opener_timing` was empty at capture. No full source snapshot was duplicated.
See [`working_source_manifest.json`](P5_abort_native_raw/working_source_manifest.json).
The existing staging pipeline created immutable remote source
`97f8bec1352266162df11f8719590e84e2826fd32897f1994f516f4c9c9ea46b` before
later work was permitted to change production inputs.

```text
python -B state/analysis/P5_abort_native_raw/compile_target.py
```

This invokes current unchanged `tools/board_tool.py flash bench/opener_timing
--compile-only`, preserving `app_build_policy.py` checks. The scoped adapter
inserts only `--jobs 1` into remote CLI compile/property commands and records
every actual remote argv/status. Board ADB `2629958581`, CLI1.5.1/core1.0.0,
FQBN `arduino:zephyr:unoq`, default startup, exact compiler flags:

```text
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1
```

Exactly one native compiler invocation completed, with no retry. Receipt
`afc5f0cc638745bf8cb44f85682e2422`, staged hashes, compiler stdout/stderr and
checked artifact identities are retained under
[`P5_abort_native_raw`](P5_abort_native_raw).

## ELF and loader accounting

| Quantity | Exact opener timing result |
|---|---:|
| Final ELF/program bytes | 172,752 |
| Compiler dynamic payload | 256,044 |
| Nominal compiler remaining bytes | 6,100 |
| Retained model peak in 262,144-byte pool | 260,816 |
| Conditional pristine free span | **1,328** |
| Conditional largest payload | 1,324 |
| Copied `.text` | 86,592 |
| Copied `.rodata` | 2,124 |
| `.bss` / `.data` | 167,316 / 0 |

Final ELF SHA256:
`9583f94d7f7595639ef84a39822e19ed7c2110e1d2e65770b10f4986319e1a41`.
The unchanged retained model SHA256 is
`1456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123`.
All 61 undefined symbols actually referenced by relocations have nonzero
exports in the hash-checked packaged loader ELF. This is file-based resolution,
not execution or proof of flashed-loader identity. Opener dispatch and P5 trace
functions are present. Details:
[`loader_account.json`](P5_abort_native_raw/opener_timing/loader_account.json),
[`import_exports.json`](P5_abort_native_raw/import_exports.json).

The D134 default-app **32-byte deficit remains an independent open result**.
This wrapper omits the default app's `UnoQDumpPort` FIFO8 native transport owner
and uses the default empty DumpPort constructor argument. The ELF consequently
omits those native transport methods and its 208-byte `.data` object. Relative
to that different profile, `.text` is 1,112 bytes smaller and `.bss` 44 bytes
larger, giving 1,276 fewer compiler payload bytes and a 1,360-byte lower modeled
peak. This is not a source repair or proof that the current full app fits.
The recorder remains present; live native dumping is not supplied by this
profile. See [`profile_comparison.json`](P5_abort_native_raw/profile_comparison.json).

## Measured target ABI and padding

Offline GDB read only the two hash-checked compiled debug ELFs, using `-nx -nh
-batch`, `sizeof`, `alignof` and `ptype /o`. It created no inferior, target
connection or MCU operation. Both queries exited zero. Debug ELF/tool hashes
and full layout evidence are retained in `D135_opener/` and `D134_default/`;
the debug ELF was not copied to the host. Compact data:
[`abi_sizes.json`](P5_abort_native_raw/abi_sizes.json).

| Type | D134 default bytes | D135 opener bytes | Delta |
|---|---:|---:|---:|
| `app::Runtime` | 166,376 | 166,424 | +48 |
| `app::Transaction` | 162,544 | 162,584 | +40 |
| `app::TransactionReport` | 504 | 504 | 0 |
| `fsm::Robot` | 2,640 | 2,680 | +40 |
| `fsm::RobotInput` | 192 | 200 | +8 |
| `fsm::RobotResult` | 400 | 400 | 0 |
| `fsm::Robot::Pending` | 88 | 88 | 0 |
| `fsm::Robot::Tick` | 180 | 200 | +20 |
| `openers::Wait` | 216 | 224 | +8 |
| `recorder::AttemptRecorder` | 159,200 | 159,200 | 0 |
| `recorder::FrameBuffer` | 126,300 | 126,300 | 0 |

`OpponentReadWindow` is 12 bytes/alignment4; it starts at RobotInput offset188,
so four former trailing padding bytes absorb part of its size and net growth
is8. `AbortEvidence` is4 bytes/alignment1. Direct Result, FlankResult and WaitResult
grow from16/20/24 to20/24/28. Direct and Flank objects remain40/152 bytes; Wait
grows8 because it retains an enlarged current result and alignment.

The Pending handover tag is at offset85, consuming former padding: size remains88
with2 trailing padding bytes. Tick has cue at180, token at184, route/epoch flags
at192/193,6 trailing padding bytes; alignment rises4 to8. The Robot's one-byte
trace phase at offset0 precedes a7-byte alignment hole. RobotResult retains4
trailing padding bytes; TransactionReport retains7. These are actual DWARF
layouts, not host ABI assumptions or permission to repack live state.

## Copied instances and stack boundary

The measured persistent hierarchy contains exactly one Transaction in Runtime
at offset152. It contains one Robot at relative offset136 and one
TransactionReport at relative offset162016. Two persistent 400-byte RobotResult
copies coexist: `Runtime.transaction_.robot_.result_` at Runtime offset2056,
and `Runtime.transaction_.report_.robot` at Runtime offset162192. Runtime's
single persistent200-byte `decision_input_` is at offset165304. These instances
are already included in Runtime166424, not additional allocations. Transaction
and Runtime copy construction/assignment are deleted; there is no by-value
Transaction copy in the normal path.

The source also requires by-value input/result operations: Runtime project and
projectThunk return RobotInput; Transaction::decideFrom holds its projected
input, applyDecision takes a200-byte input by value, and Robot::step makes its
200-byte resolved input. The alternate public decide path also takes input by
value. Robot::step returns a400-byte result to TransactionReport and its duplicate
branch creates a400-byte local result; exhaust also returns by value. Compiler
elision/storage reuse means these source operations cannot be summed into a
measured stack maximum. Runtime postDecision/completeEpoch use references to
the existing report rather than additional full result/report snapshots.

No new stack allowance, stack high-water measurement, call-chain peak,
constructor allocation bound, live loader/free-memory result or full800us WCET
was established. The pristine loader free span is not spare stack or total
MCU RAM. Those qualification limits remain despite this profile's modeled fit.

## Retention and next action

Retain one checked final ELF, compact receipts/source manifests, the two offline
ABI transcripts and import/model results for independent review. Existing stage
and generated build receipt remain for that review; no second full source tree
or copied debug ELF was created. No cleanup operation was attempted, and neither
previously policy-denied cleanup batch was retried. Configuration, capacities,
behavior, production tooling and ledgers were not edited by this task.

Next action: independent review and completion of source-bound host validation;
actual deployment/stack/timing/extraction and physical P5.3 trials need their
separate prerequisites. This native result creates no upload or motor-run grant.
