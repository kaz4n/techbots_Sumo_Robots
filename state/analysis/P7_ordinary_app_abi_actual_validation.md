# Ordinary application actual file-only ABI evidence

D209 completed one file-only observation at clean reviewed HEAD
`326931f49fb0512372a8638958acd8093754e227`, after source/host reviewf3e72aca
and admission reviewbd83b5ce. Check-only returned0 in0.540seconds; execute
returned0 in2.187seconds, with6001 UTF-16 command units against30000.
The local attempt spans16:42:22.462917-16:42:24.176394 Dubai on26September2026.
One transport ran four file tools, all return0/reapedtrue/no timeout/empty
stderr. All13 remote closing checks and localclosure passed; firsterrornull.
No compiler, upload, reset, MCU read or privileged operation occurred.
D207 remains the latest verified flashed image. Independent actual review
9627B/585be669 is FINAL PASS and accepted. No downstream instruction binding
has yet been adopted.

## Fresh observed layout

| Object | Address | Bytes | Alignment |
|---|---:|---:|---:|
| motor_port | 0x2003c348 | 40 | 4 |
| runtime | 0x20013960 | 166376 | 8 |

Both unique LOCAL OBJECT DEFAULT symbols lie in initialized zero-BSS section5.
Runtime ends exactly at motor_port start; the objects do not overlap.
There are13 complete type-layout groups, six Runtime windows and47 source-
matched enum answers:185 requested expressions,92 ordered unique markers
and79 numeric answers. The complete symbol table contains2234 rows, numbered
0 through2233 without filtering. No diagnostic Runner or SETTLE-report
coordinates were reused. Full raw layouts are retained in the summary.

| Runtime member | Offset | Bytes |
|---|---:|---:|
| attempted_ | 166218 | 1 |
| grants_ | 164640 | 21 |
| report_ | 164664 | 600 |
| transaction_.gate_ | 200 | 88 |
| transaction_.previous_ | 162632 | 48 |
| transaction_.report_ | 162128 | 504 |

## Saved evidence and closure

Paths below are relative to P7_ordinary_app_static_compile_raw/native_abi_static01.

| File | Bytes | SHA256 |
|---|---:|---|
| inputs.json | 28377 | 3ab0a217e49ffe1508d60f2f8c871eff010dad124c1dc2fdcc27741b32cc6105 |
| result.json | 581671 | 6a17c12cb24396bf9a58a883ea295ec51feff2abe68d826983f363b3bcbb6d3b |
| abi.json | 274942 | e224750ea11a9bd462c1708e2d797b622e9fee56e3e46e479242bff19eefdbf4 |
| local_result.json | 275 | 9c78721cfaa7330cc523619c31ad207832ffe6f9ca3abcc9e93bec7743212cf0 |

Root closure abi_native_closing01.json4273B/c8501453 checks159 coordinator,
10scope and133 runtime-local pins unchanged, all command/stream identities,
13 ordered remote checks and all79 numeric answers against the summary.
It inventories eight native evidence files/1475298logical bytes. C: free
space was6489399296B; no reclaimed-space attribution or manual deletion.
The first read-only local audit stopped before writing on an assumed
elapsed_seconds key; actual records expose started/finished, whose difference
is now used. No subject, fixture, result, guard or native call was changed
or rerun. This audit correction is recorded in the closing receipt.

## Evidence limits

This establishes file layouts and symbol presence only. It does not establish
ordinary loading, live values, coherent snapshots, runtime timing, live RAM,
physical acceptance, motor permission or a phase gate. Ordinary Runtime and
transaction reports update continuously; FAULT may precede completed cleanup.
Native motor bookkeeping is not a pin measurement. All absent setup grants
remain absent. Fresh selected instruction observation is the next separate
task; its ranges must be derived from this accepted complete symbol inventory.

Accepted 2026-09-26T16:48:18.143956+04:00. The review independently reconciles all162 distinct current/native-commit input pins and the exact17529-byte transported program. The file-only owner is consumed; do not rerun it.
