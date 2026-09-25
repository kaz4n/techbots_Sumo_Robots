# D188 fixed static diagnostic compile-only caller

25 September 2026. Offline implementation under D051/P7 follows reviewed D186
and D187. Hardware acceptance remains deferred. No actual manifest, boot claim,
native invocation, upload, reset, MCU read or new firmware permission is created.
Original full-app IO fault, physical gates and runtime qualification remain open.

## Public surface and ownership

Implement tools/compile_app_motor_fault.py and tools/app_motor_fault_compile_remote.py.
Keep historical code, board_tool, generic/dynamic admission and firmware unchanged.
Public caller APIs: parse_request(argv) -> (action, reviewed_head),
CompileDiagnostic(reviewed_head, *, root=ROOT), owner.check(), owner.run().
For controlled tests expose owner.artifact_program() -> str and
owner.validate_artifact_reply(text) -> dict; the latter is pure response checking.
Arguments exactly --check-only|--execute --reviewed-head <40lowerhex>, in that
order. Reject other arguments/types; no default execute, profiles or overrides.
Import can read the pinned legacy module but cannot dispatch or write. Invalid
arguments fail before owner/file/transport operations. Check-only uses read-only
local files/Git only, with no stage/output claim or board call.

Fixed project app_motor_fault.ino, FQBN arduino:zephyr:unoq:link_mode=static,
flags -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1, default startup.
Require Python-B. Execute also requires the selected output/pycache absolute
pycache_prefix, which must remain absent. Reviewed HEAD must equal current HEAD;
tree must be clean, except own new untracked output after exclusive claim.
Tracked changes never become permitted merely by living under that output.

RAW=state/analysis/P7_app_motor_fault_compile_raw. Future coordinator manifest
RAW/inputs_static.json is <=262144B duplicate-free finite JSON, exactly
schema='app-motor-fault-static-inputs-v1', source_sha256, boot_id, files.
Boot is a lowercase canonical UUID to be established by future fresh admission,
not the old D185 boot. Source is lower64hex derived from the exact staged-byte
mapping below. files maps exactly all ordinary files under src,
bench/app_motor_fault and bench/motor_fault/src, plus the caller, remote helper,
this contract, tools/board_tool.py, tools/app_build_policy.py,
tools/app_build_commands.json, tools/app_build_pins.json, D187 adapter, its three
historical Python dependencies and static_reference.json, the D185 caller,
D185 original executor/wait/two F166 baselines, and static_remote.py/static_artifacts.py.
No manifest self-hash or commit self-reference; reviewed HEAD/clean tree bind it.
All input paths use D185 relative/plain-path rules; no symlink/junction/reparse.
Keep per-file1MiB, combined three source trees4MiB/512files/1024entries bounds.
Recheck exact manifest bytes, filename sets and hashes before every transport
and during closing. No real manifest is created during this software task.

Hard-pin D185 aed3fbf4db5c962761affd5a3e2e52b1002feaaefe4e44f9f34df6ec78ba5ede,
D187 3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270,
static_remote 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8,
base artifact validator d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368.
Retain D185 executor/wait/F166/ADB/CLI hard pins and D187 dependency hard pins.
Use a private D185 module and unchanged reusable methods/executor_namespace;
never invoke its historical constructor/run or mutate shared module globals.
New boot must reach BOTH identity preambles and executor namespace. Retain
one properties query/one compiler, jobs1, isolated CLI/config/environment,
60s query/720s compiler/5s reap and30000UTF16-unit Windows command bound.
Preserve original errors when secondary receipt writes fail.

## Fresh ownership, source and compile

Local output RAW/native_static01; stage owner build/stage/app-motor-fault-static01
with child app_motor_fault. Existing owners of any type fail before board I/O.
Require128MiB local free space and1GiB target free space. Claim output exclusively
and fsync intent before board contact. Partial claims consume this attempt.
Remote owner /home/arduino/sumox26_codex_build/app-motor-fault-static01 has
commands, build and artifacts children; create exclusively without overwriting.
Canonical remote source /home/arduino/sumox26_codex_build/<source>/app_motor_fault.
Reuse a present canonical source only with exact directory/file/hash equality;
never repair, delete or overwrite a partial/different source.

