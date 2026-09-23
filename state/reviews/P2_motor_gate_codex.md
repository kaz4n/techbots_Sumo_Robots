# D-075 MotorGate software review

Date: 2026-09-23, Asia/Dubai. Baseline: `a9ee5b7`; contract/header commit:
`bc01d13`; reviewed the actual working-tree additions and changes.

Reviewer: separate fresh-context Codex agent using the same model as the
coordinator. This is not a different-model review. The reviewer implemented no
production code or tests, performed no board I/O, and owns only this report.
Read AGENTS, current PROGRESS, D-051/D-075, the MotorGate contract, relevant
BEHAVIOR/HARDWARE/FACTS, P2 prompt and REVIEW_GATE. The verified date precedes
the scheduled scope cuts and code freeze. No human gate is inferred.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed software scope.

## Verdict

PASS for D-075's checked-port MotorGate software, independent host tests and
compile-only probe. This is not GATE P2, native-adapter approval, physical R1
proof, a motor-run authorization or deployment acceptance.

## Safety and contract audit

- R1: initialization configures EN LOW and acknowledges LOW before configuring
  PWM. Every admitted transaction writes LOW, four exact integer PWM settings,
  settle, then optionally HIGH. Release capture requires the accepted current
  HOLDING/COUNTDOWN event with disabled zero output. READY cannot activate before
  the full configured 5,100,000 us hold. Cancellation/reset removes the anchor;
  completion survives later micros wrap. Time correctness retains the existing
  caller obligation to supply the actual successive decision timestamps.
- R6: this boundary consumes Robot-governed results; it does not implement a
  second governor. Existing Robot/governor code is unchanged. Either wheel at
  full magnitude additionally requires ATTACK, contact and current centered
  front perception. Period-based downward quantization is performed in double,
  then receipts report signed pulse/period settings. Default MOTORS_ALLOWED=0
  always sends LOW and four zeros. No runtime override was added.
- Fresh=false is a true no-I/O/no-consumption operation. Zero, repeated and
  regressing fresh tokens latch inhibition; increasing tokens are consumed even
  for fault outcomes. Reset preserves token high-water and never enables.
  STOPPED remains latched; successful ordinary STOP receipts truthfully report
  disabled zero settings. Only explicit successful reset permits reuse.
- Every failed checked operation leads to bounded LOW/all-four-zero/settle
  cleanup, including attempts after a cleanup failure. No HIGH retry occurs.
  Faults persist; actual callback failure upgrades the recorded fault to IO.
  Failed receipts remain invalid even when cleanup succeeds. The clock is read
  after the transaction; whole-tick duration remains invalid for the scheduler.
- Active zero-demand brake intentionally differs from disabled inhibition.
  Direction selection never requests both channels of a side simultaneously;
  all PWM settings must be acknowledged as latched before HIGH. The required
  settle semantics are an adapter obligation, not proved by a mock callback.
- No new I/O, allocation, remote command path, Bridge call or unbounded loop is
  introduced in the production module. All new loops have at most four iterations.
  Port callbacks must themselves meet the separately documented bounded-work,
  exclusive-ownership, error-reporting and lifetime contract.

## Independently reproduced checks

The reviewer ran the existing coordinator-built binaries in WSL /dev/shm,
without modifying their source, tests or build configuration:

| Configuration | MotorGate cases | Assertions | Result |
|---|---:|---:|---|
| Default-disabled normal, MotorGate filter | 37 | 3,993,226 | PASS, exit 0 |
| Host-only MOTORS_ALLOWED=1 normal | 37 | 3,796,846 | PASS, exit 0 |
| Default-disabled ASan/UBSan, MotorGate filter | 37 | 3,993,226 | PASS, exit 0 |
| Host-only MOTORS_ALLOWED=1 ASan/UBSan | 37 | 3,796,846 | PASS, exit 0 |

The filtered default runs intentionally skip 993 unrelated cases. Enabled runs
skip none. Neither sanitizer rerun produced a diagnostic. The reviewer also
independently ran `test_motor_gate_probe.py`: 3 tests PASS in 8.165 s, exit 0.
Those tests exercise both inert probe configurations through setup and 10,000
loop calls, and reject all six upload combinations before target lookup.

Inspected coordinator raw normal/sanitizer full-suite receipts: each reports
1,030 cases and 20,982,541 assertions, zero failures/skips, exit 0. These complete
suite runs are coordinator evidence, not additional reviewer reproductions.
The final coordinator tooling receipt reports 381 tests PASS in 177.779 s,
exit 0; its three new probe tests were independently reproduced as above.
The 37 new cases cover 10,000 seeded noisy releases, exact deadlines/wrap,
cancel/STOP/reset/replay, finite/range/enum validation, every checked failure
position, cleanup failures, quantization, actual Robot feedback and next-tick
inhibition following a failed receipt.

