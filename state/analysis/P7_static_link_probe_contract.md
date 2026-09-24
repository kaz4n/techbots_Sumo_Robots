# Proposed D141 static/M0 artifact probe contract

**D141 policy-only host preparation is adopted; the full probe remains a draft.**
Only the fixed public policy component below may be implemented and host-tested
after its independent oracle freeze. Artifact/runner implementation, properties
queries and native compilation remain unapproved. The question is whether one unchanged current
app can produce a correctly placed, source-bound static artifact using the
installed package's existing static mode. This cannot qualify loading, native
I/O, live RAM, stack, timing, motor operation or a release gate. D139's dynamic
default deficit of 592 bytes and both unadopted optimization candidates remain.

## One exact profile and immutable inputs

- Project `app.ino`; FQBN `arduino:zephyr:unoq:link_mode=static`; default/wait
  startup; literal C/C++ flags `-DMATCH=0 -DMOTORS_ALLOWED=0`; unchanged discovery
  flag `-DARDUINO_LIBRARY_DISCOVERY_PHASE=0`; exactly one actual compiler with
  `--jobs 1`. No alternative profile, MATCH, Immediate, flag or config override.
- Current 103 source files and existing 102 staged files must match the D139
  manifests and source/stage digest
  `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
  Reuse the independently tested D139 read-only stage verifier with its literal
  source pin and pinned manifest bytes; no stage deletion, restaging or fallback.
- Source/config/bench files and capacities remain byte-identical. Freeze the
  new probe implementation, references and independent tests before execution;
  retain existing dynamic policy/reference files byte-identically.
- A unique static-probe policy/run path separates all output from prior dynamic
  receipts and binaries. Claim its output/build directories exclusively; reject
  preexisting directories, symlinks and artifact destinations before invoking the
  compiler. Every fixed output must be newly produced by this invocation. Missing,
  empty, stale or otherwise unbound outputs fail even if packaging exits zero.
  No overwrite or cleanup of prior evidence or denied paths.

## Preserve policy checks; admit only the reviewed static recipe

Keep this one-source experiment in new files under
`state/analysis/P7_static_link_probe_raw/`: a scoped reproducer, complete command
reference and pin manifest, plus task evidence. Do not add a general production
tool or make the normal flash command accept Static. The coordinator will settle
the exact public interfaces before independent tests freeze. Keep functions
below 60 lines; use the existing policy's pure parsing,
path, CLI, builder and hash helpers and existing captured-command transport.
Do not patch production validators, normalize a static result into a dynamic
result, replace a rejection callback, or broaden `board_tool.py flash`.

The dedicated entry accepts only an explicit compile-only request for the fixed
profile; it has no upload/reset route. Before any compiler invocation it must:

1. Preserve source containment, symlink, reserved-local-source and current
   config validators through the exact read-only stage check; bind local and
   remote staged bytes before compilation and again afterward.
2. Validate CLI 1.5.1/commit, core 1.0.0, resolved data/user directories, compiler
   location, unique build path, and every existing installed dependency pin.
   Retain the existing local-platform/boards/sketch override rejection.
3. Add exact pins for `memory-static.ld`, `syms-static.ld`, firmware config and
   the three packaging/size executables from the installed-source collection.
   Keep all existing pins, including `build-static.ld` and packaged loader.
4. Validate one properties-only result against the **entire** existing controlled
   property-key set and an independently reviewed complete static reference.
   No wildcard mode substitution, relaxed hook set or unreviewed extra key.
   The static changes must be derived from pinned platform/boards sources:
   static FQBN/link mode, static linker scripts and five exact wrap options,
   static combine/check/rodata recipes, `-prelinked` packaging, and static size
   calculation using `app.ino.bin-zsk.bin`. Wait startup adds no startup flag.
5. Require the same complete property/reference checks on the actual compiler
   JSON, empty error/upload results, correct builder identities and zero external
   libraries. Nonzero command results or malformed/duplicate/nonfinite JSON fail
   closed with original stdout/stderr/return code retained.

The package's static check recipe is literally `true`; its existence is not a
fit check. A passing compiler result therefore remains separate from the artifact
validation below. Source-to-tool revision mapping must be reviewed before freezing
the references; embedded Go module names alone do not prove repository URLs.

## Fixed public policy interfaces

The first bounded component is
`state/analysis/P7_static_link_probe_raw/static_policy.py`:

```python
validate_preflight(text, *, build_path, data_dir) -> dict[str, str]
validate_compile_result(text, *, build_path, data_dir) -> dict[str, str]
```

Both return the exact validated `build_properties` mapping. Invalid input raises
`ValueError`, including malformed JSON, non-string text and invalid argument
types. They perform no transport, subprocess, network or write operation; their
only data-file read is the colocated frozen `static_reference.json`. Reuse the
existing pure parser/builder helpers, without changing or rebinding them.
The validator must compare that file's bytes to the reviewed literal SHA-256
before using it; a modified reference cannot redefine the accepted commands.

The reference is a flat mapping of all 84 existing controlled keys to exact
template strings. Only `@DATA_DIR@` and `@BUILD_PATH@` are substituted. Project,
safety flags and startup are literals, not caller options. Both validators
enforce the fixed profile, exact installed data/core/compiler paths, canonical
absolute argument paths and complete controlled-key equality. Compile validation
also rejects every nonempty or non-list `used_libraries`; the existing absent-key
default is an empty list. A properties-only preflight is not library discovery.
Fixed non-controlled metadata also includes `upload.extension=bin-zsk.bin`;
validating this literal does not create an upload interface or permission.

The independent author may prepare policy tests from this public interface and
the reviewed reference before implementation. The full artifact/execution
interfaces remain pending. Completing this component cannot authorize a board
query/compiler or produce `STATIC_ARTIFACT_PROBE_PASS`; the rest of this contract
and separate review still apply.

## Artifact validation required before a positive probe verdict

Bind final/debug/temp ELF, raw BIN, both generated ZSK forms and link map to the
exact source, tool pins, effective commands, FQBN and unique run. Retain one
checked final ELF and compact extracted evidence locally; keep other needed
checked files on Linux. Use an explicit fixed artifact list, never suffix guessing.

- Require little-endian ARM ELF32 (`ELFCLASS32`, `ELFDATA2LSB`, `EM_ARM`) and
  `ET_EXEC`; reject relocatable/shared images. Freeze the exact ARM/Thumb ABI
  flags against the pinned toolchain before accepting an image. Reject any
  relocation requiring runtime processing: the linked loader does not relocate
  this payload. Retained non-ALLOC diagnostic relocations need explicit separate
  classification. Parse entry and allocated sections/segments, including holes,
  alignment, file-backed load addresses and NOLOAD regions. Confirm that
  the executable entry is the Thumb entry at flash payload start `0x08100010`
  (`e_entry`/function-pointer Thumb bit handled explicitly), with `.entry_point`
  actually first. Inspect the exact entry disassembly and constructor ranges.
- Every flash load byte and the complete flat BIN/ZSK extent must stay within
  the pinned sketch partition `[0x08100000, 0x081c0000)`, with the 16-byte header
  accounted separately. Every RAM allocation, including final alignment padding,
  must stay within `[0x20013890, 0x20053890)`. Reject unexplained allocated orphan
  sections or overlaps. Freeze permitted named sections and placement from the
  pinned linker script; unexpected TLS, GOT or dynamic sections fail closed.
  Show actual end addresses and remaining spans; do not infer fit from the
  package's writable-section sum alone.
- Verify `_sidata/_sdata/_edata/_sbss/_ebss`, copy/zero extents and constructor
  ordering against installed `entry_point`; `.noinit` is inside this script's
  BSS output region. Do not silently assume old log preservation semantics.
- Resolve every used external call/data reference against the pinned absolute
  symbols/loader. Inspect the five wrap resolutions, heap references, static
  thread initialization, main/setup handoff and relevant native-HAL addresses.
  Reject unresolved strong or unexplained used-zero references; classify any weak
  references explicitly. Report relevant ABI sizes and old member offsets against
  D139. No unexpected capacity, object-size or source change may be accepted.
- Validate the **flat** `app.ino.bin-zsk.bin` header from the reviewed exact
  packaging source: version 1, Arduino magic, declared full length, linked flag
  exactly `0x02`, no debug/Immediate/wait-for-app bits, and exact payload equality
  to the corresponding raw BIN. Check payload mapping against ELF flash load
  bytes and expected gaps. The additionally generated ELF-ZSK is diagnostic; it
  is not interchangeable with the static upload-form artifact.
- Record source-derived unused spans separately from any allocator/runtime
  observations. The dynamic LLEXT allocation model cannot be relabeled a static
  model; the linked branch skips `llext_load`, but other startup/runtime behavior
  still exists and is outside this artifact-only claim.

## Independent tests, review and stop boundary

Before implementation execution, a separate author freezes synthetic policy and
artifact fixtures without reading the implementation. Include rejection controls
for profile/safety/startup drift, source/manifest drift, path/override/pin drift,
missing/extra effective properties, unexpected libraries/upload results, wrong
entry/address/alignment/extent, out-of-bounds RAM or flash, malformed headers,
wrong linked/startup flags, payload mismatch and failed subprocesses. Verify
wrong ELF class/endianness/machine/type/ABI flags and runtime relocation fail.
Include packaging exit zero with an otherwise-valid old BIN/ZSK pair: the runner
must reject those stale destinations before compiling or validating them. Verify
rejection occurs before the compiler/transport tripwire where applicable.
Established dynamic tests and exact dynamic-reference bytes remain unchanged;
ordinary dynamic validation must still reject static input. A separate reviewer
checks the accepted scope, frozen tests and exact new code before the coordinator
authorizes one properties query and one actual compile.

After that explicit authorization, stop after the one terminal compiler result
and artifact collection. A compile or artifact failure is a valid negative result:
preserve it, return nonzero and do not retry, repair or change capacities/flags.
A successful artifact verdict is only `STATIC_ARTIFACT_PROBE_PASS`; it is not
adoption of static linking or permission to upload. Any later deployment or
production-policy change needs its own reviewed scope and existing authorization.
