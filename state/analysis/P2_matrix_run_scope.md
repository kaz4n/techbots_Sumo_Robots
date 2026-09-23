# D088 bare UNO Q display run1

Authorization: user2026-09-23 explicitly reports bare UNO Q/no external sensors
and permits running tests on it. Earlier authority states no other connected
hardware. Scope: one inert built-in-matrix diagnostic, not a motor run or a gate.

Target ADB serial2629958581. Sketch bench/ui_matrix, normal startup,
MATCH=0/MOTORS_ALLOWED=0. Exact staged source SHA256:
e50c6da38bba5131e426d8c076e7aa7c8aad5961f60a6eb1387b1f2412aab6af.
Source contract commit8fd11dd; implementation commit385c46c,61sourcefiles byte-identical to target and Git.
Review approval: P2_matrix_raw/review/approved_inert_sources.json.
ELF14023aa1e0b788edbbfe92e6b6b8aeed0afff6e0b329360af212c9df3688a7ab,
upload-format binary6de9d536572132fc8f4fa1d7962aecf15a479da7564221df4512944db2066a69,
both80592bytes. Metadata and current61-source map retained under P2_matrix_raw.

Actions: normal board-side Arduino CLI compile/upload through reviewed board_tool;
then new exact-pinned capture wrapper using unchanged P0 read-only MEM-AP helper.
No external sensor/ADC/GPIO/PWM call, no Bridge motion input. Upload may reset the
MCU as part of deployment. Capture has no memory write/halt/reset command. It
verifies full deployed loader/sketch bytes, bounded LLEXT identity and uiBench
layout before interpreting two bounded samples; maximum120s/16reads, no retry.

Normal startup's audited loader ends its animation before sketch setup. This
isolated sketch is the only project matrix owner. That source ownership assertion
and caller grant are not an optical or IRQ timing measurement. Inherited platform
initializers/Bridge loop hook remain F091; measured complete-control800us and
clock accuracySC-AJ remain open. No other sensor connection is requested.

Expected report: successful initialization/submission remains UNCONFIRMED at the
native API level; advancing submissions supports actual loop progress, not visible
pixels or calibrated timing. Synthetic scenes intentionally mark sensors/battery
unavailable. They are not competition observations. Any upload/identity/status/
deadline failure is retained and stops that invocation without fabricated success.
