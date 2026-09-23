# D090 independent test-author handoff

2026-09-23. Objective: verify the frozen dump/session/receiver/native contracts
using public headers and pinned installed declarations, without reading D090
production implementation bodies. Compiler diagnostics and failed-test traces
were used only to resolve fixture/API mismatches. No hardware action or commit.

Owned additions: tests/test_recorder_dump.cpp; tests/fixtures/dump_fixture.h,
dump_main.cc, dump_stream.cc, dump_uart_native/**; tests/tooling/test_dump_match.py
and test_dump_uart_unoq.py. Existing tests/config/build files were not modified.

- Strict C++ syntax passed before scoped linking: syntax.log and syntax2.log.
- C++ final scoped result: 26 cases, 4052 assertions PASS in scoped3.log.
  Actual Robot -> MotorGate -> AttemptRecorder -> Transfer; STOPPED refusal,
  caller-owned reset with retained evidence, genuine LOG_DUMP gestures, literal
  stream and independent CRC, all states/faults, partial/PENDING, current-context
  age, token/time order/wrap, source identity, exact deadlines, complete-row ACK
  counters and 5001-frame/4096-event source. Root owns full normal/sanitizer suites.
- Receiver final: 33 methods PASS, 4.736s, python5.log. Includes 18 original
  strict-config checks under additive D088/D089/D090 expected declarations,
  actual compiled C++ stream -> Parser -> validated published CSV, every split
  and truncation, exact raw bytes, hostile protocol/path inputs, maximum rows,
  partial evidence, receive-only mocked transport outcomes and atomic no-replace.
- Native final: 11 methods PASS, 4.368s, native_suite2.log. 154 normal/sanitizer
  scenario processes, 4870 native assertions, 157 commands with zero failures.
  Aggregate native_commands.jsonl retains all runs; native_freeze.jsonl records
  public contract/header/fixture hashes. Exact 79-byte packet, PRIMASK, TXE/TC,
  80us/100ms boundaries, wrap, context/IRQ/DMA, readiness, 16 initial metadata/
  clock failures, 21 live corruptions, cancel/poison and no receive-register use.

Retained initial failures: scoped.log contained a 48-digit literal fixture where
the 25-byte contract requires 50; corrected only the missing byte00. python1.log
used capturefailure1 for symlink input, clarified as preflight invalidargument2.
python2.log used unspecified receive_mode=live, clarified offline/ssh/adb.
python4.log expected timeout instead of the frozen timeout_seconds outcome key.
Native compilation receipts retain missing stub API declarations; the initial
healthy DT_PROP stub incorrectly supplied1 for current_speed instead of115200.
native_suite1.log expected beginOK on a ready-pin read error; corrected to the
contract's checked GPIO failure, while LOW remains an allowed setup condition.
No failed result was hidden, and no production failure was repaired by weakening
a contract expectation. The native 78-to79 packet-capacity correction was made by
the coordinator/implementation owner from literal MessagePack arithmetic.

Limitations: synthetic host sources and modeled registers do not prove physical
origin, MCU execution, UART delivery/recovery, RAM/WCET, external hardware,
complete application integration, or a human phase gate. Root's next action is
full normal/sanitizer, exact target/source validation and independent final review.
