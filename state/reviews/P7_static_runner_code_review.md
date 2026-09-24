# D143 static runner code review

25 September 2026. Reused-context, separate same-model review of the scoped
runner; not a fresh-context, cross-model or human gate review. Read-only source,
contract, hash and AST inspection only. No runner/helper import, test execution,
board command, compiler, upload or reset was performed for this review.

## Reviewed identities

- Earliest runner inspected: `24db46d8707e2fec31a4c508d886d9efde73da8514f27a43ba60415efa73de33`.
- Current runner inspected: `2a9c5e2cef47e71c63788567d1ee2fe3b8d165bab61df07aa62313dcdf713698`
  (`state/analysis/P7_static_link_probe_raw/run_static_probe.py`, 32,912 bytes).
- Runner contract: `35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7`.
- Remote companion: `a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39`.
- Bootstrap template: `a6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419`.
- Helper currently pinned: `fa209bee067f416f7f7619e350562806b333b4d3e6faf902a7f51878eb231e1b`;
  its identity was checked, not its complete implementation reviewed here.

All 17 runner literal file pins matched on the read-only check. Production
board/common policy and frozen D141/D142 sources retain their established hashes.
AST inspection found 56 functions, maximum 42 lines, below the 60-line limit.

## Findings and disposition

1. **MAJOR, closed by source inspection before execution:** initial
   `load_module` used `SourceFileLoader.exec_module` after hashing source. That
   loader can execute an existing bytecode cache instead of the pinned bytes;
   `-B` alone prevents writes, not cache reads. The frozen D141 policy also uses
   that loader for its nested common-policy import. Current lines149-178 load
   direct dependencies from captured verified bytes. Around the unchanged nested
   import they require `-B`, absence of the current interpreter's exact cache
   path (including dangling links), canonical nonsymlink source ancestry and
   exact source hash. This meets the adopted ordinary drift checks; it does not
   claim adversarial swap-and-restore attestation. Independent cache/drift tests
   remain required before execution acceptance.

2. **MINOR, closed by source inspection before execution:** initial dispatch
   serialized arbitrary normal-result output before validating the result.
   An object-valued stdout could cause `TypeError`/partial JSON instead of the
   specified malformed-response `ValueError`. Current lines326-331 and398-408
   retain safe observed text/null/bytes or explicit Python type metadata and
   reject the malformed result. This is a validation-error receipt, not invented
   command output.

3. **MAJOR, open:** current dispatch lines406-410 sets `terminal=True` only
   after the completion receipt write. If a well-formed zero compile result is
   returned but this write raises, execute lines601-605 takes local-only checks
   and the result is UNKNOWN. D143 runner contract lines160-163 and178-185 make
   that returned zero result the normal terminal boundary, requiring all five
   postchecks even when later validation fails. Smallest correction: establish
   terminal status immediately upon recognizing the well-formed zero compile
   result, before the completion write. The write must still fail the run;
   preserve its error and perform the terminal postcheck group, never collection
   or a retry. Add a focused completion-write-failure test before execution.

The coordinator separately found and repaired completion-write masking of an
actual callback exception, an optional checks.json write that could mask the
primary failure, bool/int aliasing in nested chunk FileRecord comparison, and
postchecks incorrectly following a failure before compile dispatch. Current
lines387-397, 547-560, 583-586 and601-603 contain the corresponding corrections;
their behavior still awaits independent tests. These are coordinator findings,
not independent reviewer discoveries.

## Scope conclusion

Apart from finding3, inspected code agrees with the fixed command order and
timeouts, one query/compile attempt anchors, fresh output checks, conservative
unknown-completion boundary, independent terminal/final postchecks, baseline
artifact identities, bounded final-ELF collection and D142 report acceptance.
No validator callback replacement, firmware mutation or dynamic-admission
relaxation was introduced. The source review is not a test-pass claim.

Independent runner/helper tests are still being authored and were not frozen or
executed at this checkpoint. Close finding3, freeze the independent oracle, run
the authorized host checks, review the exact resulting runner/helper bytes and
retain first failures before final host disposition. D143 authorizes only this
host work; any native query/compiler needs a later source-bound GO. Entry/ABI,
fit/runtime evidence, D139's 592-byte dynamic deficit and human gates remain
separate and unchanged.

## Known-terminal repair closure (source inspection)

The coordinator's repair had arrived while the preceding snapshot was under
review. Re-read runner SHA256
`30d0eb335cad506444217bbae83a729ce787694ed777d52132f8fcc9a408f9cb`
(32,922 bytes). Lines402-403 now set terminal immediately after recognizing a
well-formed zero compile result, before record.update and the completion write
at404-408. A later receipt-write error therefore remains the primary failure and
execute performs all five terminal postchecks; collection is still blocked.
Malformed/nonzero results retain the UNKNOWN boundary. **Finding3 is closed by
source inspection; no open material runner source finding remains.**

All 17 literal input hashes matched again, including the updated helper
`ff7add89ac849c9849ad4cb0bfd41f7e0e5877d61df9b74150b7da2e354e069a`.
AST counts remain 56 functions, maximum 42 lines. This bounded recheck did not
import or execute either implementation. Independent frozen tests and exact
helper code review remain pending; no host-test pass or native GO is inferred.
