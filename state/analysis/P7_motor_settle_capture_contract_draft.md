# Draft: one inhibited SETTLE fault-localization capture

26 September 2026. Preparatory draft only. This document defines a concrete
candidate scope for a fresh, single inhibited upload and conditional passive
capture of the existing D198 image. It is not an adopted native run scope and
reports no new MCU observation. Actual D199 entry result/summary/closure and
instruction review are PENDING; their hashes are intentionally absent.
No entry success, publication semantics, fresh owner absence or scratch cleanup
success is assumed. Existing accepted compile and ABI evidence can support
independent preparation while those prerequisites finish.

The only files prepared here are this draft and
`state/analysis/P7_motor_settle_run_raw/capture_binding_draft01.json`:
21880 bytes, SHA256
`483cd66ff7825bff65a7b08f8ced7d4ddecf6586a419c95b19b8edfa581bd7e5`.
The binding records exact existing inputs, candidate ordered substitutions,
current window/type evidence and explicit null pending entry receipts. It is
not a callable script, runtime binding or permission to execute a native action.

## Fixed current image and evidence

The image remains static/default startup, MATCH0, MOTORS_ALLOWED0 and
SUMOX_MOTOR_FAULT_PROBE1. Preserve the compiled app_motor_observe sketch and
all configured grants, firmware limits and native source bytes. This task
adds no software repair and does not raise the150us/4096poll SETTLE limits.
The proposed RUN_ID is `app-motor-settle-117cc0e7-run01` and source SHA256 is
`117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`.
Board serial remains2629958581; expected boot is
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 with the existing full UID/GID1000 identity.
Fresh observation must establish those facts again before any attempt.

| Accepted input | Bytes | SHA256 |
|---|---:|---|
| tools/compile_motor_settle_probe.py | 7570 | b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62 |
| state/analysis/P7_motor_settle_compile_raw/inputs_static.json | 13432 | aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/result.json | 1608 | 9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json | 9648 | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/result.json | 905572 | 230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/abi.json | 5410 | 069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/local_result.json | 275 | eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9 |
| state/reviews/P7_motor_settle_compile_actual_review.md | 8475 | f046db4709a339df345b2e2214da0a946cee4ecebe00b05d80266abe8bb2f624 |
| state/reviews/P7_motor_settle_abi_actual_review.md | 7312 | a7c3993ab5e0d008b4464bf93f89b5877447992fa8e3197d8c869812e11f874f |

The manifest has129 exact source inputs, schema
app-motor-settle-static-inputs-v1. Source inventory and mapping must continue
through the checked D198 compile launcher's private load_caller(root=ROOT),
using its unchanged CompileDiagnostic seams. Never invoke its main, claim,
compile or build methods. The new HAL header is included by the actual manifest;
no source set is inferred from historical128-input metadata.

Keep build owner
`/home/arduino/sumox26_codex_build/app-motor-settle-static01/build` and sketch
source `/home/arduino/sumox26_codex_build/<exact source>/app_motor_observe`.
The sketch basename does not change to motor_settle.

| Artifact role | Bytes | SHA256 |
|---|---:|---|
| raw app_motor_observe.ino.bin | 95504 | d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc |
| packaged app_motor_observe.ino.bin-zsk.bin | 95520 | e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 |
| installed loader ELF | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| checked loader flash image | 263680 | e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2 |

The image and ABI are file observations. Neither proves publication semantics,
an emitted function's runtime success, electrical behavior or timing bounds.
The pinned entry review must establish stores to the observed object and
first-failure preservation before this capture can be admitted.

## Six exact current windows and unchanged sequencing

The D199 ABI observes these candidate windows. Only the fifth historical live
PreviousTick tuple is replaced; all other windows retain their actual current
addresses and widths. No source- or host-layout assumption supplies an address.

