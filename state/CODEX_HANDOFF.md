# Codex handoff - 2026-09-24 Asia/Dubai

Current phase is **P4 software under D128**. The user explicitly directed assumed
physical acceptance and continued development. This advances software scheduling;
unmeasured physical results and actual human gate records remain pending.
Read [CODEX_EXECUTION.md](CODEX_EXECUTION.md) for the current compact checklist;
[PROGRESS.md](PROGRESS.md) is the append-only phase/task history. This replaces
accumulated historical resume snapshots, retained in Git at `fbfb0f2e` and earlier.
Do not treat an old snapshot, template or synthetic test as current approval.

## Current software checkpoint

D130 is IMPLEMENTED/HOST-TESTED with fresh-context scoped review PASS. Source
b2229370 and original41-method oracle are unchanged after first-run112public
methods (41new+33countdown+38CSV) and13private methods pass. All648prior tracked
inputs and40protected files remain exact. Read analysis/P4_loss_analysis_validation.md.
Next P4 software task: bounded B9.4 push-through; read its options/source map,
adopt explicit lifecycle/eligibility/memory contract, then independent tests and
actual Robot/Escape integration. Default window remains0; no positive tuning yet.

D129 is IMPLEMENTED/HOST-TESTED with separate scoped review PASS and no open
scoped BLOCKER/MAJOR. Read analysis/P4_timing_evidence_validation.md and
reviews/P4_timing_evidence_review.md. All14 normal host targets pass; timing30-case
M0/M1 normal/sanitizer,32-case configured normal/sanitizer,149tooling+2registry
pass. A chronology finding was fixed with unchanged independent regression.
One new unaccepted tooling oracle was corrected from syntax assumptions to
actual compiler-rejection checks. Original failures and all oracle versions
are retained. All39 prior locked files remain exact; newe384e7fb is now protected.

D129 native compilation/default byte identity/MCU fit remain pending: current ADB
inventory found no board. No upload, reset, MCU run, physical result or gate in
this slice. Prior D128 reactive9ddaa2aa/ELF01e39e39 modeled free6512 and default
43d16734 free16 are historical figures, not D129 or live memory/WCET proof.

D130 adopted contract: analysis/P4_loss_analysis_contract.md. Existing CSV/countdown
tools stay unchanged; new analyzer usage is in docs/target_loss_analysis.md. Positive push-through is
another P4 software dependency: edge.cpp currently requires0; implement and
verify original bounded B9.4/R5 semantics before positive tuning, retaining default0.
Use analysis/P4_software_acceptance_packet.md for all deferred physical criteria.

P3 software preparation is complete (D123 drive, D125 turns, D126 stop, D127
countdown analysis); actual3.1-3.7 and human gate remain pending. Its acceptance
packet and original failures are retained. D128 reactive GO enters SEARCH with
no opener, then actual perception/contact/stall/edge paths.

User-requested storage cleanup43319eec removed inspected closed temps and
rebuildable host outputs. NTFS compression preserved all21145 evidence files
byte-for-byte. See analysis/DISK_CLEANUP_20260924.md. Use /dev/shm builds and
TMPDIR=/dev/shm, archive receipts in the same invocation and run heavy jobs
serially. Initial D129 WSL service interruption was environmental, not a test
result; partial logs are retained. Check C: free space before further artifacts.

## Historical board and P2 evidence

D118 completed one exact bare-board default/M0 app upload and passive observation
in `fbfb0f2e`. See [actual validation](analysis/P2_app_default_actual_validation.md)
and F147: source e820c0e1, sampled RUNNING/NONE, heap 4,500 free / 4,364 largest. Stored
513 us is not full-source WCET. Initialization and optional grants remained false.
The app remains loaded and may continue inhibited native ticks. Both run claims
are consumed; no replay/reset/restore under that run. Last board observation is
historical evidence, not an assertion that the present connection is unchanged.

D119 (`1c387810`) implements the pure finite B4 sequence. D120 contract f4a300c5
now integrates it through actual Robot/Runtime/Governor/MotorGate in a separate
compiler-wide bench profile. See [validation](analysis/P2_stand_integration_validation.md):
normal and ASan/UBSan all4targets pass; main1496, Gate187, new18cases eachM0/M1;
configured synthetic-button overlay19cases eachM0/M1 normal/sanitizer. All54policy
checks and9private profile probes pass. New locked safety oracle4546df24 stays fixed.
Default sourceef1efc59 reproduces exact D118 ELF/ZSK/loader; motor_direction24fe6356
compiles with M0 and empty grants, conditional loader free span13568. No MCU action.
The full hold, sources, edge priority, final electrical cap/coast and receipts are
retained; D103 service reset is unavailable in the stand profile. This software
does not establish physical B4 acceptance. P3 DRIVE_TEST is the next software task;
full B7 reversal still conflicts with R6. D120 is committed as1c2389c9 with scoped
review PASS. D121 leaves B7 unaccepted and preserves the original criterion/R6.
Use [the consolidated packet](analysis/P2_software_acceptance_packet.md) and its
fresh readiness review for remaining physical/external acceptance. D122 supersedes
the D121 stop on P3 scheduling; implement DRIVE_TEST without repeating completed P2 work.
The fresh D121 review passes the limited software/evidence characterization but
fails full P2 acceptance with P2-ACCEPT-1..5. This session made implementation and
checkpoint progress; the goal is not complete. Resume P3_first_drive.md software
under D122; do not manufacture measurements or repeat blocker audits.

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
