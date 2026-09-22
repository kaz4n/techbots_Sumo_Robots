# P0 gate review request — prepared, NOT READY for gate approval

Use docs/prompts/REVIEW_GATE.md with these values once missing evidence arrives.
Review only; read AGENTS.md and do not edit implementation or locked tests.

Phase: P0. Baseline: `52b935e`. Head: resolve the latest local commit after the
remaining P0 tasks are complete; include any board-related fixes in the range.
Specs: P0 0.1–0.5; AGENTS R1–R11; HARDWARE 1–3/5; unchanged BEHAVIOR B16;
CODEX_KICKOFF tooling safety requirements and D-015 role migration.

| Exit criterion | Current evidence |
|---|---|
| G1-G6 answered or flagged with bench checks | SOURCE-REVIEWED, FACTS F-019 onward and analysis/P0_G1..G6.md; MPU6050 now user-reported |
| Host scaffold | HOST-TESTED; P0_host_tests_recovery.txt |
| Board scripts | SCRIPT-TESTED with controlled substitutes; P0_tool_tests_recovery.txt |
| Actual matrix/counter log round trip | NOT MET; no SSH target; SC-I unresolved |
| Both startup modes measured | NOT MET |
| Physical P0 micro-benchmarks | NOT MET |
| Pin map verification and PINMAP OK | NOT MET |
| Fresh independent gate review | PENDING after physical evidence; scoped software review in P0_recovery_codex.md |
| Human GATE P0 PASS | NOT PROVIDED; never author this on the human's behalf |

Do not promote source checks, synthetic tests, or assumed connectivity to board
evidence. Include the real target/tool inventory, command logs, observed display
and counter, raw startup/timing data, approved pin map, and all resolved findings
in the eventual review. Return findings with file:line and BLOCKER/MAJOR/MINOR,
then PASS or FAIL under the original REVIEW_GATE rules.
