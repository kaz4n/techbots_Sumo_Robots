# P0 IMU installed Wire/I2C contract audit — 2026-09-23

Result: **installed mapping, driver, timeout and API facts verified; target
library compilation pending; unchanged runtime adoption not established.**
A retained, never-executed compile-only MPU6050 compatibility probe is the next
eligible software check. It requires no sensor or I2C transaction. This report
does not design a P2 HAL, install libraries, select wiring, change shared ledgers,
assign fact IDs, authorize an upload or request external hardware.

The installed driver conclusively uses a **500 ms completion wait** and
**K_FOREVER bus ownership wait**. Wire ignores stopBit, so the Adafruit pointer
write/read is two STOP-terminated transfers rather than its requested repeated
START. A further source/binary-supported risk is that a BERR-only interrupt can
be followed by a successful return without complete data. Compile success cannot
resolve these runtime limits or the previously known Adafruit error/reset issues.

Scope: read-only installed Linux files, offline packaged-ELF inspection and pinned
primary public source. No MCU debug connection, memory/peripheral operation,
I2C call, upload, reset, library installation or compilation occurred. The
coordinator was conducting separate reviewed QTR work; this audit did not access
its live MCU state. Only this new report was written.

## Context and exact installed evidence

Read P0_G6.md, FACTS F-056–F-060, P0 task 0.1 G6 / 0.4, and the established
installed-core audits. The user-reported MPU6050 identity supports source/build
work; breakout and runtime properties remain unverified. D-051/D-052 permit
eligible software work on the bare UNO Q without an extra sensor request.
The original G6 research snapshot is now corroborated by the installed package
for the specific driver facts below; it was not assumed to match merely because
the board/core names matched.

Abbreviations:

- C = `/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0`
- E = `C/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf`
- H = `C/variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include`
- DT = `H/generated/zephyr/devicetree_generated.h`
- T = `/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-`

Installed version.h:19,23 reports kernel `4.4.2-rc1`, build
`v4.2.0-18364-g1743741760ee`. The corresponding full source revision used for
driver interpretation is `1743741760ee5d2d58da50d504855d43f9f8e826`.
The actual installed files and native code remain authoritative where a public
Arduino core revision differs. No complete release-source byte identity is
inferred from a version string alone.

| Installed file, relative to C unless H indicated | SHA-256 |
|---|---|
| firmwares/zephyr-arduino_uno_q_stm32u585xx.elf | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |
| firmwares/zephyr-arduino_uno_q_stm32u585xx.config | `a1c866dac9f190630713405d831918bc294753fc82f76e7f6d4135daae7e2bba` |
| libraries/Wire/Wire.cpp | `d70664c8bae877dded9c77d5db110af553816df32f1861be91a4ac27bf33ae5a` |
| libraries/Wire/Wire.h | `669d97628df80f184ad1bc3c1f7b4c68e821edf882df7e90fdfe0a72e0880eb4` |
| libraries/Wire/library.properties | `1fc5b139be74eafee56a469a349a37d3e1a9ac2a6bff66de9c3e4b62a93d51f2` |
| cores/arduino/zephyrPinctrl.cpp | `f48670ba733b9a1a3de8fe6ee903009f48b1f3d4da6b05521daffd93a88c51b9` |
| cores/arduino/zephyrPinctrl.h | `f2c7bd8cacb563ebc89881c9771ad226eadee52419b4fc8c36895a332368183b` |
| variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | `bd4d01db1d55a641c0570044a55bc6ba375cf8a11ef9ca6aad6a7378ed5fb8c5` |
| DT | `5b0e9b1d0f7d878415d53a5d724e976061aca52177967d90d7c76c3cb0b0fb80` |
| H/zephyr/drivers/i2c.h | `bc9a4408fe58e4807fd18814f2dfb7a2109be59bec6f27f89ad9956cac8e82ea` |
| H/generated/zephyr/syscalls/i2c.h | `749db7a3e3a0dfa88374149b68d0e8007008c9754acadfd817ce33227f07ad9e` |
| H/generated/zephyr/version.h | `edc930eb795ececf06480cea0a0365392ecb9d1e47a5d038f8d708e7dad6ecf8` |
| H/generated/zephyr/autoconf.h | `52178f5eefcf276720b859bdd60fc87ca4207b0130ac1fd5ba099af74b877a0c` |
| variants/arduino_uno_q_stm32u585xx/cxxflags.txt | `fd3d40463ce35184f52c7e41010cd96f4d4f1ae403cfd784472e3ea51b0ec800` |
| cores/arduino/api/Common.h | `f50252fe58ee67f4d9ed4f38b91d718c129976b65f2e0eb726b80c51d31265f1` |
| libraries/SPI/SPI.h | `80fb981c4ff169cc1c6abe41de54c79c34a7bccb3ba8942cb18608f606cb470b` |
| platform.txt | `d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638` |

