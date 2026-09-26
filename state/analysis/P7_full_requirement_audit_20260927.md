# Full requirement audit - 27 September 2026

Audited source/evidence baseline: `ab71e01e55d076f1b244dd659eba7ee08d69fe5e`.
Root and two separate scoped auditors inspected the P0-P7 task/exit definitions,
current acceptance packets and saved native/host evidence. No test or board run
was repeated for this audit. The preceding goal turn made real progress: D241
compiled and its actual review passed, with durable raw evidence and current docs.

**The full project is not complete.** The broader audit supersedes the earlier
narrow statement that no further software preparation was identified. The P2.2
outer-loop/five-minute instrumentation gap is now closed by D243 source/host and
current target compilation/offline retention checks; its physical all-sensor
trial remains absent. See P7_outer_loop_timing_actual_validation.md. B7 additionally
retains the D121/R6 policy conflict.
P6 contains absent deliverables but is currently ineligible. Physical results,
human gates and release/rehearsal requirements remain unfulfilled.

Legend: **P** proved only within the cited scope; **S** software/compile support;
**H** missing physical/human evidence; **U** unverified requirement/policy;
**I** not currently eligible. S never implies that the physical task passed.
Historical reports keep their original sources, failures and limits.

## P0 and P1

| Item | Disposition and authoritative evidence |
|---|---|
| 0.1 G1 pins/buses/electrical | P research/H hardware: P0_G1.md and FACTS; no PINMAP OK or purchased-interface electrical acceptance. |
| 0.1 G2 APIs/PWM/IRQ/time/RAM/watchdog | P research/limited measurement: P0_G2.md, P0_pwm_irq_compile_validation.md, P0_gpio_validation.md, P0_adc_validation.md. PWM/IRQ and live RAM remain H; installed watchdog is disabled. |
| 0.1 G3 startup/Bridge | P source and bounded transport: P0_G3.md, P0_counter_validation.md, D239 actual delivery. Both true cold-start latencies remain H. |
| 0.1 G4 toolchain | P ADB fallback and actual board-side compile/upload. D241 actual validation proves current static/Immediate compilation; no M1 deployment. SSH itself is not claimed demonstrated. |
| 0.1 G5 components | P research/H actual electrical interfaces: P0_G5.md and FACTS. Unknowns retain proposed bench tests. |
| 0.1 G6 IMU | P library/API compile: P0_G6.md, P0_imu_compile_validation.md. Real identity, setup, range/rate and successful/fault timings remain H. |
| 0.2 staging, flags, compile/upload/log/test tools | P bounded routes and includes: current D241 actual validation, D240/D241 contracts, P0_counter_validation.md, P1_robot_validation.md. Generic legacy MATCH upload is not qualified deployment; AGENTS command table corrected in D242. |
| 0.2 matrix text/counter | P counter windows 4-11 and56-63; H visible SUMO text. P0_counter_validation.md and P0_gate_request.md. |
| 0.2 both startup latencies | H/U: P0_gate_request.md. Immediate compilation is not a power-on measurement. |
| 0.3 scaffold | P: host/CMakeLists.txt, doctest, source/config layout and reviewed host/target history. |
| 0.4 bare jitter/GPIO/QTR/ADC | P limited historical observations: 60000 scheduler samples;400 GPIO cycles;200 disconnected QTR acquisitions;1000 ADC calls. P0_timing_measurement_codex.md, P0_gpio_validation.md, P0_qtr_validation.md, P0_adc_validation.md. Not current loaded-robot timing/electrical acceptance. |
| 0.4 IMU timing | H: real sensor absent in board-only setup; compile-only is insufficient. |
| 0.5 pin map | S/H: HARDWARE section3/FACTS source mapping; physical acceptance and PINMAP OK absent. |
| 1.1 interfaces first | P recorded contract/commit order: P1_robot_validation.md and P1_robot_interface_audit.md. |
| 1.2 named core modules/spec tests | P software: P1_robot_validation.md and P1_fresh_gate_codex.md. |
| 1.3 properties | P software: fixed-seed10000 streams, R1/R5, mirror/finite/bounded outputs and approved policy amendments in P1_robot_validation.md. |
| 1.4 architecture/flow/FSM/rationale/explanation text | P document: docs/ARCHITECTURE.md, corrected/reviewed in P1_fresh_gate_codex.md. Human explanation remains H. |
| 1.5 MCU compile | P: historical P1 target receipt and current D241 actual production compile. |
| 1.6 safety audit/fixes | P scoped source checkpoint: P1_fresh_gate_codex.md; later changes have scoped reviews, not a new claim of an exhaustive current gate review. |

