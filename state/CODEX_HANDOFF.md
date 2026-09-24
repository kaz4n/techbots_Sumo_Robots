# Codex handoff - 2026-09-24 Asia/Dubai

**D139 qualification complete: compiler PASS, conditional default fit FAIL.**
The unchanged default/M0 image exceeds the modeled loader pool by592 bytes.
Exact evidence is in analysis/P7_default_qualification_validation.md and its
separate review. No repair, further compile, upload or reset followed. The next
read-only investigation traces the pinned package's Static linking mode; current
policy remains dynamic-only and no static probe or policy change is authorized.


**Active phase: P7 software/release preparation.** D138 informational READY and
battery-threshold software is implemented, host-tested and target-compiled.
Its separate fresh-context review passes with no open findings; see
[validation](analysis/P7_readiness_validation.md), [review](reviews/P7_readiness_review.md)
and [checklist](CODEX_EXECUTION.md). Physical and human gates remain pending.
User requests continued work, bare UNOQ testing when useful, prompt commits and
storage conservation. Software-first scheduling never creates measured acceptance.

## Current checkpoint and exact next task

D138 production remains first-source d19f8964 (interfaces36a96bd2). Normal20cases
perM0/M1, configured29public+2private perM, normal/configured ASan+UBSan and full22
host targets pass. Original new-draft failures and independently reviewed repairs
are retained; no production repair or existing protected-test amendment occurred.
Final687input freeze0fe188b7 and43protected sources are exact. Fullordinary inputs
remain valid after a configured-only oracle correction: exact M0/M1 preprocessor
comparison proves unchanged ordinary translation. Root checked82links/9fragments.

Exact MATCH/Immediate compile passed on bareUNOQ with one compiler, no upload:
sourcefcddbd8e, ELFcb5fbb53, receipt04b266d5. Conditional pristine-loader peak261280B
leaves864Bspan/860Blargest payload;62imports resolve,16target layouts and72legacy
offsets unchanged. This is not actual loading, live RAM/stack or WCET. Read
analysis/P7_readiness_native_validation.md and its retained checked evidence.

D139 now supplies the missing current default baseline: one checked default/M0
compile passed, receipt52b4ba3a and ELF72a8bfcd. Ordered loader fit fails by592B;
all61 imports resolve and16 types/79 old offsets match historical default.
No source or test changed. The original negative validator exit1 is retained.
See analysis/P7_default_qualification_validation.md and the separate review.

A bounded source inspection found no justified single repair; old24/32B failed
candidates remain unadopted. Current recipes already use -Os/gc-sections.
The official pinned package exposes a distinct Static linking option, which the
current checked policy does not admit. Next: finish primary-source tracing of
its loader/placement/address contract and prepare a separately reviewed scope
only if supported. Read analysis/P7_default_fit_options.md. Do not compile,
change policy or deploy based only on this option's existence. All D139 compiler
and board collection commands have ended; only read-only investigation remains.

D134 mode availability, D135 abort producer and D136 analyzer are closed for
software (d6a8319e/70c964a7/0faf2e6d). Their validation packets retain actual scope,
original failures and all evidence. D137 operator drafts2700da11 are updated for
D138's liveR/threshold pixel and remain NOT OPERATOR-READY. P6 stays deferred.
Do not re-run unchanged completed matrices or add generic frameworks.

## Physical and operational boundaries

Last actual MCU upload remains consumed D118defaultM0 sourcee820c0e1. Historical
4500Bfree/4364Blargest and513us are not current-image or full-source WCET proof.
No current MCU state is assumed. D138 only used Linux compile/file inspection.
Source grants and physical button windows remain default-off/unqualified.

P0-P5 acceptance packets enumerate actual PINMAP/electrical/sensor/button/motor,
measured stopping/combat/opener trials and human EXPLAINED/gates still needed.
D121 retains B7 full-reverse/R6 conflict. Native dump requires the specific
privileged holder evidence and reviewed quiescence/cancel/reopen plan in
analysis/P2_native_dump_prerequisite_followup.md. Never repeat ownership guesses
or bypass a denied action. SC-AP remains open for native matrix startup/ownership,
calibrated voltage/optics/failure display, full rearm and log preservation.
No additional hardware request now; no fresh STAND/RING authorization exists.

Storage: C:653561856Bfree at the latest check. Use owned /dev/shm, one heavy
compiler, small receipts and checked artifacts. D138 host scratch was released;
newboardrun233objects (7355110B) removed. Automaticapproval blocked local
build/stage/app cleanup (102files753087B), which remains. Earlier85.48MB/1.70MB
blocked batches also remain; no retry via another route. Storage growth outside
this small task remains unconfirmed; never alter paging or delete user data.

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
