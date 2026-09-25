# D163 additive checked compile-only route (draft)

The new motor_fault diagnostic needs the existing checked build/ELF validation
used by motor_stand. Add only the literal bench/motor_fault and motor_fault.ino
to the matching checked/default-inert/project selectors in tools/board_tool.py
and tools/app_build_policy.py. Preserve all existing recipe, installed pin,
profile, source-admission and upload manifests and existing tests byte-for-byte.
Do not repin old D141-D161 probes: their consumed historical source bindings must
refuse edited tooling. D162 source/contract/header/oracles stay unchanged.

Default M0/MATCH0 --compile-only accepts the literal diagnostic and invokes
compile_app with project=motor_fault.ino. MATCH, Immediate startup, upload,
foreign run options and sketch.yaml/sketch.yml refuse before target access.
Use existing source staging/compiled artifacts/ELF checks and exact project recipe
specialization. Compilation/policy/artifact failures propagate; no upload call or
new key in p0_inert_sources.json follows. No user-supplied project/name aliases.

Author an independent companion tests/tooling/test_motor_fault_policy.py from
these requirements/public signatures and old public policy test patterns, before
execution. Cover exact default route and flags, all refusals, specialized recipes,
failure propagation and unchanged historical tests/manifests. No implementation
body is the source of expected results. Test in RAM; no board/compiler dispatch.

This is a host tooling change only. The checked route itself does not yet supply
--jobs1 or a remote process-tree deadline; do not claim those are added by the
five literal admissions. An actual board build must use a separately reviewed
fixed caller with explicit pinned CLI/empty config/minimal environment, fresh
source/tool checks and unique paths, --jobs1, remote process-group deadline/reap,
recorded outputs and artifact identities. Reuse existing helpers/validators; no
new general framework. Do not inherit capture/upload file-size caps into a compiler.
Target compile is not upload, runtime qualification, physical acceptance or gate.
