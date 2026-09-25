# Actual static diagnostic ABI: file evidence and offline interpretation

FILE-OBSERVED / OFFLINE-INTERPRETED at 2026-09-25T19:19:17.201789+04:00. Original native invocation is FAILED,
not relabeled successful. Its four file-tool children succeeded; one local parser
rejected GNUreadelf's hexadecimal size token0x29708. That equals169736, exactly
the GDB Runner size. No board repeat was necessary. Owner native_abi_static01 is
consumed; original helper, command streams and local_result.json remain unchanged.

At reviewed90f2815c, actual --check-only exit0/5493Windowsunits; one --execute
exit1/1transport. Four children exit0/reaped/no timeout/empty stderr,12filepins plus
board identity closing PASS and local closing PASS. Invocation and source receipt:
[P7_app_motor_fault_compile_raw/native_abi_static01_invocation.json](P7_app_motor_fault_compile_raw/native_abi_static01_invocation.json).
No MCU access, upload/reset/compiler or firmware binary transfer occurred.

New interpreter6a990871 normalizes only the exact unique diagnostic symbol's
size spelling in a private copy, then uses the unchanged original layout parser.
It pins all five retained input snapshots and rechecks them afterward. Original
and projected stdout hashes/token are retained. Actual command
`python -B state/analysis/P7_app_motor_fault_compile_raw/interpret_static_abi.py --interpret`
exit0, empty stderr. Worker16controlled format/packet checks passed; separate
source review PASS. Root saved exact stdout as
[abi_static01_interpreted.json](P7_app_motor_fault_compile_raw/abi_static01_interpreted.json).

Actual ET_EXEC .bss symbol diagnostic is0x20013960,169736B/alignment8,
ending0x2003d068 within the validated zero span.19size/alignment pairs (18types
plus bool) and10member offsets are recorded. Six useful future capture windows:

| Window | Address | Runner offset | Bytes |
|---|---|---:|---:|
| trace_.report_ | 0x2001398c | 44 | 2128 |
| report_ | 0x2003cbd0 | 168560 | 1168 |
| runtime_.report_ | 0x2003c520 | 166848 | 600 |
| runtime_.transaction_.report_ | 0x2003bb38 | 164312 | 504 |
| runtime_.transaction_.previous_ | 0x2003bd30 | 164816 | 48 |
| runtime_.transaction_.gate_ | 0x200142b0 | 2384 | 88 |

These six windows total4536B per observation. They include the pre-abort snapshot
inside Report; avoid reading the166376B Runtime and its recorder as a whole.
Independent review also compared all10offsets with the nested actual GDB ptype
layout. [Actual review](../reviews/P7_app_motor_fault_abi_actual_review.md) distinguishes
raw query success, original local parser failure and offline interpretation.

Next: focused new-file entry/global-initializer disassembly using these retained
symbol addresses, then separate exact-artifact inert upload/capture preparation.
Do not reuse old application addresses or dynamic relocation. No live memory,
startup result, original IO-fault resolution, electrical/RAM/WCET/physical/human
acceptance follows from file layout. D184 is still the last uploaded image.
