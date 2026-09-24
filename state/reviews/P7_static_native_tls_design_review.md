# D147 native TLS extension design review

2026-09-25 Asia/Dubai. Separate **reused-context, same-model** design review;
this reviewer previously reviewed D146 collection. Not a fresh-context review.

Disposition: **PASS for host-only scope adoption; no open material findings.**
No implementation exists in this review scope. No implementation/test execution,
board call, source edit, parser acceptance or phase gate is claimed. Only this
review file was written.

Reviewed contract SHA256:
`588e1ad8e25be604e9b048477dd7f67e716ea206ab88b8485de5d54e99437859`.
Read the completed D146 provenance validation/receipt, retained assembly and
source analysis, original D142 contract/implementation and frozen D143 report
consumer. Rehashed the fixed assembly68bb1476 and validator d30372dd: exact.

## Findings

The exception is precisely bounded: six names, fixed offsets8/8/16/20/24/28,
size0/GLOBAL1/TLS6/other0/ABS65521, each once in every final/debug/temp image on
the nonlocal side of sh_info. This matches D146's actual assembly/object and
three-image evidence. Missing aliases, reserved-name shadows of a different
type, additional or anonymous TLS entries and changed tuple fields all fail.
Duplicate offset8 is intentional and distinct from duplicate symbol definitions.
Legacy no-alias images intentionally remain outside this new interface.

Both supplied byte sources require exact type, size and hash before source
execution. Only the frozen Python validator is executable; the assembly is
identity evidence. Fresh private namespace reuse can preserve the original
component and modules while specializing the one symbol interpretation. The
contract permits that approach and does not require modification of frozen
bytes, original fixtures or existing module state.

All other D142 checks remain required, including symbol-table partition/index
rules and essential symbols, section/program/TLS/relocation restrictions,
normalized three-image equality, initialization extents, flat BIN and both ZSK
relations. Original report fields consequently continue to describe/hash the
actual supplied artifacts, not modified surrogates. How an implementation
ensures this remains an implementation-review obligation, not an interface gap.

The additional native_tls report has exact keys and sorted fully checked tuples.
Frozen D143 rejects the proposed report both through its exact top-level schema
and its literal STATIC_LAYOUT_PACKAGE_PASS status check. The distinct new status
therefore cannot silently enter the old success path. No consumer is changed.

The pinned assembly identifies the observed packaged firmware; it does not bind
arbitrary future artifacts to a live installation. The draft correctly assigns
that separate binding to an eventual caller and excludes consumer/board scope.
Likewise, retaining TLS section/program restrictions does not prove absence of
indirect or native TLS use. The draft expressly leaves use, runtime ABI, entry/
constructor audit, measurements and physical gates unresolved.

The independent-test brief covers the complete new exception, all three images,
source admission, no mutation, old behavior and representative unchanged layout/
package failures. Combined with original regressions and source review, this is
an adequate bounded verification plan. Freeze expectations before implementation
execution and preserve any first failure; no additional unrelated matrix is
needed at design adoption.

Next: coordinator records host-only adoption, assigns the independent test author
the contract/public fixture interface, then implementation and focused regression
execution followed by separate source/receipt review. Preserve D144's original
rejection and all frozen contracts, tests and production consumers throughout.
