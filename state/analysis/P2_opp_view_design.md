# Next P2 software task: opponent-view bench

2026-09-23 Asia/Dubai. Read-only design inventory; only this document is changed.
This is input to a new scoped contract, not implementation, upload approval or
physical B1 acceptance. D105/D106 validation remains the coordinator's current
task. No existing display, configuration, test or shared ledger is changed here.

## Smallest useful scope

Add `bench/opp_view`: one existing `opp_sensors::Sensors`, one existing
`ui::UnoQMatrix`, and a small pure bench controller with direct callback bindings.
Show seven polarity-normalized current channels in literal index order, with an
explicit unknown/error display. Preserve raw electrical bits, every signed native
status, validity masks and actual source timestamps in its report. Do not run
Robot, Fusion, Runtime, MotorGate, ADC, QTR, IMU, recorder or UART for this bench.
No remote input or transport is needed for its first software increment.

P2 B1 explicitly calls for seven live matrix bits, polarity/range checks, and
zero false hits for 60 seconds on an empty ring (`docs/prompts/P2_hal_bench.md:11`).
The existing `bench/p2_opp_compile` only retains a never-called driver probe;
its setup stores a function address and loop is empty. It does not implement B1
(`bench/p2_opp_compile/p2_opp_compile.ino:1`, `src/opponent_probe.cpp` below it).

The new sketch must assert `MATCH == 0` and `MOTORS_ALLOWED == 0`. Its initial
`setup()` passes all-false grants. Neither a successful compile nor the existing
bare-board matrix authorization supplies exclusive opponent-pad ownership or
electrical approval. An all-false bench should perform no native begin/read/
submit calls, including no calls merely to obtain an expected rejection.

## Existing interfaces and their limits

- `src/hal/opp_sensors.h:8`: `InitResult` exposes `ready`, `configured_mask` and
  seven signed setup statuses; `Snapshot` exposes full/partial validity, raw bits,
  seven signed read statuses and `started_us`/`completed_us`. `Sensors::begin()`
  is setup-only; `read()` is one bounded seven-channel pass. Construction has no
  I/O. Failed setup must not become a polling retry or a fabricated ready bank.
- `src/hal/opp_sensors.cpp:32`: mappings are validated before the first configure,
  and the driver requests only `GPIO_INPUT`, without pull/output/interrupt flags.
  It preserves negative errors and unexpected positive read values. A read failure
  does not revoke initialization; a later explicit read may recover. Never turn
  an invalid active-low read into a detection (`P2_opponent_contract.md:29-43`).
- `src/hal/ui_display.h:10`: `ui::Frame` is an existing fixed 104-byte, row-major
  8x13 frame. D088 uses 0/off, 7/on and 3/unknown; these representation values are
  suitable for a small bench-only renderer. Its general `DisplaySample` renderer
  is available, but its current sensor geometry has the discrepancy below.
- `src/hal/ui_matrix_unoq.h:13`: `MatrixGrant` defaults both normal startup and
  exclusive boot ownership to false. `UnoQMatrix::begin()` is one boot-lifetime
  claim, and `submit()` validates every frame/context and limits actual writes to
  `config::UI_FRAME_PERIOD_US` (currently 40000). Returns are explicitly
  `INIT_UNCONFIRMED`/`SUBMITTED_UNCONFIRMED`, not optical success. Local faults are
  reset-only; there is no release/reinitialize recovery API.
- `src/hal/ui_matrix_unoq.cpp:37`: actual matrix writes save/restore PRIMASK and
  copy one frame. The bench must use this owner, not direct matrix C APIs,
  Arduino graphics, a second writer or a new interrupt policy. The normal-startup
  restriction and inherited animation/loop-hook review remain applicable
  (`P2_matrix_contract.md:70-100`, `src/hal/loop_hook.cpp`).

## Concrete existing finding: front-channel display order

**OPP-VIEW-1: D088's sensor geometry swaps the first two front meanings relative
to B0/D076. This is a separate production-display finding, not a pin-map change.**

