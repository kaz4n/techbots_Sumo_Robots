# P0 independent histogram-analysis test author

Date: 2026-09-22, Asia/Dubai.

Objective: protect the supplied pure
`analyze_histogram(samples, maximum, over_period, histogram)` contract using the
diagnostic's actual 60000-sample, 1001-bin design and public response fields.
Owned files are `tests/tooling/test_p0_capture.py` and this report. The diagnostic
sketch and config were read in the earlier histogram audit; no capture-tool
implementation or core cpp was read. No existing tests, tools, configuration,
ledgers or hardware state were changed.

Seventeen focused cases derive expected results independently from nearest-rank
p99: rank ceil(0.99 * 60000) = 59400, selecting the first inclusive cumulative
bin that reaches that rank. They cover zero lateness, exact rank minus/equal/plus
one, spread distributions, the highest exact bin 999 and isolated maximum-sized
outliers. Exactly 600 overflow samples keep rank 59400 below overflow; 601 move
it into bin 1000. Per the coordinator's explicit contract, the last bin always
sets p99_censored=true, including when maximum itself equals 1000. The returned
p99_us=1000 is the overflow-bin lower bound, not an invented exact sample value.

Validation cases require exactly 60000 samples, exactly 1001 nonnegative uint32
integer bins with matching sum, over_period equal to the last bin, and a
consistent uint32 maximum. Without overflow, maximum equals the highest occupied
bin; with overflow it must be at least 1000. Boolean/noninteger/negative/oversized
scalars and bins, incomplete counts, wrong shapes, mismatched totals, incorrect
over-period counts and inconsistent maxima are rejected. Where possible, malformed
boolean/float bins retain the correct sum so sum validation alone cannot mask a
missing type check. Input histograms must remain unchanged on success or rejection.

Tests accept TypeError or ValueError for validation rejection because no narrower
exception class was specified. Public result fields are checked for both values
and exact integer/boolean types. Module import is guarded against subprocess,
socket, os.system and interactive-input actions; a non-run argv sentinel and
captured stdout/stderr also detect accidental main execution during import.

Static handoff: 17 cases, no shared-build or capture invocation. Runtime evidence
is pending coordinator execution after the worker freezes its module. No claim
is made about actual RAM readout, debugger attachment, capture completion before
attachment, board timing or a P0 gate. Those require the separately coordinated
hardware run. Next action: coordinator runs the unchanged pure tests and records
their result before relying on the analyzer for physical evidence.
