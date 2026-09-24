# D138 MATCH native compile, loader and layout validation

2026-09-24. **TARGET COMPILE PASS; PASS_CONDITIONAL_PRISTINE_MATCH_FIT_ONLY.**
Exactly one authorized MATCH/Immediate compilation passed with one compiler.
The checked D138 ELF has a 256440-byte compiler payload; ordered loader
accounting gives a 261280-byte peak in the 262144-byte pool, leaving an
864-byte chunk span and 860-byte largest possible payload. These are conditional
model values, not measured live RAM, loading or physical readiness.

## Source and exact build

The source implementation remains the first D138 production commit `d19f8964`;
source-manifest HEAD is `2ebec21f2a4ae84b8d7dcf396f7a6e9ca41830bc`.
`P7_readiness_raw/freeze_retry2.json` SHA256
`1958dfcba1253a653468fc04bbd8d7ed5005cf68fbf501133330e2e536acdaa9`
binds 683 host inputs. This native task bound all 103 freeze-listed `src/` inputs,
then mapped and rehashed all 102 staged files against those frozen/current bytes.
A separate Linux hash query verified all 102 remote staged files as well.

The host freeze omits the native build tools/assets. Their five exact current
hashes match the prior checked MATCH manifest and have no Git diff from HEAD:
`board_tool.py`, `app_build_policy.py`, `app_build_commands.json`,
`app_build_pins.json`, `p0_inert_sources.json`. See
`tooling_source_binding.json`. Two local manifest-preparation failures, before
any staging/compiler invocation, are preserved: an unnecessary tracked tools
README was outside the freeze, then its working bytes did not match the Git
blob. The final manifest uses the actual frozen inputs and separately binds the
native tool dependencies; neither failure caused a compiler retry or source edit.

The existing P5 checked runners were adapted only in this task's raw directory.
The command was `python -B state/analysis/P7_readiness_native_raw/compile_target.py`,
which invokes current `tools/board_tool.py flash app --match --compile-only` with
ADB serial `2629958581` and the existing dedicated remote root. Its narrow
wrapper injects `--jobs 1` and records actual remote argv. No configuration
or library overlay was used. The exact native settings were:

```text
arduino-cli compile --jobs 1 --json
--fqbn arduino:zephyr:unoq:wait_linux_boot=no
--build-property compiler.cpp.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1
--build-property compiler.c.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1
--build-property build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0
```

The actual command receipt includes the complete generated build/output/source
paths. The runner started at 18:55:17 UTC and ended at 18:59:14 UTC, exit 0.
There is exactly one actual compiler invocation; the separate expanded-property
query is distinguished in `actual_remote_commands.jsonl`. The coordinator was
notified at terminal completion before this task continued file analysis.

| Identity | Value |
|---|---|
| Staged source SHA256 | `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2` |
| Checked receipt | `04b266d5bf6740998eb692400fb6c77d` |
| Final ELF, 174972 bytes | `cb5fbb53ce4089ef682977a66fd5337491f150f17ca2cfdcd150a0dd6bca07d4` |
| Debug ELF | `85db9e563269d96b5dbb4281828fb0e46c37793df5b5b338d48bbe1a22e80991` |
| ZSK | `004d51bffd3b04803e55cadf44087b9e1faae884690a9f46ec56232def5c724f` |
| Packaged loader | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

Fresh Linux inventory and build preflight verified CLI1.5.1/core1.0.0 and all
18 pinned core/toolchain/loader files. Existing policy verified overrides,
expanded properties, zero external libraries and checked artifact hashes.
One final ELF was archived locally; no duplicate checkout or object tree was
copied. The checked debug/temp ELFs and ZSK remain on board Linux.

## Ordered loader model and prior MATCH comparison

The unchanged retained model
`state/reviews/P2_bridge_dependency_review_raw/elf_review.py`, SHA256
`1456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123`,
ran locally, exit 0. The separate ordered/source/import validation also returned
0. Every allocation fits its remaining contiguous tail; persistent-flash peeks
and section headers satisfy their required alignment at base `0x08100010`.
No copied region needs prepadding.