| Index within each sample | Name | Address decimal | Address hex | Bytes | Current ABI type |
|---:|---|---:|---:|---:|---|
| 0 | trace | 536951180 | 0x2001398c | 2128 | motor_fault::TraceReport |
| 1 | report | 537119696 | 0x2003cbd0 | 1168 | app_motor_observe::Report |
| 2 | runtime | 537117984 | 0x2003c520 | 600 | app::RuntimeReport |
| 3 | transaction | 537115448 | 0x2003bb38 | 504 | app::TransactionReport |
| 4 | settle | 537121768 | 0x2003d3e8 | 28 | motors::SettleProbeReport |
| 5 | gate | 536953520 | 0x200142b0 | 88 | motors::MotorGate |

The separate SETTLE object is
`_ZN6motors12_GLOBAL__N_119settle_probe_reportE`, LOCAL OBJECT DEFAULT section5,
size28/alignment4 at0x2003d3e8, ending0x2003d404 inside the checked
zero-BSS interval[0x20013960,0x2003d408). It does not overlap Runner.

Omit only the live post-abort PreviousTick window at537115952 (48 bytes).
Keep Report.before_abort.previous at537120816 (48 bytes), offset1120 inside
the1168-byte Report (Snapshot starts16; its previous member starts1104).
Transaction::fail clears live applied_valid/duration_valid, while the copied
pre-abort record preserves its earlier values. These snapshots are neither
redundant nor equivalent. Keep the entire final Runtime, Transaction and
MotorGate windows, including their halt/timing/fault information.

The six windows total4516 bytes per sample. Loader flash still needs five chunks
[65536,65536,65536,65536,1536] from0x08000000. The actual95520-byte package needs
two chunks[65536,29984] from0x08100000. Therefore:

`2 * (263680 + 95520 + 4516) = 727432` requested bytes.

Retain exactly26 one-shot reads,12 SRAM files and this original order:

| Read indices | Purpose |
|---|---|
| 0..4 | before.loader chunks |
| 5..6 | before.sketch chunks |
| before7 | one recorded30-second pre-sample wait |
| 7..12 | first trace/report/runtime/transaction/settle/gate |
| before13 | one recorded2-second separation wait |
| 13..18 | second trace/report/runtime/transaction/settle/gate |
| 19..20 | after.sketch chunks |
| 21..25 | after.loader chunks |

Keep flash comparison boundaries4,6,20,25 against whole checked references.
Keep analysis.pre_sample_wait, report.wait, exact timestamp/type/order checks,
counts, snapshot list, partial reads and coherence=UNPROVEN. Preserve first
error even when a subsequent wait, clock, postcheck or close also fails.
Neither the30-second wait nor repeated identical bytes establishes progress,
FROZEN state, atomicity, completed history or an acceptable WCET.

## Proposed metadata-only remote, actions and caller derivatives

Use new files beneath `state/analysis/P7_motor_settle_run_raw/`: remote.py,
actions.py and run.py. Preserve every historical D195/D190 source, receipt and
consumed owner. The exact original files are:

| Source | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_run_raw/remote.py | 11357 | 98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db |
| state/analysis/P7_app_motor_observe_run_raw/actions.py | 12515 | 6a730069e2511306459f5c3443976a84351b155fd04660a094606cfd98f2829f |
| state/analysis/P7_app_motor_observe_run_raw/run.py | 24944 | 95cc5cb695c8d9bbee85a2105aca46d7c371c1a3bec3c5e3a36ea8fb4dbd1471 |

The binding's metadata_derivatives tables define exact ordered old/new literal
bytes and occurrence counts. They were applied only as data in memory and AST
parsed; no derived source file was written, imported or executed. Candidate
outputs are deterministic under those tables:

| Candidate file | Substitutions | Bytes | SHA256 |
|---|---:|---:|---|
| remote.py | 11 | 11343 | 577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0 |
| actions.py | 9 | 12507 | 8918231c9c2aaf1b72120539e1677db73ce9103798fa860e9fa2501ac669092a |
| run.py | 17 | 24885 | fe2b4d644edbc6096fe1956f4aa8fe801eed4d125ab19ea31eef86ca70469de4 |

These hashes are proposed derivative identities, not frozen implementation or
host acceptance. Retain the exact sketch name app_motor_observe and its C++
namespace. Retarget only run/schema/owner/module labels, source/artifact pins,
manifest/reader paths, test/contract/review paths and the new observation tuple.
In particular, do not globally replace app_motor_observe inside sketch paths.

