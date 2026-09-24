# P7 current static application's GPIO dispatch audit

25 September 2026, Asia/Dubai. **PASS for the scoped application instruction,
header and retained packaged-driver mapping. GAP for a direct packaged-loader
DWARF type/offset comparison.** No board command, build, upload, reset, peripheral
operation or production edit occurred. This is not startup or hardware acceptance.

The [compact receipt](P7_static_link_probe_raw/gpio_dispatch_audit.json) is 64,521 B,
SHA-256 `1d7c807431bea9bf594add7a188ee632dad2656633878e0c847830af0bfcb2ab`.
It records actual local command arguments/statuses, selected instruction and DWARF
output, historical commands explicitly **reused, not rerun**, and before/after
hashes. All five captured commands returned zero with empty stderr. Ten retained
inputs, three tools and all 103 frozen source files were unchanged. Git HEAD was
`57cb362f`; source identity remains
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.

## Bound evidence

- Actual static debug ELF: `P7_static_tls_raw/observed/app.ino_debug.elf`, SHA-256
  `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.
  Final ELF `5cc2dfde`, map `15da1417` and static definitions `f4f05a8a` are also
  pinned; the earlier general native/entry audit is not repeated here.
- [Retained native receipt](P2_opp_gpio_audit_raw.json), SHA-256 `cfc9e52a`,
  identifies packaged loader
  `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
  Its successful file-only GDB commands print GPIOA/B/C objects and the named
  `gpio_stm32_driver` members. These are packaged-file values, not live memory.
- [Official GPIO header](P2_qtr_native_raw/source/gpio.h), SHA-256
  `aab7888876f29b6ad98217d8099aac677f5238249b95599511038cc35d982316`,
  exactly matches that receipt's installed header. Its retained
  [provenance](P2_qtr_native_raw/source/manifest.json) pins Arduino Zephyr commit
  `1743741760ee5d2d58da50d504855d43f9f8e826` and HTTP/source-hash evidence.
- Existing [bare GPIO audit](P0_qtr_bare_contract_audit_20260923.md) establishes
  the retained QTR pad mapping and evidence limits. No pin approval is inferred.

## Slots, prototypes and device selection

Actual application DWARF gives `device` size 36 and member offsets name 0,
config 4, **api 8**, state 12, data 16. Its `gpio_driver_api` is 40 B:
configure 0, get 4, masked-set 8, set 12, clear 16, then five remaining slots.
The receipt includes the relevant DIEs and linked typedef/base-type DIEs.
The retained generated autoconf `52178f5e` has no `CONFIG_GPIO_GET_CONFIG` and
enables `CONFIG_GPIO_GET_DIRECTION`, consistent with this observed layout.

| API offset | Header prototype, typedefs expanded | Retained loader target | Scoped use |
|---:|---|---|---|
| 0 | `int(const device*, uint8_t pin, uint32_t flags)` | `0x08019151 gpio_stm32_config` | Motor EN low configuration; optional QTR and opponent configuration |
| 4 | `int(const device*, uint32_t* value)` | `0x080190bd gpio_stm32_port_get_raw` | Motor EN readback; optional QTR and opponent reads |
| 12 | `int(const device*, uint32_t pins)` | `0x080190db gpio_stm32_port_set_bits_raw` | QTR non-null capability check; no call in these inspected families |
| 16 | `int(const device*, uint32_t pins)` | `0x080190e5 gpio_stm32_port_clear_bits_raw` | Motor EN low write; also QTR capability check |

The prototypes come from header lines 241–282 and 810–825, corroborated by
the current application's debug types. Native function addresses are Thumb
pointers. GPIOA ordinal 89 at `0x0801c064`, GPIOB ordinal 90 at `0x0801c040`,
and GPIOC ordinal 91 at `0x0801c01c` all have API `0x0801c6e0` in retained GDB.
The driver's printed member order agrees with the current offsets; it is not a
direct measurement of native DWARF offsets or native function prototypes.

Current `config.h:71,74,159` and previously pinned table mapping select:
EN D10/PB9; opponents D11–D13/PB15–PB13, D16–D17/PA6–PA7 and D18–D19/PC1–PC0;
QTR D2/PB3, D4/PA12, D7/PB2 and D8/PB4. All these DT flags are zero.

## Actual calls in the current ELF

Instruction addresses below identify calls, not merely words in literal pools.
The receipt retains the loads connecting each call to its target or helper.

