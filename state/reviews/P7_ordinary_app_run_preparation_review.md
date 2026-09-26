# D212 ordinary application run preparation review

2026-09-26. FINAL PREPARATION PASS for corrected proposal02. The sole material
finding is resolved below. This is a separate same-model reviewer using reused
context, not human/cross-model review. Adoption and implementation preparation
may proceed; this review does not admit an upload or MCU observation. D211
actual cleanup, independent source/host closure and fresh native admission
remain required.

Only saved local bytes, strict JSON, AST/source spans, literal in-memory
transformations, hashes and read-only Git were used. No project subject was
imported or executed, no tests or device calls ran, and no new executable was
constructed. Only this review was written. All four prospective subject paths
were absent at the final check.

## Exact proposal and resolved finding

| Reviewed file | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_ordinary_app_run_contract.md | 25120 | `828b334235877131580618908cc164381a988f297c4e22235eb72e34fe200e75` |
| state/analysis/P7_ordinary_app_run_raw/run_derivation01.json | 119497 | `9a8ef9caa96f0e30a8ad741319d5ea59668b8e6066d0c96fb59defd35f896d66` |
| state/analysis/P7_ordinary_app_run_raw/ordinary_scalar_map01.json | 42416 | `d8f4eb7eb36430cff975e3032168fa61f2c249e55596401a67862b272bb08fb7` |

The original proposal classified nested _plan.flash as an exact retained body,
although its95368-byte sketch extent must become92944. That contradicted the
parent _plan metadata adaptation. The author corrected the classification
after review, preserving original proposal bytes at
`c9db52852d177f88ffee70350248f06b1cb83163`. Exact Git/data comparison confirms
only this classification, its correction record, and corresponding contract
counts/identity changed. The map, native recipes, geometry, semantic
requirements and test obligations are unchanged.

The corrected partition accounts for all55 historical decoder functions:
31 exact bodies, nine metadata spans, nine semantic replacements and six
removed diagnostic helpers. Parent _plan and nested flash refer to the same
single extent substitution, not two applications. The nested311-byte result
is independently reproduced as
`372f13c4062a18c88f3b44804268b6939f81ea52bf897f871c8aa5f122b16a65`.
All31 exact body pins match the predecessor. This resolves the finding without
changing a guard, accepting an old extent or weakening an assertion.

## Source, artifact and native composition

All166 input pins independently match current lengths/digests. The12 accepted
provenance entries include actual D208 compile/artifact, D209 ABI and D210 entry
results/local closures and separate actual reviews. The ordinary125-file
manifest matches the accepted packet exactly. Independent data mapping of the
actual105 src entries yields104 staged files/764405 bytes and source digest
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
The accepted ordinary mapper and app_source_hash algorithm agree on selection,
reserved paths, collision/case checks and sorted(mapped,key=Path) ordering.
This is source-only app mapping, not the prior129-file diagnostic projection.
Actual host admission must exercise the pinned mapper and crosscheck rather
than substitute a successful fake.

The fixed raw/package image sizes92928/92944 and their digests agree with
D208; ELF/debug-ELF identities are also current. Exact inherited upload and
capture bindings were reconstructed with only current source/run/owner/image
and sketch-override paths changed. All installed helper/tool pins, directory
sets,14 override-absence paths, loader image and passive capture config remain
unchanged. /tmp/remoteocd absence remains an additional upload prerequisite;
the run contains no cleanup fallback.

The three ordered native recipes reproduce every old-fragment count and final
identity, with unchanged function spans independently checked:

| Prospective subject | Steps | Bytes | SHA256 |
|---|---:|---:|---|
| remote.py | 17 | 11269 | `a2c2fc9d32694a96a406b6de499bfb04a2a159710443c8b37ca56e92921a536f` |
| actions.py | 11 | 12496 | `07c03a65fad73f49064abd0af77161b5ed10e2c6002bb6c442e7ab5b28ee25b1` |
| run.py | 19 | 24859 | `f48a8be9fa380a2a922613d188ae7622eafffdf3dc5fec12edc1372b4f7fc2d2` |