Inventory was read directly: C/libraries has Wire1.0.0, SPI1.0.0, CAN1.0.0,
RTC1.0.0, SocketWrapper1.0.0 and Arduino_LED_Matrix0.1.3. The sketchbook
`/home/arduino/Arduino/libraries` has Arduino_RouterBridge, ArxContainer,
MsgPack, DebugLog, Arduino_RPClite and ArxTypeTraits. No MPU6050, BusIO or
Unified Sensor was present in those inspected library roots;
`/home/arduino/.arduino15/libraries` does not exist. This is the pre-installation
inventory, not an assertion about every unrelated directory on Linux.

## Wire1 mapping, initialization and ownership

Wire.h:78–96 and Wire.cpp:253–270 construct named Wire objects from the ordered
zephyr,user i2cs array; `TwoWire` is a typedef of arduino::ZephyrI2C. Overlay:393
and DT:20686–20708 give **Wire=I2C2, Wire1=I2C4, Wire2=I2C3**. Thus a default
`&Wire` argument is not the intended Qwiic bus; an eventual probe must pass
`&Wire1` explicitly.

Overlay:7–13 and DT:6303,6329,6404–6442,6512 establish:

- I2C4 device ordinal40, register base0x40008400, status okay, deferred init.
- Default pins PD12 SCL and PD13 SDA; configured bitrate400000 Hz.
- The named sleep alternative uses PF14/PF15 (overlay:11–12;
  DT:6518–6533), not the Qwiic pins. It is not a second independent Wire1 bus.
- DT:6293–6297 has no status-okay I2C4 child. Generated PD12/PD13 pinctrl
  references found in this package belong to I2C4's default state. Console,
  internal Bridge UART, matrix, motor proposal and QTR pads are separate.

Offline E verifies the actual object/export and driver table:

| Item | Installed native value |
|---|---|
| __device_dts_ord_40 and its LLEXT export | 0x0801c2a4, nonzero |
| device name/config/data/state | i2c@40008400 / 0x0801e3e8 / 0x20001bcc / 0x200010f0 |
| device flags/init/deinit | 1 (deferred) / Thumb0x0800d8e5 / NULL |
| config base/bitrate/pinctrl | 0x40008400 / 400000 / 0x0801e410 |
| default pin encoding | pinmux1924 and1956, pincfg576 each |
| driver API | 0x0801c708 |
| configure/get_config | Thumb0x0800d851 / Thumb0x0800d7d9 |
| transfer | Thumb0x080192e1 |
| target_register/target_unregister | Thumb0x0800da75 / Thumb0x080193f5 |
| recover_bus | NULL |

The pin encodings match DT:5895 and6113; no live register state was read.
Deferred init means the object is available but is not by itself proof that
I2C4 is initialized or that pins are electrically safe/connected.

Wire.cpp:54–57 constructors initialize fixed TX/RX ring buffers, each256 bytes
(Wire.h:19–22), without initializing the controller. `Wire1.begin()` at:59–65
calls init_dev_apply_pinctrl and discards its return. Installed
zephyrPinctrl.cpp:71–110 recursively visits device dependencies when enabled,
calls device_init if not ready, then applies default pinctrl; it propagates most
errors internally, but Wire's void begin does not expose them. Repeated begin
can remux the pads even when the device is already ready. No exclusive Arduino
owner registry or arbitration between arbitrary pin users is established here.

The native init at0x0800d8e4 initializes completion semaphore count0 and bus
semaphore count1, sets IRQs, activates the peripheral and configures the DT
bitrate; a failed configure prevents its configured flag. A future actual
runtime caller must distinguish controller readiness from physical sensor
identity. This report makes no call to initialize it.

## Installed synchronous API and repeated START

Wire.cpp:87–101 maps only100000/400000/1000000 to named speeds; other frequencies
fall back to100000. It discards the configure result. No Wire-specific per-call
timeout setter is declared in the complete installed Wire.h. Inherited Stream
timeouts do not alter the native I2C driver completion constant.

