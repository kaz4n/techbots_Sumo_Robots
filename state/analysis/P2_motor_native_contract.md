# D077 Native MotorGate backend contract

Scope is actual P2 B4 native callbacks for the existing MotorGate under D051/D075.
No app integration, upload/run, waveform/PINMAP/phase acceptance. Prerequisites
are established by P2_motor_clock_audit.md and P2_motor_update_audit.md, including
actual installed metadata and retrieved RM0456/ES0499. This contract is finalized.
Public API motor_port_unoq.h is fixed; private state may be adjusted by its owner.

## Native instance and immutable settings

motors::UnoQPort owns no constructor I/O and cannot be copied. port() has no I/O,
allocation or reset effect; returns the same checked callbacks/context and four
immutable candidate periods. Its lifetime encloses its sole MotorGate instance.
Only MotorGate invokes those callbacks; no other output writer or command API.
Exclusive ownership of EN, four pads and TIM1/3/4 is an integration prerequisite.

Centralize unchanged proposed PWM pins3/5/6/9 and EN10 in config.h. New selected
development defaults: MOTOR_PWM_HZ10000, MOTOR_PWM_SETTLE_US150 and
MOTOR_PWM_SETTLE_MAX_POLLS4096 (explicit count-name exception, not a time claim).
No B16 value changes. Names are MOTOR_PWM_PINS[4] and MOTOR_ENABLE_PIN.
Use installed DT-generated PWM specs and GPIO pad tables,
match config-selected GPIO pads uniquely, then derive the per-device Arduino
state index. Never use analogWrite, guessed global PWM indices or a whole-state
pinctrl call. Validate all mappings before the first GPIO configuration: indices,
nonnull device/config, supported physical bit, zero flags, unique signal pads,
expected supported timer/channel mapping and no alias with EN/opponent/QTR pads.

Candidate cycles derive from installed clock lineage, never from an assumed
CPU=timer clock. Installed source candidate rates are32MHz/2.5MHz/32MHz/32MHz;
at10kHz periods are3200/250/3200/3200. port() rejects an unsupported source config
by returning zero periods, so Gate rejects before output configuration. Require
positive integral carrier periods within the actual16-bit timer limit and the
same period on shared TIM3. Use the clock report's exact RCC/HCLK/APB/parent-PSC
macros/formula and domain source checks. The MCU frequency itself remains unmeasured.

D077 clarifies D075: immutable source-derived
candidates may be copied before begin; configurePwm validates actual initialized
rates/routing after acknowledged EN LOW and before admitting channel duty writes.
The native getter is cached initialized metadata, not independent clock measurement;
also check PSC and exclude all other clock owners. No runtime clock reconfiguration.
Mismatch fails begin; never mutate MotorGate's copied periods or infer a live rate.
Every native callback remains bounded; device init/pinctrl only occurs in setup.

## Checked setup and transaction behavior

configureEnableLow validates the bank, checks readiness and configures only the
EN GPIO as OUTPUT_LOW. Preserve success only after successful native status and
raw pin readback0; otherwise invalidate local enable state and returnfalse.
Readback acknowledges the MCU interface, not the physical driver voltage. Restrict
EN's device to installed GPIOB and derive its GPIO registers from DT; verify its
selected bit remains OUTPUT/PUSHPULL/NOPULL using the installed LL getters before
and after later writes, and before admitting PWM/settle work. Do not copy a private
GPIO config ABI or silently reconfigure a remuxed EN pin during a transaction.

writeEnable(false) starts a new transaction: clears written/settled state even
on failure, then makes a checked LOW write/readback on the initialized EN pin.
It must remain usable for cleanup after other callback failures. No absent/invalid
mapping, readiness failure or unexpected read status may count as success.

configurePwm only accepts a known channel while initialized EN is acknowledged
LOW; routes that channel with the native helper, verifies ready and live cycles
against its immutable period and expected timer clock/prescaler/mode. It does
not set a duty or assert EN. Mark that channel configured only after success.
No callbacks initialize or remux hardware after this setup callback.

writePwm requires a configured channel, acknowledged EN LOW, exact immutable
period, pulse<=period, normal polarity and still-valid device/timer ownership.
Settle success and this channel's current-write bit are invalidated before
attempting it. Call checked native
pwm_set_cycles once, preserving failure asfalse; mark this channel's current
write only after success and retain its requested pulse. A repeat write updates
that channel but cannot reuse a prior settle. Gate normally writes all four once.
MOTORS_ALLOWED0 rejects nonzero native pulse requests as additional protection;
the Gate already requests allzeros in that build. Never silently clamp to success.

writeEnable(true) is rejected in MOTORS_ALLOWED0. Otherwise require all four
current writes, a successful current settle, initialized configured bank, current
EN LOW readback and unchanged relevant timer/pulse settings. Only then attempt
checked HIGH/readback1. Any failure invalidates local settled/enable-low state;
Gate performs its existing LOW/allzero cleanup and latches its fault. No callback
may claim the resulting physical output is safe after an unacknowledged write.

