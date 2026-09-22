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
| Host scaffold | HOST-TESTED; current895-case suite, P1_robot_validation.md |
| Board scripts | SCRIPT-TESTED116 checks and actual board-side ADB compile/upload receipts; P1_robot_tooling_20260923_final.txt |
| Actual matrix/counter log round trip | PARTIAL: real inert matrix uploaded; RAM counter441 to444 independently observed, optical appearance and Monitor round trip remain absent; SC-I unresolved |
| Both startup modes measured | NOT MET: default/Immediate timing compiled, default60000-sample scheduler measurement; no true cold-start/Immediate runtime measurement |
| Physical P0 micro-benchmarks | NOT MET |
| Pin map verification and PINMAP OK | NOT MET |
| Fresh independent gate review | PENDING after physical evidence; scoped software review in P0_recovery_codex.md |
| Human GATE P0 PASS | NOT PROVIDED; never author this on the human's behalf |

Updated2026-09-23: bare UNO Q ADB connectivity and installed tool inventory are
verified in FACTS F-062 onward and P0_bare_board_results_20260922.md. No SSH
configuration change was required; explicit ADB fallback builds on board Linux.
Latest inert P1 app compile-only also passed, sourcece90f09d, without upload.
Its successful target compilation does not close any missing P0 physical check.
Existing matrix/default image remains the last uploaded firmware. No request to
connect additional hardware is needed while the user defers those measurements.

Do not promote source checks, synthetic tests, or assumed connectivity to board
evidence. Include the real target/tool inventory, command logs, observed display
and counter, raw startup/timing data, approved pin map, and all resolved findings
in the eventual review. Return findings with file:line and BLOCKER/MAJOR/MINOR,
then PASS or FAIL under the original REVIEW_GATE rules.
