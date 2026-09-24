# D118 independent public-test preflight

Reviewed draft SHA256
`ee0d63b1a4d0a8f65bc01213c6177933ceb7cead989f3fd97abf54a475259064`,
2026-09-24. This is a public-contract preflight, not adoption or executable test
freeze. No new collector implementation was read, imported or executed. Earlier
app implementation inspection for eligibility is disclosed; independence applies
to the prospective capture module, not to the whole repository. Only this report
was written. No board action, production/test change or full-pool fixture was made.

**The literal ABI, bounded read plan and live-observation distinctions are
testable. Four small public-seam choices below should be fixed before executable
expectations are frozen.** No firmware or generic transport framework is needed.

## Confirmed public oracles

`src/app/runtime.h` and `src/app/transaction.h` agree with every declared phase,
fault and prefix field. The saved debug excerpt independently supplies offsets:
Transaction prefix 24 bytes at Runtime+162128; Runtime prefix 28 bytes at+164664.
Saved final ELF derivation agrees with raw ET_REL runtime offset0, size166376,
BSS section8/size167272/alignment8/address87872/file offset92384 and the exact
symbol attributes. The 16-section table's file offset175408 added to flash base
is0x0812ad30. Neither the debug ELF nor a linked-looking symbol address becomes
an upload image or raw RAM read address.

The corrected package and ELF are each176048 bytes. The five loader chunks and
three sketch chunks per sweep, plus32 pool chunks, give48 memory reads before
metadata/app views. Adding2 descriptors+2 lists+6 node reads+4 app-prefix reads
gives62 reads; four fixed metadata commands give66 commands. Byte arithmetic is
527360+352096+524288+48+16+1176+104=1405088. Stable absence omits104 bytes/four
reads, producing the stated maximum58 reads/62 commands/1404984 bytes. An empty
list additionally omits the six node reads. The newly selected64/80 ceilings are
separate from the old contracts and do not license extra diagnostic purposes.

The used-allocation interval allows alignment slack while excluding the chunk
header. Whole-node, whole-BSS, whole-Runtime and prefix containment can all be
tested at exact left/right boundaries, including a BSS overrun despite a fitting
Runtime. The final traversal follows only original addresses and compares all
node/list bytes. This admits no speculative pointer scan.

The unchanged heap decoder's existing public tests expose literal all-free,
all-used and mixed layouts, including 8-byte units, 4-byte headers, exact chunk
metadata and independently stated accounting. Both helper hashes match the
draft. Public fixtures can create valid containing allocations in RAM, and then
embed unrelated nodes, selected nodes and mutable app payload without changing
the allocator metadata. No private decoder or collector state needs seeding.

The decoder correctly avoids cross-object consistency inventions. All bool
combinations within0/1, arbitrary stored timestamps, nonzero misses and maximum
execution counters are retained as live samples. A transient DECIDED/unfinished
Transaction is not corruption. RUNNING counter advancement is an observation,
not proof of initialization, healthy receipts, zero misses or WCET. Equality,
saturation and decreases do not imply wrap/progress. A valid firmware fault or
stable absence can be CAPTURED while CLI exits1. Malformed sample content can
also be retained after otherwise complete collection.

## Choices needed before executable freeze

1. **Minimal collector result shapes and failure seam.** The pure sample decoder
   has exact keys; the collector report and intermediate APIs currently do not.
   In particular, `extension` could be a string or an object, `heap` could expose
   one report or a before/after pair, and count/layout key names are unstated.
   Specify the minimum stable keys and types used by tests/CLI: extension status,
   heap before/after/comparison, actual read/command/requested-byte counts,
   layout, app_samples and top-level errors. Also state `(ELF, ZSK)` tuple order,
   the literal `read_layout` result, whether `collect` returns the same report
   object, and whether transport/contract failures raise while preserving it.
   The existing D114 public seam is a sufficient model: ValueError for contract
   refusals, native launch/subprocess failures propagated, successful collection
   returns its populated report even for valid fault/absence/sample errors;
   main persists `capture.json`, prints the final JSON and returns the specified
   exit status. No stable exception-message text is necessary. Accept equivalent
   Path/string artifact arguments or state the exact required public type.

