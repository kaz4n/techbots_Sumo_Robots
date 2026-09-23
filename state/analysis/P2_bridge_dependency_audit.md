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

## Follow-up: CLI1.5.1 JSON dependency check contract (not adopted)

2026-09-23, subsequent read-only source audit while the coordinator validates its
separate D098 experiment. This append does not rewrite the original observations
above or certify that experiment. New pinned primary sources and hashes are under
`P2_bridge_dependency_raw/schema/`. No board command, compilation, implementation,
test or production-policy change occurred in this follow-up. A possible D099 is
not yet selected by this audit.

The smallest mechanism is **one existing compile invocation with `--json`, followed
by a narrow parser of its result before the wrapper reports app-build success**.
No second compiler, new framework, text-table scraping or source include allowlist
is needed for the specific zero-external-library policy. Apply it only to the
canonical actual app, leaving intentionally library-using benches under their
existing contracts. CLI's command implementation and JSON serialization are
`internal/cli/compile/compile.go:379-440` and
`internal/cli/feedback/feedback.go:229-258` at the pinned01f3d4f2 commit.

| Result path | Exact CLI shape / meaning |
|---|---|
| `success` | Required boolean; constructed from `compileError == nil` |
| `error` | Optional nonempty build-error string on the normal failure path |
| `compiler_out`, `compiler_err` | Strings containing captured compiler output; warnings need not imply failure |
| `builder_result` | Object, or null if no builder result was produced |
| `builder_result.used_libraries` | Array of library objects; **omitted when empty** because of `omitempty` |
| `builder_result.build_properties` | Array of `key=value` strings, normally expanded |
| `builder_result.board_platform`, `.build_platform` | Objects with optional string `id`, `version`, `install_dir`, `package_url` |
| `upload_result` | Object; normally empty for compile-only |

There is no top-level FQBN, CLI-version or compiler-version field in this compile
result. Library objects carry `name`, `version`, `install_dir`, `source_dir` and
other metadata; rejecting every nonempty list avoids interpreting incomplete
individual entries. `NewBuilderResult` explicitly returns nil for nil RPC input
and constructs its library array before Go's JSON encoder omits length zero.
The CLI JSON schema, rather than protobuf JSON naming/default rules, is decisive.
[Pinned result conversion, lines913-979](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/cli/feedback/result/rpc.go#L913).

Proposed fail-closed acceptance, all required together:

1. Actual process exit0; stdout parses as exactly one JSON object with no duplicate
   object keys/trailing data; strict `success` boolean true. Reject malformed,
   truncated, missing or alternate fatal-error envelopes. Accept `error` only
   absent or the empty string; reject explicit null/wrong types/nonempty text.
2. Require object `builder_result`, expected nonempty `build_path`, and both
   platform objects matching `id=arduino:zephyr`, `version=1.0.0` and the verified
   installed root. Require the existing independently obtained CLI1.5.1 identity;
   do not invent it from this result or from a path suffix.
3. Require a nonempty array of property strings; split each on its **first** `=`,
   reject empty/duplicate keys, and match the selected app contract's exact
   `build.fqbn`, `build.core=arduino`, variant, discovery-flag value, and controlled
   C/CPP safety flags. Check resulting link/startup properties against the existing
   contract too. Do not reject unrelated ordinary properties or assume the list
   is a JSON object. `build.fqbn` preserves the requested parsed FQBN; it does not
   automatically expand omitted default menu options.
4. Accept `used_libraries` only if absent or an empty array. Reject null, other
   types, or any array element, including null. An unknown library must fail just
   as RouterBridge does. A missing list is acceptable only after the other checks
   establish the expected normal successful build envelope.

Properties are sorted and expanded by `commands/service_compile.go:302-315`.
The normal-build imported-library list is populated by its deferred conversion
at338-344; board/core platform references come from resolved installed packages
at120-138. `internal/arduino/cores/board.go:129-139` writes `build.fqbn` from the
parsed request before applying menu properties. JSON metadata reports package
identity, not immutable package bytes; retain existing source/core/hash evidence.
[Pinned compile service](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/commands/service_compile.go#L302),
[pinned board properties](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/cores/board.go#L129).

**Invocation is part of the check.** Prohibit `--show-properties`, `--preprocess`,
`--only-compilation-database`, `--skip-libraries-discovery` and upload flags for
this result path. Show-properties/preprocess return successfully before the
normal-build library-list collection (`service_compile.go:317-343`); success
plus an absent list is therefore insufficient alone. Require the already
established artifact/hash checks for a completed build. Normal build failures
use `success:false`, `error` and nonzero exit; earlier failures can emit a different
error envelope to stderr (`feedback.go:173-204`). Preserve stdout/stderr separately;
do not treat nonempty compiler warnings as the result's failure signal.

**Macro0 does not disable ordinary explicit library resolution.** The detector
queues the merged sketch and all src translation units, runs the preprocessor,
extracts a missing active header from its error, resolves that header, adds the
library/include directory and repeats. Its resolution algorithm has no
`ARDUINO_LIBRARY_DISCOVERY_PHASE` branch. An unconditional explicit
`#include <Arduino_RouterBridge.h>` still reaches this process at either macro
value, then makes the header available to subsequent `__has_include` checks.
The candidate changes which preprocessor branches are active; it does not set
CLI's separate skip-discovery option or restrict its resolver. This conclusion
is source-verified, not a new empirical compilation result.
[Pinned detector, lines350-383 and461-564](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/arduino/builder/internal/detector/detector.go#L350).

The qualification matters: phase-conditional includes or headers may intentionally
behave differently for0/1, so there is no universal equality claim for arbitrary
libraries. A future small verification fixture should use one unconditional
header with phase-independent contents, confirm it appears in `used_libraries`
for both settings, and prove the app-only check rejects it. No such fixture or
policy is implemented here. The library list covers CLI-discovered libraries,
not every linked archive, core file, copied source or absolute-path header;
existing staging hashes and ELF audits retain those responsibilities.
