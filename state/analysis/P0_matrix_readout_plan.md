# P0 matrix counter readout plan — 2026-09-22

Read-only plan, not an executed capture. Only existing board Linux files were
inspected, through bundled Windows adb -s2629958581 shell. No debugger/MCU
access, upload, source change or timing-helper change was performed.

## Exact reviewed default artifact

Dedicated directory:

```text
/home/arduino/sumox26-build/72214f8aa1b6d84e21d2dc8a568ea01adb5fe0295f3f3d0f362e8696d2543e8f/p0_matrix/artifacts/bench-default
```

| File | Bytes | SHA-256 |
|---|---:|---|
| p0_matrix.ino.elf | 74444 | 1fbb189bba0a52f2d23040522560aee66d8c1d0629e80e6476459cf05c43ec5d |
| p0_matrix.ino.elf-zsk.bin | 74444 | 74dcf3e03f0122c6d0df7158c48d09aabf3a9b1ca6f9d7eebbc063f570d7fe48 |
| p0_matrix.ino_debug.elf | 1369936 | e5c6a69095255296717ed4c75325ae94c32e4afe834779e20a056eda68fa3d3b |

Only the exact default/dynamic build is in scope. The final ELF is ELF32,
little-endian, ARM, ET_REL. The preserved debug ELF is for code inspection;
its symbol values have not undergone the final ELF's section normalization.

## Runtime layout expectations

The normalized final ELF has exactly one .bss: section9, NOBITS, size0x1e24
(7716 bytes), alignment8. Require those exact properties and exactly one
p0Seconds symbol: GLOBAL, OBJECT, DEFAULT visibility, section9, st_value0x78,
size4. Reject a changed hash/layout rather than updating an offset implicitly.

Useful corroborating final-ELF symbols:

| Symbol | .bss offset | Size |
|---|---:|---:|
| frame | 0x4 | 104 |
| scrollColumn | 0x6c | 1 |
| lastCounterMs | 0x70 | 4 |
| lastScrollMs | 0x74 | 4 |
| p0Seconds | 0x78 | 4 |
| matrix | 0x7c | 40 |
| Bridge | 0x370 | 352 |

The debug ELF displays p0Seconds at0x5498. That is neither its normalized
BSS offset nor its runtime RAM address.

Use the same pinned loader ABI already recorded in
P0_installed_debug_contract.md, after a fresh full loader identity comparison:

- llext_list at0x200017bc: head+0, tail+4.
- struct llext size196; next+0, fixed name[16]+4.
- LLEXT_MEM_BSS index3: base pointer+32, size+92.
- Traverse at most4 nodes, reject repeated/out-of-SRAM/unaligned/incomplete
  pointers, and require exactly one NUL-terminated name equal to sketch.
- Require the complete list-node and BSS ranges within
  [0x20000000,0x200c0000), exact runtime BSS size0x1e24, consistent tail,
  and a stable list plus matching selected-node identity/BSS metadata.
- Compute p0Seconds_address=BSS_base+0x78 without overflow and require its
  complete four-byte range within that validated BSS.

No runtime pointer/address is assumed in this plan. Do not reuse the timing
sketch's BSS base or node: uploading another sketch may relocate it.

## Linked startup check

The four .init_array entries were inspected in the exact matrix debug ELF:

| .text offset | Effect |
|---|---|
| 0x2568 | HCI reference/default initialization and scalar zero stores to matrix |
| 0x4204 | Bridge/Monitor references, zeroing and fixed-buffer initialization |
| 0x4b0c | Serial1/2/3 references, semaphore and ring-buffer initialization |
| 0x52f0 | C++ error-category registration through the no-op atexit implementation |

No constructor calls matrixBegin, Bridge.begin, UART begin or network/RPC
startup. The static-thread area has size0. initVariant at0x465c is a return;
main at0x4660 invokes setup then loop/__loopHook, with no SerialUSB.begin call.

The selected __loopHook at0x2524 is the same yield-and-Bridge-started check
audited for timing. Its started flag remains false. The exact pinned loader's
uncontended zero-mutex path was disassembled in the earlier audit; this does
not establish portable mutex correctness or remove loop-hook overhead.

setup at0xd4 explicitly calls matrixBegin, matrixSetGrayscaleBits(3), and millis.
loop at0x104 draws on the100ms interval and increments p0Seconds by elapsed
whole1000ms periods, retaining fractional remainder. Installed staged config
confirms P0_SCROLL_MS=100 and P0_COUNTER_MS=1000. This sketch intentionally
activates the matrix driver/interrupt workload. Source-backed normal startup
stops the loader animation before sketch entry; Immediate remains outside scope.

