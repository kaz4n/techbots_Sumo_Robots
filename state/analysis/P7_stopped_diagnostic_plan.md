# Separate stopped-state diagnostic01

D160 run02 is consumed. Its upload and complete flash comparisons succeeded,
but both diagnostic prefixes showed STOPPED/epoch3/initfalse. Source analysis
places the first robot STOP in epoch2, followed by one completed tail epoch.
Empty grants explain initfalse, not STOP by themselves. Nested Robot/MotorGate
faults are missing from those prefixes; their exact offsets are already in D149
native_abi/0003.json (SHA a7c0c4797414e396e19d981b54e104d250cd77a32ac25e221f182e85c9da0994).

One new passive observation may use the existing hash-bound OpenOCD/MEM-AP-only
configuration on ADB2629958581/boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6/UID1000.
No flash, halt, reset, resume, configuration write, service action or new firmware.
read_stopped_remote.py loads only pinned stateless helper/support and original
capture binding bytes, checks board identity and all five installed file pins
before and after, and exclusively owns remote
/home/arduino/sumox26_codex_build/static-stopped-fcddbd8e-run02-diagnostic01.
Local intent/result live in a new stopped_diagnostic01 directory; no reused claim.

One fixed OpenOCD invocation echoes BEFORE/TRANSACTION/INPUT/AFTER/END labels,
reads188 32-bit words (752B) with mdw phys in these ordered windows, then shuts down:
0x2003bc98 count7;0x2003b2b0 count126;0x2003bef0 count48;0x2003bc98 count7.
The pinned configuration initializes only MEM-AP, disables servers and specifies
reset_config none. Fixed env/cwd,30s child deadline/+5s bounded owned-group reap,
1MiB file caps and accepted streams strictly below1MiB. Preserve both raw streams
and any partial/error outcomes. No automatic retry after failure or uncertainty.

The official guide specifies mdw's32-bit units and count:
https://openocd.org/doc/html/General-Commands.html#Memory-access-commands
The versioned MEM-AP source reads physical addresses through read_memory:
https://raw.githubusercontent.com/openocd-org/openocd/v0.12.0/src/target/mem_ap.c
OpenOCD v0.12.0 target.c:1476-1478 assigns read_phys_memory=read_memory for
no-MMU targets, so phys preserves the MEM-AP route (versioned primary source:
https://raw.githubusercontent.com/openocd-org/openocd/v0.12.0/src/target/target.c).
No fresh full flash verification is performed; D160 is inherited provenance.

Only exact ordered labels, addresses and word counts permit interpretation;
reconstruct little-endian bytes and retain them. Compare runtime brackets and
the old runtime/transaction prefix to D160; any change is a changed observation,
not permission to retry. Equal brackets prove only sampled prefix stability,
not atomicity of all nested data or uninterrupted MCU/image continuity.
Robot fault bitmap is Transaction+112(u16), escape fault+114(u8), MotorGate
fault+472(u8), consumed+473; retain unknown bits/values. The full report/input
allow checking current versus previous application receipts and their timing.
No result alone proves whole-robot timing, physical acceptance or a human gate.

Pre-action source review found a close-error/final-check preservation gap; fixed
before any native invocation. Source71507fd8 keeps the first child error and
subprocess flags, catches each close failure and independently attempts identity
and all five file checks afterward. The controlled host substitution receipt
stopped_diagnostic_host_check.json passes these failure checks (zero native calls).
Local admission binds the containing clean HEAD, source/stage, pinned modules and
ADB hash; exclusive intent precedes one60s outer command. Preserve outer errors
and post-local checks independently. A remote COLLECTED label is not parsed-data
success. No automatic retry, reset or change to any consumed startup scope.
