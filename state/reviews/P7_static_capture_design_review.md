# Static capture pure-component design review

25 September 2026, Asia/Dubai. **SCOPED DESIGN PASS**; no open BLOCKER,
MAJOR or MINOR. Separate fresh-context same-model review, not implementation
validation, an MCU observation grant or a physical/human phase gate.

Reviewed [contract](../analysis/P7_static_capture_contract.md) SHA256
`ee1bb8d4acd969fa16330f2e7a55bf26daac71a6dbe4f6922c730f46bcb96fc3`.
Read AGENTS.md, current PROGRESS, relevant FACTS/decisions, the active P7 prompt
and PLAN section 3. Local date is Friday 25 September; the plan's original
P1/P2 schedule does not establish acceptance of the current P7 preparation.

## Evidence and findings

- **Finite plan:** 18 requests and 713,656 bytes, independently recomputed as
  `2 * (263680 + 93096) + 2 * (28 + 24)`. Flash intervals end exclusively at
  `0x08040600` and `0x08116ba8`. Both complete images bracket the four RAM
  prefix requests; the contract permits no other address or hardware operation.
- **Literal ABI:** [runtime.h](../../src/app/runtime.h:52) and
  [transaction.h](../../src/app/transaction.h:9) agree with all enum names,
  numeric ranges and field order. Retained D149
  [GDB output](../analysis/P7_static_link_probe_raw/native_abi/0003.json),
  SHA256 `a7c0c4797414e396e19d981b54e104d250cd77a32ac25e221f182e85c9da0994`,
  confirms the one-byte fields, uint32 offsets and padding. The
  [result](../analysis/P7_static_link_probe_raw/native_abi/result.json) gives
  Runtime report offset 164664, transaction offset 152 and Transaction report
  offset 161976. With the retained [runtime symbol](../analysis/P7_static_entry_audit.md:87)
  at `0x20013960`, these derive exactly `0x2003bc98` and `0x2003b2b0`.
  These are image-specific file observations, not current RAM observations.
- **Input/output strictness:** count, order, names, exact scalar built-in types,
  addresses and lengths are explicit; invalid input raises ValueError. Immutable
  reference bytes and input preservation are required. Decoded results preserve
  raw flags/words and padding, with deterministic error ordering and no extra
  keys. List-container and lowercase unseparated hex clarifications were adopted
  before test freeze; no remaining interface ambiguity was found in this scope.
- **Priority:** complete flash mismatch suppresses RAM interpretation; malformed
  fields precede sampled faults; every nonzero fault or FAULT phase suppresses
  delta, including FAULT with numeric fault zero. Only two valid RUNNING samples
  without sampled faults produce a modulo uint32 delta. Zero and half-range-or-
  larger deltas cannot receive the counter-advanced status; wrap remains covered.
- **Honesty:** the component compares caller-supplied bytes and cannot prove
  reference identity, capture provenance, continuity, absence of reset, coherent
  whole-object state, initialization readiness, physical outputs or timing/RAM
  qualification. The contract states these boundaries and leaves reference hash
  binding and bounded collection timing to a separately scoped collector.

No board command, compiler, implementation import or test execution was performed.
Only this new review file was written. No generated fixture, binary, cache or
scratch copy needs cleanup. Next: independent contract/header-derived tests,
freeze before first implementation execution, then implementation/results review.
