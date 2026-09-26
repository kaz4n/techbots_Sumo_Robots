# D221 fixed inhibited B4 upload-only preparation

D051 and the user's BOARD ONLY instruction support preparation of one fixed
MOTORS_ALLOWED=0 B4 upload. This document authorizes no native attempt, cleanup,
credential use, sensor grant, motor-capable build or human gate. D219 remains a
separate capture-only caller; no capture action or synthetic predecessor belongs
to this upload path. All older files and consumed owners remain unchanged.

## Fixed artifact, API and owners

Source is 9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.
Use accepted D214 app.ino artifacts from
/home/arduino/sumox26_codex_build/b4-app-m0-static01/build, default startup and
arduino:zephyr:unoq:link_mode=static. Flags are exactly D214's MATCH=0,
MOTORS_ALLOWED=0, SUMOX_B4_STAND=1 and all other commissioning/probe profiles0.
Configured setup grants remain zero. Source identity alone does not distinguish
ordinary and B4 builds: exact raw/package pins and compile flags are mandatory.

Raw app.ino.bin is82896 bytes,
6fcad2f09c90bbc7dd72760e7a794305811d042a9d2e578e03d5154cc368a471.
Packaged app.ino.bin-zsk.bin is82912 bytes,
84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28.
Installed loader and platform/tool pins retain accepted D212 values.

RUN_ID is b4-app-m0-9044ebbb-load01. Remote staged owner is
/home/arduino/sumox26_codex_build/b4-app-m0-9044ebbb-load01-adapter, containing
remote.py. Upload owner appends -upload to RUN_ID under the same parent.
Local exclusive owner is state/analysis/P7_b4_app_upload_raw/native_upload01;
scope is upload01_scope.json in that raw directory. No owner is created during
preparation, reused, repaired or automatically retried.

tools/upload_b4_app.py exposes UploadRun(reviewed_head, *, root=None), admit(),
run(), and main(argv=None). CLI takes exactly one --check-only or --execute and
--reviewed-head forty lowercase hex digits. Check-only is local admission only:
no native call or owner creation. Python -B, exact clean committed HEAD, all pins,
plain paths, checked ADB executable/serial and fixed UID1000/boot are required.

## Exact native adapter reuse

New remote.py retains D212 remote.py's load_dependencies, selected_profile,
_artifact, checked_upload_bindings and upload bodies with only B4 module/profile,
owner, build-path and artifact metadata changes. Remove all capture functions,
read plans and SRAM window constants. Keep helper, capture-support and uploader
dependencies byte-identical and privately loaded from supplied source snapshots;
the support dependency name does not grant a capture operation.

selected_profile still passes the existing raw file to arduino-cli upload with
--config-file /dev/null, exact static FQBN and unchanged staged source path.
upload invokes the unchanged upload_remote.upload_loader. Its descriptor-bound
admission, installed/source pins, directory selections, all override absences,
/tmp/remoteocd absence, process check, exclusive output, 180-second budget,
bounded child, file-size cap2303728, raw streams, first error, final checks and
all descriptor closing remain untouched. Only a clean returned UPLOADED result
can become successful local evidence. A durable file alone is unattributed.

## Actions and returned report

New actions.py exposes checked_source, build_command(action,sources,bindings,
adapter_pin), validate_reply(action,reply), and run_actions(operations).
Only exact str action upload is accepted. sources has exactly helper/support/
upload raw-byte entries with D212 dependency pins. bindings and adapter_pin must
equal the fixed B4 selections with exact scalar types. No parameter chooses a
build, profile, FQBN, motor flag, output path or second action.

Reuse D212 canonical JSON, strict duplicate/nonfinite handling, bounded single
BZ2 member and canonical base64/base85 framing. Payload limit196608 bytes;
full native Windows argv <=30000 UTF-16 units including NUL. Inline source pins
are checked before source execution. Bootstrap dispatches upload only, holds one
root descriptor, reads the exact staged adapter, passes all three dependency
snapshots, and rechecks adapter bytes plus closes root independently in finally.
No installed p0 module or capture branch is needed. Preserve the earliest error.

