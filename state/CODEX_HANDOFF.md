# Codex handoff - 25 September 2026, Asia/Dubai

**Active: P7 software/release preparation. D165 target compile failed; D166 host fix passes.**
The UNOQ compiler found CONFIG_PWM=1 colliding with the diagnostic enum. Original
source4ec345c0, one compiler exit1/reaped/no timeout, all122transports0 and seven
final checks PASS are preserved; no upload/reset occurred. The identifier-only
D166 correction now passes macro1/1, driver3/3, normal+ASan/UBSan each18cases/
2570assertions,47input pins and separate review. Read
analysis/P7_motor_fault_compile_actual.md and P7_motor_fault_macro_validation.md.

## Exact next task

Add fresh compile02 ownership/input selection per instance to the existing
P7_motor_fault_raw/compile_motor_fault.py, without cloning it or rebinding globals.
Keep consumed compile01/compile_inputs.json and all original receipts unchanged;
the old117-pin manifest must reject changed source. Use distinct native_compile02,
remote motor-fault-compile02 and input manifest. The completed local motor_fault
stage was hash-verified and removed, so a new stage can be created normally.
Test/review the narrow ownership selection and bind the corrected source before
one separately identified default/M0 compile. No automatic retry of D165.

D164's explicit command_runner is implemented/reviewed:146legacy+15new host
methods pass. Existing caller supplies explicit CLI/config/environment, --jobs1,
remote process-group720/60s deadlines+5s reap, source/tool checks and separate
final checks. Four real-child checks pass; retain their original fixture negative.
No inherited file-size cap constrains compiler artifacts. Per-process -B and fresh
-X pycache_prefix avoid old bytecode without deleting it or changing global config.
Compile01 caller/run evidence and pre-/post-action reviews are already retained.

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

C: observed1670385664B free at this checkpoint; recheck before large work. Old inactive
session-log lossless compression reclaimed1369392201reported allocated bytes;
previous CLI compression/IMU output removal/Git packing are in STORAGE_LOG.md.
D165 completed local stage removed:104files/764034logicalB; sources and original
target failure retained. No prior denied cleanup path was retried.
All D162/D163 RAM fixtures/build outputs were released; zero sumox directories
remain in /dev/shm. Keep compact source/freeze/failure/result evidence. Previously
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
