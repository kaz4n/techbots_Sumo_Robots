# D103 independent test-author final handoff

2026-09-23. Frozen C++ source and both new fixtures still match `freeze_07.json`.
No implementation body was read. Existing tests, config, locked tests, shared
ledgers and hardware were not changed. The parent owns host build-list changes.

## Result

| Copied config / motor policy | Normal | UBSan | ASan + UBSan |
|---|---|---|---|
| Production unconfigured / 0 |9 cases,403 checks PASS|9/403 PASS|Parent full regression scope|
| Production unconfigured / 1 |9 cases,403 checks PASS|9/403 PASS|Parent full regression scope|
| Synthetic configured / 0 |34 cases,6132 checks PASS|34/6132 PASS|34/6132 PASS|
| Synthetic configured / 1 |34 cases,6139 checks PASS|34/6139 PASS|34/6139 PASS|

All six configured stream exports separately passed the strict receiver: actual
GO -> STOP -> real final tail/SEALED -> genuine local reset -> actual menu
LOG_DUMP, with exact pre-reset retained frames/events/summary/status/loss bytes,
session/epoch/CRC, one-byte fragmentation, and offline no-overwrite publication.
No fixture reset or manually seeded attempt supplied authority.

Normal and UBSan matrix receipts: `final_matrix_results.json`, runs
`run_1790187758637020914` and `run_1790187758638920013`.
Additional ASan+UBSan receipts: `final_asan_results.json`,
`run_1790187861812628252`. Every compiler/execution command has an exit code,
stdout/stderr, source hashes and output hashes. Production is copied opaquely to
`/dev/shm`; only copied config receives synthetic A1 windows. No live config edit.

Source: `tests/test_app_service_reset.cpp` SHA256
`e3b4521085cf471a1fbe71434b3968ea0e62dd19d0fa6c6a47546ef0b2c212ba`.
Fixture and exporter hashes are recorded in both final result files. The runner
adds an explicit `asan` profile after freeze07; the original runner bytes are
retained as `run_before_asan_extension.py` with their original SHA256.

## Failure accounting and limits

All exploratory failures are preserved and explained in `oracle_corrections.md`.
The material oracle correction preserves D087's independent <=5000us decision
continuity across reset. S/source eligibility alone is insufficient when a real
subsequent A0 conversion pushes D beyond that bound. Final assertions cover
source4999/5000/5001 and decision5000/5001 separately, including reset-fresh plus
terminal/no new C after an accepted S with failed subsequent chronology. A
Runtime clock rejected before Transaction.open retains its previous real C/token.
These are strengthened assertions; no production defect or old-test weakening
was required.

See `coverage.md` for the contract-group mapping. Practical public-API limits:
UINT64 token exhaustion cannot be reached in a bounded run; externally forged
recorder/receipt combinations are intentionally unavailable. Actual interrupted
attempts are tested through real abort, which also terminally faults Transaction.
An active transfer at the otherwise qualified STOP reset seam is not reachable
through genuine input; its reset-notification ordering needs source review.
POISONED native setup is a callback condition, not execution of physical UART.
All results are software evidence, not physical A1/grants, native UART, measured
loaded RAM/stack/WCET, motor-run authorization, phase gates or full-project completion.

Next action: parent consolidates fresh review, full host checks and exact target
source/ELF/memory acceptance. No further test author change is required.
