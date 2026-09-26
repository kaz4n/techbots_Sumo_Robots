# D231 source and host validation

PASS_HOST_ONLY: 21 focused Python methods, 576 fresh C++ model subprocesses and
51150 assertions passed. Both normal and ASan/UBSan variants ran; 581 total
compiler/model commands returned zero. The existing legacy suite ran all 12
methods. The FIFO suite ran its nine setup, ownership, byte, deadline, cancellation
and first-failure methods; unrelated full-stream replay/capacity and sketch
selection suites were not repeated. No board transport or target compile ran.

`P7_dump_first_failure_raw/host02/result.json` and `unittest.txt` retain completion.
`host02_receipts.tar.gz` contains every original harness command, stdout/stderr
and source-freeze receipt, with each archived member compared byte-for-byte to
its original. `receipt_archives.json` records the archive pins and counts.
The initial `host01` stopped before tests because this sparse worktree omitted
the tracked native_qtr header dependency; both compiler failures and the test
errors remain in its corresponding archive/result/text. Restoring the exact
tracked fixture headers resolved it. No production change was needed for that
environmental failure.

The added public record is exactly eight bytes. Existing NativeStatus values,
status returns, setup/refusal order, packet/clock/IRQ/ownership checks and poison
semantics remain. The new assertions prove partial packet offsets survive
terminal calls, direct setup refusal remains NOT_ATTEMPTED, cleanup ownership
loss is distinct from skipped context, and setup/runtime readback failures remain
distinct from verified cleanup. The real Transfer failure-cancellation path is
tested for READY_LOW, READY_ERROR, ownership loss and synthetic TIMEOUT, plus
failed cleanup readback and ordinary Transfer abort. The latter records CANCEL
with reason OK. Timeout is a fixture injection, not an explanation of D228.

Reproduction uses the two existing `tests/tooling/test_dump_uart_*.py` modules.
Load `NativeDumpTests` completely and `DumpUartFifoTests` excluding only
`test_actual_d116_payload_packet_replay_and_strict_receiver` and
`test_all_raw_capacity_slots_use_actual_formatter_and_native_packets` into one
serial unittest suite. Override each module's RAW to a fresh directory beneath
the D231 evidence owner before loading the suite. Run with WSL Python `-B`; the
modules retain their exact g++ commands and temporary-directory cleanup. All
relevant source, fixture and runner bytes are pinned in `host_closure.json`.

Independent source review precedes integration. Root owns any later target
compile, fit check, new ABI/capture plan or fresh run. No source-only change can
recover the already-lost D228 reason, prove runtime coherence or create physical
acceptance, motor authority or a phase gate.
