# D-067 fresh scoped review — 2026-09-23

Reviewer: separate fresh-context Codex agent p0_pwm_irq_fresh_review, same model;
not cross-model or human acceptance. Read-only report transcribed by coordinator.
Base5215453, contractc8e8f55, then-current uncommitted probe/tests and exact
source6578e07a. Installed reports and raw-byte fix54dd976 were also reviewed.

## Findings

None. No BLOCKER, MAJOR or MINOR findings in the compile-only scope.

## Verdict

**PASS — retained target API/link compatibility only.** P0 acceptance is pending.
No files edited, live board/debug/API operation, or probe invocation by reviewer.

- api_probe.cpp:11–44 follows the frozen parameters, statuses and call order.
  No pin, period, callback or device is selected globally.
- Sketch:7–20 rejects MOTORS_ALLOWED!=0, starts three volatile anchors null,
  publishes only function addresses and leaves loop empty.
- Independently reproduced8/8 focused checks in0.601s, WSL GCC13.3.0/strict
  C++17/UBSan. Exact pointer types/addresses, setup+10000 loops with zero API/heap
  activity, motor-enabled build rejection, six upload refusals before lookup.
  No unchanged core-suite repetition.
- Verified all26 current source-map entries and aggregate
  6578e07a23cc7209f127fa88c3defc8bad822818acea57097ce906053e7dc6bc.
  Final/debug/temp ELF sizes/hashes match remote provenance. Actual compilation
  exit0, default/MATCH0/MOTORS_ALLOWED0,80248B program/34048B globals.
- Local disassembly: setup0x6c has exactly three address stores, loop0x98 bx lr;
  retained probes0x24f8/0x25e0/0x2608 with requested Arduino call relocations.
- Native PWM uses local inline conversion/checking and device-vtable dispatch.
  attachInterrupt retains local GPIO configure/manage dispatch. No selected
  zero-valued named PWM syscall or GPIO IRQ-configure import.
- All five init_array entries inspected: dependency RAM/buffer/semaphore setup
  or registration through a local no-op atexit stub; no probe/PWM initialization,
  IRQ registration or UART/Bridge start. Inherited __loopHook0x246c still yields
  and locks a mutex with K_FOREVER; runtime boundedness is not approved.
- No existing locked test/config/board-tool/upload-allowlist change. Exact raw
  PWM receipt SHAe50cedcc...725f1e is preserved by scoped Git attributes.

Independent test command, exit0:

```
wsl.exe --exec bash -lc "cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots && python3 -B -m unittest discover -s tests/tooling -p test_p0_pwm_irq_compile.py -v"
```

Offline packaged-loader ELF SHA256:
39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd.
Final export commands, each exit0 (working directory is the repository):

```
arm-none-eabi-readelf -sW build/p0_pwm_irq_review/zephyr-arduino_uno_q_stm32u585xx.elf
arm-none-eabi-objdump -s --start-address=0x0801d018 --stop-address=0x0801d028 build/p0_pwm_irq_review/zephyr-arduino_uno_q_stm32u585xx.elf
arm-none-eabi-objdump -s --start-address=0x0801d338 --stop-address=0x0801d348 build/p0_pwm_irq_review/zephyr-arduino_uno_q_stm32u585xx.elf
arm-none-eabi-objdump -s --start-address=0x0801d7b0 --stop-address=0x0801d7c0 build/p0_pwm_irq_review/zephyr-arduino_uno_q_stm32u585xx.elf
arm-none-eabi-objdump -s --start-address=0x0801d3e0 --stop-address=0x0801d3e8 build/p0_pwm_irq_review/zephyr-arduino_uno_q_stm32u585xx.elf
```

Verified nonzero exported pinctrl_lookup_state0x08019613,
pinctrl_configure_pins0x08019637, device_init0x08019e5d, readiness0x08019e6f.
Lookup export at0x0801d020 contains bytes86f80108/13960108, decoding name
0x0801f886/address0x08019613. Both named PWM syscall exports and the named
GPIO IRQ-configure export are0, consistent with the installed audits.

No runtime load, waveform, IRQ lifecycle, timing, MotorGate, asynchronous QTR,
PINMAP or human-gate qualification follows. Recorded wrapper/error/ownership
limitations remain open. The current inert QTR image was not replaced.
