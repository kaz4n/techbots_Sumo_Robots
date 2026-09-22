# P5: Opening routines

**Goal:** the openers in docs/BEHAVIOR.md B12 work reliably, in priority order, in both mirrored directions.
**Needs:** GATE P4; RING OK per session.
**Load:** AGENTS.md, docs/BEHAVIOR.md B7, B12, B13; docs/PLAN.md section 6.

Priority order (each must pass before the next starts; stop where time runs out):
1. SIDESTEP_R and SIDESTEP_L (default)
2. DIRECT
3. ARC_R and ARC_L
4. WAIT (matador)

Setup for every run: robot behind its start line facing the center; box behind the opposite start line, where the opponent would be. If the organizers allow any orientation, add a pre-angled SIDESTEP variant through a DECISIONS.md entry first.

## Tests per opener
5.1 **Static box:** 10 runs. Pass: 9/10 end in ATTACK on the box; 0 self-exits.
5.2 **Charger proxy** (SIDESTEP and WAIT only): at GO, a human pulls the box hard toward our start line with the string. Film at 60 fps. Pass: 8/10 without a frontal hit on us, and the robot reaches the box side. (M9.)
5.3 **Abort check:** box placed in the opener's path. Pass: 10/10 the opener hands over to ATTACK or DEFEND_TURN within 1 tick of the abort condition.
5.4 **Mirror check:** L and R versions produce mirrored heading traces in the recorder, within 10 degrees.
5.5 **Mode UI:** the operator selects any mode in under 5 s, and the matrix confirmation is readable at arm's length.

After each block of runs, log-analyst proposes parameter changes; record every change in TUNING_LOG.md.

## Exit gate (GATE P5)
- [ ] Openers 1 and 2 pass (mandatory); 3 and 4 pass or are removed from the mode list
- [ ] Codex review with no open BLOCKER; human writes `GATE P5 PASS`

**Code freeze:** Thursday 1 October, 21:00. Tag v1.0. After the freeze only config.h values change, each with a TUNING_LOG entry.
