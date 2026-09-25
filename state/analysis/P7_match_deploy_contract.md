# D183: guarded precompiled MATCH deployment through existing transport

25 September 2026, Dubai. Implements the missing documented dynamic/Immediate
MATCH route under D051. OFFLINE development only. No actual qualification,
authorization or deploy scope will be authored by this task. Historical scopes,
pins and generic upload refusals remain intact; no static adoption or firmware
change. No signature service, second uploader or new transport/process runner.

## User interface and layering

`tools/flash.sh app --match --deploy-scope <repo-relative scope.json>` selects
one already compiled artifact. Reject compile-only, explicit default startup,
bench sketches and run-ui-adc-probe combinations before target/tool/file I/O.
Missing scope flag preserves every existing route/refusal. Route dispatch is
before flash_profile/staging/sync/core queries/compile. The new route never calls
any of those operations. --match remains a configuration, not permission.

New tools/match_deploy.py owns admission and one attempt/outcome, reusing
board_tool.target/transport/require_transport(sync=False)/remote; no subprocess
invocation except through that existing remote function. New tools/match_payload.py
owns bounded upload-only encoding/reply validation. tools/match_upload.py (D182)
owns the strict adapter; frozen uploader owns all actual child execution.

Public APIs for independent tests:

```
match_deploy.validate_request(args) -> bool
match_deploy.load_scope(root, relative, target, transport, *, now=None) -> dict
match_deploy.upload_precompiled(board, relative, *, now=None) -> dict
match_deploy.app_source_hash(root) -> str
match_payload.build_command(sources, bindings, source_sha256, build_id, run_id,
                            native_prefix) -> list[str]
match_payload.validate_reply(text, source_sha256, build_id, run_id,
                             payload_sha256) -> dict
```

`now` is UTC datetime, or None uses actual UTC; timezone-aware only. Sources is
exact role-to-bytes map helper/support/upload/adapter. Native prefix is the actual
local ssh or adb prefix used by existing remote, for the unchanged30,000UTF16
includingNUL Windows command bound. Public preparation does no native operation.

## Local scope and evidence

Strict duplicate-free finite JSON, <=65,536B per scope/qualification/authorization.
All paths are relative portable forward-slash components [A-Za-z0-9_.-]+, no empty,
dot/dotdot, trailing-dot components, absolute, backslash, reserved Windows names
or colon. Walk plain local
ancestry including root, reject symlink/reparse/nonregular files. Bounded reads
<=1MiB unless compiler stdout (<=4MiB); reject byte/hash mismatch. No cleanup.
Every pin has exactly path,bytes,sha256, with positive integer byte count and
lowercase64hex hash. Unknown/missing fields or type coercion fail explicitly.

Scope has exactly schema=`match-deploy-v1`, request, authorization(pin).
Request has exactly run_id/build_id(lower32hex), source_sha256(lower64hex),
source_commit(lower40hex, provenance label), target, transport(ssh/adb),
bindings(D182 exact shape), build_receipts, software, qualification(pin).
Target must equal current configured target/transport. Remote root is fixed
/home/arduino/sumox26_codex_build; no arbitrary remote root or flags accepted.
Request digest is SHA256 of ASCII canonical JSON (sort keys, compact separators,
ensure_ascii=True, allow_nan=False, one trailing newline).

`software` pins exactly board_tool.py, app_build_policy.py, app_build_pins.json,
app_build_commands.json, match_upload.py, match_payload.py, match_deploy.py under
tools/. These are current working software reviewed for this scope. Three frozen
remote dependencies are hard-pinned to D179 hashes in the deploy implementation.
Keep their historical modules unchanged. Also pin/reuse unchanged startup_run.py
and two F166 inventory receipts for safe local paths/projection and exact bounded
file-only prerequisite commands. Their old boot identity is never current.

`build_receipts` pins exactly roles verified,command,result. They must live at
build/app-receipts/<build_id>/{verified.json,command.json,compile.stdout.json}.
Verified exact existing schema: policy,source_sha256,fqbn,build_path,artifacts,
file_sha256,compiler_returncode,used_libraries,resolved_directories,precompile_checks.
Require native-app-v1, exact dynamic/Immediate FQBN, exact derived D182 paths,
integer returncode0, libraries[], precompile_checksTrue, data/user directories
/home/arduino/.arduino15 and /home/arduino/Arduino (exact keys data,user).
Use existing policy.validate_result(result, fqbn, '-DMATCH=1 -DMOTORS_ALLOWED=1',
build_path), passing compiler text. Require exact existing compile_app argv from command.json including
discovery property, both flags and sketch path; do not execute it. Verify all
policy.installed_pins plus exactly raw/debug/temp ELF and exported package hashes
in verified.file_sha256; every overlapping request.bindings file pin must agree,
including raw/export and installed loader/boards/platform. Require
packaged/export equality through D182. Qualification binds this exact raw/package.

