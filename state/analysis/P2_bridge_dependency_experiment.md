# D098 isolated dependency-discovery experiment

2026-09-23 Asia/Dubai. D051/D075 select this bounded investigation alongside the
D097 passive getter correction. Read P2_bridge_dependency_audit.md and its exact
installed/versioned primary-source receipts first. No production build change is
selected by this experiment, and no memory saving or successful build is assumed.

Use one exact frozen actual-app source tree, default FQBN/core/library versions,
MOTORS_ALLOWED0/MATCH0 and default startup. Fresh separate board-Linux build and
output directories outside the sketch source must contain the control and candidate.
Control uses current flags. Candidate adds only the literal compile property
build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0.
CLI supports property overrides, but this bypasses normal discovery-phase semantics
and is not an official Bridge-disable option. Its acceptability remains unproved.

No MCU operation, upload/reset, new upload key, global/package edit, arbitrary
compiler flags, fake library/header, capacity/tunable change or alternate startup.
No later production tooling may inherit this experiment implicitly. Preserve actual
commands/status/output and independent source identity for both branches, including
failed builds. Keep all generated files out of the frozen source hash.

Acceptance for investigation: capture verbose expanded compile/link commands,
generated sketch, discovered library list/dependency files and all three linked
ELFs. Compare exact native application code and source hashes. Verify whether the
implicit Bridge/RPClite/MessagePack roots and constructors disappear, while actual
main/initVariant/static threads/setup/loop, native ownership/clock/pin APIs, imports,
math exports, safety paths and strong empty loop hook remain. Recompute actual
payload and loader overhead; a compiler fit is not a loaded free-memory/WCET result.

Use a separate fresh-context read-only reviewer before any production adoption.
If the candidate is viable, a following explicit build contract and independently
derived tooling tests must pin scope/version/invariants and fail closed; do not
apply it globally to bench sketches which may intentionally depend on libraries.
If it fails, retain the failure and continue other eligible memory work. No human
gate, physical evidence or motor authorization follows either result.
