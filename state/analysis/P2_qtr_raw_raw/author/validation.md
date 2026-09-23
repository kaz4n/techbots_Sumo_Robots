# D109 independent author validation

2026-09-24 Asia/Dubai. PASS against the first production freeze after one reviewed
test-framework syntax repair. No production behavioral finding was observed.

## Ownership and independence

Only new `tests/tooling/qtr_raw_cases.cc`, `tests/tooling/test_qtr_raw.py`, this
author evidence directory and the expressly authorized single literal registry
entry in `tests/tooling/test_p0_config.py` were modified. No locked/established
assertion, other expected value, production file, configuration or ledger changed
by this author. The coordinator owns production and target evidence.

Expectations derive from D109/D085/D089 contracts and public declarations. Prior
D104-D108 context is retained. This is separate-context implementation-independent
test authoring, not a fresh repository reviewer or cross-model claim. Production
bodies were not read. The actual Runner, shared raw validator, new Native binding
and default sketch were copied opaquely and compiled. Existing Reader method
substitutes maintain only their own declared result_, as the contract permits.

The original executable tests were frozen before execution in `freeze.json` and
`frozen_*` copies. Their first execution failed to compile because this doctest
does not provide STATIC_REQUIRE/STATIC_REQUIRE_FALSE. No behavioral executable
ran in that attempt. The coordinator reviewed all five predicates and approved
the exact equivalent C++17 static_assert replacements. `fixture_amendment1.json`
proves those are the only changed expressions; runtime expectations are unchanged.
Original tests, `run1.txt`, `run1_summary.json` and all command receipts remain.

## Executed results

| Profile | Cases passed | Assertions passed |
|---|---:|---:|
| Capacity128 normal | 32 | 20,131 |
| Capacity128 ASan/UBSan | 32 | 20,131 |
| Actual Native/default sketch normal | 2 | 39 |
| Actual Native/default sketch ASan/UBSan | 2 | 39 |
| Capacity1 normal | 27 | 1,630 |
| Capacity1 ASan/UBSan | 27 | 1,630 |
| Capacity0 normal | 4 | 104 |
| Capacity0 ASan/UBSan | 4 | 104 |

All eight executables returned zero, with empty stderr. Three forbidden flag
combinations (MATCH/MOTORS 0/1, 1/0, 1/1) each failed the required static assertion.
The successful profile set contains 21 compile/execute commands and no unexpected
nonzero result. `run2_summary.json` links exact argv and individual receipts.
Native profiles deliberately select only two binding/sketch cases. Capacity1
omits five cases requiring a second captured frame; capacity0 deliberately selects
the four applicable fixture/passivity/missing-port/zero-capacity cases. These are
explicit profile selections, not silently skipped claimed coverage.

The unchanged D106 registry wrapper also passed, invoking the unchanged D093/D090
methods and all18 original P0 checks. Five profiles executed90 original checks:
one positive approved profile, three existing D096 wrong-value profiles and a
new copied QTR_BENCH_FRAMES=129 profile. Each deliberate negative failed exactly
the original expected-value assertion. `registry_summary.json` and
`registry/registry_cases.jsonl` retain the nested test output and source hashes.
The historical `registry_amendment.json` overstated byte preservation because its
comparison normalized text newlines. `registry_amendment_correction.json` records
the exact delta: the approved128 expectation plus CRLF-to-LF normalization on the
immediately preceding `BEHAVIOR_EXTRA_DEFAULTS = {` line. Removing the added line
and restoring that one CR reconstructs the prior bytes exactly. All existing
assertion tokens and values remain unchanged; the original receipt is preserved.

Commands run from the repository root:

```text
python -m unittest tests.tooling.test_qtr_raw -v
# First run: registry PASS; C++ fixture compile failure retained as run1.txt.
python -m unittest tests.tooling.test_qtr_raw.QtrRawTests.test_frozen_runner_native_capacity_and_forbidden_flags -v
# After reviewed static_assert repair: all C++ profiles PASS, run2.txt.
```

The harness dispatches only the C++ portion through WSL Python and isolated
`/dev/shm/sumo-d109-author-*` source copies. Strict C++17 warnings are errors;
ASan/UBSan uses fail-fast instrumentation. No shared build directory or board
operation is used. The original registry result remains applicable because its
inputs and code did not change in the fixture-only amendment.

## Exact hashes and next action

Final cases SHA256:
`80fec60e0c9a8eb67ad853e9b082a177663363c238dbf3e00b574ae8c4a1a7ab`

Unchanged harness SHA256:
`438ac88d3f769b32ba21794b37225de967824f6e37edf4d627e0ff61604773b2`

P0 test with sole approved literal addition SHA256:
`c0156a8e50ee38bb317f531a17c3c1ac704ec2d28b4b5bd3324a25204bc0e248`

Executed production qtr_raw.cpp SHA256:
`54b0a21b7b2867d9f816f476bec2b8cddf7b6ca7f902b7e682ccce2a9bceed33`

Executed production qtr_raw.h SHA256:
`ca134b2b36aeff657b1ea52c17d4d6c01a64e28f23aa8cb56169c77b853a9d35`

`opaque_source_copy_1790194959553662842.json` binds the full successful isolated
copy, including the actual adapter, Native and sketch sources. Further testing
is needed only if relevant source changes or a new finding requires it.

Next action belongs to the coordinator: independent source review, exact staged
target/loader/startup evidence and ledger adoption. See `coverage.md` for the
specific observables and exclusions. Finite128 public operation cannot reach
sequence wrap or counter saturation; source review must cover saturation branch
and callsite behavior. These tests establish no electrical handoff, real native
acquisition, optical classification, motor authority, physical timing or phase gate.
