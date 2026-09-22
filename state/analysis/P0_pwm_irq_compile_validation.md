# P0 G2 D-067 PWM/interrupt compatibility validation — 2026-09-23

Status: **TARGET-COMPILED / HOST-TESTED / fresh scoped review PASS.**
This is a compile-only result. No probe function, PWM operation, interrupt
registration, motor/header write, upload, reset or MCU debug read occurred.
The current MCU image remains the reviewed inert QTR61d7a2d0/default image
uploaded at03:00:13.327+04 under D-052. No new physical measurement is claimed.

## Scope and files

D-067 public contract/header commitc8e8f55 precedes implementation and independent
test authorship. The root implemented only bench/p0_pwm_irq_compile's sketch and
api_probe.cpp; a separate test-author used the contract/public header without
reading those implementation files. The installed PWM and IRQ auditors owned
separate reports/raw files, merged into F-086/F-087 by the coordinator in5ad262d.

Three retained noinline bodies compile explicit-period native PWM, Arduino
analogWrite resolution/output, and Arduino interrupt query/attach/detach APIs.
All device/pin/mode/period selections remain parameters. setup merely publishes
three addresses in volatile function-pointer anchors; loop is empty. Static
assertion rejects MOTORS_ALLOWED1. The sketch has no upload allowlist entry.
No src/core, src/hal, src/config.h, existing test or board-tool behavior changed.

## Actual target build

Native Windows Python invoked the existing tools/board_tool.py via explicit
ADB serial2629958581, compiling on UNO Q Linux rather than Windows/WSL:

```
python tools/board_tool.py flash bench/p0_pwm_irq_compile --compile-only
```

Receipt: P0_pwm_irq_compile_target_20260923.txt. Started03:20:35.162100+04,
ended03:22:01.126257+04, exit0 on the first attempt. CLI1.5.1/core1.0.0,
FQBN arduino:zephyr:unoq, default startup, MATCH0/MOTORS_ALLOWED0. No install
or package change. The three prior Adafruit pins and existing six libraries
remain in the recorded inventory. No upload command was issued.

- Exact26-file source SHA256:
  `6578e07a23cc7209f127fa88c3defc8bad822818acea57097ce906053e7dc6bc`.
- Compiler accounting:80248B program,34048B globals,228096B remaining.
  These figures do not measure free heap/stack or production recorder headroom.
- Remote artifacts:
  `/home/arduino/sumox26-build/6578e07a23cc7209f127fa88c3defc8bad822818acea57097ce906053e7dc6bc/p0_pwm_irq_compile/artifacts/bench-default`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Final .ino.elf | 80248 | `28af3e12493370098ab8ec35ab221638ec32d944e324835c46f98a181870917e` |
| .ino_debug.elf | 1929984 | `31b4846f091eae23520b29cab16f21c88f566d1771199ccab134e634259cb898` |
| .ino_temp.elf | 1945312 | `3a95dff8b2531df7ed077c0e3332a85100646726a501c3a3b29b1cc173f6b159` |

P0_pwm_irq_compile_provenance_20260923.json preserves the source map, literal
command arrays, outputs/exit statuses, inventory, artifact hashes and complete
symbol/relocation/disassembly receipts for the three ELFs. Hash-checked local
copies are ignored build/p0_pwm_irq_review/. A packaged Linux loader ELF copy
was also pulled for offline export inspection, SHA39d4a4fd; this is not MCU
flash identity or runtime state. Every recorded command exited0.

## Host checks and binary observations

Independent command:
`wsl python3 -m unittest discover -s tests/tooling -p test_p0_pwm_irq_compile.py -v`
passed8 tests in0.573s, exit0. Raw receipt:
P0_pwm_irq_probe_host_tests_20260923.txt. Strict C++17/g++13.3/-O2/UBSan,
-Wall/-Wextra/-Werror/-fno-exceptions/-fno-rtti. Six compile-time type checks
and50010 C++ assertions verify initial nulls, exact setup anchors and every one
of10000 loop iterations with zero counted API calls/allocations. Additional
tests reject motor-enabled compilation and six upload/startup combinations
before board lookup, transport, staging or subprocess execution. They never
call the probe bodies. These substitutes do not validate peripheral behavior.

Root offline ELF inspection confirms setup0x6c contains three pointer stores,
loop0x98 returns, and probes survive at0x24f8/0x25e0/0x2608. PWM get/set calls
inline-dispatch through the supplied device API; probeAnalog retains both
resolution overloads and analogWrite; probeInterrupt retains query/attach/detach.
No named z_impl_pwm_* or z_impl_gpio_pin_interrupt_configure import is selected
by those inspected paths. Relevant initialized export and constructor details
are independently reviewed in the companion review record.

The image still contains the inherited RouterBridge __loopHook with a K_FOREVER
mutex path. Setup/loop/probe nonexecution evidence is not a claim that uploading
this entire image would satisfy R3/R4. It stays compile-only. Likewise generic
PWM helper success does not prove a routed channel or nonzero clock rate; the
probe is not a checked production driver or MotorGate implementation.

The full306-tooling checkpoint and earlier3 IMU checks remain separate; this
turn adds8 focused checks, not a newly combined317-test run. The895-case core
checkpoint was not rerun because no core/config/established tests changed.

Fresh same-model reviewer independently reproduced8/8 checks in0.601s, verified
all26 source entries and three ELF hashes, inspected all five init_array entries,
and verified nonzero pinctrl lookup/configure and device init/readiness exports.
Verdict PASS/no findings: ../reviews/P0_pwm_irq_compile_codex.md. This is not a
human/cross-model review or complete P0 gate review. Root additionally verified
all14 committed installed raw receipts byte-for-byte against captured files and
all15 compile/artifact receipt exit statuses, plus unchanged probe source identity.

## Failure history and remaining limits

No compilation or new host test failed. The IRQ source audit preserved two
initial HTTP404 path guesses followed by successful official-source retrieval;
these were source lookup failures, not missing installed APIs.

Evidence packaging check found Git newline normalization changed the captured
PWM raw receipt when first committed (83280B to81764B). Commit54dd976 adds
scoped byte-preservation attributes and re-stages the original captured bytes,
without rewriting history or modifying semantic evidence. Git now preserves
the recorded83280B/e50cedcc... receipt exactly. Dated IRQ raw files and the
three compile/test receipts likewise retain captured bytes. Raw tool whitespace
is not reformatted to pass a diff check.

Stock PWM fallback/error masking, shared-timer updates and exact pin routing;
IRQ error reporting, ownership, pending state, detach/rearm races and latency;
physical waveform/fault behavior; real QTR freshness; and full robot WCET remain
unqualified. F-086/F-087 and spec_conflicts.md retain later regression needs.
No asynchronous QTR semantics, pin change, frequency, runtime waiver, P2 HAL,
PINMAP OK, STAND/RING permission or human phase gate follows.
