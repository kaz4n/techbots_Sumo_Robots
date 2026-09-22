# D-067: installed PWM and interrupt compile-only compatibility

Scope: P0 0.1 G2. Installed-source audits are in
P0_pwm_installed_contract_20260923.md and P0_irq_installed_contract_20260923.md.
This probe checks selected headers, retained code and loader imports; it is not
a driver, motor writer, asynchronous QTR implementation or runtime acceptance.

- New bench/p0_pwm_irq_compile stays outside every upload allowlist. Use only
  `python tools/board_tool.py flash bench/p0_pwm_irq_compile --compile-only`,
  default startup, MATCH=0, MOTORS_ALLOWED=0. No upload/reset, pin/IRQ operation,
  peripheral initialization, configuration/dependency changes or new tunables.
- Public src/api_probe.h includes Arduino.h, zephyrPinctrl.h and
  zephyr/drivers/pwm.h. Three retained noinline functions take all settings and
  device/pin selections as parameters; no proposed motor/QTR pad is selected.
- `int probePwm(const pwm_dt_spec*, size_t state_pin_index, uint32_t period_ns,
  uint32_t pulse_ns, uint64_t* cycles_per_sec)` returns -EINVAL for null spec or
  cycle output. Otherwise call zephyr::arduino::init_dev_apply_channel_pinctrl,
  returning its nonzero status; check pwm_is_ready_dt, returning -ENODEV if false;
  call pwm_get_cycles_per_sec, returning its nonzero status; finally return
  pwm_set_dt(spec,period_ns,pulse_ns). No runtime bound or valid mapping is implied.
- `int probeAnalog(pin_size_t pin, int value, int resolution_bits)` references
  analogWriteResolution(bits), analogWrite(pin,value), then returns the no-arg
  analogWriteResolution(). This only exposes the Arduino path for ELF inspection;
  it does not recommend mixing analogWrite with an explicitly set PWM period.
- `int probeInterrupt(pin_size_t pin, void (*callback)(), PinStatus mode)` retains
  digitalPinToInterrupt(pin), attachInterrupt(pin,callback,mode), detachInterrupt(pin)
  in that order and returns the mapping result. This is intentionally never run:
  even digitalPinToInterrupt mutates slot state, and detach is not hardware cleanup.
- Public pointer aliases PwmProbe, AnalogProbe and InterruptProbe match these
  signatures. Globals p0PwmProbe, p0AnalogProbe and p0InterruptProbe are volatile
  pointers, initially null. setup only assigns the respective function addresses;
  loop is empty. Static-assert MOTORS_ALLOWED==0. No global device object or API call.
- Independent host tests must derive only from this contract and public header:
  setup/10000 loops retain exact addresses with zero API calls/allocations,
  motor-enabled compile rejects, and upload refusal precedes board lookup for
  default and Immediate configurations. Never invoke the probe functions in tests.
- Compile on the actual selected UNO Q Linux toolchain; retain source/artifact
  hashes, command exit status, package versions and exact symbol/relocation evidence.
  Confirm setup only stores addresses, all three probe bodies/API paths survive
  optimization, and used exports are real or correctly inlined through device APIs.
  A merely successful link cannot prove runtime loadability or call availability.
- Fresh separate-context review is read-only. Preserve any failure and investigate
  at most two unsuccessful fixes of the same issue; no upstream patches or relaxed
  tests. Stock wrapper error masking, timer sharing, interrupt ownership/detach
  hazards and unmeasured PWM/IRQ timing remain explicitly flagged for later HAL.

No phase gate, PINMAP approval, motor permission, hardware observation, electrical
waveform or full-tick WCET follows. Current inert QTR firmware remains untouched.
