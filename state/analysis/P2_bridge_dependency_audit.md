# P2 inherited Bridge dependency: removal boundary

2026-09-23 Asia/Dubai. Scope: installed source/version/file reads on board Linux
through ADB serial2629958581, cached ELF interpretation and pinned official source
downloads. No compile experiment, upload, reset, MCU access, native operation,
firmware/config/test/tool edit, installed package change or commit occurred.
Only this report and `P2_bridge_dependency_raw/` were written by this task.
The coordinator's parallel IMU accessor changes were not edited.

## Finding

**No supported source-level Bridge-disable hook exists in the inspected pinned
core/library.** Narrowing native HAL includes alone cannot remove the roots:
the required `.ino` is prefixed with `Arduino.h`, the UNO Q variant deliberately
discovers RouterBridge, and the discovered library's singleton object is linked
directly. Emptying the sketch or suppressing a private HCI header guard would
not establish removal.

There is a precise **isolated build-property experiment** using the existing CLI
override mechanism, with no installed edits, alternative main, new FQBN mode or
linker change. It would force the core's discovery macro to its normal-build
value during discovery. That bypass is not an official Bridge opt-out and is not
an adopted production policy. Selecting it requires a separate bounded engineering
decision and target evidence; this audit supplies neither a fit nor an upload
authorization. If the next task must remain strictly source-only with the
unmodified build properties, the Bridge-removal premise is blocked by these
installed dependencies. The unrelated passive IMU and pin-table reductions remain
independently eligible.

## Reproducible source identity

`P2_bridge_dependency_raw/installed_receipt.json` records the exact read-only argv,
UTC timestamp, return code, installed path, byte count, remote hash and local-copy
hash for 16 files. The refreshed CLI reports **1.5.1**, commit **01f3d4f2b**,
build date 2026-06-05. `primary_tree_receipt.json` resolves that release to full
commit `01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea`; downloaded files and their hashes
are in `primary_sources_receipt.json` and `compile_primary_receipt.json`.

| Installed file | SHA-256 |
|---|---|
| core `Arduino.h` | `5f068c10a0aeb2f6d3cec1fa8b2a313b1f7374bcb77716f0b6cddba5bc198514` |
| UNO Q `postvariant.h` | `7a9789a1b9752a8da3f96ff5bc9c3f9c18ab37cb1eef2c6a871f4f3036589e79` |
| core `platform.txt` | `d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638` |
| RouterBridge `library.properties` | `a7d74f8dee9513cd7e4e29486de32bad071ddb6a1bcbd1ecc541f3ebeacd2aba` |
| RouterBridge `src/hci.h` | `3151c72764945649405ad189f3954402f9d2e074d5542df13878a634d872e050` |
| generated failed app `app.ino.cpp` | `a0b967ed18445450c65b10cd929921eb3a8a8c8098dfd3341411a005b6502e8e` |
| installed EDK `includes.txt` | `7189bd9a00755c1292194716cabac68d5f08ef8fcefa22f01ae4b8810f480575` |

The official core commit `79b3f1afdad455f55e4a25030953617152c0227c` matches
installed Arduino.h, main.cpp, postvariant.h and variant.h byte-for-byte. Its
platform.txt differs only in package display name/version: upstream
`Arduino Zephyr Boards`/`9.9.9`, installed `Arduino Q Boards (1.0.0)`/`1.0.0`.
The four captured RouterBridge files match official tag0.4.3 exactly. See
`primary_core_library_receipt.json`; this is not a claim of whole-package source
reproducibility. `generated_sketch_receipt.json` preserves the existing failed
fe65a3ad sketch preprocessing result and the absence of `boards.local.txt` at the
queried path; absence was not replaced with guessed contents. The initially
guessed primary CLI command-doc path returned404 and remains in its receipt;
the actual pinned CLI implementation and official command reference were used.

## Why the source-only shortcuts fail

1. CLI `builder/sketch.go:37,104-112` checks the main sketch for a literal
   Arduino.h include using a regex, then prefixes the include if none is found.
   It does so before concatenating the source. The captured failed app's first
   line is exactly that include. Moving functions to CPP or leaving an empty
   INO does not change the condition. An inactive `#if 0` include can fool the
   regex, but is not an official dependency-control interface and would not
   remove the eight real HAL Arduino.h includes. Do not adopt that trick.
   [Pinned CLI sketch implementation](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/builder/sketch.go).
