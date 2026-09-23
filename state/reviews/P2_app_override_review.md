# D100 local remedy review of D099-R1

2026-09-23 Asia/Dubai. Separate fresh-context, same-model, read-only review of
contract `d338d1d`, its current clarification and the current tooling diff.
**PASS within the local D100 remedy scope: no open BLOCKER, MAJOR or MINOR
finding established. D099 target adoption remains pending.** This is not a
cross-model review, human gate, target qualification or permission to upload.
The user requested completion of this task followed by a pause; this reviewer
performed no board, network, USB, upload, reset, start or MCU operation.

## Finding disposition

**D099-R1 MAJOR: addressed by the reviewed local source and host evidence.**
`tools/app_build_policy.py:120` now checks both the complete selected command
key set and exact normalized values. `tools/board_tool.py:209` resolves active
directories, rejects known overrides, verifies the 18 selected installed hashes
and validates a separate expanded-properties preflight before the real compile
at line 245. The original reviewer script, unchanged, now rejects all three
original effective recipe/compiler/prebuild mutations. Its saved default
positive control still accepts. Evidence is
`P2_app_override_review_raw/original_reproducer_current.json`.

This closes the demonstrated local validation/order gap, not the remaining
D099 acceptance work. Corrected-wrapper default/Immediate/MATCH target builds,
the explicit-library fixture experiment and required source/object/ELF audits
were not supplied as completed D100 evidence at this review checkpoint.

## Evidence and source checks

- Independently reconstructed all **84** command templates from the unchanged
  actual default compile JSON (SHA256 `416a0f71c229863fc8e4325138b9eae8897bd439979bb4afac84c21a4e08ca69`).
  Only exact data/build roots, the approved safety flags and two packaging
  argument positions are normalized. The resulting dictionary equals
  `tools/app_build_commands.json` exactly. Immediate's argument is supported by
  cached pinned platform.txt lines 69, 95-97 and 164-165, and boards.txt lines
  59-63, under `state/analysis/P2_bridge_dependency_raw/installed/core/`.
- Reviewer-owned opaque-validator probes pass **19 positive controls and
  3,118 rejection cases** across default 0/0/wait, 0/0/Immediate and
  1/1/Immediate, using three path pairs including spaces and literal semicolons.
  Every selected property is independently altered and removed in both public
  validators. Added hooks, numbered recipes, compiler/preprocessor/ctags
  entries and invalid modes also fail. Preflight deliberately does not infer
  discovered-library emptiness; real-result validation rejects a nonempty list.
  See `P2_app_override_review_raw/reviewer_probe.py` and `.json`.
- Independently reran the **46-method** authored D100 suite through local WSL:
  PASS, exit 0, 26.273 seconds. Raw stdout/stderr are retained in
  `P2_app_override_review_raw/integration.*.txt`. Controlled fixtures prove
  directory parsing failures, six regular override files, six dangling links,
  remote stale profile names, precompile hash faults and failed/altered
  properties prevent real compilation. The shell fixture executes the actual
  fixed probe with isolated paths; it is not a target filesystem test.
- Reviewed local profile refusal before transport selection
  (`tools/board_tool.py:261`), and remote sketch.yaml/sketch.yml refusal after
  synchronization, before properties (`tools/app_build_policy.py:204`). The
  `test -L` branch prevents dangling links being mistaken for absence. Both
  resolved global roots and selected local platform/boards override files are
  checked; profile initialization cannot bypass the pinned ordinary package
  route through these accepted sketch paths.
- Primary-source control flow supports the chosen preflight: cached
  `schema/primary/commands/service_compile.go:312-320` expands properties then
  returns before preprocessing/build; used-library collection is registered
  later at lines 333-344. `schema/primary/internal/arduino/builder/builder.go:304`
  places the prebuild hook inside preprocessing. These paths are relative to
  `state/analysis/P2_bridge_dependency_raw/`. This source proof is narrower than
  claiming zero effects: CLI instance initialization and explicit build-directory
  creation can still occur.
- Checked cached config-get/default/environment lookup and profile/global/local
  loader paths against `P2_app_override_source_audit.md`. Rehashed all **47**
  primary source files against its recorded SHA256 and pinned-tree Git blob
  identities. No new source retrieval occurred in this review.
- Examined the production diff: arbitrary build-property/FQBN/profile switches
  are not exposed; app uploads still fail before target lookup; bench command
  construction and inert-upload rules are retained. All **78 established test
  method ASTs** (25 SSH, 24 ADB, 29 D099) are unchanged versus `cf61b84`.
  Fixture/protocol/helper changes were inspected separately; equal test ASTs
  alone would not prove their semantics. The author/fixture final 78-method
  run is separate evidence, not a run claimed by this reviewer.

## Limits and next action

The policy assumes the same stable CLI/configuration, environment, cwd and
installed files across independent remote commands. It is not a sandbox against
a compromised host, executable replacement, permissions changing between checks
or concurrent overrides appearing after preflight. Postcompile checks detect
selected drift but cannot undo an already executed hook. These limits agree
with the D100 contract; no broader adversarial-host protection is asserted.

Properties-only success proves neither a binary nor no discovered libraries.
The real compile and artifact checks remain necessary. The 18 hashes are the
selected pinned set, not every byte in the installed toolchain. Target runtime,
loaded RAM, worst-case tick timing, physical acceptance and every human phase
gate remain unproved here. The date is Wednesday 23 September, the planned P0
gate day; the schedule does not turn pending acceptance into a passed gate.

Modified files: this report and `P2_app_override_review_raw/` only. Exact reviewed
tool/contract hashes and primary/test identity checks are in reviewer_probe_final.json.
The final repeat includes the explicit 84-key/path clarification; the initial
probe receipt is retained separately. Implementation hashes did not change.
Next action: root records this local review, checkpoints the unfinished target
acceptance work and pauses as requested. Resume target work only after the
user resumes; this review does not authorize an upload or motor run.
