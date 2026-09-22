# Connected bare UNO Q results — 2026-09-22, Asia/Dubai

Scope: D-052 authorizes the human-reported bare UNO Q, USB serial2629958581.
No additional hardware was requested or connected by the agent. All uploaded
diagnostics use MATCH0/MOTORS_ALLOWED0. No motor-capable firmware or motor run.

## Completed and evidenced

| Check | Actual result | Evidence |
|---|---|---|
| USB/Linux/toolchain inventory | ADB reaches the exact device; CLI1.5.1/core1.0.0 on board | P0_connected_inventory_20260922.md; P0_board_inventory_20260922.json |
| Board-side staging/compile | Timing default and Immediate, matrix default: exit0 | P0_*target_compile*; P0_timing_immediate_compile_20260922.txt |
| Inert timing upload | Default image uploaded23:19:29+04, exit0 | P0_timing_upload_20260922.txt |
| Bare scheduler observation |60000 samples, max/p99 lateness3us, zero observations >=1000us late | P0_timing_capture_run2_20260922.json; P0_timing_run2_raw/ |
| Inert matrix upload | Default image uploaded23:34:33+04, exit0 | P0_matrix_upload_20260922.txt |
| Matrix software progress | Counter441->444, full image/mapping checks pass, exit0 | P0_matrix_capture_20260922.json; P0_matrix_run1_raw/ |
| Tooling validation |116/116 cases passed under WSL, exit0 | P0_tooling_final_20260922.txt |

The timing histogram has16561/16683/16603/10153 samples in bins0/1/2/3us.
The nearest-rank p99 observation is59400, inside bin3. Loader/sketch flash
identity and normalized-ELF/runtime BSS layout passed; both4016-byte snapshots
were identical with before/after sample counters60000. The separate reviewer
recomputed these results from raw bytes without importing the analyzer.

Timing run1 was a real failed verification, preserved with exit1. Exactly one
packaged-BIN alignment byte differed from the uploaded ELF.32f0403 repaired the
reference to compare all physical ELF PT_LOAD bytes, without ignoring any byte.
The offline saved dump then matched exactly; new run2 passed in104.316s.
First debug attachment occurred over248s after timing upload; direct completion
was read only after flash/list checks. These timestamps and remaining observation/
cache-coherency limits are explicit in ../reviews/P0_timing_measurement_codex.md.

## Current image and limits

Current MCU image is `bench/p0_matrix`, default/dynamic startup, source SHA256
72214f8aa1b6d84e21d2dc8a568ea01adb5fe0295f3f3d0f362e8696d2543e8f.
Counter441->444 was read with a3s requested wait; actual read-time bounds are
3.000219..3.078029s. All flash identities and post-counter list/node/BSS checks
passed in104.838s, within the120s budget. Matrix optical
appearance is not remotely observed. The RAM observation does not complete the
original Monitor print/log round trip; no R3/R4 exception was taken.
Independent raw-data reproduction: ../reviews/P0_matrix_measurement_codex.md;
all36 files, nine memory dumps and13 successful command records checked.

These results do not establish full Robot::step WCET, GPIO/QTR/ADC/I2C timings,
external wiring/pin-map acceptance, cold power-on startup time, motor waveforms,
sensor calibration, ring performance or a human phase gate. Immediate timing was
compiled only; Immediate matrix upload remains blocked by F-061. Missing rsync
is reported explicitly; ADB's per-file transfer works without it. SSH setup was
not changed. The user-supplied Windows CLI remains present and Git-ignored.

## Changes, reviews and resumption

- 93e3e41: eight core include-path repairs, with independent red/green staging tests.
- f6065b4: explicit serial-selected ADB fallback, preserving SSH/motor/compile-only guards.
- af02658: actual target builds, dependency provenance and first inert upload.
- 82d65f3/32f0403: bounded timing readout and exact ELF-reference repair.
- 341bd2e: raw measured timing evidence, independent analysis and matrix upload receipt.
- a287867: separate pinned matrix counter observer, nine independent tests and review.

All reviews here are separate reused read-only Codex contexts, not cross-model or
fresh complete phase-gate review. Established locked tests and config values were
not changed by the hardware recovery. No local commit was pushed.

Active work remains P1 under D-016 with P0 acceptance pending. No human gate has
passed. At the next software session, load the current handoff/state and complete
the full Escape contract/independent tests/implementation under D-047 through
D-051, then WAIT and Robot integration. Hardware-dependent acceptance stays open;
do not request additional hardware merely to continue these host tasks.
