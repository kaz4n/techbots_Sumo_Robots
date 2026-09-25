# Codex handoff - 25 September 2026, Asia/Dubai

**Active: P7 software/release preparation. D170 fresh staging HOST-TESTED.**
Source0160d1a6 adds stage(sketch, *, attempt=None): explicit fresh ownership,
checked ancestry and retained partial failures, with legacy behavior preserved.
Independent26 methods pass across WSL/Windows (platform skips recorded),91
unchanged tooling methods PASS; separate review8233de35 PASS. Original Windows
fixture failure retained and corrected without changing assertions/production.
All9 pins and the retained104-file stage's bytes/mtime are exact. Read
analysis/P7_fresh_stage_validation.md. No active process or native action remains.

D169 activation profile is also HOST-TESTED.
Source32b2d9d4 adds only a default-zero inert build selector, sketch grant selection
and exact project-specific policy admission. Independent13 methods,29 unchanged
tooling methods and normal/sanitized18 cases/2570 assertions each PASS. All63 pins
match; separate fresh-context revieweeb297fa PASS. Read
analysis/P7_fault_activation_validation.md. No new target build or board action.

The UNO Q compiled the default-disabled diagnostic successfully: one query/compile,
123 transports and ten checked children exit0, seven final checks PASS. Separate
actual review32e1c119 passes. Source5d3d126e, final ELF87fb03e5; packet1edf4a08.
Read analysis/P7_motor_fault_compile02_actual.md. No upload/reset/MCU read occurred.
D167 ownership passes12 independent host tests; original fixture negatives and
D165's target macro failure remain preserved. D166's correction now has actual
target compilation evidence in addition to its macro/normal/sanitizer host tests.

## Exact next task

Extend the existing state/analysis/P7_motor_fault_raw/compile_motor_fault.py with
one separately owned active diagnostic profile. Record a minimal closed mapping
contract first; preserve compile01/02 defaults, strict old inputs and assertions.
Use D170's explicit attempt token and per-instance local stage/input/output/remote
paths plus D169's exact active flags. Guard existing owner before board contact,
reuse unchanged identity/prerequisite/child-deadline/reap/final-check machinery,
and independently test routing/failure preservation. No ROOT/global rebinding,
copied wrapper, implicit legacy stage call or cleanup retry. After host validation
and review, bind fresh current inputs and an identified compile-only scope.

D170 API: stage(sketch, *, attempt=None), selecting
build/stage/<attempt>/<sketch-name> for a new portable1..48-character token.
Explicit mode never deletes an earlier attempt; absent/None retains old behavior.
Do not invoke default staging on retained build/stage/motor_fault. The source copy
body is shared, including app support beneath src/app for both bench and app.

D169 activation is ready: SUMOX_MOTOR_FAULT_PROBE defaults0; the exact active
checked flag tuple is -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1.
Native limits and Trace refusal of EN-high/nonzero PWM are unchanged. Existing
compile01/02 manifests must reject this changed source; no source repinning in
consumed attempts. A fresh compile needs new ownership and the explicit safe stage.

An eventual active image needs fresh source/artifact binding and a separately
identified inert upload/capture. Existing upload_remote.py provides bounded child
primitives but its public profile is static-app-specific; runtime_capture.py has
dynamic relocation references. Neither currently admits this diagnostic. Reuse
primitives with a minimal explicit profile and ELF-derived finite capture layout;
do not claim the old static capture plan fits a new dynamic image.

Both compile01/02 are consumed. Keep their inputs and receipts unchanged. The
new104-file local build/stage/motor_fault remains present: its verified cleanup
was rejected by automatic review. Do not retry deleting it through another method
or let a staging helper implicitly remove it. Host preparation remains eligible;
future target staging must explicitly account for this retained directory.

D164's explicit command_runner is implemented/reviewed:146legacy+15new host
methods pass. Existing caller supplies explicit CLI/config/environment, --jobs1,
remote process-group720/60s deadlines+5s reap, source/tool checks and separate
final checks. Four real-child checks pass; retain their original fixture negative.
No inherited file-size cap constrains compiler artifacts. Per-process -B and fresh
-X pycache_prefix avoid old bytecode without deleting it or changing global config.
Compile01/02 caller/run evidence and pre-/post-action reviews are retained.

The diagnostic defaults to false setup permission and rejects MATCH or motors.
It wraps unchanged native callbacks, submits four synthetic disabled/zero commands
through the real Gate and retains the first false through cleanup. Timing overhead
may change the fault; unchanged native setup may still block. A later diagnostic
upload/run requires its own identified inert scope and source/artifact review.
No motor-capable run is authorized; STAND/RING remains absent.

## Last actual board state and evidence