2. Installed `Arduino.h:176` includes postvariant.h. The latter has `#pragma once`
   and no named opt-out guard: discovery phase1 unconditionally includes
   Arduino_RouterBridge.h; phase0 includes it if found. The source explicitly
   describes forcing library discovery. The variant's
   `ARDUINO_ROUTERBRIDGE_PROVIDES_SERIAL` is a capability result, not a disable
   switch. Private `ARDUINO_ROUTER_BRIDGE_H`/`BRIDGE_HCI_H` guards only control
   contents after the header has already been located.
   [Pinned postvariant](https://github.com/arduino/ArduinoCore-zephyr/blob/79b3f1afdad455f55e4a25030953617152c0227c/variants/arduino_uno_q_stm32u585xx/postvariant.h).
3. RouterBridge0.4.3 does not set `dot_a_linkage`. CLI `libraries.go:204-222`
   compiles its recursive source tree and directly appends all object files
   unless that property selects an archive. Thus discovering the library keeps
   singletons.cpp's initializer even if application references are otherwise
   removed. Changing installed library metadata is outside this task; a private
   include-guard macro alone is insufficient.
   [Pinned library metadata](https://github.com/arduino-libraries/Arduino_RouterBridge/blob/0.4.3/library.properties),
   [pinned linker-input construction](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/builder/libraries.go).
4. The existing strong `__loopHook()` is a supported weak-symbol override, but
   controls the loop call only. Preserve it. `initVariant` is another weak
   hook; changing it cannot prevent global initialization before main. Replacing
   main/entry_point or suppressing all init arrays would lose required app and
   native initialization. No such replacement is proposed.

## Bounded isolation experiment, not executed

The installed platform has exactly:

```text
build.library_discovery_phase=0
build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE={build.library_discovery_phase}
```

Both C and CPP compile recipes consume the second property. CLI preprocessing
clones the build properties, **overwrites `build.library_discovery_phase` to1**,
and derives the preprocessing recipe from the CPP recipe. Therefore passing only
`--build-property build.library_discovery_phase=0` does not disable discovery.
Overriding the flag property's literal value avoids that substitution. This is
deduced from exact code, not confirmed by a new preprocessing or target run.
[Pinned GCC preprocessing implementation](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/builder/internal/preprocessor/gcc.go).

The one candidate delta is:

```text
--build-property build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0
```

Keep the existing `compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0` and
`compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0`, default FQBN
`arduino:zephyr:unoq`, installed toolchain/core and all source bytes unchanged.
Use a new explicit build/output directory rather than the shared sketch cache.
The supported CLI mechanisms are build-property overrides and explicit build
paths; Arduino does not document this particular property value as a Bridge
feature switch. The published phase contract expects1 during discovery.
[Official CLI1.5.1 compile options](https://docs.arduino.cc/arduino-cli/commands-reference/arduino-cli_compile/),
[pinned platform phase contract](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/docs/platform-specification.md).

An exact initial control source is the existing frozen failed fe65a3ad tree:

```sh
probe_root=/home/arduino/sumox26_codex_build/fe65a3adcefccd3084a8e9d131baf8bb01902434a5dd54816df46952298a7b89
arduino-cli compile --fqbn arduino:zephyr:unoq --verbose \
  --build-path "$probe_root/bridge_dependency_probe/build" \
  --output-dir "$probe_root/bridge_dependency_probe/artifacts" \
  --build-property 'compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0' \
  --build-property 'compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0' \
  --build-property 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' \
  "$probe_root/app"
```

This is a proposed future board-Linux command, not a command run in this audit.
First recheck the frozen tree's source manifest; do not conflate results with the
coordinator's newer passive-accessor source. A separate fresh baseline directory
with the identical command minus the single candidate property should reproduce
the original overflow before attributing any delta.

Why this may isolate the root: with no RouterBridge include directory yet added,
phase0's `__has_include` should be false, so the core does not discover that
library or its transitive stack. The captured EDK includes file has no RouterBridge,
library or stub directory; no src/app or src/hal code explicitly includes
RouterBridge. Native checked HAL uses Arduino declarations and DT values, not
Bridge/Serial calls. The existing main implementation and link entry remain the
normal ones. These are necessary premises, not proof of the resulting graph.

## Required evidence before considering adoption

- Preserve exact source, generated INO CPP, expanded commands, dependency files,
  selected library list and all three ELF variants. The experiment must remove
  implicit RouterBridge/RPClite/MessagePack discovery and singleton roots; any
  remaining explicit dependency invalidates the predicted removal.
- Inspect final main/initVariant/static-thread-startup relocations and bodies,
  strong empty loop hook, exported main and every init/fini entry. Required app
  Runtime/native initialization must remain; only unintended library roots may
  disappear. Prove no startup-mode or linker-entry change.
- Match native API declarations, DT-derived pins/timers/ADC/IMU bindings, clock
  implementation and required native/math imports to the baseline. No replacement
  pin map, inferred API, new serial implementation or removed safety branch.
- Measure actual section and symbol differences; independently recompute loader
  overhead and headroom. A payload fit alone is not a load/WCET/free-RAM result.
- If successful, a new reviewed build contract must pin this dependency policy,
  prevent arbitrary flag injection, test both ordinary and experimental command
  construction, fail closed if required external libraries are accidentally
  omitted, preserve upload guards and distinguish historical inert manifests.
  Do not silently add the override to all bench sketches: existing diagnostics
  may intentionally require libraries/Serial. This is not yet a production fix.

If that build-policy experiment is outside the selected scope, stop the Bridge
removal track at this explicit premise. Continue the proven source-only
opportunities; do not replace the mandatory library with a fake local stub,
shadow Arduino.h/postvariant.h, alter installed packages, or claim that the
existing 21962-byte attributed cohort is now removable.