The preserved first test draft failed to compile because of no-exception
doctest REQUIRE use and unparenthesized logical expressions. Diff inspection
confirms unchanged assertion predicates with explicit abort on a failed
prerequisite, plus additional coverage. No established locked test was weakened.
All 14 pre-existing locked tests and the existing core/config/app files (38
paths total) are byte-identical to baseline blobs. `tools/board_tool.py` has no
logical Git diff; its working CRLF differs from the baseline LF blob, so raw
byte identity is not claimed for that file.

## Target evidence reviewed

Read the coordinator's compile command receipts and
`state/analysis/P2_motor_gate_raw/target_elf_symbols.json`, including six ELF
records, retained symbols, constructor and transaction disassembly. Both
configurations use source digest
`807b576899bc8c9f9703e284d2d43ab1ab75a9eeb36e3b006ae53220cde79965`.
The reviewer independently recomputed that staged source digest and checked
the staged MotorGate/config/probe bytes against the reviewed working files.

| Configuration | Program bytes | Compiler global/RAM figure | Main ELF SHA256 |
|---|---:|---:|---|
| Default startup, MATCH=0, MOTORS_ALLOWED=0 | 76,220 | 31,276 | `22def662c9920d0a5ad5323e0408e7aa4f1c5dccaf9a5e770ce8bb52c5577b11` |
| Immediate startup, MATCH=1, MOTORS_ALLOWED=1 | 76,692 | 31,612 | `c87975a9e2e79f07e41773f4a43bbe5037d58b1fbd179fe52c4a87ed957e9415` |

Both command receipts explicitly contain --compile-only and return 0.
MotorGate begin/apply/reset/validation/inhibition/transact methods are retained.
The default transaction's target code has no HIGH branch; the enabled image
retains quantization and conditional HIGH only after the settle callback.
The MotorGate constructor only initializes/copies object state and calls no
port callback. The final extraction includes the plain C setup/loop symbols:
in both images setup is a store plus return, and loop is only a return. This
agrees with source and independent host executions. The deliberately null Port
is not a fabricated successful hardware adapter.

The initial target-symbol output/command-receipt filename collision was corrected
to the disjoint `target_elf_symbols.json` artifact. The read-only extraction
retry succeeded; it was not a recompilation, upload or MCU execution.
The initial symbol-selector snapshot is also preserved separately; its missing
plain C setup/loop names were corrected by read-only extraction, with the final
`target_symbols_complete.json` receipt returning 0.

## Existing inert-source guards

The reviewer independently reconstructed all five baseline staged byte streams
from a9ee5b7, matching every previous approved hash exactly. Current streams have
no changed/deleted existing staged byte: their only additions are
`src/hal/motors.h` and `src/hal/motors.cpp`. Neither added module creates global
objects or initialization I/O. Approval is limited to these exact replacements:

| Existing inert sketch | Approved replacement SHA256 |
|---|---|
| p0_matrix | `a484e419fb89956f52643e46750e20c494f95b14920b54184d7fe76c32fb322c` |
| p0_timing | `d5336417d5fd1431d3668c2befcd6de4aa3d4f563598828a09c4a90a9a24c279` |
| p0_adc | `611d9ecfbc82c15ae1c811e6f75a2e47cd6cafe5c2fab0395e0665589820e3ac` |
| p0_gpio | `36c3a02cac3d113e165dad28c010f2f4cd7b4ca53f9d725b9e8e6ca421d77686` |
| p0_qtr | `e7f6cd60871e82ac05d86d01a0d9adf9fb027bae9a033240b7d7fa005369d588` |

The final manifest matches those values. No upload allowlist expansion follows;
the new probe remains rejected for upload. Reviewed production/test hashes:

- motors.h: `02b906db1e08208e5d954d126b803cc1bfdba4519142a195d46be9b614defb92`
- motors.cpp: `72edea8ec9896c4914c188a86d7eeb20d18b88be705528ee7fb7893929cb58a2`
- test_motor_gate.cpp: `54609648fb0ba5f9c559767b9ede247b5e14d91f3c630f571514708584187821`
- compile probe: `3a821638924132c01de3be889e3d65b6e8019d2ab023bb89791a3f47c8e7c5f5`

## Limits and next action

No native pin backend, pin approval, EN pull-down measurement, electrical truth
table verification, PWM waveform/latency, actual settle timing, full-firmware
RAM fit, loader/free RAM, whole-tick WCET or physical motor run is established.
The inherited platform/Bridge constructors and runtime paths remain unqualified.
The next hardware-facing step needs a separately validated native adapter and
the existing physical/human approvals; this review grants none of them.