D160 is the last successful upload: sourcefcddbd8e/static/default/M0, run02, target
ADB2629958581, observed boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6. All14 transport
calls and final checks passed;18 passive reads matched complete loader/sketch
flash. Both runtime observations were STOPPED at epoch3. D160 is consumed.
Read analysis/P7_static_startup_run02_actual_validation.md.

D161 then read exactly752B once, with independent collection/interpretation review
PASS. Robot0x0110 = APPLICATION_CONTRACT|LINE_CONTRACT; GateIO3; prior/current
applications invalid. Production state does not retain the original failed native
callback or latency. Cleanup overwrites working masks, so do not infer a timeout
from their later values. Empty SetupGrants independently prevent initialization.
D161 is consumed; no extra reset/read/retry follows. Read
analysis/P7_stopped_diagnostic_validation.md. D162 is the bounded diagnostic next
step, not a production safety-limit change or proof of D160's original cause.

Static final ELF5cc2dfde/debug0f7f2825/loader39d4a4fd remain retained. D148 package,
D149 ABI and selected D150/D151 native dispatch evidence remain valid for those
files. The original D150 name-resolution failure remains recorded. Static region
tail94352B is not live free RAM; dynamic-default modeled592B deficit remains.
Static production adoption, actual startup, live stack/heap/WCET and release
workflow remain unqualified. D160 sampled790us maximum is not an R4 WCET result.

## Phase and human boundaries

D015 migrates implementation to Codex; separate reviewer remains review-only.
D051/D075/D122/D137 authorize software-first scheduling, not invented measurements
or human gates. PROGRESS.md is authoritative and append-only. P0-P5 physical and
human acceptance remain pending; P6 is conditional; P7 is incomplete. Preserve
R1-R11, config defaults/approved decisions, locked tests and no remote motion.
No additional hardware is requested now; the user permits bare UNOQ inert testing.
The original B7/R6 conflict, native dump lifecycle, release workflow and physical
sensor/motor/electrical acceptance remain tracked in existing packets/findings.

## Storage and tools

C: observed1523920896B free near this checkpoint; recheck before large work. Old inactive
session-log lossless compression reclaimed1369392201reported allocated bytes;
previous CLI compression/IMU output removal/Git packing are in STORAGE_LOG.md.
D165 completed local stage was removed:104files/764034logicalB. D168's new stage
contains104files/764049logicalB and is retained after automatic cleanup rejection
(blocked by policy, no further reason). Receipt: analysis/storage_cleanup_20260925_motor_fault_stage02.json.
Zero bytes reclaimed by this attempt; never retry it through another method.
The new raw packet is882618B plus compact metadata; no firmware binary downloaded.
All D170 serial compiler/fixture outputs were released; zero Windows/RAM task
remnants observed. Retain compact test/failure/review evidence and244837B of unique
legacy command receipts. Independent storage audit found no new disposable files.
Incremental Git packing recovered11196416reportedB with HEAD/refs/reflogs unchanged,
new pack verified and connectivity PASS. Receipt storage_repack_20260925_d170.json.
No native packet, firmware copy, dependency download or denied cleanup retry.
Keep compact source/freeze/failure/result evidence. Previously
policy-denied deletions remain excluded; never retry through another method.
Use Python-B, serial heavy builds, no duplicate firmware/source trees. Archive
results before releasing /dev/shm; WSL shutdown can erase it between invocations.

Observed current host tools: WSL Ubuntu g++13.3.0, CMake3.28.3, Python3.12.3.
Intended target path is board-side SSH, with verified ADB fallback. Installed
zephyr1.0.0/remoteocd0.1.1 and exact CLI/config/prerequisite provenance are in F160-
F166 and retained receipts; verify current identity before another native scope.
Credentials remain outside tracked files. Use git -c core.longpaths=true.

## Resume and schedule

Read AGENTS.md fully, docs/prompts/CODEX_RESUME.md, this handoff, CODEX_EXECUTION,
PROGRESS, DECISIONS, FACTS, open findings and active P7/relevant hardware sources.
The takeover already loaded all role definitions, PLAN/HARDWARE/BEHAVIOR and P0-P7
prompts; reload task-relevant sources rather than relying on conversation memory.
Check nested instructions, status, source/review changes and actual Dubai time.
Original140971B PROGRESS prefix SHA256:
1dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77.
Append without re-encoding legacy bytes. Historical checkpoints remain in Git.

Actual P3 not passed by end28Sep requires reactive+SIDESTEP/DIRECT and recorder,
dropping ARC/WAIT/P6 polish. P6 also requires actual P4 by30Sep. Freeze1Oct21:00,
rehearsal2Oct, competition3Oct. Dates create no gate or evidence. Commit each
finished bounded task promptly; do not space commits artificially or push.
