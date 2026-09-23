# D085 coordinator tooling invocation failure

Two root invocations of unchanged `tests/tooling/test_tools.py` failed with31
subtest failures and4errors each. Receipts: P2_qtr_native_raw/tooling_final and
tooling_after_manifest. They ran Windows Python, which launched Windows bash/WSL
with untranslated C: paths and attempted privileged Windows symlinks. The first
diagnosis that the pending inert manifest explained these failures was wrong.
The exact trace instead shows bash exit127 and WinError1314. No production/test
change repairs this environment mismatch; the established suite requires Linux.

The separate earlier adoption command really did fail because its reviewer
receipt was not yet present. Once approval was persisted, exact5key adoption
passed. That failure is distinct from the Windows tooling invocation error.

Escalated the repeated invocation failure and diagnosis to the fresh reviewer.
Next bounded correction: run the unchanged suite through WSL Ubuntu with its
Linux temporary directory, preserving all assertions and original failed outputs.
No new hardware operation, approval bypass, symlink privilege change or test skip.
The result will be recorded as tooling_linux_final, not overwrite either failure.

Resolution: the unchanged WSL/Linux run passed25methods in18.899s, exit0,
recorded in tooling_linux_final.json/.txt. No implementation or assertion changes.
