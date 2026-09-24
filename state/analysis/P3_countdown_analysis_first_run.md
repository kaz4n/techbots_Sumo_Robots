# D127 first execution: inactive test injection

The original frozen public test hash `56d8b61f` ran on Windows (33 methods,
5 failures) and WSL (71 methods including 38 existing CSV tests, 4 failures).
Exact logs, commands, exit codes and original test/source bytes are retained in
`P3_countdown_analysis_raw/`. No firmware or established locked test changed.

Four failures share one test-harness cause: `validated_then()` patched the
standard imported validator module, while the analyzer loaded a separate
instance from its exact sibling file. Consequently, post-validation mutations
and descriptor-fault arming never occurred. The read-once case also passed
vacuously because its removal hook never ran. The analyzer's hash-bound reads
did not reject changes that had never happened.

The separate reviewer independently injected through file access and passed
seven private methods against unchanged production `1a91b857`, including changed
same-size/restored-mtime bytes, manifest read-once and 108 FIRST payload cases.
The reviewer agrees that this requires a correction to the new unaccepted test
fixture, not a production loader change.

Authorized correction: load one analyzer instance, discover exactly one loaded
dependency with the public `validate_bundle` capability and exact sibling path,
wrap that instance's validator, execute the same analyzer instance and require
exactly one hook invocation. Preserve every original safety assertion; make
fault-injection tests and the read-once check nonvacuous. Re-freeze before rerun.

Windows additionally lacked permission to create an actual symbolic link. This
is retained as an environment failure. The full symlink suite must execute on
WSL; no assertion is skipped or removed to claim a full Windows pass.
