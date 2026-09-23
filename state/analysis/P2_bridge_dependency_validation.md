# D098 actual dependency experiment

2026-09-23 Asia/Dubai. Contract e870cc9; frozen D097 source from 3d84958.
EXPERIMENT TARGET-COMPILED; separate fresh-context same-model review PASS.
This result does not yet change production build commands or permit an upload.

Both branches use the exact 82-file actual application source
`570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84`,
CLI1.5.1/01f3d4f2b, core1.0.0, default startup and MATCH0/MOTORS_ALLOWED0.
Only the candidate adds the literal property
`build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0`.
Separate new build/artifact directories are outside the frozen sketch tree.
Exact argv, timestamps, statuses and separate stdout/stderr are in
`P2_bridge_dependency_raw/570ef35f_{control,candidate}.json` and adjacent files.

| Result | Control | Candidate |
|---|---:|---:|
| Actual compiler exit | 1 | 0 |
| Program storage | 210600 B | 153684 B |
| Compiler-counted RAM payload | 275760 B | 248308 B |
| Nominal remainder against 262144 B | -13616 B | 13836 B |

The real payload reduction is 27452B. No capacity, rate, pin, safety branch,
source, startup mode, loader, installed package or entry point changed. The
property uses CLI's override mechanism but is not an official Bridge-disable
option; it bypasses normal discovery semantics. Original control failure remains.

Independent source/ELF/object review verifies all six downloaded ELF files against
remote hashes, all 82 source files and generated INO CPP identity. Both branches
have exact source-file-set postchecks. The control's precheck verified each
expected file; the candidate additionally enumerated the whole set before compile.
The collector's exact postcheck applies to both, with generated artifacts excluded.

Only the RouterBridge singleton object disappears (74 objects become73).
1438 common allocated sections were compared: apart from the reviewed app static
initializer, bytes/size/alignment/relocation targets are unchanged, including2904
relocations. All493 retained project function identities remain. Runtime168888B,
NativeSources848B and all DT-derived pin tables retain their sizes.
The actual app constructor, main/initVariant/static-thread start/setup/loop and
strong empty loop hook remain. Init/fini counts12/10 become1/0; the removed roots
belong to unused Bridge/Serial/HCI/RPC objects. All244 metadata texts match hashes.

Imports188 become176 with no additions;39 retained native exports and42 unchanged
AEABI bindings are present in the identical loader. The only removed native-export
subset entry is device_deinit; LPUART1 ordinal78 remains. Current app does not yet
instantiate the native dump owner. Its compiled object remains identical; this
experiment neither integrates nor budgets that future owner or local reset UI.

Separate review recomputes a conditional pristine-loader peak252472B, leaving
9672B chunk span/9668B largest payload. This assumes the pinned persistent-flash
peek/allocator model and no extra constructor/interleaved allocations. It is not
an actual load, measured free RAM, stack bound, complete800us or physical proof.
Detailed assumptions/section arithmetic: `reviews/P2_bridge_dependency_review.md`.

No broad host suite rerun is needed for this analysis-only experiment; D097's
normal/sanitizer1418main+173Gate results remain the latest software validation.
No MCU upload/reset/read/write or motor operation occurred. Last known image is
still D0911502e948. Seven inert keys and all production tools remain unchanged.

Next: separate app-only build-policy contract and independent tooling tests,
including strict CLI JSON dependency validation, pinned identities, unchanged
bench/upload guards and actual default/Immediate/MATCH compile evidence. The
ordinary production build still exceeds RAM until that policy is adopted and
validated. Physical acceptance, loaded RAM/WCET and every human gate remain open.
