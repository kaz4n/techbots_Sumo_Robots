# Exact default app: standalone one-attempt upload guard

Draft for coordinator adoption, 2026-09-24. This is a software contract, not
permission to upload. It accompanies `P2_app_default_probe_contract.md` and its
current public clarifications. Live run/approval/review records remain absent
until independent source, target, collector and guard review is complete.

## Scope and fixed request

Add only `tools/app_default_run.py`, a standalone passive-import module. Do not
modify `board_tool.py`, `p0_inert_sources.json`, build policies or existing tests.
Preserve all nine existing manifest keys and the manifest's exact bytes, SHA256
`a1587931afa5f817bf8b93054f384918dc8cd36d4fb71c8f7b083d76e6128802`.
Do not add an app key. Generic app upload remains refused. This route relies on
its own exact reviewed identity, not a claim that the normal app is I/O-free.

The only CLI request is:

```text
python tools/app_default_run.py --run-id app-default-e820c0e1-run01
```

No positional sketch, profile, MATCH, startup, compile-only, artifact, receipt,
address or alternate source option exists. Missing/wrong run ID and unsupported
arguments refuse before staging, target/transport lookup or remote operations.
The fixed internal request is sketch `app`, match false, compile_only false,
startup default. Require explicitly configured SUMO_TRANSPORT=adb and
SUMO_ADB_SERIAL=2629958581; absent transport must not inherit board_tool's SSH
default. Require SUMO_REMOTE_ROOT exactly `/home/arduino/sumox26_codex_build`.
Revalidate these values before upload; an environment change is refusal.

Literal pins:

| Field | Value |
|---|---|
| run_id | `app-default-e820c0e1-run01` |
| source_sha256 | `e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69` |
| elf_sha256 | `8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257` |
| binary_sha256 | `c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5` |
| ELF/ZSK length | Each176048 bytes |
| target / transport | `2629958581` / `adb` |
| FQBN / flags / startup | `arduino:zephyr:unoq` / `-DMATCH=0 -DMOTORS_ALLOWED=0` / `default` |

Firmware/config/grants are unchanged. This explicitly includes the existing
inhibited MotorGate/native GPIO/PWM setup and repeated LOW/zero/settle operation;
optional grants remain false. It grants no motion, connected-motor, PINMAP,
voltage, waveform, coast, STAND/RING or human phase-gate evidence. No UART or
sensor grant, synthetic START, control message, monitor, capture or recovery
command belongs to this guard. The separate passive collector supplies the
actual load/progress/fault evidence; successful upload exit alone does not.

## Minimal public seams

```python
validate_request(args, startup) -> bool
load_scope(root: Path, target: str, transport: str) -> dict
run_once(board_module, args) -> dict
upload_once(board_module, target: str, artifact_folder: str,
            board_folder: str, scope: dict) -> None
main(argv=None) -> int
```

`validate_request` is pure: require args.run_id equal the fixed ID, args.sketch
`app`, args.match and args.compile_only actual bool false, supplied startup
`default`, and args.startup absent/None/default. Return true only for that exact
request; otherwise ValueError, including missing ID. The CLI supplies these
fixed internal fields without exposing corresponding override options.

`load_scope` uses local files and local Git only, performs no staging/transport,
and returns exactly root (absolute Path), run_record, approval,
run_record_sha256, approval_sha256, review_sha256 and head_commit. It verifies
the identities, source map, file hashes, absence of attempt/outcome, environment
scope and current local HEAD described below. `run_once` owns the sole stage/
checked-build/upload sequence and returns exactly run_id, source_sha256,
artifact_folder, board_folder, attempt_file and outcome_file after success.
`upload_once` independently revalidates scope and artifacts, consumes the claim,
then invokes one upload. Tests may replace public filesystem/subprocess/board
calls; no private seeds, transport adapter framework or shared-tool monkeypatch.

## Frozen review records and current local commit

Fixed workspace-relative paths:

- Run: `state/analysis/P2_app_default_probe_run01.json`.
- Approval: `state/analysis/P2_app_default_probe_raw/reviewer/run01_approval.json`.
- Review: `state/reviews/P2_app_default_run01_review.md`.
- Attempt: `state/analysis/P2_app_default_probe_raw/run01_upload_attempt.json`.
- Outcome: `state/analysis/P2_app_default_probe_raw/run01_upload_outcome.json`.

The run record has exactly schema_version, run_id, target, transport,
source_sha256, elf_sha256, binary_sha256, approval_sha256, software_commit,
remote_root, setup, scope. Version is actual integer1, never bool. Identity
fields match the literal pins, remote_root matches the fixed root above,
setup is exactly `human-reported bare UNO Q`, and scope is exactly
`one unchanged default app upload with inhibited native GPIO/PWM setup; optional grants false; passive readout separately`.

Approval has exactly schema_version, run_id, verdict, source_sha256, elf_sha256,
binary_sha256, software_commit, review_sha256, file_sha256, source_file_sha256.
Version/identity match; verdict is exactly
`PASS_EXACT_DEFAULT_APP_SOURCE_TARGET_CAPTURE_GUARD`. The run's approval_sha256
equals the hash of the approval's original bytes. Approval.review_sha256 equals
the actual fixed review file bytes. Both software_commit fields equal one
lowercase40-hex revision and **actual current local `git rev-parse HEAD`**.

