# D081 independent test author receipt

2026-09-23 Asia/Dubai. Tests derive from AGENTS, the complete D081 acquisition
contract and public headers/config, D079/D080 contracts, and the manufacturer
sample-audit report. The author read the existing independent native fixture
and test runners/support fakes, but did not inspect any production implementation
CPP. Production CPP was copied/compiled and hashed as opaque bytes only.

Owned changes:

- `tests/native_imu_bus/acquisition_cases.cc`:14 additive native cases.
- `tests/test_imu_acquisition.cpp`:15 actual Acquirer/Setup cases.
- `tests/support/imu_acquisition_fake.h/.cpp`:additive runtime Bus substitute and
  literal D080 setup recipe; the old `imu_bus_fake.*` remained unchanged.
- `tests/tooling/test_imu_acquisition.py`:7 new methods; no inherited old methods.
- `tests/tooling/test_p0_config.py`:only exact IMU_SILENCE_US20000 admission/type/
  value checks added. Prior assertions retained; now14 strict methods.

All tests/support/native-model/locked files outside that ownership were preserved.
The root owns CMake/config/headers/production/probe files and full-suite validation.
No shared `build/host` path was used by this author. Compiler binaries stayed in
temporary `/dev/shm/sumo-d081-*` and native-runner temporary directories.

## Final execution

Command from the repository under WSL:

```
python3 -m unittest discover -s tests/tooling -p test_imu_acquisition.py -v
```

Final result7/7 methods PASS,31.058s,exit0. Actual Acquirer15/15 cases,
36,491 assertions PASS. Native14/14 cases,260 parent assertions PASS; existing
process isolation propagates child-check failures rather than adding child
assertion totals to the parent's count. Do not present260 as total child checks.
Nine compiled configuration variants passed: silence0/half-range/all-ones invalid;
silence1/max-forward accepted with exact expiry; four unsupported profile fields
blocked by actual owned Setup. Both actual inert sketch/probe macro modes passed
static-startup/setup/10,000loop Bus counters. All eight adb/ssh,match/default,
default/immediate upload combinations refused before board/transport lookup.

Every compiler/executable process has a JSON receipt with argv,exit,stdout,stderr,
and source hashes. Native receipts also contain unchanged fixture-source hashes.
Key final receipts:

- `command_1790152681173500304.json`:Acquirer strict UBSan compile.
- `command_1790152681237188589.json`:15cases/36,491assertions execution.
- `command_1790152682245989606.json`:macro0 actual inert startup execution.
- `command_1790152683308171855.json`:macro1 actual inert startup execution.
- `native_imu_bus_1790152690164973210.json`:new14case native compile.
- `native_imu_bus_1790152690292143533.json`:new14case native execution.
- Final variant compiler/execution receipts span
  `command_1790152662778139235.json` through `command_1790152692501298423.json`.

Strict config command also passed14/14 methods,0.078s,exit0:

```
python3 -m unittest discover -s tests/tooling -p test_p0_config.py -v
```

`final_source_sha256.json` freezes author files, public contracts, opaque production
sources and reused unchanged fakes/fixture. Both production hashes remained the
implementer's original frozen versions during all author executions:

- Bus:`1955d95c5e523e1538aaa44c1aa72bfc79398937245a0b573dc7285796a00603`
- Acquirer:`6dd161d0f4837ecb0c0b2874b1d7a7ddff6228c79c786ae69c2ff6890eabb4ed`

## Preserved first failures and test repairs

1. First Acquirer compile failed due to missing explicit `<initializer_list>` in
   the new test, under the real no-exceptions host configuration. Raw receipt
   `command_1790152527695158367.json` and `first_test_imu_acquisition.cpp.txt`
   preserve the draft. Added only the required include; no predicate changed.
2. First native run passed12/13 cases. The proposed frozen-poll workload used
   fixture byte delays3500 for readiness then100 for motion, which completed
   within the budget rather than exhausting it. Raw failure receipt
   `native_imu_bus_1790152538351721302.json` and `first_acquisition_cases.cc.txt`
   are preserved. Repaired the test stimulus to3500 then500 and added separate
   control reads proving each transaction independently succeeds at its own
   workload. Combined acquisition must fail POLL_LIMIT with partial motion kept
   private; all original failure/cleanup/latch assertions remain. This is test
   workload correction, not evidence of a production bug or assertion weakening.
3. The reviewer noticed one missing literal setup readback pair while the test
   file was still being authored. Added the specified SAMPLE_DIVIDER readback
   before its first compilation; there is no fabricated compile-failure receipt.
4. After the first complete passing run, bounded planned coverage tightened the
   wrap case so one actual response starts before uint32 wrap and ends after it,
   and tests every one of15 forbidden nonzero NO_NEW byte positions. Final results
   above include these additions. No further test changes followed that freeze.

## Covered boundaries and remaining limits

Native tests check exact1byte0x3A→STOP-clear/idle→15byte0x3A ordering; second status
bits0/1 never produce another observation; every unexpected status bit in either
phase; same/changed numerical payloads; each native error in both phases; ownership
loss at either STOP; aggregate599/600us boundaries and wrap; no second600us allowance;
shared frozen8192poll exhaustion; separate49/50us cleanup; no synthetic STOP/retry;
latched no-I/O through all public methods; zero failed payload and no allocation.

Actual Acquirer tests cover concrete setup-only gating/diagnostics/one-time arming;
no pre-ready I/O; repeated equal observations; no-new zero-data/unchanged sequence;
observed gaps; call/completion19999/20000us boundaries; wrapped completion; reversed/
half-range caller and transfer times; malformed phase/shape/cleanup/flags; all
nonOK native statuses taking precedence; exact599/600us response duration; invalid
decoder status; zero-valued accepted motion; every fault identical/no-I/O afterward.

Sequence increments and preservation are directly tested; exhaustive2^32
observation sequence rollover was not executed and no private-state hook added.
The native model verifies protocol progression, not MPU silicon shadow timing.
No physical freshness/rate, mounting/bias/yaw, deployment clock, fault WCET or
whole-loop timing claim follows. No hardware connection, upload, motor operation,
human gate, commit or remote publication was performed by this author. Root and
the separate reviewer own full regression/sanitizer/target/review conclusions.
