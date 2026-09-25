# D179 fixed inert caller: offline validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED / REVIEWED;
native use pending.
Source d8418fad, inert_run.py23100B,
SHA2568b47b1d6e9073179e4f587e09ce04e1a1c0cfc6797daf3151d0a7126d279f56a.
No production change was needed after its first execution.

The caller reuses the pinned startup ownership helpers, unbound compile transport
and D177 action interfaces. It requires a committed new identity/scope, pins all
local sources and provenance, owns one durable attempt, checks prerequisites
independently, conditionally captures after admitted upload, and retains primary
and closing failures. Check-only cannot create its owner or call the board.
This implements the narrow contract35f51823; it is not a generic launcher.

## Evidence

All receipts below are under [P7_motor_fault_raw](P7_motor_fault_raw/).

| Receipt | Actual result |
|---|---|
| caller_freeze.json /5fb59139 | Source + independent original44-method oracle frozen;24 input pins |
| caller_first.json /02d7e9ee | 42PASS/1FAIL/1ERROR/0skips; original result preserved |
| caller_corrected_freeze.json /6e3d69c8 | Only two independently adjudicated new fixtures corrected;23 other pins unchanged |
| caller_corrected.json | 44PASS/0failures/0errors/0skips; exit0,8.512s unittest time |
| caller_windows.json /80c3d5cd | Exact source commands28,990/25,232 UTF16 units including NUL, below30,000; missing real scope returns builtin int1 before process/owner |
| caller_closure.json | All24 current +11 prior D177 pins match; seven raw files byte-equal Git, original PROGRESS prefix intact, firmware/locked tests/tools/build config unchanged |

The independent test author did not inspect/import/execute inert_run.py while
authoring or correcting tests. Corrected oracle SHA256
2260d0bc3451473c8b62b87ae7ae126a2b1eeb5a67583393a2c3d32005e1460c,
41792B. [Failure adjudication](P7_motor_fault_caller_failure.md) records agreement
from the spec-only author and separate same-model reviewer. Original test/failure
bytes remain in Git. No established assertion or locked test changed.

Commands: WSL Ubuntu `python3 -B -` with the inline unittest loader recorded in
the receipts; module `test_inert_run.py`, all44 methods. Each run verified the
corresponding24-pin freeze before and after. Windows `python -B -` performed
local composition, missing-scope CLI and AST function-length checks. Python
versions3.12.3 WSL and3.13.11 Windows. No package install, firmware build or
unchanged-suite rerun. Existing tested dependency bytes remain pinned.

Tests use small owned /dev/shm fixtures, controlled Git/ADB checks and substituted
CompileOnce.transport; all process/native operations are prevented. Coverage
includes strict scope/reply types and bounds, every pin, changed identity,
exclusive owner/intent, command mutation/limits, exact eleven-call sequence,
partial replies, primary/causal/independent errors, closure failure and CLI modes.
Fixtures were context-cleaned; both runs left zero task scratch. Actual scope
inert_run01_scope.json and owner native_inert_run01 remain absent in this checkout.

Separate fresh-context same-model review:
[P7_motor_fault_caller_review.md](../reviews/P7_motor_fault_caller_review.md).
PASS with no open BLOCKER/MAJOR; SHA256
d67c0dcaa01aaebc61cfdb29a68ad540c222e5cb98f1830d40efc8e0f7dbe392.
Its scoped disposition is not a human gate or cross-model review.

## Remaining dependency and limits

The board is disconnected. No ADB process, identity query, upload, reset, memory
capture, decoder run or motor operation occurred. Commands use historical
bindings only for size arithmetic; they do not establish a current boot or tool.
Host substitutions do not prove live filesystem durability, native transport,
board capabilities, remote reap, startup, RAM, timing or physical acceptance.

When hardware is available, first perform fresh bounded read-only admission of
identity, Python capabilities and exact tool/artifact/prerequisite bytes. Then
bind this reviewed caller/oracle/contract/review and actual identity in one new
committed scope, review that concrete operation, and use the already compiled
default/dynamic MATCH0/MOTORS_ALLOWED0 active diagnostic. Do not reuse any old
scope or rebuild unchanged firmware. Capture is conditional on strict upload
success; raw snapshot retrieval/hash checks precede offline decoding. A timeout
does not authorize retry. No motor-capable run or physical/human gate is implied.
