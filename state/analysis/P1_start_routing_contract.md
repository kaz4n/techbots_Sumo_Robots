# Service START routing prerequisite — 2026-09-23 Asia/Dubai

D-057 implements only the bounded prerequisite identified in the B13 mode/menu
audit. countdown.h is the public test contract; source changes follow its commit.

Controller::step and Lifecycle::step add trailing allow_match_start=true. False
filters the START command supplied to Gate while Buttons/StopHold/MODE/Gate time
still advance. Controller/Lifecycle::buttonEvents() returns the last input event
snapshot without resampling or mutating. Gate's accepted release is distinct from
a qualified-but-suppressed input. Reset empties the snapshot. A suppressed pulse
cannot later replay merely because eligibility becomes true.

This selector is intentionally not an emergency inhibit or cancellation: an
already accepted hold continues even when false, with its complete existing5.1s
deadline. STOP and MODE retain their existing priority. Actual menu consumers
must use the final safe state before dispatching a service request; the snapshot
can expose a qualified input simultaneously suppressed by STOP.

No service action executes here. A suppressed idle release cannot start
calibration, inspect/consume previous bias or request a heading reset; a previous
real attempt continues/cancels by the unchanged Lifecycle rules. No new tunable,
GPIO, timing semantics, established locked amendment or test-framework change.

Acceptance: independent new locked cases from D-057/public headers, never cpp;
suppression at release-qualification time, selector changes before/after it,
boot-held/rearm, default equivalence, exact/adjacent full hold, cancellation and
both/external STOP, access/reset/no-replay, services/bias and wrap/delay. Root owns
header/source/shared ledgers. Test author owns only its new tests/report. Separate
read-only scoped review follows actual normal/sanitizer/tooling validation.