Recompute staged-app source digest read-only from current source using stage(app)
mapping: immediate src/app files except .gitkeep and C/C++ extensions go at root;
src/app/src recursively goes under src (reserved config.h/core/hal/app rejected);
config.h/core/hal go under src; C/C++ app support recursively excluding local src
goes under src/app. Plain files/dirs only; max512files, each<=1MiB,total<=4MiB.
Extensions mean .c/.cc/.cpp/.h/.hpp. Hash host-Path-sorted staged paths +NUL+bytes
as source_hash does; reject case-insensitive staged-path collisions and test
mixed-case ordering against that existing function. Require app.ino present,
no sketch.yaml/yml/json; reject destination collisions and stale/changed bytes.
Do not stage, copy, delete or depend on historical stage directories. Source
commit is evidence provenance, not inferred from current HEAD or ledger commits.

Qualification record exact schema=`match-operation-qualification-v1`,
source_sha256,raw_sha256,package_sha256,operation_image_sha256,
operation(`stand`/`ring`),verdict=
`QUALIFIED_FOR_IDENTIFIED_OPERATION`,reviewer(nonemptystr),limitations(list[str]),
evidence(list of1..16 pins). Each evidence pin must exist and hash-match.
operation_image_sha256 hashes canonical JSON with exact keys target,transport,
source_sha256,fqbn,files,directories,absent,operation; use request target/transport/
source, fixed MATCH FQBN, bindings files/directories/absent and qualification's
stand/ring operation. This binds board, build and runtime dependencies while
excluding fresh boot/run/output. It is
an explicit external review disposition for this artifact/operation; a compile
receipt alone is not qualification. The tool verifies bindings, not physical truth.

Authorization record exact schema=`match-human-authorization-v1`,request_sha256,
reply=`STAND OK` for stand or `RING OK` for ring, message_ref(nonemptystr),
issued_utc,expires_utc. UTC ISO timestamps, issued<=now<expires, positive lifetime
<=1hour. This conservative tooling freshness bound adds no motion semantics.
The referenced message must actually be a current-session human statement for
this identified operation; the operator/agent must verify that provenance before
running. A record, boolean, delegated engineering choice or test fixture is not
human permission. Software cannot authenticate the author of an arbitrary file.
Never reuse across firmware/target/operation/session; exclusive run claim also
prevents replay after even a failed attempt. No actual approval file is made now.

## Upload composition and outcomes

load_scope is read-only/no process and returns admitted request/evidence snapshots
and digest plus derived adapter profile. Public return fields include request,
profile,scope_sha256,request_sha256; extra internal fields are not a public schema.
Load all code from checked byte content,
without global mutation. Revalidate immediately before durable claim and again
after prerequisite checks/before upload; after claim revalidation allows only
this invocation's owner, never grants a new attempt.

Claim local state/analysis/match_deploy_<run_id> exclusively(mode0700); ancestors
must be plain existing directories. Write attempt.json exclusively/fsync before
any remote call, including prerequisites. Store scope/request/hash/source/target
and derived command digest. Partial claim is consumed; no resume/retry/delete.
Reject existing output path of any kind, including dangling links.

Run both exact hard-pinned F166 file-only inventory commands before upload and
independently after success/failure (at most5 remote calls:2+1+2). Use existing
remote capture=True, timeout90s per inventory. Require exit0/empty stderr,
COLLECTED, exact expected boot/UID/user/home/Linux/aarch64 identity; remaining
baseline identity fields match original except boot. Compare nonidentity payload
through existing projection (ignore only mtime_ns/ctime_ns; sort lists only if
every element is a dict). A missing prerequisite fails before upload; no CLI download
or repair. Postchecks run independently even if another fails.

Dispatch exact encoded upload once via existing remote capture=True timeout240s.
Transport timeout/disconnection means UNKNOWN motor outcome, never retry. Remote
uploader child remains bounded/reaped by inherited lifecycle when functioning;
local transport timeout is not proof remote execution stopped. Preserve raw
stdout/stderr/status on failure. Local source/scope/evidence postcheck also runs
independently. Write exclusive outcome.json/fsync once with actual status,
primary error and postcheck errors; if saving fails preserve original error and
attach/report secondary failure. A successful operation with failed evidence
write must fail. No fabricated success, capture, reset, follow-on build or motor
run. Upload naturally starts firmware; phrase it as motor-capable in docs.

