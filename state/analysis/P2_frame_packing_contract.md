# D102 lossless frame storage and explicit reads

2026-09-23 under D051/D075, after D101 checkpoint0b1013b. D101-R1 remains
open until final source-bound loader review. This changes storage representation
and the stated read API, not retained evidence, behavior, cadence or capacity.
Read P2_frame_memory_options.md and the original P2_frame_buffer_contract.md.

Keep StoredFrame as the existing26-byte value (25 payload bytes plus PackStatus).
FrameBuffer stores all configured payloads separately from two-bit status lanes,
four statuses per byte. Values OK0/CLAMPED1/INVALID2 are losslessly represented;
all other status values still reject before any stored mutation. Initialize
packed bytes before read-modify-write. Logical reset clears only existing
metadata/counters, with no array sweep. Each visible append rewrites its payload
and status; neighboring lanes and unused final-byte lanes cannot affect a read.
No allocation, extra heap, capacity/rate reduction, clock, new tuning value,
concurrency assumption or changed saturation/order/loss rule is authorized.

## Public read contract (explicitly supersedes D069 item5)

Replace FrameBuffer::at(index) with:

    bool read(std::size_t chronological_index, StoredFrame& output) const;
    const logframe::FrameBytes* bytesAt(std::size_t chronological_index) const;

read returns false outside size, including SIZE_MAX, with output unchanged.
Validate bounds before index arithmetic. Success copies all25 exact raw bytes
and the original accepted status into caller-owned output. That value survives
later reads/appends/resets/destruction. Different caller outputs never alias an
internal scratch object. No read changes source/loss/counters/order.

bytesAt returns a genuine const pointer to that retained payload, oldest first,
or nullptr outside size. Other reads do not invalidate it. Its borrowed lifetime
ends at append/reset/destruction, as before. This preserves the meaningful old
alias-to-append guarantee: first copy the25-byte incoming payload before any
destination mutation, including a full oldest-slot replacement. It does not
invent an adjacent status byte or pointer to reconstructed StoredFrame storage.

## Consumers and existing verification

Dump FRAME_ROW copies one StoredFrame and calls the unchanged CSV formatter;
read failure has the existing formatting-failure result. Inert recorder checksum
still hashes25 payload bytes followed by the reconstructed original status byte,
never packed representation. One-row-per-call and timing/cleanup stay unchanged.
Memory-probe View owns a StoredFrame plus frame_present; its event pointer remains
unchanged. probeQuery reports absent data honestly and retains its passive probe
anchors, fixed96-byte Abi fields and actual sizeof/alignof reporting.

Migrate only current production/bench callers and unlocked test fixtures listed
in P2_frame_memory_options.md. Preserve every old expected byte, count, threshold,
loss/lifecycle/CRC predicate and genuine alias scenario. Use explicit local
storage for compatibility helpers, never hidden scratch globals. Old alias tests
and the deque oracle use bytesAt for genuinely borrowed inputs. CSV nonmutation
tests must reread the real owner, not merely compare a detached local copy.
Keep tests/locked and historical tests/candidates/recorder25.cc/raw snapshots
unchanged; create a named adapted candidate only if needed for a current test.
The expanded26-byte DTO multiplication assertions remain mathematically valid;
do not confuse them with compact internal storage. Do not weaken tests to hide
an implementation failure or change protocol/config to simplify migration.

## Independent acceptance

Author new tests from this contract/public headers before implementation: all
three values in every lane, 3/4 and final-slot boundary, repeated replacements,
adjacent-lane isolation, multiple full wraps, reset/reuse, every rejected3..255
status, SIZE_MAX/output preservation, separate snapshots and genuine borrowed
oldest/interior/newest input. Enforce a representation-size upper bound justified
by payloads+ceil(capacity/4)+bounded metadata; report actual host and target ABI.
Preserve and run existing frame/attempt/rate/CSV/timing tests and full safety
regression under normal and sanitizers, affected memory/recorder tooling and
actual Runtime dump/strict receiver roundtrip. No implementation-derived oracle.

Compile final actual app inert and MATCH without upload, verify exact source,
objects/ELFs/native/startup/imports and new loader peak/allocation order. Count
new code/symbol costs as well as BSS savings. Separate fresh-context reviewer
checks storage, source lifetimes, every migrated test and target evidence.
Only then close D101-R1 if evidence supports it. Refresh the same seven inert
keys only after separate exact staged-source review, with no added upload scope.
LoadedRAM/stack/full800us, physical B8/UART and human gates remain pending.
