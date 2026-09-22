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
