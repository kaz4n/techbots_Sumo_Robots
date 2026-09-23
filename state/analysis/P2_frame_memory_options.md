# P2 lossless frame-memory options

2026-09-23 Asia/Dubai. Bounded design audit under D051/D075; only this report
was written. No source/test/ledger change, compilation, board command, upload,
MCU action or measurement. The local date is the PLAN section 3 P0/P1 day;
current P2 software exceptions do not pass any human gate. D101 integration is
concurrent work owned by the coordinator; this report does not review it.

## Recommendation

Replace the private array of 26-byte `StoredFrame` objects with a 25-byte payload
array and a packed two-bit status array. Keep `StoredFrame` unchanged as the
26-byte transfer/CSV value. Use an explicit caller-owned copy-out read operation,
not a hidden scratch buffer behind the current pointer-returning `at()`.

This preserves all 5001 frames, 25 Hz cadence, 200-second endpoint capacity,
4096 events, exact raw bytes and all existing loss/lifecycle semantics. It needs
an explicit public-contract amendment and narrow unlocked test fixture changes.
It is preferable to reducing retention or making another toolchain assumption.

At the inspected declaration, `PackStatus : uint8_t` has exactly OK=0,
CLAMPED=1 and INVALID=2 (`src/core/logframe.h:36`). `append()` already rejects
every other value before modifying payload/order. Two bits therefore preserve
every status that may legitimately enter a retained slot.

| Storage at capacity 5001 | Bytes |
|---|---:|
| Existing payload/status array, 5001 * 26 | 130026 |
| Separate payload array, 5001 * 25 | 125025 |
| Separate status array, ceil(5001 / 4) | 1251 |
| Proposed payload/status arrays | 126276 |
| Exact raw-array reduction | **3750** |
| Proposed frame plus unchanged event arrays | 159044 |

With the present field order, the predicted target FrameBuffer size is 126300
versus 130052 bytes (32-bit size_t/alignment 4), a 3752-byte object reduction.
The analogous conventional 64-bit host sizes are 126312 versus 130064. These
are layout calculations, not fresh ABI/ELF evidence. Obtain actual sizeof and
target symbol/section evidence; code size, alignment and loader metadata can
change the net saving. Do not claim exactly 3744 or 3750 bytes of loader relief.

The coordinator reports D101 MATCH's conditional loader model is 816 bytes over
the pool before its separate 400-byte duplicate-result removal. That report is
context, not independently recomputed here. A 3750-byte array saving is useful
margin against this deficit, but does not by itself prove final app loadability,
future P2 capacity, stack headroom or measured free RAM.

## Pointer contract and smallest honest API migration

`recorder_frames.h:34-36` and `P2_frame_buffer_contract.md` item 5 currently return
a pointer to an actual StoredFrame, oldest first, null outside size. It remains
valid until append/reset/destruction; other reads do not invalidate it.

A single mutable scratch StoredFrame, or any fixed small rotating cache, behind
unchanged `at(index)` silently breaks this contract. Returning a reinterpret_cast
of payload storage cannot create the absent adjacent status byte. Keeping a
decoded StoredFrame for every possible simultaneous pointer loses the saving.
Do not retain the old signature with any of these implementations.

The smallest honest replacement is:

```cpp
bool read(std::size_t chronological_index, StoredFrame& output) const;
```

Return false outside size, including SIZE_MAX, with output unchanged; validate
the bound before index arithmetic. On success copy exactly the 25 bytes and
decode that physical slot's status. Caller-owned output survives every later
read, append, reset and owner destruction. No optional/heap/caching mechanism is
needed. Document exclusive, nonconcurrent access as before. Alternative naming
`at(index, output)` is equivalent; a pointer return to the explicitly supplied
output would preserve null-check syntax but adds no useful production capability.

For ordinary old assertions, a test-only helper taking `(buffer,index,storage)`
can return `buffer.read(index,storage) ? &storage : nullptr`. Existing null/data/
status assertions then remain literally intact, using a separate local storage
object for every simultaneously retained pointer. Do not use one global/static
scratch object in that helper. Add direct read-contract tests as well.

