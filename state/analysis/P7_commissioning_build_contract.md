# D222 commissioning application compile-only contract

Scope: additive reusable compilation for the seven existing commissioning
profiles. This contract grants neither upload nor execution permission. MATCH is
always 0. MOTORS_ALLOWED=1 is a compile identity, never STAND OK or RING OK.
Existing policies, fixed callers, source, tunables and locked tests are unchanged.

## Public policy API

`tools/commissioning_app_static_policy.py` exposes `PROJECT='app.ino'`,
`FQBN='arduino:zephyr:unoq:link_mode=static'`, `PROFILES` (the seven IDs below),
and `SNAPSHOT_PINS` (the same five path/size/SHA256 entries as D213).

`safety_flags(profile, *, motors_allowed)` requires an exact built-in str ID and
an exact built-in int 0 or 1 (bool, subclasses, aliases and coercion are rejected).
It emits these ten definitions exactly once and in this order:
MATCH, MOTORS_ALLOWED, SUMOX_B4_STAND, SUMOX_P3_DRIVE_TEST,
SUMOX_P3_TURN_TRIAL, SUMOX_P3_STOP_TRIAL, SUMOX_P4_REACTIVE,
SUMOX_TIMING_EVIDENCE, SUMOX_P5_ABORT_TIMING, SUMOX_MOTOR_FAULT_PROBE.
Only the selected profile definitions are 1; all competitors/probes are 0.

| ID | Enabled profile definitions |
|---|---|
| b4_stand | SUMOX_B4_STAND |
| p3_drive | SUMOX_P3_DRIVE_TEST |
| p3_turn | SUMOX_P3_TURN_TRIAL |
| p3_stop | SUMOX_P3_STOP_TRIAL |
| p4_reactive | SUMOX_P4_REACTIVE |
| p4_timing | SUMOX_P4_REACTIVE, SUMOX_TIMING_EVIDENCE |
| p5_abort_timing | SUMOX_P5_ABORT_TIMING |

`validate_preflight(text, *, build_path, data_dir, profile, motors_allowed,
snapshots)` and `validate_compile_result` with the same parameters preserve the
complete checked D213 metadata validation, replacing only exact profile flags.
Startup remains default. No ambient policy import/read may replace any snapshot.

`validate_artifacts(artifacts, native_tls_source, frozen_validator_source, *,
exported_flat_package, profile, motors_allowed, snapshots)` preserves the full
seven-artifact ELF/TLS/layout/package/export checks and returns their report with
status `STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS`, exact `profile`, and exact
integer `motors_allowed`. Snapshot keys, types, sizes and SHA256 are checked before
execution. Failed lower-level validation never becomes a PASS report.

## Caller API and command

`tools/compile_commissioning_app.py` accepts exactly this argument order:

```
python -I -B tools/compile_commissioning_app.py --check-only|--execute --profile ID --motors-allowed 0|1 --attempt TOKEN --reviewed-head 40lowerhex
```

`parse_request(argv)` requires an exact list of exact strings, returns exactly
`{'action': '--check-only'|'--execute', 'profile': ID, 'motors_allowed': 0|1,
'attempt': TOKEN, 'reviewed_head': HEAD}`, and rejects omitted, repeated, reordered
or extra arguments. TOKEN matches `[a-z][a-z0-9_]{0,23}`. No arbitrary flags,
FQBN, paths, shell text, upload option or motor-run grant is accepted.

`build_paths(profile, motors_allowed, attempt, source_digest)` checks all four
exact types and values; the source is exactly 64 lower hex. It returns exactly
these string keys: `owner`, `output`, `stage_owner`, `stage`, `remote`, `build`,
`artifacts`, `sketch`. Owner is
`commission-ID-mN-DIGEST_FIRST12`, where DIGEST is SHA256 of the UTF-8
`source_digest + NUL + attempt`. This preserves the inherited 48-character staging
owner bound. Output is the repository-relative
`state/analysis/P7_commissioning_build_raw/OWNER`; stage_owner is
`build/stage/OWNER`; stage appends `/app`. Remote is
`/home/arduino/sumox26_codex_build/OWNER`; build/artifacts append those names;
sketch is `/home/arduino/sumox26_codex_build/FULL_SOURCE/app`.
The full source digest is retained and checked; truncated owner names do not
permit existing paths to be overwritten. Example: source `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`,
profile `p4_timing`, motors 0, attempt `compile01` yields
`commission-p4_timing-m0-37a7e0e40226`.

