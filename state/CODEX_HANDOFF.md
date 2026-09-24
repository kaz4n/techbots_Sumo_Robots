# Codex handoff - 2026-09-24 Asia/Dubai

**RESUMED by user, 2026-09-24 21:49 Asia/Dubai**, from c4fadad0.
P5 remains active. D136 public74/74 and prior112regression PASS; private18/19
original failure and duplicate-declaration review finding are being adjudicated.
MATCH compile-only already finished; loader/import checks are in progress.
The preserved pause checkpoint is state/analysis/P5_pause_20260924_1610.md.
Current results below are historical until the next completed-task update.

Current phase is **P5 software under D134**. The user explicitly directed assumed
physical acceptance and continued development. This advances software scheduling;
unmeasured physical results and actual human gate records remain pending.
Read [CODEX_EXECUTION.md](CODEX_EXECUTION.md) for the current compact checklist;
[PROGRESS.md](PROGRESS.md) is the append-only phase/task history. This replaces
accumulated historical resume snapshots, retained in Git at `fbfb0f2e` and earlier.
Do not treat an old snapshot, template or synthetic test as current approval.

## Current software checkpoint

P5 is active under D134/D135/D136. D134 host closure is committed d6a8319e:
all18 ordinary targets, four availability-pair M0/M1 sanitizer/private matrices,
positive20 timing supplement and60+296 tooling PASS; separate scoped review PASS.
Read analysis/P5_mode_availability_validation.md. Its new locked source is protected.

D135 qualified opener-abort production is committed2d924f1f. The first public
failures were independently traced to new draft assumptions; originals retained,
reviewed corrections committed94a7bb5d. No42 established protected file changed.
D135 is now closed70c964a7: full20targets, public40/configured42 plus13private
perM0/M1 normal+ASan/UBSan,18new/74admission/296regression,72layoutpairs and8faults
PASS. Separate fresh-context review PASS; newlocked e9fd accepted,43protected.
All prior656 inputs and42protected exact; all completed host scratch released.
Read analysis/P5_abort_timing_validation.md; preserve originals and do not rerun
completed matrices without relevant changes.

D135 native compile/conditional fit PASS in4b1e701e (F149): exact2d924f1f source,
ELF9583f94d, model1328B free. This wrapper omits default app dump transport.
D134 default-app model deficit32B is observed. Two isolated source-equivalent
candidates failedfit24/32B and remain UNADOPTED inbea923c8; no thirdoptimization
compile or candidatehosttests. UnmodifiedD135default has not been targetcompiled.
Separate unmodified production MATCH/Immediate compile-only session25141 is
active or recently finished: inspect P5_match_native_raw terminal receipts.
No upload/reset/MCU operation occurs in these compile checks.

D136 offline analyzer contract is adopted,74public/19private probes frozen before
implementation; pure cue decoder tests all65536values. Publicfiles transferred
unchanged to tests/tooling;694priorinputs bound. Worker owns new analyzer+notes;
root owns execution/docs. No implementation execution until firstsourcehash is
reported. Current privatefreeze includes the reviewed closure clarification.
Read analysis/P5_abort_analysis_contract.md and its separate design review.

P3/P4 software evidence and deferred physical metrics remain in their acceptance
packets. D131 bounded push is implemented/reviewed; shipped window remains0.
Native transport ownership/framing, full-source WCET, live stack/RAM, actual
sensor/button/pin/mechanical trials and human gates remain pending.

User storage policy: preserve compact evidence, use owned /dev/shm scratch and
one host compiler. Two automatic-review-denied cleanup batches (historical85.48MB
and new1.70MB duplicate stage) remain; do not retry by another route. No checked
ELF, source, unique evidence, user file or persistent virtual disk is disposable.

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

PROGRESS.md contains legacy non-UTF8 separators: append without re-encoding
historical bytes. Historical checkpoints remain in Git; this current section
supersedes their pending-task text, never their original receipts.
