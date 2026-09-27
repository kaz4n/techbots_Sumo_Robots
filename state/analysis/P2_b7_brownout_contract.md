# D244 B7 brownout bench software contract

27 September 2026. The user explicitly approved the dedicated B7-only exception
to R6 contact qualification. This contract implements the original P2 B7 trial:
a half-charged pack, twenty full-forward/full-reverse cycles, and no uptime reset.
Software/compile evidence cannot establish half-charge, motor motion or no reboot.
Actual B7 energization still requires fresh specific STAND OK and the existing
verified hardware/setup prerequisites. There is no upload or motor-run permission.

## Identity and preserved authority

Use compiler-wide SUMOX_B7_BROWNOUT, default0, exactly0/1. It is mutually exclusive
with MATCH and every existing bench/trial/probe/timing profile. Ordinary profiles
retain existing behavior, data layout where possible and R6 contact qualification.
Only the actual Robot -> sole Governor pass -> actual MotorGate path may command
outputs. Do not fabricate contact/opponents, edit a RobotResult after production,
write motor pins from another module or introduce remote motion commands.

Real initialization/source/button qualification and the existing local START
release plus COUNTDOWN_MS+COUNTDOWN_MARGIN_MS hold are required. The dedicated
profile uses OPENER only as its existing gated motion state; opponent perception
remains truthful but cannot route the stress sequence into combat or stall logic.
A dedicated B7 report identifies this trial; OPENER or generic CSV alone does not.
All default setup grants remain absent. The selected M0 wrapper remains inert.

## Electrical target and fixed finite sequence

New config-only constants, with no existing value change:
- BROWNOUT_CYCLES=20U; exactly the original fixed number of forward/reverse pairs.
- BROWNOUT_FULL_DUTY=1.0F; both sides share this signed electrical endpoint.
- BROWNOUT_DWELL_MS=500U; continuous acknowledged endpoint population per leg.
- BROWNOUT_REACH_MS=1000U; strict deadline for reaching each leg's endpoint.
- BROWNOUT_RECEIPT_MAX_GAP_US=2000U; inclusive maximum admitted decision/receipt gap.

After qualified GO, leg0 requests(+1,+1), leg1(-1,-1), repeated through leg39.
Twenty cycles means forty completed full-duty dwells, not twenty sign requests.
A new B7_ELECTRICAL Governor profile has cap1 and electrical target scale1. It
retains the same finite battery checks/filter, inhibit/brake behavior, acceleration
slew and zero-before-reversal shaping. This is the dedicated full-power bench
interpretation under D244/D051; normal B6 compensation and ATTACK remain unchanged.

The first request and each sign reversal still ramp through the actual Governor;
there is no bypass or instantaneous positive-to-negative output. MotorGate's
independent full-duty test admits only the specifically compiled B7 active-drive
report in OPENER, with coherent leg/sign, both wheels same sign and no stopping,
contract/escape/source fault. All existing token, time, countdown and finite-duty
checks remain. Escape outputs use their normal caps, not the B7 exception.

## Qualified applied receipts and boundaries

The pure helper owns no motor authority. It starts once at real GO. Robot::receive
may cache the previous validated Gate receipt but must not advance the trial there:
current STOP, source/application/clock fault and edge arbitration happen first.
The pending command carries its B7 phase/leg identity. Only its matching actual
applied receipt can enter the helper; previous/foreign/duplicate receipts cannot
be reassigned to a new leg. No retrospective loop advances multiple phases.

A qualified endpoint receipt is valid, correctly owned and time-ordered, enabled,
and has BOTH applied duties exactly the current signed1.0. Neither a request nor
a float tolerance, disabled M0 output or quantized subfull duty earns endpoint or
cycle credit. Applied receipts acknowledge successful PWM transactions; they are
not measured waveforms, continuous EN-high, wheel speed or physical power evidence.
MotorGate's existing per-transaction EN-low setup/settle interval is preserved.

Each leg starts at the decision that first chooses its request. A first endpoint
is eligible only if applied_us-leg_started_us is strictly below1000000us. An
endpoint applied exactly at the deadline loses. A valid receipt applied before
the deadline may be delivered afterward within the admitted gap; evaluate that
receipt first, otherwise decision elapsed>=deadline faults REACH_TIMEOUT.
The dwell starts at that first full receipt's applied_us. Subsequent consecutively
owned full receipts must remain within2000us inclusive in both decision and
applied chronology. At applied elapsed>=500000us, close this leg once. Any disabled
or subfull receipt after dwell begins faults ENDPOINT_LOST immediately; no dwell
restart or indefinite retry. Missing/invalid ownership or chronology faults;
reverse/ambiguous half-range time faults; ordinary uint32 wrap is supported.
Duplicate observations never advance time, dwell, counters or pulses.

