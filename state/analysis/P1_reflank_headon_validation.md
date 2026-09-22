# Re-flank, head-on and countdown lifecycle — 2026-09-22 Asia/Dubai

Status: HOST-TESTED with scoped separate review PASS; controlled script checks
pending after the approved manifest refresh. Baseline fc5a9f5 SEARCH passed540
cases/11,937,972 assertions and48 controlled scripts.

Public contracts precede source/tests: re-flank a37c9c8, additive explicit-side
head-on8a6cc48, countdown lifecycle2e629c1 and relative turn18414c0. Root owns
headers/config/docs/state and edge.cpp; worker fsm.cpp/countdown.cpp/motion.cpp;
independent spec/header-only author the four new suites and reports. Reviewer
p1_next_task_audit is a reused separate read-only context, not newly fresh,
cross-model or a full gate review. Established locked tests remain unchanged.

B11 chooses explicit truthful history and executes BACK, SWING pivot/arc and
captured TURN_IN under D-037/038/040/043. Entry notifications preserve exact-tick
order. D-044 adds startHeadOn without changing start(mask)'s established mask
set. Lifecycle composes Controller-first service start/cancel/GO and explicit
diagnostics; service completion alone never grants permission. Existing config
values, HAL and bench sketches are unchanged.

69 independent new cases:29 re-flank,14 NEW locked head-on,17 NEW locked
Lifecycle and9 relative-turn cases. Two static issues were corrected before the
first build, without weakening assertions: float coordinate narrowing at strict
tolerance, and healthy nonfinite yaw bypassing validation in latched fallback.
See P1_reflank_precision_review.md. Turn.startRelative retains double coordinate
error inside the primitive; original timeout precedence remains in force.

Owners reported strict standalone WSL C++17 syntax exit0 for all changed cpp
files. Root personally ran edge.cpp with -fno-exceptions -fno-rtti -Wall -Wextra
-Werror -pedantic -Isrc -fsyntax-only; exit0. Full actual validation:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1;
  P1_reflank_headon_build.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit0;
  P1_reflank_headon_sanitizer_build.txt.
- `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0;
  P1_reflank_headon_sanitizer.txt; **609 cases / 11,983,801 assertions**, no
  failures/skips or ASan/UBSan diagnostics. No failed runtime repair attempt.

Separate reviewer independently ran script and full binary with identical totals,
inspected sanitizer evidence and reported no open BLOCKER/MAJOR/MINOR findings.
Both23-file source maps reproduce the accepted fc5a9f5 baseline; only eight
reviewed headers/cpp files differ. Exact approved hashes are in the review record.

Disk incident after completed validation: C: reported0 free during an evidence
write, truncating this untracked summary to zero bytes. Raw receipts, sources,
tests and tracked precision analysis remained intact. A broad generated-object
cleanup was automatically rejected; the safer exact-file cleanup succeeded after
verifying its untracked, non-symlink path inside this project's sanitizer build.
Only build/host-sanitize/CMakeFiles/sumox26_tests.dir/mnt/c/Users/narut/OneDrive/
Desktop/Project/techbots_Sumo_Robots/tests/test_scaffold.cpp.o (6,462,704 bytes)
was removed. Binary/CMake cache retained. C: subsequently reported558,149,632
bytes free; the larger increase is not attributed solely to that deletion.
This summary was reconstructed from the retained receipts and review messages.

D-047/D-048 approvals are recorded1dfaa7d; their full policy integration follows
this batch. No board contact, target build, upload/reset, motor run, physical
measurement, publication or human gate. Full Robot, physical freshness, real
MotorGate writes and measured WCET remain pending. New31 locked cases become
established with this validated batch; no prior locked case changed.