2. **Transaction fault flag under malformed prefixes.** Define
   `transaction_fault_sampled` for a null Transaction slot and unknown raw phase/
   fault values. A simple literal rule is boolean OR over non-null decoded
   dictionaries of `(phase == 4 or fault != 0)`, with null contributing false;
   unknown raw nonzero values remain marked malformed and cannot supersede
   MALFORMED_SAMPLE or enable CLI success. Alternatively choose a known-enum-only
   rule explicitly. Tests must not invent one. Within each sample, confirm enum
   checks precede bool checks in declaration order, preserving the already fixed
   runtime[0], transaction[0], runtime[1], transaction[1] acquisition order.

3. **Deadline anchor and equality.** State when the600-second lifetime starts
   (Capture construction is a simple existing precedent; clock reads are passive
   observations, not process/memory actions), and the exact refusal boundary
   before and after a returned command. Specify how a successful subprocess that
   returns at/after the total deadline is recorded, and whether validation time
   before the first command counts. Every subprocess timeout must remain bounded
   by min(30, remaining); a deadline refusal must launch no next command and keep
   prior stdout/stderr/partial blobs. Tests should cover the exact boundary rather
   than choose the meaning of the current `<=600` prose. The fixed sequence makes
   64-read/80-command caps unreachable in an admitted successful plan; test the
   actual62/66 maximum plus replay/out-of-order refusal, without private counters
   or artificial repeated metadata commands.

4. **Unrelated node names/fields.** The draft requires a NUL in the16-byte name
   but specifies no encoding. Recommend comparing bytes before the first NUL
   exactly to `b'sketch'`; other NUL-terminated byte names are nonmatches, without
   an invented UTF-8/ASCII refusal. State whether unrelated nodes' BSS/header
   fields are opaque (recommended: no dereference or target-layout constraints)
   or require any generic bool validation. Their admitted link/name/allocation
   checks and all196-byte after-equality remain mandatory either way.

These choices do not change the approved source, grants, addresses, limits,
node count or observed-state scope. Separate run ID/approval/guard choices can
remain deferred while capture software is prepared, provided no execution route
is inferred from this preflight.

## Independent literal executable plan after adoption

- Pure decoder vectors: exact four-prefix literal bytes, all enum endpoints and
  invalid values, each bool offset, nonzero/changing padding, wrong lengths and
  non-bytes inputs. Assert raw preservation, exact dictionaries/error paths,
  acquired-order diagnostics, malformed precedence and the chosen fault-flag
  rule. Include advancing/equal/saturated/decreasing counters; all normal
  transient Transaction combinations; Runtime faults in either sample.
- Collector fixtures: run the actual public methods with controlled standard
  subprocess/clock/filesystem seams. Use exact independent ELF metadata text,
  coherent pinned-loader bytes and existing pure helper contracts. Preserve
  regular-file/no-symlink checks when substituting file hashes; do not remove
  delegated guards. No collector private state or ad hoc address escape.
- Exact positive traces: one sketch, three nodes with one sketch, empty list and
  three unrelated nodes. Match every argv, label, range, byte length and order;
  verify62/66 maximum and stable-absence omissions. Decode both actual generated
  pool buffers through the unchanged helper, comparing expected accounting.
- Negative traces: identity/hash/ELF duplicates and every pinned field; whole
  BSS/Runtime/prefix/allocation escapes, bad alignment and overflow; unreadable,
  free or overlapping nodes; cycles, wrong tail, fourth node, duplicate sketch;
  changed descriptor/list/node/allocator metadata; all flash-before/after failures.
  Verify immediate suppression of subsequent private reads and no retries.
