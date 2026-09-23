# D106 independent author validation

Command: `python -m unittest tests.tooling.test_native_pins -v` from the repo
root. The Windows launcher delegates the isolated compiler work to WSL Linux;
temporary copied sources and binaries live under /dev/shm and are removed by
the harness. No shared build or board operation was used.

Final run2: PASS, exit 0, one unittest containing ten compiled-and-executed
variants (five table sizes, each normal and ASan/UBSan). All ten binaries printed
`PASS shared native descriptors`. All three attempted const mutations were
refused for the expected read-only variable/member reason. The non-Zephyr
header compilation passed. All five normal native objects passed undefined
symbol and absence-of-constructor checks. Counted I/O remained zero.

Run2 has 50 command receipts: 47 successful commands and three expected compiler
refusals. No skips or unexpected command failures occurred. See run2.json,
run2.txt, command_*.json, test_freeze_*.json and opaque_source_copy_*.json.

The initial fixture omitted Arduino.h, so run1 failed before native execution.
The independent reviewer approved adding a generated Arduino.h that includes
the already-counted GPIO declarations. The only source difference from the
original frozen test is that one generated dependency. No assertion, expected
result, test stimulus, constructor check or I/O check changed. The original
test_native_pins_v1_frozen.py and all run1 failures are retained, alongside
freeze.json and fixture_correction.json.

SHA-256:

| Item | Hash |
| --- | --- |
| Original frozen test | 779008750b375980680b96a76346636d8bfe2fe96292917b53bb15c515f4dfdb |
| Final fixture-corrected test | 59ef17f29c2bed6deb5bd1da15012fbd5a9101780bb1c19549b1e4e8de4c5e5c |
| Frozen public header | 34b4fb42e33ec2232f4574c997d4a701ec5a75efcbb12f37d5040e266c13022c |
| Tested opaque implementation | 222a95a33995065596ec4a08bc1a4fe925b7743aa2bb7b27c24195230376b008 |
| Contract | a9d633d9bbe351a32d4336ac90c212beaf4ae11bdf5b82bc96fcabae71786f48 |

The limited independence and evidence boundaries are stated in coverage.md.
This result proves synthetic host behavior for the tested public binding; it
does not establish target table deduplication, loader capacity, hardware pin
acceptance or a physical gate. The production consumer suites and target ELF
checks are separate coordinator/reviewer evidence.
