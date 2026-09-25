# Current-app compile-only composition

25 September 2026. One separately invoked checked compilation per fixed profile:
`bench` is MATCH0/MOTORS_ALLOWED0/default, `match` is MATCH1/MOTORS_ALLOWED1/
Immediate. No upload, reset, capture, deletion, dependency installation, source
overlay or binary download. Historical scopes, globals, sources and stages stay
unchanged. Current source is
37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29;
current admitted boot is 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 on ADB2629958581.
Compilation is not loading, RAM/WCET qualification, physical acceptance or a gate.
The historical default model's592-byte deficit remains unresolved.

## Public interface and coordinator inputs

Owned implementation: `state/analysis/P7_current_app_compile_raw/compile_current_app.py`.
Public Python APIs for independent controlled tests:

```
parse_request(argv) -> (action, profile, reviewed_head)
CompileCurrent(profile, reviewed_head, *, root=ROOT)
owner.check() -> dict
owner.run() -> dict
```

CLI accepts exactly `--check-only --profile bench|match --reviewed-head <40lowerhex>`
or exactly `--execute --profile bench|match --reviewed-head <40lowerhex>` in that
order. No implicit execute/default profile. Invalid arguments fail before I/O.
Check-only is local/read-only: no staging claim, board command or evidence write.
Both modes require Python-B; execute additionally requires
`-X pycache_prefix=<absolute selected local owner>/pycache`, which must not exist.
The supplied reviewed head must equal current Git HEAD. Before claim the tree
must be clean including untracked files; afterward only this invocation's owned
output may be untracked. Never ignore modifications to tracked output files.
Read-only Git inspection is permitted in check-only; no other process is used.

Coordinator supplies `inputs_bench.json` and `inputs_match.json` beside the caller.
Each duplicate-free finite JSON file is <=262144B with exactly
`schema="current-app-compile-inputs-v1",profile,source_sha256,boot_id,files`.
`files` is exactly every plain file under src plus these relative paths:
the caller, this contract, tools/board_tool.py, tools/app_build_policy.py,
tools/app_build_commands.json, tools/app_build_pins.json, tools/match_deploy.py,
the frozen original executor, current wait-source, and both F166 baseline files.
Each value is a lower64hex SHA256. Manifest bytes are rechecked before every
command and in closing checks. The manifest does not contain its own hash or a
Git commit, avoiding a self-reference; the reviewed-head argument and clean-tree
check bind its committed contents. No manifests or actual run scopes are created
by implementation development.

Hard pins (independent of coordinator manifest):

- original executor `state/analysis/P7_motor_fault_raw/compile_motor_fault.py`:
  84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d
- wait-source `state/analysis/P7_static_startup_raw/capture_remote.py`:
  95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e
- F166 cli_initialization_inventory.json:
  aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62
- F166 cli_builtin_files_inventory.json:
  a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb
- installed Windows ADB32.0.0:
  e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982
- board /usr/bin/arduino-cli:
  b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433

Input paths are relative forward-slash components, with no empty/dot/dotdot or
Windows reserved components. Local ancestry and files must be plain, with no
symlink/junction/reparse traversal. Bound each source to1MiB, complete src to
4MiB and512files. Bound other pinned inputs to1MiB. Use current read-only
match_deploy.app_source_hash mapping, then verify board.source_hash of the fresh
stage agrees with the fixed source. No old stage is read as current source.

## Reuse and ownership

Build a private namespace from verified AST nodes only: original functions
require,sha,unique,decode,write,files,projection,extracted_wait; original class
methods transport,direct,command_runner; original IDENTITY and REMOTE_CHILD
literal strings. Do not execute the historical constructor, main or run method,
mutate its module globals, or copy/rewrite child process code. Bind current
ROOT/BOARD/CLI/ADB/pins/ENV/BOOT explicitly in this new namespace. The current
wait-source's exact extracted stop_child and wait_child text hashes must remain
c6545967d8236164af2570a15573810ea9ccb43773e45c49364f5b494b6a4d44 and
65512632a53799f2b33ae43623f36c697623901e6b24ce1cdddf5b223a671259.
These bodies match the historical helper; full-source pins also remain required.

