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
