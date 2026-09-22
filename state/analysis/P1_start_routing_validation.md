# D-057 START routing validation — 2026-09-23 Asia/Dubai

Public contract322ecce preceded implementation and independent tests. Source
countdown.cpp frozen SHA256a40851b63ec71b9da8075d7bdecabf42208f97218ef134740c26808b0caa1e6c.
Root owns shared header/source/ledgers; independent author reads specification
and public headers only and owns new locked tests. Separate reused read-only
review is ../reviews/P1_start_routing_codex.md, not a full gate review.

The implementation stores the current Buttons result once, filters only START
before Gate, forwards that selector through Lifecycle and returns a const event
snapshot. Default calls preserve existing semantics. A false selector is neither
STOP nor cancellation; pending real Services/GO continue. Suppressed idle release
cannot start Services or consume previous-bias input, and is never queued.

Strict C++17 syntax-only compilation passed exit0 with Werror/noexceptions/nortti;
diff-check passed. No established locked test/config value changed.

## Actual validation

| Command | Result | Raw receipt |
|---|---|---|
| `wsl -d Ubuntu -- bash tools/test_host.sh` | Build/CTest exit0;1/1 executable passes | P1_start_routing_host_20260923.txt |
| `wsl -d Ubuntu -- build/host/sumox26_tests` |740 cases/12,122,401 assertions pass;0 fail/skip;exit0 | Same host receipt |
| `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, then sanitizer binary |740 cases/12,122,401 assertions pass;0 fail/skip;both exit0 | P1_start_routing_sanitize_20260923.txt |
| `wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -v` |116 checks pass in38.984s;exit0 | P1_start_routing_tooling_20260923.txt |

24 independent new locked cases cover D-057; full suite includes all716 earlier
cases unchanged. Sanitizer cache retains address/undefined and frame-pointer
flags. There were no compiler/runtime failures, test amendments or implementation
repair attempts. The source/header/test review has no static finding; final
independent rerun and scoped verdict are recorded in the linked review.
Final scoped verdict: PASS, no open BLOCKER/MAJOR/MINOR. The separate reviewer
ran the released host binary and reproduced740 cases/12,122,401 assertions,
exit0; raw receipt P1_start_routing_reviewer_host_20260923.txt. Complete proposed
maps, approved manifest and frozen source/test hashes matched after validation.

All23 files in each proposed inert snapshot were independently compared to current
source and a94cc4d: only countdown.h/.cpp changed. Explicit source-only approval
preceded the manifest refresh. P1_start_routing_inert_proposed.json records exact
maps. No new board command occurs for this routing-only change. Earlier target
compile at a94cc4d/98c436a4 does not cover these later sources; target validation
of the complete app remains pending. Last uploaded inert matrix stays unchanged.

Implementation commit:4d323bc. Next eligible task is the actual B13 logical menu
policy/interface/test/implementation from the saved audit; D-057 is its completed
routing prerequisite. Complete Robot/event contracts then follow. No human phase
gate, hardware measurement, full R1/R5 actuator proof or remote publication.
