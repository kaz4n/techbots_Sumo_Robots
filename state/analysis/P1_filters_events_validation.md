# P1 filters, stall, DIRECT and event retention — 2026-09-22

P1 host-only under D-016; P0 acceptance and every human gate remain pending.
Accepted new decisions D-029–D-032 are recorded verbatim in scope, alongside
earlier D-025/D-028. All 76 B16 defaults remain unchanged; no pins were assigned.
Added text-specified constants REFLANK_WINDOW_MS=10000 and LOG_EVENT_CAPACITY=4096.

Implementation commits:
- 6e12422: B11.3 limiter interface/config contract.
- 4acc9c1 and 7ef428f: DIRECT interface and implementation/independent tests.
- 29779da: actual four human approvals, visible B5/B11 amendments, headers first.
- b1a8266: approved EventBuffer interface/config capacity.
- 0838c64: Detector/ReflankLimiter with independent tests.
- a5fb36b: PhantomFilter/StuckFilter with independent tests.
- 36767f7: EventBuffer with independent tests.

Coordinator authored shared interfaces/config/state and stall/Direct implementation.
Worker owned only opp_fusion.cpp, then logframe.cpp; existing methods preserved.
Three separate spec-derived author contexts wrote only their new tests/reports,
never opening implementation .cpp files. No established locked test changed.

New coverage:35 filter cases,15 detector,12 limiter,26 DIRECT,13 buffer =101 cases.
Includes all byte masks,16,384 snapshot/current pairs, two10000 mirrored episode
sets,128000 limiter and64000 detector reference calls, exact/adjacent thresholds,
legal delayed/cumulative-wrap calls, finite extremes, all4096 retained events,
counter saturation and value/reset/bounds contracts. Buffer/frame-codec independence
is checked; actual continued recording and incomplete-dump marking are not implemented.

Validation commands and receipts:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1.
  P1_filters_events_build.txt.
- `wsl -d Ubuntu -- build/host/sumox26_tests`: exit0,
  **313 cases / 8,149,851 assertions**, zero failures/skips.
  P1_filters_events_tests.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, then
  `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: both exit0, same313 cases
  and8,149,851 assertions, no ASan/UBSan diagnostics. Receipts:
  P1_filters_events_sanitizer_build.txt and P1_filters_events_sanitizer.txt.
- Worker strict C++17 object/syntax checks with -Wall/-Wextra/-Wpedantic/-Werror,
  -Wconversion, no exceptions/RTTI: exit0 (reported by worker, corroborated by build).
- `git diff --check`: exit0. `git diff --name-only 7955c0a -- tests/locked`: empty.
- Source byte audit: no CRLF in any src/**/*.h or src/**/*.cpp.

Fresh separate Codex scoped review PASS (not cross-model/full P1 gate), with no
open BLOCKER/MAJOR/MINOR. Report: reviews/P1_filters_events_codex.md. Reviewer
also independently executed tools/test_host.sh successfully (exit0).
One MINOR test-coverage finding: four LCG draws per episode biased low-bit masks
to32 of128 configurations. Author switched to bits16–22 and added128 positive
coverage assertions; replay counted61–98 appearances per mask. Existing behavior
assertions were preserved. Initial green8,149,723-assertion receipts remain in
*_tests_initial.txt and *_sanitizer_initial.txt; corrected final runs are above.
No production failure or repeated unsuccessful repair occurred.

Exact21-file-per-sketch inert source/hash review approved the values recorded in
reviews/P1_filters_events_codex.md. Manifest refreshed only after that review.
`wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v`:48/48, exit0,
P1_filters_events_tools.txt. This is controlled script testing, not a board build.
No board contact, target compile, upload/reset, motor run, physical measurement,
PINMAP OK, EXPLAINED OK or human gate. All software outputs remain standalone:
complete fusion/FSM, other opener/escape/re-flank scripts, real MotorGate, target
WCET, frames/dump and physical checks still remain. Next eligible independent
script: B12 ARC_R/L contract/tests; protected escape/SIDESTEP/FSM choices are
listed in spec_conflicts.md and must be approved before dependent behavior.
