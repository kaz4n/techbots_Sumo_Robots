# D131 independent test plan

Authored from AGENTS.md, `.claude/agents/test-author.md`, B2/B3/B4/B5/B6/B9/B11,
the adopted `P4_push_through_contract.md`, D085 line admission, D129 timing
contract, public headers and existing test fixtures. No production implementation
body was opened by the author. No test compilation or execution preceded this
handoff; root must preserve exact original files/hashes before first execution.

## Owned files and intended runs

- `tests/test_push_through.cc`: 24 declared cases; 21 base, two existing
  configured-button-protocol Runtime cases, one optional timing-profile case.
- `tests/locked/test_push_through_safety.cc`: 13 new R1/R5 cases, including
  10,000 fixed-seed bounded Escape streams and 10,000 real Robot/Gate streams.
- `tests/fixtures/push_through_fixture.h`: synthetic sources, public Escape
  checks, actual Robot/MotorGate receipt timelines, actual Runtime callbacks.
- This plan. No established tests, build configuration or production files owned.

Root's planned matrix: shipped literal0 full regression; isolated source copies
with literal20 and100; configured-button sanitizer0/20/100; configured20 plus
timing1 sanitizer. Dedicated new cases run in reactive M0 and M1. Established
locked oracles retain their original0 configuration. Duration is read solely
from `config::EDGE_PUSH_THROUGH_MS`; no feature macro or production positive tune.
Compiler admission of101/UINT32 overflow values and prior layout comparison are
root-owned checks, not represented as runtime test coverage here.

## Coverage and exact expectations

All16 masks at the Escape boundary and all15 nonzero masks at Robot/Gate;
mirrored front1/2 and head-on3; rear priority and three/four-bit fault priority;
Guard/default-false/no-permission defaults; no prior-ATTACK authority at GO or
TRACK; exact deadline minus1us, deadline, plus1us; wrapped clocks; duplicate
decisions; changing front bits, side context and contact cannot renew the anchor.

Fresh/retained line identity uses D085's2000us minimum spacing and6000us source
age. Explicit-source tests start each accepted frame100us before decision, so
expiry is tested5900us after its initial decision. Retained levels cannot begin
an allowance; retained final ticks still expire it. Stale sources inhibit.
Raw FC clearing precedes confirmed30ms debounce; confirmed/effective FC and
centering are independently necessary. FL+FR without FC cannot qualify. Phantom
removal remains authoritative. Missing contact permits approach-capped deferral
when phantom does not exclude the target; no false full-duty assertion.

Fresh black spends allowance with no entry/exit/inward pulse; next white escapes.
Only actual fresh-black completed-row exit or reset rearms. Permission loss spends
deferral; real active escape faults retain their established behavior. Replans
remain0 through deferral then preserve all three replacement starts. Consumed
invalid heading/head-on-side contexts fault; unused side/duties and unavailable
retained yaw remain unused. Fresh black does not invent a row-context fault.

New-white with old contact invalidates its stall history. The adopted same-tick
case starts fresh impact contact after deferral, allows the actual Gate to reach
qualifying duty, then provides fresh26deg deflection within13ms. M1 must enter
escape before an executed STALL/REFLANK event; M0 actual zero receipts cannot
qualify stall. After recovery, two real reflanks must still be admitted, proving
the rejected deferral stall consumed no limiter slot. The next ALL_IN keeps the
same bounded edge window. No1000ms timer is expected inside a20..100ms window.

Deferral preserves NEW_WHITE and the true frame mask, without actual escape
entry/replan/exit pulses. Source timestamps, actual Gate receipts, zero braking
and finite prior-state routing are checked. Optional timing1 keeps white an
INTERRUPTED_EDGE exclusion even while ATTACK is deferred. Runtime cases use its
real source admission and Gate callbacks, with explicitly synthetic raw frames
and ADC windows in an isolated configuration.

## Limitations and review handoff

These are software contracts, not electrical waveforms, physical QTR cadence,
wheel motion, safe positive tuning, ring acceptance, target image fit, live RAM,
full-source WCET or a human gate. APP_TEST_CONFIGURED_BUTTONS is the existing
test-only fixture protocol and must correspond to root's isolated ADC overlay.
No motor run/upload is authorized. Any post-execution oracle correction requires
preserved originals, a written failure analysis and separate review.

Ambiguities resolved before freeze: root adopted later-contact deflection as the
reachable same-tick stall case; finite initial and healthy-current heading plus
head-on-side checks retain ordinary row-fault priority; unavailable retained yaw
is ignored, and fresh black has no consumed row context. No remaining question
blocks freezing. Next action: root freeze and run the planned matrix.
