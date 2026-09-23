# D113 independent author validation

PASS: final isolated Linux run executed **75 unittest methods**: 42 new methods
(14 host/API, 28 actual generated receiver/observer script methods) and all33
unchanged D090 methods. There were zero failures, errors, skips or process timeout.
The D090 registry method also ran its original18 checks under the already approved
D093/D096 additive invocation context; no old expectation or assertion was edited.

Final test SHA-256:
`c864142fed553356254cdbfc97d7cdccf41eb2b4a78ed4a1cc4537292445fe44`.
Final tested production SHA-256:
`5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717`.
Untouched D090 test SHA-256 across every run:
`06c5bf9997d627d85eeb7c2eff9a4448f1267a7e67cf6cea068333491c21a67a`.
Exact command, elapsed time, all copied tool hashes, result and logs are in
`run4_final_command.json`, `run4_final_source_copy.json`,
`run4_final_summary.json`, and `run4_final_unittest_full.txt`.
`validation.json` joins all four executions and their exact identities.

## Preserved failures and amendments

1. Initial40 methods froze before implementation execution at fdf7e9bd. Root then
   approved one additive environment-validation method, freezing41 at d4b32d61.
   The exact insertion-removal proof and both snapshots remain in `freeze.json`,
   `environment_amendment.json`, and the adjacent frozen files/diff.
2. First run on production1492b81d executed74 methods and retained35 subtest/method
   failures plus3 errors. All host methods and all33 D090 methods passed. Remote
   fixture confinement was incorrect: logical `/` passed through to the real WSL
   root, allowing dirfd-relative `tmp` to bypass the synthetic tree. The fixture
   also lacked stdout.buffer and rendered exceptions while paths were patched.
   These are fixture failures, not established product failures. Initial evidence
   is preserved in `run1_*`; its claimed confinement must not be treated as proved.
3. Independent reviewer approved the narrow first fixture repair: map root into
   the synthetic tree; resolve dirfd-relative stat/lstat bookkeeping consistently;
   supply binary-backed text stdout; format exceptions after unpatching. All41
   test-method ASTs and other source bytes were unchanged. The exact diff, proposal,
   frozen07d09db6 file and reviewer receipt are retained. Corrected run2 passed74
   methods against the same1492b81d production bytes.
4. The reviewer found missing explicit SUMO_TRANSPORT still reached transport for
   both new CLI modes. Root authorized one additive regression, freezing42 methods
   at c864142f before its execution. Targeted run3 failed both new-mode subtests on
   unchanged1492b81d. `missing_transport_*` preserves the exact addition and red
   receipt. This is a confirmed production finding, distinct from the fixture work.
5. Worker froze the narrow explicit-transport correction at5a78257a. All42 new
   methods and all33 unchanged D090 methods passed in run4 without further test
   edits. The original red run remains available; no assertion was relaxed.

The exact real WSL path `/tmp/sumox26-dump-connection-0123456789abcdef0123456789abcdef`
was subsequently inspected read-only and was absent at that observation. See
`first_fixture_real_tmp_inventory.json`. No cleanup was performed. This does not
prove the broken initial fixture never attempted or temporarily created it.
An auxiliary diagnosis could not reopen its transient /dev/shm copy; the separate
reviewer's fixture inspection supplied the root cause. No board was contacted.

## Independence and limits

The author read public contracts/headers and existing test fixtures only, keeping
production bodies opaque. Actual generated remote Python was captured through the
public board.remote seam and executed with synthetic clock/socket/Linux state;
actual no-replace publication used confined real Linux file descriptors. Exact
byte/timing/lifecycle predicates are described in `coverage.md`. Source copies were
isolated; unrelated coordinator board_tool staging changes are separately hashed
in each receipt and were not treated as D113 receiver changes.

This is a reused independent author context with the same model, not a fresh
repository context or a cross-model review. No board smoke, remote SSH/ADB process,
MCU command, router registration, UART cleanliness/exclusivity, OS WCET, physical
button qualification or motor authorization was established. Continuous atomic
attachment is not claimed. The final source reviewer and coordinator own any later
exact deployment/readout scope. No hardware action follows from these test results.
