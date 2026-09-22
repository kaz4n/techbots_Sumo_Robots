# P1 independent tick-statistics test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: test B14 supplied-duration statistics and the B15 frame maximum
boundary against public logframe.h contract 118f9cc. Owned files are
`tests/test_tick_statistics.cpp` and this report only.

Read B14/B15, public logframe.h/config, and existing frame-test assertion style.
AGENTS and the independent test-author rules were read earlier in this continuous
session. No src/core/*.cpp source was read. No existing tests, configuration,
state ledgers or shared build files were changed; no build or commit was run.

The 12 focused cases cover empty/default/reset state; the literal 1,000 us
strict boundary (including 999/1,000/1,001 and uint32 maximum); exact totals and
monotonic maximum; zero/one/two overruns among 100 actual observeTick calls;
denominator neighbors 99/100/101 and 199/200/201; and a ratio level that becomes
false again at exactly one percent, without inventing a latched fault.

Public valid-state fixtures exercise the real observeTick at UINT64_MAX-1 and
UINT64_MAX: the last retained sample still counts without saturation, the next
sample latches incomplete status without changing either retained count, and
all later observations still update the full maximum. Fixtures cover both
zero-overrun and all-overrun prefixes, a large threshold-adjacent ratio, and
aggregate reset after saturation. Every fixture satisfies overruns <= ticks.
These are allowed plain-value arithmetic fixtures, not private-state mutation
or a claim that billions of real samples were measured.

Literal large-count ratio fixtures include exact one-percent equality at
18,446,744,073,709,551,600 ticks and adjacent overrun counts. They distinguish
one-count differences lost by floating-point conversion and exercise overflow
boundaries without a wider-integer extension or overflowing cross-products.

Real observeTick -> packFrame composition checks the 65,535/65,536 us boundary,
explicit CLAMPED status, exact little-endian maximum bytes, preservation of
every other frame byte, and unchanged full-width statistics/source maximum.
Packing a finite-width field is not treated as permission to discard the full
maximum or the status.

Validation at handoff: author static review only, CHECK/CHECK_FALSE assertions,
no shared compilation/runtime checks. Parent owns host and sanitizer evidence.
No scheduler/clock, measurement accuracy, included-match-tick selection, hardware
timing, motor response, fault-latch policy, recorder persistence/dump or phase
gate is established. A false ratio on a saturated retained prefix remains
incomplete evidence, not a measured match pass.

Next action: parent reviews and runs the frozen tests, records actual results,
and commits the completed batch.
