# D108 independent red/green and full-host validation

Frozen expectations were derived from D108's public contract before execution
or production edits. No ui_display.cpp body was read. The only amendment to an
existing test is the authorized exchange of its first two opponent coordinates
and one explanatory comment. The additive three cases exercise the actual
displaySample -> render projection with literal channel coordinates.

The original renderer was copied and hash-checked before the coordinator's
one-line correction. Targeted red and green runs used both the full preserved
15-case display suite and the three new cases, with identical frozen tests:

| Renderer | Profile | Cases | Assertions | Outcome |
| --- | --- | --- | --- | --- |
| Original 4b03f677 | Normal | 16 pass, 2 fail | 1520653 pass, 4104 fail | Expected red |
| Original 4b03f677 | ASan/UBSan | 16 pass, 2 fail | 1520653 pass, 4104 fail | Expected red |
| Corrected 9e9d5d9a | Normal | 18 pass | 1524757 pass | PASS |
| Corrected 9e9d5d9a | ASan/UBSan | 18 pass | 1524757 pass | PASS |

Every red failure is a mismatched pixel at offset 15 or 17: 4096 from the unchanged
exhaustive loops and 8 from the independent one-hot projection cases. No other
test failed; sanitizer stderr was empty. See red_characterization.json and the
preserved raw red output. No assertion or fixture changed between red and green.

The complete existing CMake host project then ran in a separate opaque snapshot
under /dev/shm, including the automatically discovered additive test file:

| Build | Main host target | Motor-enabled host target | CTest |
| --- | --- | --- | --- |
| Normal | 1446 cases, 45736428 assertions PASS | 187 cases, 4536952 assertions PASS | 2/2 PASS |
| ASan/UBSan | 1446 cases, 45736428 assertions PASS | 187 cases, 4536952 assertions PASS | 2/2 PASS |

No cases were skipped in these targeted or full suites. All compile/configure
commands succeeded. Full sanitizer and ordinary runs use the same source/test
snapshot; no shared build was used. The motor-enabled target is host simulation,
not a firmware upload or motor run.

Reproduction from repository root under WSL/Linux:

```
python3 state/analysis/P2_display_channel_raw/author/run.py red --expect-failure --renderer-hash 4b03f677e27f839ae7a0a77ed0a88635f7a2d33c759c3c80c26ea6cb2e55728b
python3 state/analysis/P2_display_channel_raw/author/run.py green --renderer-hash 9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535
python3 state/analysis/P2_display_channel_raw/author/full_host.py
```

The red command was run before the correction and deliberately requires the
original renderer hash; after correction it refuses a different source. Its
original source bytes and exact commands/results remain in red_ui_display.cpp,
red_source.json and red_*_build/run.json/txt. Green and full-host receipts retain
their commands, output and source hashes. LastTest logs are also preserved.

| Identity | SHA-256 |
| --- | --- |
| Amended existing test | 5fe13c6623daa7ed2164d8afbb1203bb50629f9c22dd180c9547c1325270cd43 |
| New projection tests | 07059bff87dee2bff6a47687aa496fc3407fed3c9abfa1b4cf6dd5dd0a43d719 |
| D108 contract | f4294624171b200c387b10125fcd68e7c9ba7450879d533e94500074bc6e4d16 |
| Original renderer | 4b03f677e27f839ae7a0a77ed0a88635f7a2d33c759c3c80c26ea6cb2e55728b |
| Corrected renderer | 9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535 |

freeze.json, oracle_amendment.json, targeted_summary.json and
full_host_source.json bind these identities. coverage.md describes limited
independence and scope. Target app compilation, source/ELF mapping and capacity
review are separate coordinator/reviewer work. No physical optical orientation,
electrical qualification, hardware acceptance or human gate is claimed.