| Loader allocation order | Chunk bytes |
|---|---:|
| Initial bookkeeping | 88 |
| Extension object | 200 |
| Section map | 136 |
| Text | 86904 |
| Data | 216 |
| Rodata | 2136 |
| BSS | 167208 |
| Exported-symbol region | 16 |
| Init array | 8 |
| Temporary global-symbol table | 4352 |
| Export copy | 16 |
| **Peak / remaining span** | **261280 / 864** |

Compared with the prior ordinary MATCH ELF `eae32ea3`, copied text and compiler
payload grew by 688 bytes; four additional global function/object symbols grow
the temporary symbol-table allocation by 32 bytes. Modeled peak therefore grows
720 bytes, from 260560 to 261280; the conditional span falls from 1584 to 864.
Copied data, rodata and BSS payloads are unchanged. The compiler's nominal 5704
remaining bytes are not loader-free bytes. ELF file size grows by 1152 bytes.

Assumptions remain the pinned 32-bit non-Harvard loader, a pristine contiguous
pool, successful persistent peeks, and no additional/interleaved constructor
allocations. This does not measure live stack, fragmentation, native transport
growth, initialization completion or WCET. It does not qualify the default M0
profile or adopt either failed default-fit candidate.

## Actual target layout and imports

File-only GDB queries (`-nx -nh -batch`, no inferior/target) against freshly
hashed current and prior MATCH debug ELFs both returned 0. GDB hash remained
`8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778`.
All 16 queried existing sizes/alignments and all 72 queried legacy member offsets
are identical to prior MATCH. The raw `ptype /o` output and direct offset queries
are preserved alongside their command/hash receipts.

| Type | Target sizeof / alignof, bytes |
|---|---:|
| Buttons / Controller / Lifecycle | 12/4; 52/4; 136/8 |
| Escape / Robot | 208/8; 2640/8 |
| RobotInput / RobotResult | 192/8; 400/8 |
| Robot::Pending / Robot::Tick | 88/8; 180/4 |
| TransactionReport / Transaction | 504/8; 162544/8 |
| Runtime | 166304/8 |
| DisplaySample / Frame | 36/4; 104/1 |
| AttemptRecorder / FrameBuffer | 159200/8; 126300/4 |

`RobotResult::match_start_eligible` is at offset396; DisplaySample's
`start_status_available` and `start_ready` are at offsets33 and34. All three
occupy prior padding. Copied RobotResult/Transaction/Runtime sizes did not grow;
recorder capacities were not changed. The ELF's Runtime static object remains
166304 bytes, native sources848 and native dump-port object208.

All 62 imports actually used by current ELF relocations resolve to nonzero
exports in the freshly hashed packaged loader, exit0. The exact set and
addresses were reparsed by the local verifier. No historical default-profile
import set or current MCU image was substituted for this file-only check.

## Evidence, storage and limits

`P7_readiness_native_raw/validation_index.json` binds the compact raw evidence,
this report, frozen source reference and retained model/baseline dependencies.
The initial read-only report is preserved byte-for-byte as
`preparation_report.md`; `preparation_index.json` refers to that report's
historical path/hash, before this final report replaced it.

Key receipts include `compile.json`, `actual_remote_commands.jsonl`,
`app/receipt/verified.json`, `app/source_manifest.json`,
`remote_source_binding.json`, `app/loader_account.json`,
`app/ordered_account.json`, `abi_comparison.json`, `import_exports.json` and the
individual script-run records. Compilation, account, source hash, import,
ABI and final ordered-validation commands all returned0.

After evidence capture, this task removed only 233 disposable `.o/.d/.a` files
(7355110 bytes) under its unique native build path, exit0. All four checked
ELF/debug/temp/ZSK hashes were verified again afterward. Automatic approval
review rejected local stage deletion before process creation, giving only
“blocked by policy”; no retry was made. The 102-file,753087-byte local
`build/stage/app` copy remains and matches the staged manifest. Cleanup plan,
actual outcome and rejection are retained for the coordinator's storage ledger.
Earlier policy-denied cleanup paths and all older receipts remain untouched.

No upload, reset, MCU read/write, native I/O, matrix operation, Bridge/log dump,
run, configuration change, host test execution or phase approval occurred in
this native task. Current software tests and their oracle corrections remain
separate coordinator evidence. MATCH Immediate/native matrix startup conflict,
optical readiness/continuing blink, calibrated voltage, actual loading/RAM/stack/
WCET, deployment and physical/human acceptance remain unresolved by this compile.
