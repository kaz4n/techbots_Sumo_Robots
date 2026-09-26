# D195 fixed observer caller and actions

26 September 2026. Prepare only new run.py and actions.py beneath
state/analysis/P7_app_motor_observe_run_raw. Reuse the D190 fixed caller/action
lifecycle, not a new transport framework. Preserve all historical files/owners.
This supplements P7_app_motor_observe_remote_contract.md c2563449; host tests
and independent review precede separately admitted native use. Actual D194
entry review d1a09f19 is PASS. D196 current scratch cleanup remains separate.

## Fixed inputs and substitutions

Original run02.py is24869B SHA0adabfc352a4bcefaf87728e08ab12c1c9c5d85271b3548544b6609095666615;
actions_run02.py is12069B SHA4eeb19f1923b5058a3df69ecd196d5f331e9e9f51ca1193f6c7026ca837ee0fb,
both in state/analysis/P7_app_motor_fault_run_raw. Fixed legacy transport,
action framing, upload/capture/helper sources and their hashes stay unchanged.
Only observer metadata, successful ABI02 evidence, D193 source projection and
new pre-sample wait validation described below differ.

Use source3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0,
run app-motor-observe-3a08ddeb-run01, board2629958581. Replace fault app names
with observe, original run02 source names with run.py/actions.py/remote.py,
preparation_run02.json with preparation.json, inert_run02_scope.json with
inert_run01_scope.json and native_inert_run02 with native_inert_run01.
All schema prefixes are app-motor-observe (fixed-app-motor-observe where fixed).
The separate immutable stage is /home/arduino/sumox26_codex_build/ plus run ID
plus -adapter; only its remote.py child is pushed, exactly11357B SHA
98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db.
All local/remote owners must be unused and are consumed even on uncertainty.

D193 manifest inputs_static.json SHA
aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e
has128 exact input pins and app-motor-observe-static-inputs-v1 schema. Preserve
all pin reads/source-name checks. Replace diagnostic launcher pin with
tools/compile_app_motor_observe.py7583B SHA
70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827.
Privately load this checked module then its load_caller(root=ROOT), using the
projected CompileDiagnostic.source_names/source_mapping with the existing
root/base owner seam. Its three exact original sources/projected hashes remain
checked by that launcher; never execute its main or compile/build/claim path.
Do not directly use the unprojected old CompileDiagnostic for observe source.

Use build app-motor-observe-static01, sketch app_motor_observe, exact raw95344B
SHAf1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc,
package95360B SHA85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c.
Preserve exact canonical local upload/capture bindings comparison before claim,
original installed dependencies/absence lists and immutable command state.
No arbitrary source/profile/root/transport option is added for native use.

## Provenance and scope

Preparation retains exact keys schema,run_id,source_sha256,bindings,files;
bindings exactly upload/capture; files maps exact paths to bytes/sha256.
Required provenance is exactly these12 files, with C meaning
state/analysis/P7_app_motor_observe_compile_raw/ and R meaning state/reviews/:

- C inputs_static.json
- C native_static01/result.json
- C native_static01/artifacts.json
- C native_abi_static02/result.json
- C native_abi_static02/local_result.json
- C native_abi_static02/abi.json
- C native_entry_static01/result.json
- C native_entry_static01/local_result.json
- C native_entry_static01/entry.json
- R P7_app_motor_observe_compile_actual_review.md
- R P7_app_motor_observe_abi02_actual_review.md
- R P7_app_motor_observe_entry_actual_review.md

The new check_evidence keeps compiled COMPILE_CHECKED/source/boot/first_error
and ARTIFACTS_CHECKED predicates. ABI02 local result must be STATIC_ABI_OBSERVED
with first_error None; ABI summary must be STATIC_ABI_OBSERVED. Preserve raw
ABI02 result as a pinned provenance input. It is successful file evidence, so
remove only the obsolete FAILED-original/OFFLINE_ABI_INTERPRETED predicates;
never alter/reinterpret the original FAILED01 receipt. Entry local result must
be STATIC_ENTRY_OBSERVED with first_error None and entry summary same status.
Actual provenance hashes are frozen in coordinator preparation, not editable
native options or invented runtime evidence.

