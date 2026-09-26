# D243 P2.2 outer-loop timing preparation

27 September 2026. Coordinator adopted D243 under D051 before implementation;
independent review remains required. This supplies measurement preparation for the existing
SUMOX_TIMING_EVIDENCE application profile. It supplies no physical timing result,
source grant, motor authority, all-sensor qualification or phase acceptance.

## Measured boundary and population

Let E[n] be the microsecond timestamp read at the start of application loop call
n. The retained duration is E[n+1] minus E[n], using checked modular chronology.
It is a loop-entry-to-entry wall interval and conservative execution envelope,
not isolated CPU time or calibrated WCET. It includes Runtime::step before S,
successful, failed, idle and terminal paths, D229 observation and completion
bookkeeping, classification/storage, loop return, the installed framework's
hook/yield/interruption gap, and the next entry timestamp boundary.

At E[n], constant-time observation closes interval n-1. That work is inside
interval n; histogram work is therefore delayed by one sample rather than hidden
after an alleged complete end timestamp. The first interval instead includes
arming work and has no previous interval to publish. No overhead is subtracted.
Target clock scale/quantization, timestamp latch semantics, generated code and
observer perturbation still need physical calibration. Interrupt/framework gaps
must not be relabeled as isolated Runtime execution.

The first loop entry after setup anchors one lifetime window A. Population
membership is the interval's START in [A, A + 300000000 microseconds). The fixed
five-minute duration is a diagnostic constant, not a control deadline. Keep the
whole last interval when its next entry crosses the boundary; do not clip its
duration. Preserve its start/end and closing overshoot. This window includes
startup/warmup and cannot claim five minutes of qualified live sensors.

At the first admitted entry outside the window, close its final in-window
interval and freeze the population. Retain exactly one following drain interval
outside that population to expose the last publication/closure work, together
with the actual Runtime call and framework gap during that interval. The final
drain timestamp's storage/freeze/return tail remains unmeasured. Do not recurse
into further drain measurements or claim perfect self-measurement.

If the next entry never arrives, the pending interval has no known duration.
OPEN or DRAINING plus its pending anchors remains incomplete, not SEALED success.
Runtime::step executes exactly once on every loop call, including closure,
draining, observer-error and sealed states. No observer state aborts or changes
the Runtime, its scheduling, motors, sources or grants. No automatic rearm/reset.

## Classification and fixed evidence

Preserve step's return value and pre/post Runtime phase, epochs, fault and
initialization context. A completed poll returns true or demonstrably advances
the nonsaturated epoch counter by one. A later stop-bookkeeping failure can
therefore be both a completed poll and a failed poll. Keep those populations
explicitly overlapping, rather than dropping the failed completion.

Differentiate early/idle polls, newly failed polls and already terminal polls.
In particular, false alone does not establish idle or failure. Preserve the
first failure's raw context, the pending/last context, classification counts and
class maxima. A saturated epoch counter or impossible transition must expose
uncertain classification; it must not fabricate completion from a zero delta.

Retain two fixed 800-bin distributions: every accepted in-window interval, and
the completed-poll subset. This prevents frequent idle polls from diluting the
completed-poll p99. Use the existing D229 distribution implementation unchanged:
exact integral nearest-rank p99 below 800 microseconds, explicit overflow,
unclipped maximum, count saturation and retained-prefix semantics. The 800-us
histogram edge does not change any runtime or safety threshold. New histogram
storage is approximately 6.5 KB; actual compiled layout remains to be checked.
Completed-labelled p99 is not reconstructed per-epoch CPU cost: delayed observer
work for a completed poll can fall inside a following idle-poll interval.

The observer stores a const-readable raw record and exposes a const summary.
Summary may scan the bounded bins only outside loop execution; the application
does not invoke it during sampling or sealing. Frozen raw distributions,
population/clock status, class counts/maxima, anchors, first fault and drain
record suffice to derive the complete sealed summary. No collection transport
or guessed target address belongs to this change. Const access is not atomic
capture; a future reader must establish exact layout and immutable sealing.

## Clock, bounds and incomplete evidence

Every consecutive entry uses uint32 modular subtraction; delta below 2^31 is
admitted and an ordinary single wrap is valid. Delta at or above 2^31 is an
ambiguous/reversed-clock failure. Equal timestamps are valid quantization until
a fixed diagnostic consecutive-no-advance limit is reached. That limit reports
stalled-clock evidence, not an elapsed-time claim. No new clock reads are added
inside Runtime or its native owners.

The first invalid/stalled clock record retains the offending raw entry, prior
entry and pending Runtime context. Freeze the known prefix with failure status;
do not insert an invalid duration, silently skip it or replace it with zero.
Likewise saturation is explicit partial evidence, not a five-minute success.
No uint32 scheme proves absence of an unobserved whole-clock wrap or a long
suspension; physical continuity/provenance remains a separate requirement.

Membership, close/drain status, interval validity, percentile overflow and
classification validity are distinct. SEALED means the bounded data publication
finished; it alone does not mean every duration was below 800 us, sources were
ready, five minutes of live sensing occurred, or P2.2 passed.

## Scope and focused checks

Owned source: new src/app/outer_loop_timing.h, a SUMOX_TIMING_EVIDENCE-only binding
in src/app/app.ino, and new diagnostic window/stall constants in src/config.h if
needed. Ordinary MATCH preprocessing introduces no observer object, clock read
or observation work. Keep a named retained diagnostic owner for future exact-ELF
readout, with a narrow compiler-retention mechanism rather than assuming an
unused C++ global survives optimization. Account for any retention work in the
entry intervals and the explicitly excluded final freeze tail. Verify its actual
symbol/layout in the later timing-profile build. Reuse the existing nonzero
APP_CLOCK_STALL_MAX_POLLS count for consecutive equal entry stamps; this changes
no Runtime stall rule or elapsed-time threshold. Initialization_complete is
context only: its readiness latch does not require IMU or prove continuous
all-sensor liveness.
Do not modify Runtime, D229, native HAL, control policy, legacy bench wrappers,
build/deploy/capture tools, source grants or locked tests.

Focused host tests cover first/last membership, exact boundary and straddler,
normal wrap, equality/stall, backwards/half-range failure, missing next entry,
one drain and immutable sealing; histogram rank/overflow/saturation and class
overlap; actual Runtime success/early/failure/terminal and post-completion fault;
allocation guards and real app-entry profile exclusion. Reuse existing Runtime
fixtures and serial strict C++17/UBSan harness machinery. Preserve failures and
compact exact-input receipts; no broad inherited-suite rerun.

Root controls later current timing-M0 and production compile-only checks. No
native command, upload, reset, physical test, new capture framework or claim of
operator readiness is authorized by this contract.
