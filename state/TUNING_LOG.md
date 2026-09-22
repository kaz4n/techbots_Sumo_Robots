# TUNING_LOG (append only)

Every bench or ring measurement and every config.h change goes here with its evidence.

## Entry format
### <date> <time> | <phase> <test id> | battery <V>
- Setup: surface, box weight, mode, firmware commit
- Runs: N, results (numbers, pass/fail per run)
- Log files: logs/...
- Change: CONSTANT old -> new (reason, evidence) or "none"
- Metric status: M# pass/fail

## Metrics board (update as results arrive)
| Metric | Target | Result | Date | Evidence |
|---|---|---|---|---|
| M1 early starts | 0 in 50 | | | |
| M2 self-exits solo | 0 in 20 | | | |
| M3 edge escapes | 24/24 | | | |
| M4 acquire | 9/10 | | | |
| M5 push-out | 8/10 | | | |
| M6 lost target | 10/10 | | | |
| M7 spectators | 0 in 20 | | | |
| M8 re-flank | 8/10 | | | |
| M9 sidestep vs charger | 8/10 | | | |
| M10 tick worst case | < 800 us | | | |
| M11 brownout resets | 0 in 20 | | | |
| M12 weight | 2,950 g +/- 20 | | | |
| M13 footprint | 199 x 199 mm | | | |

### 2026-09-22 | P0 0.3 software configuration initialization
- Setup: host only; no board, battery, bench or ring measurement.
- Change: created src/config.h with all 77 B16 constants unchanged. No pin values assigned.
- Added diagnostic-only defaults: P0_SCROLL_MS=100, P0_COUNTER_MS=1000,
  P0_JITTER_SAMPLES=60000, P0_JITTER_HISTOGRAM_US=1000. These parameterize P0
  display/capture scaffolds and do not alter robot behavior or safety timing.
- Evidence: comparison script reported all 77 B16 values exactly equal; C++17
  host build/CTest passed (analysis/P0_host_tests.txt). P0 smoke test only.
- Metric status: M1-M13 unmeasured; no tuning or physical performance claimed.
