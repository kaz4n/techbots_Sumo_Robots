# Application battery scheduling audit - 2026-09-23

Read-only explorer findings. This is a proposal for the next integration task,
not an approved D093 contract, changed requirement, implementation or measurement.
D092 timing is being validated separately. No hardware commands were issued.

## Existing evidence

One boot-lifetime power::Reader owns ADC1 and the optional A0/A1 profile
(power.h38-50, P2_adc_pair_contract.md10-15). A0 results expose status, shutdown,
raw count, actual start/completion, voltage and validity (power.h19-27). A1 also
has an accepted-conversion sequence; A0 has none (power.h29-36,power.cpp486-499).
Start precedes ownership/rank work; completion follows conversion/scaling/checks
(power.cpp424-445,449-480). Success must finish strictly before100us (config.h44),
and a fault may require a separate100us shutdown budget (power.cpp358-395).
Either channel fault latches the shared reader; both then return FAULT_LATCHED
without I/O (power.cpp449-454,486-491). No second owner/reset/reclaim is permitted.

Initialized Robot requires finite valid battery every decision and otherwise
latches INVALID_CONTEXT (fsm_robot.cpp237-242). Governor receives voltage once
per decision (714-724). Its existing1s backward-Euler filter runs each call:
alpha=dt/(1s+dt), governor.cpp53-70/config.h180. Final caps/slew follow compensation.
Low-battery warning sets in IDLE below10.8V and clears on an admitted value at/above
that threshold. Motion timing stays unchanged. Current frames contain admitted
voltage but no source timestamp/age.

Every-tick A0+A1 is callable, but IMU600+motor150+ADC100+ADC100=950us before other
work and fault cleanup. These are software deadlines, not measured call WCET.
Removing one ADC call alone does not prove the complete800us requirement.

## Recommended narrow decision for the coordinator to freeze

Extend D078's fresh-only/no-stale policy explicitly with app-owned bounded retained
voltage. Keep native Reader fresh-only and the governor filter unchanged. Proposed
config values VBAT_SAMPLE_PERIOD_US10000 and VBAT_SAMPLE_MAX_AGE_US20000 are
unmeasured development limits, not physical qualification. No value has changed.

Only a genuinely executed successful Reader::read result replaces retained data.
Validate its exact status/shutdown/valid shape, finite voltage,14-bit raw range,
forward timestamps and duration<existing100us deadline. Preserve raw zero and
actual timestamps; no healthy-range clamp. A local accepted-call counter is not
a hardware generation identifier. Retained age uses actual start conservatively,
not completion or reuse time; usable only strictly below maximum. Accumulate age
across observations, saturate, reject backward/half-range time and prevent old
source revival after full wrap. Genuine new valid data can replace expired data,
but cannot clear a previously latched Robot fault.

An A0 or A1 failure invalidates retained voltage before the next decision even
when A0 is not due. Preserve first failure/shutdown diagnostics and boot-lifetime
native fault. A Robot reset cannot clear it. Absence/expiry maps to invalid battery;
startup readiness and later inhibition must be specified explicitly in app owner.
There is no proposed low-voltage shutdown threshold.

Schedule due A0 only in an explicit bounded slot respecting next control and QTR
service deadlines. Account for failure cleanup and actual surrounding overhead,
record skipped/refused slots and source age, and include service work in scheduler
evidence. Do not hide acquisition outside the named tick. A1 independently obeys
its existing5000us age/continuity contract; do not automatically acquire both.

Held voltage remains a held input to the existing each-tick filter. Cached low
voltage after recovery may temporarily increase compensation; cached high voltage
during sag may reduce it. Final caps still hold but do not prove physical speed.
Warning changes can be delayed by the admitted age. Existing frame payload can
remain unchanged only with explicit held-value documentation and separate source-
age/acquisition/fault diagnostics; frames alone cannot prove battery freshness.

## Independent acceptance

Test exact age/duration bounds, ordinary/full wrap without revival, identical raw
values from distinct calls, future/backward sources,raw endpoints,stale startup,
A1 shared failure, no refresh after provider fault, analytic held-input filtering,
final cap/slew and actual Robot/MotorGate inhibition on expiry. Reuse native_power
pair_cases/pair_timing and test_governor. Small app-specific evidence owner only;
no generic ADC router or new filter. Then compose the actual application owner.

Physical divider/reference accuracy, channel settling, loaded voltage transients,
actual source ages and complete scheduler WCET remain unqualified. All human phase
gates and motor-run rules remain unchanged. Review recommendation before selecting
D093; timing completion alone does not authorize these proposed semantics.
