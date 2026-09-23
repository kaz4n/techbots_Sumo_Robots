The first independent reviewer probe run failed two reviewer-only assertions at
clock position 1. Its injected reading was next_release_us-1, which remained
forward from the previous C and was legitimately an early clock-only call. The
probe incorrectly required RUNNING/service_only there. Corrected only that branch
to require STOP_OBSERVING, retained pending intent and no reset. The original
immutable review JSON and original source hash remain. No production/test file
was changed, and the other 24-position observations were retained: 11 terminal
faults and 22 actual resets before this test correction.
