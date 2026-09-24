# Pure static capture implementation review

25 September 2026, Asia/Dubai. **SCOPED PASS**; no open BLOCKER, MAJOR or
MINOR in the current pure component. Separate fresh-context same-model review
of implementation, independent tests and actual first-run receipts. This is
host preparation under D-152, not permission for an MCU capture or upload.

Read AGENTS.md, current PROGRESS, D-152, the active P7 prompt, PLAN section 3,
the contract, both public report headers and the independent test-author note.
Local date is Friday 25 September; the original schedule's P1/P2 expectations
do not establish physical acceptance of this P7 preparation.

## Exact reviewed inputs

| Input | SHA256 |
|---|---|
| [Current contract](../analysis/P7_static_capture_contract.md) | `58959d7caf34cc59ddcbbaaf8d4165e4e5025d0996ab448bdac639af5ea88c7a` |
| [Implementation](../analysis/P7_static_startup_raw/static_capture.py) | `b7ab979d019814c7d66258346891457e7f09e7698896d8dbf00469f3c58e24fc` |
| [Independent tests](../analysis/P7_static_startup_raw/test_static_capture.py) | `bcb6300574e55bd18c224ed916208239264b5452bbccd1fb14a228606b84a02d` |
| [Author note](../analysis/P7_static_startup_raw/tests_author_note.md) | `becee9f4bdce94ae496ba976af2e4233f954ac4ac0aa264760c3a37f83b54330` |
| [Freeze receipt](../analysis/P7_static_startup_raw/host_freeze.json) | `1b35b7ef50d0a076c0ff2bcaf36ae275196fca636f3ee67844fb2bc1cd07c8d6` |
| [First execution](../analysis/P7_static_startup_raw/host_first.json) | `c26690530387fadb7c8a4be72e29f2c6d0d291176ac24345f5928fb5bbe07e04` |

The freeze at `2026-09-24T23:09:31.299317Z` precedes first execution at
`23:09:41.787613Z`. The recorded Python 3.13 command used `-B`, exited zero,
and passed all 37 methods in 0.206 seconds. The receipt reports unchanged pins;
this review independently recomputed all six hashes above. Source and tests
were committed in `e7f88263`; no implementation repair or oracle edit follows
the first execution in the reviewed material. I did not repeat the suite.

## Assessment

- **Scope and simplicity:** the 111-line implementation contains seven short
  functions (maximum 17 physical lines), no imports, I/O, clock, subprocess,
  hardware collector, top-level call or mutable module state. It requires no
  new dependencies and changes no firmware/configuration/old helper. The
  immutable plan has exactly 18 requests totaling 713,656 bytes in the required
  bracket order, including the two fixed public-prefix pairs.
- **Admission and identity:** references and every read are validated before
  interpretation. Exact scalar types reject bool/int/bytes subclasses and
  coercions; list/tuple semantics admit the specified containers. Names,
  addresses, order and lengths must match the plan. Complete joined image
  bytes produce four independent built-in bools. Any mismatch leaves both
  diagnostic lists and errors empty, with delta None; no RAM interpretation
  can survive a failed bracket comparison.
- **Literal decoding:** Runtime and Transaction enums/field order match their
  public headers and the contract. All flags and little-endian words remain
  raw integers; raw_hex includes padding. Unknown enums and invalid flags
  produce the exact pair-then-Runtime/Transaction-then-phase/fault/flags error
  order, while preserving decoded values and adding no coherence rules.
- **Classification:** malformed fields precede sampled faults. Every nonzero
  fault and either FAULT phase suppresses epoch_delta, including fault zero.
  Only two valid RUNNING Runtime phases without any sampled fault obtain the
  uint32 modular difference. Zero and values at/above the half range remain
  NO_RUNNING_PROGRESS with their delta retained; ordinary wrap can advance.
  Transaction readiness/timing and Runtime readiness flags add no inferred
  qualification beyond the explicit contract.
- **Preservation and coverage:** no assignment targets caller objects, and
  each result has fresh dictionaries/lists. The independent suite exercises
  all chunk endpoints and mismatch combinations, strict validation, exact
  decoded layouts/types, enum/flag boundaries, ordered errors, all priorities,
  wrap/half-range boundaries and input/result independence. This covers the
  public behavior rather than requiring a private implementation structure.

The original caller-reference paragraph had a MAJOR identity error documented
in the separate [reference review](P7_static_capture_reference_review.md).
The current contract corrects it to the ELF-derived `e9322826` loader image;
the original contract and original design review remain in `6d45e3b5`.
That correction changes no pure API or synthetic oracle. This implementation
review checks the corrected prose and its boundary; the separate reference
review supplies the independent ELF derivation and historical-byte comparison.

The comparator accepts caller-supplied references and cannot establish their
provenance, current MCU identity, sample continuity, atomicity, absence of reset,
initialization readiness, physical outputs, free RAM, WCET or a human gate.
Those limits are explicit and are not weakened by the passing host receipt.

Only this review file was written. No implementation import, test execution,
board command, build, upload, reset, private fixture, binary or cache was created
by this reviewer. No cleanup is needed. Next: coordinator records host closure;
any actual capture/reference binding remains a separate bounded scope.
