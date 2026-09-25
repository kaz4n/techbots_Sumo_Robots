# Codex handoff - 25 September 2026, Asia/Dubai

**Active: P7 software/release preparation. D162/D163 are HOST-TESTED and reviewed.**
The inert MotorGate callback diagnostic is implemented; 18 cases/2570 assertions
pass normally and under ASan/UBSan, the unsafe-flag driver passes, the unchanged
full host matrix passes22/22, and compile policies pass65/65. Separate same-model
reviews have no open material findings. Read analysis/P7_motor_fault_validation.md.
No target compilation or MCU action occurred in D162/D163.

## Exact next task

Prepare and execute one identified compile-only check of bench/motor_fault through
the existing checked project/recipe/artifact route. D163 added five literals to
board_tool.py/app_build_policy.py; historical consumed probes retain old bindings
and must reject the edited tools. Do not repin or reuse their consumed ownership.
Use an explicit installed CLI, minimal environment, empty config, fresh source-
bound paths, --jobs1, a board-side process-group deadline and bounded reap. An
outer transport timeout alone is insufficient. Existing capture_remote.wait_child
and stop_child can be reused without module-global mutation. Do not inherit the
capture1MiB or uploader2303728B file caps into a compiler. Keep the caller small.

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

C: observed1714384896B free at05:29Dubai; recheck before large work. Old inactive
session-log lossless compression reclaimed1369392201reported allocated bytes;
previous CLI compression/IMU output removal/Git packing are in STORAGE_LOG.md.
The latest independent repo/task-Temp audit found no new safe deletion candidates.
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
