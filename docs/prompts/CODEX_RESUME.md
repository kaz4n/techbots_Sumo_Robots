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

Current MCU: QTR61d7a2d0/revisiondcca300/default/MOTORS_ALLOWED0 uploaded
03:00:13.327+04 on23September.100 neutral+100 pull-up samples all completed
DEADLINE/mask15. Acquisition totals about1530..1536us, full deployed image/frozen
records verified. Fresh post-run review PASS;306 tooling tests PASS. Read
analysis/P0_qtr_validation.md and reviews/P0_qtr_codex.md. This setup-only result
is not real sensor/freshness/physical-cleanup/WCET evidence; SC-B stays open.
Current source maps61d7a2d0/afa72adb/65d7e5a3/e30b5443/9ea79c80. No repeat upload.

P0 G6 D-066 probe b7bd0df/sourcee0ee0fcc is now TARGET-COMPILED/REVIEWED.
Pinned three libraries installed with full provenance, prior packages unchanged.
No API invocation/upload; setup only anchors addresses.3 scoped host tests and
fresh review PASS. Read P0_imu_compile_validation.md/P0_imu_compile_codex.md;
F-084/SC-AG runtime wait/error limits remain. Full306-tool checkpoint plus3 new
scoped checks, not a combined309 or repeated895-core run. MCU remains QTR61d7.
P0 G2 D-067660eb08/source6578e07a is now TARGET-COMPILED/REVIEWED:80248B
program/34048B globals,8 independent host checks, fresh same-model binary review
PASS. Contractsc8e8f55; installed audits5ad262d; exact raw-byte preservation54dd976.
Read P0_pwm_irq_compile_validation.md/P0_pwm_irq_compile_codex.md/F-086..088.
No upload/PWM/IRQ execution; inherited hook/runtime and wrapper limitations remain.
No further required autonomous P0 task is eligible in current bare-board scope.
Next when physical acceptance resumes: optical matrix and true default/Immediate
cold-start checks via P0_MEASUREMENTS_TEMPLATE.md, preserving Immediate-matrix
restriction, then electrical/PINMAP and original review/human gates. Do not redo
completed diagnostics or start P2. No additional hardware request now.

Prior checkpoint: P0 fixed counter source75ab5a22/default/MOTORS_ALLOWED0 was
uploaded01:55:51+04 on23September. Its real logger received4..11 then56..63. Read
analysis/P0_counter_validation.md and reviews/P0_counter_codex.md first:156 tool
checks and40 sanitizer checks pass; fresh source/separate binary audits PASS.
Those prior manifests75ab5a22/b4c61daf have now been superseded. The8-second
logger deadline is explicit (remote142, local validation0). Another Monitor client
existed; do not claim Linux-down/no-subscriber, optical, cold-boot or WCET proof.

Production P1 core is implemented and previously software-verified.
Metadata59376fe, Robot/scenarios8692734, inert app/architecture3e46ea4.895 cases /
13,765,968 assertions pass normal and ASan/UBSan;116 tooling checks pass. Fresh
full-core and reused scoped reviews PASS, with independent runtime reproduction.
Actual bare UNO Q app compile-only sourcece90f09d passed, MATCH0/MOTORS_ALLOWED0,
125508B program/61004B globals. That P1 compile did not upload/reset/start; the
separate P0 inert upload above did. No motor permission or human gate is inferred.
Read analysis/P1_robot_validation.md, preserved P1_robot_failure_analysis.md,
reviews/P1_fresh_gate_codex.md and reviews/P1_robot_codex.md.

No human phase gate has passed. P1 needs EXPLAINED OK and GATE P1 PASS; P0 still
needs optical/cold-start and electrical/pin-map evidence. Fixed Monitor counter
delivery is now observed; stock Bridge/production transport remain separate. Current packets
are reviews/P1_gate_request.md and reviews/P0_gate_request.md. Do not redo solved
Robot contracts/tests or start P2 HAL solely because P1 software checks pass.

Later actions must respect those gates: retain the checkpoint pending remaining
original physical/optical/cold-start and human acceptance when no eligible work
exists. Do not redo the completed D-062 counter to fill time. SC-A/B and production
SC-I remain hardware/API dependencies, not assumed successes. No additional
hardware request now. Do not manufacture a gate, measurement or uninterrupted
background run; the complete app/HAL and original P2–P7 remain unfinished.
