# D099 partial app-build checkpoint review

2026-09-23 20:15 Asia/Dubai. Separate fresh-context, same-model review of
contract `6b48779` and the current uncommitted tooling/tests. **Partial checkpoint
only: D099 adoption is not accepted, and this is not a phase-gate review.** The
user requested a pause; no further target, network, upload, reset or MCU action
was performed by this reviewer. D098's accepted ELF review is not repeated.

## Findings

- **[MAJOR] D099-R1 — tools/app_build_policy.py:112:** the property allowlist
  checks safety-flag metadata but does not constrain the effective compilation
  recipes, compiler commands or build hooks. `tools/app_build_pins.json:3` pins
  `platform.txt`, but no check rejects a `platform.local.txt` override. The
  cached official platform specification explicitly permits that file to
  replace/add properties without modifying `platform.txt`
  (`state/analysis/P2_bridge_dependency_raw/primary/arduino-cli/docs/platform-specification.md:541`).
  Starting with the actual saved default JSON, the local reproducer changes
  `recipe.cpp.o.pattern` from effective `MATCH=0/MOTORS_ALLOWED=0` to both1 while
  leaving the checked `compiler.cpp.extra_flags` property unchanged: validation
  still accepts. Replacing `compiler.cpp.cmd` or the existing prebuild hook also
  accepts. Unchanged pinned files and nonempty artifact hashes do not close this
  gap. Furthermore, `tools/board_tool.py:212` executes compilation before the
  property/file checks at223-224, so postcompile checks cannot prevent an
  unreviewed build hook from running. **Required on resume:** reject unreviewed
  local/global recipe overrides before compiling, constrain the effective
  compiler/link/recipe/hook configuration to the reviewed policy, and add
  independent failure tests. Keep D099 adoption pending until fixed/reviewed.
  Evidence: `P2_app_build_checkpoint_review_raw/probe_overrides.py` and
  `probe_overrides.json` (three changed properties, all accepted). These are
  synthetic local parser mutations, not evidence of actual installed overrides
  or a defect in the captured default binary.

No additional BLOCKER or MINOR finding was established in this bounded review.
The MAJOR remains open intentionally at the user's pause.

## Evidence checked

- Read AGENTS, current PROGRESS/FACTS/DECISIONS, D099 contract, active P2 scope
  and PLAN schedule. Current date is Wednesday23September; human phase gates
  and physical acceptance remain outstanding. No firmware, config, pins,
  locked tests or inert-upload allowlist changed in this task.
- Traced command selection: only canonical app uses the new policy; app uploads
  remain rejected before target lookup; default is0/0/wait, explicit Immediate
  is0/0/Immediate, MATCH is1/1/Immediate. The bench compile branch is unchanged.
  Fresh policy/source/mode/run paths are outside the sketch tree. Compiler
  process failure preserves separate output and prevents the success markers.
- Read final independent authored tests and their isolated failure injector.
  `state/analysis/P2_app_build_raw/author/final.json` and `final.stderr.txt`
  record **29 methods PASS**, exit0. This reviewer inspected that evidence;
  did not rerun the suite while the author/fixture workers were completing it.
  It covers parser mutations, upload guards, modes, fresh paths, CLI/core
  identity, nonzero status despite successful JSON, and hash/artifact failures.
- Fixture-only changes extend the recognized version/JSON/hash protocol.
  `state/analysis/P2_app_build_raw/fixture/established.stderr.txt` records
  **49 established SSH/ADB methods PASS**. Its `assertion_integrity.json`
  records all25SSH/all24ADB test methods and assertions unchanged. The source
  diff agrees: only fixture executable registration/dispatch changed in those
  established test files. Synthetic hashes are not artifact-existence proof.
- Original authored failures remain in `author/initial.*` and `injected.*`.
  New diagnostic wording expectations and the injector's assumption of separate
  hash batches were corrected; no established safety assertion was relaxed.
- Locally revalidated the saved default result with the production parser.
  `state/analysis/P2_app_build_raw/default_receipt/` and `target_default.json`
  record compile exit0, source `570ef35f`, program153684B, memory248308B,
  nominal remaining13836B, and the low-memory warning. Its recorded final ELF
  SHA256 `9808dc594d77be8f43865a17542a48b715b4d5ee4a1277d6f946d0a6ccb09e65`
  matches the already-reviewed D098 candidate receipt. This does not substitute
  for D099's still-pending complete current source/debug/temp/startup audits.

## Verdict and exact resume point

**FAIL for D099 adoption; partial checkpoint review complete.** Keep D099-R1
open and the implementation marked WIP. First fix/test/review the effective
recipe and precompile override gap. Then perform the still-unexecuted actual
Immediate/MATCH builds, phase-independent explicit-library resolution/rejection
experiment, and complete source/ELF/dependency/startup/export/memory audits for
the adopted modes. The library probe source now exists but has no target result.

No loaded/free-RAM, WCET, physical sensor/motor, startup-runtime or human-gate
qualification follows. Existing motor-run authorization rules remain intact.
Reviewer modified only this report and its accompanying review_raw evidence.
