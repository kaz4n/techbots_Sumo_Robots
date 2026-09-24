# P7 static default/M0 PWM dispatch audit

2026-09-25, Asia/Dubai. **Actual application call-site offsets identified;
packaged formal ABI and device-init dispatcher confirmation remain pending.**
This is file-based evidence for the unchanged D144 application and retained
packaged-loader observations. No board connection, compiler, installation,
upload, reset, firmware execution or motor operation occurred in this task.

The current date is Friday 25 September, PLAN section 3's assembly/P1/P2 day.
The authoritative PROGRESS ledger nevertheless places this authorized software
preparation in P7; the calendar does not create a passed human gate.

## Inputs and reproducibility

The [compact receipt](P7_static_link_probe_raw/pwm_dispatch_audit.json) binds:

| Evidence | SHA256 |
|---|---|
| Current debug ELF, `P7_static_tls_raw/observed/app.ino_debug.elf` | `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd` |
| D139 working-source manifest | `c106c0fb8baaf0a6f2536558da0084bd7d236c4ee8e77a4110b60107ad073391` |
| [Original PWM receipt](P0_pwm_installed_raw_20260923.txt) | `e50cedcc257c7bc00315c207ddd6b010b250375ad24cbb6a92347532cf725f1e` |
| [Motor clock receipt](P2_motor_native_raw/clock.json) | `cba7a393e4abd0a9083dd9ebb774a20ef629f2242184818329568f915d82d6ca` |
| [Prior native binding receipt](P7_static_link_probe_raw/native_bindings_audit.json) | `c3233593034e9446b4333f8e02bacf1fcec8b89de3d48fefd6b1406f09565804` |

All 103 current source files match their manifest hashes before and after the
bounded disassembly. Thus this inspection retains source identity
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
The input hashes and WSL Arm objdump hash are unchanged. The recorded command
returns zero with empty stderr:

```text
/usr/bin/arm-none-eabi-objdump -d -w --start-address=0x08110cc4 --stop-address=0x08111004 state/analysis/P7_static_tls_raw/observed/app.ino_debug.elf
```

The receipt contains that complete selected 832-byte instruction-address span,
the reused pinctrl helper body, exact historical command arrays/statuses and
selected original source/binary lines. No duplicate binary, scratch script,
build output or bytecode was created. Only this note and its JSON are new.

## Packaged devices and targets

Original PWM raw lines 4, 107-141 and 1240-1251 bind the observations to loader
SHA256 `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
The original file-only GDB commands returned zero. These are packaged file
values, not freshly read MCU memory:

| Device | Address | API | `ops.init` | Deferred flag |
|---|---|---|---|---:|
| pwm1 / ordinal 120 | `0x0801c3c4` | `0x0801c720` | `0x0800e1c5` | 1 |
| pwm3 / ordinal 105 | `0x0801c37c` | `0x0801c720` | `0x0800e1c5` | 1 |
| pwm4 / ordinal 109 | `0x0801c358` | `0x0801c720` | `0x0800e1c5` | 1 |

The named API print gives `set_cycles = 0x0800de4d` and
`get_cycles_per_sec = 0x080196d7`; native disassembly begins at the corresponding
even instruction addresses. `ops.init` names `pwm_stm32_init`. Printed named
members establish values; they do not alone establish every member byte offset.

## Actual application dispatch

| Current call | Instruction evidence | Meaning and retained target |
|---|---|---|
| `UnoQPort::timerValid`, rate query | `0x08110d10` loads device+8; `0x08110d16` loads API+4; `0x08110d18` branches | r0 device, r1 channel 4 for timer0 or 3 otherwise, r2 pointer to eight output bytes. Named retained getter is `0x080196d7`. |
| `UnoQPort::writePwm`, cycle write | `0x08110fb4` loads device+8; `0x08110fb8` loads API+0; `0x08110fc0` branches | r0 device, r1 channel, r2 period, r3 pulse; halfword flags from PWM spec+12 are stored at stack+0. Named setter is `0x0800de4d`. |
| `configurePwm` to core initializer | `0x08110eaa` branches through literal `0x08115855` | Device comes from the checked PWM-spec table; r1 is the per-device pinctrl index. |
| Core initializer to native device init | `0x0811589e` branches through literal `0x08019e5d` | This path follows a false `device_is_ready` result; r0 is the device. The actual packaged dispatcher from this entry to `ops.init` still needs inspection. |

Both rate/write status checks are in the captured bodies. The installed PWM
header excerpts supply `int` return and device/channel/period/pulse/flags or
device/channel/`uint64_t*` arguments. The native setter reads its fifth argument
as a halfword at stack+40 after a 40-byte push, consistent with the current
caller. The native getter writes two words at r2. These instruction observations
support argument compatibility; the exact packaged and app type queries remain
the explicit formal ABI check.

The M0 write body compares saved pulse r6 against zero at `0x08110f70` and
rejects nonzero at `0x08110f72`, before the native call. This is a code property,
not an observed output level. `MotorGate::begin` still configures EN low, requests
EN low, configures four PWM channels, calls zeroPwm, and settles. M0 setup thus
still initializes peripherals and issues zero-duty writes.

## Initialization dependencies and evidence limits

The retained native PWM initializer dispatches RCC on/configure/get-rate through
API offsets 0/24/12. The motor clock receipt's later explicit
`p *pwm_stm32_config_N.pclken@2` query is the applicable configuration binding:
TIM1 entries are bus164/enr2048 then bus14/enr255; TIM3 bus156/enr2 then
bus13/enr255; TIM4 bus156/enr4 then bus13/enr255. The earlier bare `p pclken_N`
observations differ and remain preserved in the original receipt; they are not
silently substituted for the explicit config-pointer observation. The RCC
coordinator audit owns that interface's formal closure.

Inside packaged PWM initialization, `0x0800e284` loads reset device/id from PWM
data+4/+8; `0x0800e28c` loads that device's API at +8, `0x0800e28e` selects +12,
and `0x0800e292` calls it if nonnull. Original raw lines 1242-1244 identify reset
device ordinal69 at `0x0801bf20`, with IDs3979/3713/3714. Pinned driver source
names this `reset_line_toggle_dt`. This is an inherited internal dependency of
the native PWM driver, not an additional direct application API boundary. Its
presence does not imply an exhaustive operating-system dependency audit.

The getter computes the stored native `tim_clk/(prescaler+1)`. It does not
independently measure the live timer clock. Likewise, named pinctrl/default
states, device readiness and successful return values cannot replace ownership,
electrical, waveform, timing or motor safety measurements.

## Exact remaining file-only check

Compare `ptype /o struct device`, `ptype /o struct device_ops`,
`ptype /o struct pwm_driver_api`, and `ptype pwm_flags_t` on the current app
and pinned packaged loader. On the loader, inspect `whatis` for
`pwm_stm32_set_cycles`, `pwm_stm32_get_cycles_per_sec`, `pwm_stm32_init`, and
`z_impl_device_init`; query the PWM API and device120/105/109 values; disassemble
`z_impl_device_init` and its actual named init dispatcher if needed. In
particular, establish the `device.ops.init` byte offset and the actual branch
that consumes it rather than assuming the layout from source field order.

The coordinator owns one combined, separately bounded file-only GDB batch with
init/object auto-loading disabled and exact ELF/tool identity checks. No such
batch was run by this task. A reset-device print may corroborate that inherited
object; speculative reset type names are unnecessary for this interimage ABI
closure. The current status is deliberately pending that exact formal check,
not a full-reference, static-runtime, peripheral/timing, physical or human-gate
acceptance.
