# D222 independent commissioning compile test plan

The first public-contract oracle was authored from
`P7_commissioning_build_contract.md` and accepted historical fixtures before
reading the new production files. No test, native action or compiler has run.

`tests/tooling/test_commissioning_app_static_policy.py` independently enumerates
the seven profiles and fourteen motor identities. It checks exact ordered flags,
strict selectors, every snapshot identity before execution, real complete
metadata acceptance and cross-profile rejection, ELF/TLS/package/export failure,
result identity and private-call isolation. It reuses D213 fixture definitions;
the old test suites and source remain unchanged and are not collected.

`tests/tooling/test_commissioning_app_compile.py` initially checks exact CLI
grammar, all profile/motor/action selections, token boundaries, deterministic
paths and source-prefix collisions, invalid request types before primitive reads,
private namespaces, bound HEAD constructors and inherited injectable seams.
After the initial oracle was saved, the coordinator accepted a contract amendment:
owner suffix is SHA256 of full source plus NUL plus attempt, truncated to twelve
characters, preserving the inherited 48-character owner limit. Tests were updated
before execution; the complete source remains mandatory in the sketch identity.

The completed controlled caller fixture uses the implementation's data-only
dependency/bundle and receipt interface after the initial independent files were
saved. It exercises real local admission with exact source and supplied reviewed
HEAD bytes, read-only check, owner collision, changed HEAD/source/input, one query
and one compile with jobs1, compile-only command inspection and the preserved
Windows 30000-unit limit. It injects early prerequisite failure, compiler failure,
lost second-transfer reply and wrong late artifact identity, then requires
independent closing and preservation of the first error. Linux additionally runs
actual descriptor-backed artifact validation over the accepted synthetic ELF/TLS
packet and checks all closing observations after an invalid exported package.
Successful metadata/artifact validators are real; board/process transport and
Git answers are controlled fixtures. This suite does not claim native results.

Production inspection is permitted only after these initial independent files
are saved and the coordinator is informed. Any fixture clarification must retain
the normative expectations above; implementation defects remain defects.
That authoring boundary was observed. Integration inspection found the initial
remote adapter executing its fixed primitive before all bundle members were
validated; the implementer repaired this before any tests ran. The independent
bundle test requires rejection before exec for every malformed member.

The first Linux policy run returned 13 failed subcases in the single full-artifact
report method. The expected report originated from the accepted B4 M0 fixture;
its flags were mistakenly left at B4 M0 for the other thirteen selections. Raw
failure output and exact original oracle SHA52483de6 are retained under
`P7_commissioning_build_raw/first_linux_static_policy01/`. The independent author
confirmed the contract requires each selected full flag identity and corrected
only expected `flags` using the oracle's independently enumerated profile map.
The full-report equality assertion and all fourteen selections remain intact.
No production change or test execution was performed by this author.

After coordinator authorization, run the two focused files serially with
`python -I -B`, first Linux and then Windows, preserving raw stdout/stderr,
return codes, source/test hashes and unique failures. No ancestor suite rerun,
target build, upload, reset, motion, grant or physical acceptance follows from
this test plan. Later native compilation has separate admission and evidence.