`docs/BEHAVIOR.md:19` defines bits 0/1/2 as FL15/FC/FR15.
`docs/HARDWARE.md:66` and `state/analysis/P2_opponent_contract.md:5` put those
channels at the unchanged proposed indices 11/12/13. The installed-map audit
agrees (`state/analysis/P2_opp_gpio_audit.md:59`). Actual core code agrees:
`src/core/opp_fusion.cpp:12` maps 0x01 to -15 degrees and 0x02 to centered zero.

In contrast, `state/analysis/P2_matrix_contract.md:45` lists FC,FL,FR at
(4,1),(2,1),(6,1), and `src/hal/ui_display.cpp:93` indexes those positions directly
by bit. Passing the unchanged production mask therefore places FL15 at the
center and FC at the left position. `displaySample()` passes `result.opponent_mask`
unchanged (`src/hal/ui_display.cpp:201`). Existing literal D088 tests may encode
that adopted layout; they must not be silently rewritten as part of this bench.

The coordinator explicitly selected a literal channel-index strip for this next
bench. Do not modify the production display or silently permute the raw mask.
Record a separate scoped resolution of OPP-VIEW-1 before claiming the existing
production geometric display correctly identifies front channels.

## Proposed presentation and public seam to freeze

Use a pure bench-only renderer over the existing `ui::Frame`, with no font or
robot geometry: columns 0,2,4,6,8,10,12 correspond to channel indices 0..6. Rows
2 and 3 repeat each live bit for visibility. For a fully qualified current bank,
pixels are 0 or 7. For a disabled/uninitialized/invalid bank, all seven positions
are 3. Row 0 is a latched "setup/read error has occurred" stripe after any requested
setup/read failed or evidence was malformed; disabled acquisition alone is unknown,
not an API error. This retained indication prevents a transient invalid sample
between two 40ms display opportunities from disappearing unnoticed. Recovery may
restore current live bits while retaining the historical error stripe/count.
All other pixels are zero. This layout is a proposed structural representation
for the next contract, not a new behavior tunable or measured optical result.

Normalize a qualified bank exactly once for presentation:
`(raw_mask ^ config::OPP_ACTIVE_LOW_MASK) & 0x7f`. Retain the untouched raw mask
and validity/status evidence beside it. Use no debounce, phantom masking, contact
logic or guessed polarity. The documented default is 0x78; reference the actual
config symbol, not a duplicated literal. The literal index legend may cite D076's
FL15/FC/FR15/SL/SR/RL/RR order as a proposal, without asserting physical wiring.

Qualification should require successful full setup, exactly seven valid bits,
no high raw/valid bits, all statuses in {0,1}, and each status matching its raw
bit. The snapshot must fit the actual current outer read interval in the forward
half-range. Inconsistent `valid` flags/masks/statuses are invalid. Partial reads
remain in diagnostics but never look like a complete fresh bank. One later
genuine valid read may restore the live display; do not retain old live bits over
a failed read. Treat clock discontinuity as a terminal bench fault, not a sensor
measurement, and perform no further I/O after that fault. A terminal clock or
matrix fault may leave the previous optical frame visible; the report must mark
the bench stopped, and no retained image may be described as a current sample.

Suggested new interface, to be frozen before independent tests: a fixed `Port`
with one context and `clockUs`, `beginOpponents`, `readOpponents`, `beginMatrix`,
`submitMatrix`; `Grants` with separate default-false opponent/matrix enablement
and the existing default-false `ui::MatrixGrant`; a noncopyable `Runner` with
one-attempt `begin`, one-step `poll`, and a const report accessor. Missing required
callbacks reject before setup I/O. Disabled callbacks are never called.
Keep this bench seam local; do not reuse `app::NativeSources`, which carries
unneeded QTR/ADC/IMU owners, or fabricate Robot input/results for `displaySample`.

## Files and ownership

Implementation worker: `bench/opp_view/opp_view.ino`,
`bench/opp_view/src/opp_view.h`, `opp_view.cpp`, `opp_view_native.h`, and
`opp_view_native.cpp`. The pure runner/renderer belong in the first header/CPP;
the native pair owns exactly one Sensors and one UnoQMatrix and forwards the
five callbacks directly. The sketch delegates setup/loop and supplies `{}` grants.
No constructor calls `begin`; no global constructor changes a pad or matrix.

