# Codex handoff - 2026-09-25 Asia/Dubai

**D148 existing native packet: structural/package PASS.** Five read-only board
commands succeeded; no compile/upload/reset. See the current checkpoint below.
Production admission, runtime acceptance and physical/human gates remain separate.

**Active phase: P7 software/release preparation.** D138 informational READY and
battery-threshold software is implemented, host-tested and target-compiled.
Its separate fresh-context review passes with no open findings; see
[validation](analysis/P7_readiness_validation.md), [review](reviews/P7_readiness_review.md)
and [checklist](CODEX_EXECUTION.md). Physical and human gates remain pending.
User requests continued work, bare UNOQ testing when useful, prompt commits and
storage conservation. Software-first scheduling never creates measured acceptance.

## Current checkpoint and exact next task

D148 actual existing-packet validation PASSES under the new D147 interface:
GOdbb5f1a4, hostfbde2926, remotec6099f6d, validatorcd52a29a; five read-only
commands exit0, query/compile0, all source/installed/artifact postchecks pass.
Read analysis/P7_static_native_actual_validation.md and its linked receipts/review.
The exact current source remainsfcddbd8e;103 sources/102 staged files,17 local pins
and26 installed pins remain bound. No firmware, old test or production change.
FinalELF5cc2dfde, debug/temp0f7f2825, flat package5f08afe0 are original D144 bytes.
Flash payload93080B; static RAM span167792B, region tail94352B. The tail is NOT
measured live RAM/stack/heap or runtime qualification. No upload/reset occurred.

All native operations D144/D145/D146/D148/D149 are terminal and consumed. D144's old
unsupported-symbol rejection remains intact. D147's separately tested exact-six
TLS metadata extension passes19new+51old host methods, with independent review.
D141/D142/D143 contracts, original parsers/tests/consumers and production dynamic
admission remain unchanged. D139's dynamic default profile still has592B modeled
deficit; the native structural pass is a distinct experimental result.

Local entry/constructor audit is complete (original6ecb8ab6):34 local commands,
32 focused functions; separate review14e6d959 PASS. Read analysis/P7_static_entry_audit.md.
One literal-elision description was corrected; raw receipt92b72069 is unchanged.
Three native printk calls before initialization remain an untested startup dependency.
D149's file-only GDB comparison also passes: GO2cd8d795, source7c7fa476,
16 type size/alignment pairs and82 offsets match; five read commands0/noerrors.
Separate actualreview3f4d20b7 PASS. Read analysis/P7_static_native_abi_validation.md.
No compiler, target/inferior or upload/reset. D149 is terminal and consumed.
Bounded native address audit also passes scoped reviewf738ef54:168 ABS values,
22 veneers and62 catalogued native addresses match retained packaged evidence;
119 table entries are118 matching device pointers plus one null. Receiptc3233593
is74101B. Read analysis/P7_static_native_bindings_audit.md and its separate review.
This does not establish complete indirect driver/API dispatch coverage.
Exact next task: analysis/P7_static_native_dispatch_next.md. Reuse retained
GPIO/PWM/RCC/device-init observations to compare actual app call-site offsets;
only missing offsets/prototypes justify a separately scoped file-only loader
query. Prioritize MotorGate EN and zero-duty PWM init before any inert startup.
No static upload path or run is authorized merely by these successful file audits.
Native startup, stack/heap/WCET, physical acceptance and human gates stay pending.
Do not integrate a static upload path or run an MCU merely because structure passes.

D148 retained seven compact input/command/result files125141B plus small launcher;
no binaries/fixtures/build trees downloaded or created. Latest bounded storage
inspection found no new safe disposable files; see STORAGE_LOG.md/f2fa3c28.
All prior denied cleanup targets remain untouched; do not retry by another method.
C: free about511MB at02:29Dubai; global fluctuations are not cleanup recovery.
Use Python-B and small reports; keep one compiler maximum if later justified.

Historical detailed checkpoints and original failures remain in Git, PROGRESS
and linked validation packets. PROGRESS is append-only with legacy nonUTF8 bytes;
original140971B SHA2561dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77.

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

Storage cleanup recovered 353,796,096 allocated bytes (337.4 MiB) by transparent
LZX compression of 129 historical JSON/TXT evidence files; all before/after hashes
match. No file was deleted. Receipts are in analysis/storage_compression_20260924_*
and STORAGE_LOG.md. C: had approximately 900 MB free after that earlier batch (later850MB); recheck
before large work because system activity changes it. Keep compact evidence and
one heavy compiler; do not change paging or persistent virtual disks.

Automatic approval review blocked deletion of 154 unused Arduino download
archives (4,571,947,977 bytes), with only "blocked by policy" stated. No deletion
or retry occurred. Earlier denied stage/host/snapshot cleanups also remain intact.

The 25September 00:23Dubai follow-up removed four unrelated closed application
crash dumps and one regenerable Python cache (20,176,376 logical bytes total).
It also recovered 50,286,592 allocated bytes by transparently compressing 61
historical ELF evidence files, with all hashes/sizes/mtimes unchanged. Exact
receipts and the independent check are in analysis/storage_*20260925*; see
STORAGE_LOG.md. Both WSL crash dumps and every previously denied cleanup target
remain. C: was about942MB free then; the current checkpoint above supersedes it.

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