Envelope keys are schema,action,run_id,source_sha256,report,report_origin,
remote_result_path,full_result_bytes,full_result_sha256,first_error,
postcheck_errors. Schema b4-app-upload-action-v1, action upload, fixed identity
and output/upload_result.json. report_origin=returned only after uploader returns
through all descriptor closing. Failed-return fallback may retain a canonical
durable report as durable_unattributed, never successful. Full report length/hash
cover the actual full canonical report; stdout/stderr are omitted only from the
returned compact report. Envelope <=65536 bytes. Use unchanged D212 upload report
validation with B4 schema metadata: one attempt, reaped true, returncode0,
timed_out false, clean errors, nonnegative finite clocks and duration<180.

run_actions requires exactly five callables local,prerequisites,intent,upload,
finish. It runs local, prerequisites, intent(upload,None), increments the sole
attempt, calls upload and validates its returned reply. Then independently
attempts local and prerequisites closing even after failure. Result keys are
schema,status,upload,upload_attempts,first_error,postcheck_errors; schema
b4-app-upload-sequence-v1. COMPLETED requires no errors; finish errors force
FAILED and remain attached as sequence_result. No capture field/counter/receipt.

## Caller seams and nine-call ceiling

Privately load pinned D212 run.py with its sole top-level actions import replaced
by the checked new actions module. Preserve pinned ancestors and accepted head,
source inventory, baseline, capability, staging, descriptor/owner, transport,
state, first-error, diagnostics and finish algorithms. Bind current B4 manifest
130 inputs (fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c),
D214/D215/D217 results and independent actual reviews. Validate successful
compile/ABI/entry states and exact compile flags/FQBN/project. Preserve source
mapping9044ebbb and staged-source capability comparison.

Preparation has exactly schema,run_id,source_sha256,bindings,files; schema
b4-app-upload-preparation-v1; bindings exactly {upload: fixed binding}. files is
the closed plan01 provenance map of byte counts/hashes. Scope has exactly schema,
run_id,board,source_sha256,expected_identity,files; schema
b4-app-upload-native-scope-v1 and the ten closed files listed in plan01.json.
The coordinator creates the final concrete scope after independent host review.

Successful transport order is exactly: adapter-claim, adapter-push;
cli-initialization,cli-builtin-files,capabilities; upload;
cli-initialization,cli-builtin-files,capabilities. Stage/upload labels occur at
most once, prerequisite labels at most twice, total at most9. A new narrow guard
enforces these limits before inherited transport, whose allowlist, consumed
intent, durable receipts and error/owner checks remain. Upload outer timeout195s;
other calls60s. No capture/retrieve command enters the fixed allowlist.

Claim records only this upload owner. Upload intent requires stage_ready and
predecessor None, and uses the inherited actual-intent ordering. Inherited action
is reached only for upload. Staging failure performs independent local and
prerequisite closing and uses the same upload-only result structure. Success
counters require all nine commands, exact stage/action sets and one upload.
Unrelated untracked paths refuse; only the exclusive local owner is admitted
after claim. No successful result can contain collected local/prerequisite/
transport/finish errors. Inputs close through the accepted inherited checks.

## Evidence, bounds and later work

Derivation records immutable input identities, exact changed/removed spans,
counted metadata changes and reversal equality; unchanged method identities are
listed separately. Construction may parse/read source as data, not import or run
subjects. Measure canonical payload and full Windows argv data-only before seal.
Independent focused fixtures cover new fixed metadata, upload-only bootstrap,
report-origin refusal, one-shot order, no predecessor, nine-call/per-label limits,
failures/closing and scope/artifact admission. Do not replay unchanged historical
algorithm suites merely to duplicate evidence.

No tests or native actions run during production preparation. Later native
admission requires accepted D220 exact cleanup with fresh /tmp/remoteocd absence,
source/host review, a committed concrete scope and clean HEAD/check-only. Actual
upload acceptance remains separate from D219 capture and its complete flash
checks. Successful upload alone establishes neither B4 recording completion,
coherence, live RAM/WCET, sensor/motor behavior nor a phase gate.
