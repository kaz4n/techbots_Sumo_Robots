# D136 private companion-analysis review

Current status: PASS for scoped D136 offline software on final source `8e002c6f…` (`5277dec0`).
All reported findings below are closed; final source/receipt review is at the end.
Earlier preparation and pause checkpoints are retained as historical evidence.
Provenance: separate same-model reviewer reusing prior P4/D134/design context; not fresh gate review or cross-model. Only review/raw ownership; no production, public test, ledger, compiler or board changes.

Nineteen private spec-derived methods and a hash-bound runner are frozen in
`P5_abort_analysis_review_raw/private_freeze.json` before reading any future
companion implementation or new public test bodies. The adopted public
`decode_cue(value, mode)` seam is included. Coverage and generation provenance
are recorded in `P5_abort_analysis_review_raw/freeze.md`.

All generated evidence is temporary and synthetic, including deliberately
fabricated hardware-origin declarations. No probe/import or compiler/board
execution has occurred. Source identity, full token/EN producer guarantees,
physical ten-trial completeness, target fit and phase gates remain separate.

Next action: coordinator freezes the implementation/public expectations, then
authorizes private runner execution with the exact implementation hash. Preserve
first failures and unchanged original oracles before any justified correction.

## Independent metadata binding check, 2026-09-24

The separate D135 reviewer checked the original 19 methods against the D136
closure/loss clarification: no conflicting expectation; probes remain unchanged.
The first freeze is preserved as `private_freeze_first.json`; only its contract
dependency hash changed. See `contract_binding_update.json` for exact bindings.
These private methods do not directly cover every clarified closure/aggregate-only
loss case. Complementary public/source review remains required. No imports or
execution occurred; implementation acceptance and first execution remain pending.

Usage-guide source review: no material contradiction with D136; M0, timing bound
and physical/permission limits are correct. Nonblocking schema-detail suggestions
are recorded in `P5_abort_analysis_review_raw/usage_doc_review_first.json`.
Implementation body remains unread pending the coordinator's first source hash.

## User-requested pause checkpoint, 2026-09-24

Review stopped before completion. First implementation `c0afe321`, SHA256
`9891c3eaa8a283d918d1e253a691c55c3d7d8ad3b9574eefcc14452f1e8b7843`.
Retained first results: public 74/74 PASS; private 18/19 PASS, one failure.
No implementation, oracle, runner or first-receipt edit was made by this reviewer.

1. **Private injection mismatch, narrow correction not yet authorized/executed.**
   `private_probes.py:475` patches its conventional imported CSV module, while
   `analyze_opener_abort.py:16-20,549` loads and calls a distinct module object
   from the same unchanged validator file, following unchanged D130's pattern.
   The callback therefore never mutates the fixture; the zero call count does
   not demonstrate a binding defect. `_snapshot:340-345` checks bytes/hash/rows.
   Frozen public `validated_then:239-264` intercepts the actual dependency by
   source identity and its event/summary same-size restored-mtime tests pass.
   Preserve the original 19-case source and failure before any harness correction;
   retain mutation stimulus, exact call-count and INVALID/cleared-endpoint assertions.
2. **Potential MAJOR: unsupported duplicate config declaration admitted.**
   `_config_value:215-231` catches extra assignment, semicolon or array forms,
   but its extra-identifier check misses direct/list initialization. Appending
   `namespace duplicate { inline constexpr std::uint32_t TICK_US{2000U}; }`
   after the seven canonical declarations leaves one regex match and passes
   both extra-use rejection predicates. Ordinary reads are allowed by D136;
   duplicate/unsupported declarations are not. This is source-derived evidence,
   not an executed reproduction; independent adjudication remains pending.

Exact next step after user resume: preserve/adjudicate the duplicate-declaration
case with a bounded coordinator-owned probe, then decide any narrow production
fix and independently approved test-harness correction. Complete the remaining
source/contract review and rerun source-bound public/private and prior regressions.
No D136 acceptance verdict, further execution or permission follows this pause.

## D136 test 16 adjudication after resume

The original failure is a proven injection mismatch: the private conventional
`CSV` module differs from the file-loaded `csv_validator` actually called at
`analyze_opener_abort.py:549`. No fixture mutation occurred. This conclusion
uses import/call-site evidence, not the zero call count alone; it does not
establish that all snapshot-binding behavior is correct.

Before correction or execution, preserved original probe bytes in
`P5_abort_analysis_review_raw/private_probes_first.py` and the active freeze in
`private_freeze_before_harness.json`. The earlier `private_freeze_first.json`
and both original first-execution receipts remain unchanged. Detailed proof and
the narrow authorized correction are recorded in `private_harness_adjudication.json`.
Only test 16's dependency interception may change: load one subject, verify the
validator file identity, patch that actual dependency, then retain every original
mutation, exact one-call, INVALID and cleared-endpoint assertion. No execution yet.

The authorized harness correction is now frozen, still unexecuted by this reviewer.
Probe SHA256 `b270aafdf3a0ca43027912e4273104cf292208cc1c99d20aba3f2e8a7139b303`;
active freeze `5a27ca331c9380dc410843d9610efe41f1308083ff089dae65d57186c2a9faa1`.
`private_harness_correction.json` records the before/after bindings. The runner,
other 18 methods and every original test 16 assertion remain unchanged.