Independent author: new `tests/test_opp_view.cpp` and a small dedicated native
binding/startup test under `tests/tooling/`. They should use the frozen interface
and literal expected pixels/callback traces, not implementation-derived oracles.
Coordinator: contract/public header, required build/source-copy lists, compile
receipts, review, documentation/ledgers. Existing production drivers, display,
config, all locked tests and their assertions stay outside implementation scope.

No motor object is needed. The bench must issue no EN/PWM request, including an
ad-hoc attempt to drive EN LOW. Any future motor inhibition operation belongs to
the existing MotorGate boundary under separately authorized scope. Consequently
this sensor-only diagnostic does not establish a powered robot's safe motor
state; the later physical setup must explicitly address disconnected/inhibited
motor hardware rather than infer safety from `MOTORS_ALLOWED=0`.

## Source, display and complete-poll timing

Use only actual clock callbacks. Reuse `config::TICK_US` for one sampling release
per millisecond and `config::UI_FRAME_PERIOD_US` for display cadence; add no new
timing default. Admit at most one real sample per poll, skip missed grid releases
with explicit saturating missed counts, and never fabricate catch-up samples.
Early calls perform at most clock admission, not sensor or display callbacks.
Normal uint32 wrap is valid; backward/half-range jumps fail. Frozen clock must
not trigger repeated reads/submissions or an internal busy loop.

Record an outer acquisition start before the native read and an observation
immediately after it. Validate the driver's actual started/completed timestamps
inside that bracket, preserving its sequential-read limitation: the seven bits
are not simultaneous. Retain source-read duration and whole-call duration
separately. Render from the latest qualified current sample only when a display
is due. Bracket render/submission and end the poll with a real clock observation
after all work included in its measured duration. Counters should distinguish
attempts, valid/invalid reads, missed releases, matrix throttles, submissions and
fault statuses. Preserve first error/status evidence; saturating counters must
expose saturation rather than silently wrap.

The maximum measured poll must include sampling, qualification, rendering,
matrix validation/submission and in-poll diagnostics, not just `Sensors::read()`.
If later external diagnostic publication occurs after the runner's closing
timestamp, measure that outer work separately; do not label the inner duration
as the complete loop. Setup timing is separate from steady-state polling.
Read/setup GPIO functions have fixed call counts but no application timeout
parameter; the design cannot promise physical hard WCET from those counts.
Host simulated durations prove accounting only. Actual <800us, 5-minute full-app
WCET, clock calibration, IRQ interference and matrix visibility remain separate.

## Required software evidence and deferred physical acceptance

Before target review, independent host cases should cover all four grant
combinations; all-false and repeated setup silence; missing callbacks; all 128
raw masks under configured polarity; seven-channel setup/read error positions;
negative and unexpected-positive values; inconsistent masks/statuses; exact
unknown/error pixels; valid recovery after transient read failure; no stale bit
reuse; natural wrap, reversed/future source times, deadline/missed-grid edges;
zero-catch-up behavior; display cadence and native status accounting; and total
poll duration including slow/error display callbacks. Native binding tests must
execute the real new binding with counted existing owners and prove no motor,
Bridge, UART or unrelated source calls. Keep existing D076/D088/D106 native
assertions and full host/sanitizer suites unchanged.

Compile only through `tools/board_tool.py flash bench/opp_view --compile-only`
after the files exist. Current generic bench builds differ from the checked
app/runtime_inert policy (`tools/board_tool.py:316-326`); do not claim D100 policy
coverage unless the coordinator explicitly extends and verifies it. Audit the
exact staged source and retained ELF, one sensor/matrix owner, all-false setup,
empty strong loop hook, startup/imports and ordered loader fit. A type name or
MOTORS_ALLOWED macro alone never certifies initialization or upload safety.

Current upload allowlist rejects `bench/opp_view` before transport
(`tools/board_tool.py:295-299`). Leave that restriction in place. A later physical
run needs explicit electrical/pad/matrix ownership and startup scope, exact
source/artifact review and the corresponding reviewed upload policy. The old
synthetic `ui_matrix` grant does not authorize opponent inputs. P2 B1 then still
requires actual polarity, per-sensor black-box ranges and the 60-second empty-ring
observation with invalid/missed evidence visible. No such measurement, new
wiring assumption, motor permission or human phase gate follows from this design.
