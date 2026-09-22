# P1: Core logic on the laptop

**Goal:** the complete decision layer (src/core) exists, compiles for the laptop and the MCU, and passes spec-derived tests before the robot is assembled.
**Needs:** GATE P0. No hardware.
**Load:** AGENTS.md, docs/BEHAVIOR.md (all), docs/HARDWARE.md section 8.

## Tasks
1.1 **Interfaces first.** Write src/core/types.h (Inputs, Outputs, State, Mode, Event per B0) and the header of every core module. Commit. These headers are the contract for test-author.
1.2 **In parallel:**
- test-author: tests for B3 and B4 (into tests/locked/), then B5 to B12 and B14, with the ScenarioRunner.
- Implementation, one general-purpose sub-agent per module or done yourself: countdown, edge, opp_fusion, governor, motion, stall, openers, fsm, logframe. Each module owns its files.
1.3 **Property tests** (test-author): R1 over 10,000 random input streams with a fixed seed; R5; L/R mirror symmetry for every opener and escape; no NaN or infinity in any output; duties always within [-1, 1].
1.4 **docs/ARCHITECTURE.md:** module map, data flow per tick, Mermaid state diagram matching fsm transitions, the MCU/Linux rationale (docs/PLAN.md section 7), and a 60-second explanation a student can say out loud.
1.5 **MCU compile:** `tools/flash.sh app --compile-only` builds src/core for arduino:zephyr:unoq so no laptop-only construct slips in.
1.6 **safety-auditor** on all of src/core; fix every finding.

## Exit gate (GATE P1)
- [ ] 60 or more tests pass, including every locked test; every table row in BEHAVIOR.md has a test
- [ ] src/core compiles for the board
- [ ] safety-auditor PASS; Codex review with no open BLOCKER
- [ ] A team member explains the state diagram back to you; human writes "EXPLAINED OK"
- [ ] Human writes `GATE P1 PASS`

## Do not
Touch src/hal. Tune numbers beyond the B16 defaults (the ring does that). Add behaviors that are not in BEHAVIOR.md: propose them in DECISIONS.md.