Original command runner inserts jobs1, permits one property query and one compile,
uses isolated CLI config, fixed env-i/Python-I-B,60s query/720s compile,5s reap,
and a30000UTF16-unit Windows command bound includingNUL. Reuse original direct/
transport and remote child lifecycle. A small failure guard around inherited
receipt writing may retain secondary write errors; it must never replace an
in-flight transport/compiler error or alter successful receipt contents.

Fixed bench/match local owners are `native_bench01`/`native_match01` beside the
caller. Stages are `build/stage/current-app-bench01/app` and
`build/stage/current-app-match01/app`; exclusively claim through existing
board.stage('app',attempt=...). Existing output or stage owner of any type fails
before board contact. Partial claims consume the profile; no retry/resume/delete.
Remote command owners are
`/home/arduino/sumox26_codex_build/current-app-{bench|match}01`.
Create each exclusively with a commands child. Remote source stays canonical:
`/home/arduino/sumox26_codex_build/<source_sha256>/app`.
The first profile claims an absent source hash directory and pushes exact files.
An already present source directory is accepted only after read-only exact
filename/hash verification against the fresh stage. Never overwrite an existing
source, even after a partial prior push. Both profiles use canonical remote_root
for compile_app, preserving D182/D183 receipt paths; generated build UUIDs differ.

## Execution and closure

After local admission, exclusively create output and fsync intent before any
board call. Require >=128MiB local free space before staging and >=1GiB board
free space before compilation. Revalidate source/input/HEAD and observed identity
before commands. Boot, UID1000/arduino, CLI hash, plain remote ancestry, unlimited
file-size rlimit and absence of conflicting compiler/upload processes are checked
by the unchanged identity preamble. It reads Linux state only, never MCU state.

Run both exact pinned F166 inventory argv before compilation, comparing identity
with only boot replaced by the current admitted boot, and comparing remaining
payload through original projection (ignore mtime_ns/ctime_ns only). Independently
repeat each inventory after success/failure. A failed prerequisite stops before
staging or compiler dispatch. No repair/download is attempted.

Pass the current checked board module's compile_app the exact source, canonical
source/root, profile FQBN/flags/startup and bound original command_runner. Obtain
the exact build UUID from its returned artifacts path, never latest mtime. Verify
and report `build/app-receipts/<build_id>/verified.json`; require checked policy,
source/profile/path/flags, returncode0 and precompile_checksTrue. Count exactly
one property query and one compiler call before declaring success.

Closing checks run independently: local inputs/HEAD/stage, board identity, each
prerequisite, remote source (when present), installed pins and override absence
(once remote source is available). Keep first failure and attach later findings.
Retain raw inherited transport/child receipts and exclusive final result.json;
result save failure must fail the run while preserving any earlier exception.
Outcome fields include schema,current profile/reviewed head/source/boot, status,
compiler/query/transport counts, artifacts, receipt, first_error,final_checks,
started_utc,finished_utc. status is COMPILE_CHECKED only when build and all closing
checks succeed; otherwise FAILED. Failed run raises the original exception with
compile_outcome attached. Check-only never creates this outcome.

## Independent validation boundary

Freeze contract-derived tests before source execution. Controlled fixtures cover
argument/profile/type rejection, exact extraction/pins and unchanged lifecycle,
source/HEAD/manifest drift, owner exclusivity, check-only no writes/board calls,
fresh app stage/canonical paths, existing exact source reuse without pushes,
partial/mismatched source refusal, both flag modes, one query/compiler, returned
receipt identity, prerequisite/timeout/compile failures, independent final checks
and failed evidence saves preserving first errors. No target execution follows
merely from passing host tests; a committed reviewed current invocation is separate.
