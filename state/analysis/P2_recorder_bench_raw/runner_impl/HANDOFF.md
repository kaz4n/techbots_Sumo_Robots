# D091 Runner implementation handoff

Owned production edits are bench/recorder_inert/src/recorder_bench.cpp and only
private declarations/members in recorder_bench.h. Public API, 256-byte Report,
296-byte Diagnostics, existing tests, config, build, native HAL, wrapper and
state ledgers are unchanged by this worker. Compile-time inert guards use the
actual config macros MATCH == 0 and MOTORS_ALLOWED == 0.

The pure C++ Runner owns the actual Robot, MotorGate and AttemptRecorder. The
inert Gate port accepts only zero pulse/disabled EN; all active attempts are
counted and rejected. Five configure calls only count software callbacks. Its
unit PWM period represents no timer or physical signal. Clock readings are the
only external callback; no Arduino, peripheral or transport API is included.

A monotonic bounded-forward clock schedules at most one real tick per poll,
retains missed slots/lateness and never catches up. Every startup button stage
starts on its first actually observed tick and lasts debounce plus four ticks.
Real Robot START-release evidence starts the 200-second age. STOP is locally
requested at that age; the source must seal its deferred frame within BTN_LONG_MS.
Applied/timing feedback comes from the real inert Gate and the callback clock,
with runner-only timing explicitly excluding the wrapper/diagnostic publication.
A sealed source is traversed in insertion order, one retained row per advancing
poll. CRC32/ISO-HDLC includes each frame's 25 bytes then status byte, followed by
each eight-byte event. Repeated clock values do no work, including checksum.

Report copies every AttemptSummary, FrameBuffer and EventBuffer loss/status
field plus source identity/counts. Loss alone never aborts. elapsed_us records
actual sampled age since accepted release through checksum completion; stop_us
minus release_us separately identifies the recording window. Terminal polls do
not call the clock or mutate evidence. Reentry causes permanent failure; the
first failure reason remains frozen. poll-before-begin cannot revive via begin.

Validation: runner_impl/run_smoke.py compiles the actual core/hal Runner pipeline
with strict C++17 warnings-as-errors, exceptions/RTTI disabled and both inert
macros zero. Current smoke_receipt.json captures exact command/source hashes and
success. The deterministic local host clock yielded release69000us,
stop200069000us (200 seconds later), 200070 real Robot steps, 5001 retained frames,
8 events, 5009 checksum rows, CRC4157801787, GO observed, no recorder loss, no core
fault and zero active PWM/EN callbacks. Gate STOPPED6 is the expected final latch.
Older receipts remain alongside the final receipt.

These are host synthetic checks, not an actual MCU duration, hardware acquisition,
physical motor gate, UART delivery, allocator/stack headroom or full800us WCET
qualification. Independent author tests, final target compile/link inspection and
fresh inert-run approval remain owned by the root. No upload/reset/daemon/native
hardware operation or commit was performed by this worker.