Scope retains exact six keys schema,run_id,board,source_sha256,expected_identity,
files and plain SHA256 values. Required scope file keys are exactly:

- state/analysis/P7_app_motor_observe_run_raw/preparation.json
- state/analysis/P7_app_motor_observe_run_raw/run.py
- state/analysis/P7_app_motor_observe_run_raw/actions.py
- state/analysis/P7_app_motor_observe_run_raw/remote.py
- tests/tooling/test_app_motor_observe_run.py
- tests/tooling/test_app_motor_observe_actions.py
- tests/tooling/test_app_motor_observe_remote.py
- state/analysis/P7_app_motor_observe_caller_contract.md
- state/analysis/P7_app_motor_observe_remote_contract.md
- state/reviews/P7_app_motor_observe_caller_review.md
- state/reviews/P7_app_motor_observe_remote_review.md

No scope/preparation self-hash. Keep reviewed clean committedHEAD, unchanged
local/source/ADB checks, exact fresh board identity, exclusive owner and bounded
command count. Check-only is local admission only and may not create an owner,
stage a file, access the board, upload/reset or capture memory.

## Action validation delta

Keep public build_command(action,sources,bindings,adapter_pin), validate_reply
and run_actions interfaces and all framing/sequence/first-error/closure guards.
Keep exact11 action-envelope fields and returned-only success, 65536B reply,
196608B decoded payload and30000UTF16 command bounds, pinned three inline
sources, checked staged adapter before and after execution. Retain durable
unattributed fallback as failure when an outward/close error occurs.

Read plan has exactly26 commands/reads727152B with12 SRAM snapshots, unchanged
six addresses/sizes and full four flash comparisons. Package span95360 affects
the two sketch bracket chunks only. Keep report.wait exactly2seconds and all
existing start/end/time/type tests. Add precisely analysis.pre_sample_wait to
analysis's exact key set. It must have exactly requested_seconds,before,after;
requested_seconds is an int equal30 (bool rejected), both times finite int/float
excluding bool. Require started_monotonic <= before <= after <= wait.before,
after-before >=30, and existing wait.after <= finished_monotonic plus >=2gap.
This successful receipt check rejects absent/null/short/backward/nonfinite/
misordered wait and unknown fields. No terminal/FROZEN/epoch assertion added.
Failure envelopes still retain raw partial result and wait evidence; never
turn an inner COLLECTED result into success after any outer failure.

## Unchanged execution and controlled tests

Run keeps InertRun(reviewed_head,*,root=None), old test seams and exact CLI
--check-only/--execute with --reviewed-head. Import privately composes local
checked code only. Actual commands and underlying lifecycles stay original:
seven allowlisted labels,13transports on complete success (2stage,1upload,
1capture,3each of3prerequisites),1dispatch per stage/action and3per prerequisite.
Stage durableintent precedes claim/push and push requires verified claim.
Upload195s/capture630s/prerequisites60s, remote upload180s/capture600s unchanged.
No retry, automatic reset, loader substitution, extra read or deletion.

Independent oracles must freeze before reading implementation. Preserve all
old test_run.py20 and test_actions.py13 fixture methods/assertions by private
metadata/fixture projection; adapt only old ABI fixture shape to actualABI02
success,128source inventory and successful capture's extra recorded30swait.
Do not weaken old safety/error/order assertions. Supplement exact source mapping
through the projected D193 launcher, old manifest/source/artifact refusals,
wrong ABI02 status/error and direct failed-predecessor rejection; successful
wait validation plus each invalid shape/type/time/order/count, actual framed
capture/upload payload identities/pins/command bounds, and no native check-only.
Mock filesystem/clock/transport only; no real board or sleep in tests. Preserve
first failures, freeze every input, test Windows and Linux serially, separately
review source and actual receipts before creating final scope. Native success,
physical behavior, callback history completeness, atomic coherence, liveRAM/
WCET and human phase gates remain separate evidence.