## Smallest separate capture approach

Create a narrowly pinned matrix-only script if the coordinator authorizes it.
Do not broaden p0_capture.py's timing-only path, hashes, symbols or completion
criteria. A new script may import its already reviewed pure loader_image and
bounded file/range/read helpers, with its own exact matrix identity/layout
checks and two-counter-read result. No common framework or arbitrary memory
read arguments are needed.

Before any read, validate unchanged OpenOCD, absolute swj-dp helper, MEM-AP
configuration and package ELF identities using the existing hashes. Use the
unchanged MEM-AP-only configuration: no Cortex target, reset pin, flash driver
or event hook. Store raw outputs and JSON in a fresh dedicated capture child.

First read the263680-byte loader flash span and compare every byte against the
pinned ELF's contiguous file-backed PT_LOAD image, as corrected in
P0_loader_identity_analysis.md. Packaged BIN is provenance only. Then read
exactly74444 bytes at0x08100000 and compare against the pinned matrix
elf-zsk.bin. Do not interpret RAM if either comparison fails.

Resolve the bounded LLEXT node/BSS as above, then read p0Seconds as one aligned
32-bit MEM-AP transfer. Prefer explicit
sumox.mem read_memory <validated-address> 32 1
rather than assuming that four separate byte reads make a coherent live
counter. Save exactly one uint32 result and monotonic/UTC timing bounds.

Take a second aligned32-bit read after a host-side3-second interval. A single
bounded OpenOCD command sequence may echo fixed labels around the two scalar
results with sleep3000 between them; that sleep delays the Linux debugger
process and does not halt the MCU. Alternatively two short read sessions with
a bounded Python wait make individual host timestamps easier to record.
Neither sequence should write, halt, reset, flush caches or call MCU functions.

Retain a finite overall deadline and the same bounded node traversal. A
120-second capture budget is a reasonable first reviewed candidate: the timing
loader read took approximately79seconds, and matrix/sketch data adds another
roughly23seconds at that prior rate. This is a planning estimate, not a
matrix-active throughput guarantee. Timeout must leave an incomplete capture;
it must not skip identity bytes or silently extend/retry.

## Interpretation and evidence limits

Both results must be exact uint32 integers from the same verified symbol and
loader/sketch/node/BSS identity. The coordinator's explicit counter contract is
advance=(second-first) modulo2^32, with1 <= advance <= 0x7fffffff. This permits a
forward wrap and rejects equality or an ambiguous/reverse half-range jump.
Record the raw values, advance, read timing bounds and requested wait rather
than claiming an exact one-second clock calibration. Failure must not trigger
an automatic reset/retry.

Advancement shows the reviewed sketch reached loop and progressed through the
matrix work to update its elapsed-period counter. It does not prove that SUMO
is visually correct, that every matrix LED works, that no reset occurred
outside the observation, or that a1kHz loaded control tick meets its budget.
A human visual observation remains separate. Matrix-active reads perturb the
bus, so this is a liveness/counter observation, not a timing qualification.

Recommended JSON fields: pinned artifact/source identities; loader/sketch
comparisons; node/BSS/symbol addresses and ranges; raw counter results; UTC and
monotonic read bounds; delta; status; command results and deadlines; and these
limitations. Missing identity/layout/read evidence must produce nonzero failure.

Evidence queries all exited0: sha256sum/stat of the three artifacts,
readelf -hSW/-sW/-rW, bounded nm filters and objdump address ranges,
staged config constants, and installed matrix-constructor source. Only this
plan was initially written. The coordinator subsequently authorized the separate
tools/p0_matrix_capture.py implementation, importing the exact unchanged timing
helper SHA885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c.
Its quiet-import pure API is analyze_counter(first, second), returning
dict(first=first, second=second, advance=modular_delta) or raising ValueError.
The wrapper uses the existing Capture reader for each aligned four-byte scalar,
records each read's raw file and host timing bounds, and waits three seconds
within the shared120-second capture deadline. It reuses find_bss/verify_flash
and the unchanged MEM-AP configuration; it does not broaden the timing helper.
Before reporting COUNTER-ADVANCED, the wrapper also rereads the eight-byte
LLEXT head/tail and the selected196-byte sketch node. It compares head/tail,
next pointer, the complete fixed name field, and BSS base/size against the
original raw dumps selected through validated read metadata and hashes. A
missing/modified original dump or changed post-counter identity fails closed.
These two post-counter reads keep the worst-case total at12 memory reads and
remain under the unchanged16-read/120-second limits.
Independent tests/review remain required before any matrix MCU read. No board
invocation or MCU operation was performed by this worker.