There is one important limit to fixture-only compatibility: four named tests
at `test_recorder_frames.cpp:410-474` and the fixed-seed oracle at 581 onward
exercise a *genuine retained-array alias* passed back into append, including the
oldest slot replacing itself. A copied local cannot honestly test that condition.
Two defensible choices exist:

1. Smallest production API: adopt read only and explicitly supersede the old
   borrowing capability. Preserve all output/order/counter assertions and the
   read-then-append scenarios, but name their changed scope honestly. This is an
   API migration, not identical alias coverage.
2. Recommended when retaining every old alias guarantee is required: also expose
   `const logframe::FrameBytes* bytesAt(std::size_t index) const`, with the old
   append/reset/destruction lifetime and null bounds. The separate payload array
   supports that contract directly. Use bytesAt only in the genuine alias tests;
   use read for normal consumers. Preserve append's local 25-byte source copy
   before any destination mutation. This adds one small accessor, no persistent
   cache and no capacity cost. The old data/status/order/counter predicates and
   their true alias condition can all remain. This is the recommended variant
   if the coordinator's acceptance requires preserving every existing assertion
   *and* the scenario each assertion was intended to prove.

Do not substitute private-layout test hooks for the public alias contract.

## Bounded implementation details

Use `FrameBytes payloads_[config::LOG_FRAME_CAPACITY]` and
`uint8_t statuses_[(config::LOG_FRAME_CAPACITY + 3U) / 4U] = {}`. The constants
four slots/byte and two bits/status are representation facts, not tunables.
Keep all indices and counters unchanged. For physical slot p, the status byte
is p/4 and the shift is 2*(p%4). Clear only that two-bit lane, then insert the
validated status; reads shift and mask 3. Three lanes in the final byte are
unused for capacity 5001. Reject unknown statuses before touching either array.

Zero-initialize packed bytes before any read-modify-write, including automatic
host instances. Reset stays a constant logical clear: do not clear either array.
After reset, each newly visible slot gets both payload and status rewritten.
Keep append's accepted/loss saturation operations and overwritten ordering
unchanged; no traversal, codec conversion, timestamp interpretation or new clock.
No atomics or concurrency assumptions are introduced.

The CSV schema and raw hex remain unchanged. `csv::frameRow(const StoredFrame&)`
needs no API change. Native/inert checksums must feed the reconstructed original
single status byte after the unchanged 25 payload bytes; hashing packed storage
would change the wire evidence and is prohibited.

## Exact migration inventory from current source

Production and active bench callers:

- `src/hal/recorder_frames.h/.cpp`: arrays, public read/optional bytesAt contracts
  and implementation. Keep StoredFrame size assertion and owner noncopyability.
- `src/hal/recorder_dump.cpp:233`: one local StoredFrame in FRAME_ROW, read it and
  call the unchanged formatter; preserve the existing failure outcome.
- `bench/recorder_inert/src/recorder_bench.cpp:307`: local snapshot and identical
  byte/status CRC ordering, failure and one-row-per-call behavior.
- `bench/p2_recorder_memory/src/memory_probe.h/.cpp`: View must own a StoredFrame
  value plus explicit frame-present flag; no pointer to a function-local snapshot.
  QueryProbe remains bounded/passive when uncalled. The 96-byte Abi record keeps
  its current fields and reports the new actual sizes.

Current test callers requiring only fixtures/API adaptation:

- `tests/test_recorder_frames.cpp`: lookup helpers, bounds, retained-source and
  oracle sites as above. Existing 26-byte DTO and multiplication assertions stay
  mathematically true; label them expanded representation, add packed-size checks.
- `tests/test_attempt_recorder.cpp`: frame-check and snapshot helpers, with every
  loss/epoch/token/lifecycle assertion unchanged.
- `tests/test_recorder_csv.cpp`: two retained-owner read sites around lines 510
  and 535. Preserve repeated capture nonmutation checks with fresh reads of the
  source in addition to checking the caller snapshot, so tests do not become
  vacuous local-copy checks. Standalone literal-format tests remain unchanged.
