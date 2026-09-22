# P4: Hunt, push, defend, re-flank

**Goal:** the reactive core finds, tracks, pushes, defends, and breaks off stalled pushes, without ever leaving the ring on its own.
**Needs:** GATE P3; the test box (about 20 x 20 cm, matte black sides, 2.5 to 3 kg); RING OK per session.
**Load:** AGENTS.md, docs/BEHAVIOR.md B5, B6, B8 to B11, B14.

Enable SEARCH, TRACK, ATTACK, DEFEND_TURN, and STALL/REFLANK. Openers stay disabled: the robot enters SEARCH at GO.

## Tests
4.1 **Acquire and push:** 10 random box placements, including directly behind and at each side. Pass: 9/10 acquired within 3 s of GO; 8/10 box pushed out with the robot staying in. (M4, M5.)
4.2 **Lost target:** during ATTACK approach, a human pulls the box sideways out of the path with the string. Pass: 10/10 the robot brakes and stays in; the recorder shows the duty drop within OPP_CLEAR_MS + 5 ms. Tune ATTACK_APPROACH_DUTY here: highest value that still passes. (M6.)
4.3 **Defend:** box at 90 and 135 degrees on each side. Pass: the robot faces it within DEFEND_TIMEOUT_MS, 8/8.
4.4 **Push-through window:** raise EDGE_PUSH_THROUGH_MS from 0 in 20 ms steps only while 4.1 still passes with 0 self-exits. Keep the largest safe value; never above 100 ms.
4.5 **Stall and re-flank:** tie the box to a fixed point outside the ring so it cannot move. Pass: REFLANK starts within STALL_MS + 200 ms and the robot reaches the box side 8/10; never more than REFLANK_MAX_PER_10S attempts. Check the logs for false stall triggers during 4.1 pushes. (M8.)
4.6 **Spectators:** a person stands 30 cm outside the border, no box, 20 runs of 60 s. Pass: 0 exits; phantom events appear in the recorder. (M7.)
4.7 **Stuck sensor:** tape a white card 5 cm in front of one side sensor so it reads "detected" permanently. Pass: the fault is flagged, the bit ignored, and the robot still hunts with the others.

## Exit gate (GATE P4)
- [ ] 4.1 to 4.7 pass with log files named in TUNING_LOG.md
- [ ] safety-auditor PASS; Codex review with no open BLOCKER; human writes `GATE P4 PASS`
- [ ] Record the date: P6 is allowed only if this gate passed by 30 September
