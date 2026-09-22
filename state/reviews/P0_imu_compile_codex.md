# P0 D-066 MPU6050 compile-only review — 2026-09-23

## Findings

No BLOCKER, MAJOR or MINOR finding in the scoped compile-only probe.

## Verdict

**PASS — selected source/API compilation and retained link-path evidence only.**
This is a separate same-model, fresh scoped Codex review, not a human review,
different-model review, runtime qualification, upload authorization or phase gate.

Reviewed AGENTS.md, PLAN section 3, P0 task 0.1/G6, REVIEW_GATE, current PROGRESS
and FACTS, D-051/D-052/D-066, P0_imu_compile_contract.md and
P0_imu_installed_contract_20260923.md. Local date was 23 September, the schedule's
P0/P1 day; the prior measured QTR image remains the current-image checkpoint.
The reviewer made no board call, upload, reset, debug attachment or I2C operation.
Only this review file was written by the reviewer.

## Source and safety scope

- `bench/p0_imu_compile/p0_imu_compile.ino:7` rejects MOTORS_ALLOWED != 0.
  Its two global anchors start null; setup at line 12 only assigns the probe
  and Wire1 addresses, and loop at line 17 is empty.
- `bench/p0_imu_compile/src/imu_probe.cpp:8` applies noinline to the retained
  function. Local MPU construction, begin, the three setters and getEvent are
  confined to this never-invoked function. Arguments preserve the prospective
  settings; there are no adopted runtime sensor tunables or global MPU objects.
  `src/imu_probe.h:12` within that bench sketch declares the exact contract type.
- The compiler substitutes independently reproduce inert setup/loop behavior,
  while the real target ELF separately proves actual dependency/API retention.
  Neither setup, loop nor a host test invokes the probe.
- `tools/board_tool.py:191` continues to reject this sketch's upload before
  target lookup. The probe is absent from `tools/p0_inert_sources.json`.
  The compile path retains MATCH=0, MOTORS_ALLOWED=0 and default startup.
- Diff against checkpoint 9a4ff32 shows no change to src/config.h, src/hal,
  tests/locked, board_tool.py or the inert upload manifest. No motor-pin write,
  wiring change, HAL implementation, strategy change or production loop is added.

## Reproduced checks and retained failures

The reviewer ran:

```text
wsl.exe --cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots python3 -m unittest discover -s tests/tooling -p test_p0_imu_compile.py -v
Ran 3 tests in 0.446s
OK
```

These cover setup plus 10,000 empty loops with no substituted MPU calls or new
allocations, rejection of a motor-enabled compilation, and upload denial before
board lookup. The successful host build uses UBSan and strict warnings.

An initial reviewer attempt with Windows Python lacked g++ on PATH: the two
compile-dependent cases ended in FileNotFoundError, and the upload-denial case
passed. This environment failure is not a product failure or a successful test;
the unchanged suite was then rerun successfully in WSL as shown above.

The coordinator's separate initial receipt,
`analysis/P0_imu_probe_host_tests_20260923.txt`, preserves one fixture error:
direct flash() raised the existing ValueError denial, while the fixture had
expected the CLI's SystemExit boundary. The current test expects the exact
ValueError denial; `P0_imu_probe_host_tests_fixed_20260923.txt` records all 3
passing. The rejection requirement was preserved, and no locked test changed.

## Provenance and actual target result

Saved evidence is `analysis/P0_imu_compile_provenance_20260923.json` and
`analysis/P0_imu_compile_target_20260923.txt`. Independent local consistency
checks compared every recorded archive file hash with the installed-file map,
the before/after library inventories, the three current probe files, all three
retrieved ELF files and the complete staged source digest.
The completed `analysis/P0_imu_compile_validation.md` was also reviewed and
agrees with these receipts and the stated compatibility/runtime distinction.

| Package | Exact version | Official archive SHA-256 | Files matched |
|---|---|---|---|
| Adafruit MPU6050 | 2.2.9 | acaad12ee2399f3225e6725e421d92699b006d7359cdda6ea5281c6b832cfc56 | 13 |
| Adafruit BusIO | 1.17.4 | c7bab1b6c6eee64b50964c8e149b795719a01f1d9dfcdcef170b35daa696349b | 24 |
| Adafruit Unified Sensor | 1.1.15 | d64cdec0b817535f568fc3b8b8d44e7e097749f5ab8040aea573f412a3cbaec6 | 6 |

