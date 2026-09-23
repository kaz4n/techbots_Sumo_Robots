# D114 run01 actual evidence review

**PASS_ACTUAL_D114_BOUNDED_INERT_ADC_DIAGNOSTIC.** No open BLOCKER, MAJOR or MINOR findings.
Reused separate same-model reviewer; offline original-byte and receipt review only. No board action or rerun.

The one consumed `d114-ui-adc-01` approval, ADB target2629958581, run record and all11 file pins agree.
Fresh checked default receipt `68f3d6d38d9541c5afec8e54e5bcbec0` uses MATCH0/MOTORS_ALLOWED0, no libraries,
and reproduces source396bcc45, ELF76e23fe0 and ZSK567fb90d. The identified upload returned0 without timeout/error.
Normal upload halt/reset is confined to that upload; all22 capture commands are the four allowed metadata queries
and18 exact MEM-AP dump/shutdown reads. Command ordering, monotonic brackets,30s bounds and complete outputs pass.

All63 original files (936771 transferred bytes) match both remote/local manifests. Capture returned0 and its stdout
matches retained capture.json. Reads total587232 bytes over176.207 seconds, within the complete bounded plan.
Both full263680-byte loader images match independently reconstructed pinned ELF PT_LOAD bytes; the known single
packaged-loader-BIN byte difference remains explicit. Both19840-byte sketch images match the approved ZSK exactly.
The list and196-byte node are unchanged across reads: one terminated sketch node0x200138e4, BSS0x2001530c/9893.
Direct ELF32 Runner st_value0, size9892 and BSS section8 confirm relocated BSS+0; no nm VMA subtraction is applied.

Both9892-byte Runner snapshots have SHA256 `3d33a0ed00c6cdfb467aefa8c2f51ee8349482fba6c15fcca201ec2f189298a6`.
The separate literal ABI decoder agrees with every public report/capture field: COMPLETE/NONE,128 contiguous
samples, zero missed releases, raw2061..3984, all UNCONFIGURED with INVALID presence/NONE level/mask0.
Observed MCU-clock maxima: setup957us, source60us, read65us, due-poll70us. These are not calibrated physical time,
isolated SAR conversion timing or full-app WCET. Setup timing is separate from post-setup ticks.

This proves bounded actual raw A1 acquisition and sampled terminal consistency for the identified bare-board run.
It does not prove physical buttons/release, voltage, noise, PINMAP OK, SC-A/SC-AJ closure, motor permission or a gate.
ADC shutdown remains NOT_ATTEMPTED; COMPLETE native-callback passivity is the design, not a shutdown measurement.
Two equal snapshots plus identity brackets do not establish an atomic snapshot or future state lease.

Evidence: `state/analysis/P2_ui_adc_probe_raw/reviewer/actual_review.py` and `actual_review.json` (210 checks),
original `actual_run01/`, and `state/analysis/P2_ui_adc_probe_actual_analysis.md` with independent literal decoder.
