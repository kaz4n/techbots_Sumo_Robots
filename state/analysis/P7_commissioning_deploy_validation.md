# D227 independent deployment validation

Status: PASS for the focused host scope. Linux's first complete 29-method run
passes on FINAL03; Windows original coverage and targeted repair checks close.
The two independent-review config findings are reproduced and repaired. No native action,
board read, upload, motor run, physical qualification or human phase gate occurred.

## Scope and oracle

The independent test owner modified only the two new tests and this validation/raw
evidence. The production owner modified the two new deployment tools. Existing
MATCH, D222, firmware/config and locked sources were not edited by the test owner.
Four missing historical fixture files were hydrated byte-for-byte from this
worktree HEAD to reuse accepted synthetic ELF/metadata builders; historical suites
were not run. Tiny temporary repositories provide real Git commits and blobs.

`P7_commissioning_deploy_raw/oracle01.json` freezes the initial 27 methods before
reading/importing new production. `oracle02.json` strengthens the command bound
to the contract's 30,000 UTF-16 units including quoting/NUL. `oracle03.json` adds
mandatory valid baseline admission before every deployment method and a precise
Git-blob mismatch assertion. `oracle04.json` corrects only the inherited metadata
fixture's explicit Arduino data directory. `oracle05.json` adds two regression
methods from independent review, for 29 methods total. Original changed test
versions and production FINAL01/FINAL02 are retained beside these manifests.

The matrix covers seven fixed profiles times M0/M1; complete D222 compile receipts,
metadata, layout, package and loader bindings; real Git blob identity despite a
coherent replacement manifest; inhibited grants versus operational qualification;
request-bound physical/gate/auth records; exact JSON, path and scalar types; local
check-only behavior; one upload, consumed ownership, UNKNOWN timeout without retry;
independent closing; and evidence-write failure. Adapter checks cover closed
profile construction, artifact paths and M flags, frozen dependencies, command
isolation/length, envelope identity, report shape and reply refusal.

Fixtures explicitly label source, receipts, measurements and authorization as
synthetic. They exercise validation mechanics and do not establish hardware facts
or grant permission. Native commands are only constructed; transport callbacks
are mocks. Local Git subprocesses operate solely inside temporary fixture repos.

## Retained attempts and adjudication

Every attempt directory contains exact commands, five source/contract/test pins,
unmodified stdout/stderr, elapsed time and an input-unchanged result. All completed
attempts below recorded unchanged inputs.

| Raw attempt | Result | Disposition |
| --- | --- | --- |
| `first_windows01` | 27 methods, exit 1; all nine adapter methods pass | Actual FINAL01 defect: required `result.artifact_sources_identity` does not exist in D222's result. Invalid initial baseline also prevented downstream negative-test claims. |
| `corrected_windows02` | 18 deployment methods fail baseline setup | Fixture defect: inherited envelope defaults to `/synthetic/arduino-data`; D222 uses `/home/arduino/.arduino15`. Production correctly refused. |
| `corrected_windows03_check` | One valid baseline/check-only method passes | Explicit fixture data-dir repair confirmed through full admission. |
| `corrected_windows03_remaining` | 15 of 17 methods pass; two setup errors | Inherited `compile_ordinary_app_static._read_handle` refused `compile_app_motor_fault.py` as changed while reading, before D227 admission. |
| `corrected_windows04_two` | Both affected methods pass unchanged | Platform-sensitive inherited read-identity refusal retained; no production/oracle weakening or automatic retry was introduced. Exact timestamp cause was not established independently. |
| `counterexamples_windows05` | Two new methods fail with seven invalid cases admitted | Actual FINAL02 parser and operational button-window gaps; source repair required. |
| `repaired_windows06` | All 14 tuples and five invalid button variants pass; decoy method setup error | Inherited `compile_b4_app_static._read_handle` refuses `compile_ordinary_app_static.py` before D227. FINAL03 and test pins unchanged. |
| `repaired_windows07_decoys` | Decoy method passes unchanged | Both config findings closed by focused Windows checks; earlier inherited setup error retained. |
| `first_linux01` | All 29 methods pass on FINAL03; 52.763 s tests / 66.265 s controller | First complete Linux run, with source/contract/test pins unchanged. |

