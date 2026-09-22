# P0 fixed counter transport contract — 2026-09-23

Selected under D-051/D-062 for P0 task 0.2 only. This is an inert diagnostic,
not the P2 recorder, a new motion channel, or a relaxation of R3/R4. The current
matrix image remains installed until the complete new staged source and target
binary have independent review. Preserve the existing upload hash guard.

## Public packet contract (before implementation/tests)

`bench/p0_matrix/src/counter_packet.h` defines a fixed-storage `p0::CounterPacket`.
It has exactly one 36-byte message slot and states IDLE, BUSY, FAULT. No clock,
allocation, I/O, reset method, retries or variable-length payloads belong here.
The constructor takes a timeout in microseconds; zero or >=2^31 starts FAULT.

- `submit(counter, now_us)` succeeds only from IDLE. It creates the MessagePack
  notification `[2, "mon/write", ["P0 counter=dddddddddd\n"]]`, using ten decimal
  digits with leading zeros for the entire uint32 range. It anchors the deadline
  at submission, sets cursor zero and becomes BUSY. BUSY/FAULT refusal changes
  neither bytes, cursor nor anchor; it never queues a second packet.
- `nextByte(out)` returns the current byte only when BUSY and cursor <36;
  otherwise returns false and leaves out unchanged. It does not advance state.
- `accepted(count)` is valid only when BUSY with an unsent byte and count exactly
  one. It advances one byte; accepting the last byte still leaves BUSY because
  FIFO acceptance is not physical transmission completion. Every other call
  latches FAULT. A failure cannot restart a partly transmitted stream.
- `complete()` succeeds only when BUSY and all36 bytes were accepted, then
  returns to IDLE. Other calls latch FAULT. The target adapter may call this
  only on a subsequent UART transmit-complete interrupt after the last byte.
- `service(now_us)` latches FAULT when BUSY and unsigned elapsed time >=timeout.
  Strictly earlier service leaves state unchanged; wrap-safe intervals must be
  serviced at least once within2^31us. IDLE/FAULT service is inert.
- `fail()` latches FAULT from any state. `status()` and `remaining()` are read-only;
  remaining reports unaccepted bytes while BUSY and zero otherwise.

`PacketStatus` and the above method signatures are the independent-test surface.
Tests must derive expected MessagePack/text bytes independently, including0,
decimal boundaries andUINT32_MAX; busy refusal, retained partial data, final-byte
versus complete distinction, timeout exactly/adjacent/wrap, invalid operations
and permanent fault. Compile the real opaque .cpp in an isolated host runner.

## Target adaptation prerequisites and intended limits

Use only the existing internal router UART, from installed devicetree, with its
installed115200/8N1/no-flow-control configuration. No header pin or wiring change.
Default startup already waits for Linux-ready; Immediate matrix upload remains
forbidden. Never start Bridge/Monitor/Serial2, install an inbound callback, or
send a request expecting a response. The required RouterBridge global stays
unstarted; verify the exact linked constructors and loop hook before upload.

Installed audit found this UART is deferred-initialized. Call the existing core
`zephyr::arduino::init_dev_apply_pinctrl` once in setup, check its result and device
readiness, then validate the installed configuration. This initializes only the
existing devicetree internal UART route. Its driver has TEACK/REACK waits, so it
is forbidden after setup; it is not a bounded runtime send API.

The adapter public header exposes setup, counter submission, deadline service
and a copied diagnostic snapshot. Initialize once only; failed setup or transmit
is terminal for the sketch lifetime. Saturating submitted/completed/refused
counters distinguish software admission, physical TC observation and refusal.
The final accepted byte receives one subsequent TC interrupt before completion;
there are at most37 callbacks per successful36-byte packet. Disable on unexpected
readiness/completion/zero progress. No receive callback or retry is installed.

One callback handles at most one FIFO byte per invocation. Submit/ISR/service
share state under a bounded interrupt critical section. Disable TX IRQ at idle,
error or timeout; disable RX/error IRQs at initialization. Do not busy-wait for
UART, Linux, a mutex, a response or queue capacity. Timeout is100000us, a P0-only
value in config.h, not a B16 behavior change. A fault is terminal for this test;
do not restart after a partial packet or claim stream resynchronization.

Installed source/binary audit must first establish exclusive ownership, actual
API exports, finite driver paths and critical-section assumptions. In particular,
STM32 CR1 LDREX/STREX retry loops require a justified bound; merely wrapping an
unbounded routine does not satisfy R4. If this cannot be established, implement
and host-test the packet primitive only; no adapter upload or rule waiver.

Evidence levels stay separate: packet tests, target compile, inert upload,
actual received counters, and timing under this workload. The Linux listener
has accepted a receive-only probe with zero payload; that is not a counter round
trip. Notification enqueue/transmission has no delivery acknowledgment. P0's
optical/cold-power and full robot WCET acceptance remain separate.
