# P6: Judge pack (conditional)

**Runs only if GATE P4 passed by Wednesday 30 September.** Match performance still wins every conflict: drop P6 work the moment the team needs help on the ring.
**Load:** AGENTS.md, docs/PLAN.md sections 7 and 10, docs/ARCHITECTURE.md, state/TUNING_LOG.md.

## Tasks
6.1 **tools/plot_match.py:** one PNG per log with state timeline, opponent-sensor raster, edge events, heading, duty L and R, battery. Generate plots for three real runs: a push-out, a re-flank, an edge escape.
6.2 **Start evidence:** histogram of GO delay after START release over every logged start.
6.3 **docs/JUDGE_PACK.md** (two pages at most): the MCU/Linux decision with its numbers; the state diagram; the sensor-fusion table; test counts (host tests, bench tests, ring tests with pass rates); the three plots; what we would do next.
6.4 **Five-minute demo script:** SENSOR_VIEW mode; the 5-second hold with gyro calibration on the matrix; an edge escape on the ring; a stalled push against the tied box triggering a re-flank; a log dump and its plot.
6.5 **Rehearsal:** each team member explains one section in under 60 s. Human confirms.

## Exit gate (GATE P6)
- [ ] JUDGE_PACK.md reviewed by the team; every plot comes from a real run
- [ ] Human writes `GATE P6 PASS`
