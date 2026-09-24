# Next existing-scope native dispatch check

Checkpoint after D148 structure, focused entry audit, D149 selected project ABI
comparison and the bounded native-address audit. All have scoped reviews; none
qualifies a static upload or full native runtime. No new execution scope is
adopted by this note. Reload the current handoff before continuing.

First reuse retained binary/source evidence to bind actual current app call-site
offsets to native driver slots. The concrete open site is opponent setup at
0x08111788: device+8 supplies API, API+0 supplies the branch target. Do not repeat
the already consumed compile or read operations, or collect a second ELF copy.

| Family | Current uses to check | Existing evidence under state/analysis |
|---|---|---|
| GPIO | Configure, raw read, set bits, clear bits | P2_opp_gpio_audit_raw.json; P0_qtr_bare_contract_audit_20260923.md |
| PWM | set_cycles, get_cycles_per_sec, deferred initialization | P0_pwm_installed_raw_20260923.txt; P2_motor_native_raw/clock.json |
| RCC | Direct on in ADC/I2C owners; PWM clock dependencies | P2_adc_native_raw/installed_source_03.json and _04.json; motor clock evidence |
| Device init | PWM and optional LPUART ops.init | PWM evidence; P2_dump_raw/native/offline_gdb.txt and uart_stm32_init.txt |

The exploratory lookup reports GPIOA/B/C API0x0801c6e0 with configure0x08019151,
read0x080190bd, set0x080190db and clear0x080190e5; PWM ordinals120/105/109 share
API0x0801c720 with set0x0800de4d, get0x080196d7 and init0x0800e1c5; RCC ordinal9
API0x0801c76c has on0x080189a3, get_rate0x0800b9ed, configure0x08018a13.
Re-read and bind those original observations to packaged loader39d4a4fd before
using them as current closure evidence. GPIOG/ordinal94 and optional LPUART78
are covered by the retained dump audit. These are file values, not live readings.

Only if necessary offsets/prototypes are missing, separately scope one file-only
GDB batch against the exact packaged loader, with init and object auto-loading
disabled and exact tool/loader hashes before/after. Candidate queries are ptype/o
for device, gpio_driver_api, pwm_driver_api and clock_control_driver_api; values
of gpio_stm32_driver, pwm_stm32_driver_api, stm32_clock_control_api and devices
89/90/91/94/120/105/109/9/78. Verify exact type names against installed evidence
before execution. No target, inferior, native function call, compile or upload.

Prioritize GPIOB MotorGate EN operations, PWM1/3/4 zero-duty initialization and
their clock/pinctrl dependencies before considering a bare-board M0 startup.
M0 still initializes MotorGate and PWM; it is not a proof of zero peripheral I/O.
The current SetupGrants{} leaves optional services ungranted. ADC/I2C owners
use direct registers plus RCC.on, rather than native transfer APIs; UART uses
direct registers after initialization. Keep any later optional-service/runtime
qualification explicit, including ownership, stack, timing and physical gates.

This is a concrete next audit within the existing native qualification task,
not authorization to run firmware or a new strategy/framework requirement.
