# P0 independent matrix counter-analysis test author

Date: 2026-09-22, Asia/Dubai.

Objective: verify the supplied pure `analyze_counter(first, second)` contract
without reading `tools/p0_matrix_capture.py`. Owned files are
`tests/tooling/test_p0_matrix_capture.py` and this report. Existing tests and all
production files remain unchanged; no hardware operation or implementation read
was performed.

Nine focused cases cover exact integer uint32 observations, ordinary progress,
wraparound with preserved original observations, one-count progress, the maximum
accepted modular delta 0x7fffffff, zero change, backward movement and the rejected
half-range 0x80000000 boundary. Both argument positions reject booleans,
nonintegers, int subclasses, negative values and values above uint32 before any
modular conversion. Success requires exactly the documented dictionary fields
first/second/advance with integer values; malformed observations raise ValueError.

Quiet import is guarded against subprocess calls, socket creation/connections,
os.system and interactive input. A non-run argv sentinel plus captured empty
stdout/stderr also detects accidental CLI/main execution. The tests never invoke
capture, discovery, debugger attachment, upload or a board process.

Static handoff: nine cases; runtime execution awaits coordinator/worker freeze.
These arithmetic tests cannot verify the identity or location of a hardware
counter, target artifact/profile restrictions, actual elapsed time, visual matrix
output or a P0 gate. No additional CLI behavior was assumed because that public
contract was not part of this bounded assignment. Next action: coordinator runs
the unchanged pure suite and records verified evidence before physical capture.
