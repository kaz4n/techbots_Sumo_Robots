# Fixed current static-image observation: pure host component

This is a software preparation scope within P7, not an MCU-read/upload grant.
Implement only `P7_static_startup_raw/static_capture.py`, pure Python with no I/O,
clock, subprocess, import of hardware collectors or module-import side effects.
No production source, configuration, old helper/test or upload policy changes.
The purpose is to plan and interpret a later finite passive MEM-AP capture of
the exact existing static image, without applying the old dynamic heap model.

## Public interface

`read_plan() -> tuple[tuple[str, int, int], ...]` returns exactly18 immutable
requests in this order. Each triple is name, absolute address, byte count:

1. `before.loader.0` through `.4`: read263680 bytes from0x08000000, divided
   into65536-byte blocks and the final1536 bytes.
2. `before.sketch.0` and `.1`: read93096 bytes from0x08100000, divided into
   65536 and27560 bytes.
3. `first.runtime`, 0x2003bc98,28; then `first.transaction`,0x2003b2b0,24.
4. `second.runtime` and `second.transaction`, the same addresses and lengths.
5. `after.sketch.0` and `.1`, followed by `after.loader.0` through `.4`, using
   the same ranges as their before copies.

Total requested bytes713656. The later collector must place a bounded, recorded
interval between sample pairs; this pure component does not wait or run tools.
No other address, whole-Runtime read, peripheral read, LLEXT walk or heap sample.

`analyze_capture(reads, expected_loader, expected_sketch) -> dict` takes a list
or tuple of exactly18 triples `(name, address, data)`, in the plan's exact order.
Names must be actual strings, addresses actual ints (not bool/float), data actual
bytes of the exact planned length. Each triple must be a list or tuple of3.
References must be actual bytes of263680 and93096 bytes respectively. Any shape,
type, length, count, duplicate/reordered label or address mismatch raises ValueError.
Neither arguments nor their contained objects may be modified.
Scalar strings/ints/bytes require their exact built-in types; container admission
uses list/tuple semantics (subclasses allowed). A phase FAULT with numeric fault0
still follows SAMPLED_FAULT below and has no epoch_delta.

Return exactly these keys:

- `flash`: dictionary with `before_loader`, `before_sketch`, `after_loader`,
  `after_sketch`, each an actual bool from complete byte comparison.
- `observation`: status below.
- `runtime`, `transaction`: lists of two decoded dictionaries each, or empty lists if
  any flash comparison fails. Never interpret fixed RAM as this app after a
  flash mismatch.
- `epoch_delta`: None unless all prefixes are valid and both Runtime phases
  are RUNNING with no sampled Runtime or Transaction fault; then modulo2^32
  difference of the epoch words, including0 and values at/above2^31.
- `errors`: list of strings naming malformed prefix fields, empty otherwise.

Reference identity is intentionally the caller's responsibility: the later
collector must bind loader SHA6b2ffd3a and static package SHA5f08afe0 before
calling this pure comparator. Synthetic host fixtures are not native evidence.

## Literal public-prefix layout

Runtime prefix28 bytes: phase0, fault1, flags at2..6 named `fresh`,
`initialization_complete`, `raw_lines`, `imu_expired`, `calibration_interrupted`.
Little-endian uint32 words at8,12,16,20,24 are `next_release_us`,
`missed_releases`, `epochs`, `service_passes`, `maximum_execution_us`.
Phase names0..4: NOT_STARTED,RUNNING,STOPPED,FAULT,STOP_OBSERVING.
Fault names0..5: NONE,PORT,CLOCK,SERVICE_LIMIT,TRANSACTION,PROJECTION.

Transaction prefix24 bytes: phase0,fault1, flags2..4 named `decision_made`,
`finished`, `timing_valid`; words8,12,16,20 named `started_us`, `decision_us`,
`completed_us`, `execution_us`. Phase names0..4:
NOT_INITIALIZED,IDLE,ACQUIRING,DECIDED,FAULT. Fault names0..6:
NONE,SETUP,ORDER,CLOCK,IDENTITY,RECEIPT,ABORTED.

Every decoded dictionary has raw integer phase/fault, phase_name/fault_name
(`UNKNOWN` for out-of-range values), all named raw integer flags/words and
`raw_hex` of the entire prefix (lowercase bytes.hex(), no separator). No other keys. Enum values outside the stated
ranges and flags other than0/1 add `runtime[i].field` or `transaction[i].field`
to errors, ordered by pair0 then1, Runtime then Transaction, phase/fault/flags.
Padding bytes are preserved in raw_hex but are not semantic fields or errors.

## Observation priority and limits

1. Any flash mismatch: `FLASH_MISMATCH`, no diagnostics decoded, deltaNone.
2. Any malformed prefix field: `MALFORMED_SAMPLES`, keep decoded raw values,
   deltaNone.
3. Any nonzero Runtime or Transaction fault, or either phase named FAULT:
   `SAMPLED_FAULT`, deltaNone.
4. Both Runtime phases RUNNING and delta in[1,2^31): `RUNNING_COUNTER_ADVANCED`.
5. Otherwise: `NO_RUNNING_PROGRESS`. If both phases are RUNNING, retain delta;
   otherwise deltaNone. A delta at/above2^31 is not positive progress.

Samples are live and non-atomic, not synchronized whole-object snapshots.
Advancing sampled epochs support restricted execution progress only; they do
not prove absence of intervening resets, initialization readiness, physical
outputs, memory/stack headroom, calibrated timing, full-source WCET or a gate.
No inferred coherence requirement is added for changing transaction flags/times.

Independent tests derive from this contract/public headers, not implementation.
Cover exact plan bounds/order/total, argument rejection, all four flash mismatch
positions, literal little-endian fields, raw padding, every enum/flag boundary,
status priority, no-progress/fault cases, modulo wrap and half-range boundary,
and input preservation. Freeze the new tests before first implementation execution;
keep fixtures in memory and use Python-B. A separate review follows real results.
