# D139 read-only stage reuse: probe interface

This is the public contract for independent controlled probes. The adapter has
not been executed. Passing this contract does not authorize compilation; the
coordinator separately requires review, probe results and an explicit go.

```python
verifiedStage(board_tool, sketch, source_manifest, stage_manifest)
    -> (stage_path: pathlib.Path, receipt: dict)
```

`board_tool` provides the existing `ROOT` pathlib.Path, `check_source(path)`,
`validate_push_through_config(path)`, `validate_mode_availability_config(path)`
and `fail(message)` interfaces. Existing `fail` raises SystemExit; controlled
substitutes may supply a raising failure callback. No original `stage` call,
transport, compiler, writer, deletion or fallback is part of this interface.
Its only accepted sketch is the full `app`.

Source input shape, also shown in `working_source_manifest.json`:

```json
{"files": {"src/app/app.ino": {"sha256": "64 lowercase hex characters", "bytes": 829}}}
```

The complete real manifest contains exactly 103 current `src/` file names.
`bytes` and other top-level provenance fields are metadata; exact names and
SHA256 values define the byte check. They bind the current final687-input host
freeze `state/analysis/P7_readiness_raw/freeze_final.json`, not the old683 test
manifest. Controlled substitute trees need not contain real firmware; they must
exercise the complete fixed-count source/stage relationship.

Stage input shape, also shown in `checked_stage_manifest.json`:

```json
{"source_sha256": "64 lowercase hex characters", "files": {"app.ino": "64 lowercase hex characters", "src/config.h": "64 lowercase hex characters"}}
```

The real manifest contains exactly 102 staged files. `app.ino` maps to current
`src/app/app.ino`; every other staged path maps to the identical current source
relative path. Each staged hash must equal its source hash. The ordered digest
is SHA256 over sorted stage-relative UTF-8 names followed by NUL and their exact
file bytes, using the established staging digest convention. Real expected
digest: `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.

Success returns the existing `ROOT/build/stage/app` and:

```json
{"source_files": 103, "stage_files": 102, "source_sha256": "fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2", "read_only_reuse": true}
```

The wrapper separately adds a UTC timestamp and writes that receipt only to its
new raw evidence directory. The adapter itself writes no receipt or other file.

Required independent probes include successful exact reuse and rejection of
absent/extra/changed source files, absent/extra/changed stage files, mismatched
source-to-stage mapping and digest, wrong sketch, source/stage symlinks or unsafe
ancestry, and reserved sketch-local `src/{config.h,core,hal,app}` conflicts.
Existing source checks for app parent and src, path containment checks, and both
current configuration validators must remain active; validator failures must
propagate. The real source/stage file sets and hashes must remain unchanged.

Controlled substitutes must trap source/stage write or deletion and original
stage/fallback calls. No file drift case may be repaired or ignored. No board
access or compiler is needed for these probes. Profile settings remain outside
the staged source bytes and are handled by unchanged flash_profile/build policy:
the later default build must use default startup, MATCH0 and MOTORS_ALLOWED0.
