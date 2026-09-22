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

Current bare-board checkpoint: read state/analysis/P0_bare_board_results_20260922.md.
The last image is inert p0_matrix/default, not robot firmware. D-051 delegates
engineering choices without questions; D-052 permits bare-board diagnostics only.
Do not request additional hardware for the next P1 host task or reuse a recorded
USB connection as proof that the device is still attached. Full Escape/WAIT/
contact preview are now HOST-TESTED716cases and TARGET-COMPILED inside inert
timing only; see P1_escape_wait_validation.md. D-057 START routing subsequently
passed740host cases and sanitizers (P1_start_routing_validation.md); that later
source has no new target build. Logical Menu9d9b858 is now HOST-TESTED776 cases/
12,231,614 assertions normal+sanitizers with separate scoped review;116 scripts
pass. Read P1_menu_validation.md. Resume GO heading ownership from the unadopted
P1_robot_heading_contract_audit.md, then production Robot integration. Menu and
START routing are complete as components; service execution remains pending.
Use the event audit as unadopted recommendations. Keep phase gates and the real
app/HAL gaps explicit.
