# Codex handoff - 2026-09-24 Asia/Dubai

Current phase is **P2 software under D051/D075**. No human phase gate has passed.
Read [CODEX_EXECUTION.md](CODEX_EXECUTION.md) for the current compact checklist;
[PROGRESS.md](PROGRESS.md) is the append-only phase/task history. This replaces
accumulated historical resume snapshots, retained in Git at `fbfb0f2e` and earlier.
Do not treat an old snapshot, template or synthetic test as current approval.

## Current work and board

D118 completed one exact bare-board default/M0 app upload and passive observation
in `fbfb0f2e`. See [actual validation](analysis/P2_app_default_actual_validation.md)
and F147: source e820c0e1, sampled RUNNING/NONE, heap 4,500 free / 4,364 largest. Stored
513 us is not full-source WCET. Initialization and optional grants remained false.
The app remains loaded and may continue inhibited native ticks. Both run claims
are consumed; no replay/reset/restore under that run. Last board observation is
historical evidence, not an assertion that the present connection is unchanged.

D119 (`bf2c4524`) adopts a pure finite B4 directional request sequence. Separate
implementation/test contexts completed it: 18 new tests, full 1,496 main + 187 Gate pass
in normal/sanitizer,12 private reviewer profiles and scoped review PASS. See
[validation](analysis/P2_stand_sequence_validation.md) and the checklist. One
Linux compile-only build 62e38204 produced exact unchanged D118 loadable bytes;
no new MCU action. Resume the actual B4 integration contract next.
It has no motor authority. Actual Robot/Runtime directional integration remains
unfinished and must preserve real sources, full hold, edge priority, governor,
MotorGate and receipts. P3 DRIVE_TEST stays unavailable. Existing B4 bench only
covers setup/inhibition. Full B7 reversal still conflicts with R6.

Native dump execution is blocked by UART-holder visibility and unproved clean
cancel/reopen. Read [the exact follow-up](analysis/P2_native_dump_prerequisite_followup.md).
An earlier passwordless sudo attempt already failed; don't repeat it or guess a
password. No grants follow from TCP CONNECTED, GPIO ready, flush/open success or
elapsed silence. Continue genuinely independent P2 software rather than adding
another helper that fabricates readiness.

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
