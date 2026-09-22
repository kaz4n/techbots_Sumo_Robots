# P0 G6 MPU6050 compile-only compatibility — 2026-09-23

Result: **selected APIs compile and remain linked against the installed UNO Q
core; probe never invoked or uploaded.** First target compile passed without an
implementation repair. This closes the narrow D-066 compilation question. It
does not establish runtime adoption, a sensor result, P2 eligibility or a gate.

## Contract, implementation and scope

D-066 / `P0_imu_compile_contract.md` commit `452502d` preceded this implementation.
The public `bench/p0_imu_compile/src/imu_probe.h` was supplied before the
coordinator authored the independent test. Its exact `p0::ApiProbe` pointer
accepts the wire, address, gyro range, divisor, bandwidth and three event objects.
All prospective settings remain parameters. No new configuration value or pin
assignment was introduced.

The 3 source files are the public header, `src/imu_probe.cpp`, and
`p0_imu_compile.ino`. The noinline local-object probe references `begin`,
`setGyroRange`, `setSampleRateDivisor`, `setFilterBandwidth`, and `getEvent`.
Null-initialized volatile globals retain its address and the address of `Wire1`.
`setup()` assigns only those addresses; `loop()` is empty. A static assertion
rejects `MOTORS_ALLOWED != 0`. No code calls the probe, even in host tests.
The new sketch remains outside both the upload name guard and inert manifest.

Commands were limited to dependency acquisition/installation, Linux file reads,
compilation, preprocessing, and offline ELF inspection. No upload, reset, MCU
debug connection, peripheral access, I2C transaction, Bridge start, header/motor
write or sensor operation occurred. The preceding MCU firmware was not replaced.

## Exact dependency provenance

The board-side CLI is 1.5.1 (`01f3d4f2b`, 2026-06-05); Arduino Zephyr core is
1.0.0. Inventory found all 3 candidate packages absent. For each package, the
installed Arduino index entry matched the live official HTTPS index entry's URL,
filename, size and checksum. Downloaded ZIP bytes matched that official SHA-256;
every production `.h`, `.cpp` and `library.properties` matched the pinned GitHub
commit. All installed archive files then matched those same ZIP bytes exactly,
with no extra files. The 6 preexisting library inventory entries were unchanged.

| Package | Exact version / commit | Official ZIP SHA-256 |
|---|---|---|
| Adafruit MPU6050 | 2.2.9 / `502a7caccda630a151dfb03ecbdd4b8452809ef7` | `acaad12ee2399f3225e6725e421d92699b006d7359cdda6ea5281c6b832cfc56` |
| Adafruit BusIO | 1.17.4 / `3b8364267c3ee6e16bad91bc2101aefbd5b5915f` | `c7bab1b6c6eee64b50964c8e149b795719a01f1d9dfcdcef170b35daa696349b` |
| Adafruit Unified Sensor | 1.1.15 / `0a9127a1e886ff1adb4c1b6f5958b24108d55aa6` | `d64cdec0b817535f568fc3b8b8d44e7e097749f5ab8040aea573f412a3cbaec6` |

Install commands, each exit 0, were `arduino-cli lib install --no-deps` followed
by respectively `Adafruit MPU6050@2.2.9`, `Adafruit BusIO@1.17.4`, and
`Adafruit Unified Sensor@1.1.15`. No upstream file was patched. GFX and SSD1306,
declared metadata dependencies used by the OLED example, were intentionally
excluded by D-066; the actual production compile needed neither. Full official
archive URLs, index records, version metadata, file hashes, commands and outputs
are in `P0_imu_compile_provenance_20260923.json`.

## Target result and binary proof

The actual command was `python tools/board_tool.py flash bench/p0_imu_compile
--compile-only`, using explicit ADB serial `2629958581`. It ran board-side from
03:08:39.758 to 03:11:49.764 Dubai, exit 0. FQBN `arduino:zephyr:unoq`, default
startup, `MATCH=0`, `MOTORS_ALLOWED=0`. CLI reports **96236 B program / 39356 B
globals**. These are tool size reports, not a measured runtime memory budget.
Complete output is `P0_imu_compile_target_20260923.txt`.

Staged source SHA-256, independently recalculated over remote and local bytes:
`e0ee0fcc1d714a489a79c628b505829ab4ccc2f651be318742bc09e4996566bc`.
Remote artifact directory:
`/home/arduino/sumox26-build/e0ee0fcc1d714a489a79c628b505829ab4ccc2f651be318742bc09e4996566bc/p0_imu_compile/artifacts/bench-default`.

