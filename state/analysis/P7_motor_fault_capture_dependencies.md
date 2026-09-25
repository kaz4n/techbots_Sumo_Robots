# Diagnostic capture dependencies after D172

Read-only explorer mapping,25Sep2026; no native operation or source change.
First accept/review the active compile, then obtain one bounded file-only
artifact/ABI observation. Do not upload or assume the old static layout fits.

The diagnostic is anonymous-namespace `diagnostic` at motor_fault.ino:10.
motor_fault.h defines Runner containing trace_.report_ and report_ (lines81/84):
64 Call records plus current/first_failure, and four motors::Result slots.
This is source structure only. Actual symbol, section, extent, sizeof/alignment
and member offsets must come from the exact final/debug ELF. Results include
PreviousTick's64-bit token; do not infer packing from desktop sizes.

Collect final ELF class/endian/machine/type; diagnostic OBJECT binding, section,
relative offset and size; matching debug sizes/offsets for Runner, Trace,
TraceReport, Call, Report, motors::Result, HaltResult and PreviousTick. Bind exact
artifact/source hashes and installed readelf/GDB tools, using file-only queries.
Also verify the dynamic motor_fault.ino upload recipe and installed loader ABI.

Reusable existing surfaces:
- P7_static_startup_raw/upload_remote.py:447 upload_loader has bounded child,
  exclusive ownership and independent final checks. Admission:61/:118 is only
  old static fcddbd8e run01/run02. Retain upload's2303728B loader-copy allowance.
- P7_static_startup_raw/capture_remote.py:524 collect has durable bounded read
  receipts, but its exact18-read/713656B static plan is not this diagnostic.
- tools/runtime_capture.py:393 find_bss supplies bounded <=3-node LLEXT traversal,
  cycles/unique-sketch/BSS-size checks and list confirmation. Its collector still
  requires historical GLOBAL runtimeDiagnostics/232B; do not invoke it directly.

Only matching loader bytes/ABI justify reusing list0x200017bc,196-byte nodes,
BSS base offset32/size offset92. After ABI evidence, prefer two whole-Runner
snapshots if size fits the bound, bracketed by exact flash and relocation checks.
Compute finite read/byte totals from the accepted artifact; no heap dump needed.
Add one closed profile to existing upload/capture primitives, not copied wrappers.
Derive independent decoder/control tests before any separately identified run.

Interpretation: begin sets RUNNING only after native setup returns
(motor_fault.cpp:125). A blocked callback can leave NOT_STARTED with current
in-progress; cleanup can also stop before terminal phase assignment(:144).
Trace::finish retains first false before its trailing clock(:59). Preserve these
incomplete observations; two passive snapshots do not establish atomicity or
the original D160 fault cause. No new motor-capable permission or gate follows.
