# Codex handoff - 2026-09-24 Asia/Dubai

**Current: P7 awaiting release prerequisites; D137 documents closed2700da11.**
User resumed from
c4fadad0 and requests commits as tasks finish. P5 software is complete; actual
physical and human phase gates remain pending. The software-first scheduling
assumption is not measured acceptance. See [checklist](CODEX_EXECUTION.md) and
append-only [phase history](PROGRESS.md). Historical pending snapshots remain in
Git; this checkpoint supersedes their next-task text, never original receipts.

## Current software checkpoint

- D134closed d6a8319e: mode availability and all host/configured/sanitizer/private
  checks pass. See analysis/P5_mode_availability_validation.md.
- D135closed70c964a7: real qualified opener-abort producer,20hosttargets,
  public40/configured42 and13private perM0/M1 normal/sanitizer, tooling/layout/fault
  checks pass. New safety coverage accepted;43protected source files total.
  See analysis/P5_abort_timing_validation.md; retain original failed draft receipts.
- D136closed0faf2e6d, source5277dec0/8e002c6f:93public including65536cuevalues,
  19private and112unchanged-dependency regressions PASS;694prior inputs and
  43protected unchanged. Separate reused-context same-model scoped review PASS.
  See analysis/P5_abort_analysis_validation.md and reviews/P5_abort_analysis_review.md.
  Finite source syntax validation does not prove general C++, firmware origin,
  physical timing, common attempt, transport, producer semantics or a human gate.
- MATCH/Immediate target compilation finished beforepause; resumed file/accounting
  and import review completed418624cd/2dbae98b:1584Bconditional loader span and
  62resolved imports. See analysis/P5_match_native_validation.md. No live
  stack/RAM/WCET or upload claim follows. All jobs are terminal.

D134default app has32B modeled deficit. Two isolated candidates failed24/32B and
remain UNADOPTED; no third candidate or candidatehosttests. UnmodifiedD135default
has not been targetcompiled. D135inert wrapper conditional1328B omits the default
native dump owner; neither wrapper nor MATCH qualifies the default build.

P7 original7.2/7.4 and blank7.3 records are now written and scoped-reviewed in
2700da11. The P7.1 build-only example is corrected.52links/9fragments and43protected
hashes pass; production/tools/tests unchanged. P6 remains deferred. No print,
rehearsal, release tag, operator-readiness or human gate is claimed. Read
analysis/P7_software_acceptance_packet.md and reviews/P7_operator_docs_review.md.

Next: act on newly supplied real P0-P5 qualification evidence or the exact native
transport prerequisite receipt/plan; then resolve openSC-AP against that qualified
release (matrix READY/battery criterion, full rearm and capture preservation).
Do not enable hardware grants from assumptions, reuse a run grant, rerun completed
matrices, retry denied cleanup or invent another helper to bypass missing evidence.
Draft preparation is finished and no background job remains. Resume instructions
and the pending gate request identify the actual external acceptance still needed.

## Historical board and acceptance evidence

Last actual MCU upload was consumed D118defaultM0 sourcee820c0e1, fbfb0f2e. F147
and analysis/P2_app_default_actual_validation.md record sampled RUNNING/NONE and
4500Bfree/4364Blargest heap. Stored513us is not full-source WCET. Do not infer
current loaded state or reuse its run grants. Current resume only read Linux
inventory/file identities; no new compile/upload/reset/MCU read or run occurred.

D119/D120 finite B4 direction software is complete/reviewed; physical B4 remains
pending. D121 preserves the full-reverse/R6 B7 conflict as BLOCKED. D122 permits
subsequent software work, not fabricated acceptance. P2/P3/P4/P5 acceptance packets
map original criteria to evidence and missing trials. Current empty SetupGrants,
physical button windows/pin/electrical/sensor qualification, live stack/WCET,
source-bound deployment and native dump transport remain unresolved dependencies.
Read analysis/P2_native_dump_prerequisite_followup.md before transport work; no
repeated ownership/framing/cancel/reopen guesses or sudo workaround.

Bare UNOQ is user-reported connected; no additional hardware is requested now.
D131push-through window remains0; no tuning occurred during D136/P7. Preserve
unique failures, reviewed oracle adjudications and actual versus synthetic labels.
Use /dev/shm and one compiler. C:2.135GBfree at22:18Dubai; prior denied85.48MB and
1.70MBcleanup batches remain, no retries. See STORAGE_LOG.md for retained artifacts.

## Authority and roles

D015 supersedes only D009's agent assignment: Codex implements/orchestrates;
a separate context reviews read-only. Legacy Claude documents remain provenance.
Four native contexts are available. Assign exclusive file ownership; coordinator
alone changes shared interfaces/config/build/state, merges FACTS and assigns IDs.
Independent test authors read specs/public headers, not implementation bodies;
freeze executable expectations before first execution. Separate same-model Codex
review is not cross-model or human review. Log analysis uses actual evidence only.

D051 delegates engineering choices and D075 permits P2 software before physical
acceptance. Neither supplies physical facts, PINMAP/EXPLAINED/gate entries or a
specific motor run. User reports the UNO Q connected alone and permits inert tests;
no additional hardware is requested now. Never upload/run motor-capable firmware
without fresh identified STAND OK/RING OK. No locked test changes without the
required human decision. No push, tag movement, history rewrite or secrets.

## Sources and tools

The takeover loaded AGENTS/CLAUDE/README, all four .claude role definitions,
PLAN/HARDWARE/BEHAVIOR, P0-P7 prompts, kickoff/resume/review prompts and state ledgers.
On resume read root AGENTS fully, current state and relevant active-phase sources;
check nested instructions before edits. Historical source-load claims are not a
substitute for this refresh. Imported bootstrap workflows are unrelated here.

Observed Windows/PowerShell/WSL environment is recorded in analysis/environment.md.
Fresh local 2026-09-24 checks: WSL Ubuntu g++13.3.0, CMake3.28.3, Python3.12.3.
Windows Python3.13/Git2.52 observations are historical. C: has limited space;
check it before artifacts/builds, use WSL /dev/shm for isolated builds where useful.
WSL auto-shutdown can erase /dev/shm between invocations: archive results/build
metadata in the same live invocation. D120 normal build/status output survived,
but its later LastTest copy did not; full sanitizer LastTest was preserved.
Use `git -c core.longpaths=true`. Intended firmware compilation remains board-side
SSH with verified ADB fallback; actual prior runs used ADB serial2629958581.
Exact installed toolchain/startup/loader identities are in FACTS and each checked
build receipt, particularly D118's actual_build_receipt. Do not infer fresh access
or reuse old upload grants. Credentials stay outside tracked files.

## Deadlines and resumption

Use actual Asia/Dubai time. P3 not passed by end28September invokes the documented
scope cut; P6 needs P4 by30September and no stronger cut. Freeze1October21:00;
rehearsal2October; competition3October. No cut/freeze was due at this checkpoint.
Resume with docs/prompts/CODEX_RESUME.md. Commit bounded finished tasks promptly,
record actual tests/failures/evidence, and stop at real external blockers rather
than inventing a phase pass or promising unattended completion through human gates.

PROGRESS.md contains legacy non-UTF8 separators: append without re-encoding
historical bytes. Historical checkpoints remain in Git; this current section
supersedes their pending-task text, never their original receipts.
