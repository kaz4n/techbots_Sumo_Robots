# D093 fixed ADC input owner and bounded battery evidence

2026-09-23 Asia/Dubai; baseline8e4544a. Active P2 under D051/D075. Prior turn made
progress: D0922081ca1/8e4544a implemented and verified complete-tick timing. This
contract explicitly amends only D078's app-level prohibition on retained voltage;
the actual native Reader remains fresh-only, unchanged and exclusively owned.

## Ownership and public API

Implement power::InputOwner in hal/power_inputs.{h,cpp}; native forwarding only in
power_inputs_unoq.cpp. Public header is frozen first. A noncopyable boot-lifetime
owner has a copied fixed InputPort: same-context beginWithButtons/readA0/readA1,
clockUs. Context outlives owner. Production readerInputPort binds one actual Reader
and its micros clock domain; no other caller may use that Reader. No arbitrary
sample-ingest API, generic channel routing, additional ADC owner or voltage filter.
Constructors/destructors/factory make no callbacks or I/O. No reset/recovery API.

begin marks attempted before admission. Reject any null callback (context may be
null for stateless ports) or invalid owner config before callbacks. Config requires
0<conversion<=period<max_age<2^31, reference finite in(2.4,3.6], divider finite>=1;
existing native hardware-config validation is unchanged. New development values
VBAT_SAMPLE_PERIOD_US10000, VBAT_SAMPLE_MAX_AGE_US20000. No original B16 value changes.
One begin invokes clock/setup/clock, no conversion. Accept only known exact setup
OK+ready+NOT_ATTEMPTED and forward elapsed<half-range. A first ALREADY_STARTED is
SETUP failure even if native ready=true. Known nonOK setup means SETUP failure;
unknown enums or OK with inconsistent ready/shutdown means SOURCE failure. Save
actual setup result and first status/shutdown. Repeat begin returnsfalse with no
callbacks or state change, even after success. Before begin, all other methods
return unavailable/no attempt without callbacks or changing the future clock anchor.

## Clock, lifetime and failure

Every clock observation uses unsigned forward delta<2^31; equality is allowed.
Clock reversal/exact half-range/greater distance latches CLOCK. Maintain last
observation and saturating uint32 battery age by adding each valid delta. Caller
must observe more frequently than half-range: an entirely unobserved full wrap
is unknowable from uint32 and is not claimed detectable. Across observed full
wraps, expired evidence never revives by modulo subtraction. Only a new actual
accepted read replaces it. Native callbacks are trusted to execute real fresh
conversions; brackets validate returned evidence, not timeout a blocking callback
or prove physical generation against a dishonest substitute. Production native
Reader's actual bounded fresh-conversion implementation supplies that guarantee.

Any CONFIG/PORT/SETUP/ADC/CLOCK/SOURCE fault is latched until reboot and invalidates
both outputs immediately. Preserve the first fault/operation/native status/shutdown.
All later port callbacks (including clock) are suppressed. Report remains readable;
observe/projection cannot clear a fault. No blind native shutdown/reinit is added.
A known nonOK native result with valid=false takes ADC (or SETUP) precedence over
post-call clock errors; unknown status/shutdown or contradictory validity is SOURCE.
A native-success result is then subject to clock chronology and source validation.
First failure diagnostics are never replaced by subsequent FAULT_LATCHED responses.
Ordinary age expiry is not an owner fault and can recover on a genuine new read;
this never clears a fault already latched in Robot/MotorGate.

## Battery calls and retention

readBatteryIfDue observes port time if initialized/healthy. First read is due;
after acceptance, due when accumulated age>=period, anchored to actual source
start. If not due, no A0 callback and no refusal. If due but slot_granted=false,
saturating-increment battery_refused and retain due. With grant, invoke exactly
one A0 callback, bracketed by clock reads. No catch-up or implicit A1 acquisition.
Counters battery_attempts/button_attempts count actual calls and saturate; local
battery_generation increments on acceptance, saturates at uint64max (never wraps).
No conversion is refused merely because its diagnostic counter saturates.

