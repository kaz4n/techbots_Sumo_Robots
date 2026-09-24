# D143 independent test handoff

Objective: derive and freeze host tests from the public D143 contracts, then run
only coordinator-authorized host fakes and private Linux filesystem fixtures.
No new implementation body was read by the test author. No board transport,
Arduino compiler, target code, upload, or motor action was executed.

Terminal result: all 80 accepted methods pass across five separately invoked
suites. This is host protocol and filesystem evidence only.

| Suite | Methods | Accepted execution receipt |
|---|---:|---|
| Runner protocol, oracle revision 2 | 22 | `retry1_runner_execution.json` |
| Runner completion-receipt failures | 2 | `first_receipts_execution.json` |
| Synthetic public bootstrap | 23 | `../P7_static_remote_test_draft/first_bootstrap_execution.json` |
| Remote descriptor protocol | 28 | `../P7_static_remote_test_draft/retry1_remote_execution.json` |
| Remote claim/size admission supplement | 5 | `../P7_static_remote_test_draft/first_admission_execution.json` |

Every execution receipt records exact argv, cwd, timestamps, actual exit code,
and before/after source and frozen-input hashes; exact stdout/stderr are retained
in adjacent files. All before/after hash comparisons were unchanged. All runs used
Python `-B`. Remote descriptor tests ran under actual nonroot WSL uid 1000.

Accepted runner/helper implementation hashes are respectively
`983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208` and
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
The unchanged public bootstrap was independently tested using synthetic helper
bytes on the initial implementation pair; no real helper execution is involved
in that suite.

The first runner run retained one failure: the original test erroneously closed
the entire receipt directory's file set and rejected `inputs.json`. Independent
review confirmed that the contract requires recording the runner's own hash and
permits compact input metadata. Coordinator-approved oracle revision 2 adds only
that file, then checks its exact keys, all 17 pinned inputs, exact D139 stage
evidence, and current runner hash. Original test/freeze bytes are preserved in
commit `047d6576`; the first failure receipt and output remain here.

The first remote run retained one failure: inode replacement was detected but
classified `FILE_READ` rather than the test's `SOURCE_DRIFT`. The coordinator
adopted a precise source-drift diagnostic refinement. The remote oracle remained
byte-for-byte unchanged; its next authorized run passed all 28 methods.

Owned sources are `public_fixtures.py`, `test_static_runner.py`, and
`test_static_runner_receipts.py` here, plus `test_static_bootstrap.py`,
`test_static_remote.py`, and `test_static_remote_admission.py` in the remote draft
folder. Four freeze JSONs bind their independent public inputs. Seven execution
receipts and their stdout/stderr captures preserve both initial failures and
accepted reruns. Existing production files, prior D141/D142 tests, source/stage,
contracts, and shared ledgers were not edited by this subtask.

Storage: tests used normally cleaned temporary receipt directories and private
`/dev/shm` source/artifact fixtures. Read-only cleanup inventories found zero
`sumox_runner_*` directories in the Windows temporary directory and zero
`sumox_remote_*` entries in `/dev/shm`. No persistent binary fixtures or Python
bytecode were created in these owned folders. All retained files support
reproduction, review, or failure evidence; no additional deletion is needed.

Next action belongs to the coordinator: review these host results, record them
in shared state, and decide any later execution scope separately. The author has
stopped expanded testing; no runtime qualification or phase gate follows.
