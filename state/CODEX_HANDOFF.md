# Codex handoff - 25 September 2026, Asia/Dubai

**Active: P7 software/release preparation. D174 offline decoder HOST-TESTED.**
Source68653597/f6e2fd36; independent tests b2995dea frozen7712ae0b,22/22 PASS on
first execution,0.825s; seven frozen inputs unchanged. Separate fresh-context
same-model reviewefe5a39ePASS. Read analysis/P7_motor_fault_decode_validation.md.
All64calls/fourresults,208enum/367boolean/eightfloat locations and partial/failure
states are covered. decode_snapshot returns structural DECODED and explicitly
UNPROVEN coherence; it never authorizes hardware or claims a gate.

D173 file-only observation succeeded: execution089de986/evidence cc9f50c6;
one transport/five children exit0/reaped,26remote+120local checksPASS. Actual
review60fdc78ePASS. Exact ARM layout is analysis/P7_motor_fault_raw/active_abi.json,
SHA822c917d: final ELFf9460a16, debug7a4b2953, Runner2592B/alignment8, BSSsection7
size2632/symboloffset0, trace report44/main report2312. Loader39d4a4fd confirms
list0x200017bc and196B nodes with BSSbase32/size92,index3. Full ten-type offsets
and dynamic recipe are recorded. Read analysis/P7_motor_fault_abi_validation.md.
No MCU memory was read. The reader's original findings/draft remain preserved;
all were repaired/reviewed before the single successful file-only execution.

D172 compiled the active inert diagnostic: execution6bf5ecb1/evidence db1228ce,
source8f592937/ELFf9460a16/exportb4416792,123transports/tenchildren0,7finalchecksPASS.
Exact flags MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1, default wait startup,
dynamic linking. Build/export ELF-ZSK hashes match. No upload/reset occurred.
D160 remains the last actual upload; diagnostic execution and fault cause unknown.
No process is running. Previous source/failure/recipe/review evidence is retained.

## Exact next task

Add the smallest closed exact-artifact inert diagnostic profile to the existing
bounded upload/capture primitives. Start from analysis/P7_motor_fault_capture_dependencies.md,
D173 active_abi.json, tools/motor_fault_decode.py, and existing static startup
upload_remote.py/capture_remote.py plus runtime_capture.py's dynamic LLEXT traversal.
Do not invoke those old consumed profiles unchanged or clone another launcher.

Use the actual dynamic motor_fault.ino.elf-zsk.bin recipe, exact source8f592937/
ELFf9460a16/exportb4416792 and loader identity. Preserve upload's2303728B loader-copy
allowance, explicit environment, fresh exclusive ownership, child deadlines/reap,
raw failed output and independent final checks. Derive finite read/byte totals
from the observed2632B BSS and2592B Runner; bounded <=3-node LLEXT traversal and
exact flash/relocation bracketing precede two whole-Runner snapshots. No heap dump
needed. Retain both raw snapshots even if decoding fails; matching samples do not
prove atomicity. The offline decoder must not become a safety/acceptance predicate.

Record a compact contract, independently derive/freeze profile/decoder integration
tests, implement and review the exact changed boundaries, then identify one new
inert upload/capture scope under the existing bare-board permission. No motor-capable
run is authorized. D172/D173 and compile01/02/active01 remain consumed; never repin
or automatically retry them. Hardware identity must be rechecked for a later run.

Both build/stage/motor_fault and build/stage/motor-fault-active01 remain after
policy-blocked cleanup. Never retry their removal or invoke implicit staging
against them. Explicit absent ownership is the tested safe staging route.
Firmware limits, pins, locked assertions, and human/physical gates are unchanged.

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

C: observed1296179200B free at this checkpoint; recheck before large work.
D173 retained219185B file-only ABI packet and D174 compact sources/test results;
no firmware/debug download or persistent test scratch. No new cleanup attempted.
D172 raw packet890157B plus compact metadata/review is retained; no firmware binary
was downloaded. Its verified104-file/764719B staging removal was rejected before
execution (blocked by policy, no further reason), leaving0B reclaimed. D168's
104-file/764049B legacy stage also remains. Both are excluded from future deletion
attempts, including implicit staging. Receipts are storage_cleanup_20260925_motor_fault_active01.json
and storage_cleanup_20260925_motor_fault_stage02.json under analysis/.
Incremental D172 Git packing reclaimed720896reportedB (704KiB), with new pack and
connectivity verified and HEAD/refs/reflogs identical. This is additional to D170's
11196416reportedB and earlier old-session compression1369392201allocatedB.
See STORAGE_LOG.md; never recount prior savings or attribute system fluctuations.
All earlier policy-denied targets stay untouched. No new disposable candidate was
identified outside this completed task. Preserve unique evidence/source/history,
use Python-B and serial heavy builds, avoid duplicate source/firmware snapshots.

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
