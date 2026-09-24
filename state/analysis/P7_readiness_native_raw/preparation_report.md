# D138 MATCH native qualification: preparation only

2026-09-24, approximately 22:51 Asia/Dubai. **READ-ONLY PREPARATION COMPLETE;
COMPILATION NOT AUTHORIZED OR RUN.** The coordinator requires the frozen host
tests and a validated source commit before the native compilation. The initial
host attempt stopped at a new test fixture compiler warning before production
execution; its independent correction and validation belong to the coordinator.

## Fresh inventory

`python -B state/analysis/P7_readiness_native_raw/inventory.py` returned 0.
All 11 captured commands returned 0. Exact argv/stdout/stderr are retained in
`P7_readiness_native_raw/inventory.json`.

- ADB serial `2629958581` is reachable, Linux user `arduino`; no password used.
- CLI `1.5.1` / commit `01f3d4f2b`; installed `arduino:zephyr` core `1.0.0`.
- All 18 installed toolchain/core/loader files from the prior checked MATCH
  receipt retain their recorded hashes. Packaged loader remains
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
- GDB remains `8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778`.
- No `arduino-cli`, gcc/g++, cc1 or collect2 compiler process was listed.
- Board `/home/arduino` free: 14,167,465,984 bytes; available memory:
  3,298,050,048 bytes. `/tmp` and `/dev/shm` each had 1,924,096,000 bytes free.
- Existing dedicated build root uses 2,017,700 KiB. Prior checked MATCH debug
  ELF remains present for an eventual same-profile layout comparison.
- Local C: free was 733,069,312 bytes. Keep receipts and one checked final ELF
  compact; do not duplicate the source tree or copy native object directories.

No source staging, compilation, upload, reset, MCU/runtime access, matrix action,
Bridge action, log dump or deletion occurred. Inventory reads Linux files only.

## Proposed checked command after authorization

Use the established prior scripts in `P5_match_native_raw/compile_target.py` and
`invoke_checked.py`, adapting copies only into this task's new raw directory.
The exact board-tool argv remains:

```text
tools/board_tool.py flash app --match --compile-only
```

The task-local wrapper must intercept each `arduino-cli compile` remote argv and
insert exactly `--jobs 1`, as the prior successful wrapper did. Run the prepared
new wrapper through `python -B state/analysis/P7_readiness_native_raw/compile_target.py`.
These task-local compile scripts have not been created or executed at this
preparation checkpoint. Do not invoke the historical scripts: their outputs are
already evidence, and their paths must not be reused.

Environment is the established verified fallback:

```text
SUMO_TRANSPORT=adb
SUMO_ADB_SERIAL=2629958581
SUMO_ADB_EXECUTABLE=C:\Users\narut\AppData\Local\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe
SUMO_REMOTE_ROOT=/home/arduino/sumox26_codex_build
PYTHONDONTWRITEBYTECODE=1
```

Current tooling selects `arduino:zephyr:unoq:wait_linux_boot=no` and exact C/C++
flags `-DMATCH=1 -DMOTORS_ALLOWED=1`, with
`build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0`.
It generates content-addressed remote source paths and a unique UUID build and
receipt directory. Existing policy checks the CLI, installed pins, overrides,
expanded properties, dependency set and artifacts. No configuration overlay,
grant, capacity, startup, library, toolchain or production-tooling change is
part of this plan. One actual native compilation only, pending authorization.

## Source, artifact, loader and layout evidence plan

Before staging, bind the coordinator's final validated commit and current frozen
manifest (current starting reference: `P7_readiness_raw/freeze.json`, SHA prefix
`276d4e12`, 678 inputs; its final successor is to be supplied after test repair).
Retain a compact byte manifest for every native source and tooling dependency.
Recheck these bytes before invocation. Capture the generated staged-file manifest,
reconstruct its ordered source hash, and prove every staged file maps to those
bound original bytes. Notify the coordinator once the remote source snapshot is
complete. A later source change invalidates this qualification until re-bound;
the older P5 source hash is not D138 evidence.

Preserve actual remote argv, timestamps, return codes, all policy receipts and
first-failure output. Require explicit nonzero propagation. Archive one checked
final app ELF and verify its hash against the new receipt; record the policy's
debug/temp ELF and ZSK hashes without copying disposable compiler products.

Run the retained ordered loader model
`state/reviews/P2_bridge_dependency_review_raw/elf_review.py` against that exact
ELF, checking each allocation and peek alignment. Report payload, ordered peak,
remaining span or deficit and assumptions. Compare against the prior same-profile
MATCH account (260560-byte peak, 1584-byte conditional span), including actual
section sizes and Runtime static-object size. A compiler success or nominal
remainder is not loader fit or measured live RAM.

With the new debug ELF and GDB hashes verified first, use file-only
`arm-zephyr-eabi-gdb -nx -nh -batch <checked-debug-ELF>` and `sizeof`, `alignof`,
`ptype /o` queries. Compare current and prior MATCH layouts for actual Buttons,
Controller, Lifecycle, RobotInput, RobotResult, Robot, Robot::Pending,
Robot::Tick, TransactionReport, Transaction, Runtime, DisplaySample and Frame;
include recorder owner/buffer sizes and unchanged old member offsets. This
checks the appended metadata and copied-result growth using target DWARF,
not host ABI assumptions. No inferior or target connection is needed.

Finally compare this ELF's relocation-used imports against current, freshly
hashed packaged-loader exports using the established file-only GDB query path.
Retain a compact validation index. Release only verified task-owned disposable
scratch after required evidence is copied; coordinate any storage-ledger entry.
Do not retry the older policy-denied cleanup batches or delete old receipts.

## Limits and next action

This is readiness to attempt a compile-only qualification, not a new artifact
result. Wait for the coordinator's host validation and exact compile authorization.
No upload or motor-capable run is authorized. Prior default-fit candidates remain
unadopted; this legitimate MATCH feature check neither retries them nor proves
default-profile fit. MATCH Immediate/native matrix startup, physical display,
calibrated voltage, live RAM/stack/WCET, deployment and human phase gates remain
separate qualifications.
