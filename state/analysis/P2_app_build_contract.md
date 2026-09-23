# D099 app-only checked dependency policy

2026-09-23 Asia/Dubai. Selected under D051/D075 after D098 investigation1447ec8
and its separate review. This is a build-tool change, not a firmware behavior,
wiring, loader, capacity, startup or upload-authority change.

Only canonical `flash app --compile-only` uses the fixed discovery property
`build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0`.
Ordinary benches retain their current commands/dependencies/allowlist. All app
uploads remain rejected before target/transport lookup, including non-MATCH.
No user option/env variable permits arbitrary extra flags or an alternative policy.
Default uses MATCH0/MOTORS_ALLOWED0/wait; explicit Immediate keeps both0; MATCH
uses both1/Immediate, never default. Each mode needs actual compile evidence before
its success is claimed. No mode will be flashed by this task.

Use pinned CLI1.5.1 commit01f3d4f2b and existing core1.0.0. Verify CLI identity
before compilation. New app build/output directories are outside the sketch tree,
under a policy/version/source/mode path with a fresh random run identifier; the
source hash alone cannot identify different build policies or modes. Keep normal
sketch staging and the board-side SSH/verified ADB build path. Preserve separate
compiler stdout/stderr, including failures. No reset/upload/start or MCU access.

Compile once with --json, explicit --build-path/--output-dir and only controlled
properties. Never use show-properties, preprocess, compilation-database-only,
skip-libraries-discovery or upload on this path. The accepted result requires
process exit0 plus exactly one JSON object (no duplicate keys or nonfinite JSON
constants), strict success=true, error absent or empty string, and builder_result
an object. Compiler output strings must be strings when present; warnings do not
cause rejection. upload_result must be absent or an empty object.

Require builder_result.build_path equal to this fresh build path, both platform
objects id=arduino:zephyr/version1.0.0 with identical absolute install_dir, and a
nonempty array of build-property strings. Split each at its first equals; reject
malformed/empty/duplicate keys. Match exact FQBN, core=arduino, UNOQ variant,
runtime.platform.path/build.variant.path, project_name=app.ino, discovery flag,
C/CPP safety flags, dynamic link mode, -e main and expected wait/immediate boot.
Reject additional nonempty C-ELF/S/build/link extra flags. Ordinary unrelated
properties remain allowed. Pin selected installed core/discovery/EDK/compiler/
loader bytes against reviewed identities, not merely a directory named1.0.0.

Accept used_libraries only absent or an empty array; reject null/wrong types/any
element. Absence is the real CLI omitempty encoding, acceptable only after the
complete successful envelope checks. Explicit libraries still resolve normally
under phase0; a separate phase-independent fixture must demonstrate that and
prove rejection. Library-list checks do not replace ELF/source audits or prove
arbitrary libraries preserve behavior under this macro.

After JSON checks, require real nonempty final/debug/temp ELF and packaged sketch
artifacts; record SHA256 for them and pinned installed files. Fail on missing or
changed dependency files before reporting checked build success. Keep complete
target source/dependency/startup/export/memory audits as D098 for adoption. A
successful check proves compilation/identity only, not load/freeRAM/WCET/physical
behavior or a phase gate. Existing inert source keys are unchanged.

Public Python validation seam, for independent spec-derived tests:
`tools/app_build_policy.py`: `validate_cli(text)` returns None or raises ValueError;
`validate_result(text, fqbn, flags, build_path)` returns the unique property dict
or raises ValueError. No I/O in these validators. Integration uses board_tool's
existing remote transport; failure never prints COMPILE command completed or a
checked-policy success. Successful app builds identify policy `native-app-v1`.

Tests: independent parser mutation matrix, default/Immediate/MATCH commands,
bench unchanged, CLI/core/JSON/library/property/hash/artifact failures, preserved
compiler exit/output, app-upload guards, fresh output paths, no motion actions.
Established test assertions stay unchanged. Extend only controlled transport
fixture protocols where the newly documented read-only commands require it;
record that fixture adaptation separately from new independent expectations.
No locked test, source, config or installed package change belongs to D099.