Return BatteryRead actual native sample unchanged, attempted=true, accepted only
on full admission. Success requires OK/valid/NOT_ATTEMPTED, raw<=16383, finite
voltage exactly equal to the native documented float expression
float(raw)/16383.0F * VBAT_ADC_REFERENCE_V * VBAT_DIVIDER_RATIO. Raw0 is valid;
no clamp or healthy-voltage restriction. From the common call-before anchor:
0<=sample_start<=sample_completion<=call_after<2^31, and conversion interval is
strictly below VBAT_ADC_CONVERSION_US. Native failures are never replaced by cached
values in the returned read. On acceptance save exact native sample, set age to
call_after-source_start, increment local generation, and expose available iff
age<max_age. Before read, expired cache stays invalid; successful replacement may
be identical numerically. Replayed old source intervals fall outside a later call
bracket. A callback's genuine identical timestamp after a whole observed clock
wrap is a new call, not proof that unchanged bytes alone imply new hardware data.

Report retains last accepted sample for diagnostics even after expiry/fault, but
battery_available and battery_due are separate. Healthy expiry remains due. Fault
means neither available nor due. Before first sample healthy setup is due/unavailable.

## Buttons and shared failure

readButtons observes clock and invokes at most one A1 callback when slot_granted;
false grant increments button_refused while healthy and returns unattempted. There
is no internal button period, cached substitute, implicit A0 or catch-up. Validate
same successful status/valid/shutdown/raw/interval/bracket shape. First sequence
must be1 (owner is exclusive after fresh pair setup); each later accepted sequence
must equal previous+1 modulo uint32, including natural wrap0. Any skipped/replayed
sequence is SOURCE; it indicates another caller or stale callback evidence. Return
native ButtonSample unchanged with attempted/accepted flags, never synthesize NONE.
Any A1 failure invalidates a young retained battery before next projection. A0
failure likewise blocks A1. Successful A1 calls advance battery age but never refresh
its source or generation. The scheduler still must satisfy D087 button continuity.

## Projection and startup

observe(decision_us) performs no callbacks, advances the same clock/age, and returns
a snapshot. report() is a nonmutating last-observed snapshot, not an age refresh.
applyBattery(input) observes input.t_us, modifies only vbat_v/vbat_valid, projecting
last accepted voltage only if available; otherwise canonical0/false. It returns
availability and never changes initialization_complete, decision, other sensors,
Robot state, governor or MotorGate. App initialization must remain incomplete until
first available battery plus its other prerequisites; an initialized Robot still
inhibits on unavailable voltage through the existing INVALID_CONTEXT rule.

applyButtons(input,read) observes the same decision time and modifies only buttons.
A healthy owner with read.attempted=false/read.accepted=false uses existing absent
ButtonSample{} mapping. A healthy accepted attempted read uses ui::applyButtons
on its exact native sample. Attempted rejection, contradictory attempted/accepted
flags or any owner fault projects explicit INVALID with contract_valid=false,
never a neutral release; preserve raw native bytes separately in ButtonRead. Caller
must supply the actual result of this owner's latest requested operation; this
helper does not turn caller-invented structs into hardware evidence. Existing Robot
source/sequence/age checks remain active and reject stale/replayed A1 as specified.

Held voltage feeds the existing per-decision1s governor filter; do not freeze it,
filter twice, alter final caps/slew or add a low-voltage stop. Current frame voltage
is the admitted held value; frame layout unchanged and cannot alone prove source
age. InputReport provides actual timestamps, accumulated age, local call identity,
refusal/attempt counts and first-fault diagnostics for future app evidence.

## Scope and validation

Scheduler grants are explicit obligations: fit success and failure cleanup plus
surrounding work before control/QTR deadlines; bracket checks alone do not prove
800us or abort a blocking port. Whole scheduling must include these calls in its
evidence, not hide work outside the control tick. Actual app composition follows.
No physical accuracy/settling/wiring/PINMAP/clock/phase/motor authority is implied.

Independent tests derive from this contract/header, not CPP. Cover all API shapes,
setup once, raw/interval/age/period boundaries, refusals/no bursts, ordinary/observed
full wrap without cache revival, half-range faults, identical new conversion and
old replay, exact nominal scaling, shared A1 failure, no callbacks after fault,
projection isolation/invalid buttons, analytic held-input filter and final caps,
actual Robot/MotorGate inhibition at expiry and persistent Robot fault on replacement.
Use actual native power.cpp with existing installed-shaped process-isolated fixture
for Reader->owner pair setup/channel/fault/no-allocation checks. Preserve all old
tests; new config registry is additive without weakening its assertions.

Add an inert compile-only probe retaining actual nativeReader->owner->Robot/Gate/
recorder paths without executing setup/callbacks; no upload allowlist key. Full
host/sanitizer, controlled native/probe/compile-only refusals, actual target source/
ELF checks and fresh separate review precede completion. Observe lowRAM headroom.
