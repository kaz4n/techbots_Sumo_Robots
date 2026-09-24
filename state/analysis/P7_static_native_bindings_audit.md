# P7 current static image: bounded native binding audit

2026-09-25, Asia/Dubai. **Enumerated native bindings agree; complete reference
coverage remains pending.** This is local file inspection of the actual D144
static/default/M0 image, not a target execution, loading or physical result.
No firmware, config, policy, tests or previous entry-audit artifact changed.

The [compact receipt](P7_static_link_probe_raw/native_bindings_audit.json)
contains command arguments/statuses, selected disassembly, literal and table
records, input/tool hashes before and after, and explicit coverage limits.
Six local commands returned zero: debug/final `readelf -Ws`, debug/final
`readelf -Wr`, and two reads of the same debug ELF using Arm `objdump -d -w`.
Full disassembly stayed in RAM; its 1,647,170-byte output hash is retained.
The second read supplies two additional HAL bodies without another saved dump.
The receipt is 74,101 bytes, below the assigned 100 KiB limit.

## Image and retained evidence binding

- Debug ELF: `P7_static_tls_raw/observed/app.ino_debug.elf`, SHA256
  `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.
- Final ELF: `P7_static_link_probe_raw/diagnosis-v1/app.ino.elf`, SHA256
  `5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
- Map: `P7_static_tls_raw/observed/app.ino.map`, SHA256
  `15da1417d5a7f781195d86ba1554dd449e4e14548dde1ea8052e8da78cd16806`.
- Installed absolute definitions: `P7_static_link_research_raw/syms-static.ld`,
  SHA256 `f4f05a8a411196fad575360a1b6cc9f5f10a337864548e7387fb8580c4092d62`.
- All 103 project sources match the D139 working-source manifest before and
  after; the source digest remains
  `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.

The two ELFs have identical allocated-section names, addresses, sizes and
file-backed hashes. Both report no relocations. Neither contains a named
undefined symbol. The null symbol-table entry is not classified as an unresolved
external. This does not prove all register-indirect targets are correct.

The packaged-loader comparison reuses actual retained file-only binary evidence:
[`D139 import exports`](P7_default_qualification_raw/import_exports.json), SHA256
`a948dc53c459df625811b65ae0e350e7a7c108b20f2e21b76ffd03c9c8a1a392`, and
[`D140 loader dispatch`](P7_static_link_research_raw/loader_dispatch.stdout),
SHA256 `bb578bae6f83763e54eabd232b84c5af3dc92ac9dc23c197d401cea793b8b612`.
These bind to packaged-loader SHA256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`;
their provenance and limitations remain as recorded in the original audits.
No fresh board connection or assertion about live memory is made here.

## Present absolute symbols and actual branch destinations

All **168 present linker-provided absolute symbols** match `syms-static.ld`
numerically, in both debug and final ELFs. The other three NOTYPE absolute
symbols are the image's `_sidata` and the two derived system-heap bounds. The
six established native TLS aliases are outside this audit's scope. Symbol
presence alone is never classified as use or reachability.

The actual instruction bodies establish **22 native veneer destinations**:

- Seventeen `__aeabi_*` helpers materialize the destination with `movw ip`,
  `movt ip`, then `bx ip`: double arithmetic/comparisons/conversions and unsigned
  64-bit division. Each computed target equals the matching `__real_*` symbol
  in both the static definitions and D139's packaged-loader export observation.
- `memcpy`, `memset`, `fmod` and `sqrt` load a PC-relative target literal and
  tail-branch to it. `abort` loads its literal and calls it. All five also match
  their named packaged `__real_*` exports.

These are decoded branch destinations, not raw-word coincidences. They establish
what the bodies call if reached; they do not prove all 22 execute in this profile.
For example, the separately audited entry and constructors call the memory
veneers, while a present abort path is not evidence of an observed abort.

Selected full function bodies also establish conditional native calls through
loaded literals:

| Image body | Native destination(s) |
|---|---|
| `entry_point` | `printk`, three calls before data/BSS initialization |
| `micros` | `sys_clock_cycle_get_64`, followed by the checked division veneer |
| `UnoQMatrix::begin` | `z_impl_device_is_ready`, `matrixSetGrayscaleBits`, `matrixGrayscaleWrite`, `matrixBegin` |
| `init_dev_apply_channel_pinctrl` | `z_impl_device_is_ready`, `pinctrl_lookup_state`, `pinctrl_configure_pins`, `z_impl_device_init` |
| UART `clocksAvailable` | `z_impl_device_is_ready` for the retained clock-related devices |
| `start_static_threads` | `z_impl_k_thread_create`/`z_impl_k_thread_name_set` in the loop body; current empty table skips that body |

