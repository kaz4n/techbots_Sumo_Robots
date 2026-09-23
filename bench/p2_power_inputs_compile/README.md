# D093 compile-only ADC input-owner probe

`python tools/board_tool.py flash bench/p2_power_inputs_compile --compile-only`
uses the configured board-side build transport. This sketch has no upload allowlist
entry. Its `setup()` only stores a function pointer and `loop()` is empty. Global
constructors obtain passive ports; they do not initialize or sample peripherals.

The retained `power_inputs_probe::exercise` body links the actual native Reader,
fixed InputOwner, UI projection, Robot, native MotorGate and AttemptRecorder. It
includes explicit complete-tick receipts. It is never invoked by the sketch and
is not an application scheduler: external sensor evidence/readiness and slot
grants remain caller obligations. Do not execute it as a bare-board sensor test.

Compilation, source/ELF identity and host substitutes are separate evidence.
Neither proves physical ADC accuracy, electrical ownership, button windows,
sensor readiness, full 800 us timing, motor safety measurements or a phase gate.
