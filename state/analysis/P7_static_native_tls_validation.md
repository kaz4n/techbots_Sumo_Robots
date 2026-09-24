# D147 exact inherited TLS structural extension

25 September 2026, Asia/Dubai. **IMPLEMENTED / HOST-TESTED / SCOPED REVIEW PASS.**
This is the new pure structural interface only. It has not validated the actual
D144 packet, changed production admission, compiled/uploaded firmware or passed
a physical/human gate. The original D144 rejection remains preserved.

## Change and scope

D14703383c2e adopts [contract](P7_static_native_tls_contract.md), SHA256
`588e1ad8e25be604e9b048477dd7f67e716ea206ab88b8485de5d54e99437859`.
Actual D146 installed assembly/object/map evidence supports exactly six inherited
TLS constants. The new [static_native_artifacts.py](P7_static_link_probe_raw/static_native_artifacts.py)
requires both the exact977-byte assembly hash and original validator hash before
loading the original source into a fresh private namespace. It specializes only
the symbol interpretation; every ELF form must contain all six exact tuples once.
All other original layout, initialization and packaging checks remain in force.

First implementation2d39b8f9 remains unchanged, SHA256
`cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0`.
The original validator remainsd30372dd, with its contracts/tests/fixtures and
all consumers unchanged. The distinct `STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS`
report is deliberately rejected by the old consumer. No application TLS storage,
native TLS use, source freshness, native ABI or runtime claim is introduced.

## Independent expectations and actual checks

A separate fresh context derived19 methods from the public contracts, synthetic
fixture and exact assembly fixture, without reading validator/collector bodies
or using a target ELF as the expected result. Freeze3462c6f8, SHA256
`e1cd0763877276c279718003deced702d8f6e902958b5db7382eb798b167a8e4`,
precedes first execution. Fixtures are constructed in RAM; no old test was edited.

Actual command receipts/stdout/stderr are retained under
[native_tls_host](P7_static_link_probe_raw/native_tls_host/native_first.json):

| Invocation | Result |
|---|---|
| `python -B -m unittest discover -s state/analysis/P7_static_native_tls_test_draft -p test_static_native_artifacts.py -v` | 19/19 PASS,7.421s |
| `python -B state/analysis/P7_static_artifact_test_draft/test_static_artifacts.py` | 39/39 PASS |
| `python -B state/analysis/P7_static_artifact_test_draft/test_static_artifact_consistency.py` | 6/6 PASS |
| `python -B state/analysis/P7_static_artifact_review_raw/test_artifact_consistency.py --source-ref working` | 6/6 PASS |

**70 methods passed:19 new and51 existing.** New coverage includes all six
aliases in all three images; altered fields, local partition, missing/extra/
anonymous/duplicate/shadow symbols; byte-source admission before execution;
no I/O; caller/result/module isolation; old rejection unchanged; artifact bounds,
normalized empty allocations, initialization metadata and both package pairs.
All ten recorded source/oracle pins match before/after. No source or oracle fix
was needed. The initial private-regression command omitted `--source-ref` and
exited2 at argument parsing, before tests. Its usage error remains in
`legacy_private.*`; the corrected invocation changed only the command argument.

The separate fresh-context same-model [code/receipt review](../reviews/P7_static_native_tls_code_review.md)
passes with no BLOCKER/MAJOR/MINOR. Review SHA256
`dc7156b35737070cd4244384eb3ced35d1f1de18edacd6da014a8e7271547362`.
It inspected code, expectations and actual receipts; it did not claim an
independent rerun, cross-model review or human gate. No unrelated C++ rebuild
was needed because firmware and production tooling are unchanged.

## Exact next step

Separately scope read-only validation of D144's existing seven-artifact packet
under this new interface, binding the new source hash, unchanged original
validator/helper, installed assembly/loader, old Claim/FileRecords and current
project source. Do not recompile or reuse a consumed GO. Keep the new result
separate from the original rejection and from unchanged production consumers.
Entry, constructors, native bindings/ABI, live stack/RAM/WCET and physical/human
acceptance remain required even if that structural check later passes.

Retain the compact frozen tests, focused receipts and reviews. They provide
reproduction and first-run evidence; no native tree, duplicate checkout, bytecode
or persistent binary fixtures were created by this host task.
