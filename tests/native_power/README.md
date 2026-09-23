# Independent native B5 tests

`test_power_unoq.py` compiles actual, opaque `src/hal/power.cpp` bytes against
controlled native headers. The author used the public contract, API and source
audits; production CPP was not opened. Compiler diagnostics necessarily contain
source locations, and those diagnostics are retained without using them to set
expected behavior.

Run under Linux/WSL with g++, without board access:

```
TMPDIR=/dev/shm SUMO_NATIVE_RECEIPT_DIR=<receipt-directory> \
python3 -m unittest tests.tooling.test_power_unoq -v
```

The checked-in extract generator uses the exact installed STM32U585 headers in
`state/analysis/P2_adc_ownership_raw/headers/`. Register field offsets, bit values,
and selected LL bodies remain source-derived; four-byte register words model
W1C and command acknowledgement. IRQ/device APIs are controlled native fixtures.
The SYSCFG address is the U585 nonsecure `0x46000400`, verified against the saved
CMSIS header, not an older STM32 family map.

Each modeled fresh boot runs in a forked process. There is no driver reset hook.
Same-boot second-reader tests retain the process lifetime claim. A small doctest
listener propagates child CHECK failures to the child exit code; parent checks
also reject signals. Two intentional failing native executions prove those paths.
The overall Python suite expects these two exits of 1 and passes only when their
failure diagnostics are present. Doctest totals in ordinary output count parent
status assertions; they must not be described as totals of all child assertions.

Coverage includes setup order and deadline boundaries, finite frozen-clock
failure, timer wrap, metadata/proposal alias exclusions, nominal clock/supply/peer
ownership, runtime mode changes, stale/fresh flags, partial completion, full-width
raw values, zero data, voltage arithmetic, latched failures, stop/disable failure,
cleanup time, process lifetime claims, allocation avoidance and inert probe/upload
refusal. No physical accuracy, frequency lock, MCU timing, integration or gate
acceptance is inferred.

Preserved authoring evidence records:

- Initial fixture extraction/compiler problems, corrected from source headers.
- Actual extra write after regulator-ready ownership loss (production defect).
- Actual second-reader recovery after an ignored first divider write (defect).
- Timing-draft failures that incorrectly treated flag observation as completion;
  final tests retain time for all required final checks and test equality rejection.
- Review corrections to the SYSCFG fixture address and stock-init test isolation.

Compiler/execution receipts contain every subprocess status, stdout and stderr.
Capture is explicitly `text=True`, with normalized stream newlines. Receipt file
bytes are not subsequently normalized. Final variants stage source/header/config
and record their exact SHA-256 values, including intentionally modified configs.
The root coordinator archives receipts into the final state evidence directory.
