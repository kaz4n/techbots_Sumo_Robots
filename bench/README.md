# P0 inert diagnostics

`p0_matrix`: fixed SUMO glyph scroll using core 1.0.0 matrix draw API, plus
`p0Seconds` in RAM. No Bridge, UART, motor or external GPIO writes. Source-backed
API only; target build/display unverified. This is **not** the required printed
counter round trip. SC-I records the conflict between Monitor and R3/R4.

`p0_timing`: 60,000 scheduled samples at TICK_US, fixed RAM lateness histogram,
max lateness and over-period count. Final histogram bin means >=1000 us, not an
exact value; max records actual observed lateness. Compute p99 from cumulative
bins; if it lands in the overflow bin, report >=1000 us. A debugger readout or
approved bounded transport is needed. With missed periods, acquisition takes
longer than 60 seconds. This measures bare-loop scheduling only, not complete
robot tick WCET or the 5-minute M10 requirement.

No GPIO/QTR/ADC/I2C micro-benchmark writes are implemented before pin/setup/model
verification. P0_G1/G2/G5/G6 specify their measurement plans. Motors/drivers must
remain disconnected for the bare-board P0 procedure. No board run has occurred.
