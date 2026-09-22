# P0 timing run2: scoped measurement review

Date: 2026-09-22, Asia/Dubai. Reused separate reviewer context; no hardware operation or implementation edit.
Disposition: PASS for independent reproduction of this bare-scheduler capture. No open BLOCKER, MAJOR or MINOR in this evidence scope; no full REVIEW_GATE or phase pass.

Inspected `state/analysis/P0_timing_capture_run2_20260922.json`, invocation receipt, all 36 files in `P0_timing_run2_raw`, the upload receipt, pinned capture contract and prior loader-identity analysis.
Saved record SHA-256: `97e841e770b143f3f5c84a0efb411e0d6762230fe6da5558389bfe45918b487e`.
Original raw capture.json SHA-256: `d553cd4496c28a8c1f4055076f4573430039f90be9d5d25f277814160ab8c045`; parsed contents exactly equal the saved record despite formatting differences.

Independent Python byte decoding, without importing the production analyzer, found exactly 1001 histogram bins. Nonzero bins: 0 us=16561, 1 us=16683, 2 us=16603, 3 us=10153; all other bins zero.
Sum=60000, raw sample counter=60000, highest occupied bin=3 us, raw maximum=3 us, overflow bin=0 and raw over-period counter=0.
Nearest-rank p99 uses ceil(0.99*60000)=59400. Cumulative count through 2 us is 49847 and through 3 us is 60000; therefore p99=3 us, uncensored.
Both 4016-byte snapshots are byte-identical, SHA-256 `050ece168b85b6c1b4dafb132779cd7bcb6951f20c39f62717686e5af720d39e`. Separate first/last uint32 sample reads both equal60000.

All nine raw memory dumps match recorded byte lengths and SHA-256s. Full loader image hash `e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2` matches the pinned ELF-derived reference; sketch hash `c49b80f110fd34b7b5844a33f9c40da28b6b7543fe136b41621640c9b02802b8` matches the reviewed default artifact. The original packaged-BIN padding mismatch remains explicit.
Raw LLEXT records confirm one sketch node at0x200138e4, stable head/tail, null next, BSS base0x200191c0 and exact size11572. All four symbol addresses independently derive from the reviewed normalized ELF offsets and fit that BSS.
All13 command records exited0 without timeout. Preserved stdout/stderr agree with their recorded prefixes and truncation flags; the long readelf symbol output is explicitly truncated in JSON and preserved in full as a raw file.

Run2 readout lasted104.315778s, within its120s deadline, from23:31:52.396 to23:33:36.712+04. First and second value reads completed23:33:35.391 and23:33:36.670+04; raw values remained identical.
Upload completed23:19:29.798+04. The first SWD read was run1 at23:23:38.153+04,248.355s later; run2 began its first SWD read742.836s after upload. Run1 is preserved as an identity-comparison failure before RAM decoding.

Limits: this is one default-startup, 60000-sample bare scheduler result including installed core/library yield-and-mutex loop-hook overhead. It is not loaded Robot::step WCET, motor/sensor timing, clock calibration, matrix-active timing, optical evidence, boot-to-sketch latency or a phase gate.
The elapsed upload-to-attach interval and frozen data support the intended delayed readout, but the first actual sample read occurs after flash/list reads; it does not independently prove completion before first SWD activity. Repeatable bytes and histogram consistency do not replace separate cache-coherency qualification.
Next action: record the measured bare-scheduler result with these limits; keep other P0 hardware and phase criteria separate.