Wire.cpp:103–107 resets both rings on beginTransmission. endTransmission:109–123
ignores stopBit, calls synchronous i2c_write, consumes the claimed TX bytes even
on error, and reduces all failures to status1. requestFrom:129–150 likewise
ignores stopBit and calls i2c_read; failure commits zero receive bytes and returns
zero. A successful claim may be shorter than requested, so callers must check
the returned byte count. read:164–169 returns-1 when no buffered byte remains.

The installed H/zephyr/drivers/i2c.h is decisive:

- i2c_write:1412–1422 sets WRITE|STOP for one message.
- i2c_read:1457–1467 sets READ|STOP for one message.
- z_impl_i2c_transfer:875–898 dispatches via dev->api; it also ensures final
  STOP unless the no-stop Kconfig option is enabled.
- Native i2c_write_read:1506–1520 offers two messages, WRITE then
  RESTART|READ|STOP, in one call. This separate API is not used by Wire's pair.

Therefore BusIO's default write_then_read(stop=false) cannot make the installed
Wire honor the requested combined repeated START. There is a STOP and a released
bus semaphore between the pointer write and read, allowing another owner to
interleave. A native two-message call is source-supported as a possible later
integration option, not an adopted HAL or waveform validation. The driver checks
direction-change RESTART and rejects intermediate STOP, matching that native
form. Sensor compatibility with the actual Wire waveform remains unmeasured.

An important link caveat: packaged exports named z_impl_i2c_configure,
z_impl_i2c_get_config, z_impl_i2c_transfer, z_impl_i2c_recover_bus and both
z_impl_i2c_target_driver_* have **address0**. Their corresponding weak symbols
are value0. The normal installed header bodies can compile local inline dispatch
through the nonzero device API; this does not justify calling a zero export.
Target compilation must inspect actual relocations and local wrapper bodies.
A successful link that leaves an executed zero-valued import is not runtime
compatibility. Nonzero device_init/readiness exports are
Thumb0x08019e5d/0x08019e6f. Recovery remains unavailable through the NULL API
slot even if a local inline recovery wrapper exists (it returns-ENOSYS).

## Installed timeout and fault paths

The installed config:928–948, autoconf.h:384 and native instructions agree:
STM32 I2C v2, interrupt mode and target support are enabled; callback, RTIO,
DMA, calculated-v2-timing and bus recovery are disabled. PM_DEVICE/PM are
disabled (:102,114). SYS_CLOCK_TICKS_PER_SEC=10000 (:90).
CONFIG_I2C_STM32_TRANSFER_TIMEOUT_MSEC=500 (:948).

Offline full-function disassembly establishes these actual behaviors:

1. i2c_stm32_transfer0x080192e0 validates messages, then passes all-ones64-bit
   timeout to k_sem_take at0x08019302–0x0801930c for data+24 bus_mutex:
   **K_FOREVER**, independently of the completion timeout. It releases that
   semaphore at0x0801935c after its message loop or transaction failure.
2. Runtime configure0x0800d850 also takes that bus semaphore with K_FOREVER
   at0x0800d898–0x0800d8a2. Changing Wire clock does not avoid ownership waits.
3. i2c_stm32_transaction0x080194f6 passes5000 ticks to the completion semaphore
   at0x080195be–0x080195c6: **500 ms at10000 ticks/s per message**. NACK,
   arbitration loss or failed/timed-out semaphore acquisition leads to-EIO
   at0x08019608. For the small1/14-byte candidate reads no255-byte reload is
   needed. A multi-message operation has separate per-message waits, not a
   single500ms bound for the entire high-level library call.
4. The finish path disables the peripheral on normal STOP or detected error,
   subject to target/SMBus ownership state. There is no configured bus-recovery
   implementation. IRQ delivery, scheduler delays, contention and all outer
   library retries must be considered separately;500ms is not measured WCET.

