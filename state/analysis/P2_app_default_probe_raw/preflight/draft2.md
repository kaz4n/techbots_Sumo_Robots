# Exact default app: bare-board load and passive observation proposal

Draft for coordinator adoption, 2026-09-24. This document authorizes no upload,
MCU read, peripheral operation, grant change or manifest entry. It follows
`P2_app_default_bare_eligibility.md` (reviewed corrected revision72841817), with the exact
target-size correction below. D104/D114 retain their original limits and scope.

## Scope and one attempted run

Prepare one identified load of the **unchanged** default-startup app, MATCH0 and
MOTORS_ALLOWED0, on serial2629958581 through explicit ADB, under the human-reported
bare UNO Q setup. Explicitly admit the existing MotorGate/native motor setup:
proposed D10 output LOW, existing D3/D5/D6/D9 PWM device/pad setup, zero pulses
and bounded timer-settle checks. Successful due epochs repeat inhibited output.
This is real native I/O, not an I/O-free probe. No HIGH/nonzero request is admitted
by this build. No PINMAP, motor connection, voltage, waveform, coast, physical
safety or STAND/RING qualification is inferred.

All optional `SetupGrants{}` remain false; app/core/HAL/config bytes remain
unchanged. No sensor, ADC, QTR, I2C, matrix, UART, Bridge or service-reset grant is
introduced. Retain the exact loader/startup/empty loop-hook/thread evidence from
D117 and the eligibility audit; do not equate app-source silence with no stock
loader/peripheral initialization. No new firmware Runner or diagnostics exist.

After independent source/target/collector/guard review, a separately frozen run
record and approval may allow **one** fresh checked build/upload attempt and
**one** capture attempt. Reproduce the exact ELF/ZSK hashes before upload. Reuse
the D114 pattern of an exclusive local attempt receipt created before invoking
the uploader, binding run ID, serial, transport, source, software commit, hashes,
scope and exact review bytes. Failed/uncertain upload consumes the attempt;
there is no automatic retry, reset, restoration, app abort, halt or replacement
image. The existing generic app upload refusal remains until the separately
reviewed exact route is adopted; it must remain the default thereafter.

Start the one capture after successful upload command completion, without a
guessed readiness delay or polling until success. The app does not terminate
when observation ends. Report that it remains loaded and may continue inhibited
native ticks; finite collector lifetime does not mean a finite firmware run.

## Fixed identity and ABI

| Item | Exact pin |
|---|---|
| Source | `e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69` |
| Loadable `app.ino.elf` | 176048 bytes; `8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257` |
| `app.ino.elf-zsk.bin` | 176048 bytes; `c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5` |
| Offline debug ELF | `d9746e05b7081e95d07d1244015aa5bcd587741d6ab23c2449e17ff14dc70449` |
| Loader ELF | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

The earlier176064-byte prose was incorrect; neither an added header nor an
omitted prefix is assumed. Both exact176048-byte files are retained under
`P2_dump_fifo_raw/target_e820c0e1_bench-default/`. The unique checked receipt is
`d92f929c6cc84961bb86dfea3da2ad00`; final ELF is in its `build`, ZSK in `artifacts`.
Debug ELF is an offline type reference, never an upload candidate.

Proposed passive input directory is exactly
`/home/arduino/sumox26-capture-input/app_default_e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69`,
containing just the two pinned loadable files. Coordinator must explicitly prepare
it without overwrite and preserve copy/hash receipts; existence is not claimed.
No runtime search, generic-artifact fallback, new compilation or repinning.

Reuse only unchanged pure helpers in `p0_capture.py` (SHA256
`885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`) and
`recorder_heap.py` (`d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92`).
Pin p0's OPENOCD/HELPER/LOADER/LOADER_ELF/CONFIG paths and hashes verbatim, plus
READELF hash `c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e`.
All regular-file/no-symlink/hash checks precede commands; no old capture module
is monkeypatched or repinned. Loader flash comparison uses unchanged
`p0.loader_image(pinned_loader_elf_bytes)` over all263680 bytes; retain the
existing loader-BIN versus flashed-ELF identity qualification, not a blind BIN
comparison. Compare all176048 sketch flash bytes directly to the pinned ZSK.

