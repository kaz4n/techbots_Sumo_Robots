# D227 commissioning application deployment contract

This additive path admits one existing D222 artifact. It changes no firmware,
configuration, legacy helper or gate. There are exactly seven profiles, static
linking, default startup, MATCH=0, and an explicit integer MOTORS_ALLOWED 0 or 1.
No native invocation is authorized by source/host acceptance of this contract.

## Public interfaces

`tools/deploy_commissioning_app.py` exposes `parse_request(argv)`,
`load_scope(root, relative, reviewed_head, target, transport, *, now=None)`,
`check_only(board, relative, reviewed_head, *, now=None)` and
`upload_precompiled(board, relative, reviewed_head, *, now=None)`.
The CLI is exactly `python -I -B tools/deploy_commissioning_app.py
--check-only|--execute --scope RELATIVE_JSON --reviewed-head 40lowerhex`.
No automatic compilation, resume, retry, cleanup, capture or motor command exists.

`parse_request` returns exactly action, scope, reviewed_head. `load_scope` returns
root, relative, reviewed_head, request, selection, profile, scope_sha256,
request_sha256, code, compiler_owner, qualification; private implementation state
may also be included. `check_only` returns schema `commissioning-app-deploy-check-v1`,
status `ADMITTED_LOCAL`, board_observed false, mode/profile/motors_allowed,
source_sha256/run_id, scope_sha256/request_sha256/reviewed_head. Execute returns
schema `commissioning-app-deploy-outcome-v1`, status ACCEPTED, FAILED or UNKNOWN,
attempts 0 or 1, selected profile/motors/mode/source/run/target/transport,
remote_result, commands, first_error, postcheck_errors and UTC start/finish.
Failure attaches this dictionary to the raised error as `deploy_outcome`.
Board injection uses the unchanged match_deploy board protocol (ROOT, target,
transport, require_transport, remote, adb_executable/SSH_OPTIONS, report_app_error).

The JSON scope has exactly `schema`, `request`, `authorization`, with schema
`commissioning-app-deploy-v1`. Request has exactly `profile`, `motors_allowed`,
`mode`, `compile_attempt`, `run_id`, `source_commit`, `source_sha256`,
`config_sha256`, `startup`, `target`, `transport`, `bindings`, `build_receipts`,
`qualification`. Profile IDs match D222; compile_attempt matches D222's token;
run_id is 32 lower hex; source_commit is 40 lower hex; digests are 64 lower hex.
Startup is `default`. Transport is `adb` or `ssh` and must equal the caller's
configured transport and target. UID is 1000 and boot is D222's observed boot.
`mode` is `inhibited_diagnostic` for M0 or `operational_commissioning` for M1.

Every evidence pin is exactly `{path, bytes, sha256}`, uses a confined portable
repository-relative plain file and bounded exact bytes. Empty stderr pins may
have zero bytes; other evidence is nonempty. JSON duplicate keys/nonfinite values
and wrong exact built-in types are rejected.

`build_receipts` keys are exactly `inputs`, `intent`, `staged_files`, `result`,
`artifacts`, `compile_command`, `compile_stdout`, `compile_stderr`,
`properties_command`, `properties_stdout`, `properties_stderr`. Paths are the
D222 deterministic owner output plus respectively inputs.json, intent.json,
staged_files.json, result.json, artifacts.json and compile/compile.command.json,
compile/compile.stdout.json, compile/compile.stderr.txt,
compile/properties.command.json, compile/properties.stdout.json,
compile/properties.stderr.txt. Every receipt is checked, including the one-query,
one-compiler outcome and all nine successful independent closing checks. The
complete metadata/policy/artifact validators are reused, not replaced by status
strings. Exact source mapping, staged-file map, input hashes, flags, startup,
paths, artifact identities and intended build command must agree.

All current compiled source and compile-helper input bytes must equal their
actual `source_commit:path` Git blobs and the complete D222 input manifest. The
deployment caller/adapter/contract and all frozen upload dependencies must equal
actual reviewed deployment HEAD blobs. Current HEAD must equal reviewed_head and
be clean before claim. After claim only new untracked files under this run's
owner are allowed. Later evidence-only commits may therefore use an older compile
commit without relabeling changed source. Local checks create no native evidence.

## Inhibited and operational admission

M0 requires authorization and qualification both null. Its exact config must
contain the closed 17 APP_GRANT declarations as literal uint32 zero, the literal
three zero APP_IMU_BODY_AXIS values and APP_DUMP_ORIGIN zero. Unsupported syntax,
duplicate declarations, extra APP_GRANT names or preprocessor overrides fail.
Its accepted upload is only an inhibited diagnostic, never operational or
physical qualification.

M1 requires a pinned qualification JSON and pinned fresh human authorization.
Qualification keys are exactly `schema`, `operation_image_sha256`, `operation`,
`verdict`, `reviewer`, `limitations`, `checks`, `grants`, `gate`, `turn_basis`.
Schema is `commissioning-operation-qualification-v1`; verdict is
`QUALIFIED_FOR_IDENTIFIED_OPERATION`. Operation is stand for b4_stand and ring for
all other profiles. The image digest is SHA256 of canonical JSON of the full
request except qualification, so it binds source/config/profile/flags/startup,
artifacts, receipt pins, target, boot, dependencies and the individual run.

