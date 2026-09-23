# D110 independent author validation

2026-09-24 Asia/Dubai. **PASS on the first execution**, against the second frozen
production source. No test-fixture or implementation correction was required.
Frozen test bytes remain unchanged. No production body was read by this author.

## Scope, independence and exact files

Authored only new `tests/tooling/vbat_cases.cc`, `tests/tooling/test_vbat.py` and
this author evidence directory. The coordinator owns config/registry additions,
production, target work and ledgers. Existing or locked test assertions were not
edited. A separate explicitly requested D109 evidence-wording correction is
recorded in its own author directory; it changed no test or production source.

The oracle derives from the adopted D110 public contract, declarations, config
and D078/D086/D093 contracts. Prior D104-D109 context is retained. Author and
implementer worked in separate contexts; source/status hashes were received,
but production bodies were not read. This is same-model independence, not a
fresh whole-repository or cross-model claim. `freeze.json` and the two `frozen_*`
test copies precede the first execution. `coverage.md` describes exact observables.

The actual Runner, Native binding and default sketch were copied opaquely and
compiled in a private `/dev/shm/sumo-d110-author-*` workspace. Native tests replace
only the existing public Reader methods with counted owners. They execute actual
new binding code and the actual sketch, including setup plus10000loops; they do
not execute or qualify ADC register operations or physical conversions.

## Executed profiles

| Profile | Cases passed per binary | Assertions passed per binary |
|---|---:|---:|
| Capacity128 normal and ASan/UBSan | 31 | 21,066 |
| Native/default selection normal and ASan/UBSan | 3 | 911 |
| Capacity1 normal and ASan/UBSan | 22 | 2,864 |
| Capacity0 normal and ASan/UBSan | 3 | 60 |
| Eleven invalid-config ASan/UBSan profiles | 3 | 60 |
| Five valid-config ASan/UBSan profiles | 1 | 10 |
| Five-record saturation normal and ASan/UBSan | 1 | 38 |
| Accumulated-half-range normal and ASan/UBSan | 1 | 24 |

All28 executables returned zero and had empty stderr. All3 forbidden MATCH/MOTORS
combinations failed the actual sketch static assertion as expected. There were
61 isolated compile/execute commands and zero unexpected nonzero outcomes.
`run1_summary.json` links every profile to its exact command/output receipt and
records the3 required refusals separately. `run1.txt` retains the outer unittest
result: two top-level tests passed in123.575s.

The native selector is case-insensitive, so it executes the two intended actual
binding/default-sketch cases plus the ordinary `native read failures` case.
Observed3/911 is reported, not the planned2-case subset. Capacity1 omits the nine
source/late/multiple-record cases needing later capture space. Capacity0 selects
only the three applicable admission/passivity cases. Config and special profiles
likewise have explicit selectors recorded in receipts; no filtered case is claimed
as executed in those profiles. The same frozen bytes run in every profile.

Saturation is an executed public-path result: under period=conversion=1, five
accepted samples reach exactly UINT32_MAX without setting counter_saturated,
then attempt one additional missed release and set the flag while retaining the
maximum. No Runner private state was seeded. The separate long-period profile
reaches aggregate source half-range through individually valid early-poll gaps.
Neither profile implies a physical1us conversion rate or physical clock accuracy.

The registry test independently verifies raw bytes: removing the coordinator's
one `VBAT_BENCH_SAMPLES: 128` line restores the pre-addition source exactly.
`registry_amendment_check_*.json` retains both hashes. The unchanged D106 wrapper
executes the unchanged D093/D090 registry methods and all18 original P0 checks.
Five profiles executed90 original checks: the positive approved config, three
existing D096 wrong-value profiles and the new copied VBAT_BENCH_SAMPLES=129
profile. Each negative is rejected by exactly the original value assertion.
`registry_summary.json` and `registry/registry_cases.jsonl` retain full outcomes
and prove that execution changed none of the monitored source bytes.

Command from the repository root:

```text
python -m unittest tests.tooling.test_vbat -v
```

The harness dispatches the C++ tests to WSL, uses strict C++17 warnings as errors
and fail-fast ASan/UBSan, and leaves every command receipt under this directory.
No shared build, board, network, upload or motor action was used. The separate
reviewer also reported a private rerun PASS on these exact source/test bytes;
that evidence is independently owned under `P2_vbat_review_raw`.

## Frozen hashes and limitations

Cases SHA256:
`196faa64a112c6a7b37d50524a84433e83b1fb7a21403781953dcf02f795e0f7`

Harness SHA256:
`34e3a8967cb7048f5d4e482416c4cc01847ac2c9607cfab431283ed0bcbf1283`

Executed vbat.cpp SHA256:
`b5fa7eea988e91a9b0fdb350b34fed982cef9893bde47e56c289e07a403c0475`

Executed vbat.h SHA256:
`cb03249f54b2ebb26d52fc38d5bbe20fee6316b2af8378f329d8b842a0546dfa`

`opaque_source_copy_1790195767414049308.json` binds all copied source hashes,
including Native, sketch and config. The registry before/after hashes are
`c0156a8e50ee38bb317f531a17c3c1ac704ec2d28b4b5bd3324a25204bc0e248` and
`9252acfc639c9729fe47b03d1d5e5f7e21088ef90bcb0c65132620f00315ce5e`.

This author run does not replace existing ADC-driver/native-pins regressions,
source review or exact target/loader/startup evidence owned by the coordinator.
Other impractical diagnostic-counter saturation branches remain source-reviewed.
ADC shutdown is never inferred from stopped callbacks. No physical supply,
divider/reference calibration,0.05V multimeter criterion, electrical permission,
native timing, full-app WCET, motor authorization or human phase gate is proved.

Next action: coordinator integrates independent reviewer, existing-native and
exact target evidence, then records adoption. No rerun is needed unless relevant
source changes or a new finding justify it.