- `tests/test_recorder_rate.cpp`: checkTime and out-of-range lookups; retain the
  literal 25 Hz, 5001 capacity and 200000 ms endpoint assertions.
- `tests/test_tick_timing.cpp:341`: copy out the last frame before its existing
  byte assertion; no timing/core test predicate changes.
- `tests/fixtures/app_dump/roundtrip.cc:18`: copy out for independent expected CSV.
- `tests/tooling/recorder_bench_cases.cc:53,260`: CRC and status lookup helpers.
- `tests/tooling/test_recorder_memory.py:432`: replace the forbidden old method
  stub with the new read method; include bytesAt only if a retained probe uses it.
  Keep all allocation/startup/probe-anchor/ABI assertions.

`tests/candidates/recorder25.cc` also uses at but is explicitly a historical
D071 artifact. Preserve it and its old receipts. For current-source candidate
reproducibility, add an explicitly named current-API adapted copy/runner, preserving
all six test predicates, rather than silently changing that historical evidence.
The old `P2_memory_candidate_tests.py` already refuses to overwrite its receipt.
`tools/recorder_memory_build.py` copies current source and should not need a
semantic change; its 25/50 source preparation tests still need to pass.

No at caller was found in tests/locked. No config, core encoding, EventBuffer,
AttemptRecorder lifecycle, receiver schema, wiring or build-policy change is
needed. Historical state/analysis source snapshots must remain untouched.

## Required evidence for adoption

1. Freeze the explicit contract amendment under D051/D075 before implementation;
   preserve D069 ordering/loss/reset and D072 cadence/capacity clauses.
2. Independent new tests cover all three statuses in every two-bit lane, repeated
   replacements 0->1->2->0, adjacent-lane isolation, slot 3/4 and final-slot wrap,
   full multiwrap mixed statuses, stale status after logical reset, unknown values
   3..255 causing no stored change, SIZE_MAX rejection with unchanged output,
   independent simultaneous snapshots and live payload aliasing if bytesAt exists.
3. Preserve existing literal/deque/attempt/rate/CSV/CRC/timing assertions; run the
   affected normal and sanitizer suites and full existing safety regression.
   Rerun inert memory/recorder tooling and actual app dump/strict receiver roundtrip.
4. Review source hashes before any existing inert-manifest refresh. Compile the
   final actual app in inert and MATCH modes without upload. Capture source/ELF
   identity, target sizes/alignment, runtime owner size, relevant sections and
   constructors; recompute the conditional loader peak and worst contiguous chunk
   requirement. Count new text and symbol metadata, not just bss savings.
5. Independent fresh-context review must check lane isolation, new API lifetimes,
   probe ownership, absence of weakened tests and identical serialized evidence.
   Retain any oversize/failure receipt. Loaded RAM/stack/WCET/physical B8 and all
   human gates remain pending even if compile and conditional model pass.

## Simpler alternatives considered

- The coordinator's separate duplicate RobotResult removal is the first sensible
  small fix; do not duplicate that work here.
- Sharing installed generated pin-table access has an older captured-ELF gross
  opportunity of 1680 bytes (`P2_app_runtime_ram_audit.md`). Current retention must
  be rechecked. It crosses native sensor/motor adapters and their identity/timing
  fixtures, so prefer recorder representation work before that wider change.
- Transfer retains one 1152-byte wire line, while CSV's public 1024-byte bound plus
  the longest current row prefix needs at most 1048 bytes including NUL. A proved
  104-byte bound reduction cannot provide adequate margin here. Reducing CSV's
  1024-byte bound is a separate established-contract change and chiefly affects
  formatter stack, not another persistent 1024-byte app object.
- Packing five ternary statuses per byte saves only another 250 bytes over two-bit
  lanes at 5001 slots and adds division/remainder representation complexity. It
  is not the simplest useful choice.
- No evidence supports changing startup/linker/toolchain behavior, borrowing a
  different heap, reducing frame/event capacity, omitting statuses/loss fields or
  assuming external memory. Those are outside this proposal.

Next action: coordinator chooses the explicit read-only versus read+bytesAt API
contract, then independently authors tests and implements the bounded migration.