P0 exits: G1-G6 source questions/flagged unknowns and host tooling have scoped
evidence. Optical text, both startup latencies, PINMAP OK, complete gate review
and human GATE P0 PASS remain absent. P1 exits: the895-case/13765968-assertion
normal/sanitizer checkpoint, table/locked coverage, target compile and fresh
scoped safety review pass; EXPLAINED OK and human GATE P1 PASS remain absent.
The authoritative registry still says Active phase P0, gates none. Software
scheduling delegation does not author human gate lines.

## P2

| Item | Disposition and evidence |
|---|---|
| B1 opponents | S/H: P2_opp_view_validation.md, P2_display_channel_validation.md. Need seven real polarities/ranges, black-box hits, live mapping and60s empty-ring false-hit result. |
| B2 QTR | S/H: P2_qtr_raw_validation.md, P2_qtr_native_validation.md. Need actual black/white/brown evidence, brown-as-black, electrical and asynchronous frame/source-age qualification. |
| B3 IMU | S/H: P2_imu_heading_bench_validation.md, P2_imu_resume_validation.md. Need calibration, <2deg/60s drift,360deg within3deg, rate/range and live tick cost. |
| B4 motors | S/H: P2_stand_integration_validation.md and P2_motor_native_validation.md. Need wiring, specific STAND OK, wheel agreement, forward/reverse/brake/coast, EN kill within1tick, waveform/frequency and fault checks. |
| B5 power | S/H: P2_vbat_validation.md/P2_power_inputs_validation.md. Need actual meter agreement within0.05V across9.5-12.6V. |
| B6 UI | S/H: P2_ui_bench_validation.md, P2_button_routing_validation.md, P2_ui_adc_probe_actual_validation.md. Floating128samples do not qualify button/BOTH windows or visible behavior. |
| B7 brownout | U/H: D121 in P2_software_acceptance_packet.md and P2_motor_stand_feasibility.md. Original20 full forward/reverse cycles conflict with unchanged R6/current ATTACK. Protected resolution, then actual half-pack run and no-reset evidence are required; partial-duty tests cannot substitute. |
| B8 recorder | P synthetic subset/H live robot: D239 actual validation proves607508B wire,5001frames/8events/session/CRC/CSV/SEALED/no reportedloss. Missing actual200s live acquisition and live free-RAM/stack qualification. |
| 2.1 application integration | S/restricted native evidence: P2_app_runtime_validation.md, P2_app_default_actual_validation.md, D241 current compile. All-source initialized runtime acceptance remains H. No watchdog integration is required for the verified disabled installed watchdog. |
| 2.2 five-minute full timing | S/H: D243 now supplies conservative outer-loop intervals and the fixed five-minute cohort, with focused host and current target compile/retention proof in P7_outer_loop_timing_actual_validation.md. D229 completed-epoch evidence stays separate. All-sensors-live <800us worst-case/p99 remains a physical requirement. |
| 2.3 MATCH traffic | S/H runtime: P2_app_dump_validation.md, D240/D241 contracts and current compile. IDLE-only operational capture/ownership remains unqualified; no motion-input route is authorized. |
| 2.4 QTR_CAL | S/H: P2_qtr_cal_validation.md, P2_calibration_delivery_validation.md, P2_qtr_receiver_validation.md. Need real color sequence/ranges/visible service/accepted delivery. |
| 2.5 dimensions | H: no accepted assembled weight or footprint measurement. |

P2 exits are unachieved: B1-B8 on the assembled robot with numbers, hardware-checked
FACTS, five-minute full timing, B7 zero resets, complete safety/gate review and
human GATE P2 PASS. P2_software_acceptance_checkpoint_review.md explicitly accepts
only bounded software characterization. D239 does not override that boundary.

## P3, P4 and P5

| Item | Software evidence | Missing original acceptance |
|---|---|---|
| 3.1 | P3_countdown_analysis_validation.md |50 real starts,each>=5.1s,spread<5ms. |
| 3.2 | P3_software_acceptance_packet.md | Three front and three per rear-corner R_room measurements. |
| 3.3 | P3_stop_trial_validation.md |15 runs across five duties, compatible distance/R_room readings and human-approved safe cap. |
| 3.4 | P3_turn_integration_validation.md |20 signed90/180degree trials within5degree and measured timed fallback. |
| 3.5 | P3_drive_test_validation.md |24/24 physical edge escapes at approved cap. |
| 3.6 | P3_software_acceptance_packet.md |Ten actual brown-line crossings,zero false edges. |
| 3.7 | P3_software_acceptance_packet.md |Twenty60s search runs,zero exits/resets,observed deliberate pattern. |
| 4.1 | P4_reactive_profile_validation.md |Ten placements:>=9 acquisitionswithin3s,>=8safe push-outs. |
| 4.2 | P4_timing_evidence_validation.md/P4_loss_analysis_validation.md |Ten qualified lost-target trials with duty dropwithin35ms and supported approach-duty tuning. |
| 4.3 | P4_software_acceptance_packet.md |8/8 physical facing successeswithin800ms. |
| 4.4 | P4_push_through_validation.md/P4_push_literal_validation.md |20ms-step tuning only with zero self-exits and4.1stillpassing,never>100ms; currentzero retained. |
| 4.5 | P4_software_acceptance_packet.md |Onset<=1200ms,8/10side reaches,attempt-limit and false-stall observations. |
| 4.6 | P4_software_acceptance_packet.md |Twenty60s spectator runs,zero exits,genuine phantom events. |
| 4.7 | P4_software_acceptance_packet.md |Real card test proving fault indication,bit masking and remaining hunt behavior. |
| 5.1 | P5_software_acceptance_packet.md |Ten runsperincludedopener,>=9ATTACK outcomes,zero exits. |
| 5.2 | P5_software_acceptance_packet.md |Applicable ten-run charger cohorts,60fps video,>=8side approaches withoutfrontimpact. |
| 5.3 | P5_abort_timing_validation.md/P5_abort_analysis_validation.md |Ten qualified physical trialsperopener; retain frontTRACKthenqualifiedATTACK semantics. |
| 5.4 | P5_software_acceptance_packet.md |Actual mirrored heading traceswithin10degree. |
| 5.5 | P5_mode_availability_validation.md/P7_readiness_validation.md |Measured mode selection<5s and arm-length readability. |