| Current function / source | Instruction chain |
|---|---|
| `UnoQPort::configureEnableLow`, motor_port_unoq.cpp:246 | `0x08110bce` loads device+8, `0x08110bd4` loads slot0, `0x08110bd8` calls it; flags `0x60000` = OUTPUT_LOW |
| EN readback in configure, writeEnable and enableLow | Calls at `0x08110bf4`, `0x08110c78`, `0x08110cae` reach helper `0x081106e6`; it loads device+8 at `0x081106ea`, slot4 at `0x081106ee`, calls at `0x081106f0` |
| `UnoQPort::writeEnable`, motor_port_unoq.cpp:288 | `0x08110c5c` loads device+8, `0x08110c5e` slot16, `0x08110c60` calls with pin mask |
| `Reader::configure` / cleanupPad, line_qtr.cpp:185,390 | Calls `0x0810f892` / `0x0810fcc4` reach helper `0x0810f350`; device+8 at `0x0810f36a`, slot0 at `0x0810f374`, tail-call `0x0810f378` |
| QTR readCharge / readDischarge | Calls `0x0810fa18` / `0x0810faec` reach helper `0x0810f37a`; device+8 at `0x0810f37e`, slot4 at `0x0810f382`, call `0x0810f384` |
| `Sensors::begin`, opp_sensors.cpp:57 | device+8 at `0x08111772`, slot0 at `0x08111784`, call `0x08111788`; INPUT flags `0x10000` |
| `Sensors::read`, opp_sensors.cpp:77 | device+8 at `0x08111832`, slot4 at `0x08111836`, call `0x08111838` |

QTR configure selects OUTPUT_HIGH `0xa0000` or INPUT `0x10000`; cleanup selects
INPUT. Charging therefore uses **configure slot0**, not a set-bits call. QTR
`validSpec` at `0x0810f3b4` only checks slots 0/4/12/16 for non-null values
(`line_qtr.cpp:37–45`). Slot presence alone is not execution evidence.

In this M0 image `writeEnable` tests the `high` argument at `0x08110c36` and
rejects a true value before its driver call. Its only GPIO write dispatch is
clear slot16; no set slot12 call exists in that function. This matches
`MOTORS_ALLOWED == 0` at motor_port_unoq.cpp:291–300. Raw-read helpers preserve
nonzero native errors and extract a pin bit only after a successful port read,
consistent with gpio.h:1565–1580. Inline configure also updates the inversion
metadata at device.data before calling the native driver, as the header specifies.

## M0 scope and the remaining exact query

`app.ino:20` supplies empty SetupGrants. `runtime.cpp:78` initializes the
transaction before optional sources; `motors.cpp:83–95` still configures EN,
writes it low and initializes zero PWM. These native dependencies must be
qualified for an inert startup. Opponent and QTR setup require their separate
false-by-default grants (`runtime.cpp:57–60`); their retained machine code is
covered above, but their physical operation is not authorized or demonstrated.

The old GDB receipt prints device and driver **values**, not their compiled
`ptype`/offsets. Therefore the remaining direct native-type comparison is explicit.
One coordinator-owned file-only invocation against the pinned packaged ELF could
use `-nx -nh -batch -iex "set auto-load no"`, then these `-ex` expressions:

```text
set language c
ptype /o struct device
ptype /o struct gpio_driver_api
ptype gpio_stm32_config
ptype gpio_stm32_port_get_raw
ptype gpio_stm32_port_set_bits_raw
ptype gpio_stm32_port_clear_bits_raw
p sizeof(int)
p sizeof(gpio_pin_t)
p sizeof(gpio_flags_t)
p sizeof(gpio_port_value_t)
p sizeof(gpio_port_pins_t)
```

Require native device.api offset8, GPIO offsets 0/4/12/16, matching prototypes
and widths 4/1/4/4/4. This query was **not executed** here. The receipt records
the exact pinned packaged path and arguments. No target, inferior or function
call is needed. Missing debug types would remain a gap, not an assumed pass.

This closes the scoped application dispatch identification without claiming
complete native ABI compatibility, all GPIO consumers, current loader identity,
native internal-call coverage, peripheral ownership at runtime, stack/heap/WCET,
static adoption, startup permission or any human/physical gate. The final native
type comparison is a software evidence step; actual electrical and full sensor
runtime checks remain distinct later work. Full 1.65 MB disassembly and 24.28 MB
DWARF text stayed in memory; only focused excerpts were saved. No binary copies,
temporary compiler tree or bytecode were created.

After writing, a separate PowerShell hash check again found zero mismatches across
the ten pinned inputs and 103 sources. An optional repository-wide WSL
`git diff --check` stalled for over a minute and was terminated along with only its
identified Python parent (child argv, parent PID and repository cwd checked first).
No Git-check success is claimed; the completed focused audit commands and their
receipt are unaffected. No test, compiler, board attempt or tracked-file mutation
was involved in that terminated read-only check.
