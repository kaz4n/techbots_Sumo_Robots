# D-066: MPU6050 compile-only compatibility probe

Scope: P0 G6 requires a library that compiles against the installed UNO Q core.
MPU6050 is user-reported; no sensor is attached. Compilation is eligible without
electrical facts. It does not authorize P2 HAL, I2C execution or library adoption.
Installed audit is recorded separately in P0_imu_installed_contract_20260923.md.

- Pin Adafruit MPU6050 2.2.9 (502a7caccda630a151dfb03ecbdd4b8452809ef7),
  BusIO1.17.4 (3b8364267c3ee6e16bad91bc2101aefbd5b5915f), Unified Sensor1.1.15
  (0a9127a1e886ff1adb4c1b6f5958b24108d55aa6). Verify official index archive URL,
  checksum and installed version. Install only these absent pinned libraries,
  explicitly --no-deps, preserving any installed conflicting version. GFX/SSD1306
  are metadata display dependencies unused by the inspected production source;
  exclude them deliberately, and fail compilation explicitly if actually needed.
- New bench/p0_imu_compile remains outside the inert upload allowlist. Only
  tools/board_tool.py flash bench/p0_imu_compile --compile-only may build it.
  MATCH0/MOTORS_ALLOWED0/default. Do not upload, reset, start I2C, or change config,
  loader/dependencies already pinned, Wire wiring, motor pins or library sources.
- Define p0::probeMpu(TwoWire&, uint8_t address, mpu6050_gyro_range_t,
  uint8_t divisor, mpu6050_bandwidth_t, sensors_event_t&, sensors_event_t&,
  sensors_event_t&) -> bool. It constructs a local Adafruit_MPU6050 and references
  begin(address,&wire), setGyroRange, setSampleRateDivisor, setFilterBandwidth and
  getEvent(&accel,&gyro,&temperature). All prospective settings are parameters,
  not adopted runtime tunables. Do not execute this function, even in a host test.
- Public header src/imu_probe.h defines ApiProbe as the exact pointer type above,
  declares probeMpu and global `extern p0::ApiProbe volatile p0ImuProbe` plus
  `extern TwoWire* volatile p0ImuBus`. Globals start null. setup only assigns
  &p0::probeMpu and &Wire1 respectively. loop is empty. No global MPU instance,
  constructors with I/O, dynamic allocation or hidden API invocation in setup.
  Static-assert MOTORS_ALLOWED==0. No Bridge begin or header/motor writes.
- Host substitute test derives from this contract before reading implementation:
  setup sets exact addresses without constructing/accessing an MPU or bus;
  loop preserves them and performs no calls; motor-enabled build rejects.
- Actual target compile must include/link the installed Wire1 and all three
  candidate libraries. Inspect the exact final ELF for retained probe function,
  globals, Wire1 binding, selected API/library paths and actual imports. Dead code
  elimination of the whole API probe is not an accepted compatibility claim.
  Verify setup merely stores addresses and cannot invoke the probe.
- Preserve commands/statuses/source/artifact/dependency hashes and versions.
  No successful build clears the installed500ms transfer timeout, indefinite bus
  ownership, ignored stop arguments, masked read failures or unbounded reset
  polling. Keep source/binary inferences separate from exercised hardware faults.
  If incompatible, retain exact error and investigate at most two bounded repairs;
  do not patch upstream libraries or relax compile expectations to claim success.
