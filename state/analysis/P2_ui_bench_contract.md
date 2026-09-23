# D112: finite A1 raw and decoder evidence bench

Adopted2026-09-24 under D051/D075 after separate author and source/API preflight.
Implementation and independent execution follow the frozen public contract. This is the smallest
remaining B6 acquisition bench, not a claim that all of B6 is implemented or
physically accepted. References: `docs/prompts/P2_hal_bench.md:16`,
`P2_adc_pair_contract.md`, `P2_button_routing_contract.md:9`,
`src/hal/power.h:32`, `power.cpp:325,485`, `src/hal/ui.h:9`, `ui.cpp:71`.

## Fixed scope and declarations

Files are `bench/ui/ui.ino` and
`bench/ui/src/{ui_bench.h,ui_bench.cpp,ui_bench_native.h,ui_bench_native.cpp}`.
Public declarations are in `bench/ui/src/`; original reviewed drafts remain in `P2_ui_bench_headers/`.
Use exactly one existing power::Reader, beginWithButtons() once and readButtons()
only thereafter, plus the existing pure ui::decodeButtons(). Native owns that
Reader directly and forwards clock/begin/read callbacks. No InputOwner, second
ADC owner, battery read(), arbitrary channel, Runtime, Robot, MotorGate, matrix,
IMU, QTR, UART/Bridge, transport or remote control. Construction, destruction,
port creation and accessors are passive. No decoder reimplementation or logical
gesture/debounce copy. Including the public ui.h does not instantiate a Robot.

The adopted sole new config value is uint32 UI_BENCH_SAMPLES=128. Cadence uses
existing TICK_US; no pin, ADC guard, decoder window, age or voltage default changes.
The sketch requires MATCH=0/MOTORS_ALLOWED=0 and uses Grants{} with
exclusive_adc=false. This API expresses a prerequisite; the contract supplies no
physical permission. No upload key is added.

Store the first configured count of admitted raw-source Capture records in
fixed RAM, without overwrite, filtering, voltage conversion or synthesized
samples. Each includes the unchanged ButtonSample and actual ButtonDecode.
captureCapacity() returns the configured count; captureCount() equals
Report.captured_samples. capture(i) is const and non-null iff i<count. Published
records remain unchanged for the Runner lifetime, including after failure.
A zero-capacity profile may use one inaccessible array placeholder for valid
C++ syntax only; its effective capacity remains zero. Private storage/helpers
are assigned to the implementer; this contract permits only private fixed storage/helpers to be added during implementation.

## Begin and admission prerequisites

begin is one attempt. Repeating it returns false, changes nothing and invokes
nothing. False exclusive_adc takes precedence over every check: true/DISABLED,
no callback, including clock. Enabled begin checks all three callbacks, then
wrapper config, before any callback. Null context is allowed for stateless
callbacks. Missing callback is PORT. Wrapper config requires positive capacity
and 0<VBAT_ADC_CONVERSION_US<=TICK_US<2^31, otherwise CONFIG. Invalid zero-period
profiles still compile under strict C++17 warnings, using an explicit compile-time
guard instead of a substitute period. Native setup/config ownership validation
stays in Reader, including its existing ADC reference/divider prerequisites even
though this bench records A1 raw counts rather than battery voltage. A native
INVALID_CONFIG is retained as SETUP; nothing bypasses or weakens those checks.
Decoder config validation stays in ui::decodeButtons.

Enabled begin observes S, calls beginButtons exactly once, then observes A
immediately after return. Retain the actual InitResult and classify it before
evaluating A chronology: unknown Status/Shutdown is CONTRACT; a known non-OK
status is SETUP, including ALREADY_STARTED regardless of ready; OK requires
ready=true and shutdown=NOT_ATTEMPTED or is CONTRACT. Every public enum through
NOT_ENABLED and every Shutdown value is known. With accepted A, observe C after
validation/counter work, even on a nonclock setup fault. Only fault-free accepted
C enters RUNNING and returns true. The first RUNNING poll is immediately due.

## Poll cadence and finite capture

Each poll clears fresh. Outside RUNNING, it returns false with no callback and
no other mutation. A RUNNING entry increments poll_timing.calls, clears its
last_valid and observes S once. Rejected S faults without a read or more clocks.
Otherwise first read is due; subsequently due means accumulated age since the
last committed sample.started_us >= P=TICK_US. Early polls increment not_due and
return false after S alone: no read, A/C or measured poll duration. Retained
sample/decode/read timing/last_read_accepted do not change on these polls.

