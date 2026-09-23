# D107 independent policy tests

2026-09-23. Scope: new `tests/tooling/test_opp_view_policy.py` only, plus this raw
evidence directory. The author used the D107 target-correction contract, D099/D100
contracts, existing runtime-inert test API usage, independent compiler fixture,
and public tooling signatures. Edited tooling bodies were not read. No hardware
or network operation occurred; all transport calls were substituted.

The test file was frozen before root's narrow policy edits and before any test
execution: SHA256 `59155eebc8905f9b16ce00ccfa917ec8391237511557b31c8c96a643f220d59a`.
`first_freeze.json` also identifies the contract and unchanged source fixture;
`test_opp_view_policy_first.py` preserves the exact test bytes.

First execution passed all15 methods in1.004s, exit0, no skipped tests. Actual
symlink and dangling-symlink cases ran under WSL. No test assertion or fixture was
changed after this freeze. `first_run.json` records the exact invocation and
identical before/after test/tool/fixture hashes; stdout and stderr are retained.

Coverage includes default/Immediate validation and preflight, mixed project
references, inert flags, boot metadata/hooks, library rejection, command/hook
mutation/removal/addition, all installed pins and four selected artifact names,
pre-transport MATCH/upload/profile refusals, unchanged app/runtime/generic routes,
and propagation of checked-build failure without fallback or upload.

Existing D100 wrapper-order tests are unchanged and remain a separate root-run
regression check. Controlled fixture tests do not establish target compilation,
actual constructors/imports, loader capacity, physical behavior or upload approval.
