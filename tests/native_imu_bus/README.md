# Independent native B3 transport tests

The author derives expectations from `P2_imu_bus_contract.md`, the public header,
config, and retained installed headers/manual audit. The production CPP is copied
as opaque bytes for compilation and hashing; it is not opened to author tests.
Compiler diagnostics necessarily expose source locations and are retained.

Run on Linux/WSL with g++:

```
TMPDIR=/dev/shm python3 -m unittest tests.tooling.test_imu_bus_unoq -v
```

The default receipt directory is
`state/analysis/P2_imu_bus_raw/author_receipts/`. Set
`SUMO_NATIVE_RECEIPT_DIR` to a separate directory for independent review.
Receipts retain staged production/header/config hashes and fixture hashes,
subprocess arguments, return codes and complete text-mode streams. Newline
normalization during text-mode capture is declared. Receipt bytes are not
subsequently rewritten.

`extract_bits.py` extracts exact installed register constants, field layouts and
selected LL bodies from the retained I2C and common source headers. It verifies
the full I2C header SHA-256 before generating files. `extraction.json` records the
source hashes, selected functions and storage/formatting adaptations. ST license
notices are retained. The installed RCC source helper uses a raw volatile
uint32_t read at its fixed 32-bit address. Its body is unchanged; a local GCC
diagnostic scope suppresses only the 64-bit-host integer-to-pointer warning.
That raw read observes model memory but bypasses the observable `Reg` counters.

Four-byte `Reg` words preserve offsets and model independent START, TXIS, TC,
RXNE and STOP acknowledgements, W1C clearing, RXDR/TXDR effects and local PE
disable. Model controls can deny acknowledgements, delay data, retain BUSY,
hold actual input lines LOW, ignore writes or inject ownership loss. No physical
clock, oscillator lock, supply, pad waveform, sensor configuration or sensor
freshness is implied by these modeled conditions.

Each modeled boot runs in a child process. The production boot claim has no
test reset backdoor and remains set within that process. A doctest listener
propagates child assertions to its exit code; parent assertions also reject
signals. Two deliberate failing executions must return 1 with failure output.
Ordinary doctest output totals count the parent assertions, not all child checks.

`run_fixture.py` checks the model's exact offsets/LL command encodings and final
RXNE+STOPF behavior, then compiles the independent case translation units before
production is available. This is a fixture check only. Production completion
requires the complete main suite, target compile and independent review recorded
by the coordinator; no partial fixture pass establishes B3 implementation.

The config allowlist extension in `tests/tooling/test_p0_config.py` is separately
authorized by the coordinator: ten D079 names/types/values are explicit, strict
whole-file declaration equality and every older assertion remain in force.

No test invokes SSH, ADB, a serial port, an MCU, board reset or firmware upload.
The upload-refusal test mocks lookup/transport and requires refusal before either.
The inert probe is tested with 10,000 empty loops under both macro modes.