The entry/main conditions and their runtime limits remain in
[the focused entry audit](P7_static_entry_audit.md). The source meaning of the
HAL paths is consistent with current
[`ui_matrix_unoq.cpp`](../../src/hal/ui_matrix_unoq.cpp),
[`dump_uart_unoq.cpp`](../../src/hal/dump_uart_unoq.cpp),
[`opp_sensors.cpp`](../../src/hal/opp_sensors.cpp) and
[`motor_port_unoq.cpp`](../../src/hal/motor_port_unoq.cpp). This audit does not
establish their physical behavior or timing.

## Initialized native pointers and coverage accounting

The receipt retains raw bytes and each first-word classification for these
source-defined tables. Strides are the retained descriptor interpretation, not
a substitute for the separate native type-layout audit.

| Table | Entries | Device-pointer result |
|---|---:|---|
| Shared `arduino_pins` | 70, stride 8 | All 70 match named native device addresses |
| Motor `PWM_PADS` | 16, stride 8 | All 16 match |
| Motor `PWM_SPECS` | 16, stride 16 | All 16 match |
| Core `pinctrl_map` | 17, stride 8 | 16 match; one null device entry |

`native_pins::COUNT` is 70 and `native_pins::TABLE` points exactly to the shared
array at `0x08116168`, consistent with
[`native_pins.cpp`](../../src/hal/native_pins.cpp). Opponent setup's captured
instructions load the COUNT/TABLE objects, index the array at stride eight, and
pass the selected native device to `z_impl_device_is_ready`. Motor configuration
indexes `PWM_SPECS` at stride sixteen and passes the selected device to the core
pinctrl initializer. The captured core initializer traverses `pinctrl_map`.
This is evidence that those code paths consume the tables, not evidence that a
particular pin was exercised or electrically verified.

The separate text-literal catalog contains 65 occurrences and 28 unique native
values. It is deliberately labelled **candidates only**: an address literal in a
code section is not automatically a call or an executed reference. Combining
that catalog, the 22 proven veneer targets and the initialized table values
produces **62 distinct native address values**. Exactly 61 match the values in
D139's packaged-loader export record. The remaining `printk` Thumb address
`0x080173d5` matches D140's actual loader calls to instruction address
`0x080173d4`. No enumerated non-null native address is unexplained.

## Five allocator/random aliases

Each of `__wrap_malloc`, `__wrap_realloc`, `__wrap_free`, `__wrap_calloc` and
`__wrap_random` is marked `[!provide]` in this map. Neither the wrapper name nor
its exact base name is a symbol in this image. Their expected native addresses
have no matching aligned word in any allocated file-backed section and no match
among the checked MOVW/MOVT veneer targets.

This supports **no reference identified through those named aliases and checked
encodings**, not a missing-definition defect. The expected addresses and native
allocator arena remain the D140 source/binary facts; no alternate allocator is
invented. These results cannot prove absence of allocations behind arbitrary
computed pointers or native services, nor a whole-program no-allocation claim.

## Specific remaining coverage gap

The full original requirement to resolve *every used* external reference is
**not yet proved**. There is no complete control-flow/reachability reconstruction
here, and runtime-loaded driver API slots are not established by application
literals. A concrete example is opponent setup at `0x08111788`: its branch
register is loaded through the selected device's API pointer (`device+8`) and
then API slot zero. The actual slot target lives in the packaged native image,
not in the inspected application's literal pool. Other GPIO/PWM/clock operations
have corresponding indirect driver dispatch paths.

The next bounded closure task is to map those reachable driver slots and data
structure offsets to the pinned packaged image, using retained native ABI/binary
evidence where it covers the exact slot, and a file-only extraction for anything
missing. Do not promote the 62-address catalog to a complete reference set or
silently treat the 119 table entries as measured hardware. Public ABI comparison,
startup/runtime verification, stack headroom and complete tick WCET remain
separate. No static-production adoption, gate or motor-run permission follows.

All new output is these two compact audit files. No compiler output, duplicate
ELF/map, temporary script, Python cache or installed tool was generated.