Every row is S/H, not a passed physical test. P3 exits additionally need actual
tuning evidence and human GATE P3 PASS; P4 needs named logs, complete safety/gate
review, human GATE P4 PASS and its actual date; P5 needs mandatory SIDESTEP_R/L
and DIRECT passes, optional ARC_R/L and WAIT either passed or removed, complete
review and human GATE P5 PASS. Optional modes currently remain enabled.

## P6 and P7

| Item | Current disposition |
|---|---|
| 6.1 plotter/three real plots | I: tools/plot_match.py is absent; real push-out,re-flank,edge-escape cohorts absent. |
| 6.2 start histogram | I: no delivered plot; countdown JSON analysis is not the requested histogram. |
| 6.3 two-page judge pack | I: docs/JUDGE_PACK.md is absent; architecture material is not that deliverable. |
| 6.4 five-minute demo | I/H: no completed dedicated demo; real sensor/hold/edge/stall/dump demonstration unavailable. |
| 6.5 team rehearsal | I/H: no <60s per-member confirmation. |
| 7.1 freeze/release | P software/H release: D241 actual compile and guarded deployment exist; qualified frozen config,actual deployment,v1.0 tag and release conditions absent. |
| 7.2 runbook | P document/H operation: RUNBOOK and MODE_CARD cover all original topics; physical qualification,filled release record/team verification/printing absent. |
| 7.3 rehearsal | H: REHEARSAL_SCOUTING has blank forms,not three performed best-of-three sets. |
| 7.4 kit | P checklist/H possession: RUNBOOK lists required items; charging,packing/possession and printed copies unverified. |

P6 is conditional on actual P4 by30September and the stronger P3scope rule. No
such gate exists; do not create conditional judge deliverables early or imply
eligibility. P6 exits need the team-reviewed pack with real plots and human pass.
P7.2 includes night-before,pit,mode card,ring,between-round,timeout/battery swap,
after-match and all six failure-playbook topics. Written instructions are not
execution. P7 exits require tagged hash,printed runbook,rehearsal and human pass.
`git tag --list` is empty. No human phase gate appears in the current registry.

## Cross-cutting requirements and next action

PLAN metricsM1-M9 correspond to the physical P3-P5 cohorts above. M10 is full
initialized timing, M11 is B7, M12 is2950gwithin20g, M13 is the assembled199mm
box check; none has current complete robot acceptance. PLAN assumptionsA1/A2/A5/A7
need scouting/physical maneuver/grip/stall evidence; A3/A4 need real sensors/IMU;
A6 and PLANsection5 need organizer answers. No email was sent without authorization.

R1/R5/R6 have source-derived safety tests and reviewed implementation, but actual
starts/edge/governor performance remain unmeasured. R2/R3 have source/transport
guards; current full operational behavior is not established by synthetic capture.
R4 remains physically unqualified and D243 supplies missing preparation. R7/R8
remain enforced: no motor-enabled run or pin/electrical change is authorized by
this audit. R9config changes require evidence; none is made here. R10localcommit
constraints remain, no push/tag; R11 requires actual measurements beforeacceptance.
All intended core/HAL modules exist; a complete hardware claim still cannot be
derived from module presence, tests or a package manifest.

D243 software measurement preparation is complete within its reviewed scope.
The next substantive work needs new physical evidence or the explicit B7-only R6
exception decision. That question is pending the human; silence does not authorize it. Do not
repeat accepted builds/diagnostics without a source change or a new evidence
question. Current date precedes end28September scope cut and1October21:00freeze.
The full goal remains active and unachieved; this audit does not pass a phase.
