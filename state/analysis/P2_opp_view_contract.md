# D107 opponent-view bench contract

2026-09-23 Asia/Dubai, selected under D051/D075. Implements the software for
P2 B1 using the existing native sensor and matrix owners. No wiring grant,
physical result, motor operation, upload permission or human gate follows.
Design references: P2_opp_view_design.md, D076/D088/D106 and P2 B1.

## Scope and presentation

Own only bench/opp_view and its new tests. One Sensors and one UnoQMatrix;
no Robot, Runtime, MotorGate, UART, recorder or unrelated source owner. Sketch
asserts MATCH=0/MOTORS_ALLOWED=0 and calls begin with all-false Grants. Preserve
the existing upload refusal. No motor-pin writes of any kind belong here.

Public bench-local Port/Grants/Report/Runner interface is opp_view.h. Ports are
copied at construction; no callback during construction. begin is one attempt;
repeated begin returns false without callbacks or changing retained state.
All-false grants take precedence over configuration checks and yield
DISABLED/true and no callbacks, including clock; later
polls return false without callbacks. Enabled ports require clock and only their
corresponding begin/read or begin/submit pair, validated before any setup I/O.
Validate existing TICK_US/UI_FRAME_PERIOD_US as positive half-range values and
OPP_ACTIVE_LOW_MASK with no bits above0x7f; invalid config fails before I/O.

During setup bracket requested sensor begin then requested matrix begin with
clock observations. A sensor setup is usable only with ready=true,
configured_mask=0x7f and all seven statuses0. Otherwise latch sensor_error but
continue the optional matrix setup/display; never retry sensor setup/read an
unready bank. Only INIT_UNCONFIRMED means matrix setup accepted; any other
returned status is a terminal MATRIX fault. Preserve all native result fields.
The two existing MatrixGrant fields pass through unchanged.

Bench rendering is literal channel order, not robot geometry: columns
0,2,4,6,8,10,12 correspond to indices0..6, on rows2 and3. Available current bits
use7/on and0/off; unavailable uses3. If sensor_error is latched, all13 pixels of
row0 are7. All other pixels0. Use the existing ui::Frame, completely overwritten.
No debounce or fusion. Qualified detection is (raw_mask ^ OPP_ACTIVE_LOW_MASK)
&0x7f; preserve raw masks/status/timestamps beside it. The existing production
display discrepancy OPP-VIEW-1 is documented separately, not silently changed.

## One bounded poll

Setup's final accepted clock anchors next_release_us. First due poll can run
immediately at that timestamp. Time is only actual Port.clockUs observations;
equality and natural32-bit wrap are valid, backward or half-range jumps latch
CLOCK and stop further I/O. No busy loop, repeated equal-clock sample, catch-up
read, delay, allocation or unbounded work. poll before begin/fault/disabled is
passive. Early RUNNING polls only observe one clock and return false.

For a due poll, start S is the admission clock. Count releases before the latest
grid point <=S as missed; consume that latest due point once. Next release is its
successor. If completion C passes further grid points, count/skip those strictly
before C; a point exactly at C remains due for the next poll. Use bounded
wrap-safe arithmetic and saturating uint32 counters with a visible saturation
flag. Preserve the original release grid rather than reanchoring to S/C.

At most one sensor read and one matrix submit per poll. If initialized, increment
read_attempts, take a clock immediately before read and after read, and retain
the returned Snapshot. Require valid=true, valid_mask=0x7f, no high raw bits,
every status in{0,1} matching its raw bit, and started/completed within that
actual outer bracket in forward order. Invalid or inconsistent evidence increments
invalid_reads, latches sensor_error, and saves the first failed Snapshot once.
Never present previous live bits as current after failure. A later valid read
can restore current availability while retaining the historical error indication.
If the post-read global clock fails, count that attempted read as invalid and
retain its evidence before stopping. Valid read duration is completed-started;
preserve last/max duration only for qualified reads. No sensor grant means no
read and unknown current bits, not a sensor error.

Render every completed due poll. For an initialized matrix, first submission
is immediately due; subsequent attempts require now-last_attempt >=
UI_FRAME_PERIOD_US. Observe clock before submission, pass that real timestamp,
then observe clock after it. SUBMITTED_UNCONFIRMED increments submissions;
THROTTLED increments throttles and is nonterminal. Any other status latches
MATRIX. Remember every attempted submit's timestamp, including THROTTLED.
Disabled matrix causes no matrix callbacks. Frame/report success is not optical
confirmation. A terminal fault can leave an old image physically displayed;
FAULT/current_available=false must never be reported as live evidence.

