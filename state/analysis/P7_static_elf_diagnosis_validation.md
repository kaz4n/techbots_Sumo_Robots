# D145 rejected static ELF diagnosis

25 September 2026, Asia/Dubai. **DIAGNOSTIC_ELF_COLLECTED; symbol rejection
identified.** This is a read-only follow-up to the terminal D144 negative result,
not a repaired build or structural, runtime, physical or gate acceptance.

## Actual collection

Coordinator authorization is committed in `0e41849f`. The literal Python block
in the reviewed plan, SHA256
`5f52f30631fe07d5ecaa0105e46f1b08293421f2d9ae4e10380232e72fed8de9`,
ran with Windows Python `-B` after checking that exact plan hash. Unchanged
runner `983e86d7` and helper `8ba9b190` made exactly one checked read through
the pinned ADB executable to serial2629958581. Its receipt records
21:42:40.889915–21:42:41.210259 UTC, exit0, empty stderr. Query and compile
counts are zero. Local pin/stage/runner postchecks reported no errors.

The returned final ELF is170616 bytes, SHA256
`5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
Its complete FileRecord and retained boot/directory Claim match D144. Evidence
is in [diagnosis-v1](P7_static_link_probe_raw/diagnosis-v1/result.json), with the
single original command receipt and input hashes beside it. No upload, reset,
MCU start, remote mutation, retry or compiler action occurred.

## Observed failure cause

The local diagnostic [inspect_symbols.py](P7_static_link_probe_raw/diagnosis-v1/inspect_symbols.py)
checks the exact ELF hash, enumerates its ELF32 symbol records using `struct`,
and captures `wsl -d Ubuntu -- readelf -hSWlrs <ELF>` (GNU Binutils2.42).
It exited0. Retained `symbols.json` and `readelf.txt` agree:2242 symbols,
six outside D142's explicit type0–4 allowlist. All six have GLOBAL binding1,
TLS type6, default visibility0, absolute section65521 and size0:

| Symbol | Value |
|---|---|
| `_TLS_MODULE_BASE_` | `0x8` |
| `errno` | `0x14` |
| `_localtime_buf` | `0x1c` |
| `_strtok_last` | `0x18` |
| `z_tls_current` | `0x10` |
| `_rand_next` | `0x8` |

The final ELF has no PT_TLS segment, SHF_TLS section or relocation records.
Those observations alone cannot establish absence of resolved TLS accesses or
correct native thread ABI. The immutable D142 validator correctly rejects this
unadmitted encoding under its current contract. No parser, contract, oracle,
production policy or firmware change was made. D144 remains rejected.

An initial shell-only filtered `readelf` display failed because PowerShell
removed awk's `$4`; the later direct PowerShell filter and retained independent
struct/readelf diagnostic succeeded. This was display-command quoting, not a
test, compiler or artifact failure. No data were altered to obtain the result.

## Next evidence and boundaries

Read the separate [primary-source diagnosis](P7_static_tls_sources.md).
Exact installed TLS-symbol assembly/input-object provenance and actual use
remain to be bound before proposing any narrow admission amendment. The
current final ELF must remain available as original negative evidence; no
rebuild is needed to investigate it. Entry, constructor, native-binding and
ABI audit remain pending even if structural compatibility is later resolved.

Storage retention is intentional: this one checked ELF, its original read
receipt and compact diagnostic output replace neither the old negative result
nor existing evidence. No duplicate checkout, target build tree or bytecode
was created. Do not repeat the consumed D145 read.

## Separate review and final disposition

Fresh-context same-model read-only review PASS, no new BLOCKER/MAJOR/MINOR:
[review](../reviews/P7_static_elf_diagnosis_result_review.md), SHA256
`a22deffcfa341ff519e93ffefd93fd68a791c7465fe6c0d3055fc9e70fb87cf2`. It independently verified the original receipt bytes, one
read argv,17 input pins,103 source/102 stage records, all25 original D144
receipt hashes and negative result, frozen validator/contracts/oracles, and
2242symbols/sixTLS entries. Fresh local readelf output exactly matches the
retained diagnostic output. This is scoped evidence review, not a human gate
or native/runtime acceptance. No additional tests or board commands were run.
