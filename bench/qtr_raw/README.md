# QTR raw capture bench (P2 B2)

The checked-in pad grant is false. This software preparation cannot configure or
charge pins until a separately reviewed physical setup explicitly grants the
existing Reader ownership. Uploads and MATCH are refused. It owns no motors,
matrix, IMU, ADC, UART, Bridge or application controller.

Build only with the existing board connection settings:

```
python tools/board_tool.py flash bench/qtr_raw --compile-only
python tools/board_tool.py flash bench/qtr_raw --compile-only --startup immediate
```

An enabled future revision services one Reader operation per ordinary loop pass;
it does not wait for a full discharge or use a1kHz sampling grid. The selected
config::QTR_BENCH_FRAMES default128 bounds the capture. Published records are
immutable; the final record freezes the runner. Stop/fault preserves the partial
capture and separate native cleanup evidence. A fresh pulse means one newly
published complete record, never an old or pending frame.

Each record retains four timing intervals, timeout masks, source chronology,
native statuses and cleanup fields. A timeout is a censored lower bound, not an
exact1500us reading. This bench does not classify colors or change thresholds.
Actual black/white/brown evidence needs a labeled physical run and later frozen
RAM readout. Software tests, compile receipts and simulated clocks cannot supply
surface provenance, sensor safety, cadence, full-app800us timing or a human gate.
See state/analysis/P2_qtr_raw_contract.md for the exact API and fault rules.
