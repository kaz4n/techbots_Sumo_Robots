# P1 B5.5/B5.6 independent filter test authorship

Date: 2026-09-22, Asia/Dubai. Scope: P1 host-only under D-016; no gate acceptance.
Objective: independently specify the D-029/D-030 phantom episode and marker
contracts and the D-031 observed-span, reset-only stuck-sensor contract.

Owned files:
- tests/test_opp_filters.cpp: 35 new doctest cases.
- state/analysis/P1_opp_filters_test_author.md: this report.

Sources read: session AGENTS.md and test-author role, PROGRESS.md, BEHAVIOR.md
B0/B5.5/B5.6 and their amendments, DECISIONS.md D-029/D-030/D-031, config.h,
types.h and the opp_fusion.h public contract committed as 29779da. Existing
test helpers were read only for style and the already specified B5.2 bearing
table. No src/core/*.cpp implementation was opened. No existing test, locked
test, header, configuration or another author's file was edited for this task.

Phantom coverage: all known states, all 256 input byte masks, seven-bit input
normalization, front-only eligibility, current world-bearing capture, initial
edge qualification, first-observation anchoring across TRACK/ATTACK, repeated
target-pattern changes, inclusive 1500 ms window and adjacent us/ms samples,
contact at the first/intermediate/current sample, first-edge consumption even
when invalid heading prevents a marker, no repeated-edge lifetime refresh,
state/target interruption and rearm, marker replacement and exclusive 3000 ms
expiry. All close101/111, side and rear exemptions are immediate. Circular
distance includes 25 degrees and excludes the next representable float.

Fault/history coverage: missing or nonfinite IMU heading prevents marks and
masking while expiry advances; invalid initial heading does not invent a new
chase anchor. Reset clears contact/episode/marker history. Window/expiry survive
micros wrap, and old chase/marker history cannot return after a full timer
revolution reached using legal per-call gaps. Extreme finite headings must
produce finite canonical marker angles; no small-angle precision at float
maximum is claimed.

Stuck coverage: all 256 byte masks and all seven independent sensors; inclusive
5000 ms time, strict greater-than-360 angle span and adjacent representable
values; motion before/after the time threshold; retained minimum/maximum after
returning to the initial heading; cumulative oscillation with span exactly 360
does not qualify. Each bit has its own assertion time; clearing one resets only
its undeclared evidence. Invalid/unavailable IMU restarts time and angle evidence.
Declared bits stay suppressed across clear/reassert/IMU fault and report their
new fault only once, until reset. Tests include no aging before first assertion,
wrap/long-lived candidates and opposite float extrema requiring safe span math.

Property coverage: 10,000 fixed-seed mirrored phantom/stuck episodes compare
reflected masks, world angles, marker state and newly/previously declared faults.
Stuck fault expectations additionally check the independently known sweep.
After the fresh review identified correlated low PRNG bits at the four-draw
episode cadence, mask sampling uses bits 16-22. Per-mask counters and 128 explicit
assertions require all 128 logical masks to appear in the randomized episodes.
All prior behavioral assertions remain. These randomized episodes use finite
healthy headings; invalid/unavailable variants remain the explicit cases above.
Independent uint32 PRNG replay after the fix observed all 128 masks, with
61-98 observations per mask and 10,000 observations in total. The host tests
still need the coordinator's rerun to validate the complete corrected fixture.

Ambiguities: none requiring new policy within the committed contract. Its
first-edge consumption rule is tested even for an invalid edge, and its
close101/111 exemption is a B5.2 current pattern rather than the independently
timed B5.4 Contact counter. No other contact-lifetime policy is invented.

Validation at handoff: exactly 35 cases counted, CHECK-only assertions; no
shared build or test run by this author. Coordinator owns normal/sanitizer
results and final validation receipts.
Limits: these are standalone confirmed-input filters. They do not prove the
future FSM filter order, physical spectator rejection, a physical full turn,
actual IMU acquisition, HAL behavior, MotorGate permission or any phase gate.
Next action: coordinator reruns normal/sanitizer tests after the PRNG coverage
fix and retains the initial receipts separately from final validation.
