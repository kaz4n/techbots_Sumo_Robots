# B14 supplied-tick statistics — 2026-09-22 Asia/Dubai

Status: HOST-TESTED with scoped review PASS. Public contract118f9cc
precedes source and independent tests. Worker owns logframe.cpp only; independent
spec/header-only author owns test_tick_statistics.cpp/report; root owns shared
header/config/state/build files. Reused separate read-only reviewer, not fresh
full P1 gate or cross-model review.

No clock, scheduler, match boundary, fault latch or motor response is introduced.
The caller supplies included tick durations. Counts use strict duration>TICK_US;
the rate is strictly above B14's existing1%. Exact quotient/remainder arithmetic
avoids a wide-count multiplication overflow. At count capacity, further count
updates are rejected and saturated latches; max_us still updates. Retained-count
ratios describe only that prefix. Caller must preserve incomplete status.

TICK_OVERRUN_PERCENT=1 centralizes existing B14 text, with exact source test and
TUNING_LOG entry. All76 B16 defaults remain unchanged. Existing encoders/event
buffer and established locked tests are untouched. Public valid-state fixtures
at representational limits test production arithmetic, not simulated measurements.

Strict worker C++17 syntax and diff checks reported exit0; coordinator inspected
the actual24-line source addition. Root validations/review are recorded below.

Coordinator commands/results:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1;
  P1_tick_statistics_build.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit0;
  P1_tick_statistics_sanitizer_build.txt.
- `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0;
  P1_tick_statistics_sanitizer.txt, **509 cases / 11,920,737 assertions**, zero
  failures/skips or ASan/UBSan diagnostics.

12 new focused independent cases cover strict duration/percentage boundaries,
exact ratios beyond floating-point integer precision, real production updates
from valid near-capacity fixtures, reset/max and actual packFrame clamping.
No failing production test or repair attempt occurred. Implementationdc9daa4.
Separate reused read-only review PASS/no findings; independent full host totals
agree. Exact reviewed23-file hashes and context scope are in
../reviews/P1_tick_statistics_codex.md. Full phase review/gates remain pending.

No target build, upload/reset, motor run or physical measurement. Next eligible
integration work is the production countdown lifecycle, per its saved audit;
full Robot/escape/SEARCH/re-flank/WAIT and remaining B14 integration are unfinished.

After the exact approved manifest refresh, controlled script validation
`wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` passed48/48,
exit0 (P1_tick_statistics_tools.txt). These tests use controlled substitutes and
host compilation; they do not establish a successful board build.
