# B13 logical menu contract — 2026-09-23 Asia/Dubai

D-058 selects the saved independent audit's recommended gesture semantics under
D-051. The new public contract is countdown.h Menu/Service/MenuSelection/
MenuSample/MenuResult. D-057 already supplies single-sampled qualified START and
START-only match routing; retain its default API/locked tests unchanged.

Composition: derive match-start eligibility from entry state/selection, step
Lifecycle once with real input, then Menu with entry state and final STOP/fault
inhibition plus that tick's genuine ButtonEvents.start_release. A canceled
countdown must still supply COUNTDOWN-at-entry. Capture the running mode from
the accepted Gate release; no MODE action can change it while moving. Menu
returns no permission/duties and executes no QTR calibration, dump or drive.

The header defines full NONE/MODE qualification, frozen release duration,
short/medium/long ties, contamination/rearm, all modes/services, service intent,
duplicates, reset and bounded wrap-safe timing. DRIVE_TEST intent is explicitly
unavailable; other intents require actual consumers rather than a fake success.
No external mode setter is needed. Compile-time MODE_DEFAULT validity must be
checked rather than constructing an invalid enum from a bad configured value.

MODE_SHORT_MS=600 centralizes existing B13 text; no original B16 default changes.
TUNING_LOG records that source-derived addition, not a physical tuning result.
New config/header invalidate the old inert snapshots until separate review.

Ownership: root edits shared interface/config/spec/ledgers; a bounded worker owns
countdown.cpp implementation only. Independent test author owns new menu and
locked menu-routing files/reports and must never read cpp. Separate read-only
reviewer checks actual frozen source/tests/evidence and exact inert snapshots.
No hardware action is needed for this P1 task.

Acceptance: original audit section4, exact/adjacent20/600/1000ms boundaries,
qualification-time anchors, held/released/invalid combinations, all mode/service
cycles, no action after countdown cancellation or entry-state change, duplicate
timestamps, multiple timer wraps, fixed-seed input properties and actual Lifecycle
composition. Service START never starts the gate/calibration; STOP always wins;
match START preserves the full5.1s hold. Established locked tests are immutable.
