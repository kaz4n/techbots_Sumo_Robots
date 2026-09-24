# D146 local final-ELF TLS-use observations

Read-only analysis on 2026-09-25 Asia/Dubai. This scoped note is the only written
artifact; no disassembly copy, board command, compile or validator change.

Input: `P7_static_link_probe_raw/diagnosis-v1/app.ino.elf`, 170616 bytes,
SHA256 `5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
WSL Ubuntu `/usr/bin/readelf` and `/usr/bin/arm-none-eabi-objdump` both report
GNU Binutils 2.42 (objdump package `2.42-1ubuntu1+23`).

## Actual commands and method

From repository root, PowerShell passed Python through stdin with
`@' ... '@ | wsl -d Ubuntu -- python3 -B -`. Python ran the following commands
using `subprocess.run(argv, capture_output=True, text=True, check=True)`; all
returned zero. Output stayed in memory and only selected lines were printed.

```
readelf -hSWls state/analysis/P7_static_link_probe_raw/diagnosis-v1/app.ino.elf
readelf -sW state/analysis/P7_static_link_probe_raw/diagnosis-v1/app.ino.elf
readelf -lW state/analysis/P7_static_link_probe_raw/diagnosis-v1/app.ino.elf
readelf -rW state/analysis/P7_static_link_probe_raw/diagnosis-v1/app.ino.elf
readelf -x .init_array state/analysis/P7_static_link_probe_raw/diagnosis-v1/app.ino.elf
arm-none-eabi-objdump -d -C state/analysis/P7_static_link_probe_raw/diagnosis-v1/app.ino.elf
```

The symbol search was case-sensitive for
`TLS|__aeabi_read_tp|__tls_get_addr|__real_.*tls|__emutls|_TLS_|tdata|tbss`.
The disassembly label/annotation search was case-insensitive
`<[^>]*(?:tls|read_tp)`. Direct branch/call targets were extracted with:

```python
pattern = r'\t(?:b(?:l|lx|eq|ne|cs|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?(?:\.[nw])?)\s+([0-9a-f]+)(?:\s|$)'
for line in disassembly.splitlines():
    match = re.search(pattern, line)
    if match:
        count += 1
        if (int(match.group(1), 16) & ~1) == 0x08007f30:
            hits.append(line)
```

Raw address searches used `struct.pack('<I', address)` and repeated `bytes.find`
with a one-byte advance, thus including unaligned occurrences. ELF32 little-endian
section headers were decoded with `<IIIIIIIIII` to classify the found file offset;
NOBITS `.bss` has no file bytes and is excluded from file-backed membership.

## Findings

The six observed TLS symbols are all GLOBAL, DEFAULT visibility, ABS, size zero:

| Symbol index | Name | Value |
|---:|---|---:|
| 1557 | `_TLS_MODULE_BASE_` | `0x08` |
| 1598 | `errno` | `0x14` |
| 1615 | `_localtime_buf` | `0x1c` |
| 1872 | `_strtok_last` | `0x18` |
| 1927 | `z_tls_current` | `0x10` |
| 2071 | `_rand_next` | `0x08` |

The sole accessor-named symbol returned by the search is index 1665,
`__real___aeabi_read_tp`, GLOBAL/NOTYPE/DEFAULT/ABS, size zero, value `0x08007f31`.
No `__aeabi_read_tp`, `__tls_get_addr` or `__emutls` function definition appears
under those names. There are zero TLS/accessor-named disassembly annotations.

There are 3342 parsed direct branch/call instructions and zero targets matching
`0x08007f30` after clearing the Thumb bit. Raw little-endian `0x08007f30` occurs
zero times. `0x08007f31` occurs once at file offset `0x1f174`: `.symtab` entry
1665, value field offset +4, not in loaded code/data. `.symtab` starts at
`0x18960`, uses 16-byte entries and is `0x8c20` bytes long.

No section has SHF_TLS (`0x400`), no PT_TLS header exists, and readelf reports no
relocations. The three program headers are two LOADs and GNU_STACK. The LOAD
file ranges are `[0x1010,0x17ad8)` and `[0x18890,0x18960)`.

## Small entry-order observation

ELF entry is Thumb `0x08100011`. Disassembly at `0x08100010` shows three indirect
`printk` calls, `.data` copy and `.bss` zero, preinit then init-array traversal,
then `main`. Preinit is empty; the single init-array word is `0x08100101`, pointing
to `_GLOBAL__sub_I_setup`. `main` at `0x081157a0` calls `initVariant`,
`start_static_threads`, `setup`, then repeats `loop` and `__loopHook`.
The static-thread list's start/end both equal `0x08115970`; the observed
`__loopHook` at `0x081106e4` is `bx lr`. This is a small disassembly observation,
not a completed constructor/native-binding audit.

## Limits

These searches do **not** establish absence of TLS use. Indirect targets,
computed addresses, inlined access sequences and code in the packaged native
loader/libraries remain outside this direct-reference scan. No-relocation output
alone proves nothing about TLS use in a fully linked image. Symbol provenance,
native accessor semantics and thread-pointer/layout compatibility still require
the separate installed-source/object/map investigation. No structural parser
acceptance, runtime correctness, memory fit, upload or physical gate follows.
