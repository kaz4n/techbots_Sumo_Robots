# Remaining P2 work after D115

Read-only eligibility checkpoint,2026-09-24. D115 implementation, independent
tests and target collection are substantively complete per coordinator handoff;
the final evidence/review closure remains coordinator-owned. This note does not
declare that closure, any physical acceptance or a human gate. No source, test,
ledger, configuration or board action was performed.

**Next action: finish D115's exact target/ABI/loader and independent review
binding, then checkpoint the completed adopted software scopes.** There is no
remaining already-adopted, fully specified standalone bench implementation found
in this bounded audit. Further useful work exists, but its missing evidence or
unadopted scope must remain explicit; another generic runner would not close it.

## Mandatory acceptance still outstanding

| Requirement | Current preparation and exact remaining action |
|---|---|
| B1/B2/B3/B5 | Named `opp_view`, `qtr_raw`, `imu_heading` and `vbat` benches now exist. Run separately identified physical trials when their actual sources/ownership are qualified: polarity/range/empty-ring60s; QTR black/white/brown and frame timing; rest bias/60s drift/hand360; multimeter comparison9.5–12.6V. These are the literal criteria in `docs/prompts/P2_hal_bench.md:11-15`, not satisfied by synthetic fixtures or compilation. |
| B4/B7 | D115 observes existing setup/inhibition only. It deliberately excludes apply/reset/demand/tokens and full directional or powered-kill trials (`P2_motor_stand_inhibit_contract.md:11-19`). Resolve the separate command-authority question below before implementing directional trials; retain run-specific STAND OK, wiring and electrical prerequisites. Full B7 also has the unresolved R6 conflict. |
| B6 | D112 supplies real A1 acquisition/decoder evidence; D114 now has actual frozen COMPLETE128 on the bare board (`P2_ui_adc_probe_actual_validation.md:3-16`). Its decoder remained UNCONFIGURED/INVALID and no circuit/voltage/button qualification follows (`:18-21,38-42`). Determine actual A1 windows/physical BOTH, then verify real gestures, menu and countdown with the existing matrix path. This is not a missing ADC/decoder/renderer implementation (`P2_hal_bench.md:16`). |
| B8/native dump | D091 already retains an actual200s explicitly synthetic real-Robot/Gate/Recorder run; `recorder_inert` is the existing alternate named bench, not a reason to write another recorder (`P2_recorder_bench_validation.md:65-82`). D101/D103 already attach dump/local inhibited reset; D105 delivers calibration text. Native end-to-end UART/CSV and loaded full-app RAM remain unqualified; actual assembled-robot B8 remains open (`P2_hal_bench.md:18`). |
| Integrated application | Existing `src/app/app.ino:11-24` constructs Runtime/native sources/Gate/dump and keeps all setup grants unconfirmed. Qualify full live sources, QTR_CAL and actual snippet receipt, then measure five minutes of p99/worst-case tick below800us and loaded RAM; weigh/check footprint (`P2_hal_bench.md:21-25`). D104's absent-source Runtime measurement is not all-live timing. |
| Human/physical gates | Update measured hardware facts and tuning evidence, obtain the required final safety review and actual human gate entries. B1–B8 assembled-robot success, B7 zero resets and GATE P2 remain required (`P2_hal_bench.md:27-31`). D051/D075 do not manufacture these (`DECISIONS.md:442-453,841-853`). |

The conditional watchdog clause does not authorize a loader/watchdog project:
installed generated configuration already establishes watchdog disabled
(`P0_installed_debug_contract.md:62-66`; `P0_G2.md:88-90`). The older F031 unknown
row is not a newly discovered missing P2 implementation. Likewise the old
OPP-VIEW-1 display finding was resolved by D108 (`DECISIONS.md:1410-1418`);
current `ui_display.cpp:93` places bit0 left and bit1 center. Do not reopen either
as a substitute task based only on an older inventory.