These facts independently corroborate the source in pinned
[i2c_stm32.c](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/i2c_stm32.c#L144),
[i2c_stm32_v2.c](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/i2c_stm32_v2.c#L678)
and [Kconfig.stm32](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/Kconfig.stm32#L68).
Their full-content SHA-256 values are respectively
`eb85fcfcff500e12b33de4f961ea0bff81a53d6be86fd918e2236017dad9f725`,
`3d6764569c403e6a40ac3a82d0d0970432b20649bc445aea87a6bfe735efcb2b`,
`109a20701cd8855d7ec93a9619a90f681fdbf91a2bfb03d78afc3c6a12dfd597`.
Line anchors use conventional raw-file lines, not web extractor renumbering.

**Additional source/binary finding: possible BERR-only false success.** In
i2c_stm32_v2.c:644–652 the error ISR sets current.is_err and goes to its common
end;:672–675 disables transfer interrupts and gives the completion semaphore.
The finishing test at:694 checks is_nack, is_arlo and semaphore return, but not
is_err. The actual E instructions independently match: BERR handler sets data+76
at0x080194e8, then takes the IRQ-disable/semaphore-give path0x080194be–0x080194c6;
transaction finish0x080195ca–0x080195d2 reads data+72 and+68 and the semaphore
result, never+76. Thus if BERR is the sole flag and the wake succeeds, the
transaction can return0 without complete data. The ISR's own-EIO return does
not become the waiting thread's result. This is a control-flow inference,
not an exercised physical fault or claim about how often BERR occurs. The
source comment about ignoring spurious BERR does not supersede actual code.
See the [error and finish bodies](https://github.com/arduino/zephyr/blob/1743741760ee5d2d58da50d504855d43f9f8e826/drivers/i2c/i2c_stm32_v2.c#L613).

Consequences: checking only Wire/BusIO's success flag is necessary but not
sufficient evidence for all installed native fault cases. A stock synchronous
read cannot be claimed compliant with the under800us complete R4 tick under
faults; even Kconfig's minimum selectable timeout is1ms, and ownership still
uses K_FOREVER. No timeout override, loader replacement, async architecture or
production workaround is adopted by this audit.

## Pinned Adafruit source and compile dependencies

A separate read-only source reviewer inspected complete pinned production
source trees and archive contents in memory; no dependency was installed.

| Candidate | Exact commit |
|---|---|
| Adafruit MPU6050 2.2.9 | `502a7caccda630a151dfb03ecbdd4b8452809ef7` |
| Adafruit BusIO 1.17.4 | `3b8364267c3ee6e16bad91bc2101aefbd5b5915f` |
| Adafruit Unified Sensor 1.1.15 | `0a9127a1e886ff1adb4c1b6f5958b24108d55aa6` |

MPU6050.h:20–24 includes Arduino, BusIO_Register, I2CDevice, Unified Sensor and
Wire. Its public begin accepts a TwoWire pointer (:210–215); range/filter/divisor
getters/setters are declared at:220–245. RANGE_1000_DEG=2,
RANGE_2000_DEG=3 and BAND_184_HZ=1 (:105–124).
[Pinned header](https://github.com/adafruit/Adafruit_MPU6050/blob/502a7caccda630a151dfb03ecbdd4b8452809ef7/Adafruit_MPU6050.h#L210).

MPU6050 library.properties:1–10 declares architectures=* and dependencies
BusIO, Unified Sensor, GFX and SSD1306. BusIO and Unified Sensor declare
architectures=* with no depends field. The complete production .cpp/.h sources
of these three packages have no GFX/SSD1306 includes; SSD1306 appears in the
MPU6050 OLED example. A minimal explicit dependency installation may therefore
omit display libraries for this production-source probe, but the coordinator
must record that choice and actual resolved inputs rather than rewrite metadata
or imply automatic metadata resolution installed everything.
[MPU metadata](https://github.com/adafruit/Adafruit_MPU6050/blob/502a7caccda630a151dfb03ecbdd4b8452809ef7/library.properties),
[BusIO metadata](https://github.com/adafruit/Adafruit_BusIO/blob/3b8364267c3ee6e16bad91bc2101aefbd5b5915f/library.properties),
[Unified metadata](https://github.com/adafruit/Adafruit_Sensor/blob/0a9127a1e886ff1adb4c1b6f5958b24108d55aa6/library.properties).

Compatibility points a real target compile must cover:

- BusIO_Register.h:6–11 and Register.cpp:3–4 gate even I2C register support
  on SPI_INTERFACES_COUNT undefined or>0, and include GenericDevice/SPIDevice.
  BusIO therefore brings compile dependencies on SPI types even for this I2C use.
- SPIDevice.h:61–64 disables fast pin I/O for __ZEPHYR__, before its generic
  ARM branch. Installed cxxflags.txt:14 explicitly defines __ZEPHYR__=1;
  platform.txt:26,135 selects gnu++17 and ARDUINO/ARDUINO_ARCH_ZEPHYR macros.
  Common.h:45–49 provides BitOrder and installed SPI.h exists. The reviewed
  core/variant/SPI headers do not define SPI_INTERFACES_COUNT; final preprocessor
  output should establish its actual state for the exact probe.
- I2CDevice.cpp:14–20 defaults to32-byte chunks outside its SAMD/ESP32 branches;
  the14-byte sensor burst fits. Its generic requestFrom form:197–203 and
  Wire.end/setClock branches:49–54,311–318 must compile against ZephyrI2C.
- Unified Sensor.h:23–30 selects Arduino.h/Print.h for ARDUINO>=100.
  Its .cpp contains Serial printing even if the helper is ultimately link-dead;
  do not invoke that helper in the probe.

Sources: [BusIO Register header](https://github.com/adafruit/Adafruit_BusIO/blob/3b8364267c3ee6e16bad91bc2101aefbd5b5915f/Adafruit_BusIO_Register.h#L6),
[SPI header](https://github.com/adafruit/Adafruit_BusIO/blob/3b8364267c3ee6e16bad91bc2101aefbd5b5915f/Adafruit_SPIDevice.h#L61),
[I2C implementation](https://github.com/adafruit/Adafruit_BusIO/blob/3b8364267c3ee6e16bad91bc2101aefbd5b5915f/Adafruit_I2CDevice.cpp#L196),
[Unified header](https://github.com/adafruit/Adafruit_Sensor/blob/0a9127a1e886ff1adb4c1b6f5958b24108d55aa6/Adafruit_Sensor.h#L23).

The existing upstream runtime blockers remain verified: MPU begin allocates,
performs retries/delays and initializes hardware; _init defaults gyro to500dps,
not the required>=1000dps. reset polls without an iteration/deadline bound.
_read ignores the14-byte read result into an uninitialized local array, then
reads two ranges; getEvent timestamps before acquisition and returns true.
Separate sensor objects reacquire independently. Events use m/s² and rad/s;
their timestamp is not proof of a fresh hardware generation.
[MPU implementation: begin/reset/read/event](https://github.com/adafruit/Adafruit_MPU6050/blob/502a7caccda630a151dfb03ecbdd4b8452809ef7/Adafruit_MPU6050.cpp#L70).

BusIO's own read/write_then_read can report short-read and transfer failure,
but Adafruit MPU discards relevant results. Additionally Register::read returns
0xffffffff on failure (:188–190), Bits::read masks that value (:330–333), and
the reset bit consequently remains1 on persistent I2C failure. MPU reset's
unbounded loop can therefore persist on transport errors, not only a physically
stuck reset bit. RegisterBits::write (:342–353) also does read-modify-write
without separately rejecting a failed prerequisite read.
[Register implementation](https://github.com/adafruit/Adafruit_BusIO/blob/3b8364267c3ee6e16bad91bc2101aefbd5b5915f/Adafruit_BusIO_Register.cpp#L188).

| Pinned full-content file | SHA-256 |
|---|---|
| MPU6050 Adafruit_MPU6050.cpp | `dc18db3e4b03319b07f59de899d943d7d1d23c5f4e183535cb16ca6968500f1c` |
| MPU6050 Adafruit_MPU6050.h | `d4e744a8a1a87df4c9ceec8ded365b1d9d5b8bb2f3b3311aaa936011827c369a` |
| MPU6050 library.properties | `f9e1078006e646f01a01506d2a741774baad7a6a400216eb282bb278174f550d` |
| BusIO Adafruit_I2CDevice.cpp | `317c342821f1df676a0e034f65685b4d6bf240d2ab8dcea91d18f1e063326d37` |
| BusIO Adafruit_I2CDevice.h | `88b843d7a44e3f974950d883649e5682f21d9f8ce135daff3a42d015f7cd27e7` |
| BusIO Adafruit_BusIO_Register.cpp | `9a0af578ea07956296834f4505e5b134ad7e1cc22ac9c9d84a640a07a94f870b` |
| BusIO Adafruit_BusIO_Register.h | `91560f9fc1b8cda42ab039ccdfe0abf92bf09c425a6142ff54af099809b9d47a` |
| BusIO Adafruit_SPIDevice.h | `58ff1433718cef7317638403160d5dd918d92c0f7b4204fb08ad401751d74508` |
| BusIO library.properties | `1f1c13c18d84a15f71e8e833aeaf1ada2d505cc915485174167ea661ed085194` |
| Unified Adafruit_Sensor.h | `7f3a6d8889e9d852aecf1c64cdab9d66d801101ae03a9af28e86021245b04c64` |
| Unified Adafruit_Sensor.cpp | `e6cc18df0ce4dd1894b224b232d3b589536cac8ed201025f6e900facd40e7bcb` |
| Unified library.properties | `9898dcd235542e85f504cc0d1c5bff9e99f17602607dae944075fdcab6831d37` |

For reproducible subsequent acquisition, SHA-256 of codeload tar.gz URLs
`https://codeload.github.com/adafruit/REPO/tar.gz/COMMIT` was read in memory:
MPU archive `1463d1db7b9255d6ccc18e56d39a225c36f999974dea2d3fd12436f313d2a7ac`;
BusIO archive `e5d8163c527af3c868f6ff5eaf6b92ed6c6baf297b9c39906611c817d553f5eb`;
Unified archive `5d3397934cd15fe002cd2289c2fcf347856a56b8d6c9ff41f20e1b8f33abe1f9`.
REPO names are Adafruit_MPU6050, Adafruit_BusIO and Adafruit_Sensor; commits
are in the table above. The coordinator must verify downloaded bytes again.

## Recommended compile-only probe contract

This is a source-justified recommendation, not an implemented probe or adopted
behavior. It belongs in a recorded coordinator decision before dependent work.

1. Pin the three versions/commits and actual archive/source hashes. Resolve
   libraries explicitly on the existing board-side build path, record the
   display-dependency choice, selected include paths and compiler output.
   Do not silently modify upstream libraries to make the candidate pass.
2. Use a distinct **compile-only, never-uploaded** probe. Avoid global MPU or
   BusIO objects; put local construction and API calls in a noinline retained
   function. Its API surface should include explicit MPU begin(address,&Wire1,id),
   gyro1000/filter184/divisor0 getters/setters, getEvent and checked BusIO
   transfer forms. These are compile operands, not configured runtime settings.
3. setup may only publish that function's address to an externally visible
   volatile function-pointer anchor; loop is empty, and neither invokes it.
   Verify the final ELF retains the function, its call dependencies, the anchor
   and Wire1's ordinal40 binding. An unused function, if(false), or source used
   attribute alone is insufficient evidence against linker garbage collection.
4. Inspect actual final undefined symbols/relocations, especially zero-valued
   z_impl_i2c_* exports. Confirm local inline wrappers dispatch to the nonzero
   native API where expected. Inspect dependency constructors and startup paths;
   linking Wire can construct all three fixed Wire objects. Do not equate empty
   application loop with absence of every dependency constructor.
5. A pass is **selected library source/API compilation and retained link-path
   compatibility only**. Keep it separate from sensor identity, successful bus
   transactions, waveform, fault handling, timestamp freshness and timing.
   No probe registration in the inert upload allowlist is needed or implied.

If the target fails, preserve the exact compiler/import finding. If it succeeds,
the source/runtime limitations above still stand. No P2 production driver,
loader change, wiring change or physical test is necessary to answer this
bounded next compilation question.

## Explicit unknowns and reproduction

Still unknown: actual MPU6050 breakout/revision/rails/pull-ups/AD0; current live
I2C4 state; actual SCL waveform and rate; sensor identity/configuration; whether
STOP-separated library reads behave as required; unique sample generation,
coherence during faults, mounting/units calibration, bias/filter behavior,
successful/failing transaction timing and full R4 WCET. Those are not supplied
by target compilation, this package audit or the bare UNO Q connection.

The existing382.5us ideal14-byte burst and562.5us ideal complete getEvent
arithmetic at400kHz remain lower bounds from P0_G6, excluding software,
interrupts, bus-free time, stretching, extra status reads and failures. They
are not revised into measured durations here. SC-A/SC-B and later HAL design
remain outside this audit.

Reproduction used tools.board_tool.remote with existing ADB serial2629958581,
SUMO_TRANSPORT=adb and the installed Windows adb32.0.0 executable. Remote
Python used pathlib/hashlib and T nm/gdb on E. GDB was `-nx -nh -batch E`
with only p/ptype/disassemble against the file; there was no target, run or call.
Public source requests read pinned raw GitHub/codeload bytes without writing
or installing them. Two attempted GDB symbol names absent from this interrupt
build were reported absent rather than inferred; the actual selected driver/API
and complete transaction/config/init/error functions were then inspected.
Source/API links and hashes above identify the positive evidence.

Next action: coordinator records the limited compile-probe choice and performs
the separately reviewed target build. This report supplies no runtime IMU
acceptance, PINMAP approval, motor authorization or phase gate.
