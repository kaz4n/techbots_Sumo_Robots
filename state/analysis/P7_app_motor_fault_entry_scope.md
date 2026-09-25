# D188 static diagnostic initialization file observation

The compiled diagnostic's actual ABI is retained in `native_abi_static01`; its
first local parser rejected GNU readelf's hexadecimal object size. The separate
offline interpreter preserves that failed attempt and raw packet. This new
scope reads instruction and initializer bytes from the same checked files.

Helper: `P7_app_motor_fault_compile_raw/inspect_static_entry.py`.
Exclusive local owner: `P7_app_motor_fault_compile_raw/native_entry_static01`.
Remote absent-only scope label:
`/home/arduino/sumox26_codex_build/app-motor-fault-entry-static01`.
No remote persistent owner is created; the local owner is never reused.

The helper loads unchanged original ABI reader SHA256
`0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c`
into a private namespace. Exact count-checked substitutions change only:

| Old literal | New literal | Count |
|---|---|---:|
| `'/inspect_static_abi.py'` | `'/inspect_static_entry.py'` | 1 |
| `'native_abi_static01'` | `'native_entry_static01'` | 1 |
| `app-motor-fault-abi-static01` | `app-motor-fault-entry-static01` | 1 |
| `D188_STATIC_FILE_ONLY_ABI` | `D188_STATIC_FILE_ONLY_ENTRY` | 2 |
| `STATIC_ABI_CHECKED` | `STATIC_ENTRY_CHECKED` | 1 |
| `STATIC_ABI_OBSERVED` | `STATIC_ENTRY_OBSERVED` | 2 |
| `'file-abi'` | `'file-entry'` | 1 |
| `'abi.json'` | `'entry.json'` | 1 |
| `StaticAbi` | `StaticEntry` | 2 |

Only its `queries` and `summarize` functions are replaced. The original reader
and actual ABI result SHA256
`684670c538bb032ab3b4b4ebc68ffd6cbecb743f0209aacc154af58b244101d2`
are added to local hard pins. Existing admission, actual compile/artifact/source
pins, board/boot bindings, 12 remote file pins, bounded/reaped children, stream
accounting, raw receipts, final closure and first-error preservation are reused.
The source projection remains `21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950`;
the boot remains the freshly observed `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.

Four file-tool commands run: pinned readelf/GDB versions; `readelf -hSWs -x
.init_array` on the new static ELF; and batch GDB on the matching debug ELF.
The GDB command disassembles 27 numeric ranges totaling 2,654 bytes, derived
from actual retained readelf symbols. Constructor C1/C2 aliases share one range
and both symbols are checked. GDB uses no target connection, init scripts,
auto-loading or function calls. Each child retains 60-second/5-second reap and
1 MiB stream limits; transport remains 400 seconds.

Selected functions cover entry, setup/loop, the global initializer, actual port
factories, Runner constructor/begin/poll/status/freeze, Trace constructor/port,
motor conversion helpers, memcpy/memset/divide trampolines, initVariant, main,
and start_static_threads. The parser rechecks their exact symbols, sizes,
bindings and `.text` containment; six init/preinit/thread boundary symbols;
the sole four initializer bytes; and the initializer's Thumb pointer. It requires
ordered unique GDB markers, exact range headers and complete nonempty instruction
coverage. The compact summary hashes each raw block instead of duplicating it.

This is file evidence. Semantic review of the observed initialization chain is
still required. Empty preinit/static-thread spans do not establish absence of
other RTOS activity. Any further constructor range must derive from observed
calls and have its own bounded scope. There is no MCU read, upload/reset,
compiler invocation, running firmware, measured RAM/WCET or human gate here.

Run `python -B .../inspect_static_entry.py --check-only --reviewed-head <40hex>`
after source review/commit; execute once only after that clean-HEAD admission.
Check-only composes commands and reads local evidence without ADB dispatch or
owner creation. Failed attempts remain consumed; original files remain unchanged.

## Controlled local checks (2026-09-25)

Helper SHA256 `cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34`.
Actual-pin composition with only the in-progress Git state substituted passed:
four commands, 27 ranges/2,654 selected bytes, 11,011 program bytes, 4,937 Windows
UTF-16 command units including NUL. Subprocess dispatch was replaced by a
refusal; no native command ran and the fresh local owner remained absent.

A separate `python -B -` controlled invocation passed 19 parser checks:
actual retained symbol tuples; complete synthetic 16-bit instructions; two
halfword 32-bit instructions; raw eight-hex-digit literal words; and refusals
for missing middle/tail, first-row-only truncation, overlap, unparsed/address
rows, outside addresses, wrong range header, missing/duplicate markers,
wrong initializer pointer/address, missing/duplicate initializer dumps,
changed function size and changed boundary symbol. The first fixture invocation
had an unmatched parenthesis and exited before executing any checks; correcting
that invocation changed no helper source.

During source review, a separate agent identified that the draft accepted
incomplete disassembly. The pre-test repair requires complete contiguous byte
coverage, rejects every unparsed address row, and records validated byte counts.
The repaired helper passed the checks above. Original reader and prior raw
receipts remain unchanged. These fixtures are not native instruction evidence.
