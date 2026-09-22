# P0 scaffold and inert-diagnostic audit

Date: 2026-09-22, Asia/Dubai. Active phase P0; no human gate is recorded. This is
the scheduled P0 day in PLAN section 3; no scope-cut or freeze deadline applies.

Objective: recover the exact P0 0.3 B16 scaffold evidence and check the two
diagnostic loops using their actual source with synthetic clocks. No board
connection, compilation, upload, GPIO access, or motor run was attempted.

## Scope and findings

- **B16 count correction:** BEHAVIOR.md B16, lines 351–426, has **76** tunable
  rows, including the single four-element QTR_WHITE_US row. The original config
  also declared `FC = 0U`, from the unrelated B5.2 bearing table. The prior
  PROGRESS claim of “77 defaults compared exactly” counted that unrelated row.
  The new check isolates B16 before parsing and rejects missing or extra names;
  only the four explicitly named P0 diagnostic constants are allowed in addition.
  All 76 intended initial values and their existing integer/float/array
  representations matched on the initial audit. B16 does not independently
  specify C++ types; the representation test preserves the P0 scaffold's
  uint32_t/float choices under AGENTS section 6.
- **Seconds-counter defect:** the initial matrix loop assigned
  `lastCounterMs = now` and incremented once. Synthetic calls at 1500 ms and
  2100 ms yielded a seconds counter of 1 instead of 2. Larger gaps also lost
  whole seconds. The required repair is a bounded elapsed-period calculation
  retaining the fractional-period remainder; no catch-up loop is needed.
- **Timing loop source bounds:** each call takes at most one sample, with fixed
  scalar work and one histogram update. Synthetic boundary/wrap tests passed;
  lateness at 999 us occupies its exact bin, 1000 us and above use the overflow
  bin, while the maximum retains the actual late value. An over-period event
  restarts scheduling from the observed timestamp. `p0OverPeriod` counts late
  sample events, not the number of elapsed missed periods. Exactly 60,000 samples
  stop further acquisition and preserve the result; the nominal no-miss run
  spans 60,000,000 synthetic us. This is scheduler lateness, not tick execution
  time, and missed periods may extend real acquisition beyond 60 seconds.
- **Matrix loop source bounds:** a due draw traverses exactly 8 x 13 pixels and
  draws once per invocation, even after a long pause. Short-circuit tests bound
  glyph access and shifts. Synthetic coverage across the complete scroll cycle
  verified valid pixels, blank top/bottom rows and the visible S glyph. Ordinary
  uint32_t millis wrap passed. This is no substitute for inspecting the actual
  display or measuring the matrix interrupt cost.
- **Host scaffold:** CMake configures pure C++17, uses vendored doctest, excludes
  HAL from core compilation, and applies no-RTTI/no-exceptions flags on g++.
  The existing one-test/four-assertion scaffold checks only countdown defaults,
  the tick default, and default motor inhibition. It proves no implemented robot
  behavior, locked safety property, or target timing.

The coordinator owns configuration, benchmark repairs and append-only state
corrections. This audit agent changes only the two new test files and this report.
The coordinator removed FC and changed the matrix counter to add whole elapsed
periods while advancing the prior timestamp by those periods. Both findings are
now **FIXED / HOST-TESTED** by the final run below.

## Validation evidence

Initial run, before either source repair:

```text
wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -p 'test_p0_*.py' -v
Ran 10 tests in 1.067s
FAILED (failures=2), process exit 1
  test_only_b16_defaults_and_explicit_p0_diagnostics_are_declared: extra 'FC'
  test_matrix_counter_preserves_elapsed_seconds_after_delayed_calls:
    p0Seconds == 2 failed after timestamps 1500, 2100
```

The other eight tests passed. Both real sketches were executed in compiled C++17
harnesses using g++ with warnings as errors and undefined-behavior sanitizer.
Only clock and matrix hardware APIs were substituted. These are deterministic
host simulations; the existing test_tools.py already supplies separate syntax,
inert-build-guard and staged-include-path coverage. One additional explicit test
then fixed the four P0 diagnostic expected values: scroll 100 ms, counter 1000 ms,
60,000 jitter samples, and 1000 us histogram overflow threshold.

```text
wsl -d Ubuntu -- bash tools/test_host.sh
1/1 CTest target passed; process exit 0
```

Final focused run after the coordinator's two source repairs:

```text
wsl -d Ubuntu -- python3 -m unittest discover -s tests/tooling -p 'test_p0_*.py' -v
Ran 11 tests in 1.353s
OK; process exit 0
```

This consists of five configuration checks and six actual-sketch synthetic
runtime scenarios. The two regression assertions were not weakened.

## Limitations and next action

No target build or physical measurement is established here. In particular,
uint32_t wrap simulation assumes the installed time source behaves as documented;
FACTS F-029/G2 explicitly leaves installed cycle-counter configuration unresolved.
The matrix API's source bounds come from F-025/G1; host stubs cannot prove library
linking, ISR load, or hardware WCET. RAM counters are still not the required
once-per-second printed counter round trip. The existing SC-I Monitor/R3/R4
conflict, startup measurements, GPIO/QTR/ADC/I2C benchmarks and PINMAP OK remain
pending. No protected decision is resolved by these checks.

Next: coordinator records the verified corrections without rewriting prior
progress and includes these tests in the complete tooling run and independent
review. P0 exit approval still requires the existing hardware evidence and human
gate.
