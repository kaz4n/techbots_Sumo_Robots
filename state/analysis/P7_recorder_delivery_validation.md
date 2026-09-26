# D225 recorder delivery caller host validation

2026-09-26. Status: **PASS_HOST_ONLY**. No board operation, upload, motor action, hardware acceptance or phase gate is claimed.

Caller: `tools/run_recorder_delivery.py`, 50592 bytes, SHA256 `9ea1be98388139343be02bc74857c220faa75c32b876b9938f855188d750b6cd`.
Base checkout HEAD: `ee1bdcedf412903445c5076cae5980a43e0dc34e`. Production and locked tests were not edited by this test worker.

## Results

- Windows: **42 applicable unique methods passed**; one Linux-only compiler method skipped.
- Linux/WSL: **43 unique methods passed**. Generated header compiled with MATCH=0/MOTORS_ALLOWED=0 and was rejected for the other three MATCH/motor combinations, one compiler process at a time.
- Existing core validation was not repeated. The real full synthetic wire fixture was reparsed at the supplied uint64 identity and checked as 5,001 frames, 8 events, SEALED, zero declared loss, zero duty and the complete expected lifecycle.
- Real checked helper construction, independent source hashing/staging, generated identity inclusion, static upload bindings, stale scratch admission, and one prepared payload/read-only admission passed. Controlled process fixtures cover exact receive commands, claim-once ownership, operation ordering, late refusal, bounds, closure races, original error retention, available partial bytes and cleanup errors.

## Execution receipts

| Receipt | Methods | Passed | Failed | Skipped | Exit |
|---|---:|---:|---:|---:|---:|
| `P7_recorder_delivery_raw/tests/first01` (windows) | 43 | 21 | 21 | 1 | 1 |
| `P7_recorder_delivery_raw/tests/windows02` (windows) | 21 | 18 | 3 | 0 | 1 |
| `P7_recorder_delivery_raw/tests/windows03` (windows) | 2 | 0 | 2 | 0 | 1 |
| `P7_recorder_delivery_raw/tests/windows04` (windows) | 3 | 3 | 0 | 0 | 0 |
| `P7_recorder_delivery_raw/tests/linux01` (linux) | 43 | 42 | 1 | 0 | 1 |
| `P7_recorder_delivery_raw/tests/linux02` (linux) | 1 | 1 | 0 | 0 | 0 |

Every receipt retains the exact argv, output, duration, input hashes and unchanged-input result. After a failure, only failing methods were repeated on that platform. Windows and Linux are distinct executions; successful historical/core suites were not repeated.

Canonical suite: `python -B -m unittest tests.tooling.test_recorder_delivery tests.tooling.test_recorder_delivery_run tests.tooling.test_recorder_delivery_receiver -v`. Linux used `TMPDIR=/dev/shm` and the explicit read-only reference root. Exact WSL argv is in `linux01/linux.json`; targeted argv is in each subsequent receipt.

## Retained failures and corrections

1. `first01`: shared intended-valid attempt fixture had 33 hex digits instead of 32; Windows path separator comparison was not portable; post-claim closure correctly used a transport wrapper retaining the original ValueError. Test fixtures were corrected, retaining their original bytes and explanations. No admission requirement was relaxed.
2. `windows02`: the old baseline lacked the newly introduced exported-artifact role; fixtures now explicitly use the checked sketch image metadata for that export. Actual admission also refused one checkout-converted inventory JSON. A full HARD_PINS check found a second converted JSON; root restored both to exact main/HEAD bytes. Guard rejection and drift hashes remain recorded.
3. `windows03`: **production defect**, Windows `upload_bindings` imported the Linux-only `resource` module through the complete native support module. Both real bindings and prepared payload failed. The author repaired local construction with the existing pure binding-support extractor; full native support bytes remain unchanged. Original caller bytes, exception output and fixture update are retained. `windows04` passed all three unresolved methods.
4. `linux01`: one inherited bootstrap checked-read guard rejected `tools/app_motor_fault_static_policy.py` while comparing file/ancestor metadata. All pinned input bytes were unchanged. Shared ancestor metadata churn is a possible cause, not established. A single unchanged targeted rerun passed (`linux02`); no guard or source change was made, and the original refusal remains evidence.

## Evidence boundary and storage

Native ADB/upload/process behavior is represented by controlled substitutes; this is software validation, not board delivery or measured target timing. Raw wire preservation and acceptance are exercised on an existing synthetic host fixture, never claimed as a new target capture. Temporary fixture directories and compiler inputs were managed by TemporaryDirectory and cleaned on exit. Only compact results and unique failing source/test snapshots are retained; main checkout was read only.

Full final source/test pins, per-method passed identities, reference wire digest and counts are in `P7_recorder_delivery_raw/tests/closure.json`. Raw evidence hashes are in `P7_recorder_delivery_raw/tests/evidence_manifest.json`.

Test source pins:

- `tests/tooling/test_recorder_delivery.py`: 18 methods; SHA256 `4e6408e854b67565e8cc857304baa2faa86c4bad43a8b8df27eed284011f3ac5`.
- `tests/tooling/test_recorder_delivery_run.py`: 12 methods; SHA256 `fedd88906f8e3440ebc33c0631fd2154069cb35df7996eebde91b2f26d71777f`.
- `tests/tooling/test_recorder_delivery_receiver.py`: 13 methods; SHA256 `d6ed189b6b4bc6c380547ec10cb2e3f5bda3b78cd0e484ce808aefdd33984573`.
