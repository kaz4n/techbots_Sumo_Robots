# D104 identified bare-board Runtime run1

2026-09-23 Asia/Dubai. User explicitly states the UNO Q alone is connected and
permits testing it. Target ADB serial2629958581. No extra hardware or mechanical
state is inferred. This is an inert upload authorization, not STAND/RING.

Exact91-file source revision:
2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5
(base6d2ae96 plus the reviewed D104 files; committed software ID recorded below).
ELF8be8768aca2990eafa1edabcff37b645c9beec51df7617db7324f228f672daf8.
ELF-ZSKeb1d2b5b7ddeb432ec453da12cf69b4e86f2bb61b2ca63b3e58df4819de5f852.
Independent source/target receipt: reviews/P2_runtime_inert_review_raw/target_2bd817c4.json.
Final guard/capture approval must also exist before invocation.

Scope: tools/board_tool.py flash bench/runtime_inert; default startup, MATCH0,
MOTORS_ALLOWED0, one checked build which must reproduce both reviewed hashes,
then exactly one CLI upload. Upload resets/restarts MCU; only actual Runtime
and checked inert motor callbacks run, with all sensors/services unavailable.
No native GPIO/PWM/ADC/I2C/UART/matrix/Bridge owner, network motion input, motor
capability or additional peripherals. No daemon/router/service action.

After200s, separately read exact fixed MEM-AP diagnostic and heap evidence with
reviewed runtime_capture.py. No halt/reset/write in capture. Do not silently
repeat upload or retry changed code. Keep raw failure if a guard or run fails;
collection success and experiment acceptance remain distinct. No P0/P1/P2 or
later human gate, full-app load, D103 reset, physical sensing or full800us claim.

Software/runrecord committed before upload: 1fa2a019b26dc1e7ff74e9491cca94477ce7f681.

Upload completed exit0 at2026-09-23T18:56:06.821827+00:00. Fresh checked
receipt49aaf6a759164599850e6407ad22092d reproduced both reviewed loadable hashes.
One MCU reset/upload only; observation window and separate capture follow.

Capture exit0; reviewed exact bytes confirmed, FROZEN/NONE and acceptancePASS.
200001epochs/zero misses; maxRuntime269us, maxRunner285us; no active outputs.
Board now retains this frozen inert2bd817c4 image. No further reset/upload/run.
