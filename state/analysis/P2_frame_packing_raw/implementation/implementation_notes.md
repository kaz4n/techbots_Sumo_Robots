# D102 bounded storage and caller migration

Implemented against frozen public interfaces at `f6f65fc` and the full
`P2_frame_packing_contract.md` / `P2_frame_memory_options.md`. Local date checked:
2026-09-23 Asia/Dubai, still the PLAN P0/P1 schedule day; the current P2 software
exception does not supply a human gate or physical acceptance.

## Modified implementation files

- `src/hal/recorder_frames.h`: private storage only. The public header prefix is
  identical to `f6f65fc`. Payloads are separate from initialized two-bit lanes.
- `src/hal/recorder_frames.cpp`: validates status before stored mutation, copies
  the full incoming payload before destination writes, updates only its lane,
  and preserves the existing ring/counter/saturation order. `read` checks bounds
  before arithmetic and copies into caller storage; `bytesAt` returns the real
  retained payload. Reset remains a metadata-only clear with no array sweep.
- `src/hal/recorder_dump.cpp`: only FRAME_ROW copies a StoredFrame before calling
  the existing formatter, retaining the same read-failure formatting outcome.
- `bench/recorder_inert/src/recorder_bench.cpp`: only checksum frame lookup changes;
  it still feeds 25 raw bytes, then the original reconstructed one-byte status.
- `bench/p2_recorder_memory/src/memory_probe.cpp`: writes the owned View frame via
  read and sets frame_present to its result. A false result reports absence;
  it leaves the existing owned frame value untouched and never leaves a local
  pointer. Event pointer, summary, anchors and Abi reporting are unchanged.

No hidden persistent scratch/cache, heap, new tunable, rate, capacity, schema,
codec, app behavior, wiring or concurrency assumption was introduced.

## Fixture migration and assertion preservation

Only these eight existing current files were migrated:

| File | Original assertion expressions preserved | Added assertions |
|---|---:|---:|
| tests/test_recorder_frames.cpp | 188 | 0 |
| tests/test_attempt_recorder.cpp | 458 | 0 |
| tests/test_recorder_csv.cpp | 106 | 3 |
| tests/test_recorder_rate.cpp | 53 | 0 |
| tests/test_tick_timing.cpp | 97 | 1 |
| tests/fixtures/app_dump/roundtrip.cc | no doctest macros | 0 |
| tests/tooling/recorder_bench_cases.cc | 119 | 1 |
| tests/tooling/test_recorder_memory.py | all Python/harness predicates unchanged | 0 |

`assertion_preservation.json` compares every old CHECK/CHECK_FALSE/REQUIRE
expression against current expressions after the narrow API mapping written in
`validate.py`; no old expression is absent. Counts are source expressions, not
the much larger runtime assertion counts. This mechanical check supports, but
does not replace, the independent review of scenario meaning.

The four named retained-alias cases and the fixed-seed deque oracle pass real
`bytesAt` pointers back to append. Ordinary reads use explicit caller-local
storage, including the compatibility helper; no static/global scratch exists.
Every literal byte, counter, threshold, loop extent, CRC polynomial/order,
lifecycle condition and 26-byte DTO multiplication expectation remains.
The DTO-capacity test name now explicitly says expanded representation.

The CSV repeated-capture case preserves its snapshot assertions and adds a
fresh successful read of the real owner after all 100 captures, comparing raw
bytes and status to the saved frame. It therefore continues to detect an owner
mutation rather than testing only a detached local copy. Timing and bench CRC
callers additionally require successful read before their existing checks.
The memory tooling harness changed only its forbidden `at` stub to forbidden
`read`; passive-startup, allocation, anchor and ABI assertions are unchanged.

The independent reviewer identified that the two newly introduced REQUIRE read
checks in the ordinary CSV/timing suites were incompatible with their existing
DOCTEST_CONFIG_NO_EXCEPTIONS setting. Those checks were corrected to explicit
read-success bool, CHECK and failure-return guards; no test configuration was
relaxed. The bench tool already uses the all-asserts configuration, so its added
read-success REQUIRE is unchanged. Original assertions remain intact.

`scope_preservation.json` confirms no diff to locked tests, the historical
`tests/candidates/recorder25.cc`, config or core, unchanged public FrameBuffer
header, and the exact one-line memory-harness migration. No additional unlocked
migration or current adapted historical candidate was required. The root owns
independently authored new tests and full/target validation.

## Scoped validation

- Actual WSL host ABI: pointer and size_t 8 bytes; FrameBuffer 126312 / alignment8;
  StoredFrame 26 / alignment1; AttemptRecorder 159216 / alignment8.
- Existing recorder-memory tooling: all 23 tests pass, including 25/50 source
  preparation, passive setup/10000 loops, no allocations/probe calls, ABI and
  prohibited motor/MATCH/upload combinations.
- Existing recorder bench runner: normal and ASan+UBSan both pass all 11 cases,
  each with 1479334 runtime assertions. Existing one-row checksum sequencing and
  CRC checks are included. Fresh command/output receipts are in `bench_runner/`.
- Both corrected CSV/timing fixtures compile independently under the unchanged
  no-exceptions doctest setting; separate compile receipts preserve those checks.
- `git diff --check` passes. Git reports CRLF/LF checkout
  normalization notices for three migrated test files, with no whitespace error.

`validate.py` and adjacent stdout/stderr/JSON receipts contain the executed
commands and exact source hashes. Tool receipts were redirected into this new
implementation directory, preserving historical evidence.

No board access, target upload, MCU execution or motor action was performed by
this worker. Full host/sanitizer acceptance, independent review and final target
loader evidence remain coordinator-owned. These scoped results do not establish
loaded RAM, stack, complete 800us timing, physical B8/UART or a human phase gate.
