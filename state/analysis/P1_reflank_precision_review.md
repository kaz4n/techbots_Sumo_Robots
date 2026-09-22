# Re-flank pre-build precision review — 2026-09-22

Separate reused reviewer found a MAJOR in the new local-frame transform before
any runtime test. At origin90, captured bearing-90, current yaw nextafter(5,0),
the true error is -4.999999523. Narrowing relative yaw -85.000000477 to float -85
makes B7 see exactly-5 and incorrectly remain ACTIVE. Independent new test already
covers this strict boundary; it must not be weakened. A separate exact+180 test
also protects the antipodal sign from absolute target rounding.

Correction contract: add motion::Turn.startRelative with original float measured
inputs but retain its captured origin and relative target inside Turn. Coordinate
normalization/subtraction/error stays double until B7 evaluates tolerance, sign
and duty. Existing absolute start and all its clients retain their behavior.
New relative mode clears on start/reset, uses the same timer/fallback and rejects
noncanonical relative bearings. Reflank passes actual yaw directly to Turn.step.
Remove the temporary fsm coordinate helper/field. No fabricated sample or change
to heading tolerance, target rule, timeout, duty or any test assertion.

This is a pre-build static finding, not a failed-test repair attempt. Full source
review and regression verification remain required before completion.

Correction implemented and statically verified by the separate reviewer:
coordinate reduction, subtraction and error evaluation now stay double inside
Turn.step; Reflank passes actual yaw. Ordinary start uses equivalent widened
arithmetic and reset clears relative mode. Existing strict-boundary expectations
stay unchanged; new relative API tests are being authored independently.

Coordinator's additional pre-build finding in the touched shared Turn primitive:
the public contract says a healthy nonfinite heading latches INVALID, but an
already-latched fallback bypasses that validation. Before the original timeout,
imu_ok=true plus NaN/Inf can remain ACTIVE. Existing tests did not cover this
recovery combination. Separate reviewer assessment and new spec-derived cases
were requested; original timeout precedence and existing tests must be preserved.

Reviewer confirmed the existing-contract mismatch. Turn now checks timeout
first, then healthy nonfinite yaw before either control mode. New independent
tests cover absolute/relative starts, initial/mid-turn fallback, NaN/+Inf/-Inf,
unavailable readings, latched invalid output and exact timeout. All609 cases /
11,983,801 assertions passed normal and ASan/UBSan on the first batch run after
the static fixes. Separate reviewer independently reproduced the totals and
closed both findings. See ../reviews/P1_reflank_headon_codex.md.