`load_caller(request, *, root=ROOT)` validates the exact request shape, loads the
hash-checked D214 primitives privately, and returns a private module exposing
`CompileDiagnostic(reviewed_head, *, root=ROOT)`. Each call owns an independent
namespace: configuring one profile cannot change another or the old modules.
The supplied reviewed_head must equal the request head. The returned owner keeps
the inherited injectable `git_state`, `local`, `transport`, `direct`, `inventory`,
`prerequisite`, `stage`, `command_runner`, `build`, `closing`, `finish` seams.
`make_owner(request, *, root=ROOT)` is the convenience constructor.

Input admission calculates the complete current application source mapping and
checks every required source/helper against the exact reviewed HEAD bytes. The
current HEAD and clean worktree are required before mutation; only the owner's
new untracked output is permitted after exclusive claim. A deterministic in-memory
manifest (schema `commissioning-app-static-inputs-v1`; exact keys schema, profile,
motors_allowed, attempt, reviewed_head, source_sha256, boot_id, files) binds
profile, motors, attempt, HEAD, full source digest, boot and every
input hash. It is saved under the claimed output as `inputs.json`; no separately
hand-authored manifest is necessary. Repeated admission must match the first
manifest and source set. Frozen primitive/snapshot pins remain fixed; new source
is bound directly to the reviewed HEAD rather than recursively pinning old reviews.

The expected boot is the already observed
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`; native initial and closing identity
observations must match it. A reboot requires a separately reviewed update to the
expected boot, never silently accepted identity drift.

Check-only performs local admission/path/space checks and returns a descriptive
receipt with `board_observed=false`. It creates no owner, invokes no transport and runs no compiler. Execute
exclusively claims a fresh local output and stage plus fresh remote command owner;
failure or success consumes that owner. Source-addressed remote app reuse requires
the exact complete file/hash/directory set. There is no automatic retry/resume.

Execution inherits D214's board identity, CLI/init/builtin checks, no conflicting
compiler/debugger process, input/override checking, source confinement, one query
and one compiler, jobs=1, bounded child wait/reap/output and transport limits.
Only the profile flags, owner paths, source identity, schema/report profile labels
and policy adapter change. Runtime never sends an upload, reset or motion command.
Artifact source transfer stays bounded and its closing observation is retained.
Every available closing check is attempted independently while the first error
remains primary. Raw command/output evidence is retained on failure.

## Remote artifact adapter and test boundaries

`tools/commissioning_app_compile_remote.py` exposes
`inspect_artifacts(build_path, artifacts_path, bundle, *, profile, motors_allowed,
attempt, source_digest, fs_root=Path('/'))`. Paths must equal the deterministic
owner paths above. It uses the checked D214 descriptor reader and artifact
observation/closing primitives. The bundle includes the old checked reader,
five policy snapshots and base validator plus this new policy and the frozen B4
remote primitive; the new policy bytes are supplied by the HEAD-bound caller.
Explicit complete bundle identities are validated before any supplied Python is executed.
The nine role names are helper, policy, adapter, common, static_policy, reference,
extension, base and primitive. The primitive is D214 `b4_app_compile_remote.py`
(7821 bytes, SHA256 `7dc788cbfb92688d3b1a2343f673da1bae3fa3ade1df5836ae437c013750b2d3`).
The commissioning policy is 4779 bytes, SHA256
`1e46cf058ccab40a2cb8e0aa9f3e9583b1f11d35fd22baaf93ff9b55d78ba931`.
The other seven source identities retain the exact D214 pins.

Host tests should independently enumerate all 14 flag identities, reject type and
identity confusion, exercise full inherited metadata/artifact validators, check
CLI/path derivation, cross-profile isolation and request mismatches, and drive the
caller seams through success, refused input, repeated ownership, early/late failure
and independent closing. Inspect generated commands to prove compile-only/jobs=1
and unchanged bounds. Native compiler results are separate evidence; host success
does not prove physical commissioning, timing, free RAM, UART or any phase gate.