A due poll makes one readButtons call, with no wait, retry, catch-up or burst.
At actual invocation add floor(age_at_S/P)-1 to missed_releases, or zero for the
first read. Capture.missed_before stores that local value. These are unserved
cadence releases, not inferred missing ADC conversions; count them even if that
read/A/C fails. Age P or 2P-1 skips zero, 2P skips one, 3P+1 skips two. Time after
S does not alter this call's skip count. Counters saturate without adding reads.

Only successful C reanchors source age to C-new_sample.started_us. Until then
retain the previous source-era accumulator. A delayed C may make the next poll
immediately due; there is no extra C-based skip calculation. A failed read is
terminal and never reanchors. Frozen time can keep polls early indefinitely;
finite storage does not assert an independent wall-time watchdog.

## Actual diagnostics, source admission and publication

Immediately before the native read, increment read_timing.calls, clear its
last_valid and set last_read_accepted=false/decode_matches_sample=false. Save the
actual returned ButtonSample unchanged and set sample_seen=true alongside that
saved result, before observing A immediately. No validation or decoder work
precedes A. This return remains sample_seen even if A fails. Apply the raw-result precedence below, then evaluate A chronology.
Rejected A suppresses decoder delivery and every later clock/callback; retain
the previous Report.decoded with decode_matches_sample=false. For admitted A,
call actual ui::decodeButtons exactly once on the actual returned sample, even
if raw semantics already failed. Store the complete actual output and set
decode_matches_sample=true, without replacing a primary wrapper fault. Decoder
delivery precedes successful source admission and C. No injected decoder
callback or copied classification. Before the first read, sample/decoded are
their declared defaults and sample_seen=false/decode_matches_sample=false;
these defaults do not claim an executed decode.

Classify raw results before A chronology, in this order:

1. Unknown Status/Shutdown, status/valid disagreement, or known non-OK with
   nonzero raw or sequence is CONTRACT. D086 promises invalid raw/sequence zero.
2. Known non-OK with valid=false and raw=sequence=0 is ADC. Preserve its actual
   timestamps, shutdown and decoder output; do not impose success-only source
   brackets or a conversion duration on native failure/cleanup.
3. OK requires valid=true, shutdown=NOT_ATTEMPTED and raw<=16383, else CONTRACT.
4. Evaluate A chronology independently. Only after admitted A and valid raw shape,
   require unsigned offsets `0 <= start-S <= completed-S <= A-S < 2^31`, source
   duration strictly below VBAT_ADC_CONVERSION_US, and sequence first1 then
   previous committed sequence+1 in uint32 arithmetic. Violations are SOURCE_ORDER.
   Equality at the default100us conversion limit fails. Raw0/16383 and repeated
   numeric readings on successive distinct sequences are permitted.

An actual decoder result never grants source/clock acceptance or replaces the
wrapper's first fault. For admitted raw conversions, all actual qualifications
are retained without modifying them: UNCONFIGURED, UNKNOWN and AMBIGUOUS remain
unqualified evidence; even INVALID caused by malformed decoder config is useful
raw/decoder evidence and does not stop this raw capture. No decoder-valid claim
follows from capture publication, COMPLETE or last_read_accepted. Only the
actual decoded.evidence.presence/contract_valid/qualification describe logical
interpretation. In particular, an INVALID-presence level NONE is not a release.
The production unconfigured windows stay unconfigured. This explicit choice
avoids cloning decoder config checks merely to prevent observing their result.

For an admitted raw result, copy sample, actual decode, S/A, qualified source
duration, S..A read duration and local missed count into the next unpublished
slot before C. C follows decoder/validation/tentative copying/ordinary counter
work. Only after fault-free accepted C store C and S..C duration, increment
captured_samples, set last_read_accepted/fresh=true and return true. Those closing
publication fields are explicitly outside S..C. Bad C hides the tentative slot
and preserves the prior count. At capacity enter COMPLETE before returning;
the final record is true/fresh. No extra read, clock or implicit shutdown follows.

The first1/contiguous rule is this new Reader bench's exact D086 expectation,
not a change to Robot's broader sequence-admission API. With a new owner and128
captures, native sequence wrap cannot be reached; do not invent a private seed
or promise an impossible wrap run. Natural timestamp wrap remains required.

## Clock, timing and terminal ownership

All consecutive observed wrapper deltas are unsigned and strictly below2^31;
equality timestamps and natural wrap are allowed. Accumulate accepted deltas
inside each setup/due S..C bracket and from the last committed source start,
including early polls and inter-poll gaps. Reject cumulative age reaching2^31,
even if individual deltas are smaller. Before the first capture only wrapper
clock/bracket constraints apply. A wholly unobserved full wrap is unknowable.

