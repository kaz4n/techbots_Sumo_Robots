# D188 fixed static diagnostic compile-only validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED / REVIEWED. Separate
fresh-context same-model review e6557e61 PASS/no open findings is recorded in
reviews/P7_app_motor_fault_compile_review.md. This is not cross-model review.
This is offline tooling evidence, not a target compilation or a phase gate.

Source commit6b6c883b adds tools/compile_app_motor_fault.py and
tools/app_motor_fault_compile_remote.py only. It reuses private pinned D185
execution and D187 static validation; generic build/upload admission is unchanged.
Final caller SHA256cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a;
remote SHA2561428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2.
No implementation changes followed the first test execution.

The fixed configuration is static/default/MATCH0/MOTORS_ALLOWED0/probe1.
It exclusively owns a fresh attempt, checks current source/boot/tool pins,
executes one properties query and one compiler, then checks the eight artifact
files and installed loader/TLS. Independent closing checks preserve the first
failure. Raw compiler/observation receipts remain separate from success status.
No upload, reset, MCU observation, generic static admission or actual manifest
was created or executed during this task.

| Evidence | Actual result |
|---|---|
| raw/remote_freeze.json, remote_first.json; e200477c/672da5c7 |14/14 independent WSL methods PASS, no skips,1.736s;11pins unchanged. Actual pinned loader/TLS plus synthetic ELF fixtures; no board. |
| raw/caller_freeze.json, caller_first.json;4930d9ac/caca776a |36 setupERRORs from new fixture class/instance mismatch; no test bodies ran. Original retained. |
| raw/caller_corrected_freeze_2.json, caller_corrected1.json;1dbfe31b/903555b9 |39/40 PASS; one correctly early constructor refusal escaped the fixture assertion. Original retained. |
| raw/caller_final_freeze.json, caller_final.json;ad9f771a/11326551 |40/40 independent WSL methods PASS, no skips,34.800s;134pins unchanged. Includes actual preflight and controlled complete pipeline, timeout/write failures and independent closing. |
| raw/windows_composition_first.json |Python3.13.11/zlib1.3.1, actual source bundle/Windows framing29,664 UTF16 units including NUL, below unchanged30,000 limit. Synthetic boot and replaced transport: zero native dispatch. Not a full Windows test-suite run. |
| raw/integrity.json |134pins current;17 owned committed blobs byte-exact; protected firmware/bench/host/locked/shared-tool/historical-validator diff against50cda7fa empty. Longest new function35lines. |

Here raw/ means analysis/P7_app_motor_fault_compile_raw/. Tests were independently
derived from the committed contract and declared APIs; the author did not read
new implementation bodies. The coordinator and separate same-model reviewer
approved only new-fixture corrections: bind git_state on an owner instance;
compare CalledProcessError first_error with its exact type/message while retaining
exception identity/stderr assertions; include construction in the hard-pin
rejection assertion. Four actual-preflight cases were added. No established or
locked test was amended, skipped or weakened. All original failures remain.

C: unexpectedly filled during the first corrected-freeze save. The zero-byte
draft and checkpoint_enospc.json preserve that failure; the suite had not run.
Subsequent receipts were saved first under the small WSL recovery directory and
then copied to the repository. Git commit1dbfe31b preserved the corrected oracle
before rerun. Free-space recovery was independent of cleanup and is not savings.
Completed fixtures left zero /dev/shm/sumox-d188-* remnants. Small recovery
copies remain temporarily useful while this session has unstable disk space.

Next eligible native task, after hardware work resumes: freshly observe board
identity/tool pins and prepare a reviewed inputs_static.json for this exact
source21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950.
Only then invoke the fixed compile-only caller with the reviewed clean HEAD.
Actual static ET_EXEC/package/init/ABI and later capture bindings must be newly
established; D149 addresses and the D1732592B decoder are inapplicable. Original
full-app IO fault, physical input qualification, RAM/stack/WCET, release/rehearsal
and human phase gates remain unresolved. Do not infer them from these host tests.
