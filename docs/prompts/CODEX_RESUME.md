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

Current checkpoint: production P1 core is implemented and software-verified.
Metadata59376fe, Robot/scenarios8692734, inert app/architecture3e46ea4.895 cases /
13,765,968 assertions pass normal and ASan/UBSan;116 tooling checks pass. Fresh
full-core and reused scoped reviews PASS, with independent runtime reproduction.
Actual bare UNO Q app compile-only sourcece90f09d passed, MATCH0/MOTORS_ALLOWED0,
125508B program/61004B globals. No upload/reset/start or new motor permission.
Read analysis/P1_robot_validation.md, preserved P1_robot_failure_analysis.md,
reviews/P1_fresh_gate_codex.md and reviews/P1_robot_codex.md.

No human phase gate has passed. P1 needs EXPLAINED OK and GATE P1 PASS; P0 still
needs optical/Monitor/cold-start and electrical/pin-map evidence. Current packets
are reviews/P1_gate_request.md and reviews/P0_gate_request.md. Do not redo solved
Robot contracts/tests or start P2 HAL solely because P1 software checks pass.

Next eligible work must respect those gates: review remaining P0 bare-board-only
transport/startup dependencies from existing G3/G4/Facts before any new bounded
inert test; otherwise retain the checkpoint pending the original human evidence.
SC-A/B/I remain hardware/API dependencies, not assumed successes. No additional
hardware request now. Do not manufacture a gate, measurement or uninterrupted
background run; the complete app/HAL and original P2–P7 remain unfinished.