| Artifact | SHA-256 |
|---|---|
| Final `p0_imu_compile.ino.elf` | `64810fb03b6af089564861e80d10da44d0d407ad73e76350c5d588020fefc751` |
| Debug `p0_imu_compile.ino_debug.elf` | `0f99a986ea358543489602f65285508020601e8d493582b96587df9352f32520` |
| Temp `p0_imu_compile.ino_temp.elf` | `f64af5ce365d4fe9ae7c71fa06e2b23b4d0d7c66e974af325319941452e4618a` |

These 3 ELFs were fetched to ignored `build/p0_imu_review/` and checked against
the remote hashes for independent offline review. The provenance JSON preserves
all 10 generated artifact hashes, complete final symbols/undefined symbols,
sections, relocations and disassembly, plus actual build metadata and dependency
files. The cache folder is
`/home/arduino/.cache/arduino/sketches/92A6A7AB15B23DD28E844ED581503CC8`.

The final relocatable ELF establishes the following; addresses below identify
ELF code offsets, not live MCU memory addresses:

- `setup` at `0x6c` has exactly two store instructions and returns. Its four
  relocation operands are `p0ImuProbe`, `p0::probeMpu`, `p0ImuBus`, and `Wire1`.
  There is no call. `loop` at `0x8c` is a single `bx lr`.
- `probeMpu` at `0x24e8` remains present. Its 7 call relocations resolve to the
  local MPU constructor, `begin`, the 3 requested setters, `getEvent`, and the
  destructor. The API function was not discarded by dead-code elimination.
- Wire's global constructor binds `Wire1` to `__device_dts_ord_40`; it also
  constructs Wire/Wire2. The `ZephyrI2C` constructor initializes fixed buffers
  and fields without controller initialization or a transaction.
- `requestFrom(...,bool)` at `0x5458` and `endTransmission(bool)` at `0x5514`
  dispatch through the device's API table transfer slot. No `z_impl_i2c_*`
  undefined symbol or relocation is present. The prior audit's zero-valued
  direct I2C exports therefore are not selected by this build's I2C path.
  This is a selected-path finding, not a claim that every import is nonzero.
- Actual compiler commands and `.d` files select the three installed Adafruit
  directories plus installed Wire and SPI. Unified Sensor's production source
  is compiled and linked; its unused print helper can be discarded. SPI is a
  genuine compile dependency of BusIO even though this probe specifies I2C.
- A preprocessor-only replay of the recorded probe compiler arguments verifies
  `__ZEPHYR__=1`, `ARDUINO=10607`, `MATCH=0`, `MOTORS_ALLOWED=0`, with
  `SPI_INTERFACES_COUNT` and `BUSIO_USE_FAST_PINIO` undefined. The installed
  completion timeout macro remains 500 ms. No object or firmware was emitted by
  this additional preprocessing check.

Core Wire files and the packaged native ELF were rehashed. Native ELF remains
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`, matching
`P0_imu_installed_contract_20260923.md`; no loader was modified. The final image
still contains Arduino/RouterBridge dependency constructors and the installed
loop hook. Empty sketch code is not evidence that all framework code is absent:
the known hook/Bridge waits and runtime limitations remain separate.

## Independent host checks and failure accounting

The coordinator authored the 3 cases from D-066 before reading implementation:
null anchors, setup's exact pointers, no MPU construction/API/allocation during
setup or 10000 loop calls, MOTOR1 compile rejection, and upload refusal before
board lookup. Final run passed 3 cases in 0.290 s with strict C++17/UBSan.
A fresh reviewer reproduced all 3 in WSL in 0.446 s.

The first coordinator run had one test-fixture expectation error: direct Python
`board_tool.flash` raises `ValueError`, whereas the fixture expected the CLI's
`SystemExit`. Upload was correctly refused before board lookup. The new test
expectation was corrected to require `ValueError` plus the exact refusal text;
the original and corrected receipts remain in
`P0_imu_probe_host_tests_20260923.txt` and
`P0_imu_probe_host_tests_fixed_20260923.txt`. No production change or weakened
locked test followed. The reviewer's first Windows run lacked `g++` on PATH;
its successful WSL rerun was an environment correction. Target compile had no
error or repair. Shared tools/config/tests were not changed by this worker.

Fresh source and exact binary reviewer findings are recorded separately by the
coordinator/reviewer. No full robot or physical test is inferred from these cases.

## Unchanged limits and next action

The installed 500 ms completion wait, K_FOREVER bus ownership, ignored stop
arguments, potential native BERR-only false success, library-masked read errors
and unbounded reset polling are unchanged. They prevent assuming unchanged
dependencies meet the 1 kHz loop's under-800-us requirement. No sensor identity,
waveform, sample freshness, configuration, bias, timing, fault injection, wiring,
PINMAP acceptance, motor permission or human gate was proved.

Next action: coordinator records this narrow compilation result and the fresh
review, preserving runtime IMU adoption as unresolved. Do not invoke or upload
this probe or begin P2 HAL on the strength of compilation.
