# D215 actual B4 file-only ABI review

FINAL PASS, 2026-09-26. The single admitted file-only attempt produced consistent
current B4 ABI observations. Independent same-model review with reused project
context; no reviewer subject imports, test executions, new queries or device
calls. All conclusions below concern saved file evidence. The separate
b4_next_scope reviewer independently checked the eight added type layouts,
source declarations, recorder capacities and nested stand geometry read-only.

## Provenance and closure

Native reviewed HEAD is a68ab59e70e496c3b48764571f7f46bc1fee5a44.
Check-only returned0 in0.5268268 seconds; execute returned0 in2.7248692 seconds.
Exactly one transport ran four file children. All children returned0, were
reaped, did not time out and had empty stderr. Thirteen remote closing rows
(twelve files plus identity), independent local closure and all three outer
closing checks passed; first_error is null throughout. No retry occurred.

I independently checked all166 prerequisite files against both current bytes
and their exact native-HEAD Git blobs, all145 native local pins, eight native
saved-file identities, raw/base64 outer and child streams, transported program
and ordered commands. The accepted153-file coordinator and14-role scope remain
bound by that evidence. The command has6981 UTF-16 units including NUL. The
actual24363-byte transported program hashes to
d0c4f1233e1de6b00d64688f92c1d12ae0b7333ab4638dda9f6f677c1731e5b0,
matching preparation, saved inputs and scope. Literal AST inspection recovered
the exact ordered pins and commands without executing the program. Fixed
readelf/GDB commands retain -nx/-nh/-batch, disabled auto-load and inferior
calls, all313 planned expressions,60-second child bounds/five-second reap,
1MiB streams,400-second transport and8MiB reply. Embedded identity reports the
expected boot, arduino/UID1000, no conflicts and13871202304 free bytes.

Key evidence under state/analysis/P7_b4_app_compile_raw:

| File | Bytes | SHA256 |
|---|---:|---|
| abi_native_invocations01.json | 3788 | d14b9f61df657d7c82a2abcb91880b269e3d63128cda12bec5dca163618c697e |
| native_abi_static01/inputs.json | 38209 | 1715c6302cd5605eec32a947b9c5422209bce7afbacb60a725600b2c1dd9d27b |
| native_abi_static01/result.json | 597470 | ac0f379ad7da6d02d9cce4f1035405f48fd4f9fcf19de4bb7bcec7f31cf8f69a |
| native_abi_static01/abi.json | 293222 | 25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc |
| native_abi_static01/local_result.json | 275 | 7175682488de957b36582fc3b030554ac3cfb8a83ea6ab10ffde6fa2a8534729 |
| abi_native_closing02.json | 6509 | c505a725316584594f2db23dc9cb62875102bc8f403d6d20332d1bbb80ad7949 |

## Actual answer reconciliation

All156 ordered markers match the sealed query. Every21 retained layout block
is byte-identical to its raw GDB block. All135 numeric answers reconcile:
42 sizes/alignments,seven window offsets,two suboffsets,eleven member extents
and73 enum values. Profile and capacity dictionaries equal the normative plan.
All2037 ELF symbol entries have contiguous indices0..2036. The selected
Runtime and motor_port symbols are unique LOCAL OBJECTs in section5 and match
observed sizes/addresses; both fit the accepted initialized-BSS interval.

Runtime is166456 bytes/alignment8 at0x20013960; motor_port is40 bytes/alignment4
at0x2003c398, exactly after Runtime. Seven windows have correct derived
addresses, alignment, containment and no overlap. Their Runtime offsets are:
gate200,recorder2984,transaction report162184,previous162712,grants164720,
runtime report164744 and attempted166298. These are current B4 answers, not
reused ordinary addresses or inferred runtime content.

The recorder is159200 bytes/alignment8 and occupies [2984,162184), immediately
before the transaction report. Added observed sizes/alignments are:
stand Report16/4,AttemptSummary96/8,FrameBuffer126300/4,EventBuffer32780/4,
TickStatistics24/8,FrameBytes25/1 andEventBytes8/1. Arrays are125025 payload
bytes,1251 packed-status bytes and32768 event bytes. All three queried indices
are4 bytes and five queried enum widths are1. Thus capacities5001 frames and
4096 events match the declared layout; component sums fit observed parents.
These are capacity and structure facts, not recorder occupancy or loss results.

The fresh TransactionReport is528 bytes and its direct RobotResult container
is [24,448), size424. Stand report [24,40) and stopping bool [40,41) are contained,
aligned and disjoint; addresses are537113344 and537113360. The complementary
review checked their raw member rows and current source declarations, along
with all eight added type layouts. No source/layout mismatch was found.

Root preserved closure01 (5846 bytes/fc2cc848b362e7f18c2a20281bef05ead8667aa9c45d3afb020a318909e2e3a5)
and corrected only symbol inventory accounting in closure02: its initial
size-column regex omitted Runtime index8 because its size is printed0x28a38.
The corrected count2037 matches the independent full-index audit. The earlier
local closing-order audit refusal and reviewer command-slice/symbol-whitespace
extraction corrections were data-only; raw evidence, actual ABI, sources,
fixtures and the single native execution were unchanged. No finding remains.

Acceptance is limited to this fixed D214 M0/B4 artifact's observed file ABI.
All raw layouts remain retained for a separately checked scalar/array decoder
map. This does not observe MCU memory, initialization, stand execution,
recorder state/completeness, snapshot coherence, live free RAM, WCET or physical
inhibition. No compile, upload, reset, motor run or human gate followed; the
existing flashed firmware was not changed by this file-only operation.
