# D230 recorder failure observation preparation

This source-only preparation under D051 is fixed to the D228 recorder attempt
377911abefabd094971ee6d089326604, session3997245574426120340, source702ad99e,
static/default recorder.ino, MATCH0/MOTORS_ALLOWED0. It neither retries delivery
nor authorizes a new upload. Main and all firmware bytes stay unchanged.

There are two bounded steps. First tools/recorder_failure_abi.py observes the
existing build's ELF and DWARF files. Then tools/recorder_failure_capture.py
adapts the reviewed passive MEM-AP Capture lifecycle to the accepted ABI data.
The completed delivery attempt, independent source/host review, exact committed
collector HEAD and check-only must precede any actual file-only action. The
accepted fresh ABI and mechanically derived frozen capture spec must precede
any actual passive action. Root owns these admissions; this preparation creates
no physical acceptance, motor permission or human phase gate.

The historical compile HEAD004dc7cff534896a851901f9d7d0ba6066cae060 remains
distinct from the later reviewed collector HEAD. The inherited recorder source
admission rechecks all144 compile inputs against those historical Git blobs and
the current files and recomputes the109 staged files including the identified
header. The collector independently binds its own source, dependencies, plan
and exact four compile records to its reviewed HEAD. No equality between these
two HEADs is required. Current source drift refuses observation.

File-only observation has exactly four children: installed readelf --version,
gdb --version, readelf -hSWs on this recorder.ino.elf, and guarded offline GDB on
this recorder.ino_debug.elf. Keep -nx/-nh/-batch, auto-load no and
may-call-functions off. Only sizeof/alignof/ptype, null typed member offsets
and enum casts are queried. No attach, target, inferior, function call or
memory examination is allowed. Complete layouts cover Runner, its Report,
Transaction, TransactionReport, Transfer, its Report, UnoQDumpPort and bool.
Every status field has a fresh numeric offset and width; no old dynamic object
size, B4 address or296-byte diagnostic schema supplies a missing answer.

The static runner must lie wholly in the checked bss_zero interval. The
nonzero-initialized native_dump may occupy the checked data_copy destination
or bss_zero; its freshly observed ELF section must match the corresponding
exact current section. Never substitute the larger .bss section for the
initialized interval. Type size/alignment, nonoverlapping objects and windows,
field extents and scalar widths are checked. Enum widths/values and bool width
are exact. Missing/duplicate/reordered/incomplete DWARF answers refuse.

Reuse D209 descriptor readers and strict result/number/layout/symbol parser
primitives; reuse the D188 execute/finally lifecycle with only the fixed scope
label changed. Reuse D173's offline GDB builder and bounded remote file reader.
Twelve remote file identities plus board identity are checked independently at
closure; local source closure follows even on failure. Preserve60s child/5s
reap,1MiB streams,400s transport,8MiB reply,30000 UTF16 command units and128MiB
local free minimum. The absent-only local native_abi01 owner is consumed by
partial output; the absent-only remote scope is never created. No retry,
cleanup, arbitrary profile, generalized query or new transport is introduced.

The capture receives a spec mechanically derived from the accepted ABI bytes
and its SHA256. The caller must pin the canonical spec SHA256 in its reviewed
invocation. It reads only Runner Report, Transfer Report, session,
TransactionReport and native status/cleanup/initialized/attempted/active/poison
fields. Four-byte MEM-AP alignment padding is explicit. Adjacent ranges merge;
each snapshot stays at most16KiB. No full recorder, peripheral or UART register
is read. Two snapshots have the inherited two-second separation. Full263680B
loader and55104B sketch flash comparisons occur before any SRAM and after both
snapshots; any initial mismatch stops before SRAM. All existing descriptor,
identity, file, process, deadline, child/reap, stream and closing guards remain.

The capture implements only profile_bindings, prepare_plan, gather and complete
hooks. Raw bytes, addresses, hashes and per-command receipts survive malformed
scalar values and failures. Invalid bool/enum bytes produce explicit decode
errors and prevent successful collection, while final flash comparisons are
still attempted when reads themselves succeed. Missing/partial snapshots
remain incomplete. Session equality is reported, not required: an early setup
failure may leave session0. Each snapshot remains non-atomic and coherence is
always UNPROVEN, even when every field agrees. Status values are observations;
they do not establish an earlier cause, UART delivery or timing qualification.

Focused serial synthetic tests cover data/BSS containment, overlapping objects,
strict streams/layouts/markers, fixed queries, map extents, raw incomplete
status, invalid values, flash-before-SRAM sequencing, two snapshots and final
flash checks. Their results are host evidence only. The existing frozen
transport/descriptor lifecycle is reused; no native operation is part of tests.
