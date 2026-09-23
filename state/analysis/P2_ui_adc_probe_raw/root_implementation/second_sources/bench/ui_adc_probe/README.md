# Bare-board A1 diagnostic (D114)

This named probe grants the existing native ADC owner permission to attempt its
unchanged live admission checks. It uses the same four implementation files as
bench/ui; staging copies those exact files. The ordinary UI bench stays disabled.

Only default-startup, MATCH0 and MOTORS_ALLOWED0 are eligible. No motor, matrix,
I2C, UART or Bridge owner is added. Compilation is preparation; a run requires
its exact reviewed source/artifact/readout and separate identified run record.
The upload route stays closed until that review is complete.

A successful trial retains128 raw A1 samples and actual UNCONFIGURED decoder
results. A failed initialization/read retains its original status and cleanup
result. An unconnected input has no expected code or voltage. Neither outcome
qualifies a button circuit, calibrated timing, reference/divider, full-app WCET
or a human phase gate. SC-A and SC-AJ remain open.

COMPLETE stops native reads but normally leaves ADC enabled and idle. Reader
has no stop/reset API. A frozen clock can leave the Runner nonterminal; readout
must preserve that outcome instead of claiming a completed trial. See
state/analysis/P2_ui_adc_probe_contract.md and the later exact run record.