Any rejected S/A/C sets clock_fault and primary CLOCK if no earlier fault exists;
it suppresses remaining callbacks/clocks and any decoder work not yet delivered.
Already returned data/pure decode are retained. Semantic result faults precede
A chronology; decoder delivery and successful source checks follow admitted A.
An admitted A measures S..A even on semantic failure. With no clock fault still
observe C and measure the failed nonclock path. No time or successful closure
is fabricated. First fault is immutable and terminal; clock_fault may additionally
record the remaining required observation after a nonclock failure.

Timing.calls counts actual beginButtons/readButtons calls for setup/read, and
RUNNING entries for poll. Setup is S..C, read is S..A, due-poll is S..C.
Source_us is completed-start in published captures. Attempt clears only that
category's last_valid; measurement updates last_us/maximum_us/measured_calls.
Unmeasured attempts preserve prior numeric history. In particular early/bad-S
polls do not change read timing. All diagnostic uint32 counters saturate;
counter_saturated becomes true only on attempted overflow, not exact max.
Capture count is capacity-bounded. sample_seen, last_read_accepted and
decode_matches_sample describe the latest actual read and remain historical
across no-read polls/faults. Report.decoded may describe an older operation after
bad A; decode_matches_sample=false explicitly prevents pairing it with the new
Report.sample. Its retained fields are not overwritten with an invented decode.
fresh alone is the new-record pulse, cleared even by passive terminal polls.

Reader has no public stop/disable/cancel/reset. COMPLETE or wrapper failure only
ceases callbacks: preserve actual Shutdown, normally NOT_ATTEMPTED on success.
Never fabricate DISABLED, force a failing conversion, recreate/destruct the
Reader to recover it, or manipulate ADC registers. Known native faults own
D078/D086's existing bounded cleanup; do not repeat it. A malformed substitute
result cannot manufacture a cleanup API. Boot-lifetime ADC ownership persists.
Future calls cannot overwrite first-failure diagnostics with FAULT_LATCHED.
Callback brackets/finite guards do not abort a blocked callback or prove WCET.

## Acceptance before any implementation/physical claim

Independent tests freeze from these public rules before first
execution, without implementation reads. Check passive grant/repeat/default
sketch, callback/config precedence, zero/one/default capacity, zero/half-range
period, all enum/shape/native-failure cases, first/equal/early/late cadence and
miss arithmetic, no bursts, raw endpoints/repeated values, first/duplicate/gapped
sequence, exact source brackets/conversion equality, clock wrap/cumulative
half-range/bad S/A/C, immutable final/partial capture, failed-C hidden slot,
historical flags, bad-A decoder suppression/provenance and separate timing categories.
Compare stored decode to the
actual existing decoder; synthetic profiles exercise valid/unknown/overlap,
unconfigured and malformed config while preserving each actual qualification.
They neither propose thresholds nor prove four physical button states.

The D110 public saturation profile also applies with test-only TICK_US and
conversion both1us, capacity>=5 and valid consecutive native sequences. After
first sample, equal S/start/end/A/C at source ages2^31-1,2^31-1,4,2 give local skips
2147483646,2147483646,3,1; total saturates exactly then overflows on the fifth
record. No private state seeding or physical1us conversion claim. Other enormous
counter paths may be source-reviewed explicitly rather than claimed executed.

Counted native-binding tests prove one Reader, beginWithButtons/readButtons only,
no begin()/read(), no other owner and passive construction/default sketch loops.
Keep all existing assertions unchanged. Later coordinator work owns literal
config registration, normal/sanitizer/target checks and the checked ui.ino inert
default/Immediate compile route. MATCH/upload/profile including symlink refusal
must occur before transport. Exact staged source/ELF/startup/import/conditional
loader evidence is required; compile exit0 alone is insufficient. This contract
authorizes the described software changes under D051/D075, with no physical run or pin grant.

B6 still needs verified electrical windows/settling/START-versus-BOTH resolution,
actual local-button gesture behavior, mode cycling/service-menu/countdown matrix
composition and physical display acceptance. `docs/HARDWARE.md:140` makes START
and BOTH nominally identical; SC-A remains open. Existing D087 logical services,
D088 display and D103 Runtime composition should be reused for subsequent work;
this short raw capture does not replace them or demonstrate a long-held gesture.
Later physical trials/readout need verified deployed identity, pad/ADC permission,
actual stimulus labels and separately reviewed capture retrieval. No physical
accuracy, timing, whole-loop800us, gate or wiring claim follows here.

Adoption: UI_BENCH_SAMPLES128 and the exact raw/decoder evidence rules above.
The coordinator adds one literal registry expectation, preserving every old byte.
No existing production behavior, hardware window, motor permission or locked test changes.
