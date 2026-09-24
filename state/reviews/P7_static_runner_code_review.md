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

## First host execution: independent oracle adjudication

Reviewed the retained first runner execution without re-executing it:

- `P7_static_runner_test_draft/freeze_runner.json`:
  `06e7e61c68fc0aaf2fe329c29547805cde9c4a0ee6c8588aa7677c4b00f2bc2b`.
- Original `test_static_runner.py`:
  `cb6055a7d24312cada12b7b18e8debb7cd083df8abf30c9d0c509fe6203e5c91`.
- `first_runner_execution.json`:
  `04394b356432afb737e65959a6ce6cd06721a14e5f4b192bf23805c21d205108`.
- `first_runner_stderr.txt`:
  `4160cd85ec4f5dd381d1dbc580feef942dbe55309f40a69c92cd2089b38518ad`.

The receipt binds runner
`006fdb709fa695714c38f208cad2650be9cc60e7cdaac13fa95b6e9d441dbfb3`
and helper `521773e51b62e19421efe7e25192ed938e4367acd6336984b8c7ba954d9a93d1`
before/after execution, together with unchanged independent inputs. Stderr reports
22 methods in13.135s, 21 passing and one failing. The sole failure is the success
test's directory-set assertion at172-173: actual output contains `inputs.json`.
Later assertions within that failed method did not run; this is not 22/22 PASS.

**MINOR oracle overconstraint, not an implementation defect.** The frozen
contract requires the runner's own hash to be recorded at line79. Its exact
success and command schemas at48-56 and233-236 contain no field for that hash.
It specifies no exclusive whole-directory file set. The storage provisions
at252-258 limit duplicate large artifact transfers; compact input provenance is
consistent with them. Runner lines636-637 exclusively create `inputs.json`
containing its own hash, literal pins and verified-stage receipt before commands.
Removing that evidence to satisfy the new assertion would undermine line79.

Smallest compliant remedy: retain the original test/freeze and first failure;
correct only the new oracle's expected directory set to include `inputs.json`,
preserving exact equality and all command/result assertions. Independently check
the recorded runner hash against the current source bytes; the compact receipt's
pin/stage contents can also be checked against existing public evidence. Do not
allow arbitrary extra files, change the frozen contract, remove evidence or
weaken an established test. The test author should freeze the narrowly corrected
oracle separately before another run. This ruling does not declare that rerun
passed and adds no native authority. Reviewer modified only this review.

## Corrected-oracle retry and scoped host disposition

Independently compared the current test with Git `047d6576`. Only
`test_success_exact_protocol_receipts_and_checked_final_only` changed: it now
includes exactly `inputs.json` and checks its exact three fields, all reviewed
pins, current runner source hash and verified-stage103/102/source digest receipt.
The other21 methods and the entire public fixture are unchanged. Directory,
command and result equality assertions remain exact. The original failure is
also present in `5fc7c2d9`; this is the adjudicated new-oracle correction, not a
production-code concession or an alteration of established tests.

Read-only verification of the separately frozen retry evidence:

- Corrected test: `594d399dc818d3ae5113648d92589d8921b16fd37c36d1682d4ea59ba6bfbc20`.
- Corrected freeze: `af5e4cea516e1ed00a511d2cd5b1703fb817a908ed2c8da14136859d0ebfa645`.
- `retry1_runner_execution.json`:
  `868da5a8069c198c0fb8a398a520337433b7ea797c5ec1dafe0adfa285b8dbb5`.
- `retry1_runner_stderr.txt`:
  `cc9e0f2213db4aa8a13575cee24e08a63d589608ae16daba7641873fee9db4d9`.
- `retry1_runner_stdout.txt` is empty, SHA256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Runner: `983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`.
- Helper: `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.

Retry stderr reports **22/22 PASS in13.275s**, exit0. All19 before/after receipt
hashes agree and match current bytes; all16 corrected freeze inputs and all17
runner literal pins also match. The runner differs from the first executed
version only in its helper hash literal. No further execution was performed by
this reviewer.

**Scoped disposition: runner source review PASS, HOST-TESTED22/22, no open
material runner source finding.** This does not replace the separate helper
review or its pending supplemental checks. The repaired completion-write branch
for an already confirmed zero compile remains verified by source inspection;
the22 methods exercise planned-write failure but not that exact branch. A small
independent regression for it was recommended to the coordinator before final
full-tool host disposition. No native query/compiler, static target fit, ABI,
runtime, motor or human-gate acceptance follows from these controlled tests.

## Completion-write regression closure

Reviewed the independently authored two-case supplement frozen in `9f71e716`:
`test_static_runner_receipts.py` SHA256
`b85fa86d61031647f5be48483e1edf3aaa34c75c5a79f554fe2cd364888dba73`,
with `freeze_receipts.json`
`49cc9d75f76b93b72d19170af8019a818094d1ef0e25e0bb43f085a9562bb2f9`.
It injects failure at the actual io.open boundary only after command17 was
dispatched. A known-zero completion preserves the receipt OSError, records
FAILED and performs the exact three remote terminal checks (20 dispatches total)
without collection. A timeout plus completion-write error preserves the original
TimeoutExpired object and partial bytes, records UNKNOWN, observes both local
pin/stage checks and stops at17 dispatches. Validators are not replaced.

The retained `first_receipts_execution.json`
`a2a92a9d763f59cfb965369b7d8700e36173bbb1b1944d51694c24afb7d5d694`
and stderr `7689de6b57b8f65e96a6737db0bb1efe7c991ac1c109200e5cd8d83e5cf9c142`
show **2/2 PASS in0.667s**, exit0; stdout is empty. All21 before/after input
hashes and the four supplement-freeze inputs match current bytes. Runner
`983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`
and helper `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`
are unchanged from the22-method retry.

The last runner coverage note is closed. **Final runner disposition: source
review PASS and24 independent host methods PASS across the retained22+2 runs;
no open runner finding or requested regression remains.** The reviewer read
source/receipts and rehashed evidence only, without another execution. Separate
helper review remains its own evidence; later native source-bound GO and all
target/runtime/human boundaries are unchanged.