Remote's11 transformations replace the full source hash and run ID once, the
remaining app-motor-observe hyphenated prefix8 times, private module prefix once,
class AppMotorObserveCapture twice, raw size/hash once each, package size twice
and hash once, previous tuple once, and total727152 with727432 once. The new
factory class is AppMotorSettleCapture. Every method body and condition remains
unchanged apart from this fixed metadata/window/count delta, including the
existing30-second pre_sample_pause and2-second pause.

Actions'9 transformations change full source and run ID once, remaining schema
prefix4 times, private module prefix once, exact new adapter hash/length once
each, package extent once, previous tuple once and total once. Its frozen
candidate staged adapter is11343 bytes SHA256
577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0.
It keeps the11 envelope fields, strict canonical payload/result checks,
returned-only success, all wait validation, no success from durable_unattributed
fallback,65536-byte reply,196608-byte decoded payload and30000UTF16 command bound.
The actual composed command bound remains a required controlled check; no
command-size result is inferred from source length.

Caller uses17 count-checked substitutions. It changes fixed source/run once;
P7_app_motor_observe path prefix7 times; test_app_motor_observe names3 times;
remaining hyphenated schema/owner prefix6 times; native_abi_static02 to
native_abi_static01 eight times; abi02_actual_review to abi_actual_review once;
launcher path twice and its exact SHA once; actual manifest SHA once;
manifest count128 to129 once; D193 diagnostic labels twice toD198 and ABI02 label
once toABI; raw and package lengths/hashes once each. Detailed literal spellings
are in the binding. Source inventory remains through the projected launcher.

Caller retains InertRun(reviewed_head,*,root=None), exact check-only/execute
CLI, immutable commands, canonical upload/capture bindings comparison,
prepare/claim/stage/action/finish order, seven allowlisted labels and13 complete
transports:2 staging,1 upload,1 capture and3 observations of each of three
prerequisite groups. Durable staging intent precedes claim/push; verified claim
precedes push. Upload195s/capture630s/prerequisite60s and remote180s/600s budgets
remain unchanged. A failed/uncertain owner is consumed. No retry, manual source
option, compiler, extra reset, extra SRAM read or automatic deletion is added.

Keep original dependency bytes and load/validation behavior: static_remote.py
33321B/8ba9b190, capture_remote.py37525B/95b0344d, upload_remote.py24710B/e926b7ba,
and inherited transport/actions helpers. Full hashes remain in the old checked
sources and fixed source pin chain. Remote import remains passive; actions and
caller retain their existing private local composition on import, with no
native dispatch. Do not introduce a new transport or claim passive no-I/O
imports for these historical caller/action modules.

Proposed local owner is new RAW/native_inert_run01; scope file is
inert_run01_scope.json and preparation file preparation.json. Proposed remote
owners are PARENT/RUN_ID-adapter (only remote.py is pushed), RUN_ID-upload and
RUN_ID-capture. PARENT remains /home/arduino/sumox26_codex_build. None is claimed
absent here. Existing /tmp/remoteocd absence remains a hard upload requirement;
D200 cleanup results/fresh inspection must establish it separately. No consumed
D191/D196/D200 cleanup helper or owner may be rerun from this capture.

## Field-map and offline interpreter seams

A new field map must be bound to D199 native_abi_static01/result.json and its
accepted ABI summary, not to the old D195 result. The binding records independent
full SUMOX_LAYOUT block comparisons for all14 selected historical types. They
are byte-identical without namespace or declaration projection. Thus retain
all104 selected old fields exactly, including Trace count/rejected/overflow/
timing_fault/current/first_failure flags and every nested PreviousTick field.
The full source map has SHA256
b96b6a3e7349baff471af3bb115c13ab2c1de07c6949a419ed3e9ed1afe16939
(10447 bytes). Preserve that file; create a new current field map later.

