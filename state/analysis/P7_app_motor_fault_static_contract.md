# D187 fixed static diagnostic validation adapter

25 September 2026. D186 host closure766abd20 precedes this offline task.
Implement only tools/app_motor_fault_static_policy.py. No compiler/transport,
stage claim, upload, board connection, firmware change or generic admission.
The later native caller reuses existing bounded execution; this adapter supplies
the missing exact metadata and artifact checks, not another process framework.

## Fixed interface and provenance

Expose PROJECT='app_motor_fault.ino',
FQBN='arduino:zephyr:unoq:link_mode=static', and
FLAGS='-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1'.
No profile selection, overrides, CLI or dynamic registration.

Reuse unchanged historical code in a private module namespace. Before use,
require these exact local files, ordinary file/ancestor paths with no reparse
points, each at most65536bytes, and these SHA256 values:

| Relative file | SHA256 |
|---|---|
| tools/app_build_policy.py | adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8 |
| state/analysis/P7_static_link_probe_raw/static_policy.py | ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775 |
| state/analysis/P7_static_link_probe_raw/static_reference.json | 1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b |
| state/analysis/P7_static_link_probe_raw/static_native_artifacts.py | cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0 |

Missing/changed/linked inputs fail explicitly. Importing the new module must not
dispatch commands or write files. Each public validation call checks its relevant
dependencies. Do not modify historical files, their globals in other consumers,
reference bytes, shared dynamic policy, board_tool or any established tests.

## Metadata checks

Public functions keep the D141 signatures:
validate_preflight(text, *, build_path, data_dir)
validate_compile_result(text, *, build_path, data_dir)

Delegate all original JSON, finite-number, platform/version/variant, path,
library, property-set and expanded-command comparisons to the unchanged D141
validator. In its private namespace only, adapt expected project name and flags.
The84-entry frozen expected-command reference contains exactly24 occurrences
of 'app.ino' and5 of '-DMATCH=0 -DMOTORS_ALLOWED=0'. Substitute those exact
tokens in the EXPECTED templates only, then perform the original literal path
substitution/checks. Raw compiler response and caller path strings remain exact.
Retain default/wait startup, static linking, discovery flag and every other
comparison. Return the original actual-properties dictionary, with its actual
new name/flags. Old project, inactive probe, MATCH/M1, dynamic/Immediate, extra
flags/libraries/commands and malformed/nonfinite/duplicate JSON fail.

## Artifact checks

Public function:
validate_artifacts(artifacts, native_tls_source, frozen_validator_source,
                   *, exported_flat_package)

Accept exactly seven actual filename keys (no legacy keys or extras):
app_motor_fault.ino.elf, app_motor_fault.ino_debug.elf,
app_motor_fault.ino_temp.elf, app_motor_fault.ino.bin,
app_motor_fault.ino.bin-zsk.bin, app_motor_fault.ino.elf-zsk.bin,
app_motor_fault.ino.map.
All values and exported_flat_package must be bytes. Exported flat package must
equal the build's app_motor_fault.ino.bin-zsk.bin bytes exactly. Build-file sizes
and ELF/package/init/TLS consistency are governed by unchanged D147/D142 checks.
Pass the identical byte objects to D147 under a fixed bijection replacing only
the app_motor_fault.ino filename prefix with app.ino. Never rewrite ELF/package
contents or infer source/artifact identity from a filename.

Preserve D147 source/TLS SHA checks and all six exact inherited TLS tuples.
On success return exactly these fields:
- status: STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS
- project, fqbn, flags: the fixed constants above
- artifact_aliases: actual filename -> legacy validator key
- artifact_sha256: actual filename -> SHA256 of the supplied bytes
- validator_report: unchanged complete D147 report, including its legacy keys
The outer explicit alias map explains those inner selectors; neither report
asserts the original app's source or any runtime observation. Propagate failure,
never return a success envelope around a rejected packet. Caller inputs stay
unchanged. This host structural result does not establish target compilation,
loader/native initialization/ABI, live RAM/stack/WCET or hardware acceptance.

## Acceptance and next dependency

Freeze independent contract-derived tests before execution. Use existing public
synthetic static/TLS fixtures as fixture mechanics, never implementation bodies
as expected behavior or real board artifacts as invented synthetic evidence.
Cover exact acceptance, raw input preservation, finite/duplicate JSON and paths,
each profile/command/property/library mutation, source pin/link failure, exact
seven-key mapping, export/build equality and inherited malformed package/ELF/TLS
rejection. Run in memory/owned RAM with Python-B; no compiler or native action.
Separate fresh-context reviewer inspects actual diff/tests/results. Existing
historical tests/source/pins remain intact. Only after this host closure prepare
the fixed native compile caller and separately reviewed fresh board invocation.
