# D114 actual bare UNO Q diagnostic

Run `d114-ui-adc-01`,2026-09-24 Asia/Dubai: exact inert image uploaded once;
one passive readout collected a frozen COMPLETE128 result. The human reported
the UNO Q alone and permitted testing. No motor-capable firmware was uploaded.

Software9bb947b and exact staged source396bcc45 reproduce ELF76e23fe0/ZSK567fb90d
in fresh checked receipt68f3d6d38d9541c5afec8e54e5bcbec0. The fixed run record
dd17b5c0 binds reviewer approval01f95d07 and eleven exact files. Original files
are preserved under raw/run01_reviewed_files for future tool changes. The single
exclusive upload attempt/outcome shows exit0, no timeout, no retry. The standard
uploader uses its normal halt/program/reset sequence; no separate reset occurred.
The separately reviewed passive collector performs no halt/reset/write operation.

Both original9892-byte Runner reads are identical, SHA256
`3d33a0ed00c6cdfb467aefa8c2f51ee8349482fba6c15fcca201ec2f189298a6`.
Actual source sequence1..128 is contiguous, with zero missed releases, no clock
fault and no counter saturation. Raw codes2061..3984 are floating-input observations.
All128 decodes correctly remain UNCONFIGURED; INVALID presence/NONE level is not
a valid release. Setup measured957 MCU-clock us; source intervals54..60us,
callback S..A59..65us, sampled due-poll S..C63..70us. These component samples do
not establish calibrated physical time or complete worst-case control-tick timing.

Collection integrity is VERIFIED: complete deployed loader and sketch agree with
their pinned identities before and after the reads, and the list/node/BSS mapping
is unchanged. Actual18reads/587232bytes/22commands stay within the admitted maxima;
all commands exit0. The one collection took176.207s on the host. All63 original
files match remote/local transfer manifests and coordinator rehashing. Independent
literal-ABI decoding agrees with every public field and record. The known loader
BIN padding difference is retained; deployed loader identity uses pinned ELF
PT_LOAD bytes, not substituted package BIN bytes.

The independent analysis is P2_ui_adc_probe_actual_analysis.md, with raw decoder,
CSV and byte checks under P2_ui_adc_probe_raw/actual_analysis. Final actual review
is recorded separately in state/reviews/P2_ui_adc_actual_review.md. Reviewers are
separate reused same-model contexts, not human phase-gate or cross-model reviews.

No configuration value changed. The probe remains the last uploaded MCU image;
COMPLETE stops its native callbacks but leaves ADC enabled/idle by design. No
button circuit, calibrated voltage/clock, SC-A/SC-AJ closure, PINMAP, full-app
RAM/WCET, sensor/motor/assembled-robot acceptance or human gate is inferred.
Original receipts and failed preflight/fixture histories remain preserved.