Add only motors::SettleProbeSample and motors::SettleProbeReport with the11
observed fields below. Their full ptype block hashes, individual queried
member widths/offsets and reason values are in the binding. Retain separate
observed motors::SettleProbeReason size1/alignment1. The resulting selected map
has16 struct types and115 selected fields; enum semantics are additional
metadata, not an invented memory window.

| Type/member | Offset | Width | Decoder representation |
|---|---:|---:|---|
| Sample.elapsed_us | 0 | 4 | u32 |
| Sample.poll_index | 4 | 4 | u32 |
| Sample.reason | 8 | 1 | u8 plus observed enum annotation |
| Sample.fresh_mask | 9 | 1 | u8 |
| Sample.valid | 10 | 1 | u8 |
| Sample.reserved | 11 | 1 | u8 |
| Report.current | 0 | 12 | SettleProbeSample |
| Report.first_failure | 12 | 12 | SettleProbeSample |
| Report.has_current | 24 | 1 | u8 |
| Report.has_failure | 25 | 1 | u8 |
| Report.reserved | 26 | 2 | u8[2] |

The observed reasons are NONE0, SUCCESS1, NULL_CONTEXT2, PRECONDITION3,
INITIAL_BANK4, POLL_DEADLINE5, POLL_BANK6, FINAL_DEADLINE7 and POLL_LIMIT8.
The validity masks elapsed1/poll2/fresh4/allowed7 are pinned header semantics,
not GDB-observed constants. Do not conflate source semantics with target ABI.
For each completed sample, preserve these D197 meanings:

| Reason | Expected valid mask | Existing observation semantics |
|---|---:|---|
| NULL_CONTEXT, PRECONDITION, INITIAL_BANK | 0 | elapsed/poll/fresh all0; INITIAL_BANK has no elapsed capture |
| POLL_DEADLINE | 7 | loop-top elapsed >=150, current poll, fresh mask before current poll checks |
| POLL_BANK | 7 | earlier loop-top elapsed, current poll, mask after three flag checks |
| FINAL_DEADLINE | 7 | final elapsed >=150, current poll, mask7 |
| SUCCESS | 7 | final elapsed <150, current poll, mask7 |
| POLL_LIMIT | 7 | last loop-top elapsed, poll4095, mask after last flag checks |

The uint32 elapsed is unsigned wrap subtraction already performed by firmware;
the interpreter must not reconstruct duration from extra timestamps. POLL_BANK
and POLL_LIMIT specifically retain an earlier time sample. Poll_index is an
executed zero-based loop index, not4096 or a separate hardware-read count.
Presence flags govern availability. A zero scalar with valid bit clear is not
an observed zero duration. Never clear or replace stored first_failure with
current, and never equate current with first_failure after later cleanup.

Prepare a new offline interpreter under new RAW, preserving the old3516-byte
interpret_run01.py/d6409ff5 unchanged. Retain its validated saved-file base64,
length/hash checks, checked field map, explicit little-endian decode and fixed
six-window type mapping. Replace only the live previous mapping with
settle=motors::SettleProbeReport, retain nested PreviousTick decoding and add
only fixed u8[2] decoding for reserved bytes. Proposed pure seams for independent
fixtures are decoding one fixed known type and interpreting a supplied saved
packet; fixed packet/map pins and default paths belong to the thin offline main.
Finalize exact function signatures in the adopted interpreter contract before
its independent oracle or implementation is authored.

Strengthen the future interpreter's admission where the old one-off script was
only manually reviewed: reject duplicate/missing/unexpected saved-file and
snapshot identities, malformed base64, bad size/hash, unknown window name or
wrong current address/width, trailing/short window bytes, and invalid stored
bools. Do not silently overwrite duplicate names in a dict. Retain original raw
bytes and capture receipt even when interpretation fails. New u8 enum/mask/
presence/reserved fields must retain their numeric bytes; annotate unavailable,
unknown or inconsistent values separately and never manufacture a valid sample.
Reserved values, reason/mask expectations and flag relationships must not be
used to rewrite input or assert atomicity. Whether that annotation is a returned
inconclusive result or an interpretation failure is an open narrow API choice
for the final interpreter contract, not a hardware behavior change.

