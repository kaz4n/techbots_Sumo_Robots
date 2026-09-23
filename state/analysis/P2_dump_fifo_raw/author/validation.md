# D117 independent author validation

PASS on the first execution, with no fixture, oracle or production amendments.
The isolated aggregate ran 26 Python methods with no failures, errors or skips.
All 599 compiler/executable commands are retained; eight nonzero compiler results
are the unchanged D116 flag/upstream-constraint refusal expectations.

The adopted public contract is 00a6c36c. Executed native source is
`fdd3df0bff64a510a1333dd906f0aa0a1031214caf1bca0c00508ab7507b27fe`;
the header and two sketches match the implementer's second freeze. Test expectations
were frozen before any implementation compilation/execution by this author:
`test_dump_uart_fifo.py` SHA256
`ae9e2c8454a82730da015d71dea07df0d7002b25f94819acc6ef9765b26b0e3c`.
All ten frozen author files remain byte-identical. Nineteen existing D090/D116
test/fixture files are also byte-identical to tracked HEAD.

This is a reused separate author context, not a fresh repository or cross-model
review. Earlier D104 runner implementation context was disclosed. D117 production
bodies were not read; public contracts/headers and established test fixtures supplied
the oracles. Compilation and execution used opaque copied production sources.

Run from PowerShell:

```text
wsl -e python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_dump_fifo_raw/author/run_tests.py run1
```

Builds ran in `/dev/shm/d117-author-_zn4l0um` and nested temporary workspaces.
`run1_source_copy.json` binds every executed source and established fixture hash.
`first_test_freeze/` retains the original executable expectations.

| Evidence | Observed result |
|---|---|
| New native normal/sanitizer | 201 stimuli and 21,915,290 counted checks per profile; zero failures |
| Exact setup/cleanup | Three CR1 writes with DMB/immediate readback; partial failure, retained first cause, owned-only cleanup, no retry, PRIMASK restoration |
| Live native guards | AUTOCR, context, metadata, clock, pad and IRQ loss before/mid/after stores; unchanged store/time/deadline bounds and pending identity |
| FIFO model | Eight queued entries plus one separate shift byte; rational 115200 8N1 stop-bit timing, real full-queue PENDING, no overflow, TC-only completion |
| Actual sketches | Recorder M0, app M0 and app M1, each normal/sanitizer: explicit FIFO selection, no dump callbacks under unchanged false grants |
| Unchanged D090 | 11 methods; 77 subprocesses / 2,435 checks per normal/sanitizer profile |
| Unchanged D116 | 22 cases / 4,202,902 assertions per normal/sanitizer profile; default factory/sketch, six flag refusals, five CONFIG profiles of 224 assertions and two upstream refusals |

The app sketch test retains actual Runtime MotorGate/clock initialization. Its
passivity assertion applies to the optional dump callbacks; it does not invent
global app startup silence. The recorder sketch's disabled delegation is wholly
callback-passive. Actual D116 Runner behavior is checked by its unchanged suite.

Full D116 replay uses the retained actual synthetic 200 s Transaction/recorder/Transfer
stream. Each native profile emits exactly 532,562 payload bytes in 10,027 packets:
682,967 wire bytes and 99,267 calls at 1 kHz in the serial reference model. Independently
decoded packet payloads match every original byte. The strict receiver accepts
5001 frames / eight events with synthetic provenance, and bundle format/consistency
both pass. The unchanged D116 tests separately retain their exact source-row/status/
summary comparisons and slow-progress TOTAL refusal.

The separate arbitrary-raw stress formats every 5001 frame and 4096 event row through
the actual serializers. Observed maximum line widths are 170/73 bytes, including LF.
It emits 1,148,071 payload bytes in 23,216 packets, 1,496,311 wire bytes and 215,676 calls
per native profile. Raw enums are deliberately unrestricted; this capacity stress
is not asserted to be a valid Robot attempt or a strict-receiver success.

The independent conservative model accounts for 23,303 packets, 1,156,084 payload
bytes and 1,505,629 wire bytes. Eight effective stores/call require 217,659 calls;
six require 288,575 and complete within 300,000. Five require 331,091 and are explicitly
refused at 300,000 after 1,056,322 acknowledged payload bytes. This lower service rate
is a separate model assumption, not a guaranteed minimum inferred from the native
eight-store ceiling or invented FIFO contents.

Machine-readable results, exact command outputs and stream hashes are in
`validation.json`, `run1_summary.json`, `run1_command.json`, `run1_full.txt`,
`run1_new/`, `run1_legacy/` and `run1_d116/`. No original failure was removed; this
author execution produced no unexpected failure. The earlier target-fit failure
and representation repair are separate coordinator/implementer evidence.

No board action occurred. Physical setup acknowledgement, FIFO/shift behavior,
nominal baud, actual 8-store/80 us service, framing and complete receiver delivery,
whole-tick 800 us, motor authorization and phase gates remain unproved. Root owns the
unchanged D101 193-check factory/full-app regressions and exact target fit/review.
