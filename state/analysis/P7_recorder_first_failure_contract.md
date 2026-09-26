D233 fresh-image projection: the historical compile HEAD is
ce4e69390d21d9a91231581a186be4a63213135e; source is
29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9.
Attempt 07f19e32c483cebadecaa63f4d6d720f / session 572412568535289530
uses 145 exact inputs and 110 staged files. The package is 55376 bytes, SHA256
b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584.
The separate collector HEAD is pinned after preparation and review. Execute
from the isolated sumox-recorder-fresh-diagnosis-20260927 worktree; MAIN stays
frozen. No native action before the current recorder run closes and root admits
this diagnostic. A passed compile does not establish the loaded image.

Only fixed identity/artifact/path/inventory data and layout projections differ
from D230. One fresh FailureRecord window adds reason, site, cleanup,
cleanup_ownership, packet_offset, packet_size, payload_size and
ownership_evaluated. The new FailureSite and CleanupDisposition enums use exact
D231 declarations. Query every type, enum, offset and extent from this image;
reuse no D228 addresses or observed values. First-failure data remains raw and
non-atomic with coherence UNPROVEN. Packet progress is not acknowledged payload;
NOT_ATTEMPTED and ownership_evaluated=false must not imply attempted cleanup.
Full flash checks still precede all SRAM and close afterward. No cause is
inferred before observation. Existing lifecycle, transport, descriptor, owner,
source comparison, budgets and strict invalid-bool/enum behavior are unchanged.

# D233 recorder failure observation preparation

This source-only preparation under D051 is fixed to the D233 recorder attempt
07f19e32c483cebadecaa63f4d6d720f, session572412568535289530, source29cb1e76,
static/default recorder.ino, MATCH0/MOTORS_ALLOWED0. It neither retries delivery
nor authorizes a new upload. Main and all firmware bytes stay unchanged.

There are two bounded steps. First tools/recorder_first_failure_abi.py observes the
existing build's ELF and DWARF files. Then tools/recorder_first_failure_capture.py
adapts the reviewed passive MEM-AP Capture lifecycle to the accepted ABI data.
The completed delivery attempt, independent source/host review, exact committed
collector HEAD and check-only must precede any actual file-only action. The
accepted fresh ABI and mechanically derived frozen capture spec must precede
any actual passive action. Root owns these admissions; this preparation creates
no physical acceptance, motor permission or human phase gate.

The historical compile HEADce4e69390d21d9a91231581a186be4a63213135e remains
distinct from the later reviewed collector HEAD. The inherited recorder source
admission rechecks all145 compile inputs against those historical Git blobs and
the current files and recomputes the110 staged files including the identified
header. The collector independently binds its own source, dependencies, plan
and exact four compile records to its reviewed HEAD. No equality between these
two HEADs is required. Current source drift refuses observation.

File-only observation has exactly four children: installed readelf --version,
gdb --version, readelf -hSWs on this recorder.ino.elf, and guarded offline GDB on
this recorder.ino_debug.elf. Keep -nx/-nh/-batch, auto-load no and
may-call-functions off. Only sizeof/alignof/ptype, null typed member offsets
and enum casts are queried. No attach, target, inferior, function call or
memory examination is allowed. Complete layouts cover Runner, its Report,
Transaction, TransactionReport, Transfer, its Report, UnoQDumpPort, bool and FailureRecord.
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
fields plus the eight first_failure fields. Four-byte MEM-AP alignment padding is explicit. Adjacent ranges merge;
each snapshot stays at most16KiB. No full recorder, peripheral or UART register
is read. Two snapshots have the inherited two-second separation. Full263680B
loader and55376B sketch flash comparisons occur before any SRAM and after both
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

Focused serial synthetic tests cover the new field/query/enum inventory,
strict extents, invalid bool and enum bytes, fixed complete flash plans and
exact reverse projection to the reviewed D230 tools. Real file-only owner
composition checks all145 historical inputs and110 staged files, without any
transport. Existing descriptor/lifecycle tests remain the accepted D230
evidence; no native operation is part of these tests.

Concrete root sequence after the D233 run closes and this source review passes:
from the isolated worktree, set H to its clean `git rev-parse HEAD`, run
`python -B tools/recorder_first_failure_abi.py --check-only --reviewed-head H`,
then once `python -B tools/recorder_first_failure_abi.py --execute --reviewed-head H`.
The fresh local owner is P7_recorder_first_failure_raw/native_abi01; the remote
file-only scope is recorder-07f19e32c483ceba-failure-abi01. Preserve all results
and closing checks. After root accepts the fresh ABI, use its exact abi.json
SHA256 with the caller contract's --prepare-bindings command. Commit the actual
ABI evidence and three mechanical bindings in this isolated tree, then use its
new clean collector HEAD for the caller's --check-only and single --execute.
No source changes or second source-review chain are needed for those mechanical
bindings; any material source change requires review. Failure consumes each
native owner. No reset, upload, UART operation, register write or cleanup occurs.