The recorded installation commands add exactly these previously absent pins
with --no-deps. The previous library inventory is unchanged. There are no extra
files in the three installed-package maps. The production file maps match the
pinned source hashes from the installed-contract audit. GFX/SSD1306 omission is
explicit in D-066, and the actual successful compile confirms they were not
needed for this selected probe. This reviewer inspected saved acquisition and
installation evidence; it did not independently query the live board.

Actual board-side compile-only completed at 2026-09-23 03:11:49 Dubai, exit 0,
with 96,236 bytes program and 39,356 bytes globals reported. The saved command
and receipt explicitly say no upload requested. Build options, compile commands,
dependency files and libraries.cache select installed Zephyr core 1.0.0,
Wire/SPI and the exact three Adafruit library directories. The selected
preprocessor record retains MATCH=0/MOTORS_ALLOWED=0 and the installed API macros.

| Exact reviewed item | SHA-256 |
|---|---|
| Complete staged source | e0ee0fcc1d714a489a79c628b505829ab4ccc2f651be318742bc09e4996566bc |
| Final p0_imu_compile.ino.elf | 64810fb03b6af089564861e80d10da44d0d407ad73e76350c5d588020fefc751 |
| Debug ELF | 0f99a986ea358543489602f65285508020601e8d493582b96587df9352f32520 |
| Temporary ELF | f64af5ce365d4fe9ae7c71fa06e2b23b4d0d7c66e974af325319941452e4618a |

## Exact ELF inspection

The reviewer used local WSL arm-none-eabi-objdump/nm against the retrieved ELFs
in `build/p0_imu_review/`, and inspected the full saved symbols, relocations,
sections and disassembly embedded in provenance. Addresses below are ELF
section/display offsets, not evidence of a deployed MCU address.

- setup at 0x6c contains only two loads/stores and bx lr. Its literal relocations
  at 0x7c/0x80 are p0ImuProbe/probeMpu; 0x84/0x88 are p0ImuBus/Wire1.
  There is no branch or indirect call to the probe. loop at 0x8c is bx lr.
- The global anchors are retained BSS symbols. probeMpu at 0x24e8 is retained;
  0x2540..0x2558 reference the real MPU constructor, begin, setGyroRange,
  setSampleRateDivisor, setFilterBandwidth, getEvent and destructor. The begin
  call forwards the supplied bus and address and uses its default sensor ID 0.
  The success and failure paths both destroy the local object.
- Wire's constructor array at 0x56c0 binds Wire1 through the 0x570c ordinal-40
  relocation and 0x5710 Wire1 relocation. The constructor at 0x55ac initializes
  fixed object fields/ring buffers without controller initialization. This
  matches the installed audit's nonzero I2C4 device export.
- No undefined z_impl_i2c_* symbol or relocation is present. setClock at 0x541c
  dispatches through the device API configure slot. requestFrom at 0x5458 and
  endTransmission at 0x5514 dispatch through its transfer slot, constructing
  STOP-terminated messages. They do not call a zero-valued named I2C export.
- All 13 init-array entries were inspected. The translation-unit wrappers
  initialize guarded RouterBridge HCI fields; the Bridge/Monitor, Wire and SPI
  constructors initialize fixed objects. Serial buffer construction calls
  sem_init, not Serial begin. The C++ category registrations reach the local
  no-op __cxa_atexit at 0x5954. No initializer calls probeMpu, MPU begin or Wire
  begin. Dependency constructors exist despite the empty application loop.
- Full undefined-symbol and relocation lists remain in provenance. This review
  does not claim every loader import was dynamically resolved or exercised.
  The retained platform __loopHook at 0x245c still yields and uses a K_FOREVER
  Bridge mutex path; no runtime boundedness or whole-image inertness guarantee
  is inferred from the application's empty loop.

## Limits and next action

Successful compilation does not validate MPU identity, wiring, bus waveform,
read freshness/coherence, ranges/rates actually configured, error propagation,
sensor bias, timing or the complete under-800-us control tick. The installed
500-ms completion wait, indefinite bus ownership, ignored stop arguments,
source/binary-inferred BERR issue, library-masked read failures and unbounded
reset polling remain unresolved runtime blockers. No sensor transaction ran.

Keep this probe compile-only and outside the upload allowlist. Record the
scoped result and runtime limitations in the coordinator's ledgers/handoff;
current MCU remains the measured QTR61d7a2d0 checkpoint. Any production IMU path
requires its own later contract, implementation and physical/fault evidence.
No P0/P1 gate, PINMAP approval, motor-run permission or P2 authority follows.
