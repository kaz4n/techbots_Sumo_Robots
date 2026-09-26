# D223 UART holder observation

One read-only Linux metadata observation on the connected UNO Q. The observer
must not open `/dev/ttyHS1`, read any descriptor payload, change services, send
router RPC, or touch the MCU. Authentication is limited to this exact reviewed
observer; the password is supplied through no-echo stdin and is never saved.

`tools/observe_uart_holders.py` runs with no arguments, isolated Python and no
bytecode, and requires effective UID 0. It emits a bounded JSON receipt. Its
`observe(ops, clock)` function accepts a synthetic metadata provider for host
tests; the command line has no filesystem or command overrides.

Observe boot/kernel, caller credentials/capabilities, the fixed tty character
device (expected major/minor 239:1), and the router's MainPID/start time/executable
identity before and after two scans. Each scan includes every enumerated process
and task FD table, so private thread FD tables are included. Compare process and
task start times plus task/FD name lists around each observation. Read only small
fixed proc metadata files; executable bytes may be read only for the identified
router, with a regular-file and 32 MiB bound. Each actual holder also has its
process name/UID/GID and executable path/stat observed (without reading those
other executable bytes). No cmdline or environment content,
unrelated FD targets, or unrelated file payloads are collected.

Limits: 4096 processes, 8192 tasks per scan, 4096 FDs per task, 65536 FD stats
across both scans, 15 seconds per scan, 5 seconds per fixed systemctl query,
1024 retained error details, 4096 retained holder rows, and 1 MiB serialized
output. Directory enumeration is bounded while iterating. Every error/cap is
counted even if detail storage is full. A host timeout must remain indeterminate
unless child completion is actually observed; no automatic retry is permitted.
Only the observer's own temporary directory handles are excluded from FD names,
after stat proves directory type and exact device/inode equality to the enumerated
FD directory. Those handles cannot be UART holders. These stat operations also
count toward the global FD metadata budget. A 45-second process alarm bounds
stuck metadata calls; absent output/abnormal termination is indeterminate.

Output schema `sumox-uart-holders-v1`: before/after boundary metadata, two sweep
records with counts, holders, problems and completeness, explicit boundary and
holder-set equality, elapsed time, and `visibility` equal to
`SAMPLED_COMPLETE` only when every scan and boundary is complete/stable. Otherwise
visibility is `INCOMPLETE`. Holder absence alone never implies completeness.
`continuous_exclusivity`, `framing_clean`, `receiver_ready` are always `UNKNOWN`.
This observation supplies no UART setup grant, last-close/DMA proof, actual
reopen/delivery proof, motor permission or phase gate.

Tests derive from these requirements: private-thread holders, denied/vanished
tables, reused task/process IDs, changed FD sets, device/router/boot changes,
limits/deadlines, bounded enumeration, non-root refusal, and stable held/open
device results. Source review also checks the read-only operation allowlist.