The private caller22977-byte projection matches
`56b7e654537694ffb52b4557f21b369a4ad942cb507a876882bfa587c7899dd3`;
the private actions19129-byte projection matches
`a26d7f7480a13c39d3071de779076ea61feb65253838f37effb9062b550e3202`.
The exact11-role scope and12-member preparation provenance are retained.
Map/decoder/oracle/review/freeze and D211 closure must additionally be pinned
by the coordinator before native admission; the11-role scope alone is not
complete authorization.

Descriptor/ancestry/type/hash checks, isolated Python, exclusive ownership,
durable intent before dispatch, bounded framing, returned-result attribution,
all closing attempts and first-error ordering remain inherited. A durable but
unattributed result remains evidence, never successful action attribution.
Capture follows only successful returned upload; maximum one each. Complete
execution retains13 transports and exact order, including adapter claim/push,
three baseline/capability passes and fixed action counters. Claim still needs
1GiB free and no conflicts. Upload180s plus5s reap,195s local envelope,
capture600s budget/630s envelope and30s read children are unchanged.

Independent data-only reconstruction of the prospective action strings and
standard compression/framing produced upload29662 and capture28722 UTF-16
units including NUL using the existing base85 fallback. Their initial base64
forms are31359/30356 units. Both selected forms fit the unchanged30000 limit;
actual source/host/admission must still measure generated argv. No larger
limit, shell fallback or additional operation is permitted by this result.

## Actual ordinary ABI and finite read plan

Both map objects equal the accepted D209 objects: Runtime at0x20013960,
166376 bytes, and UnoQPort at0x2003c348,40 bytes. All13 layout hashes match.
All107 selected scalar rows independently match the actual ptype line text,
declared scalar/enum type, width and offset, including array element strides.
Field names, unique spans and nonoverlap were checked within every window.
The seven observed enum dictionaries equal all47 accepted numeric answers.

Nested dotted names agree with actual containing structures: TransactionReport
robot begins24, outputs36, applied.feedback424 and halt480; MotorGate halt
begins68; SetupGrants mounting/matrix/dump begin5/11/14. Standalone RobotResult,
Outputs, Result, PreviousTick and HaltResult layouts corroborate those bases.
The source-only RobotFault bits are exactly1 through512 with known mask1023;
they are not observed GDB enum answers. The17 absent grant flags, three zero
mounting axes and zero dump_origin match pinned config/configuredSetupGrants.

| Window | Address | Bytes | Scalars |
|---|---|---:|---:|
| report | 0x2003bc98 | 600 | 10 |
| transaction | 0x2003b2b0 | 504 | 36 |
| previous | 0x2003b4a8 | 48 | 9 |
| gate | 0x20013a28 | 88 | 15 |
| grants | 0x2003bc80 | 21 | 21 |
| attempted_word | 0x2003c2a8 | 4 | 1 |
| motor_port | 0x2003c348 | 40 | 15 |

Each window lies wholly in its observed allocated/startup-initialized object;
the seven extents do not overlap. attempted_ is precisely byte2 of the aligned
four-byte container; bytes0/1/3 remain opaque. No other unselected pointer or
padding is promoted to a field. The21-byte grants read needs no relaxation of
the existing positive-length range guard.

The independently rebuilt ordered plan equals all28 declared rows: loader5,
sketch2, first7, second7, sketch2, loader5. Each flash chunk is at most65536B.
Totals are715858B, including14 SRAM reads/2610B, with107 fields per sample set.
Initial30s wait is immediately before index7;2s gap is before14. Full image
comparison boundaries are4/6/22/27, and snapshots are exactly reads[7:21].
Upload consumes raw92928B; flash comparison uses the92944B package. Completed
wait records, all four comparisons, exact counters/rows and clean closure are
required independently; sleeping or transport return alone cannot prove them.

