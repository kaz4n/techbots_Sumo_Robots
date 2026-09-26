# D229 completed-epoch timing distribution contract

Proposed under D051 and approved by the implementation coordinator on 27 September
2026; base `004dc7cff534896a851901f9d7d0ba6066cae060`. No native actions belong to
this change. Original P2.2 requires worst case and p99 over five minutes with all
sensors live, under 800 us. This change supplies distribution machinery only.

## Observation and identity

The population is every `Runtime::completeEpoch` transaction that successfully
finishes and whose completion clock is accepted. Its existing unsigned duration
is C minus S, with chronology already checked by Transaction and Runtime. One
sample is recorded after those checks, including a completed transaction whose
later stop bookkeeping fails. Failed/incomplete transactions and idle/early polls
are absent. Existing scheduling, clocks, maximum_execution_us, behavior, motors,
recorder and wire format remain unchanged. No reset/rearm is added: the population
starts with the first completion of this Runtime object's lifetime.

This S..C window excludes work before Transaction::open, the timing observer and
all completion bookkeeping after C, plus outer loop/idle/failed-poll execution.
It is NOT all-poll WCET, a full-loop duration or P2.2 acceptance. Later evidence
must separately measure the complete loop (including instrumentation overhead),
establish the actual five-minute capture interval and prove all sensors live.

## Fixed memory and public diagnostics

`config::TICK_DISTRIBUTION_LIMIT_US = 800U` is a diagnostic range, not a changed
scheduler or safety deadline. An asserted positive range no larger than 800 us
allocates one uint32 counter for each integral duration 0..799 us. Durations at
or above the limit have an explicit overflow counter; their actual maximum is
preserved. The histogram is private, with only const diagnostic access. The
small implementation is header-only so existing explicit-source host runners
gain no new linker dependency.

`app::epoch_timing::Distribution::observe(execution_us, started_us, completed_us)`
does constant bounded work: no loop, allocation, I/O, clock read or division.
`data() const` exposes a const `Data&` for source-bound memory/capture tooling.
`summary() const` returns a readable `Summary` by value and scans at most the
configured number of bins outside the tick. Runtime exposes only a const owner
via `epochTiming() const`; this adds no firmware command or transport.

For N retained observations the exact nearest rank is N - floor(N/100).
Summary status EMPTY means no samples; EXACT gives the exact integral p99_us;
RANGE_OVERFLOW means that rank lies in the overflow tail and p99_us is not valid.
INCONSISTENT rejects a histogram whose sum differs from the sample count. Status
SATURATED means later samples could not be retained; retained_status still
describes the fixed prefix and its p99 value is valid only if retained_status is
EXACT. No block maximum is presented as a per-tick percentile.

At UINT32_MAX retained observations, the next observation sets saturation, freezes
the histogram, retained count/max and retained last-completed anchor, and counts
rejections (itself saturating at UINT32_MAX, which means a lower bound). The
all-observed maximum and last-completed anchor continue to update. First-started
and last-completed values are raw modular microsecond anchors, not proof of elapsed
duration or continuity across multiple wraps. There is no automatic five-minute
window or reset. At an actually sustained 1 kHz, uint32 capacity would exceed
49 days; this arithmetic is not runtime-liveness evidence.

The new owner is appended to Runtime to avoid moving existing members. Fresh
source-bound target layout/addresses and coherent acquisition remain required;
old image addresses cannot be reused. Const access does not make concurrent RAM
reads atomic. Histogram sum validation is not proof of a coherent capture.

## Focused evidence and limits

New tests cover zero/empty, exact rank transitions, endpoint/overflow tails,
unclipped maximum, wrap anchors, uint32 count/bin saturation and rejection count,
plus actual Runtime successful completion, idle/failed/terminal/stale calls and
natural clock wrap. Synthetic near-limit data are seeded only in test code via
a const_cast of an originally nonconst owner; there is no production mutation
or reset API. Existing real Runtime allocation probes may run as a small focused
regression. Compiler/run output, source pins and measured host object sizes are
saved in the validation receipt. Host timing cannot bound target observer cost.

Owned production: new src/app/epoch_timing.h; narrow additions to src/config.h,
src/app/runtime.h and src/app/runtime.cpp. Owned tests: two new C++ tests and one
focused runner. No legacy transport, source-bound reader, locked test or existing
config value is changed. Parent records D229 in main DECISIONS after review.