A completed reverse dwell increments cycles once. Completing reverse leg39 records
cycles20/legs40 and COMPLETE, immediately requests inhibit/zero/brake on that
observation, and asks the real Lifecycle for terminal STOP on the next distinct
tick. Final counts/timestamps and the first terminal reason are immutable.
M0 must never complete a full-duty leg or cycle; it ends truthfully on its endpoint
deadline. No simulated applied endpoint may substitute for this negative case.

## Safety priority and lifetime

Current STOP/fault and current edge arbitration win even when the preceding full
receipt would otherwise complete a dwell or cycle. STOP/fault inhibits through
the existing authority path. Edge permanently interrupts the stress attempt and
uses the existing R5 escape with its usual caps; successful escape exit inhibits
and requests terminal STOP. An escape fault remains inhibited. No trial resumes
after edge escape, completed sequence, timeout, reset request or any abort.

D103 Runtime/Transaction service-reset paths refuse this profile. B7's public
Robot::reset preserves the instance, tokens and evidence, consumes any not-yet-
terminal attempt as RESET_REQUEST and latches stopping; terminal first reason and
counts remain intact. The next distinct admitted tick requests actual STOP.
The reset method itself has no hardware-I/O/immediate-stop claim and duplicate
timestamps remain passive. Other profiles' reset semantics do not change. A new
object/hardware reboot starts normal BOOT and needs a fresh qualified START; a
reboot during the physical trial invalidates that trial instead of renewing it.

## Report and physical acceptance boundary

Retain fixed-size report fields for phase, current leg/index, completed legs/cycles,
first reason, current request, start/leg/first-endpoint/last-endpoint/terminal
anchors with validity, last receipt token and bounded acknowledged uptime from
start. No heap, arbitrary callbacks or unbounded loops. The declaration-only
helper API is frozen with this contract before implementation tests execute.
Do not label a volatile report as proof that no reset ever occurred.

Actual B7 acceptance additionally needs a reviewed build/attempt identity,
half-charge evidence, verified stand/electrical setup, observed directional motion
and continuous observer-owned uptime/boot continuity from before START through
final stop. Gaps, reset/reconnect, missing endpoint evidence or an unsealed trial
are not PASS. Current25Hz CSV is insufficient to reconstruct every per-tick dwell;
retain the dedicated report and require exact source-bound readout/continuity
qualification when that real run is possible. This change introduces no new live
transport or native reset-cause claim. Board-only compile checks cannot close B7.

## Required focused verification

Freeze independent contract fixtures before the author's first implementation
execution. Cover exact20 pairs/40 endpoint dwells through genuine Robot/Gate,
full hold and MotorGate writes, high/low voltage electrical endpoints, ordinary
R6 regression, slew and sign-zero, M0 never-count, both-wheel/ownership rejection,
phase boundary receipt reuse, strict deadline ties/delayed delivery, endpoint
loss, inclusive gap boundaries/wrap/duplicate/backwards clocks, first reason and
one-shot behavior, current STOP/edge/fault over final count, public/service reset
refusal, native-source Runtime composition, missing grants and profile exclusion.
Keep every existing locked test unchanged. Use serial focused strict host and
sanitizer checks plus justified current target compile-only M0/M1 and ordinary
production checks. Independent scoped review must close material findings.
No build success, test double or offline artifact is a physical test result.

## Frozen public API and oracle clarifications

Declaration-only src/core/brownout_sequence.h is2992 bytes, SHA256
ff16d6a4fab0dcc19fbe16068d347d96a60947a96d3776b142655c68705a89f7.
Its names/fields are the public fixture surface. RobotResult adds the conditional
brownout report, brownout_stopping, brownout_edge_interrupted and constant
BROWNOUT_PROFILE identity. Endpoint-valid flags preserve observed historical
anchors on abort; phase/reason determine whether a dwell is still active.
A new decision replaying an old receipt token faults; only duplicate decision
timestamps are passive. An owned disabled/zero M0 receipt is permitted in REACH
until the strict REACH_TIMEOUT; it never creates endpoint or cycle credit.
Acknowledged elapsed time is derived from retained start/last-applied anchors,
within the finite trial bound. It is not a new native boot-uptime/reset counter.
