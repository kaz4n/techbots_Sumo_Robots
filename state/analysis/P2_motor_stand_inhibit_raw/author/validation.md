# D115 independent author validation

PASS on the frozen D115 implementation and checked compile route, after one
reviewed fixture-only name repair. No production finding or source change was
required. The original failing run is retained, not replaced with the rerun.

## Scope and independence

Expectations came from adopted contract `d8f5fd9691e00521af665687c730e274605934c48f30f160ebe26bae0ed84cb2`,
the public motor/bench headers, D075/D095 contracts, and established test fixtures.
This is a reused separate test-author context, with prior D104 implementation and
later independent bench-test experience; it is not a fresh repository or
cross-model review. D115 and underlying production implementation bodies were not
read. Actual source bytes were copied and compiled opaquely after the test freeze.

Owned new executable files:

- `tests/test_motor_stand_inhibit.cpp`: 12 cases in the isolated allocation-guard
  build; 11 when that optional guard macro is absent in the ordinary host build.
- `tests/tooling/motor_stand_native_cases.cc`: actual Native forwarding and actual
  default sketch, with counted ordinary public UnoQPort/Runner substitutes.
- `tests/tooling/test_motor_stand_inhibit.py`: isolated normal/sanitized builds,
  original locked regressions, native profiles, and forbidden flag compilations.
- `tests/tooling/test_motor_stand_inhibit_policy.py`: eight public policy methods.

No existing test, locked assertion, production source, configuration, shared
build, ledger, board state, or gate was changed by this author task.

## Results

| Selection | Result |
|---|---|
| Actual Runner + actual MotorGate, normal | 58 cases / 4,242,601 assertions PASS |
| Same selection, ASan + UBSan | 58 cases / 4,242,601 assertions PASS |
| Counted actual Native/default sketch | Four binaries PASS: normal/sanitized, each with substituted begin returning false/true |
| Forbidden MATCH/MOTORS_ALLOWED combinations | Six required compilation refusals PASS: three Runner, three sketch |
| Public checked compile-only policy | Eight methods PASS |

Each 58-case selection includes 12 new cases and 46 unchanged locked motor gate
and halt cases. Literal expectations cover the successful 19-event trace,
LOW/zero-only writes, begin callback failures, every halt failure, missing
callbacks, invalid/accepted period boundaries, PORT-to-IO upgrade, equal/wrapped/
reverse/half-range clocks, callback-visible publication, first-grant consumption,
retained terminal reports, and passive repeated calls. A separate actual Gate
comparison supplements these with delegation compatibility for established
cleanup paths; it is not an independent proof of that Gate algorithm.

The native programs assert startup counters before setup, exactly one default
false-grant begin, 10,000 passive loop calls, exact callback/context/period
forwarding, and distinct local Native owners without backend or clock callbacks.
Policy tests exercise the exact default M0 project, rejected flags/Immediate/
uploads/foreign D114 option, effective project references, external libraries,
profile files and dangling links, no unchecked fallback, and no new upload key.

## Preserved first failure and correction

`first_test_freeze.json` and `first_tests/` precede every implementation execution.
`run1_full.txt`, `run1_summary.json`, `run1_commands/`, and `run1_source_copy.json`
preserve the first run: all Gate/policy checks passed, while native linking failed
before native execution. Within the ordinary `UnoQPort::port()` substitute,
unqualified `settle` and `clockUs` resolved to existing class member declarations
instead of the two counted fixture functions.

The coordinator reviewed `fixture1_native.diff` and approved only renaming those
two helpers to `countedSettle`/`countedClock` and updating their identical
references. No assertion, callback effect, value, stimulus, or production byte
changed. `fixture1_native_proposal.cc`, `fixture1_proposal.json`, and
`fixture1_applied_freeze.json` preserve the proposed and approved bytes.

Only the native selection was rerun, avoiding repetition of passed Gate/policy
work. `native_run2_full.txt`, `native_run2_summary.json`, and
`native_run2_commands/` contain its PASS results. Comparing the two source-copy
manifests identifies exactly one changed input: the native test fixture.

## Reproduction and identities

Executed from WSL with `/usr/bin/python3`:

```text
state/analysis/P2_motor_stand_inhibit_raw/author/run_tests.py run1
state/analysis/P2_motor_stand_inhibit_raw/author/run_native.py native_run2
```

Each harness copies source/tests into a unique `/dev/shm/d115-author-*` workspace.
Compiler and executable argv, return codes, stdout/stderr, and copied source
hashes are retained. Harness labels refuse existing evidence paths. The initial
outer harness is frozen as `1273bbc998c7a6c0b56171c6dd86fca36b4c90117944b60c8d228b35a82c8ffc`;
the targeted harness is `095bc86a47117b9c9a5fdf77378b80a3ad7a2469852d1575d3c3e64c4d147126`.

Final executable test SHA-256 values:

| File | SHA-256 |
|---|---|
| `test_motor_stand_inhibit.cpp` | `199b699284bac79ba4f8d78c09e5cc46647e4f0c05edffbf29ed43e7fdf82bf1` |
| `motor_stand_native_cases.cc` | `2f8600e899d3d87277aa5a70726e3dad42f7b372c3631f96954b2cba20205d98` |
| `test_motor_stand_inhibit.py` | `14f4b464fa4afd379232dd7398350329f4d92128fad0c799d6d503a086e16c74` |
| `test_motor_stand_inhibit_policy.py` | `f379a3a290b8ae84d2bd77ee53015b2eaa8c3dcba570831a9c4b526d9afc505f` |

All five copied bench files match the implementer's first freeze; Runner source
is `7e1b99a433855741fa708c58bbec3f6304e6abc21ebce6700d2499135ff70eed`.
Copied board tooling is `e93ef30ca82264c350f376a67206c3f3cfb94ab5738879d58c230aafb4fa7565`,
and policy is `9b8f86392f6ec5d7144f6e15ebaaea560ffc795dea7b3460abd3a97f40ef578b`.

## Limits and next action

All true-grant executions use synthetic host callbacks. Native binding tests
substitute the public owner definitions and do not validate physical pins,
timers, electrical readback, coast/brake, wheels, powered kill, full reversals,
supply integrity, or brownout. Runner allocation checks include wrapped C
allocators and C++ new/delete; native fixture guards cover C++ new/delete only.
Neither result establishes bench WCET, target ABI, motor-run authorization,
physical acceptance, or a phase gate. Non-reentrant Port use is the contract;
misuse through callback reentry is not tested.

Coordinator/reviewer can now integrate these frozen tests and complete their
independent source, full-host, policy-regression, and checked target audits.
Machine-readable details are in `validation.json` and `coverage.json`.