Stage via checked board.stage('bench/app_motor_fault', attempt='app-motor-fault-static01').
Expected stage: sketch files under bench/app_motor_fault map relative to that
directory (omit its root .gitkeep); src/config.h, src/core/** and src/hal/** retain
their paths; src/app support with .c/.cc/.cpp/.h/.hpp suffix retains src/app/**,
excluding src/app/src/** and app.ino. The two canonical motor_fault.h/.cpp map
to src/motor_fault.h/.cpp. Reject collisions. Hash sorted relative name + NUL +
exact bytes as board.source_hash does, then require staged names/hashes/source
equal the admitted mapping. No historical stage is used as current evidence.

Reuse D185 identity/F166 prerequisite/source checks and guarded execution. Fixed
compile argv is arduino-cli compile --json --fqbn <fixed> --build-path
<remote>/build --output-dir <remote>/artifacts, C++ and C extra flags both exact,
the unchanged common DISCOVERY build property, then canonical sketch path.
No --upload or serial port/reset option. Validate CLI, exact resolved data/user
directories (/home/arduino/.arduino15 and /home/arduino/Arduino), override absence
and installed pins before expanded-properties query. D187 validates query and
compile raw JSON with its fixed signatures. Capture each raw command/result
through existing board.capture_app_command and checked command_runner; no call
to generic compile_app/selected_project/verify_files for this new profile.

## Remote artifact observation and receipt

Remote helper public API:
inspect_artifacts(build_path, artifacts_path, bundle, *, fs_root=Path('/')) -> dict.
bundle has exactly helper,adapter,extension,base byte values, each matching the
hard-pinned static_remote,D187,D147,D142 sources. Load privately; never run old
main/owner/claim. Reuse unchanged directory/read_file/observe_file behavior.
Use fs_root only for isolated host fixtures; native caller always supplies '/'.
Paths must be exactly this attempt's build/artifacts paths. No arbitrary read.
D187's private artifact dependency hook may supply only its checked extension
snapshot; do not alter the validation function or bytes passed to it.

Observe seven build files with prefix app_motor_fault.ino and suffixes .elf,
_debug.elf,_temp.elf,.bin,.bin-zsk.bin,.elf-zsk.bin,.map; observe exported
artifacts/app_motor_fault.ino.bin-zsk.bin separately. Preserve D187/D147 limits:
16MiB except .bin786416B and flat786432B. Missing/empty/linked/oversize/unstable
files fail. Require flat export exact byte equality, and actual D187 validation.
Read installed loader (<=16MiB, SHA39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd)
and tls-syms.S (<=65536B, SHA68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70)
at the unchanged core1.0.0 paths recorded in D148. No native installation change.

Return exactly schema='app-motor-fault-static-artifacts-v1', status,
build_path, artifacts_path, files, loader, tls_source, layout, postchecks,
first_error. files uses actual build/<name> and artifacts/<name> selectors with
unchanged helper records (state, identity, sha256); layout is full unchanged
D187 report. Success status ARTIFACTS_CHECKED requires initial reads/validation
and independent final loader/TLS/all-eight-file comparisons to succeed.
Failure status FAILED retains first error and all attempted final-check outcomes,
without a success envelope. Never send ELF/package bytes to the laptop.
postchecks is exactly three ordered rows named loader,tls_source,files; each row
has name,status (PASS|FAILED),error (null or type/message). first_error is null
on success or type/message on failure. All three are attempted independently.

Caller composes a compressed, pinned source bundle through existing direct;
enforce the actual Windows command length, not an estimate or relaxed bound.
Validate exact response schema/status/paths/file keys/record types/size bounds,
hard installed hashes, layout identity and its seven artifact hashes against
records, all postchecks and first_error before accepting. Native raw response
stays intact. Save compact artifact receipt under exclusively claimed output.

Closing independently attempts local inputs/stage, identity, both F166 baselines,
source (if attempted), installed pins/overrides (if available) and a repeated
artifact observation (if first succeeded). Its artifact identities/hashes must
equal the first observation. Keep first exception; append later failures.
Outcome includes schema='app-motor-fault-static-compile-outcome-v1', fixed
project/fqbn/flags, reviewed_head/source_sha256/boot_id, status, start/finish,
counts, artifact paths/receipt, first_error and final_checks. COMPILE_CHECKED
requires exactly one query/compiler plus all validation/closure success.
Result-write failure fails the run; attach compile_outcome to original exception.
This is compilation/structural evidence only, never runtime or phase acceptance.

## Independent acceptance

Independent spec-derived tests frozen before execution cover argument rejection,
check-only no mutations/board dispatch, source/manifest/HEAD/pin drift, plain
paths, owner exclusivity, fixed staging/map, canonical exact reuse/refusal,
exact compile argv/counters, prerequisite failure, compiler timeout/nonzero,
receipt-write first-error preservation, independent closing, metadata/packet
rejection, all remote file/link/size/export/TLS/loader/drift cases, and realistic
Windows command size. Use controlled substitutes and owned RAM, Python-B.
Fixture helpers may reuse existing public synthetic metadata/ELF builders;
expected behavior comes from this contract, not new implementation bodies.
Separate fresh-context reviewer checks actual diff/tests/results. No native
invocation follows automatically; future fresh admission remains separate.