## Decoder semantics, coverage and limits

The decoder is explicitly a semantic adaptation. Its exact map admission,
public argument types/order, seven kind names and bounded scalar spans are
specified; no diagnostic alias or pointer traversal survives. Raw unsigned
bits and little-endian bytes remain available for every scalar. Noncanonical
bool, unknown enum and nonfinite float values become ordered annotations with
unambiguous numeric/null values; they do not silently become defaults or
abort later valid fields. Negative zero and64-bit integer precision are
preserved. Fresh return containers and whole-window bytes remain required.

Application findings have exact fields and stable read/field ordering. Issue
annotations precede any applicable canonical-value semantics; invalid values
are not double-counted as guessed faults, grants or motor commands. Finding
presence cannot change structural collection status. Repeated-field equality
compares only selected raw scalar bytes, not padding; coherence remains
UNPROVEN even for equal results. No automatic application PASS, first-failure
history, final halt or diagnostic SETTLE/Trace interpretation is introduced.

The retained admission chain preserves strict JSON/duplicate/nonfinite/depth,
size/hash/base64 verification, bool-versus-int receipt typing, exact file/path
sets, wait chronology, flash boundaries, native/closing errors and first
structural-error precedence. All57 admissible attempted/successful prefix
pairs are specified. Failed capture needs its native first error, including
failure after all reads. Missing declared bodies differ from unread tails.
Malformed early results remain raw evidence without fabricated partial schema.

The planned native106 cases comprise91 ancestral behavior methods plus15
explicit ordinary metadata/admission methods. The historical decoder70
methods are completely partitioned into34 retained and36 excluded: the
excluded nested diagnostic/SETTLE/provenance semantics are replaced by12
explicit ordinary obligations, giving46 methods. Applicable rejection paths,
all prefixes, distinct stale negatives, exact ordering, real125-file admission
and explicit inherited Windows skip coverage are preserved. Historical files
are unchanged. Independent fixtures, exact method/assertion selection and
subject identities must be frozen and reviewed before the first eight serial
host suites, each with600s outer bound and isolated temporary owners. These
are required future tests, not results asserted here.

Separate post-attempt retrieval is limited to saved upload/capture results and
the successful SRAM prefix, at most16 files. Only actual returned/durable
pins may fill the fixed EXPECTED/PINS seams; no report hash is predicted.
The unchanged60s read-only template retains helper/descriptor/hash/size checks,
second file pass and before/after board identity. It does not make another
MCU read. Actual result/retrieval/decoded acceptance remains separate.

Ordinary semantics are appropriately limited: begin's return is discarded;
attempted_ is an entry latch; absent grants can coexist with RUNNING, advancing
epochs, incomplete initialization and Robot BOOT. Freshness clears even on
early returns. Transaction reset/publication, PreviousTick copies,64-bit
tokens and counters can be sampled mid-update. FAULT precedes portions of
cleanup; an unattempted/default HaltResult is not proof cleanup failed. Native
low/settled/mask fields are bookkeeping, not measured outputs. Ending host
capture leaves the ordinary loop running and establishes neither a terminal
snapshot nor final inhibition. Linux boot/flash equality does not establish
MCU reset continuity; sampled maxima do not establish WCET. Unselected callee
interiors and physical facts remain outside this evidence.

The original local authoring OS206 refusal and this resolved review finding
remain recorded; no subject/native retry was used to resolve either. Before
one check-only and at most one execute, require adopted scope, D211 actual
closure, source/host acceptance, fresh complete identity/source/artifact/helper/
process/resource/unused-owner checks and clean reviewed committed HEAD, with
all writers held. No cleanup, compiler, configuration change, motor-capable
run or human gate is authorized here. This preparation review is sealed for
the exact corrected identities above; reviewer writes stop after sealing.