Exact final ELF is ELF32, little-endian, ARM, ET_REL. Require one `.bss`, section8,
NOBITS, flags3, sh_addr87872, file offset92384, size167272, alignment8. Require one
LOCAL/OBJECT/DEFAULT symbol `_ZN12_GLOBAL__N_17runtimeE`, section8, raw
st_value0, size166376. **Runtime address is relocated BSS base+0**: do not
subtract sh_addr from the already section-relative ET_REL symbol. The pinned
loader's `llext_load.c:781-782` adds raw st_value for ET_REL. The whole BSS and
whole Runtime must fit their validated containing allocation and SRAM.

Saved actual debug ABI places TransactionReport at Runtime+162128 (full size504),
RuntimeReport at Runtime+164664 (full size600). Capture only these prefixes:

| Prefix | Byte fields and little-endian u32 fields, relative to prefix |
|---|---|
| Transaction,24 bytes | phase0; fault1; decision_made2, finished3, timing_valid4 (bool); padding5..7; started_us8, decision_us12, completed_us16, execution_us20 |
| Runtime,28 bytes | phase0; fault1; fresh2, initialization_complete3, raw_lines4, imu_expired5, calibration_interrupted6 (bool); padding7; next_release_us8, missed_releases12, epochs16, service_passes20, maximum_execution_us24 |

Runtime phase values0..4 mean NOT_STARTED/RUNNING/STOPPED/FAULT/STOP_OBSERVING;
fault0..5 means NONE/PORT/CLOCK/SERVICE_LIMIT/TRANSACTION/PROJECTION. Transaction
phase0..4 means NOT_INITIALIZED/IDLE/ACQUIRING/DECIDED/FAULT; fault0..6 means
NONE/SETUP/ORDER/CLOCK/IDENTITY/RECEIPT/ABORTED. All bool bytes must be0/1;
padding is preserved raw but has no semantic constraint. Unknown enum/bool or
wrong extent is MALFORMED_SAMPLE, not an invented firmware fault. There is no
pointer/token/floating-value/Robot/Gate/recorder decoder in this minimal scope.

## Validated loader references and allocation containment

Fixed SRAM is `[0x20000000,0x200c0000)`. LLEXT list at0x200017bc is8 bytes:
head+0 and tail+4. Node size196: next+0:u32; name+4:16 bytes requiring a NUL;
BSS pointer+32:u32; BSS-on-heap+71:bool; BSS size+92:u32; section count+184:u32;
section-header pointer+188:u32; headers-on-heap+192:bool. These offsets and
the24-byte heap descriptor were confirmed by **offline** GDB on the pinned
loader, not by MCU reads.

Heap descriptor at0x2000112c is24 bytes. First three u32 must be
`(0x20013890,0x20013890,262144)`; preserve all24 bytes and require exact before/
after equality. Pool is exactly262144 bytes at0x20013890, with16 indexed16KiB
reads per snapshot. Validate each through unchanged `recorder_heap.decode_pool`;
compare canonical allocator metadata through unchanged `compare_pools`.
Changing allocated app payload is expected and does not invalidate metadata
equality. The decoder's free/used payload, largest-free-payload, chunk counts,
overhead and both snapshot hashes remain allocator facts, not total system RAM.

Before reading each node, require aligned4 SRAM bounds and its entire196-byte
extent within a **used** allocation from the first validated heap snapshot.
Follow only the admitted head/previous next, at most3 distinct nodes. Empty list
requires both head/tail0; nonempty list requires null termination and tail equal
to the last visited node. At most one name may equal `sketch`; duplicate matches,
cycle, invalid pointer, invalid bounds or excess nodes refuse further private
reads. A sketch node must have BSS-on-heap1, size167272, aligned8 BSS entirely
within one used allocation, and section count16/header pointer0x0812ad30/
headers-on-heap0 (the exact resident flash section table). Runtime and both
prefixes must fit both BSS and that allocation without uint32 overflow.

A used chunk's admitted payload interval is
`[HEAP_BASE + index*8 + 4, HEAP_BASE + (index+size_units)*8)` using validated
decoder output. Alignment slack may precede a section; containment does not
require its pointer to equal the raw chunk payload start. Recheck the same
containment against snapshot2. No inferred pointer authorizes any other read.
The final pass rereads exactly the original node addresses, follows no new
links, and requires all node bytes and the list bytes unchanged. All checks are
sampled consistency checks, never an atomic allocator or running-object snapshot.

## Complete read plan and new finite ceiling