Invoke local `git -C ROOT rev-parse HEAD`, capture stdout/stderr, timeout10s,
require exit0 and exactly one40-hex revision after stripping outer whitespace.
Missing Git, failure, timeout or differing HEAD refuses. ROOT is the current
local repository root and must equal board_module.ROOT; never query board Git
or accept a caller-provided historical revision instead of current HEAD.
Preserve actual local Git command/status evidence in the orchestration receipt.

The reviewed software is committed first. Actual run/approval/review records are
then created locally and stay uncommitted through the attempt, avoiding a
self-referential approval/commit cycle. No commit is permitted between the final
scope check and upload. Scope is rechecked repeatedly, but the receipt is a
non-hostile workspace review control, not an atomic Git/filesystem lock or a
signature against a concurrently malicious editor. No clean-worktree fiction
is required for the uncommitted live records.

`file_sha256` has exactly these root-relative keys, each an actual lowercase
64-hex hash of the regular non-symlink file:

```text
tools/board_tool.py
tools/app_build_policy.py
tools/app_build_pins.json
tools/app_build_commands.json
tools/app_default_run.py
tools/app_default_capture.py
tools/p0_capture.py
tools/recorder_heap.py
tools/p0_mem_read.cfg
tools/p0_inert_sources.json
state/analysis/P2_app_default_probe_contract.md
state/analysis/P2_app_default_run_contract.md
```

`source_file_sha256` has exactly the91 staged-relative source names of this
candidate. Each key is a normalized relative POSIX path: no empty/dot/parent
component, backslash, absolute path or duplicate. Only `app.ino` maps to local
`src/app/app.ino`; all90 `src/...` names map identically below ROOT. Each value
equals the current local file hash. Recompute the existing source digest from
sorted staged-relative name bytes, NUL, then actual file bytes, and require the
literal e820c0e1 full digest. This binds exact names and contents, not just a
count. The proposed exact map is retained in
`P2_app_default_probe_raw/preflight/guard_route/source_pin_proposal.json`; that
proposal is not a live approval and is not imported as executable policy.

Both JSON records are at most65536 bytes; review is a regular file of at most
65536 bytes. Reject malformed JSON, duplicate keys, nonfinite constants,
unexpected schema/keys/types, wrong hashes and symlink ancestry. ROOT itself
must be a real directory. Check the same guards on every approved source/tool
file. Missing/unreadable files retain actual OSError; semantic refusal uses
ValueError. Reject attempt/outcome paths already existing, including dangling
symlinks, before staging or any remote access. No caller-selectable receipt path.

## Single checked preparation path

Each admitted invocation executes these calls once, in order, with no fallback:

1. Pure request validation; explicit environment/target/root validation; local
   `load_scope`. Reject any `src/app/sketch.yaml` or `sketch.yml` entry using
   existence including dangling links. No profile is allowed. Check source
   ancestry through unchanged `board.check_source`; require available explicit
   transport using unchanged `board.require_transport(sync=True)`.
2. Call unchanged `board.stage('app')`. Require returned folder exactly
   `ROOT/build/stage/app`, safe ancestry, exactly the approved staged file set
   and hashes, and unchanged `board.source_hash(folder)` equal the pinned digest.
   This check also rejects extraneous sketch metadata/files omitted from the
   source-map proposal. Recheck scope before the first remote call.
3. Use board_folder exactly
   `/home/arduino/sumox26_codex_build/SOURCE/app`. Call unchanged
   `board.verify_core(target)`, `board.remote(target,['mkdir','-p',board_folder])`,
   then `board.sync_sources(target,folder,board_folder)`.
4. Call unchanged `board.compile_app(target,SOURCE,board_folder,REMOTE_ROOT,
   'arduino:zephyr:unoq','-DMATCH=0 -DMOTORS_ALLOWED=0','default')` exactly once.
   Retain its actual returned fresh artifact directory. Do not call
   `board.flash`, whose existing app branch discards that return value, and do
   not invoke/alter `verify_inert_source` or the nine-key manifest.
5. Recheck scope, actual local/staged source map/digest and returned artifacts;
   enter upload_once with those exact returned values. Any stage, source,
   core, sync, preflight, policy or compile failure/interruption prevents upload.

The unchanged checked compile owns the UUID and `build/app-receipts/UUID`
evidence, validates pinned tools/core/recipes/overrides/library isolation and
effective commands, and returns
`REMOTE_ROOT/_app_builds/native-app-v1/SOURCE/bench-default/UUID/artifacts`.
UUID must be exactly32 lowercase hex. Reject any other mode/root/source/path,
extra suffix, old generic artifact directory or passive capture-input directory.
The standalone CLI accepts no artifact argument. Public upload_once receives
this internal result; it is not a new alternate-artifact CLI.

