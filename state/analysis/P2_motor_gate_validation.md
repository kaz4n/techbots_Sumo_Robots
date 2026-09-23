# D075 MotorGate — software verified, physical B4 pending

2026-09-23 Asia/Dubai. Contract/header bc01d13; receipt clarification447ff94.
Latest user explicitly authorized advancing software using untested hardware
assumptions. No physical fact, PINMAP, EXPLAINED, phase gate or motor permission
has been asserted. This completes the checked MotorGate boundary, not B4's real
driver/stand acceptance or application integration.

## Implementation and independent checks

`src/hal/motors.cpp` implements the sole checked write boundary. EN is taken LOW
before channel writes; activation follows successful four-channel settings and
bounded confirmed settling. It independently enforces the accepted-release hold,
current permission/state, token freshness, finite duties and full-duty contact.
Callback failures latch inhibition, attempt every cleanup channel and retain
invalid application receipts. Successful receipts report quantized cycle ratios.
Default MOTORS_ALLOWED0 cannot activate. No pins, carrier frequency or behavior
tunables were changed, and no concrete UNO Q Port has been supplied.

Separate test author used the frozen contract/public headers without reading
implementation. New locked file has37 cases including10000 fixed-seed logical
release streams, adjacent deadlines, wrap, actual Robot feedback, active braking,
reversal, all callback failure positions, default inhibition and truthful failure
receipts. Existing14 locked files and core/config/app remain byte-identical to
baselinea9ee5b7. New tests become established locked tests with this commit.

| Validation | Actual result |
|---|---|
| Full default C++ suite |1030cases /20982541assertions PASS,0fail/skip |
| Separate host-only enabled boundary |37cases /3796846assertions PASS,0fail/skip |
| ASan+UBSan, both configurations |same counts PASS, no diagnostics |
| Full controlled tooling suite |381tests PASS,177.779s test duration,exit0 |
| New probe host tests |both0/1 startup+10000loops inert; six upload combinations rejected before target lookup |
| Fresh separate same-model review |state/reviews/P2_motor_gate_codex.md; independent scoped reruns and exact manifest/ELF audit |

Exact argv/start/end/returncode and full output are in `P2_motor_gate_raw/`.
`P2_motor_gate_host_run.py` configures/builds/tests within one WSL lifetime in
/dev/shm because disk was full and a prior RAM build disappeared between calls.
These CMake/direct-doctest runs are equivalent host validation; no desktop runtime
measurement proves the MCU tick budget. Review's filtered default subset reports
37cases/3993226assertions with993 intentionally filtered, not skipped in full runs.

## Real target compilation (no upload/reset/run)

Actual USB serial2629958581, board CLI1.5.1/corearduino:zephyr1.0.0 refreshed.
`tools/board_tool.py flash bench/p2_motor_gate_compile --compile-only` and
`--match --compile-only` both exit0 on board Linux. Exact staged source:
807b576899bc8c9f9703e284d2d43ab1ab75a9eeb36e3b006ae53220cde79965.

| Configuration | Program bytes | Compiler-reported global bytes |
|---|---:|---:|
| MATCH0/MOTORS_ALLOWED0/default |76220|31276|
| MATCH1/MOTORS_ALLOWED1/Immediate |76692|31612|

Probe setup only publishes the retained function address; loop is empty. Its
global Gate has a null/unusable Port and is never invoked. Linux-only nm/objdump
receipts in target_elf_symbols.json preserve six artifact hashes, methods, startup
and loop; no debugger attachment or MCU execution occurred. Existing inherited
Bridge constructors/hooks remain as F091: these builds do not qualify runtime.
The small probe's size is not complete-firmware RAM or WCET evidence.

Fresh reviewer independently approved the exact five old inert manifest updates.
`P2_motor_gate_inert_manifest_proposal.json` proves only motors.h/.cpp additions;
every previous staged file remains unchanged. No upload allowlist expansion;
new probe upload always rejected. No motor-enabled firmware was flashed.

## Failures retained and next work

Initial doctest draft failed compilation on exception-disabled REQUIRE and an
unparenthesized complex expression. Original test draft/build output retained;
test author repaired framework syntax/prerequisites without changing predicates,
and strengthened coverage. First actual runtime tests passed; no production fix.
`P2_motor_gate_failure_analysis.md` also records infrastructure/receipt repairs.

P2 B4 still needs an actual checked UNO Q backend with verified pin ownership,
timer periods and bounded preload settling, electrical/pull-down checks, measured
write/fault paths and fresh per-run human authorization for physical motor work.
No success stub may replace the missing backend. Application remains inert.
Continue permitted P2 software development with B1 opponent-input HAL contract
and checked installed GPIO audit; preserve raw polarity for Robot's existing
debouncer, distinguish read errors from detections, and compile-only until the
physical connection is accepted. P0/P1 human acceptance remains independently pending.