Coordinator selected **64 memory reads / 80 commands for this new contract
only**, retaining <=2097152 total requested bytes, <=16384 per RAM read,
<=65536 per flash read, <=600 seconds entire collector lifetime and
<=30 seconds per command (also bounded by remaining total time).
Attempts, including launch/short-read/failure, consume their purpose and budget.
No widening after refusal or execution, resumption, fallback, retry or extra
diagnostic scan is allowed. These limits are observation bounds, not guarantees
of completion or a permission to use spare slots for other reads.

| Fixed purpose | Maximum reads | Requested bytes |
|---|---:|---:|
| Full loader before+after:5 blocks each | 10 | 527360 |
| Full ZSK before+after:3 blocks each | 6 | 352096 |
| Two complete heap snapshots:16 blocks each | 32 | 524288 |
| Heap descriptor twice | 2 | 48 |
| LLEXT list twice | 2 | 16 |
| At most3 nodes, each twice | 6 | 1176 |
| Runtime28 and Transaction24 prefixes, each twice | 4 | 104 |
| **Complete maximum** | **62** | **1405088** |

Exactly four metadata commands precede memory: OPENOCD `--version`, READELF
`--version`, READELF `-h -S -W app.ino.elf`, READELF `-s -W app.ino.elf`.
Thus max commands=62+4=**66**. The complete plan is checked before first command.
The earlier48-read/64-command contracts cannot accommodate this image/plan.

Fixed order and labels:

1. `loader-before-00..04`, `sketch-before-00..02`; verify both full images before RAM.
2. `heap-descriptor-before`, `pool-1-00..15`; validate the pinned descriptor/pool.
3. `llext-list-before`, reachable `node-before-1..3`; validate references/containment.
4. If one valid sketch: `runtime-first`, then `transaction-first`.
5. `pool-2-00..15`, then `heap-descriptor-after`; validate/compare metadata and descriptor.
6. If one valid sketch: `runtime-second`, then `transaction-second`.
7. Same-address `node-after-1..3`, then `llext-list-after`; require exact equality.
8. `loader-after-00..04`, `sketch-after-00..02`; verify both full images again.

Flash addresses are base+65536*index, sizes min(65536,total-offset); bases
0x08000000/0x08100000. Pool addresses are HEAP_BASE+16384*index. Stable absence
of `sketch` omits exactly the four app-prefix reads, still completes both flash/
heap sweeps and descriptor/list/node checks (maximum58 reads/62 commands,
1404984 bytes). No absence-to-OOM diagnosis is made. Invalid/ambiguous evidence
fails immediately, preserving all already collected bytes; it is not an absence.

## Honest output and minimal implementation seam

Propose one passive module `tools/app_default_capture.py`, reusing p0's pure
identity/range/image helpers and the existing heap decoder. Public seams:
`decode_app_samples(runtime_first: bytes, transaction_first: bytes,
runtime_second: bytes, transaction_second: bytes) -> dict`,
`Capture(folder: Path, report: dict)`, `Capture.run(argv, attach=False) -> str`,
`Capture.read(label,address,size,region='ram') -> bytes`,
`check_identities(capture,artifact_dir) -> tuple[Path,Path]`,
`read_layout(capture,elf) -> dict`, `collect(capture,artifact_dir) -> dict`,
`main(argv=None) -> int`. Imports/construction are passive. `attach` means only
the existing MEM-AP command category, never Cortex attach. Test substitutes
may replace public subprocess/clock/filesystem calls; no new transport framework.

CLI: `python3 tools/app_default_capture.py --artifact-dir EXACT [--output DIR]`.
Use existing p0 fresh direct-child/no-symlink/exclusive0700 rules under
`/home/arduino/sumox26-capture`; generated default is `app-default-<UTC>-<PID>`.
No address/size/command/limit/image/phase override. Command execution accepts
only the four ordered metadata argv and the one currently admitted MEM-AP read:
`OPENOCD -f CONFIG -c 'dump_image {EXCLUSIVE_OUTPUT} 0xADDRESS SIZE' -c shutdown`.
CONFIG stays byte-identical: no Cortex target, halt/reset/write, peripheral
read, daemon, GDB/telnet/TCL listener, UART/socket/Bridge operation or MCU call.

