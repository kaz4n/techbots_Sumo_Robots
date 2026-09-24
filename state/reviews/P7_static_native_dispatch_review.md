# P7 selected direct native dispatch review

25 September 2026, Asia/Dubai. Separate fresh-context, same-model review;
not cross-model, human, runtime or gate review. Read-only inspection plus this
review file only; no board command, compiler, installation, firmware/test edit,
upload/reset, cleanup or commit. A bounded read-only helper independently
checked RCC/UART/init instruction claims and reported no findings.

## Findings

No open BLOCKER, MAJOR or MINOR findings within the selected direct
GPIO/PWM/RCC/device-init boundary.

## Evidence checked

The reviewed closure is `analysis/P7_static_native_dispatch_validation.md`,
SHA256 `471de2b81b2bd69884dc2d27c8e2198ec5093a4f75ff9c15ac50e31cad1e3363`.
Companion note hashes, under `analysis/`:

| File | SHA256 |
|---|---|
| P7_static_gpio_dispatch_audit.md | f224a49a38ec8377cde3832bc2af73177c3da31ebd244aa829f101edc4508632 |
| P7_static_pwm_dispatch_audit.md | fa1902450d9c7d3fedca83b6dd9b5db4a312a3c42586331e43436d37e6fc5fce |
| P7_static_rcc_dispatch_audit.md | fda4f1cd32ce7c093a7af3d26aab6eab0d0febadb933ecd76077eafa59db5482 |

Independently rehashed all31 distinct compact-receipt inputs,17 D151 local
pins,103 working-source files and102 staged files: zero mismatches. Source
identity remains fcddbd8e, debug ELF0f7f2825 and final ELF5cc2dfde. Parsed the
ELF32 section table locally and compared836 retained application instruction
or literal rows from the GPIO/PWM/RCC receipts and pinctrl helper with actual
debug-ELF bytes: zero mismatches. This checks retained excerpts, not exhaustive
control-flow coverage. Compact receipt hashes under `analysis/P7_static_link_probe_raw/`:

| File | SHA256 |
|---|---|
| gpio_dispatch_audit.json | 1d7c807431bea9bf594add7a188ee632dad2656633878e0c847830af0bfcb2ab |
| pwm_dispatch_audit.json | 51509dc19ea48c063a69294c2721ee3532d2b31870c9a4d1c528eee8110a56be |
| pwm_dispatch_type_supplement.json | 90328b4f2c6db1538df8b88476219a939b006e21d7a35740aebc0f2d3c883252 |
| rcc_dispatch_audit.json | 7daa3ced5ce09eaab9e958fb20627ddc2ab66389961cf355c783d57fba5068c3 |

Reparsed D150's actual stdout:50 ordered numbered sections,49 nonempty; only
LOADER_32 is empty. Twelve of13 common APP/LOADER comparisons match after
removing result-number prefixes. GPIO differs only at the unused
manage_callback bool/_Bool spelling. Selected GPIO slots0/4/12/16, device.api8,
device.ops.init20, PWM slots0/4, RCC on0 and stm32_pclken layout agree. The
GPIO widths/prototypes and expanded PWM typedef chains support the selected
actual argument and return conventions. RCC passes the observed device and
subsystem pointers and checks its integer status; no claim of all callback
signature coverage follows.

Inspected the actual load/branch chains and argument preparation. Motor EN
uses configure-low/read/clear; M0 rejects EN-high before dispatch. QTR charge
uses configure, while set/clear slot presence checks are not calls. PWM uses
the observed set/get slots, halfword stack flags and eight-byte rate output;
M0 rejects nonzero pulse before its setter. Source grants remain empty, while
MotorGate initialization still configures EN and zero PWM. Retained native
values and selected targets agree with the later D150 observations.

D150 remains NATIVE_API_READ_FAILED: original command0003
5b2c1c1c, result a6a0b69a and launcher46de16c1 are unchanged from the prior
review's full hashes. Its stderr still says `No function contains specified
address.`; zero command exits do not convert partial observations to success.

D151 command0003 SHA256
49eda4578514c5ae2e233b8d269ee4a8245d9d09e396daabf02278c70a7608e2
contains exactly the numeric18-byte wrapper body. It loads state at device+12,
tests byte1 bit0, returns -120 via `mvn #119`, or tail-branches to08019e2c
without changing r0. The retained installed_02.json records[13] helper calls
device+20 when non-null, bounds the saved error and marks initialization.
This supports precisely the reported wrapper/helper/selected initializer edge.
Five D151 receipts exit0 with empty stderr; before/after Claim and eight
FileRecords match inputs,26 installed-hash lines agree, and source4c39fafc
matches the unchanged-source launcher. Result835c4277 remains observation
collection, not execution evidence.

## Verdict

**PASS for the selected direct dispatch file-evidence closure.** No whole-OS,
complete reachability, loader/startup, running ownership, stack/heap/WCET,
electrical, motor, human-gate or static-production-admission conclusion follows.
Historical pending text in the companion reports remains provenance and is
explicitly superseded only for the bounded edges closed by the new report.
No firmware changed, so no new host behavior tests or target build were needed
for this evidence review. Any future startup attempt requires its own concrete,
source-bound preparation and authorization; this review does not supply it.
