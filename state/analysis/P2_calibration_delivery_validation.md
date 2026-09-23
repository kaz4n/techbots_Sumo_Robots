# D105 actual Runtime calibration delivery

2026-09-23 Asia/Dubai. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED.
Separate source review PASS; target-capacity BLOCKER remains pending D106.

The actual ordinary Runtime commit pulse now owns one bounded, non-MATCH export
attempt per committed bank. Both default-off grants are required. Current real
MotorGate receipt, inhibited QTR_CAL context, source evidence, bank identity,
adjacent tokens and actual clock observations govern progress. Recorder and
calibration share the existing output owner with cancellation/poison preserved.
No extra persistent text buffer, dynamic allocation, remote command or config
change was added. MATCH excludes mutable export state and execution.

Independent spec/public-interface author tests passed26 cases/8441 assertions
in both normal and ASan/UBSan non-MATCH builds; MATCH passed3/342 in both modes.
An isolated short-total-deadline sanitizer profile passed1/47. Two actual host
eight-request calibrations produced exact snippets that round-tripped through
the strict receiver. Those are synthetic source fixtures, not physical readings.
Coverage limits and the two reviewer-approved fixture corrections are retained
in `P2_calibration_delivery_raw/author/validation.md`, `coverage.md`,
`fixture_correction.md` and original failed-run receipts.

Root full host and sanitizer builds passed both CTest targets with all established
assertions unchanged. Command/status evidence is in `P2_app_build_raw/d105_*`:
full_host_refactor, sanitize_build and sanitize_test. Existing standalone Runtime
harness changes only add new exporter/formatter dependencies; no locked test,
old assertion or config value changed.

The separate same-model reviewer independently passes27 cases/8478 assertions
normal and ASan/UBSan for non-MATCH MOTORS_ALLOWED=0 **and**1, plus full host tests.
It reproduced the initial Gate-cleanup ordering defect, verified the unchanged
regression after correction, and approved final source. Read
`reviews/P2_calibration_delivery_review.md` and raw/source_review_summary.json.
This is separate-context scoped review, not cross-model or human gate approval.

Final D105 source c05916c6 (89 exact files) compiles on the installed UNO Q core
with payload258324 bytes. Exact ELF/loader audit finds peak263112:968 bytes over
the262144-byte pool. Initial4c3487f4 evidence preserves the earlier1032-byte
deficit. Compile success is not loadability; default/Immediate/MATCH acceptance
awaits the separate byte-preserving D106 pin-table optimization. No D105 upload
or native UART/calibration measurement occurred. The MCU remains frozen D104.

Receiver-only scope was already committed36ae9bc; contract/API0d38be9 and
clarifications4778ced remain authoritative. No human phase gate passed.
