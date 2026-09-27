# P2 software checkpoint and physical acceptance packet

2026-09-24 Asia/Dubai. Software revision **1c2389c9**, D120 contractf4a300c5.
Current phase remains P2 under D051/D075. **P2 is not passed and the full P0-P7
project is not complete.** No human GATE, PINMAP or EXPLAINED acceptance is supplied.
This index consolidates existing requirements/evidence; it creates no new phase.

**2026-09-27 B7 update:** D244 records the human-approved B7-only full-duty
exception. It supersedes the policy implementation stop in the historical D121
section below. Dedicated applied-feedback software, host validation and all three
target compile-only checks passed independent review; original half-charge/
20-cycle/no-reset acceptance remains open. The stand-only deployment route is
host-tested and unexecuted. See [target evidence](P2_b7_brownout_actual_validation.md)
and [deployment evidence](P2_b7_deploy_validation.md). Other entries retain their
dated evidence scopes and are not a claim about the latest loaded firmware.

## Filled review request

- Phase: P2 software/readiness checkpoint; full physical gate remains pending.
- Latest change range:1c387810..1c2389c9 (D120); earlier P2 work is covered by the
  existing scoped reports below. Inspect current critical safety paths as well.
- Specifications: AGENTS R1-R11, P2 B1-B8 and2.1-2.5, relevant HARDWARE wiring and
  BEHAVIOR B3/B4/B6/B13-B15, and explicitly recorded decisions throughD120.
- Claimed: implemented software and the host/target evidence identified below.
  No assembled-robot exit criterion, full-source WCET, motor trial, native dump,
  team explanation, electrical check or human gate is claimed.
- Review method: fresh separate same-model Codex context, actual critical source/
  latest diff and existing evidence; not cross-model review or a fresh exhaustive
  line-by-line audit of all historical P2 code. Report material software findings
  separately from the missing physical/gate criteria. Do not invent a PASS.
- Review: [checkpoint report](../reviews/P2_software_acceptance_checkpoint_review.md).
  Fresh review completed: PASS for the bounded software/readiness characterization,
  no new software findings; FAIL for full P2 acceptance. P2-ACCEPT-1 through5
  explicitly retain physical, full timing/stack, B7, native delivery and gate gaps.

## Existing tasks, evidence and remaining acceptance

All paths below are current evidence entry points, not proof that a physical
measurement happened. Each report retains its exact source/version/scope and
original failures. A synthetic test is not competition evidence.

