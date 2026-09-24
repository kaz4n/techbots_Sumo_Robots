# D143 static probe host validation

Status: IMPLEMENTED/HOST-TESTED,80 passing methods across five scoped suites.
Separate source/receipt reviews close the inspected findings. No native command
was executed by these tests; target execution remains a separate scope.

The scoped runner and Linux helper compose the unchanged D141 policy and D142
structural parser. They bind one fixed inert/default/static profile, the current
source stage and installed-tool identities. The runner has no upload, reset,
restaging, cleanup or retry path. Unknown compiler transport completion prevents
further remote commands; a successful structural collection is not runtime proof.

## Actual checks

| Check | Result | Receipt |
|---|---|---|
| Exact controlled runner protocol | 22/22 PASS, Windows Python3.13.11 | [retry1](P7_static_runner_test_draft/retry1_runner_execution.json) |
| Real Linux descriptor fixtures, nonroot UID1000 | 28/28 PASS, WSL Python3.12.3 | [retry1](P7_static_remote_test_draft/retry1_remote_execution.json) |
| Fixed bootstrap with synthetic helper bytes | 23/23 PASS | [first](P7_static_remote_test_draft/first_bootstrap_execution.json) |
| Deep malformed JSON and rejected-file metadata | 5/5 PASS | [first](P7_static_remote_test_draft/first_admission_execution.json) |
| Known/unknown compile completion with receipt-write failure | 2/2 PASS | [first](P7_static_runner_test_draft/first_receipts_execution.json) |
| Prior project inputs, current bindings and legacy progress | 687 unchanged, 17 pins exact, prefix unchanged | [root check](P7_static_runner_root_checks.json) |

The runner success fixture requires the exact26-command sequence and arguments;
negative cases cover admission, identity/resource/source/tool/property drift,
stale outputs, malformed evidence, transport errors, original-failure retention,
independent postchecks and final collection. It substitutes only the public
transport callback and filesystem observations. It does not simulate a successful
board build. Linux tests perform actual descriptor operations on private /dev/shm
fixtures and mock account/platform/resource labels; they never change the real
stage. Bootstrap tests execute synthetic helper bytes, not an unreviewed remote
program. All invocations use -B and preserve compact actual stdout/stderr/exit
records with pre/post oracle and implementation hashes.

The supplements exercise the original parse/fstat findings and the known-zero
completion boundary. A failed completion-record write after an observed zero
compile still runs all terminal checks and remains FAILED; a timeout plus the
same write failure preserves the original exception/bytes and stops remote
commands at17 with COMPILE_OUTCOME_UNKNOWN. Normal temporary fixture cleanup
completed; the nonroot WSL check found zero remaining sumox_remote_ directories.

Final tested runner SHA256:
`983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`.
Helper SHA256:
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
The root AST check accepts Python3.9 syntax; it is not Python3.9 execution proof.

## Original results and dispositions

First source and inspection repairs are preserved in cd5625e2/e64c61f9. Initial
tests/freezes are in047d6576. First runner21/22 and helper27/28 receipts remain;
bootstrap passed on its first execution. No failure was erased.

The runner's new success oracle incorrectly excluded compact inputs.json despite
the contract's own-hash recording requirement. Independent author and reviewer
agreed. D143 permits only adding that exact file plus stronger exact metadata
checks; every other method/common fixture remains byte-identical. The corrected
freeze records its predecessor. No established or locked test was amended.

Source inode replacement already failed closed with exit2/FILE_READ. The contract
does not uniquely assign that diagnostic. The coordinator adopted the reviewer's
bounded SOURCE_DRIFT refinement for positively detected source identity changes,
retaining ordinary read/bounds/ancestry errors and the unchanged helper oracle.
See [clarifications](P7_static_runner_implementation_notes.md),
[runner review](../reviews/P7_static_runner_code_review.md) and
[helper review](../reviews/P7_static_remote_code_review.md).

The helper review is a fresh same-model context. Runner review reuses a separate
same-model context. Neither is cross-model review or a human phase gate. Current
host tests establish tooling behavior only: the static image has not been built,
the dynamic default still has its592-byte modeled deficit, and native entry,
constructors, bindings, ABI, loading and runtime remain unqualified. A later
source-bound coordinator GO is required for the one query/compiler experiment.