Capture JSON has schema_version1, pinned source/ELF/ZSK/loader/helper identities,
maximum plan and actual counts, all command/read argv and UTC/monotonic brackets,
output directory, file hashes/partial blobs, layout, extension, heap, app_samples,
errors and limitations. `collection_status` is CAPTURED only after all required
identity/metadata checks; otherwise FAILED. Extension is PRESENT or ABSENT only
for validated stable descriptors; otherwise UNKNOWN with the actual error.
Absent app_samples is null. Keep raw integer enum values plus literal names.
Pure sample errors are ordered, non-exhaustive, deduplicated `{code,path}` with
EXTENT/ENUM/BOOLEAN; no cross-object state consistency assertion is introduced.
The pure decoder returns exactly `runtime` (two sample dictionaries),
`transaction` (two sample dictionaries), `errors`, `runtime_observation` and
`transaction_fault_sampled`. Each sample contains the named prefix fields above
as integers plus `phase_name`/`fault_name`; an unknown enum name is UNKNOWN.
A wrong-size prefix produces null in its array position and an EXTENT error.
Other invalid values remain raw with errors. Paths use `runtime[0]`,
`transaction[0]`, `runtime[1]`, `transaction[1]` and their field suffixes;
check in that acquisition order. Immutable exact bytes are required for each
argument; wrong Python type follows the same EXTENT error path. Padding is
excluded from the semantic dictionaries and retained in the original blobs.

For present samples, independently classify Runtime observation in this order:
MALFORMED_SAMPLE on decoder errors; FAULT_SAMPLED if either sampled phase is
FAULT or fault code is nonzero; RUNNING_COUNTER_ADVANCED if both phases are
RUNNING, both faults NONE and second epochs>first epochs; otherwise
INCONCLUSIVE_SAMPLED. Epochs saturate in this source: do not infer wrap or health
from equality. Always retain both raw values, missed releases and all selected
fields. Transaction observations retain both phase/fault/flags/timestamps as
samples; nonzero fault/FAULT phase is separately flagged. No relationship among
S/D/C/execution, no matching Runtime/Transaction epoch, receipt, completion or
Robot state is asserted from these live multi-byte reads. A valid transient
combination is not normalized into a healthy transaction or called corruption.
`maximum_execution_us` is merely the sampled stored counter, not WCET.

Fault and absent-extension observations can be successfully **collected**, but
their run outcome is nonzero. CLI exit0 requires CAPTURED, PRESENT, no sample
errors, RUNNING_COUNTER_ADVANCED and no Transaction fault sample. Every other
collection/observation outcome exits1, including CAPTURED with ABSENT, a sampled
fault, malformed bytes or inconclusive progress; CLI argument errors exit2.
The collector report keeps those distinctions rather than converting a valid
fault observation into a transport failure. No
COMPLETED/PASS gate label. Retain actual failure/launch/timeout/partial files and
final JSON even on errors after exclusive output creation. Bounded child timeout
only ends the observer process; it does not stop firmware. Do not perform a
cleanup upload/reset or signal any unrelated service.

Two validated matching allocator-metadata samples report retained LLEXT free
payload and largest region. They do not measure transient loading peak, stack
headroom, total free system RAM, five-minute timing, calibrated clock, electrical
inhibition or hardware/gate acceptance. Advanced sampled epochs are evidence
of observed app progress on the identified load, with live-read limitations.

## Independent acceptance before any run

Freeze independent literal ABI/heap/prefix fixtures before implementation
execution. Cover exact identity/byte lengths/ET_REL offset0, duplicate symbols,
wrong BSS/section header, pointer arithmetic/alignment/allocation escapes,
zero/one/three/four nodes, cycles/duplicates/changed descriptor/node/metadata,
absent extension, full before/after flash mismatch, payload-only heap changes,
all enum/bool/extent errors, changing/equal/saturated/decreasing counters,
faults and normal transient report combinations. Cover finite-purpose order,
replay/unused budget rejection, output/symlink guards, launch/nonzero/timeout/
short read, exact62-read/66-command maximum, and no retry/extra action. Preserve
all old D104/D114 tests and pinned helper bytes. Source review must inspect
actual allowed commands and single-attempt upload route before any execution.

Coordinator selections still required: adoption of this draft; exact new run ID,
run/approval receipt names and specialized guard route; final collector/guard
hashes and review receipt; explicit input-directory preparation. No unresolved
choice permits a source/grant change or substituted image. The64/80 ceiling,
prefix sizes and unchanged-app scope are already selected for this proposal.

Preflight evidence is under `P2_app_default_probe_raw/preflight/`: saved ELF
derivation and actual debug excerpts, exact budget, and bounded board-Linux
offline loader type/symbol receipts. The initial offline query used a nonexistent
heap backing-symbol name and exited1 after returning the other requested types;
that failure is preserved. Corrected query for `kheap_llext_heap` exited0 and
confirms0x20013890. Neither query attached to or accessed the MCU.
