# D082 independent heading test author

2026-09-23 Asia/Dubai. The author derived tests from the frozen
`P2_imu_heading_contract.md`, public `imu_heading.h`/D081 headers, configuration,
the previously read D079-D081 source contracts and AGENTS. No production CPP
file was opened or used to derive expectations. Production bytes were copied,
hashed and compiled opaquely. The initial test-macro compilation error emitted
unavoidable production diagnostic snippets; those are preserved, not described
as a separate source inspection or used to change behavioral expectations.

Owned files are only `tests/test_imu_heading.cpp`,
`tests/tooling/test_imu_heading.py`, the narrow D082 addition to
`tests/tooling/test_p0_config.py`, and this author receipt directory. No support
fake was necessary: synthetic qualified Samples exercise the actual numerical
consumer without a Bus. Old tests, fakes, native models and locked assertions
were not modified. Root owns headers/config/CMake/production/probe/integration.

## Final evidence

WSL command from the repository:

```
python3 -m unittest discover -s tests/tooling -p test_imu_heading.py -v
```

Final6/6 methods PASS,16.974s,exit0. Actual estimator22/22 cases,
64,370 assertions PASS with strict no-exceptions C++17 and UBSan. Ten isolated
configuration variants PASS:7 invalid gap/silence configurations and3 valid
boundary configurations. The actual estimator also passed allocation and I/O
counters across construction,10,000 accepted observations,10,000 NO_NEW reports,
bias updates, a terminal fault and destruction. Both actual sketch/probe macro
modes passed constructors/setup/10,000loops startup checks. All eight upload
combinations refused before board or transport lookup.

Strict config command passed15/15 methods,0.110s,exit0:

```
python3 -m unittest discover -s tests/tooling -p test_p0_config.py -v
```

The only allowed new config name is `IMU_HEADING_MAX_GAP_US`, exactly2000 as
`std::uint32_t`; every previous strict default/type/extent assertion remains.

Every compiler/executable command records exact argv, exit, full stdout/stderr
and source SHA256. All builds use isolated `/dev/shm/sumo-d082-*` temporary
directories. No shared host build was used. Key final receipts:

- `command_1790154170646761014.json`:22case estimator compile.
- `command_1790154170667240253.json`:22cases/64,370assertions execution.
- `command_1790154171175439459.json`:macro0 actual inert probe execution.
- `command_1790154171705111818.json`:macro1 actual inert probe execution.
- `command_1790154172180674091.json`:10,000observation allocation/I/O execution.
- Config compiler/execution receipts run from
  `command_1790154172613799292.json` to `command_1790154178983798299.json`.

`final_source_sha256.json` freezes the exact tests, public/opaque source files,
config/contract and probe files. The estimator implementation stayed at the
initial frozen hash throughout every author execution:
`e314f57b78980993f782cf85aa48f0cd6ffadf1cb1ae99fb801c7981f1736411`.

## First failure retained

The first actual22case run passed, as did both probe modes, upload refusals and
the allocation/I/O harness. All10 configuration compiles failed because the
author used `-DVALID`, colliding with public `Presence::VALID`. Raw exit1 compiler
receipts are `command_1790154123868724756.json` through
`command_1790154125848176838.json`. The complete draft runner is preserved as
`first_test_imu_heading.py.txt`.

Renamed only the author macro to `D082_EXPECT_VALID`. No behavioral predicate,
expected result, production source, compiler warning policy or sanitizer was
weakened. Console failure excerpts were capped at6000characters to avoid repeated
cascade noise; receipt stderr remains complete. The final6method run then passed.
No production defect was established by these failures.

## Coverage and limits

The actual estimator cases exercise all24 proper signed coordinate permutations
and all24 reflected permutations; invalid/unconfirmed maps; one-shot lifecycle;
positive/negative continuous yaw beyond360; a closed-form ramp;40,001 observations
checking retained double precision after large yaw; bias changes without jumps;
finite/range boundaries on all scaled axes; known/unknown source failures; envelope
check precedence; first/later/absent sequence metadata; explicit gap1999/2000/2001
checks; wrapped/backward/half-range time; repeated completion; coherent shape,
duration/status validation; selected gyro/acceleration rail separation; absence
with junk unused data; no re-decoding raw arrays or native phase timestamps;
no GO-like reset via repeated begin; terminal identical zero-payload fault reports.

No fake physical mounting is selected: every coordinate map is synthetic test
data. The inert probe retains a default zeros/unconfirmed candidate map. I/O
counters observe Bus and clock entry from static startup; allocation counters
cover the explicit tested method scopes and sketch setup/loops, excluding process
startup allocation. Constructors are covered inside the runtime allocation guard.

Sequence increments/duplicates/skips/reset attempts and retention are dynamically
tested; a full2^32-observation rollover was not executed. No private-state mutation
or reset hook was introduced. The defensive NUMERIC accumulator-overflow branch
was not forced by invalid private state: legal rate/gap bounds make a realistic
finite test unable to reach float-maximum accumulated yaw. Nonfinite inputs,
inclusive range boundaries and long finite double-accumulation outputs are tested.
These limits must not be represented as exhaustive rollover/overflow execution.

No board connection, hardware operation, upload, motor run, commit, human gate or
physical freshness/axes/drift/sample-rate/WCET evidence occurred. Full host and
ASan validation, target compile and independent review belong to root/reviewer.