The source defect was confirmed independently against the actual D222 result
field construction; `result_field_observation01.json` preserves the observation.
FINAL02 removes only the nonexistent result-field requirement. All nine required
closing statuses, including `artifact_sources`, remain mandatory.

The metadata repair passes `data='/home/arduino/.arduino15'` to the inherited
fixture envelope. It changes no production code or assertion. Mandatory valid
baseline admission prevents unrelated early rejection from satisfying negative
tests.

Independent review's parser counterexamples combine an inactive conditional or
string containing a valid zero grant declaration with an active `(1U)` expression.
FINAL02 admits both as M0; a comment-only decoy is already refused. Operational
counterexamples set `BUTTON_WINDOWS_CONFIGURED=1` while ranges are all zero,
reversed, overlapping, sharing inclusive endpoints, or exceeding 16383. All five
are admitted by FINAL02. Their original failures are retained, not replaced.

FINAL03 (`deploy_commissioning_app.py`, 28479 bytes,
`d5f6e5f9e7cae19b74294422b29cb83111de722fd4e6f8b5a828f67d21033213`)
masks comments and ordinary string/character literals, refuses ambiguous raw
strings/line splices and conditional or extra protected references, and requires
the protected literal declarations to account for the remaining names. It parses
both four-element button arrays and applies the existing inclusive 14-bit ADC
range rules plus pairwise disjoint ranges for M1. M0's disabled/default config
remains admissible. The adapter and contract remain unchanged.

Final tested identities (SHA-256):

| File | Bytes | Digest |
| --- | ---: | --- |
| `tools/deploy_commissioning_app.py` | 28479 | `d5f6e5f9e7cae19b74294422b29cb83111de722fd4e6f8b5a828f67d21033213` |
| `tools/commissioning_app_upload.py` | 13772 | `6fe131d2d7dbffa1af54bebaf080a0deababee5e08a2286f1abed943ddede765` |
| `state/analysis/P7_commissioning_deploy_contract.md` | 10696 | `9a8c36c7d62b321230ae9f6c7a135f79e11853c054dafeecc00c331b26190220` |
| `tests/tooling/test_commissioning_deploy.py` | 30152 | `ceec69cac41352d2c14a5271fe2a5ec5f0f1d0904f9adc5f49b46fe1661046d4` |
| `tests/tooling/test_commissioning_app_upload.py` | 11197 | `fd358fb3300f07eef2a82898e100682289289a6a2c61fe85d8de047308e1d59a` |

Windows used Python 3.13.11; Linux used WSL Ubuntu Python 3.12.3. Windows did not
repeat the entire suite after each bounded repair: original nine adapter passes,
corrected 18 deployment passes, and FINAL03's two regression methods plus valid
14-tuple method are retained separately. Linux ran all final 29 methods together.
Windows's inherited read-identity refusals on fresh temporary copies remain an
observed fail-closed limitation; successful unchanged reruns do not prove that
the platform-sensitive refusal cannot recur.

Source-author pre-freeze observations, not independently reproduced by this test
owner: Windows named/descriptor ctime mismatch in the new bootstrap was repaired
to inherited D222 stamp semantics; oversized full-adapter payload was replaced by
the contract's checked native-only prefix. The focused adapter command-bound test
passes. These observations are not board/runtime validation.

## Reproduction and limits

From this isolated worktree, invoke
`python -B state/analysis/P7_commissioning_deploy_raw/run_focused.py windows NEW_ATTEMPT tests.tooling.test_commissioning_app_upload tests.tooling.test_commissioning_deploy`
or select `linux` for WSL Ubuntu. The controller permits only these focused test
names, creates a fresh evidence owner and imposes a 600-second child deadline.
Use a new attempt name; do not overwrite prior evidence. Failed methods are
rerun specifically after adjudication. No full historical suite or hardware job
was run. `validation_receipt.json` indexes every retained attempt and final pins.

Completed temporary fixtures auto-clean; bytecode is suppressed. Unique test,
review and source failures are retained. No real compile artifact, source file,
credential or Git history was deleted. These host results cannot qualify the
board, physical controls, ring/stand setup, firmware timing or actual uploading.
Final inspection found no `sumox_d227_*` fixture directories in Windows Temp or
Linux `/dev/shm`. The retained raw evidence occupies 329,950 bytes. No manual
deletion batch was needed; fixture cleanup is the registered test lifecycle.
