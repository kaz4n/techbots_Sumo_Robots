# D224 recorder session host validation

Isolated worktree: `C:/Users/narut/AppData/Local/Temp/sumox-recorder-session-20260926`.
Base commit: `ee1bdcedf412903445c5076cae5980a43e0dc34e`. No main-checkout, board or network action. No commit made by the test author.

## Result

- New receiver tests: 11 Windows methods PASS and the same 11 Linux methods PASS; one additional Linux parser-reuse method PASS.
- Native UART register model: 128 grant/mode/session combinations plus 8 retained-guard cases PASS (136 subprocess cases). This is simulated UART behavior, not a board measurement.
- New C++ transfer/runner tests: 5 cases and 54,034 assertions PASS in each normal and ASan/UBSan build. The full synthetic 200 s scenario retained 5,001 frames and 8 events, emitted the supplied 64-bit session, and produced identical bytes in both builds. Both streams passed the strict expected-session receiver and CSV publication; wrong expected identities failed.
- Unchanged compatibility tests: 58 Python methods PASS; 47 C++ cases / 4,191,932 assertions PASS. One additional new sticky-reuse method ran alongside the Python compatibility selection.
- Actual default recorder sketch setup plus 10,000 loop calls passed the unchanged counted-native fixture with zero native clock/setup/ready/write/cancel calls. Default identity remains disabled. No host/CMakeLists.txt change was necessary: its existing *.cpp glob discovers the additive C++ test.
- No production or test oracle repairs. All 14 first-run source/test pins and 7 compatibility pins remained unchanged at closure. No skipped methods in these selected runs.

## Coverage and evidence boundary

Independent fixtures cover legacy session zero, supplied one/high-bit/maximum uint64 values, every v1 envelope and CRC, one-byte partial progress, active identity changes before repeated-time suppression, all old ownership/setup grants, unknown admission modes, Linux readiness, FIFO packet completion, ownership refusal, poisoning, exact packet timeout, slow total deadline, inhibited IDLE, retained recording bytes and full lifecycle composition.

The receiver rejects wrong BEGIN, every row kind and END even with corrected CRC; stale complete wire with a fresh synthetic connection ticket; stale prefixes/fresh suffixes; concatenation; garbage; truncation; arbitrary chunk boundaries; noncanonical CLI and nonexact integer API inputs. Successful and failed captures retain expected/observed/rejected identity with raw bytes. Parser reuse preserves the first error and cannot resynchronize.

This validates host software only. The delivery caller under construction was not tested. No loaded target layout, UART delivery, throughput, physical safety acceptance, motor-run permission or phase gate is established.

## Retained launcher failure and correction

`legacy01` initially ran 59 methods: 46 PASS, 13 ERROR in setUp because my launcher omitted the existing error-journal suite requirement that TMPDIR resolve under /dev/shm. The tests did not reach their assertions in those 13 cases. Original stderr and launch receipt are retained. `legacy_driver02.py` selects only those 13 methods and adds external `env TMPDIR=/dev/shm`; all 13 PASS. It then performs the previously unexecuted C++ compatibility and disabled-sketch checks. No successful Python method was rerun and no source/assertion was changed.

Two unrelated legacy tooling methods were not selected: the separate C++ stream compile round trip (covered by the executed C++ compatibility and supplied-ID pipeline) and broad historical config-registry replay. The receiver/transport compatibility checks otherwise used their existing assertions unchanged.

## Reproduction and storage

First test commands, exact arguments, stdout/stderr, timings and input identities are retained in [raw receipts](P7_recorder_session_raw/closure.json). New Python fixtures are in tests/tooling/test_recorder_session.py, test_recorder_session_reuse.py and test_recorder_session_host.py. C++ fixtures are tests/test_recorder_session.cpp and tests/fixtures/dump_uart_fifo/session_cases.cc.

All compiler invocations ran serially. Focused build scratch `/tmp/sumox-session-rir5m7ph` and compatibility scratch `/dev/shm/sumox-session-legacy-dwku8gse` were owned TemporaryDirectory contexts and closed after their tests; they held only generated host executables/objects/CSV copies. No full source snapshots, target artifacts, bytecode or external cleanup were created. Retain the compact receipts and unique launcher failure for review/reproduction; source plus the base commit provides the dependency history.

## Frozen source and new test hashes

| Path | Bytes | SHA-256 |
|---|---:|---|
| `src/hal/recorder_dump.h` | 3201 | `e25df3d2875e822b78c770baccecadbd70547c4fce2632250c6f42bff03fc552` |
| `src/hal/recorder_dump.cpp` | 15424 | `b65f1a9e67eea89a01e7e03b39c618d27bc2dcaad98deb71db2035c2012f585c` |
| `src/hal/dump_uart_unoq.h` | 2910 | `e25b764a03828709ebddf5f2fb2a630e723101088a7effaf38b17d3691b42e04` |
| `src/hal/dump_uart_unoq.cpp` | 17430 | `b544607f3c3570bf81dac150488e18d3111ffce9ac387eb4b45a2ccddd205338` |
| `bench/recorder/src/recorder_transport.h` | 6620 | `78544532be7ec489909e6d18894f95332d92943cab428294a1d6fd9b2568c292` |
| `bench/recorder/src/recorder_transport.cpp` | 6571 | `b62e2bed555466d802b913c56ed0188c33ae55f730d5f408857561f83cca2bcd` |
| `bench/recorder/src/recorder_transport_io.cpp` | 4052 | `a419d76bd4c86c12385b3117ac6dde110c282d8e77aea8d1f9fea4845b16dcc5` |
| `bench/recorder/src/recorder_run_identity.h` | 645 | `9daf17d5c1305057e7a775019ba9db242bc2a068631e8be80c4e45c48df3620c` |
| `bench/recorder/recorder.ino` | 796 | `d88b6951e75f7be90b31193cad992494e3e4eb4c0518c4b350bfa20f1d326a1a` |
| `tools/dump_match.py` | 53588 | `ef9b871db109b6b58f2c695ba2919c996a01b6e6e231859666e9b2a73abc69f3` |
| `tests/test_recorder_session.cpp` | 8985 | `cfc2a659bb238854a11f9d7547cd55b6b327e8f320dc7fa4475d4814b51a12ed` |
| `tests/fixtures/dump_uart_fifo/session_cases.cc` | 4071 | `1dce591e56e058871c3bcd5e3152678721cec0fc88fe1716fb70f7a2583aca07` |
| `tests/tooling/test_recorder_session.py` | 9677 | `bd7ebd3212468aa26986fc9a19bb4f964cc85c6be1337229e9ff284ec3bc29d1` |
| `tests/tooling/test_recorder_session_host.py` | 5075 | `6acfd344f3a05c338f2494b79a4cd87007bbf3ca405943bc2c776dbeeba0d015` |
| `tests/tooling/test_recorder_session_reuse.py` | 1401 | `25f495e7ff5ff835450dfeaf97dcd1b83e1d1ea81e4f1ed8c1a410421f6fe822` |

Unchanged compatibility file hashes are in [compatibility_inputs.json](P7_recorder_session_raw/compatibility_inputs.json); complete raw receipt hashes are in [closure.json](P7_recorder_session_raw/closure.json).
