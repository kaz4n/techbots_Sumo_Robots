# D091 bare-board synthetic recorder validation

2026-09-23 Asia/Dubai. P2 B8 preparation under D051/D075 and explicit bare-board
user test authority. This is not a phase gate or assembled-robot acceptance.

## Scope

Actual Robot -> inert MotorGate -> AttemptRecorder on the MCU, real elapsed clock,
200000ms from actual synthetic accepted release, STOP/deferred frame, bounded CRC.
No sensor, GPIO motor, ADC, QTR, IMU, matrix, UART, Bridge or RX initialization.
The actual source supplies synthetic data, clearly identified in all evidence.
Strong empty loop hook remains. Capture uses reviewed read-only MEM-AP only.

Status: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/INERT-UPLOADED. Fresh separate
same-model review PASS, no open findings. Exact source1502e948/ELFeff3e050 uploaded
at13:17:26UTC to bareUNOQ2629958581. Firstcapture failed30s wholeloaderread before
privateRAM; preservedruntime_run1. Reviewed chunkedidentity retry is running,
without firmware change/reset. Runtime result remains UNOBSERVED until decoded.

## Evidence and limits

- Contract: P2_recorder_bench_contract.md. Pinned source/layout: native audit F113.
- Offline decoder: tools/recorder_heap.py; independent28methods pass in author receipts.
- Runner tests: new dedicated .cc harness, normal/sanitizer; no locked tests changed.
- Target compile exit0: source1502e948,74files and3ELFs inspected; exact physical
  staging/board hashes match. CLI146072program/236660globalRAM/25484remaining with
  low-memory warning. These compiler labels are not measured free RAM.
- Runner11cases/1,464,342assertions normal andASan/UBSan PASS. Heap28methods PASS;
  capture39 plus12newflash methods PASS;5controlledupload methods PASS.
- Existingtooling56checks PASS:49passedfirst,7passedaftercorrecting two importpaths.
- Actualupload andboundedreadback scope/receipts: P2_recorder_bench_run.md andraw.
- Freshreview: reviews/P2_recorder_bench_review.md, source/final/chunked approvals.
  The chunkedhelperfd1932ac preserves every original guard and established test.
- Native wrapper publishes coherent296B terminal diagnostic and samples SP at clock
  call sites. This cannot measure historical stack high-water or fullapp WCET.
- Allocator captures describe loaded LLEXT pool capacity only, not all memory pools,
  historical minimum, arbitrary aligned allocation guarantees or atomic snapshots.
- SC-AJ independent MCU clock qualification, physical B8/no-gap UART transfer,
  local reset/service integration and full sensor scheduling remain separate.

## Preserved development corrections

The independent author corrected only new harness expectations: doctest no-exception
assertion macro, then expected final MotorGate STOPPED rather than NONE. The root
corrected a new capture-contract capacity typo5000 to the existing config5001.
Heap logical metadata digest excludes all unused padding including chunk0 bytes4..7;
prior encoding receipts are preserved. No established assertion was weakened.
Runner review closed failure-revival paths before final target/source review.

## Capture retry and source review corrections

The first real capture's throughput required smaller flash reads, not larger
limits. See P2_recorder_capture_timeout.md. New12flash tests preserve the known
one-byte packagedloader/ELF difference while requiring exact deployedELF equality.
First new package-equality expectation was corrected with its failedreceipt kept.
A suspected layout defect was retracted before code changes: nm includes section
VMA while readelf st_value0x28928 was already relative; six new tests protect it.
One ELF audit helper initially inherited the old raw output directory; only its
new uniquely named receipt was moved within the verified workspace, with a move
receipt. Existing artifacts were untouched. No established/locked tests changed.
