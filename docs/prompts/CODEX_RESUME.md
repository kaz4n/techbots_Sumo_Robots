# Resume SumoX-26 with Codex

Read AGENTS fully, CODEX_HANDOFF, PROGRESS, DECISIONS, FACTS, TUNING_LOG,
CODEX_EXECUTION and open conflicts/reviews. Inspect Git and actual Dubai date;
preserve original deadlines, human gates, evidence and unrelated work.
D051/D075 permit active P2 software despite untested physical acceptance. Full
P0-P7 ACTIVE/incomplete; no human gate/PINMAP/EXPLAINED or motor authority.

Latest software: D09117bb38a, inert recorder200s bench and bounded readback tools.
Read analysis/P2_recorder_bench_contract.md, native_audit.md, validation.md,
run.md, raw/runtime_summary.json and reviews/P2_recorder_bench_review.md including
runtime addendum. Exact74-file source1502e948/ELFeff3e050/ZSK0448e3ac uploaded
once to bareUNOQ ADB2629958581, defaultstartup/MATCH0/MOTORS_ALLOWED0.

Actual MCU run passed scoped synthetic recording: release-toSTOP200000998us,
hold5100000us,5001frames/8events, independent CRC900325728, no recorder losses or
active motor callbacks. Missing synthetic IMU gives one expected calibration
rejection event. Max203us is runner timing, not fullHAL/WCET. Two matching loaded
LLEXT pools show25116B free payload/largest21604B; sampled stack31208B headroom
is not historical high-water. Native UART transfer and physical B8 remain pending.

First capture timeout preserved. Reviewed flash subdivision retry succeeded
without reupload/reset,47reads/934892B/51commands/281.633s within original limits.
Board left frozen inert1502e948; recheck connection before any future board work.
No sensor/native motorGPIO/UART initialization. User authorizes bareUNOQ inert
work; do not ask for more hardware now or flash/run motor-capable firmware.

First unfinished software task: SC-AK acquisition-start versus decision time.
Read analysis/P2_app_integration_map.md, spec_conflicts.md, P1_robot_contract.md
and P2_imu_integration_contract.md before source changes. Under D051 record the
narrow additive contract/decision, publish interfaces, obtain independent tests,
implement bounded timing accounting, run meaningful checks and fresh review.
Keep sensor decision timestamps after acquisition; include acquisition in whole
execution duration without changing legacy receipts or established locked tests.
No D092 or final timing contract has yet been allocated. Do not treat the map's
recommendation as already implemented or fully specified.

After timing, compose the real app transaction owner then native scheduling.
app.ino is still a forced-inert link scaffold. QTR sub-tick service, bounded battery
age, native transport clean framing, local-only reset and QTR_CAL print ownership
remain integration work. Existing600us IMU+150us motor+100us ADC ceilings do not
prove an800us whole tick. Physical SC-A, SC-AJ and human phase gates stay pending.

Append ledgers and make task-owned local commits only. At boundary record exact
files/commits/commands/results/limits and the first eligible unfinished task.
Never push, tag, rewrite history, manufacture measurements or author human gates.