Keep decoded first/second windows and repeated equality indicators, but retain
coherence=UNPROVEN even when all selected fields repeat. No automatic matching
of the lifetime first native failure to an epoch, outer trace stage or final
HALT is justified without cross-evidence: the new sample has no stage, token or
epoch identifier. A reason localizes a recorded branch, not its physical cause.
Diagnostic publication overhead can affect timing; measured values would be
for this instrumented image. No WCET or safety-pass label follows from decode.

## Provenance, scope and independent oracle work still required

The future caller preparation retains its exact schema/run_id/source_sha256/
bindings/files keys and upload/capture binding roles. Twelve required
provenance paths are the new COMPILED inputs_static, native_static result and
artifacts, native_abi_static01 result/local_result/abi, native_entry_static01
result/local_result/entry, and the three actual compile/ABI/entry reviews.
Compile and ABI have the exact accepted pins above. All four entry pins are
PENDING. The actual entry review must assess both native SETTLE/publication
blocks and prior entry/Runner behavior; do not fill its hash from a source-only
review or the earlier build's entry receipt.

Scope retains the exact six keys schema/run_id/board/source_sha256/
expected_identity/files and11 required file roles (preparation plus three new
sources, three new run/action/remote oracles, final caller/remote contracts and
their two reviews). No scope/preparation self hash. A final interpreter/map and
offline decode review are separate evidence, never an implicit native action.
Every file/path/pin must be frozen, reviewed and in the clean HEAD used for the
single attempt. The draft filename is not silently substituted for either
final caller/remote contract.

Freeze new independent tests before their authors read new implementations.
The existing D195 test inputs are pinned in the binding:

| Historical oracle | Total selected methods | Current SHA256 |
|---|---:|---|
| test_app_motor_observe_remote.py | 42 (26 inherited+16 additions) | f45218ea3d9fb118adfe796c12fc5f4bab654c843cf33cc531e81d99a3f41fc6 |
| test_app_motor_observe_actions.py | 24 (13 inherited+11 additions) | 103493975bccdcab094b412a5ba26cf125a6f294a9b5efac167660f6fda8a563 |
| test_app_motor_observe_run.py | 25 (20 inherited+5 additions) | 7af304d06b85de0f835856ecbd241d957c193b7d252c2849eea474e6043fbb9c |

Reuse all applicable assertions through explicit metadata/private fixture
projection. Document adapted names/bytes/hashes/type maps; preserve old files
and all original failures. Keep independent remote lifecycle/wait/first-error
checks, action framing/strict waits/closure and caller one-shot/fresh-owner/
source inventory/cleanHEAD/admission tests. Add exact six windows/26 read plan/
727432 accounting and old previous/address/package/source refusals,129-input
D198 projection, matching remote/action plans, unchanged closure and actual
composed payload/command bounds. Do not replace unrelated historical assertions
with a weaker new harness.

The new field-map/interpreter oracle must independently check observed-offset
provenance, all old104 fields plus the11 additions, nested pre-abort PreviousTick
retention, first/current separation, zero-validity versus measured zero,
unsigned values and all9 reason labels; reserved/mask/presence annotations,
loss-field preservation and strict saved-packet identities; raw immutability,
partial/failure retention and no synthesized terminal/WCET/coherence claim.
Use synthetic bytes and clocks, no device or real sleep. Tests for the new
interpreter must be meaningful first-time checks; the historical one-off script
has no claimed independent decoder suite. Run Windows/Linux serially, freeze
first failures and source/reviews before native admission.

Outstanding concrete inputs: accepted actual entry four-file pins; adoption of
final fixed caller/remote scope; exact interpreter pure API/invalid-record
policy and its final field-map/source/oracle hashes; frozen new source and host
review receipts; fresh board/tool/process/space/owner/scratch admission; exact
preparation/scope/clean reviewed HEAD. These are evidence or implementation work
remaining, not new general privilege or motor-run permission requests.

Draft preparation performed only local reads, raw JSON/base64/ptype comparison,
count-checked in-memory byte transformations and AST parsing. No candidate
implementation or new test was written or run; no board/native/MCU/credential
action occurred. This draft intentionally leaves actual results unresolved.
