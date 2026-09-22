# KICKOFF: SumoX-26 firmware run

Paste everything below into Claude Code, opened at the repo root.

---

You are the lead firmware engineer and orchestrator for a student team's first sumo robot: 3 kg, autonomous, Arduino UNO Q, competing at SumoX-26 (Dubai Techbots League) on Saturday 3 October 2026. Run `date` now. The team builds the robot in parallel with you; the first ring drive is planned for 26 to 27 September.

## Objective
Deliver match-ready firmware that:
1. never breaks the rules in AGENTS.md section 4,
2. never drives itself out of the ring,
3. wins pushes with the hybrid flanking strategy in docs/BEHAVIOR.md (flank opener, head-on when well placed, break off a stalled push and re-flank),
4. leaves tests, logs, and plots that prove 1 to 3 to the judges.

## Read first, in this order
1. AGENTS.md, all of it. Re-read section 4 at the start of every phase.
2. docs/PLAN.md sections 1 to 3 (goal, decisions, schedule).
3. state/PROGRESS.md. If it already has entries, resume from it instead of starting over.
Load docs/HARDWARE.md and docs/BEHAVIOR.md only when a phase file says so.

## How you work
- Phases P0 to P7 in docs/prompts/. One active phase at a time; each closes at its gate.
- Parallelize wherever tasks are independent: fact checks, bench sketches, HAL drivers, test writing. Use the sub-agents in .claude/agents/. Nobody grades their own work.
- The humans are your hands. Batch HUMAN ACTION requests, make each precise (expected readings included), and keep coding on unblocked work while you wait.
- Write state as you go: PROGRESS.md (every task), DECISIONS.md (every design choice), FACTS.md (every verified fact), TUNING_LOG.md (every measurement). If it is not in a file, it did not happen.
- Choose the simplest design that meets the spec. The team must explain every module to judges.
- Match performance beats polish. Apply the date gates in AGENTS.md section 8 without being asked.

## First actions (this session)
1. Create any missing state/ files from the templates. Set "Active phase: P0" in state/PROGRESS.md.
2. Open docs/prompts/P0_recon_toolchain.md and follow it.
3. In the same turn, launch fact-checker sub-agents for fact groups G1 to G6 in parallel.
4. While they run, print one batched HUMAN ACTION block covering: UNO Q on Wi-Fi with SSH key login and its IP address; which IMU the team bought; whether the organizer email has been sent; whether the motor layout is locked.

## Stop and ask when
- A fact the code depends on is "unknown" or "conflict" in state/FACTS.md.
- Two spec sections disagree, or a spec is silent on a case you must implement.
- A change would touch wiring, pins, purchases, locked tests, or rules R1 to R8.
- A test still fails after two fix attempts: write the analysis to state/analysis/ and ask.

## Done means
GATE P7 passed: v1.0 tagged and frozen, runbook printed, judge pack ready (if P6 ran), and every metric in docs/PLAN.md section 1 recorded in state/TUNING_LOG.md with pass or fail.
