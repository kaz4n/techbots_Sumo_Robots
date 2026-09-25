# D188 static diagnostic file-only ABI observation

Purpose: discover the actual new diagnostic object/type layout before designing
any bounded MCU capture. This is follow-up to the successful compile at
`P7_app_motor_fault_compile_raw/native_static01/`; it is not an upload or run.

`P7_app_motor_fault_compile_raw/inspect_static_abi.py` fixes local one-shot output
`native_abi_static01`, source `21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950`,
board `2629958581`, and freshly admitted boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. It requires a clean reviewed HEAD,
the original 127 compile input pins, hard-pinned actual result/artifact receipts,
unchanged source projection, pinned ADB, and 128 MiB free local space.

The original D185 transport/preamble and extracted bounded wait/reap functions
run in a private namespace. The hard-pinned D173 `gdb` builder and `REMOTE_READ`
block are reused, replacing only its scope label. No historical constructor or
run method executes. Four fixed commands read board-local files: readelf/GDB
versions, `readelf -hSWs` of the static ELF, and GDB batch type/member queries
against its debug ELF. GDB disables init files, auto-loading, and function calls;
its maximum value size is explicitly bounded to 1 MiB. No target connection,
compiler, upload, reset, firmware execution, or binary download exists here.

All eight actual artifacts, both file tools, loader ELF and TLS source are
hash/identity checked before and after. Each child has a 60-second deadline,
5-second reap, and 1 MiB stream bound; outer transport retains the inherited
400-second deadline. The fresh remote scope path
`/home/arduino/sumox26_codex_build/app-motor-fault-abi-static01` must be absent;
it is not created. Only temporary output files are used on Linux. The local
owner is created exclusively and never reused, including after a failed attempt.

Tagged size/alignment/layout queries cover the 18 declared types and `bool`;
ten tagged Runner member offsets identify candidate windows. The local parser
requires a unique `_ZN12_GLOBAL__N_110diagnosticE` OBJECT in the checked static
`.bss`, exact Runner size, aligned windows wholly inside the object, and the
object wholly within the checked BSS zero span. Raw ptype/readelf output is
retained for independent interpretation. Static addresses must not be combined
with D173's dynamic relocation or old 2592-byte decoder.

`--check-only --reviewed-head <40hex>` checks local files/Git and composes the
actual Windows command without ADB dispatch or file creation. `--execute` uses
the same admission, saves raw receipts plus parsed `abi.json`, checks remote
stream accounting/reaped children and final pins, and closes local pins/Git.
Any failure consumes the local owner and retains original evidence; a secondary
closure-write failure must preserve the first exception.

File ABI is not runtime evidence, measured free RAM, stack margin, WCET, physical
acceptance, or a human gate. A later separately reviewed initialization query
must derive actual entry/global-initializer addresses from retained symbols.
Any subsequent inert upload/capture requires its own exact artifact scope.

## Controlled local validation (2026-09-25)

Two `python -B -` in-memory fixture invocations exited 0, with 17 and 5 checks
passing. Helper SHA256:
`0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c`.
No native process dispatched and no observation output owner was created.
Composition used actual local compile/artifact/source/tool pins with only
`git_state` substituted for the in-progress working tree; subprocess dispatch
was replaced with a refusal. Actual clean-HEAD check-only remains required.

- Real-pin composition: 15,295 program bytes, four commands, 12 remote file
  pins, 5,493 Windows UTF-16 command units including NUL (limit 30,000).
- Admission refused wrong HEAD, dirty tree and changed artifact digest.
- Stream fixtures accepted exact valid accounting and refused byte mismatch,
  unreported stderr, malformed base64, unreaped child and changed deadline.
- Synthetic ELF/GDB fixtures accepted a bounded static object and refused
  non-EXEC images, duplicate/missing objects, Runner size mismatch,
  missing/duplicate scalar tags, duplicate offsets, out-of-object windows,
  unaligned windows and BSS-zero-span overrun.
- A simulated primary child exception remained the exact raised object when
  the final receipt write also failed; the secondary disk error was attached.

Before these checks, independent source review found that the draft's final
receipt write could mask the first exception. The repair above preserves it;
strict decoded stream accounting was also added. The initial draft was not
hashed before editing; its observed digest is unavailable. No native attempt
or established test was executed or changed during this correction.