| Existing task | Software/limited observation evidence and scoped review | Remaining physical or external criterion |
|---|---|---|
| B1 opponents | [named bench](P2_opp_view_validation.md), [review](../reviews/P2_opp_view_review.md); [display channel](P2_display_channel_validation.md), [review](../reviews/P2_display_channel_review.md) | Actual polarity, seven set ranges, black-box detection and60s empty-ring false-hit result; live visible mapping |
| B2 QTR | [raw bench](P2_qtr_raw_validation.md), [review](../reviews/P2_qtr_raw_review.md); [native acquisition](P2_qtr_native_validation.md), [review](../reviews/P2_qtr_native_review.md) | Actual black/white/brown readings and thresholds; complete-frame cadence/source-age and electrical verification under D085; brown remains black |
| B3 IMU | [heading bench](P2_imu_heading_bench_validation.md), [review](../reviews/P2_imu_heading_bench_review.md); [resume behavior](P2_imu_resume_validation.md), [review](../reviews/P2_imu_resume_review.md) | Purchased MPU6050 wiring/address/setup, at-rest calibration, under2degree/60s drift,360degree within3degree and live tick cost |
| B4 motors | [actual B4 controller](P2_stand_integration_validation.md), [review](../reviews/P2_stand_integration_review.md); [native boundary](P2_motor_native_validation.md), [review](../reviews/P2_motor_native_review.md) | PINMAP/electrical/source qualification, new identified STAND OK, both wheels each side direction, forward/reverse/brake/coast, EN kill within1tick, waveform/PWM and driver fault checks |
| B5 power | [voltage bench](P2_vbat_validation.md), [review](../reviews/P2_vbat_review.md); [input ownership](P2_power_inputs_validation.md), [review](../reviews/P2_power_inputs_review.md) | Actual divider/reference/supply readings against multimeter within0.05V from9.5 to12.6V |
| B6 UI | [UI bench](P2_ui_bench_validation.md), [review](../reviews/P2_ui_bench_review.md); [routing](P2_button_routing_validation.md), [review](../reviews/P2_button_routing_review.md); [matrix](P2_matrix_validation.md), [review](P2_matrix_review.md); [actual raw ADC](P2_ui_adc_probe_actual_validation.md), [review](../reviews/P2_ui_adc_actual_review.md) | Real A1 circuit distinguishes all required states including BOTH, measured windows, gestures/countdown/service/visible display.128floating raw samples are not button acceptance |
| B7 brownout | [R6 conflict](P2_motor_stand_feasibility.md), [follow-up](P2_motor_stand_next_audit.md), [checkpoint](P2_after_D115_checkpoint.md); no passing B7 result | Explicit conflict disposition below; original20full-forward/full-reverse cycles and no reset are unperformed and unaccepted |
| B8 recorder | [full synthetic200s transport](P2_recorder_transport_validation.md), [review](../reviews/P2_recorder_transport_review.md); [FIFO](P2_dump_fifo_validation.md), [review](../reviews/P2_dump_fifo_review.md); [earlier bench](P2_recorder_bench_validation.md), [review](../reviews/P2_recorder_bench_review.md) | Actual200s live acquisition/free-RAM/no-gap dump; native ownership/framing/delivery prerequisites remain unproved |
| 2.1 app integration | [Runtime](P2_app_runtime_validation.md), [review](../reviews/P2_app_runtime_review.md); [checked build](P2_app_build_validation.md), [acceptance review](../reviews/P2_app_acceptance_review.md); [actual default load](P2_app_default_actual_validation.md), [review](../reviews/P2_app_default_actual_review.md) | Complete live-source setup; stack/RAM and actual output acceptance. D118 only observed inhibited default app with unconfirmed optional grants |
| 2.2 tick measurement | [timing ownership](P2_tick_timing_validation.md), [review](../reviews/P2_tick_timing_review.md); [restricted actual observation](P2_app_default_actual_validation.md) | Five minutes all sensors live, full fault/timeout worst-case under800us and p99; stored513us from restricted app is not this measurement |
| 2.3 MATCH traffic | [app dump](P2_app_dump_validation.md), [review](../reviews/P2_app_dump_review.md); [frame packing](P2_frame_packing_validation.md), [review](../reviews/P2_frame_packing_review.md); [FIFO](P2_dump_fifo_validation.md) | Actual IDLE-only log transport acceptance under verified native prerequisites; no remote motion input is permitted |
| 2.4 QTR_CAL | [calibration](P2_qtr_cal_validation.md), [review](P2_qtr_cal_review.md); [delivery](P2_calibration_delivery_validation.md), [review](../reviews/P2_calibration_delivery_review.md); [receiver](P2_qtr_receiver_validation.md); [pin table](P2_pin_table_validation.md), [review](../reviews/P2_pin_table_review.md) | Physical color sequence, measured ranges, visible service behavior and actual accepted output delivery |
| 2.5 dimensions | No fabricated measurement | Actual assembled mass and footprint recorded in TUNING_LOG |

Historical capacity findings must be read with their closure evidence: frame
packing addresses the D101 capacity issue; pin-table work addresses D105;
D120 reproduces the current default loadable bytes. The default conditional
loader free span is still8bytes; actual D118 retained4500free/4364largest bytes
does not prove peak stack or full-source WCET. The separate B4 bench's13568byte
conditional free span is a model result, not a loaded-board reading.

## B7 disposition (D121, open conflict SC-AM)

Preserve R6 and the actual Robot/Gate contract. The original B7 requirement cannot
currently be executed faithfully: ordinary reverse profiles stay below full,
full duty requires centered-contact ATTACK, and actual ATTACK does not request
full reverse. No fabricated contact, negative ATTACK override, patched output,
MotorGate bypass, low-duty substitution or repeated D119 sequence is selected.

Leave **B7 BLOCKED / NOT ACCEPTED**. D120's0.25sequence proves neither full-power
brownout endurance nor B7. Before dependent implementation, an explicit protected
resolution must identify how to reconcile the full-power stress criterion with
R6 while retaining actual governor/Gate/hold/edge authority; any later powered
run still requires fresh identified STAND OK and real measurements. This
disposition changes no behavior, locked test, full-power criterion or gate.

## Board and resumability

Only the bare UNO Q is requested/available now; no additional hardware request
is made. D120 performed two Linux compile-only builds, no upload or MCU/UART
operation. Last actual MCU evidence is the consumed D118 e820c0e1 default/M0
run; no run authorization is reused. Actual source readiness is never inferred
from a build, clock passage or the user's request to assume success.

Native dump remains blocked by [the exact prerequisites](P2_native_dump_prerequisite_followup.md)
and [their review](../reviews/P2_native_dump_prerequisite_followup_review.md).
The known passwordless sudo failure is not retried; do not guess a password,
bypass holder visibility or invent clean framing/cancel/reopen acknowledgments.

First eligible work after this checkpoint review is a supported concrete finding
or newly supplied physical/native prerequisite. Without one, save the checkpoint
and stop; do not invent another helper framework or begin P3 without its gate.
P0 physical/pin acceptance and P1 EXPLAINED OK/GATE remain pending as well. Apply
the existing28September scope cut,30September P6 condition and1October21:00 freeze
when their actual Asia/Dubai deadlines arrive; none is fabricated as passed.