Remote payload is canonical ASCII JSON <=196608B, bzip2 + canonical base85,
exactly one BZ2 member with bounded expansion; digest covers uncompressed JSON.
Trusted small bootstrap may be compressed for Windows command size. Envelope
contains exact source/build/run identifiers, four source texts+hashes and
bindings. Decode/validate all shapes, hashes and IDs before loading modules;
invoke D182 only. Environment empty except fixed HOME/USER/LOGNAME/PATH/LANG/
LC_ALL; /usr/bin/python3 -I -B. No installed helper source required beyond Python.
Output <=65536B, canonical JSON envelope exact keys schema=`match-action-v1`,
source_sha256,build_id,run_id,payload_sha256,remote_result_path,full_result_bytes,
full_result_sha256,report,first_error. payload_sha256 covers the complete dispatched
payload, including bindings/boot/source bytes. remote_result_path is derived
output/upload_result.json. Full result bytes/hash cover support.json_bytes(report)
(the exact canonical form written by inherited uploader). If no result exists,
full-result fields and report are null with a nonnull first_error; reject it.
Report omits stdout/stderr for bounded output;
full streams/report stay in inherited remote output. Exact reply schema, clean
errors, UPLOADED, one attempt, correct identity/schema, finite ordered clocks,
child exit0/no timeout/reaped and empty postcheck errors required for acceptance.
Projected report has exactly schema,run_id,source_sha256,status,attempts,
started_utc,finished_utc,started_monotonic,finished_monotonic,subprocess,
first_error,postcheck_errors. Child has exactly returncode(int0),timed_out(False),
reaped(True). UTC timestamps must be valid UTC and ordered; monotonic values
finite/nonnegative/ordered, attempts exact int1, error null, postchecks[].
Any other response fails; raw response is retained locally. No success from exit0
alone. Validate reported remote paths through identity-derived owned output.

## Validation and limitations

Independent fresh-context tests from this public contract precede execution.
Controlled positive and negative fixtures cover argument routing/no-I/O refusal,
source digest mapping/collisions, source/evidence/receipt/target/boot drift,
authorization freshness/reply/request mismatch, current callback dispatch and
single-use claims, prerequisite and upload failures/timeouts, independent closing
checks, failed outcome writes, exact payload/framing/command-size/response guards.
No actual approved scope, native process, transport, compiler, device, download,
new large directory or existing/locked-test amendment. Preserve first failures;
separate reviewer checks source/results. Test complete actual source composition
size on Windows, with current helper/support/upload/adapter bytes. This finishes
software preparation only; target compilation of changed firmware, current-board
qualification, MotorGate diagnostic, RAM/WCET and human gates remain pending.

## Public fixture clarifications before implementation execution

Software map keys are full repo-relative tools/<name>. `board` is the existing
board_tool module (or controlled test seam) with ROOT,target,transport,
require_transport,remote,SSH_OPTIONS,adb_executable,report_app_error. Its ROOT is
the root passed to load_scope; tests may substitute an owned RAM workspace.
load_scope has no transport call. upload_precompiled returns only accepted
outcome; otherwise raises the primary error with deploy_outcome attached.

Outcome exact fields: schema=`match-deploy-outcome-v1`,run_id,source_sha256,
scope_sha256,request_sha256,target,transport,status,attempts,remote_result,
commands,first_error,postcheck_errors,started_utc,finished_utc. Status FAILED
before upload dispatch, UNKNOWN after any unaccepted dispatch, ACCEPTED only
after validated response and all closing checks. Attempts is0/1; remote_result
is the accepted decoded envelope or null. Command receipts have exactly label,
argv_sha256,returncode,stdout,stderr,error; retain transport output including
failures. Errors are type/message records; postchecks add check. Successful
receipt-save failure raises; primary errors survive secondary-save errors.

Payload exact fields: schema=`match-upload-payload-v1`,source_sha256,build_id,
run_id,sources,bindings. Source values have exactly source(UTF8 text),sha256.
Remote argv after -c is BOOTSTRAP,payload_sha256,bare canonical base85 token
(no prefix); the digest is argv[-2]. validate_reply returns the complete decoded
accepted envelope. full_result_bytes must be exact int1..16777216; two inherited
<1MiB streams can expand to about12MiB in ensure_ascii JSON. Metadata's full
result hash has strict digest syntax; omitted streams cannot be rehashed locally
from the compact reply. Do not claim otherwise.

The canonical flash.sh wrapper invokes python3 -B so the local inherited binding
checker and remote -I -B policy agree; direct Python invocation must also use -B.
This prevents bytecode storage and changes no build flags or upload authority.

First-run portability/snapshot repair clarification: local binding admission
uses exactly the five pinned pure support definitions require,keys,json_bytes,
valid_path,check_pin in an isolated json/re namespace. Require exactly one
top-level definition each; do not import Linux resource on Windows or stub it
globally. Remote support remains unchanged/full. Local policy executes its
checked AST with only the two exact Path(__file__).with_name(<commands/pins JSON>)
.read_text() calls replaced by checked UTF8 string constants, one each. Preserve
every other node; fail on shape drift. No historical module/global mutation.
On outcome-save failure promote that error if no primary exists, mark UNKNOWN
after dispatch, attach deploy_outcome and add outcome_write postcheck details.
Retain any original primary; do not retry saving or return accepted success.
