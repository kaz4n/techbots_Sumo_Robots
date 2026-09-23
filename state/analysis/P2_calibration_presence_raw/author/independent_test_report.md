# D083 independent author evidence

Objective: independently test the actual Services/Lifecycle gyro-admission path
against contract commit `3c356ec`, preserving established tests and safety policy.

## Independence and scope

Expected behavior was derived from `P2_calibration_presence_contract.md`, public
`countdown.h`, `types.h`, `config.h`, B3, D024 and D083. The author did not open
production `.cpp` files or established C++ tests. Production `.cpp` bytes were
copied and hashed opaquely for actual-source builds. The author read the actual
new compile-only `.ino` and `tests/tooling/test_imu_heading.py` only for the
separately authorized probe/tool runner mechanics. No old source/test, framework,
header, config, build file or ledger was modified by this author.

Owned deliverables:

- `tests/test_calibration_presence.cpp`
- `tests/tooling/test_calibration_presence.py`
- this `author/` evidence directory

Frozen production SHA-256:
`09174efe38003245c635237bdd489454efc86b9ec1e65b089fcc167a2106eb7d`.

Final C++ test SHA-256:
`e3cf267e15ab43a5ecedf87028f998f721d66ce057ebe0bf6d0729efb793403f`.

Tooling source SHA-256:
`88f7f0e6b1f9489ac9735f82ad1232a6ff0991e94a1c0fe3a46457d1f9e4f120`.

## Results

WSL Ubuntu, GCC 13.3.0, C++17, strict warnings, exceptions/RTTI disabled, pinned
doctest 2.4.12. Isolated `/dev/shm` builds copied the real implementation. The
final command was `bash state/analysis/P2_calibration_presence_raw/author/run_focused.sh run_2`.

- Final tooling run: 5 methods PASS, 13.109 s, process exit 0.
- Focused normal: 31 cases / 2,283 assertions PASS.
- Focused AddressSanitizer + UndefinedBehaviorSanitizer: 31 cases / 2,283 assertions PASS.
- Actual compile probe, MATCH/MOTORS_ALLOWED each 0 and each 1: constructors,
  setup and 10,000 loops retain zero exercise calls, ordinary allocation calls,
  and instrumented clock calls; entry pointer becomes the real exercise function;
  exposed candidate inputs and result remain at defaults.
- 10,000 actual Services/Lifecycle attempts: ordinary allocation and instrumented
  clock counters remain zero, including explicit valid/absent/duplicate/invalid,
  finish/reject, cancel/reset, invalid start and STOP paths.
- All 8 mocked upload combinations (ADB/SSH, match false/true, default/immediate)
  refuse before `target`, `remote` or `require_transport` is called.

`command_*.json` retains exact argv, stdout, stderr, return code, and source hashes
for each real compile/execution. Text capture normalizes line endings. The two
`upload_refusals_*.json` files retain each refused combination and zero mock counts.
`run_2.*` retains the full top-level command/timestamps/output/process status.

## Coverage

Tests cover append-only aggregate/default LEGACY compatibility; all four known
statuses and all unknown uint8 enum codes; explicit VALID independent of imu_ok;
ABSENT contaminants and INVALID without source-identity consumption; unknown mode
nonselection; mode selection by ABSENT/VALID/INVALID and mixing both ways.

Temporal/identity cases include exact decision/source-window endpoints, closure
before a CAL_END delivery, maximum age equality and one beyond, future/half-range
source times, fresh/stale duplicates on later decision ticks, equal signed zero,
conflicting raw value, partial identity, independent reversal, allowed source/
sequence forward gaps, arbitrary initial/zero sequence, sequence half-range,
source/decision/release/sequence wrapping, and ignored duplicate decision ticks.
A fresh pre-window source is excluded while committing identity, proved by replay
and conflicting sequence tests. Outside-window observations do not select mode,
validate, admit or change calibration output.

Aggregation includes absent-only/one-reading minimum failures, exact and next-float
spread thresholds, all non-finite forms, previous-bias retention, and continued
diagnostic counting after rejection. A fixed-seed LCG creates exactly 125 absent
slots and 375 distinct delivered observations, each with a replay; an independent
sum of the generated unique values provides the expected mean. The modulo-four
argument proves the expected count without implementing the admission algorithm.

Service/lifecycle checks cover warnings, latest masked snapshots (including zero),
terminal freeze, mode/identity/rejection reset through start/cancel/reset, invalid
start recovery, qualified START release through the full hold including wrap,
explicit accepted bias, post-GO STOP evidence retention, MODE cancellation and
restart, STOP priority at sample/calibration/GO deadlines, and BOTH qualification
despite absent gyro.

## Initial failures and corrections

The initial source hash was captured before any implementation execution in
`initial_freeze.json`. Review identified a comment-only modular-arithmetic typo;
`comment_correction.json` records its correction before first execution.

Run 1 passed the probe, allocation/clock, and upload checks, but both focused C++
compiles failed because the new test source lacked `<initializer_list>` and used
five REQUIRE macros incompatible with the project's no-exceptions doctest mode.
The compiler failures are retained in structured receipts and `run_1.stderr`.
The new source was corrected to include the header and use CHECK with identical
expressions; no assertion was removed or expected behavior weakened. Subsequent
value-type calls are safe even after a failed start assertion. No production
change followed this failure. `compilation_correction.json` records the freeze.

The original outer shell wrapper failed to retain its exit variable because of
command quoting; its `run_1.exit` is not a valid status receipt. Inner compiler
receipts retain actual exit 1, and run_1.stderr retains unittest's failed result.
The literal `run_focused.sh` fixes only that evidence-capture issue for run 2.

## Limits and next action

This is host software evidence, not hardware provenance, board runtime, ADC/IMU
measurement, WCET, MotorGate/physical hold proof, P2 acceptance or a phase pass.
The author performed no hardware/network operation and did not invoke a real
upload path. Whole-repository regression, actual target compile and fresh review
are owned by the root agent and are not inferred from this focused pass.

Ordinary allocation instrumentation covers linked malloc/calloc/realloc/free and
ordinary C++ new/delete forms; it does not claim arbitrary external-library or
aligned-allocation interception. Clock instrumentation covers micros/millis and
delay variants, not every possible external I/O function. Source-time half-range
observations necessarily fail freshness before identity ordering within the
3-second calibration span; those tests establish observable rejection, not an
unreachable private-branch coverage claim.

Next action: root should combine these receipts with full host/sanitizer, target
compile-only and fresh-review evidence without broadening physical claims.
