# P0 inert diagnostics

`p0_matrix`: fixed SUMO glyph scroll, `p0Seconds` in RAM, and a fixed counter
notification through the existing internal router UART. D-062 uses one packet
slot and bounded TX callbacks; it never starts Bridge or receives commands.
Target compile/upload and actual counters4..11 then56..63 were observed on the
bare UNO Q. Optical appearance remains unverified. See
`state/analysis/P0_counter_validation.md` for exact source, review and receipts.
Default startup only; Immediate matrix uploads remain blocked. No motor or
external-header GPIO writes. This diagnostic is not a production logging HAL.

`p0_timing`: 60,000 scheduled samples at TICK_US, fixed RAM lateness histogram,
max lateness and over-period count. Final histogram bin means >=1000 us, not an
exact value; max records actual observed lateness. Compute p99 from cumulative
bins; if it lands in the overflow bin, report >=1000 us. A debugger readout or
approved bounded transport is needed. With missed periods, acquisition takes
longer than 60 seconds. This measures bare-loop scheduling only, not complete
robot tick WCET or the 5-minute M10 requirement.

`p0_adc`: D-063 startup-only timing of1000 calls to the installed A0 ADC input.
Fixed RAM retains each raw signed return and elapsed time plus paired micros
overhead. Sample0 includes deferred initialization; the other999 are subsequent
calls. All ADC work is in setup; loop is empty. Stock analogRead can wait forever,
so this characterizes completed calls only and is not a production ADC HAL or a
worst-case bound. Floating codes do not measure battery voltage or accuracy.
Default-only upload requires its exact reviewed inert source manifest; passive
readout uses `tools/p0_adc_capture.py`. See `state/analysis/P0_adc_contract.md`.

`p0_gpio`: D-064 setup-only timing on internal LED_BUILTIN/LED3_R (PH10/index50).
Checks GPIOH readiness, then400 samples of individual configure/write/read calls
and a contiguous pinMode(OUTPUT)+digitalWrite(HIGH) pair. Preserves signed
readbacks, stops on mismatch and makes a final HIGH/off attempt before freezing
RAM. Empty loop, no external headers or motor pins. Arduino wrappers mask native
errors, so readback success is not recovery of those error codes or optical proof.
Default-only reviewed snapshot; passive readout is `tools/p0_gpio_capture.py`.

QTR/I2C micro-benchmarks still require their pin/setup/API verification.
P0_G1/G2/G5/G6 specify their measurement plans. Motors/drivers must
remain disconnected for the bare-board P0 procedure. The old bare timing image
was measured separately; its max3us lateness is not timing evidence for the new
matrix/UART workload. No pin approval or phase gate follows from either run.
