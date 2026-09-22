# SumoX-26 Agent Kit

Plan, specs, and agent prompts for your SumoX-26 sumo robot (Dubai Techbots League, Saturday 3 October 2026, Canadian University Dubai).

## What's inside

| Path | Read by | Purpose |
|---|---|---|
| docs/PLAN.md | You first; agents on demand | Goal, metrics, decisions, schedule, order list, organizer questions, strategy stress test, risks, not-doing list, judge evidence map |
| docs/HARDWARE.md | Build team and agents | Power, pin map, wiring with pre-connect checks, sensor layout, weight budget, physics limits |
| docs/BEHAVIOR.md | Agents and judges | State machine, openers, sensor fusion, speed governor, re-flank, tunables |
| AGENTS.md | Codex and Claude Code (auto-loaded) | Rules file: hard safety rules, architecture, conventions, commands, workflow |
| CLAUDE.md | Claude Code (auto-loaded) | Imports AGENTS.md; sub-agent and Codex review policy |
| .claude/agents/ | Claude Code | Sub-agents: fact-checker, test-author, safety-auditor, log-analyst |
| docs/prompts/00_KICKOFF.md | You paste it once | The super prompt that starts the run |
| docs/prompts/RESUME.md | You paste it each new session | Resume from state/ |
| docs/prompts/P0 to P7 | The agent, one per phase | Phase tasks and exit gates |
| docs/prompts/REVIEW_GATE.md | Codex | Independent review at every gate |
| state/ | Agents write, you read | Progress, decisions, facts, tuning log |

## Do this today, in order

1. Place the order in docs/PLAN.md section 4.
2. Send the organizer questions in docs/PLAN.md section 5.
3. Lock the motor layout (docs/HARDWARE.md section 6) before cutting the chassis.
4. Create a git repo, copy this kit into its root, commit.
5. Open Claude Code in the repo (WSL/Ubuntu) and paste docs/prompts/00_KICKOFF.md. It will walk you through putting the UNO Q on Wi-Fi with SSH.

## How the work splits

The agent writes, tests, and reviews code. You build, wire, measure, and run every test that turns a wheel. The agent prints a `HUMAN ACTION REQUIRED` block whenever it needs your hands, a tape measure, or a yes. Answer those fast: they are the critical path.

Gates: each phase closes only when you write `GATE Pn PASS` in state/PROGRESS.md.