This is a finite single-pass preparation sequence, **not** an end-to-end
wall-clock deadline: existing core inventory, sync/ADB pushes and checked compile
do not uniformly supply timeouts. Preserve that limitation; do not monkeypatch
their transport, fabricate completion, or continue to upload after an interrupted
preparation. A later invocation before any upload attempt is a new preparation
invocation, not an automatic retry. Once the attempt exists all replays refuse
before transport.

## Artifact verification, final claim and upload

`upload_once` first requires the in-memory scope's exact key set and equality to
a fresh load_scope on board_module.ROOT and explicit current target/transport.
Check artifact/board folder form above. Call existing
`app_build_policy.verify_hashes(board.remote,target,pins)` for exactly:

- sibling `build/app.ino.elf`: the pinned ELF hash;
- returned `artifacts/app.ino.elf-zsk.bin`: the pinned ZSK hash.

The exact hashes already bind the176048-byte files. Keep the returned artifact
directory from the current checked compile; no generic-path reconstruction.
Revalidate scope/HEAD/environment/current local and staged source after remote
hash verification and immediately before creating the attempt. The last check
must still equal the original run scope, including original approval/run/review
hashes. No commits or edits occur between that check and launch.

Create the fixed attempt using exclusive creation, rechecking non-symlink
ancestry. Store schema_version1, run_id, target, transport, source_sha256,
elf_sha256, binary_sha256, software_commit, run_record_sha256,
approval_sha256, review_sha256, artifact_folder, board_folder, started_utc, argv.
Flush/fsync/close it **before** upload invocation. Claim creation failure prevents
launch; a partial claim consumes the attempt. Pre-existing outcome also refuses.

Exact upload argv is:

```text
arduino-cli upload --fqbn arduino:zephyr:unoq --input-dir ARTIFACT_FOLDER BOARD_FOLDER
```

Use unchanged board.remote with capture=True and timeout120 seconds, once.
Normal uploader reset is part of this separately reviewed upload; no additional
reset/halt/restore/read/capture command follows. Timeout is a bounded caller
observation and may not cancel remote work already accepted: retain UNKNOWN
launch/completion where applicable and do not retry.

On each returned/raised outcome, exclusively retain outcome JSON containing
schema_version1, run_id, finished_utc, returncode (actual int or null), stdout,
stderr, timed_out(bool), error(string or null). Text fields are always strings;
null becomes empty, timeout bytes decode UTF-8 with replacement. Flush/fsync the
outcome. Nonzero returned upload becomes CalledProcessError with original
stdout/stderr; remote OSError/subprocess/timeout failure propagates after evidence
retention. Outcome-write failure is itself failure and permits no second launch.
Host termination may leave intent only: that is a consumed unknown attempt.

Main returns0 only for the successful upload command and saved outcome,1 for
ordinary scope/preparation/upload/evidence failure,2 for CLI parse errors.
Preserve checked compile receipts, local Git checks and actual stage/source/
artifact binding in one exclusive orchestration receipt under this raw run
directory: `state/analysis/P2_app_default_probe_raw/preparations/UUID.json`, where
UUID is a newly generated32-lowercase-hex identifier for this invocation. It is
not a new upload run ID or permission to retry. Validate non-symlink ancestry;
one exclusive receipt records schema_version1, run_id, started_utc, finished_utc,
phase, local_git_checks, source_sha256, artifact_folder (null until returned),
checked_receipt (null until returned), and error (null or actual type/message).
Append each local Git argv/status/stdout/stderr/time result to local_git_checks;
retain the actual checked UUID receipt path when available. The ordinary
main/run_once error path saves this receipt, including preparation failure,
without any recovery command. A host kill may leave no final preparation
receipt; it never excuses reuse of an existing upload attempt. Receipt-write
failure prevents upload if reached before launch; after launch it is a failure
with the attempt still consumed. No transcript of credentials or broad
environments is collected. Actual failed command/status/output already retained
by checked build/upload evidence and the last completed phase remain evidence.
No outcome claims
LOADED, RUNNING, COMPLETED, RAM margin, timing, pin voltage or a gate pass.

## Independent tests and adoption boundary

Freeze independent fixtures before implementation execution. Cover all request/
environment/record/path/hash/HEAD refusals before transport, malformed types and
duplicate JSON keys, source-map omission/extra/name/content changes, profiles,
staged extras, different board ROOT, current HEAD change at each checkpoint,
scope/file/source change during sync/compile/hash verification, exact one checked
compile and retained fresh artifacts, propagation of every preparation failure,
generic/cached/malformed UUID artifact refusal, exact ELF/ZSK pins, exclusive
claim races/fsync failure, prior attempt/outcome including dangling links, exact
one upload argv/120s bound, nonzero/launch/timeout/outcome-write/unknown cases,
and no capture/retry/reset/manifest mutation. Preserve all old tests unchanged;
in particular the established nine-key manifest assertion remains valid.

Coordinator owns final run/review/approval records, artifact placement and
adoption after independent review. No live records or route implementation are
created by this drafting task. Local source/API evidence is in
`P2_app_default_probe_raw/preflight/guard_route/`; it records all91 current source
hashes, the nine-key manifest and actual inspected shared-tool hashes. This
draft changes no prior evidence, source, test, tool, manifest or board state.
