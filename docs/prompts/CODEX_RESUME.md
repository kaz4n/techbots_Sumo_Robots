# Resume SumoX-26 in Codex

1. Read AGENTS.md in full and applicable nested instructions. Check actual local
   date/time in Asia/Dubai, git status/log, and preserve all user edits.
2. Load state/CODEX_HANDOFF.md, PROGRESS.md, DECISIONS.md, FACTS.md,
   CODEX_EXECUTION.md, TUNING_LOG.md, analysis/spec_conflicts.md and latest reviews.
3. Recover the active phase from genuine progress/human gates, never templates.
   Read that phase prompt and relevant specification sections. Apply PLAN section
   3 deadlines; D-015 changes roles only. D-016 permits P1 host development while
   P0 acceptance remains pending; it supplies no hardware evidence or gate.
   P7 build-only is --match --compile-only.
4. Briefly report phase, last result, open human/review dependencies, schedule,
   and first eligible unfinished task; execute it. Do not bypass gates to fill time.
5. Separate host tests, script substitutes, target builds, uploads, measurements,
   ring validation. Never reuse motor authorization across runs or revisions.
6. Keep PROGRESS append-only; make small local commits, never publish. At the
   boundary record files/commits, commands/statuses, limitations, human requests,
   review findings and exact next task. Use existing HUMAN ACTION/CONFUSION formats.

Current checkpoint: Menu9d9b858 and HeadingReference4671c8b are HOST-TESTED:
807 cases/12,233,461 assertions normal+ASan/UBSan;116 script checks pass; separate
scoped read-only reviewer reproduced the host result. Current core also TARGET-
COMPILED inside inert p0_timing/default sourcebbf6c22, MATCH0/MOTORS_ALLOWED0,
exit0. No new upload/reset/start; prior inert p0_matrix remains the last firmware.
Read P1_menu_validation.md, P1_heading_validation.md and their scoped reviews.

Current work: D-060 public Robot interfaces ea4618c/4ae6d45 are committed. Complete
fsm_robot.cpp and independent actual-Robot/locked/event tests against the adopted
analysis/P1_robot_contract.md, then freeze/review/build. Metadata implementation
and inert app compile entry are also in progress, not yet whole-suite validated.
D-059 heading ownership and D-057/D-058 logical menu/routing are completed components;
service consumers, full Robot/app/HAL and all human phase gates remain pending.
The adopted contract and actual headers supersede proposal declaration sketches.
Do not request extra hardware now or treat historical USB evidence as live access.
Bare-board evidence is P0_bare_board_results_20260922.md; no motor permission exists.
