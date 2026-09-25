# D192 inhibited application observation: scoped review

26 September 2026, Asia/Dubai. **PASS for the host software scope; no open
material findings.** Reviewer: `/root/fresh_review`, a separate same-model,
reused context. This is not a fresh whole-project or phase-gate review.

The reviewer read the contract, all three new bench files, the exact config and
tooling diff, all three new oracle files, and the actual saved test receipts.
Local data/hash inspection was independent of the coordinator's summaries.
The reviewer did not execute subjects or tests, compile, access the device, or
edit implementation/tests. Only this review document was written.

## Reviewed implementation and contract

The [contract](../analysis/P7_app_motor_observe_contract.md) has SHA-256
`74ceaa0a638168237ccc8b32696764e12fb626721d7b71d9694f6c6b867488f2`.
Final reviewed source pins are:

| File | SHA-256 |
|---|---|
| `bench/app_motor_observe/app_motor_observe.ino` | `1df77ff537ef354bcb6bae9141ad117881216df125581f0d4ade3e286a6f007b` |
| `bench/app_motor_observe/src/app_motor_observe.h` | `25bf299be1e2b917a0f91e7ad933eec5179cbfe6d92273bed0a8d9f5ce97d77e` |
| `bench/app_motor_observe/src/app_motor_observe.cpp` | `eec10eacd250590f4eb4a6b1c01b0cac925411c1f126fe45fda9401de3de4bb3` |
| `src/config.h` | `34d6d6bce215fc098c3c4ae8e2c4436cb66e50e4f73db81a7ef8da964ba242c6` |
| `tools/board_tool.py` | `0ba071553971374339fce2809780f32685567f4e7b46544557df75dddc25f255` |

One unchanged Trace forwards to one unchanged Runtime. The new observer counts
each active poll before one real step, preserves Runtime clock/epoch authority,
and freezes on callback failure, timing fault, invalid application, terminal
Runtime, epoch bound or poll bound in that order. The header bounds both counts
and prevents counter exhaustion before termination. Setup failure retains its
specified special priority. Pre-abort reports precede one diagnostic abort;
terminal/repeated calls remain passive.

Trace overflow is correctly treated as explicit retained-prefix truncation.
The unchanged Trace still updates first failure and timing faults after its
64-entry prefix fills. Neither rejected-count growth nor successful returned
callbacks is relabeled as complete native history. The default-disabled sketch
keeps empty peripheral/service grants, MATCH0/MOTORS0 enforcement, and the
existing explicit probe admission. It adds no motion authority.

The production diff outside the new bench contains only two count declarations
and their comment, plus four exact-name staging/refusal conditions. The final
diff shows no changes to Runtime/core/HAL, historical diagnostic sources,
locked tests, app-build policy or MATCH deployment policy. Generic upload and
dynamic registration remain refused. Existing fresh-owner, plain-path and
canonical shared-source safeguards apply to the new sketch.

## Independent tests and actual results

The reviewer inspected the oracles before their first execution. Their freeze
is [independent_test_freeze01.json](../analysis/P7_app_motor_observe_raw/independent_test_freeze01.json),
SHA-256 `cace89c936c94def39b9bc9b9fd49964240482bfbf798128521547a7c4a98f09`.
All three oracle files remain byte-identical to that freeze; no concrete fixture
bug or material coverage gap was identified.

Actual saved receipts establish:

- [New runtime driver](../analysis/P7_app_motor_observe_raw/runtime_first.json):
  10 methods PASS. Default bounds: 14 cases / 9,172,698 assertions in each normal
  and ASan/UBSan run. Copied 12/12 boundary fixture: 4 cases / 2,931 assertions
  in each mode. This includes 10,000 controlled epochs, 60,017 callbacks,
  64 retained calls and 59,953 rejected records; late failures and failed final
  cleanup, early polls, bound ties, clock anomalies, absent grants, invalid
  compile flags/bounds and sketch wiring are covered.
- [Unchanged D186 driver](../analysis/P7_app_motor_observe_raw/legacy_runtime_first.json):
  5 methods PASS, 14 cases / 23,885 assertions in each normal and sanitized run.
- [Selected unchanged locked checks](../analysis/P7_app_motor_observe_raw/locked_first.json):
  all four builds/runs exit0 without stderr. M0: 88 cases / 9,709,140 assertions;
  M1: 46 cases / 3,797,571 assertions; each normal and sanitized. These are the
  recorded selected countdown/Robot/edge/Gate/halt checks, not every locked file.
- Final LF tooling: [new Linux](../analysis/P7_app_motor_observe_raw/staging_linux_lf.json),
  [new Windows](../analysis/P7_app_motor_observe_raw/staging_windows_lf.json),
  [legacy Linux](../analysis/P7_app_motor_observe_raw/legacy_staging_linux_lf.json)
  and [legacy Windows](../analysis/P7_app_motor_observe_raw/legacy_staging_windows_lf.json)
  each report 10 methods, exit0 and unchanged pins. Linux skips the Windows-only
  junction method and executes symbolic-link cases. Windows executes real junction
  and simulated reparse checks, with 12 new / 7 legacy symbolic-link subcases
  skipped for missing privilege. Actual Windows symbolic-link creation remains
  unexercised; the platform scopes are reported rather than called skip-free.
- [Unchanged D162 trace regression](../analysis/P7_app_motor_observe_raw/trace_regression_corrected_command.json):
  3 methods PASS, 18 cases / 2,570 assertions in each normal and sanitized run.

The preserved [first D162 invocation](../analysis/P7_app_motor_observe_raw/trace_regression_first.json)
exited2 because the coordinator named the absent `test_motor_fault_diag.py`.
No test executed in that invocation. The corrected command names the existing
`test_motor_fault.py`; no implementation or oracle correction was made.

[normalization01.json](../analysis/P7_app_motor_observe_raw/normalization01.json)
records 354 CRLF pairs replaced in board_tool.py and unchanged AST. The pre-change
hash was `0060c20c1f7d7ea623183e9aa9786c5325482d7bdf89d4e8c4fec2bc68e99c9e`.
The final source diff retains the four reviewed condition changes, and all four
staging suites were rerun against the final LF bytes. Runtime/oracle sources did
not change, so their successful runs remain applicable.

All 168 pins in [final_freeze01.json](../analysis/P7_app_motor_observe_raw/final_freeze01.json)
were independently rehashed and match. Freeze SHA-256:
`c4f0a6c852095036187bcb81eae9fa968792470cca3c2c5481ae364ad74edc84`.
Compared with the first-run freeze, only the disclosed tooling newline pin
changes; the final freeze additionally records two unchanged D162 oracle files.
New runtime receipt SHA-256:
`50545a984aac13bf2fd2b2df277320ccc546229150bc0c676b09206aadb634e9`.

## Evidence limits and next action

Tests exercise controlled host callbacks/clocks, not sustained native execution.
They do not drive the unchanged rejected-counter saturation billions of times
or manufacture inaccessible malformed internal receipts. No new target image,
ABI/layout, native loading, measured duration, RAM/stack, WCET, physical acceptance
or human phase gate is established. Ten thousand epochs is not a measured ten
seconds. A blocking callback is not preempted by the returned-poll count bound.

`EPOCH_LIMIT` and `FROZEN` describe observation termination, not a successful
final halt. Any later native interpretation must separately inspect final
inhibition and cleanup failure evidence. D160/D161 remain unreproduced/unresolved.
Any target continuation requires a new reviewed artifact/source/identity/layout
scope and unused owners; this host review grants no upload/reset/capture action.
