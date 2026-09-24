# D142 static artifact structural validation

The pure host layout/package component is implemented, host-tested and separately
reviewed with no open findings. Its first execution after
two pre-execution inspection fixes passes all 45 independently frozen public test
methods. The unchanged private six-method probe also passes on the repaired
source and reproduces both gaps on the preserved initial source. The
[final scoped code review](../reviews/P7_static_artifact_code_review.md), SHA256
`305c87e216e6c4ac19605059e4c4d08ef8fc838ea0777f7298e7009a6b32bf22`,
closes both MAJOR findings. The repaired component and execution evidence are
committed in `9f79bf41`.
This is synthetic host evidence only; no static app has been compiled or run.

## Scope and source

[D142 contract](P7_static_artifact_contract.md), SHA256
`b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54`,
was adopted after the [separate design review](../reviews/P7_static_artifact_design_review.md)
reported no open findings. That review used a separate reused same-model context,
not cross-model or human review. Parent policy contract and production policy
remain unchanged.

The new [static_artifacts.py](P7_static_link_probe_raw/static_artifacts.py), SHA256
`d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368`,
accepts only seven byte payloads. It checks the fixed ELF32 executable identity,
bounded tables/names/symbols, named allocations and segments, separate LMA/VMA,
copy/zero ranges and complete BSS padding, cross-form allocation/entry consistency,
exact raw BIN and flat/diagnostic ZSK packaging. It performs no filesystem,
process, clock, environment or network operation. All24 functions are below60
lines (maximum31, AST inspection); no firmware/config/established test changed.

Its sole success status is `STATIC_LAYOUT_PACKAGE_PASS`. The link map is retained
and hash-bound, not parsed as proof. Undefined weak names are reported for later
classification. Source/run freshness, actual instruction and constructor order,
native/wrapper/heap bindings, ABI sizes/offsets, loading, live RAM, stack and WCET
remain separate requirements of the full parent probe. No full-probe verdict,
source adoption, target action or gate follows from these unit tests.

## Independent expectations and actual first run

The separate test author read the contract/source references, not implementation
bodies. Code writing proceeded concurrently; execution waited for both freezes.
The original39 methods and fixture were frozen/committed in `8d6eb7bb`. Six
consistency methods were added in a separate frozen supplement; the original
oracle files were not edited. Fixtures are generated in memory, with ordinary
ELFs under4KiB and one transient16MiB+1 buffer for rejected input-size boundaries.

- [Original freeze](P7_static_artifact_test_draft/freeze_artifacts.json), SHA256
  `535f985874ec0cd0395516b7ff73175ce31760928a84b48b950ead890e64bab1`.
- [Supplement freeze](P7_static_artifact_test_draft/freeze_consistency.json), SHA256
  `ba5c6444815e7b7d81ccbbadfb031e8c1dc519deaa51c6c2f256dea2e6239163`.
- [First-run receipt](P7_static_link_probe_raw/artifacts_first.json), SHA256
  `ac5602988c92b24dd1bcd4f653c40b8ae0c2db2b17e30af721647c840c0e27bd`:
  exact argv, original stdout/stderr, returncode0, unittest45 PASS in1.825s
  (whole invocation1.960s); all11 frozen inputs unchanged before/after.

Reproduce with `python -B -m unittest discover -s
state/analysis/P7_static_artifact_test_draft -p 'test_static_artifact*.py' -v`.
Positive fixtures exercise true zero-filled BIN gaps despite different ELF file
padding, flash LMA distinct from RAM VMA, BSS reservation beyond its cleared
range, different debug/file offsets, weak-symbol union, empty allocations and
section/symbol-index renumbering. Negative cases exercise identity, limits,
overlap, permissions, orphan/TLS/relocation data, malformed symbols, inconsistent
ELF forms and exact package fields/content/lengths. The map remains opaque by
contract, so no tests imply a native instruction or source-provenance audit.

## Pre-execution findings preserved

Initial parser SHA256
`50d067223087fe8a64fd34378cd4cf255b1d46a654d0c156aa50e86db70ab793`
is preserved in `a986ffdb`. Inspection found two MAJOR consistency gaps before any
module execution: empty allocated records were omitted from comparison, and only
the entry value was compared across forms instead of its complete normalized
symbol record. A separate reviewer confirmed both. One bounded patch includes
all allocated records and compares entry value/size/type/binding/visibility with
the semantic section name, preserving valid section-index renumbering.
No assertion was weakened. The separate reviewer froze its
[six-method probe](P7_static_artifact_review_raw/test_artifact_consistency.py), SHA256
`2b2e4f4cd0667243d728dfd8a1781e99ad1a049f1dc55ccaec9837b437e750a7`,
before running it. [Its freeze](P7_static_artifact_review_raw/freeze_consistency.json)
binds the same contract, public fixtures and both implementation identities.

- [Original result](P7_static_artifact_review_raw/original_consistency.json), SHA256
  `b5f9204424114419f9bc562410c6062769a56f640fb845b8d4571ea5fd0b741b`:
  exit1, 18 failed negative subcases across three methods; three positive methods
  pass, zero errors. The original module was read from Git into memory, not
  checked out over the repaired file.
- [Fixed result](P7_static_artifact_review_raw/fixed_consistency.json), SHA256
  `84a89281fd142a013f571ffd59698243ed0b16d0bdf36e30b4631183a08b2759`:
  the identical six methods pass, exit0, zero failures/errors. Missing/changed
  empty allocations, entry size/binding/visibility and valid section-index
  renumbering are explicitly covered. Original failure text remains retained.

## Remaining work and retention

Next settle/adopt the one-shot runner's command
templates/interfaces and freeze independent failure/stale-output tests. The
runner must preserve source/tool hashes, all production checks, exact static
policy, exclusive outputs and one compiler attempt. Query/compiler execution
remains unapproved until that work passes its separate review. A later real-image
native audit must satisfy every parent-contract item before a positive probe.
D139's592-byte default dynamic fit deficit remains; no actual fit or phase gate
has changed. Retain compact source, independent oracles, first result and review;
no build tree, downloaded dependency or binary fixture was created here.