- Distinguish changing allocated payload from changing allocator metadata;
  stable absence from an invalid/ambiguous graph; valid firmware fault and
  malformed app bytes from collection transport failure. Keep all original raw
  evidence and classify CLI exit0/1/2 from the adopted literal rules.
- Command/CLI boundaries: direct arbitrary argv, unused/spent/out-of-order read
  purposes, wrong region/address/size, output collisions/symlinks, launch error,
  nonzero status, timeout and short output. Each deliberate caller violation
  starts a separate collection; recovery after violation is not assumed.

Build large valid pool/flash vectors in isolated `/dev/shm` workspaces from small
literal fixture recipes, retain hashes and failure receipts, and avoid persisting
many full-buffer duplicates on the nearly full host volume. Freeze the executable
source before its first module import/implementation execution. Existing D104,
D114, heap-helper tests and helper bytes remain unchanged.

## Final coordinator-selection recheck

Reviewed the normative appendix in contract SHA256
`9dbcf627c4bcfb3e8376075df74d6f215fba22efe4446b52ad18c00d8419856b`
on 2026-09-24 against the public Runtime/Transaction declarations and the
previously checked literal ABI and read-plan evidence. **PASS: no material
public-oracle blocker remains.** The original four recommendations above remain
as preflight history; the coordinator selections below govern later tests.

- The outer report now has stable minimum keys and types, literal layout fields,
  `(ELF, ZSK)` return order and equivalent Path/string input semantics. Extra
  diagnostics remain allowed. `extension.sketch` is the intended null-or-object
  mapping with integer node_address, bss_address and runtime_address; a small
  wording clarification to say "object" explicitly was sent to the coordinator.
- `collect` returns the original report on ordinary collection failure, preserving
  counts/artifacts and actual exception-class diagnostics. This supersedes the
  initial propagation recommendation. A second collection refuses before action
  without replacing the first report; direct run/read outside admission refuses.
  Completed collection of absent/fault/malformed sample observations remains
  distinct from failed collection, and CLI success requires every stated field.
- Construction is wholly passive, including no clock observation. The sole
  collection entry starts lifetime before identity/filesystem work; validation
  time counts. Admission and completion reject exactly600 seconds and beyond,
  including late exit0. Attempts count before invocation; preserved late output
  cannot authorize the next command. The finite-purpose plan remains62/66, so
  synthetic repeated commands are unnecessary to claim unreachably high caps.
- Transaction fault is known-evidence tri-state: known FAULT or known nonzero
  fault wins true; otherwise any malformed Transaction sample gives null; only
  two well-formed fault-free samples give false. Unknown enum alone is not a
  firmware fault. Runtime MALFORMED_SAMPLE precedence remains unchanged. Enum
  checks then ordered bool checks are now literal, without same-epoch claims.
- Raw pre-NUL bytes select exactly b'sketch'; other terminated names, including
  non-UTF8, are nonmatches. Unrelated BSS/header fields remain opaque, while
  link/name/allocation validation and full-node equality remain mandatory.

These choices are independently observable through the declared public methods,
literal byte fixtures and standard subprocess/clock/filesystem substitutes.
The final recheck found no contradiction with prefix sizes, public enum values,
whole-allocation checks, purpose order, stable absence, captured firmware faults,
or the explicit nonterminal/live-read limitations. Output/report-write failure
must remain nonzero; tests need not invent exception-message text or extra
metadata schemas. No collector body was read or executed, no executable test was
created or run, and no board action occurred. Adoption, executable freeze and
any separately reviewed actual run remain subsequent coordinator decisions.

Final wording-only binding: coordinator clarified extension.sketch as a null-or-
object mapping in contract SHA256
`06377731b7565116ed74c89823e3157e1e7e3ab135dec0e08a08d0c0fc4c338e`.
This changes no oracle or PASS conclusion above. D118 adoption and independent
executable authoring were subsequently assigned by the coordinator; no execution
is implied by this hash binding.