Required checks are pinmap, electrical, buttons, battery, line_calibration,
motor_inhibition, profile_parameters and source_clock. Each is exactly
`{verdict, evidence}` with verdict `PHYSICALLY_ACCEPTED` and a nonempty bounded
list of pins to actual measurement/review evidence. All enabled grants require
their own check of the same shape in `grants`; its keys equal exactly the enabled
grant names. Opponent, ADC-pair and QTR-exclusive-pad grants are mandatory. Button
windows must be configured; zero defaults do not qualify. Other grants are
optional and cannot be silently enabled. No source setting creates evidence.

The gate object is exactly `{reply, message_ref, evidence}`. Required replies:
b4_stand `GATE P1 PASS`; p3_drive/p3_turn/p3_stop `GATE P2 PASS`;
p4_reactive/p4_timing `GATE P3 PASS`; p5_abort_timing `GATE P4 PASS`.
The referenced human message must be nonempty, and pinned gate evidence is
required. D051/D122 software scheduling assumptions cannot satisfy these gates.
For p3_turn, turn_basis is `imu_accuracy` or `timed_fallback`; IMU accuracy requires
all three IMU grants and a signed-axis permutation. The timed fallback is declared
as such and makes no angular-accuracy claim. Other profiles use `not_applicable`.

Authorization keys are exactly `schema`, `request_sha256`, `reply`, `message_ref`,
`issued_utc`, `expires_utc`; schema `commissioning-human-authorization-v1`, full
canonical request digest, STAND OK for B4 or RING OK otherwise, nonempty human
message reference, aware UTC timestamps. The inherited MATCH guard's maximum
one-hour window is explicitly adopted here as an engineering freshness policy;
it does not invent permission and expires at a strict upper bound. Revalidation
occurs immediately before upload and during closing. No authorization fixtures
are actual permission.

## Native adapter and lifecycle

`tools/commissioning_app_upload.py` exposes
`commissioning_profile(uploader, support, *, profile, motors_allowed,
compile_attempt, source_sha256, run_id)`, `build_command(sources, bindings,
selection, native_prefix)`, and `validate_reply(text, selection, payload_sha256)`.
Selection has exactly profile, motors_allowed, compile_attempt, source_sha256,
run_id. `sources` has exactly helper, support, upload, inherited_adapter, adapter;
the first four are the exact frozen static reader/capture/upload/MATCH adapter.
The new adapter is HEAD-bound. Source bytes are checked before execution. The
existing MATCH initializer supplies only instance initialization; unchanged
static Upload owns descriptor admission, complete artifact/tool pins,
directory/override/scratch absence, process conflicts, bounded resource-limited
child, durable owner, every closure and original-error precedence.

Raw is D222 build/app.ino.bin, packaged is build/app.ino.bin-zsk.bin, exported is
artifacts/app.ino.bin-zsk.bin; packaged/exported bytes must agree. The remote
owner is `/home/arduino/sumox26_codex_build/commission-upload-RUN_ID`; the local
owner is `state/analysis/commissioning_deploy_RUN_ID`. Owners are exclusive and
consumed on any attempted execution. Before claim, failure creates no native
operation. The host repeats both pinned CLI prerequisite observations before and
after the one upload. Every available closing check is attempted independently.
Native nonzero/unknown/transport/closing failure is not retried or called success.

The bounded compressed inline payload follows the existing MATCH command-size
guard including Windows command-line NUL and uses isolated Python -I -B with an
empty controlled environment. A compact returned envelope binds selection,
payload identity and the full durable native result size/hash. Returning an
UPLOADED result is not firmware readback, initialization, measured inhibition,
WCET/RAM evidence, physical qualification, phase acceptance or a motor trial.

The exact native envelope is schema `commissioning-app-action-v1`, selection,
payload_sha256, remote_result_path, full_result_bytes, full_result_sha256,
report and first_error. Compact report is the inherited MATCH report without
stdout/stderr, with schema `commissioning-app-upload-result-v1`; success requires
UPLOADED, attempts integer 1, no errors, a zero-return/non-timeout/reaped child,
valid monotonic and UTC ordering. Payload is schema
`commissioning-app-upload-payload-v1`, selection, sources and bindings; each
source record is exactly source UTF-8 text plus sha256. The native bootstrap
checks canonical duplicate-free bounded JSON and compressed input boundaries
before importing the checked adapter. Host binding validation uses the existing
pure extractor, so imports and check-only work without Linux-only resource APIs.

Pre-freeze implementation clarification: transmitting the full new adapter
duplicates its host-only payload builder/reply validator and exceeds the retained
30,000-unit Windows command bound. `build_command` therefore projects only its
checked source prefix before the single exact `BOOTSTRAP = '''` boundary. This
prefix contains profile/binding/native-upload definitions; it is compiled locally
before transport and hash-bound in the payload. Legacy source bytes remain full
and unchanged. Full bindings are checked locally using the same five pure support
definitions as the frozen MATCH extractor before any command is constructed.
