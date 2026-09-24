# P7 static RCC calls and optional UART initialization

25 September 2026, Asia/Dubai. **Scoped RCC call identification and common type
comparison PASS. UART helper-to-initializer mapping established; the 18-byte
device_init entry wrapper remains a GAP.** D150 itself remains terminal FAILED.
This audit reused its successful sections without rerunning a board command or
turning its failed section into success. No build, install, upload, reset,
peripheral operation, source/configuration change or binary copy occurred.

[Receipt](P7_static_link_probe_raw/rcc_dispatch_audit.json): 85,165 B, SHA-256
`7daa3ced5ce09eaab9e958fb20627ddc2ab66389961cf355c783d57fba5068c3`.
The four local inspection/version commands returned zero with empty stderr.
Sixteen original inputs, four later evidence inputs, three tools and all 103
frozen source files were checked unchanged. Full disassembly/DWARF stayed in RAM;
only focused output was saved. The separately completed GPIO files remain frozen.

## Identities and scope

The actual debug ELF is
`P7_static_tls_raw/observed/app.ino_debug.elf`, SHA-256
`0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.
Source identity remains
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
Final ELF, map, static definitions and source manifest are pinned as in the
[GPIO audit](P7_static_gpio_dispatch_audit.md).

Retained primary evidence is `P2_adc_native_raw/installed_source_03.json` and
`installed_source_04.json`, with their exact `query_installed_03.py` / `_04.py`
collectors; `P2_dump_raw/native/uart_identity_receipt.json`, `offline_gdb.txt`,
`uart_stm32_init.txt` and `native_receipt.json`; and
`P2_adc_ownership_raw/installed_02.json` with `query_02.py`. Full hashes and the
selected actual commands/statuses are in the receipt. The UART saved text matches
its original command stdout after ordinary CRLF decoding. Retained package identity
is loader SHA-256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
These are packaged-file values, not live MCU state.

## Direct application RCC.on calls

Both call sites load device `0x0801befc` (RCC ordinal 9), load its API at device+8,
check `on`, and dispatch API slot0. Retained GDB records RCC API `0x0801c76c`
and `on = 0x080189a3 stm32_clock_control_on`.

| Source / actual containing function | Actual call chain and arguments |
|---|---|
| power.cpp:198–207, inlined into `power::Reader::beginProfile` | device+8 at `0x0811233a`, slot0 load at `0x08112384`, call at `0x08112386`; stack words `{0x8c, 0x400}`, then RCC+0x8c bit10 readback |
| imu_bus_unoq.cpp:143–150, inlined into `imu::Bus::begin` | device+8 at `0x0810e41a`, slot0 load at `0x0810e43c`, call at `0x0810e43e`; stack words `{0xa0, 2}`, then RCC+0xa0 bit1 readback |

Actual application DWARF specifies `clock_control_driver_api` size28 and `on`
offset0. `stm32_pclken` is size8: bus bits0–11, div bits12–31, and enr at byte4.
The constructed words therefore specify div0, the listed bus and enable mask.
Do not substitute the retained **other** ADC configuration `adc_stm32_cfg_1`
with bus0x94/enr0x20 for the actual current ADC12 request bus0x8c/enr0x400.

The retained native `stm32_clock_control_on` body at `0x080189a2` extracts the
low12 bus bits, rejects a bus outside 0x88–0xa8, ORs enr into RCC+bus, reads that
register back, and returns. It contains no polling loop or further function call.
This agrees with the [pinned official source](P2_adc_native_raw/clock_stm32_ll_u5.c):168–187,
SHA-256 `ae2a3612`, whose URL/revision/hash are retained in `downloads.json`.
Finite instructions in this one function are not a complete setup or tick WCET
measurement, and readback is not physical clock qualification.

## Actual D150 common-type evidence

The coordinator's [actual command receipt](P7_static_link_probe_raw/native_api/0003.json)
has 50 labeled query sections, 49 nonempty. Its GDB return code is0 but stderr is
`No function contains specified address.`; the experiment therefore remains
FAILED. No result below depends on the failed query succeeding.

The exact APP/LOADER text blocks 00, 01, 04, 05 and 07 match: `device`,
`device_ops`, `clock_control_driver_api`, `stm32_pclken`, and
`clock_control_subsys_t` (`void*`). In particular, device.api is+8,
device.ops.init is+20 and has prototype `int(const device*)`; clock.on is+0;
the pclken bitfields and size above agree on both sides. LOADER29 reports
`stm32_clock_control_on` as `int(const device*, clock_control_subsys_t)`.
LOADER20/24 confirm the retained RCC device/API values. These successful sections
close the scoped common-type comparison that was initially pending D150.

The by-name `whatis z_impl_device_init` in LOADER28 instead describes the exported
constant (`void* const`). LOADER32, the by-name disassembly, is empty. This is
symbol-resolution failure, not evidence that the native entry is absent.

## Optional UART device_init path and remaining wrapper gap

In `UnoQDumpPort::begin` (`dump_uart_unoq.cpp:138–157`) the current ELF requires
four explicit grant bytes before setup. It checks metadata/readiness and pristine
device state, configures its ready input, then calls native `device_init`:
`0x0810c574` loads the literal at `0x0810c694` (`0x08019e5d`),
`0x0810c576` passes UART device `0x0801c13c` (ordinal78), and `0x0810c578` calls.
The ready-pin GPIO configuration is a separate optional dispatch, outside the
MotorGate/QTR/opponent GPIO scope; it is not made necessary by this audit.

Retained GDB and D150 LOADER21 agree that UART78 has
`ops.init = 0x0800f351 uart_stm32_init`. ADC ownership receipt records[13]
successfully disassembles `do_device_init`: at `0x08019e2e` it loads device+20,
and at `0x08019e44` calls that initializer if non-null. It records an initializer
error magnitude capped at255 and sets the initialized bit after the initializer
returns, on success or failure. It does not establish an in-progress lock.

The retained symbol table identifies adjacent code addresses:

```text
08019e2c T do_device_init
08019e5c T z_impl_device_init
08019e6e T z_impl_device_is_ready
```

The successful helper disassembly ends at `0x08019e5a`. It does **not** contain
the wrapper at `[0x08019e5c, 0x08019e6e)`. The historical ADC receipt records[12]
already preserves the same failed by-name wrapper query. Symbol adjacency cannot
prove the missing wrapper-to-helper branch. If required before inert startup,
the smallest remaining evidence is file-only numeric-range disassembly of those
18 bytes from the pinned package, e.g. `disassemble /r 0x08019e5c,0x08019e6e`.
This audit did not execute that query or authorize a board action.

## Native internals and eligibility are separate

The retained UART initializer calls RCC.on through device+8/API+0 at
`0x0800f36a`, using its retained pclken `{bus=0xa8, div=0, enr=0x40}`. It also
traverses pinctrl, reset, parameter, error-log and IRQ setup paths; this note does
not recursively qualify that whole native graph. Its body explicitly contains
unbounded TEACK polling at `0x0800f500–504`, REACK polling at `0x0800f506–50a`,
and an exclusive-access retry at `0x0800f3f2–400`. These remain optional setup
dependencies, not evidence of a bounded post-setup control tick.

The current `app.ino:20` supplies empty SetupGrants. ADC and IMU admission in
`runtime.cpp:55,64` is false; `runtime_dump.cpp:8` returns before UART setup when
dump_enabled is false. Thus the two direct RCC.on sites and optional UART setup
are retained application paths, presently ungranted. M0 MotorGate initialization
still has its own GPIO/PWM/native dependencies, covered separately; this result
does not claim there are no other RCC users.

No new software defect is asserted from a missing evidence slice. The unresolved
wrapper edge, all native internal coverage not scoped here, actual loaded image,
runtime ownership, startup/stack/heap/WCET and physical tests remain distinct.
This note grants no static adoption, upload/run permission or phase/human gate.
