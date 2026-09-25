# Dynamic diagnostic capture integration notes

25September2026; implementation mapping, not a native scope or acceptance result.
D173 observes Runner2592B at .bss offset0, BSS2632B/alignment8. The later file-only
deployment_files01 observation proves raw ELF and both ELF-ZSK files are29836B,
with f9460a16/b4416792 hashes. flash_sketch.cfg writes packaged sketch bytes at
0x08100000; loader comparison must use the pinned ELF PT_LOAD image (263680B,
e9322826), not assume the separately packaged .bin is identical.

Reuse capture_remote.py's descriptor ownership, one_read, evidence collection,
deadlines/reap and independent final checks. Preserve its old18-read static profile
and global defaults. Introduce only a closed selected diagnostic profile; no
arbitrary read-address API exposed by the native caller.

Candidate finite sequence:
1. Before private RAM access, compare complete loader/sketch flash references:
   five loader chunks (maximum65536B) and one29836B sketch chunk, six reads.
2. Use the existing runtime_capture.find_bss traversal semantics:8B list at
   0x200017bc, at most three196B nodes, one8B confirming list. Require bounded
   aligned SRAM nodes, no cycle, terminated names, exactly one sketch, consistent
   tail and exactly2632B BSS. Require BSS base alignment8 in addition to the reused
   traversal's four-byte SRAM alignment. Preserve actual list/node raw reads and metadata.
3. Read2592B at BSS+0, preserve bytes; wait the existing bounded two-second gap;
   read a second2592B snapshot at the same address. Decode only after retaining
   both raw snapshots, including when later decoding or identity checks fail.
4. Repeat and compare complete relocation evidence, then complete loader/sketch
   flash comparison again. Reject changed relocation or flash; matching samples
   still do not prove atomicity or continuous identity between reads.

With N=1..3 unchanged nodes in each traversal, exact successful totals are
18+2N reads and592248+392N requested bytes: maximum24reads/593424B. Count failed
launches against the same command/byte ceiling. Every individual RAM read is
<=2592B; flash reads are <=65536B. The existing30s child and600s sequence bounds
remain. Confirm final implementation against actual order and test boundary cases;
this arithmetic does not authorize a collector that has not been reviewed/tested.

The static collector's current checked_bindings, fixed plan/admit, gather,
check_analysis and finalize counts must select their profile consistently.
Attempt/result source and schemas must follow that same selection. Existing
FILE_NAMES can remain openocd/config/swj/loader/sketch with diagnostic sketch path
and size. The offline decoder needs no board-side file import: retain/copy bounded
raw snapshots first and run tools/motor_fault_decode.py locally afterward.

runtime_capture.py's whole collect entry is pinned to an old runtimeDiagnostics
symbol and heap inspection; do not invoke it unchanged. Its find_bss function is
the reusable traversal. A thin adapter to the existing one_read primitive can
provide read(name,address,size), record verified flash state, and retain the
extension result without copying the traversal or rebinding module globals.
The eventual bootstrap must pin exact source of every reused primitive.

D175 upload profile is implemented/tested/reviewed (67eccbc5, review1317cc4f).
D176 precise capture contract is P7_motor_fault_capture_contract.md; implementation
and independent tests are in progress. After that, bind current tools/artifacts/
identity and source inputs in a fresh caller, then record one identified inert run. ExistingD172/D173
and legacy static scopes are consumed. No further hardware is requested now.

Native caller source map for the next bounded task (no caller implementation yet):
startup_run.py:60 bootstrap supports only historical static runs and bundles a
static decoder; :234 validator requires18reads/713656B. :411 load_probe and :448
prepare_commands verify the historical static artifact/staging packet, not the
D172 diagnostic. Never call that NativeRun unchanged for this build. Its checked
payload construction, transport ownership, conditional-upload/capture sequencing
and independent final checks are useful existing machinery to extend minimally.
Old run01/run02 source pins/scopes stay consumed, not repinned. Loader parser on
board is18880B/885c4e42; full runtime_capture module also imports p0_capture and
recorder_heap. A future bundle must account for those real dependencies, verify
all bytes before execution, and test its actual Windows command-size bound.
Do not silently substitute the old runtime decoder or heap collector. Upload
input remains raw ELF; capture reference remains its packaged ELF-ZSK sibling.
