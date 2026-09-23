# D101 independent test-author evidence

2026-09-23 Asia/Dubai. Objective: test the actual optional Runtime dump boundary
against D101, D090 and D096. Expectations were derived from the frozen contracts,
public headers and existing independent test fixtures. The author did not read
production implementation `.cpp` files. Compilation copied and hashed production
sources opaquely. No private Runtime/Robot/recorder buffers were seeded or altered.

## Owned additions

- `tests/test_app_dump.cpp`: 21 unique contract cases; 5 apply to unconfigured
  production button windows, all 21 apply to the synthetic configured profile.
- `tests/fixtures/app_dump/fixture.h`: typed source and dump callback traces,
  real Runtime/Transaction/Robot/MotorGate/AttemptRecorder composition.
- `tests/fixtures/app_dump/roundtrip.cc`: actual Runtime stream producer and
  retained public-API CSV snapshot for independent receiver comparison.
- This `author/` directory: scoped runner, exact subprocess stdout/stderr/exit
  receipts, byte hashes, synthetic configuration, strict capture artifacts,
  preserved failed attempts and final source audit.

No existing test, locked test, production configuration, implementation, ledger
or hardware file was changed by this author. Root owns CMake and shared wiring.

## Final results

Final run: `run_1790185111677398343`. All compiler/executable commands exited 0.
Compiler flags include C++17, warnings as errors, no RTTI/exceptions, UBSan and
`-fno-sanitize-recover=all`. Host-only `MATCH` and `MOTORS_ALLOWED` match the table.

| Button profile | Motor setting | Cases | Assertions | Result |
|---|---:|---:|---:|---|
| Production unconfigured | 0 | 5 | 166 | PASS |
| Production unconfigured | 1 | 5 | 166 | PASS |
| Copied synthetic windows | 0 | 21 | 6085 | PASS |
| Copied synthetic windows | 1 | 21 | 6085 | PASS |

The configured profile changes only copied `BUTTON_WINDOWS_CONFIGURED`,
`BUTTON_LOW_RAW`, and `BUTTON_HIGH_RAW`; its exact bytes are retained as
`synthetic_config.h`. It is not an electrical profile or physical button grant.
Final source audit makes 184 hash comparisons and passes; both production source
snapshots and test inputs remain identical to their compiled versions. The copied
configured header is compared to its retained synthetic copy, and the default
header is compared to the unchanged production header.

Coverage includes passive disabled/missing/setup-failed ports; Gate-first setup
and exact grants; once-only setup; early and terminal passivity; real local menu
intent; actual completed countdown-cancel attempt; unchanged retained source;
real current consumed motor receipts; complete callback timing; partial/pending
writes and malformed callbacks; immediate Linux readiness loss; active and passive
failed motor receipts; 999/1000/1001-us readiness freshness; post-ready/post-write
clock faults without fabricated completion; terminal cancellation after motor halt
and before genuinely active QTR cleanup; STOP and menu-exit/START preemption;
micros wrap; actual pending epochs reaching the exact stall boundary; and
Transfer abort passivity, active cancellation and retained replay/time history.

START requires leaving the dump menu first, so the public UI cancels the active
transfer on that earlier menu exit, before the later genuine countdown. STOP
preemption is exercised directly. There is no fabricated post-STOP reset API.

## Strict receiver roundtrip

Each successful source follows real neutral/START/release -> COUNTDOWN -> MODE
cancel -> real final tail -> IDLE -> long MODE/service selection -> LOG_DUMP.
The standalone strict Python Parser receives one byte at a time. Its frame,
event and summary CSV bytes equal the public retained-owner snapshot exactly.
The real `save_capture` path then receives 13-byte chunks, validates the complete
bundle and publishes using its no-overwrite rename on native Linux `/dev/shm`.
Published artifacts are copied into this evidence directory for retention.

Both motor settings emit identical 1268-byte streams:

- Session 1476, retained epoch 86, explicitly synthetic origin 1.
- Two frames, three events, CRC32 4237426210.
- SHA-256 `725d57136686946f15694569d5948de134ffa3a32a3eb4711630d3c52c594765`.
- Receiver format integrity and owner-summary consistency PASS; no reported loss.
- Lifecycle SEALED, no GO, no missing final frame; output remains inhibited.

Capture manifests correctly retain synthetic provenance, offline receive mode,
null firmware/source/config declarations and false hardware/transport acceptance.

## Preserved failures

1. `run_1790184930060854855/command_05`: author fixture compile error passed
   `app::DumpPort` to standalone `Transfer`; corrected to `.output`. Both earlier
   default builds passed. No production change was needed.
2. `run_1790184985847368303`: configured motor-0 cases and strict Parser/CSV
   comparison passed, but publication under `/mnt/c` failed with EINVAL because
   DrvFS does not support `renameat2(RENAME_NOREPLACE)`. The receiver preserved its
   `.partial` folder and error report. The final run uses a native Linux filesystem
   for the exact existing publication operation; no fallback overwrite was added.

## Limits and next action

This evidence proves scoped host software behavior. It does not establish native
UART ownership/framing, physical wiring, Linux monitor capture, loaded free RAM,
whole-robot 800-us WCET, a human phase gate or motor-run authorization. No board,
network, upload, reset or native motor operation was performed by this author.
Root should combine these results with full unchanged regression suites, final
target memory/dependency/startup audits and separate fresh-context review.