No runtime initialization during cleanup: unconfigured channel writes returnfalse
without touching that peripheral. Gate still attempts other channels. A partial
setup failure may therefore need a fresh boot/object lifecycle, not a fabricated
successful reset. Full configured instances may recover via Gate's normal reset
only when every LOW/zero/settle action succeeds. No new retry loop or fault bypass.

## Fresh timer update confirmation

settle returnsfalse without timer operations unless all four channels configured,
all four current writes succeeded, and EN is acknowledged LOW. Start one unsigned
microsecond deadline for the complete pass, not one per timer. Recheck ready,
EN readback and expected settings. Require TIM1/3/4 upcounting, running counters,
update enabled, regular update source, no slave/external trigger, no interrupt/DMA
or unowned channel use, expected prescaler/ARR, PWM1/normal enabled/preloaded owned
channels, and zero TIM1 repetition. Also exclude OPM/dithering, OCclear/full extended
mode bits, complementary outputs, all break/automatic-output/deadtime/lock options.
Exact masks and distinct reset/partial/full-state expectations are supplied by
P2_motor_clock_audit.md. Complete state has CR1=CEN|ARPE, CCMR1/CR2/SMCR/DIER=0,
only owned PWM1+preload fields/enables, and TIM1 BDTR=MOE/RCR0. Do not read reserved
TIM3/4 advanced-only registers. Newly initialized state is CEN without ARPE, ARR0,
all channel registers0. First successful setting adds that channel's enable/mode
and shared ARPE. Maintain the acknowledged enabled-channel progression, allowing
cleanup of an initialized channel while another channel remains unconfigured.
Reject initially ready/preowned timer devices except the same instance's already
configured shared TIM3; do not reset an unknown owner's timer. Once configured,
no callback reinitializes or resets it to disguise a state mismatch.

Clear stale UIF once on each unique timer AFTER all writes. Poll a bounded fixed
three-timer pass, accumulating separately observed fresh update bits. Native first
enable UG or preexisting UIF cannot satisfy this contract. After allthree fresh
bits, recheck EN/settings and require time still strictly below150us before true.
Readiness/configuration loss, elapsed>=150us or4096passes returnsfalse. Wrap uses
unsigned subtraction. Frozen clocks cannot create an unbounded loop; the count
guard may conservatively expire first. No delay/sleep or elapsed-only success.
No artificial UG, counter restart or claim of cross-timer simultaneous updates.
An event racing a clear is post-write: if its set wins it qualifies; if cleared,
wait for the next event. Do not require an intermediate observed UIF0. Exact MMIO
write/read order is part of final target inspection; no cached flag substitute.

A successful update observation proves the source-specified latch sequence only;
GPIO/compare readback alone is not waveform, full-duty, deadtime or physical EN
proof. Whole-tick WCET and fault-path timing require later actual measurements.
clockUs returns the current wraparound micros value; no additional services.

## Independent checks and target probe

Compile this actual native cpp using controlled installed-shaped headers. Test
factory/constructor no I/O; full mapping validation; native failures/readiness/
readback at every slot; exact routing and live period mismatch; no HIGH until all
writes and fresh updates; independent timers/sharedTIM3; separate preload/active
values; stale/late/missing flags; every relevant mode/owner change; zero/full/
reversal ordering; micros wrap/freeze and deadline boundaries; bounded counts/no
allocation. Compose the real existing MotorGate in both default0 and host-only1
with unchanged locked tests. Invalid/unconfigured cleanup must remain explicit.

Prepare a new inert compile-only bench retaining a real UnoQPort and MotorGate,
with a never-called begin/apply/reset wrapper. Constructor/factory are inert;
setup only retains function address; loop empty. Compile default and MATCH-only
configuration separately, never upload. Verify actual retained imports/register
paths/constructors/loop against the installed toolchain. A board-only compile
does not qualify runtime hooks/loader or energize anything.

Separate test-author context uses this finalized contract/public headers/API facts,
not implementation cpp. Separate fresh reviewer is read-only. Preserve locked
tests, failures and exact raw bytes. Existing five inert source guards change only
after independent diff approval; never expand the upload allowlist.

Probe public interface: bench/p2_motor_native_compile/src/native_motor_probe.h
declares Result{began,applied,reset}, Probe=Result(*)(uint32_t,constRobotResult&),
native/gate/address globals and exercise. Global native default construction and
gate{native.port()} perform no I/O. exercise calls actual begin/apply/reset in that
order and retains every result, but no startup/loop path invokes it. setup assigns
the address only; loop is empty. Both MOTORS_ALLOWED0/default and1/MATCH may compile
for retained-path evidence; neither upload is allowed. Quarantine the platform
EMPTY macro at the public probe include boundary. Tests must execute startup and
10000 loops in both configurations with zero native I/O, and verify upload refusal
for both transports/default/Immediate, before target lookup or any board action.
