@AGENTS.md

# Claude Code specifics

## Operating mode
- Start each phase in plan mode: read the phase file, list its tasks, mark which run in parallel, then execute.
- Keep your own context lean. Load only the documents the phase file lists. Send bulky material (datasheets, search results, long logs) to files under state/ or logs/ and read summaries.
- Start a fresh session between phases with docs/prompts/RESUME.md.

## Sub-agents (definitions in .claude/agents/)
Use sub-agents for context isolation and parallel work. There is no fixed cap: spawn one per independent task. Never put two sub-agents on the same file.

| Sub-agent | Use it for |
|---|---|
| fact-checker | Any hardware or API fact before code or wiring depends on it (P0 fans out one per fact group) |
| test-author | Tests written from docs/BEHAVIOR.md, independent of the implementation |
| safety-auditor | Adversarial review of rules R1 to R6 at every gate and after any change to hal/motors, core/countdown, core/fsm, core/governor, core/edge |
| log-analyst | Turning logs and TUNING_LOG entries into evidence-backed config proposals |
| general-purpose | One per independent module or bench sketch (for example each HAL driver in P2) |

Output contract for every sub-agent: at most 30 lines back to you, plus the paths of files it wrote. Details go into files.

Verification discipline: no agent grades its own work. Your code is checked by test-author's tests and by safety-auditor. Treat any sub-agent claim as unverified until a test, a build, or a measurement confirms it.

## Cross-model review with Codex (every gate)
1. Once per machine, run `codex --help` and confirm the non-interactive command (usually `codex exec "<prompt>"`). Record it in state/FACTS.md.
2. Fill docs/prompts/REVIEW_GATE.md (phase, commit range, spec sections) and run Codex with it from the repo root. Save the output to state/reviews/Pn_codex.md.
3. If the Codex CLI is missing or fails, print the filled prompt inside a HUMAN ACTION block so the human can paste it into Codex, and wait for the result.
4. Fix every BLOCKER. For every MAJOR, fix it or justify it in state/DECISIONS.md. Re-run the review after BLOCKER fixes.
Codex reviews only; it does not edit files.
