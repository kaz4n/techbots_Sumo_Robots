# D147 draft: exact inherited TLS symbol extension

Status: proposed, not implementation or execution authority. D1469ee2d559 binds
the six symbols to installed generated assembly and the actual linked object.
This narrowly extends structural interpretation; it does not change firmware,
production admission or any original D142 contract, implementation or test.

## Pure interface

New module: `state/analysis/P7_static_link_probe_raw/static_native_artifacts.py`.
Public function:

```python
validate_artifacts(artifacts, native_tls_source, frozen_validator_source) -> dict
```

No file, clock, environment, network, subprocess or device I/O. Inputs are
immutable bytes plus the original seven-artifact dict. Do not mutate caller
objects or existing imported modules. Malformed data raises ValueError; wrong
Python argument count follows ordinary Python call semantics. No source-size,
ELF/table/section/package bound from D142 is raised or removed.

`native_tls_source` must be exactly bytes, length1..65536, SHA256
`68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70`.
`frozen_validator_source` must be exactly bytes, length1..32768, SHA256
`d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368`.
Check both types/bounds/hashes before any execution of supplied source. Only
that exact frozen validator may be loaded into a fresh private namespace for
reuse. No dynamic caller code, monkeypatch of an existing module, arbitrary
dependency, file import path or optional legacy fallback is permitted.

The assembly header identifies packaged firmware SHA256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
Byte acceptance is not a live installed-file check: the eventual caller must
separately bind these bytes, current toolchain/source and actual artifacts.

## Only additional symbol interpretation

Retain every D142 rule and check, except its blanket rejection of STT_TLS6 is
replaced for exactly these six names by the following complete symbol tuples.
Each must appear exactly once in each final/debug/temp ELF; none may be absent.

| Name | Value |
|---|---:|
| `_TLS_MODULE_BASE_` | 8 |
| `_rand_next` | 8 |
| `z_tls_current` | 16 |
| `errno` | 20 |
| `_strtok_last` | 24 |
| `_localtime_buf` | 28 |

Every row must have size0, STB_GLOBAL1, STT_TLS6, st_other0 and SHN_ABS65521,
and be on the nonlocal side of sh_info. These values are TLS offsets, not
ordinary RAM addresses. Repeated values for the first two names are intentional.
Reject any changed field, wrong type under a reserved name, shadow/duplicate
definition, missing name or extra/anonymous TLS symbol. All other symbols still
pass through the exact frozen D142 checks, including unsupported bindings/types,
reserved visibility, local partition, undefined nonweak and essential symbols.

No application TLS storage, PT_TLS, SHF_TLS, .tdata/.tbss, new relocation or
section/program form is admitted. Existing D142 allocation, bounds, normalized
three-image equality, entry/copy/zero, exact flat BIN and both ZSK checks remain.
Presence of these inherited constants never establishes their use or runtime ABI.

## Result and isolation

Return the original D142 report fields, with status replaced by the distinct
`STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS`, plus `native_tls` containing exactly:

- `source_sha256`: the fixed assembly hash above;
- `loader_sha256`: the fixed packaged firmware hash above;
- `symbols`: six dictionaries sorted by name, with exactly name/value/size/bind/
  type/other/section and the fully checked tuples above.

This status prevents an unchanged D143 consumer from accepting the extension.
No consumer integration, board collection/validation, retry/rebuild, upload/reset,
native binding/constructor/ABI acceptance, free-RAM/WCET measurement, release tag
or human gate is part of this host-only task. Preserve D144's original failure.

## Independent verification before execution

A separate test author uses this contract, D142 contract and public synthetic
fixture builders, without reading validator implementation bodies. Freeze new
expectations before first execution. Cover all three ELF forms and all six names;
wrong/missing/additional/duplicate fields/names, legacy no-alias input, source
type/size/hash failures, caller immutability, representative D142 structural and
package negatives, permitted diagnostic-only differences, and no change to the
old component's rejection behavior. Keep original D142 tests and fixtures intact.
After implementation, run the new focused tests plus the original component
regressions and separate read-only source/receipt review. No native run follows
merely because host checks pass.
