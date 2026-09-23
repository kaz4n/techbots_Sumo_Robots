# D091 bare-board synthetic recorder validation

2026-09-23 Asia/Dubai. P2 B8 preparation under D051/D075 and explicit bare-board
user test authority. This is not a phase gate or assembled-robot acceptance.

## Scope

Actual Robot -> inert MotorGate -> AttemptRecorder on the MCU, real elapsed clock,
200000ms from actual synthetic accepted release, STOP/deferred frame, bounded CRC.
No sensor, GPIO motor, ADC, QTR, IMU, matrix, UART, Bridge or RX initialization.
The actual source supplies synthetic data, clearly identified in all evidence.
Strong empty loop hook remains. Capture uses reviewed read-only MEM-AP only.

Status: PASS_SYNTHETIC_BARE_BOARD_RECORDER. Software17bb38a is implemented,
host-tested, target-compiled and independently reviewed. Exactsource1502e948 /
ELFeff3e050 /ZSK0448e3ac uploaded at13:17:26UTC to bareUNOQ2629958581.
Firstcapture failed30s wholeloaderread before privateRAM and remains preserved.
The reviewed smaller-read retry succeeded without changing/resetting firmware.
Fresh separate same-model runtime review PASS, no open findings; independently
verified155 artifacts, retained rows/bitwise CRC, heap accounting and read guards.
See reviews/P2_recorder_bench_review.md; no physical B8 or human gate.

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

## Actual bare-board runtime / capture

Evidence: P2_recorder_bench_raw/runtime_summary.json andruntime_retry1/.
MCU terminalFROZEN/failure0/recorderSEALED; sourceepoch71. Synthetic release507802us,
GO5607802us (full5100000us hold), STOP200508800us (recording200000998us). Terminal
elapsed200137638us includes CRC completion. Inputs explicitlysynthetic; no real
sensors or motion. MissingIMU deliberately produces one calibration-rejection
FAULT event(type9/detail5/value1), not an unexplained fault-free sensor claim.

Retained5001frames/8events,5009checksumrows; independent extraction from actual
captured RAM matches MCU CRC900325728 and both snapshots. Frames0..200000ms,
allpackOK/actualappliedduties0;5000intervals39ms809,40ms3382,41ms809. No skipped,
overwritten, rejected, invalid, incomplete or overflowing recorder evidence.
200073scheduler ticks,missedslots0,maxlateness3us;194902membertimingreceipts,
overruns0,maxstep203us. This is the synthetic runner only, not full app/HAL WCET.

LLEXT pool262144B: usedpayload236892,freepayload25116,largestfree21604,overhead136;
9used/3free chunks. Fulltwo262144Bsnapshots are identical (caa1c1cc...935fb),
validated logicalmetadata consistent. These are point-in-time capacity facts for
this loaded pool, not combined system/libc memory, allocation history or all RAM.
Mainthread region32768B/delta64; sampledminimumSP gives31208B headroom at clock
call sites,51,544,630samples. No stackpainting or historicalwatermark claim.

Capture47actualreads/934892B/51commands/281.632730s; every native read-only MEM-AP
command remains bounded30s and original48read/2MiB/600s guards unchanged. Deployed
loader/ELF/ZSK verified before privateRAM, fixed296B terminaldiagnostic and24B
heapdescriptor identical before/after. Loaderpackagedbin's known one-byte padding
difference is reported; deployedflash equals pinnedELF exactly. No second upload,
MCU reset, router/daemon action, Cortex attach or memory write during capture.
The earlier explicit CLIupload used the documented board programmer/reset path.

Leave the board in frozen inert recorderdiagnostic1502e948. Native UART/B8 dump,
physical sensors/buttons/wiring, SC-AJ calibratedtime, fullRAM history/full800us
WCET and humanphasegates remainpending. Next eligible software task is SC-AK whole
acquisition/decision timing, documented in P2_app_integration_map.md.
