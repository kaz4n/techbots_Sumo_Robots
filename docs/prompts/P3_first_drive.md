# P3: First drive: legal start, edge survival, speed limits

**Goal:** the robot starts legally every time and cannot drive itself out of the ring.
**Needs:** GATE P2 and a ring (black, 3 cm white border, 1.5 m). Every session needs RING OK.
**Load:** AGENTS.md, docs/BEHAVIOR.md B2 to B8, docs/HARDWARE.md section 8.

Firmware for this phase: mode DRIVE_TEST (openers and ATTACK disabled). SEARCH_DUTY_MAX starts at 0.30.

## Tests
3.1 **Countdown proof:** 50 starts. From the recorder: FIRST_NONZERO_DUTY minus START_RELEASE. Pass: every start at or above COUNTDOWN_MS + COUNTDOWN_MARGIN_MS, spread under 5 ms. (Metric M1.)
3.2 **R_room:** push the robot slowly over the edge by hand, 3 times at the front and 3 at each rear corner. Record the distance from the first white reading to the point where it would lose. (HARDWARE.md section 8.)
3.3 **Stopping table:** drive straight at the edge at duties 0.30, 0.40, 0.50, 0.60, 0.70, three runs each. The human measures from the white border's inner edge to the robot front at rest. Record duty, battery voltage, distance. log-analyst proposes SEARCH_DUTY_MAX as the highest duty whose worst stop stays under 70 % of R_room; the human approves.
3.4 **Turn accuracy:** turnTo 90 and 180 degrees in both directions, 5 each. Pass: error within 5 degrees. Also measure TURN_MS_PER_DEG for the IMU-fault fallback.
3.5 **Edge escapes:** approach the edge at 0, 30, 60, and 90 degrees on each side (8 angles), forward, 3 runs each at SEARCH_DUTY_MAX. Pass: 24/24 stay in. (Metric M3.)
3.6 **Brown lines:** cross the start lines 10 times. Pass: 0 false edge events.
3.7 **Solo reliability:** 20 runs of 60 s in SEARCH. Pass: 0 exits, 0 resets, and the pattern looks deliberate. (Metric M2.)

## Exit gate (GATE P3)
- [ ] 3.1 to 3.7 pass, all numbers in TUNING_LOG.md
- [ ] config.h changed only from evidence (log-analyst tables)
- [ ] Codex review with no open BLOCKER; human writes `GATE P3 PASS`

**Date rule:** not passed by the end of Monday 28 September? Apply the scope cut in AGENTS.md section 8 and say so in PROGRESS.md.