## Directional B4 is not an existing authorized command path

The public Gate accepts `const fsm::RobotResult&`, not a stand demand
(`src/hal/motors.h:35-44`). Its contract says these are Robot-governed outputs;
Gate does not replace sensor validation or edge arbitration
(`P2_motor_gate_contract.md:34-61`). The actual Transaction calls Robot once and
applies that exact returned result/token, preserving actual feedback
(`P2_app_transaction_contract.md:80-93`). Robot requires identity-matched
application receipts and keeps DRIVE_TEST unavailable (`src/core/fsm.h:479-511`).

Real Countdown plus Governor alone therefore cannot produce an authoritative
replacement RobotResult. Editing a genuine result's wheel demands/state, reusing
its token, or inventing line/opponent/contact/receipt fields would change the
adopted contract even if all selected duties were below full. The actual Robot
does one final contact commitment and governor pass (`fsm_robot.cpp:692-735`).
Explicit line absence/expiry faults after initialization (`fsm_line.cpp:85-100`),
and Runtime requires actual granted/current sources (`P2_app_runtime_contract.md:193-198`).
Wheels-off-ground does not implicitly exempt R1, R5, R6 or those source rules.

An unchanged real Robot can truthfully exercise behaviors under actual qualified
stimuli, or under declared synthetic inputs with inert callbacks. That is not a
deterministic individual-side forward/reverse/brake/coast command facility. D091
already covers the latter inert composition; relabeling it adds no B4 evidence.

Thus **no complete directional B4 stand controller can be adopted as a mere
composition of the present interfaces while also claiming every existing
Robot/source/token contract is unchanged**. A future proposal could preserve
R1–R11 in principle, but must explicitly specify its relationship to the actual
Robot, authoritative source/edge handling, full hold and fresh local start,
governor/feedback/token ownership, finite trial termination and fault cleanup.
No new duty, dwell, timing rule, synthetic-black allowance or edge exemption is
selected here. D051 permits recorded engineering choices; it is not an implicit
protected-contract exception. D115 explicitly adopted none (`DECISIONS.md:1470-1473`).

Full B7 is a separate stronger conflict: non-ATTACK governor profiles are capped
below full, full duty requires genuine centered contact ATTACK, and actual ATTACK
does not request full reverse (`governor.cpp:10-33`, `motors.cpp:133-139`,
`fsm.cpp:79-97`). A below-full reversal cannot be reported as the specified20
full-forward/full-reverse cycles. Do not manufacture contact or silently relax R6.

## Feasible next scope, if continued separately

Native dump preparation is the distinct useful candidate that does **not** need
external sensors or motor authority. It is not yet a fully specified/adopted
implementation task. D113 now proves a sampled completed TCP connection only,
with router registration explicitly UNKNOWN (`P2_dump_receiver_arm_contract.md:96-103`);
its actual zero-byte timeout smoke did not transmit a log (`PROGRESS.md`, D113
actual receive-only smoke entry). This supersedes the old note's missing
connection-ticket feature, but not its framing/ownership blockers.

The exact next action there is a narrow preparation/probe contract based on
`P2_native_dump_bare_feasibility.md:125-163`: verified quiescent MCU TX, completed
exclusive close/purge/reopen, bounded failure-indeterminate handling and a real
receiver before an autonomous synthetic IDLE dump. Existing native grants must
remain factual; partial TX poisons its owner and cannot be recovered by an
invented ACK (`P2_dump_native_contract.md:9-19,30-44`). Reuse the existing
Robot/inert Gate/Recorder/Transfer/UnoQDumpPort and receiver. Do not build a new
transport framework or silently treat TCP CONNECTED as framing_clean.

Until such a scope or a directional authority resolution is explicitly adopted,
the honest result is a software-preparation checkpoint with the above open
acceptance items. It is not a claim that P2 is complete, all future software is
impossible, or the user must repeat the existing D075 authorization.
