# D149: file-only comparison of existing static debug information

D148a1d2daae establishes structural/package evidence for D144's unchanged packet.
The next gap is its actual debug type layout. No new compiler or MCU action is
needed. This scope uses the installed, pinned GDB only to read the existing ELF.

After separate glue review and coordinator D051 adoption, execute
`P7_static_link_probe_raw/compare_native_abi.py` once from the exact repo with
Python-B, captured-source hash checked before execution and afterward. Preserve
the fresh exclusive `native_abi/` receipts; no retry after failure/uncertainty.

Reuse the unchanged D143 runner/helper and original D144 Claim/eight FileRecords,
17 local pins,103 sources/102stage,26 installed dependencies including GDB8e709e32.
The current-default ABI command receipt7a3e3fb9 and comparisonfe137985 are pinned.
Retain all230 exact baseline query strings, replacing the historical ELF argument
with D144's existing debug ELF and adding `-iex "set auto-load no"` before the
file argument. The resulting467 arguments use `-nx -nh -batch` and only language/size setup,
echo, sizeof/alignof, ptype and null-base member-offset expressions. There is no
target connection, inferior, function call, shell, script or firmware operation.

The five intended commands are original helper source/artifact/identity inspection,
installed hashes, one file-only GDB invocation, helper inspection, installed hashes.
Run final remote/local checks independently after failure and preserve first error.
Old tested dispatch bounds Windows command size and records full arguments,
stdout/stderr/status; response must be successful, empty stderr and <=1MiB.
Require16 exact unique type names and82 exact unique member names, then compare
every size/alignment/offset with the unchanged current-default baseline. A mismatch
is evidence and a failed comparison, never permission to alter tests or code.

The existing pinned debug ELF has no .debug_gdb_scripts, .gnu_debuglink,
.gnu_debugaltlink or .debug_sup section; no additional debug-file script is
introduced. Object-associated script auto-loading is also explicitly disabled
before file opening, independently of the init-file flags, as documented in the
[official GDB manual](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html).
No installed tool is modified and no file is transferred from board.
Local preflight checks the full historical output parser plus three incomplete/
wrong-key negative outputs; these are script checks, not new board evidence.

A pass establishes these98 queried layout entries only. It cannot establish native
function/device ABI compatibility, reference completeness, live memory, startup,
WCET, runtime acceptance, static adoption or any physical/human gate. Preserve
original dynamic deficit and native structural results separately. No production
code, configuration, frozen contract/oracle or upload path changes.
