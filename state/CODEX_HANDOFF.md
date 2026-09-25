# Codex handoff - 2026-09-25 Asia/Dubai

**D158 fresh ownership is host-tested and reviewed; run02 is not yet executed.**
All227 aggregate tests pass, scoped review bda4208e PASS. D159 removed only the
exact reproducible1MiB temporary loader fragment/empty parent; original D156
failure and consumed run01 remain intact. Next review and commit the concrete
run02 scope, then invoke the corrected M0 upload/conditional capture once.
Read analysis/P7_startup_run02_validation.md and P7_static_startup_run02_plan.md.

**Active phase: P7 software/release preparation.** D138 informational READY and
battery-threshold software is implemented, host-tested and target-compiled.
Its separate fresh-context review passes with no open findings; see
[validation](analysis/P7_readiness_validation.md), [review](reviews/P7_readiness_review.md)
and [checklist](CODEX_EXECUTION.md). Physical and human gates remain pending.
User requests continued work, bare UNOQ testing when useful, prompt commits and
storage conservation. Software-first scheduling never creates measured acceptance.

## Current checkpoint and exact next task

Current source is fcddbd8e; static final ELF5cc2dfde, debug ELF0f7f2825 and
packaged loader39d4a4fd remain unchanged. D148 structure/package and D149 selected
project ABI results remain valid for these files. Static RAM region tail94352B
is not live free memory. D139's dynamic default modeled592B deficit remains.
Production admission is still dynamic-only; no static deployment was adopted.

New work is consolidated in analysis/P7_static_native_dispatch_validation.md:
actual GPIO/PWM/RCC application call sites, selected cross-image types and native
vectors are bound to retained evidence. D150 GO9c995322 correctly ended FAILED
because the exported init name resolved ambiguously; its49 useful sections are
partial evidence only. Original failure and all receipts remain unchanged.
D151 GOa60ef466 then read exactly18 bytes by numeric address, with all5 read
commands and postchecks passing. It proves the conditional wrapper branch to
the retained helper, which calls device.ops.init at+20. Separate reused-context
actual collection review e35ee292 and fresh-context combined review e4eca064
PASS, with no open findings. Read state/reviews/P7_static_native_dispatch_review.md.
All read scopes D144-D151 that performed board work are terminal and consumed.

Three fresh Linux file-only receipts and CLI version confirm the upload tools
and absent include shadows: dependency commit4ba1c84e. The exact CLI input-file
must select raw build/app.ino.bin so the static recipe chooses its existing
flat sibling, not append the suffix twice. See analysis/P7_static_upload_route.md.
The completed pure plan/parser and37 frozen tests are under P7_static_startup_raw;
first sourcee7f88263, result/reference correction8fa01d1f. Current loader reference
is ELF-derived263680B/SHAe9322826, not packagedBIN6b2ffd (one-byte difference).

D153's native collector implementation and50 controlled tests are complete in
P7_static_startup_raw/capture_remote.py and linked validation. Original unexecuted
draftd5c8d6d6 is preserved; repaired first-executed source5f85268f stayed unchanged.
All fixtures were removed. CLI --config-file /dev/null with exact minimalenv
has now been observed to select the intended data/user directories (F162); raw
queries and original mistakenprojection are preserved. Existing board p0_capture.py
is hash885c4e42/18880B, file-verified; reuse it to fit the Windows command budget.

Exact next task: scoped run02 pre-action review and native scope creation. Current
launcher c9588835, uploader23661c8a, collectorab0bb320; review bda4208e. Distinct
native_run02 and remote run02 owners preserve all run01 evidence. D159 already
removed the known temporary fragment (exit0); normal uploader admission must
still freshly require its absence. No retry or new scope follows from cleanup.
Use --execute --run run02 --reviewed-head with the committed scope-containing HEAD.
Bind reviewed HEAD/source, D144 packet,
installed dependencies, explicit CLI configuration and selected core/recipe.
F165/F166 file-only receipts establish observed initialization prerequisites;
recheck them immediately before the later native scope.
The host validation alone is not a run grant. Do not rebuild or copy another
source tree. Separate upload/capture claims, bounded process deadlines, independent
postchecks and no recovery reset/retry remain required. Final capture bootstrap
has been sized: actual upload28068/capture24981units, below30000, reusing the
installed loader utility. Identify the concrete inert run/revision before upload.
The user permits bare UNOQ testing and requests no additional
hardware now. No motor-capable run is authorized; STAND/RING remains absent.
Native loading/startup, live stack/heap/WCET, full release workflow and all
physical/human gates remain pending. Do not infer them from file inspection.

Storage cleanup commits13d50c43 and495fb0be saved about49.9MiB: verified lossless
compression recovered8495104 allocated bytes; incremental Git packing reduced
reported loose+pack storage by43829248 bytes. All refs/reflogs were unchanged,
new pack verification and connectivity checks passed. No source/history/evidence
was deleted. The exact111-file P2 matrix host-output deletion was blocked by
automatic approval before process creation; add those paths to prior denied
cleanup targets and do not retry deletion. See STORAGE_LOG.md and compact
storage_compression_20260925_matrix_objects.json/storage_repack_20260925.json.
Recheck C: free space before material work; it fluctuates independently.
No compiler tree, binary copy or Python cache was added. Use Python-B.
Fresh03:08Dubai read-only cleanup check found zero new disposable repo or
task-owned Temp remnants. C: free513421312B at03:11; recheck before material work.
D153 fixtures left no temporary directories; retained code/oracles/compact
receipts remain necessary. C: free449900544B at03:27Dubai, system-dependent.

Historical detailed checkpoints and original failures remain in Git, PROGRESS
and linked validation packets. PROGRESS is append-only with legacy nonUTF8 bytes;
original140971B SHA2561dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77.

## Physical and operational boundaries

Last known successful MCU upload remains consumed D118defaultM0 sourcee820c0e1. Historical
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

Storage follow-up 2026-09-25T03:34:58.350778+04:00: idle local arduino-cli.exe compressed without
content/size/mtime change, saving20,187,648 allocated bytes. Eight newly
identified cache removals were blocked before process creation; zero deleted,
no retry. Exact new denied paths and source-preserving receipts are in
analysis/storage_cleanup_20260925_new_caches_blocked.json and STORAGE_LOG.md.
The P7 implementation resume task above is unchanged.

P7 file-only selection follow-up 2026-09-25T03:38:33.159664+04:00: F165 observes unique zephyr1.0.0
and remoteocd0.1.1, exact old boards/platform bytes, matching installed/indexed
tool dependencies and five absent overrides. See analysis/P7_static_cli_selection.md.
Do not describe board-details as unconditionally read-only: CLI initialization
can download/migrate. The query was not invoked. Original inventory size-bound
failure and metadata projection mistake remain beside corrected observations.
Next still: implement/test/review the host coordinator and one-shot upload wrapper,
using these explicit selection checks before a separately identified inert run.
No native grant was consumed/created and no MCU operation occurred.
