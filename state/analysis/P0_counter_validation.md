# P0 bounded counter validation — 2026-09-23 Asia/Dubai

Outcome: the bare UNO Q now runs the reviewed inert SUMO matrix/counter image.
Actual fixed counter notifications reached the project's receive-only Linux
Monitor logger. P0 remains GATE-PENDING: optical display, true cold-start tests,
external measurements and PINMAP OK are still absent. P1 software remains at its
previously verified checkpoint; this task does not authorize P2 or motors.

## Implementation and review

- D-062/public contracts precede code and tests:8f94452,cab665c,3f9ea7f.
- Packet implementation/independent tests:dd4ed33. Adapter, matrix integration,
  explicit P0 config values and complete validation snapshot:6b99a60.
- One36-byte MessagePack mon/write notification slot, immediate busy refusal,
  exactly one byte per data callback, separate final TC, terminal timeout/error.
  No inbound handler, Bridge start, serial command, motor write or dependency patch.
- Existing internal115200/8N1/no-flow-control UART; no header-pin/wiring change.
  Deferred UART initialization is setup-only and may wait for hardware. Runtime
  CR1 exclusive retries rely on the pinned single-core IRQ-mask/ownership proof;
  this is not a general worst-case guarantee for arbitrary builds or hardware faults.
- Source review: reviews/P0_counter_codex.md, fresh same-model context, PASS.
  Exact binary audit: P0_counter_binary_audit_20260923.md, separate context, PASS.
  Both distinguish ordinary driver assumptions from measured timing. No gate review
  or human approval is manufactured from these scoped reviews.

## Host and target receipts

| Check | Result | Evidence |
|---|---|---|
| Independent fixed-packet tests |25 cases/156553 assertions PASS |tests/tooling/counter_packet_cases.cc; sanitizer and tooling receipts |
| Independent actual adapter with API substitutes |39 process-isolated cases PASS |tests/tooling/counter_uart_cases.cc; separate reviewer reproduction |
| New packet/adapter ASan+UBSan |40 Python checks PASS,13.841s |P0_counter_sanitize_20260923.txt; compile flags/commands preserved |
| Full tooling suite |156 checks PASS,44.130s,exit0 |P0_counter_tooling_20260923_final.txt |
| Board-side compile-only |exit0,77596B program/31416B globals |P0_counter_target_compile_20260923.txt |
| Actual inert upload/reset/start |exit0,01:55:51.731+04 |P0_counter_upload_20260923.txt |

Target is explicit USB2629958581, user-reported bare UNO Q under D-052. Build and
upload ran on board Linux through ADB with CLI1.5.1/core1.0.0, default startup,
MATCH0/MOTORS_ALLOWED0. The upload used `python tools/board_tool.py flash
bench/p0_matrix`; the prior build added `--compile-only`. No motor-capable image
was uploaded and no other hardware was connected/requested by this task.

Source75ab5a2257a6f322bc9b5c2ee9059f3e8ac6b3817eca39f03991d18e2ebda0af
has28 staged files. Timing snapshotb4c61daf57f7273c93e97572d53f5ccd8ac456b4c104cdc328ab30d87086afd2
has24. Both complete maps were independently checked before updating the upload
manifest. The timing image was not uploaded this session. Post-upload Linux
artifact hashes match the exact pre-upload audit, including wrapped image
06de35038870da90a14e7259770d689438c656a5b6346c164db81209eb964939.
This post-check is not MCU flash readback; see P0_counter_post_upload_identity_20260923.json.

## Actual counter observations

The coordinator invoked the real `board_tool.logs()` implementation used by
`tools/logs.sh`, preserving its receive-only Python body. Only a Linux
`signal.alarm(8)` prefix imposed a finite capture window. No Monitor input bytes
were sent. The raw remote command, logger source hash, output, elapsed time and
exit are preserved in each JSON receipt. The remote process intentionally exited
142(SIGALRM); the local validator separately returned0 after checking at least
five complete exact-format sequential uint32 counters. This is not a naturally
successful termination of the indefinite logger, nor a swallowed transport error.

- Capture from01:55:54.249+04: eight complete counters4 through11,8.119839900s.
  Evidence: P0_counter_monitor_capture_20260923.json.
- New client from01:56:46.265+04: eight complete counters56 through63,8.130008300s.
  Evidence: P0_counter_monitor_reconnect_20260923.json.

This verifies real MCU-to-Linux counter delivery and this client's reconnection
while the MCU continued progressing. A socket snapshot showed another established
Monitor client, so it does not prove an interval without any subscriber. Linux
and its router remained running. No Linux-down/backpressure, physical timeout
injection, exact interrupt count, masking duration, final diagnostic RAM snapshot,
optical appearance, power-on latency or full-loop WCET was measured. Eight seconds
of receipt is not a clock-accuracy or competition qualification test.

The earlier60000-sample/max3us result belongs to the previous bare timing sketch;
do not apply it to this new matrix/UART workload. P1's895-case result is prior
software evidence, not a core-suite rerun during this P0 transport task.

## Failures, next action and boundary

P0_counter_failure_analysis.md preserves the initial31/34 independent adapter
expectation discrepancies and the first full tooling150-check fixture failure.
Clarification2f7e1b4 precedes the three new-case amendments. Fixture repairs retain
all original assertions and add exact D-062 config/scheduling checks. No existing
locked test or any of the76 B16 defaults changed.

No further transmission implementation is needed for P0's fixed counter. Preserve
this checkpoint and remaining physical/human acceptance list; do not repeatedly
redo solved transport work or start P2 through a gate bypass. Production recorder
transport/Immediate startup behavior still require their own later contract and
validation. Current firmware remains this inert default matrix/counter image.
