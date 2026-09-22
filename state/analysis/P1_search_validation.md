# B8 SEARCH — resumed 2026-09-22 Asia/Dubai

Status: HOST-TESTED with scoped review PASS and controlled script validation PASS.
Public contracts daddb87/421a766 precede source/tests. D-041/D-042 are accepted;
no new behavior permission needed for the documented bounded contract. Root owns
interfaces/config/state; worker fsm.cpp only; independent author test_search.cpp
and report only, never implementation sources. Reused separate read-only reviewer.

SearchSide implements selected nonzero relative-bearing side retention. SEARCH
captures a recent world-memory turn, then full directed scan, timed heading-held
advance and alternating scans. First-scan hint overrides the memory-turn direction;
otherwise its captured nonzero sign precedes last-side/default right. Hint is not
reapplied after each cycle. D-042 loss-time fallback is latched and independent of
the short-turn timeout. Inward history ages internally to zero and cannot revive
after clock wrap. Context ages must be truthful; no physical freshness is proved.

Existing 360-degree sweep and 5-second recent-edge interval are centralized in
config with source assertions/TUNING_LOG. All 76 B16 values remain unchanged.
Existing locked tests and existing fsm function bodies remain untouched.

Resumed tool observations: WSL g++13.3.0, CMake3.28.3, Python3.12.3; sanitizer
cache includes address,undefined and frame pointers (P1_search_environment.txt).
Pre-build reviewer found one MAJOR near-antipode precision issue, recorded in
P1_search_review_fix.md. This must be corrected/reviewed and regression-tested
before claiming completion. The owner corrected it and reviewer confirmed the
double-precision sign calculation before the first build. No failed test repair
or assertion change occurred. No target compile, board operation or gate implied.

Coordinator commands and actual results:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1, P1_search_build.txt.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`: exit0,
  P1_search_sanitizer_build.txt.
- `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0,
  P1_search_sanitizer.txt; **540 cases / 11,937,972 assertions**, no failure/skip
  or sanitizer diagnostics.

31 new independent cases cover B8 direction/history boundaries, all masks in
every active phase, full-sweep timing/loss/recovery, exact wraps, mirrors,
low-voltage governor composition and the precision regression. See the separate
spec/header-only author report. Whole-Robot integration, actual sensor freshness,
motor writes, physical scan behavior and robot WCET remain unproved.

Reused separate read-only reviewer independently ran normal script/binary and
confirmed the same totals, no open findings and exact23-file inert hashes.
See ../reviews/P1_search_codex.md. After the approved snapshot refresh,
`wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` passed48/48,
exit0 (P1_search_tools.txt). Controlled substitutes are script evidence only.