Finish with real clock C after qualification/render/matrix/counters. On an
accepted C retain last/max poll duration C-S, including an observed matrix
failure path, and increment completed_polls. No fake C or duration is published
when the closing clock fails. Set fresh=true/return true only for a completed
nonfault poll; early/fault/disabled returns false. First terminal fault remains;
no recovery or setup rearm. Setup duration is outside steady-state poll metrics.
The metric ends at C; publishing the measured duration/returning takes additional
instructions. An eventual outer loop measurement must include those instructions
and any diagnostic publication. Do not label this inner bracket full-app WCET.

## Validation and ownership

Coordinator owns contract/public header/build wiring/ledgers. Worker owns bench
implementation and native bindings. Independent author derives exact pixels,
trace/time and error expectations from this contract/public headers, not bodies.
Cover grant truth, callback absence, 128 masks, each invalid channel/status,
partial/malformed/future/reversed snapshots, recovery/error latch, grid/deadline
and natural wrap, display cadence/throttle/fault, measured complete callback
cost, repeated setup/early passivity, and exact real binding/default sketch silence.
No old or locked test changes. Host normal/sanitizers and native substitutions
are software evidence. Compile exact bench default and Immediate without upload;
audit source/ELF/owners/startup/imports and required normal-startup matrix grant.
P2 physical ranges, polarity, empty-ring60s, optical result and full-app800us
remain pending. Never infer electrical approval from this default-disabled bench.

## Pre-test observable clarifications

- Disabled means both enable flags opponents/matrix are false; unused nested
  MatrixGrant fields do not enable anything. Enabled begin returns true if it
  reaches RUNNING, including failed sensor setup with latched sensor_error;
  terminal fault and repeated begin return false.
- Every poll clears fresh before admission; repeated begin preserves every field.
- Unavailable detection_mask is canonically0, while the genuine Snapshot remains
  retained. A fault also makes current_available=false/detection_mask=0.
- Read/display attempts count actual callback invocations only: failure of the
  pre-callback clock does not add an attempt. A post-read clock failure counts
  the already attempted read invalid as specified above.
- Each enabled setup callback has its own immediate before/after clock pair.
  No shared boundary is assumed. The final post-setup observation anchors the
  release grid; no extra setup clock is needed. Stop immediately on bad chronology.
- Interpret a failed matrix result before observing its post-callback clock;
  it remains the first MATRIX fault if that subsequent observation regresses.
  Accepted closing C still measures the matrix failure path; invalid C does not.
- The native public seam is opp_view_native.h: Native owns exactly one Sensors
  and UnoQMatrix. port() returns direct callbacks and its own context without I/O.
  Tests may substitute those existing public owner methods to inspect the real
  new binding; this does not repeat or replace existing native driver validation.
- Also bound the aggregate accepted clock deltas within each active setup/poll
  interval below half-range. Several individually forward observations must not
  conceal a half-range or wrapped total interval. Reaching that boundary fails
  CLOCK without publishing a successful duration or grid update; no private
  seeded counter is needed to test this chronology rule.
- Preserve the matrix owner's separate timestamp contract: after its first
  attempt, accumulate accepted clock deltas since that attempt without wrap
  aliasing. If that gap reaches half-range, fail CLOCK before another submit,
  even if each poll/individual clock gap was smaller. No stale timestamp may be
  passed to the native matrix owner. With matrix disabled this extra bound does
  not apply. Equality at UI_FRAME_PERIOD_US still permits an ordinary attempt.

## Target build correction after generic artifact review

D107-R3 rejects the first generic artifacts: inherited Arduino Bridge/Serial
constructors run outside Runner grants; the image also retains thread/allocation
imports. Retention alone does not show that each imported operation executes.
Adopt the existing exact D100 native dependency policy for this one additional
literal project, opp_view.ino. Require MATCH=0/MOTORS_ALLOWED=0 for default and
Immediate compile profiles; reject MATCH before transport. Reject sketch.yaml/
sketch.yml before transport, including symlinks. Preserve every installed hash,
effective-command, no-library, preflight and result check. Other generic benches,
app and runtime_inert retain their existing routing and constraints. No upload
allowlist/key change. Matrix enablement still requires normal startup even though
the all-disabled bench also compiles with Immediate startup.

Add independent controlled route/profile/refusal tests and retain the rejected
generic source/artifacts as evidence. New checked artifacts need source, ELF,
constructor/import and conditional loader review; a compiler exit0 is insufficient.
