# D231 native UART first-failure review

FINAL PASS - source and focused host scope. No open material finding.

Reviewed independently on 2026-09-27 against D231 and the frozen contract in
the isolated first-failure worktree. The reviewer changed only this report and
ran no tests, target commands, upload, reset or peripheral operation.

## Frozen scope

Production changes are limited to `src/hal/dump_uart_unoq.h` and `.cpp`.
Reviewed the two changed register-model case files, their existing tooling
runners, and the real `Transfer::fail`/`abort` call path used by the new fixture.
No locked test, configuration, pin, grant, motor policy or transport changed.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `src/hal/dump_uart_unoq.h` | 4244 | `5a88a26ac50d7765fff08895ee7e4badb88af0b1a24b32660249506cc105a693` |
| `src/hal/dump_uart_unoq.cpp` | 19862 | `0ad432cf80eb99db2582b53a0da8916743d36b4e01d970e6a7c71c55f065b76f` |
| `state/analysis/P7_dump_first_failure_contract.md` | 3014 | `8425c70888095ce836b5f5e6347ac6963461041d5bf0dd8125ae4891706067c9` |
| `state/analysis/P7_dump_first_failure_validation.md` | 2760 | `1c49607c765292704424c8654b40dea7564bb877e9176185f13a68aa84eac7d8` |

The flat `state/analysis/P7_dump_first_failure_raw/host_closure.json` has SHA-256
`8f80ed919f0117045b9cbef281c6795848cd6e5a660600f7bbdeafa5d5c5e97e`.
Independently recomputed all 15 pinned sizes/hashes with zero differences.

## Source findings

The appended record is statically constrained to eight bytes. Existing
NativeStatus values, public status behavior and existing field order are
preserved. The const accessor performs no observation. Packet offset, packet
size and payload size are copied before poison clears them; their existing
79-byte/64-byte bounds fit the stored uint8_t fields.

The first non-NONE site latches reason, site and progress. Later ready, write,
cancel and begin calls cannot replace the record. Ordinary cancellation is
explicitly OK/CANCEL; repeated begin has its own site. Immediate setup refusal
retains NOT_ATTEMPTED cleanup even if cancellation follows, as specified.

Cleanup classification uses the existing single ownership evaluation and CR1
readback. Context/ownership refusal still avoids foreign register writes;
verified inhibit and failed readback remain distinct. Diff inspection found no
added peripheral read, clock call, loop or retry, and no reordered admission,
IRQ, packet or deadline check. The existing fail/abort/poison status sequence
is preserved, including the later POISONED status from Transfer cancellation.
Extra diagnostic stores are not a target timing measurement.

## Host evidence

`host02` completed 21 methods with no failure, error or skip: all 12 legacy
methods and the nine focused FIFO methods. Inspected the actual compiler and
model receipts: 169 legacy commands and 412 FIFO commands all returned zero
with empty stderr. They contain four normal/sanitized model builds, one syntax
check and 576 fresh model executions. ASan and UBSan were enabled in both
sanitized variants. Full stream/capacity and sketch-selection suites were not
repeated and are not claimed by this review.

The FIFO fixture links the real recorder, formatter, Transfer and native UART
implementation. Its new cases exercise Transfer::step -> native failure ->
Transfer cancellation for READY_LOW, READY_ERROR, ownership loss, a synthetic
deadline failure and failed cleanup readback, plus ordinary Transfer abort.
Assertions distinguish submitted packet progress from zero acknowledged
Transfer bytes and prove retention after repeated terminal calls. Legacy
partial-packet cases cover skipped context, lost ownership, register mismatch
and verified cleanup. Existing model checks retain packet, clock, IRQ,
foreign-write, FIFO room and completion invariants. The copied FIFO HAL,
Transfer and changed fixture hashes match the reviewed source.

`host01` preserves both setup failures caused by missing tracked sparse-worktree
header dependencies; it ran zero methods. Restoring those dependencies did not
change production behavior. Independently compared all four host01 and all 415
host02 archived receipt members with their retained originals: exact matches.

## Boundary and next action

Accept this diagnostic source change and its focused host evidence for
integration. Target compilation, fit and any later native attempt remain
separate root-owned work under the existing guards. A future observation must
derive the new record's layout from its exact current ELF; the prior image's ABI
does not describe this appended field. Mechanical new-image binding does not
require another review of unchanged capture machinery.

This change cannot recover D228's already-lost original error. It establishes
neither a timeout explanation nor a UART repair. The record is non-atomic;
packet progress does not prove shifted, received or acknowledged wire bytes.
No motor permission, physical acceptance, phase gate or delivery success follows.