The first-source contract review is complete, with the declaration finding open.
It also affects comma declarators such as `OTHER = 1U, TICK_US{2000U}`: their
prefix defeats the original declaration predicate. The coordinator reports
independently frozen pre-fix reproductions and owns the repair. No additional
material finding arose in cue grammar, chronology, actual declared route-state
checks, snapshot/manifest binding, loss/owner precedence or aggregation; see
`source_review_first.json`. Final D136 verdict remains PENDING exact repair
review, corrected-private execution and bound regression receipts.

## First repair review: MAJOR remains open

Reviewed source `02b2180a1014a7b78243101585730ab66849a3803b7336bbab407124d7e72ab4`.
The bounded declaration helper closes the original reproduced forms. Verified
receipt/log hashes for public 74, private 19 and declaration 8 PASS on this source;
corrected private 19 also passes unchanged first source. Existing 112 regressions
passed first source with unchanged dependencies. These results remain preserved.

`_extra_declarator` still misses `inline constexpr std::uint32_t (TICK_US) = 2000U;`
and extra list declarations prefixed with `[[maybe_unused]]` or `alignas(8)`.
Each can accompany the canonical constant in another namespace and escape both
extra-declaration predicates. This is the same open MAJOR admission defect,
source-derived and not executed by this reviewer. Sent concrete cases to the
coordinator before adoption; independent probes and bounded repair remain needed.
`source_fix1_review.json` binds the receipts and exact examples. No final PASS.

## Second repair review: two bounded cases remain

Source `1c124dfe816f90faf694c1820376b6a6a5a0cf60f7e8d1e84558a82914195fd0`
closes the preceding parenthesized/leading-decoration examples. Public 74,
private 19 and declaration 15 methods pass; receipt/log hashes are verified in
`source_fix2_review.json`. Canonical declaration spelling remains strict.

The same admission finding remains open for `unsigned short (TICK_US) = 2000U`:
the finite builtin-type alternative omits terminal `short`. Also, the new
decoration helper mistakes the partial prefix before a name for a malformed full
decoration: `alignas(MODE_ARC_ENABLED) inline constexpr char ordinary = 0;`
is a valid ordinary read with canonical MODE_ARC_ENABLED=1, but is rejected.
Both examples were source-derived and sent to the coordinator before adoption.
No reviewer execution or implementation/public-test edit; final verdict pending.

## Alignment-read/builtin repair review

Source `65cba907d3a425e24706b6ca44a6e4a671971d9c75f5955f7bfe46342cf9d5f1`
changes only three declaration helpers and closes the two preceding cases.
Verified public 74/private 19 PASS receipts; supplemental discovery failed
before tests because the declaration helper was imported from the other copy's
directory. Preserve that runner-location receipt and rerun byte-exact tests from
one official directory. See `source_read_fix_review.json` for the bindings.

The parenthesized qualified-type predicate still omits trailing cv and a leading
global qualifier: `std::uint32_t const (TICK_US) = 2000U` and
`::std::uint32_t (TICK_US) = 2000U` are concrete extra declarations not recognized.
These finite cases were forwarded for independent adjudication before a verdict.
No reviewer execution or production/public-test edits.

At coordinator request, remaining concrete single-qualified-type cases were
batched in `qualified_type_batch.json`: global qualification, trailing cv,
cv-qualified pointers inside/outside parentheses and pointer/reference tokens
interleaved with balanced name parentheses. Positive controls retain ordinary
reads while declaring another name. No template/function/member-pointer or
general-C++ parser expansion is proposed. All cases remain source-derived here;
the independent author/coordinator own pre-fix reproduction and any repair.

## Final scoped D136 verdict — PASS

No open material finding remains in the adopted offline analyzer and the reviewed
finite input boundary. Final source SHA256:
`8e002c6f627e1cb39af94d244a3ba62b817967e9d0e8ceac7497f9f6eb52c4d2`.

Verified terminal results and exact source/test/log bindings: 93 public methods
PASS (3.721 s), 19 private methods PASS (1.841 s). The unchanged legacy analyzer/
CSV dependencies retain their 112-method PASS. Independently rehashed all 694
prior inputs with zero mismatches, including all 43 protected locked files.
Original public 74 and private 19 expectations, first failures and later
independently frozen regression cases remain preserved; the sole private harness
correction changes dependency interception while retaining every original assertion.

The final type-head delta closes the reported global/CV/pointer/reference forms
without changing canonical extraction, trace/report logic or ordinary-read intent.
This is a finite lexical admission utility, not a C++ parser, preprocessor,
compiler or blanket assertion about arbitrary C++ source. Discovery-path failure
and a transient post-test README byte/EOL drift were preserved/adjudicated; the
README was restored byte-exact and the final 694-input check passed.

`P5_abort_analysis_review_raw/final_receipt_review.json` binds the evidence;
SHA256 `fcbb4dbcd9623b3627f308297ca33e4097c3a1282e8ea8c6c1ff95931a28fcce`.
This is separate-context same-model review with reused context, not cross-model
or fresh phase-gate review. The reviewer executed no tests, compiler or board action.
All evidence is synthetic local software evidence. Deployed-image/producer runtime,
transport, native fit, calibrated clock, WCET, physical 10/10, motor permission
and human phase gates remain outside this PASS; acceptance booleans stay false.
