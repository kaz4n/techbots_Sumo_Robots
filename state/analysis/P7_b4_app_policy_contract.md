# D213 B4 ordinary application policy

Adopted under D051 on 26 September 2026. This is host-only policy software, using
the existing app.ino entry. It grants no build, upload, hardware acceptance or
motor-run permission. Existing firmware, config and seven inert wrappers stay
unchanged. B4 STOP/reset refusal and IDLE-only dump restrictions remain.

The new tools/b4_app_static_policy.py exposes validate_preflight(text, *,
build_path, data_dir, motors_allowed, snapshots), validate_compile_result with
the same arguments, and validate_artifacts(artifacts, native_tls_source,
frozen_validator_source, *, exported_flat_package, motors_allowed, snapshots).
No default motor selection exists. Exact integer0 or1 is required; bool,
subclasses, floats, strings and other values are refused before snapshot
validation or private execution.

Snapshots must be an exact dict with exactly the five ordinary string keys below
(no key subclasses), and exact bytes values. Verify every length/hash before any
private execution, copy the mapping per call and permit no source-data rereads,
writes, subprocess or transport. Inherited read-only module-location resolution
is allowed. Snapshot values are immutable; input/result dictionaries do not alias
other calls. Private module state must survive M0/M1/M0 calls without leakage.

| Snapshot | Bytes | SHA-256 |
|---|---:|---|
| tools/app_motor_fault_static_policy.py |8262|3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270|
| tools/app_build_policy.py |14956|adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8|
| state/analysis/P7_static_link_probe_raw/static_policy.py |4836|ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775|
| state/analysis/P7_static_link_probe_raw/static_reference.json |17809|1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b|
| state/analysis/P7_static_link_probe_raw/static_native_artifacts.py |3718|cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0|

Privately reuse the unchanged D187 adapter and its four dependencies. Route its
checked source reads exclusively to the validated snapshots, select project
app.ino, static/default FQBN arduino:zephyr:unoq:link_mode=static, and seven
identity artifact filename aliases. Preserve every validation body, raw response,
path and artifact byte object forwarded to the historical checks.

Exact flags, with only the indicated integer substituted:
-DMATCH=0 -DMOTORS_ALLOWED=<0|1> -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0 -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0 -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0

Reject alternative, reordered, extra or duplicate flags, other project names,
Immediate startup and dynamic linking. Keep the84-property reference,
24project-name and5flag-substitution checks. Metadata APIs return the complete
historical property dictionary. Artifact validation retains all ELF/TLS/layout,
three-image, flat/ELF-package and exported-package checks, returning the unchanged
report fields except status STATIC_B4_APP_LAYOUT_PACKAGE_PASS and an added
motors_allowed field. That field declares the validated profile selection; binary
contents alone do not prove compiler origin, motor authorization or runtime state.

Independent spec-derived tests cover both profiles, malformed inputs and private
snapshot/isolation boundaries, plus applicable D187 metadata/artifact semantics.
Keep the original33-case suite untouched. Root seals implementation before reading
the new tests; a separate same-model reviewer checks source and saved host results.
Run focused Linux/Windows suites serially with isolated temporary storage and
Python-I-B; preserve failures. No target command follows this policy acceptance.

Separate checked build/deploy admission, target artifacts/loading, physical grants,
fresh STAND OK for a specific M1 run, retained-memory recording delivery and the
actual commissioning measurements remain necessary.

