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
| Board scripts | SCRIPT-TESTED243 checks and actual board-side ADB compile/upload/logger receipts; P0_gpio_validation.md/P0_adc_validation.md/P0_counter_validation.md |
| Actual matrix/counter log round trip | COUNTER OBSERVED: D-062 inert adapter delivered4..11 and56..63; optical matrix appearance remains absent; stock Bridge is not the adapter |
| Both startup modes measured | NOT MET: default/Immediate timing compiled, default60000-sample scheduler measurement; no true cold-start/Immediate runtime measurement |
| Physical P0 micro-benchmarks | PARTIAL: bare scheduler60000samples and startup ADC1000calls and GPIO400cycles measured; QTR and available external-device checks still separate |
| Pin map verification and PINMAP OK | NOT MET |
| Fresh independent gate review | PENDING after physical evidence; scoped software review in P0_recovery_codex.md |
| Human GATE P0 PASS | NOT PROVIDED; never author this on the human's behalf |

Updated2026-09-23: bare UNO Q ADB connectivity and installed tool inventory are
verified in FACTS F-062 onward and P0_bare_board_results_20260922.md. No SSH
configuration change was required; explicit ADB fallback builds on board Linux.
Latest inert P1 app compile-only also passed, sourcece90f09d, without upload.
Its successful target compilation does not close any missing P0 physical check.
The D-064 GPIO1dfbd571/default image is the latest upload at02:36:15.644+04
on23September. All400 readback cycles and final HIGH/off succeeded; pair2..3us,
pinMode2..11us after the first call. Full deployed image/frozen RAM verified.
Fresh source/binary/receipt reviews PASS in P0_gpio_codex.md. This is empirical
setup-only timing, not optical verification, native error recovery or robot WCET.
Prior ADC first276us/subsequent139..140us is retained for its earlier image.
Fixed-counter
source/binary reviews and raw logger receipts remain preserved. No request to
connect additional hardware is needed while the user defers those measurements.

Do not promote source checks, synthetic tests, or assumed connectivity to board
evidence. Include the real target/tool inventory, command logs, observed display
and counter, raw startup/timing data, approved pin map, and all resolved findings
in the eventual review. Return findings with file:line and BLOCKER/MAJOR/MINOR,
then PASS or FAIL under the original REVIEW_GATE rules.
