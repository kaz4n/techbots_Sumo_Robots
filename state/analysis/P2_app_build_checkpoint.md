# D099 pause checkpoint - incomplete adoption

2026-09-23 Asia/Dubai. User explicitly requested finishing current checks, saving
work and pausing for hardware/network disconnection. No board/network operation
was started after that request. The already-running default compile completed.

Completed prerequisite work: D097 getter correction3d84958; D098 independent
dependency experiment/review1447ec8; D099 public contract6b48779. D097 full normal
and sanitizer suites1418main/25218819assertions +173Gate/4536382 passed. D098
isolated candidate saved27452B with actual native/app/startup paths preserved.

Current D099 work implements app-only native-app-v1 property selection, strict
CLI1.5.1 identity/JSON/platform/selected-property/zero-library checks, fresh build
paths,18 installed file pins and4 artifact hashes, with raw compiler output saved
locally. Benches retain their previous commands. App uploads remain rejected
before target/transport lookup. No firmware/config/locked-test change occurred.

Actual default invocation:
`python tools/board_tool.py flash app --compile-only`.
Receipt `P2_app_build_raw/target_default.json` records start16:10:52Z/end16:12:19Z,
exit0. Source570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84;
153684program/248308RAM/13836nominalremainder, including actual low-memory warning.
`default_receipt/` preserves command, compiler JSON/stdout, stderr and verified
hashes. Final ELF hash9808dc594d77be8f43865a17542a48b715b4d5ee4a1277d6f946d0a6ccb09e65
is identical to reviewed D098 candidate. Debug/temp hashes differ; their new
source/object audit has not been performed. No new load/freeRAM/WCET claim.

**OPEN MAJOR / ADOPTION NOT ACCEPTED:** separate fresh-context checkpoint reviewer
demonstrates that altered effective recipe.cpp.o.pattern, compiler.cpp.cmd and
prebuild hook values can pass the current selected-property validator. An
unreviewed platform.local.txt can change recipes without changing platform.txt's
pinned bytes. This is a real policy gap, not an observed defect in the actual
default binary. Preserve the exact reproduction in
`reviews/P2_app_build_checkpoint_review_raw/`; do not close or downgrade it.

First resume task: reject unreviewed local configuration before compiling and
verify effective compiler/recipes/link/startup/hooks, with independent regression
tests derived from this finding. Review the actual supported CLI expansion before
choosing the smallest fix. Then complete default/Immediate/MATCH target audits,
the phase-independent explicit-library discovery fixture and final D099 review.
No target mode other than default was built by D099; neither logical mode tests
nor D098 default evidence establishes their binary behavior.

Established fixture adaptations affect only fake version/JSON/hash protocols.
All49 existing SSH/ADB test methods/assertions are AST-identical and passed in
58.926s, exit0. New independent test results and original oracle/fixture failures
are retained under `P2_app_build_raw/author/`; final result is appended below.
The local library fixture is prepared but has never been built/run on the board.

No source/MCU upload/reset/pin action or motor operation, new inert key, remote
push/tag or human gate. Last known deployed image is D0911502e948, the old inert
synthetic recorder. Every physical acceptance, actual loadedRAM/full800us, local
reset/nativeUART integration and human gate remains pending. Work stops at this
checkpoint until the human explicitly resumes it.

Final independent author run:29 host methods (18 parser/11 command), exit0,
12.996s. All malformed JSON, version/property/library, process/output and
hash/artifact failure cases pass within the authored scope. Original new-test
oracle and fixture errors remain preserved. No established assertion was weakened.
Checkpoint reviewer disposition: FAIL for D099 adoption, open **D099-R1 MAJOR**.
This review completed its bounded task and stopped; it did not run target tests.
