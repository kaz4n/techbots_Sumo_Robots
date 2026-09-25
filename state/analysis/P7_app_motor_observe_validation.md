# D192 longer inhibited observation - host validation

26 September 2026. The new `bench/app_motor_observe` runs the unchanged real
application Runtime through the unchanged MotorGate trace for at most 10,000
application epochs or 10,000,000 polls. It preserves the first 64 callbacks and
explicit loss counts while independently retaining the first failure after that
prefix fills. Callback, timing, application and runtime faults outrank limits.
A pre-abort snapshot distinguishes the initiating state from the diagnostic halt.

This is HOST-VERIFIED preparation. No D192 target build, firmware upload, native
ABI/capture or physical acceptance is claimed. The D190 inhibited four-epoch
image remains the last uploaded firmware. Its historical full-app fault remains
unreproduced and unresolved. No motor permission or phase gate follows.

## Changes and fixed identities

The contract is `P7_app_motor_observe_contract.md`, SHA256
`74ceaa0a638168237ccc8b32696764e12fb626721d7b71d9694f6c6b867488f2`.
The new sketch and two Runner files have hashes `1df77ff5`, `25bf299b`,
`eec10eac`. Config `34d6d6bc` adds only two dimensionless count constants.
The trace, native callbacks, old diagnostic and locked tests are unchanged.
`board_tool.py` changes four name checks to stage the new project with the same
fresh-owner/plain-source/shared-trace rules and to refuse generic flashing.
It does not register a dynamic build or deployment route.

The independent author read the contract and public interfaces, not the new
implementation. Three frozen oracles are `ccc727e5`, `729425a0`, `fdcd0458`;
full hashes are in `P7_app_motor_observe_raw/independent_test_freeze01.json`
(`cace89c9`). A separate same-model reviewer checked source and frozen coverage
before first execution. Final freeze contains 168 exact input pins.

## Actual results

| Check | Result |
|---|---|
| New runtime driver | 10/10 methods pass; no skips |
| Default 10,000-epoch C++ cases | 14 cases / 9,172,698 assertions pass, normal and ASan/UBSan |
| Copied 12-epoch / 12-poll boundaries | 4 cases / 2,931 assertions pass, normal and ASan/UBSan |
| New staging | Linux and Windows pass with complementary platform skips described below |
| Existing D162 Trace | 3/3 methods; 18 cases / 2,570 assertions pass normal and ASan/UBSan |
| Existing D186 runtime | 5/5 methods; 14 cases / 23,885 assertions pass normal and ASan/UBSan |
| Existing D186 staging | Linux and Windows pass with complementary platform skips |
| Locked inhibited safety | 88 cases / 9,709,140 assertions pass normal and ASan/UBSan |
| Locked host-only enabled MotorGate | 46 cases / 3,797,571 assertions pass normal and ASan/UBSan |

New cases verify exact 60,017 callbacks / 64 retained / 59,953 rejected at the
healthy bound; first-prefix preservation; every late operation failure including
epoch 10,000; cleanup failure without rewriting the initiating reason; callback
versus timing and epoch versus poll ties; clock reversal/wrap/stall/skip; missing
callbacks; absent peripheral/service activity; unsafe flags and invalid bounds.
The enabled locked tests use a HOST fake port, not the UNO Q or a powered run.

Each staging driver has 10 methods. Linux skips its one Windows-junction case;
Windows executes that case but lacks symlink-creation privilege (12 new / 7 old
subcase skips). Linux executes those real symlink cases. Metadata-reparse guards
run on both. No assertion failed. Default and copied-bound Runtime tests do not
fabricate malformed internal receipts or execute billions of calls to overflow
the unchanged uint32 loss counter; those coverage limits remain explicit.

All first outputs are retained under `P7_app_motor_observe_raw`. The initial
Trace-regression invocation used the nonexistent filename `test_motor_fault_diag.py`
and exited 2 before test loading. `trace_regression_first.json` preserves this
coordinator command error; it is not a product or oracle failure. The corrected
existing driver is `tests/tooling/test_motor_fault.py`; all three methods passed.

After first passes, `board_tool.py` alone was normalized from mixed CRLF to LF to
preserve exact tested bytes in Git. `normalization01.json` records 354 replacements
and equal parsed ASTs; final hash is
`0ba071553971374339fce2809780f32685567f4e7b46544557df75dddc25f255`.
All four affected staging invocations were repeated and passed unchanged oracles.
No firmware or C++ oracle changed, so their successful builds were not repeated.

## Evidence and next task

Receipts include `runtime_first.json`, `legacy_runtime_first.json`,
`locked_first.json`, both first staging platform receipts and four `*_lf.json`
receipts. Commands, stdout/stderr, status, elapsed time and pin comparisons are
saved rather than inferred. The independent review is
`../reviews/P7_app_motor_observe_review.md`.

Next: finish the new fixed static compile projection and independent validation,
prepare fresh source/board/owner admission, and compile once under a clean reviewed
HEAD. Observe actual artifact/ABI/entry layout before defining a new finite native
capture. Historical compile/upload owners and address layouts are not reusable
permissions or current artifacts. The longer observation does not finish the
commissioning, production-memory, native-recorder or physical release work listed
in `P7_completion_audit_20260926.md`.
