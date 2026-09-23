# Battery voltage bench (P2 B5)

The checked-in ADC grant is false. Construction, setup and loop therefore make
no ADC or clock calls. The future enabled bench owns one battery-only Reader;
it never enables the A1 button profile. No motor, UART, Bridge, matrix or
application controller is included. Uploads and MATCH are refused.

Compile only with the existing board connection settings:

```
python tools/board_tool.py flash bench/vbat --compile-only
python tools/board_tool.py flash bench/vbat --compile-only --startup immediate
```

The finite capture retains the first128 accepted samples at the existing10ms
cadence, including source and wrapper times, raw codes, nominal voltage and
missed releases. Each poll makes at most one read. Published records are immutable;
a fault preserves earlier records and actual failure/shutdown evidence. No
averaging, clipping, cached voltage or catch-up burst is used.

The Reader has no public stop API. Reaching the capture limit stops callbacks;
it does not disable the ADC or prove a safe electrical state. Default-false
software is preparation only. A later enabled revision needs the existing
ownership checks and a reviewed way to read the frozen capture.

The0.05V criterion requires time-correlated multimeter comparisons across9.5–12.6V
with a verified divider/reference and actual connected supply. Floating input
codes, host tests and target compilation cannot prove that accuracy. Physical
points, settling conditions, clock qualification, readout and phase gates remain
pending. See state/analysis/P2_vbat_contract.md for the exact software contract.
