# Proposed D207 inhibited constant-metadata runtime comparison

26 September 2026. This is a data-only proposal for one fresh inhibited diagnostic
attempt after D202 moved expected timer metadata arithmetic into constants.
It follows D203 compilation, D204 ABI and D205 entry observations. No source,
test, executable, native scope or attempt owner is created by this proposal.
Adoption, independent implementation/oracle ownership and the gates below are
still required. Preserve every historical source, failure, receipt and owner.

The objective is to observe whether this image completes setup in this one
attempt and then report its bounded runtime and lifetime SETTLE outcomes.
D201's accepted observation was FROZEN/SETUP_FAILED, begin_ok=false, zero
epochs/polls, and a lifetime first failure FINAL_DEADLINE at154us against the
unchanged150us predicate. The subsequent SUCCESS132us sample was initialization
cleanup; it did not make setup successful. No automatic causal attribution or
claim that an intermittent failure is eliminated follows from a later success.

## Fixed current image, evidence and owners


Current source is 4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2; run identity is app-motor-const-4bc3a2e6-run01.

The profile stays app_motor_observe.ino, arduino:zephyr:unoq:link_mode=static,
default startup, MATCH=0, MOTORS_ALLOWED=0 and SUMOX_MOTOR_FAULT_PROBE=1.
The existing grant path stays empty/inhibited. Do not alter firmware, pins,
config,150us deadline,4096 SETTLE polls,10000 epochs,10000000 observer polls,
priority ordering or stop behavior. No motor-capable authorization is supplied.

Board is ADB serial2629958581; expected identity is user arduino, UID/GID1000,
home /home/arduino, Linux6.16.7-g0dd6551ae96b/aarch64, Python3.13.5 and boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. These fixed values must be freshly checked
by the inherited lifecycle; saved file evidence never substitutes for use-time
identity, installed-tool, source or artifact checks.

Fixed build is /home/arduino/sumox26_codex_build/app-motor-const-static01/build.
Only these current application files may bind the upload/capture:


| Role | Bytes | SHA256 |
| --- | ---: | --- |
| raw app_motor_observe.ino.bin | 95352 | 76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3 |
| packaged app_motor_observe.ino.bin-zsk.bin | 95368 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 |
| installed loader ELF | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| loader_image | 263680 | e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2 |


The twelve current provenance roles are fixed below. D205's completed independent
actual review is now final and pinned; no unfinished review is included.
The unchanged caller checks machine-readable status/source/boot/first_error
predicates and pins review bytes, but does not parse prose review conclusions.
Coordinator acceptance remains a separate gate.


| Repository-relative provenance | Bytes | SHA256 |
| --- | ---: | --- |
| state/analysis/P7_motor_const_compile_raw/inputs_static.json | 13559 | 1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/abi.json | 5410 | 6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97 |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/local_result.json | 275 | 3cd224b237fc1b18586d7b2fb22c2a47833a801fea06b96b338027102db5d55d |
| state/analysis/P7_motor_const_compile_raw/native_abi_static01/result.json | 904847 | bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0 |
| state/analysis/P7_motor_const_compile_raw/native_entry_static01/entry.json | 10875 | b80c8ce88d199de4538c465ab9c858ca69f2c635a5630a9b731297d9aa7cf2d5 |
| state/analysis/P7_motor_const_compile_raw/native_entry_static01/local_result.json | 277 | 495c501ded117bb53e09e6e64eba56403b66469a41bc7b8c376a5d7aa90600e9 |
| state/analysis/P7_motor_const_compile_raw/native_entry_static01/result.json | 423604 | 6700e974d75a99d3b82d044bb026cb43c060730b4f94fad16c007d4702d944e2 |
| state/analysis/P7_motor_const_compile_raw/native_static01/artifacts.json | 9645 | fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd |
| state/analysis/P7_motor_const_compile_raw/native_static01/result.json | 1605 | 323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7 |
| state/reviews/P7_motor_const_abi_actual_review.md | 10178 | 4cd28fe8ce3b689319da5ddb42739c664fd0e4bcdc2552b521ee23b8b3331411 |
| state/reviews/P7_motor_const_compile_actual_review.md | 10135 | 9c3e8cfe07ae33cac8d4a91f74127c33d3929e299bd5da339934943d784f21df |
| state/reviews/P7_motor_const_entry_actual_review.md | 19761 | 008572bfc541b8f0213fe6ed284af242dff8517e7fdc96283ee255d386d9e3f1 |


Require COMPILE_CHECKED, ARTIFACTS_CHECKED, STATIC_ABI_OBSERVED and
STATIC_ENTRY_OBSERVED under the same inherited predicates; pin raw ABI/entry
results as well as summaries and local closures. Retain all failed predecessor
evidence; never substitute its bytes into current successful provenance.

Use state/analysis/P7_motor_const_run_raw/ for preparation.json,
inert_run01_scope.json, run.py, actions.py, remote.py, interpret_run01.py,
native_inert_run01 and retrieved_inert_run01. The first two owner directories
remain distinct. Fresh remote owners are:


- /home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-adapter

- /home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture

- /home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-upload


No current owner absence is claimed by this proposal. No old D190/D195/D201
owner, adapter or result may be reused. The inherited upload creates/reset-runs
this exact inhibited image once; capture follows only successful upload under
the existing action sequence. No alternate image or reset is admitted.

## Exact metadata source derivatives

The companion state/analysis/P7_motor_const_run_raw/run_derivation01.json is
normative fixed data: complete ordered old/new/count operands, every intermediate
identity, prospective output identities, current ABI comparisons,129 source
pins, all twelve provenance pins and proposed preparation data derivation.
It is not executable or a runtime selector. This contract contains no digest of the companion; the companion pins this
contract, so there is no circular binding. The scope must freeze both files
after adoption.

For every source below, apply substitutions in table order to its complete
pinned predecessor bytes, preserving LF and every other byte. Counts apply
after preceding replacements. Do not add branches, imports, predicates,
arguments, parameterization, reads, sleeps, retries or filesystem operations.
Do not rename app_motor_observe sketch/namespace or motors::SETTLE semantics.



### Remote

Input: state/analysis/P7_motor_settle_run_raw/remote.py, 11343 bytes, SHA256 577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0.

Proposed output: state/analysis/P7_motor_const_run_raw/remote.py, 11331 bytes, SHA256 51c60cd5ac87b823b84b2c7d993933690f0a3110e4d89c7cb958549fb5f111bc.


| Old literal | New literal | Count |
| --- | --- | ---: |
| 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da | 4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2 | 1 |
| app-motor-settle-117cc0e7-run01 | app-motor-const-4bc3a2e6-run01 | 1 |
| app-motor-settle | app-motor-const | 8 |
| _app_motor_settle_private_ | _app_motor_const_private_ | 1 |
| AppMotorSettleCapture | AppMotorConstCapture | 2 |
| 95504 | 95352 | 1 |
| d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc | 76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3 | 1 |
| 95520 | 95368 | 2 |
| e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 | 1 |
| 727432 | 727128 | 1 |


### Actions

Input: state/analysis/P7_motor_settle_run_raw/actions.py, 12507 bytes, SHA256 8918231c9c2aaf1b72120539e1677db73ce9103798fa860e9fa2501ac669092a.

Proposed output: state/analysis/P7_motor_const_run_raw/actions.py, 12501 bytes, SHA256 8aac6877a3bae25001c26c088ea947bbf3c7c0f2c0113619fb1db8c2a53834d9.


| Old literal | New literal | Count |
| --- | --- | ---: |
| 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da | 4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2 | 1 |
| app-motor-settle-117cc0e7-run01 | app-motor-const-4bc3a2e6-run01 | 1 |
| app-motor-settle | app-motor-const | 4 |
| _app_motor_settle_actions_legacy | _app_motor_const_actions_legacy | 1 |
| 577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0 | 51c60cd5ac87b823b84b2c7d993933690f0a3110e4d89c7cb958549fb5f111bc | 1 |
| ADAPTER_BYTES = 11343 | ADAPTER_BYTES = 11331 | 1 |
| 95520 | 95368 | 1 |
| 727432 | 727128 | 1 |


### Caller

Input: state/analysis/P7_motor_settle_run_raw/run.py, 24885 bytes, SHA256 fe2b4d644edbc6096fe1956f4aa8fe801eed4d125ab19ea31eef86ca70469de4.

Proposed output: state/analysis/P7_motor_const_run_raw/run.py, 24862 bytes, SHA256 d135835d22be424e9599d5a100f66275732bac6486facd7b86367d09c2c811ff.


| Old literal | New literal | Count |
| --- | --- | ---: |
| 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da | 4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2 | 1 |
| app-motor-settle-117cc0e7-run01 | app-motor-const-4bc3a2e6-run01 | 1 |
| P7_motor_settle | P7_motor_const | 7 |
| test_motor_settle | test_motor_const | 3 |
| app-motor-settle | app-motor-const | 6 |
| tools/compile_motor_settle_probe.py | tools/compile_motor_const.py | 2 |
| b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62 | 957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247 | 1 |
| aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 | 1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95 | 1 |
| D198 | D203 | 2 |
| 95504 | 95352 | 1 |
| d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc | 76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3 | 1 |
| 95520 | 95368 | 1 |
| e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 | f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7 | 1 |
| state/analysis/P7_motor_const_caller_contract.md | state/analysis/P7_motor_const_run_contract.md | 1 |
| state/analysis/P7_motor_const_remote_contract.md | state/analysis/P7_motor_const_run_raw/run_derivation01.json | 1 |


### Interpreter

Input: state/analysis/P7_motor_settle_run_raw/interpret_run01.py, 31266 bytes, SHA256 ea43a42f582f6e8bf2dfa4e2090efb03313f3333036cc1a3159d72295f680c88.

Proposed output: state/analysis/P7_motor_const_run_raw/interpret_run01.py, 31259 bytes, SHA256 d96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab.


| Old literal | New literal | Count |
| --- | --- | ---: |
| P7_motor_settle | P7_motor_const | 2 |
| MAP_BYTES = 16346 | MAP_BYTES = 16755 | 1 |
| 0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd | ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709 | 1 |
| app-motor-settle-117cc0e7-run01 | app-motor-const-4bc3a2e6-run01 | 1 |
| 117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da | 4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2 | 1 |
| motor-settle | motor-const | 4 |
| 95520 | 95368 | 1 |


The remote is a10-step derivative, actions8, caller15 and corrected interpreter7.
The interpreter predecessor is the corrected ea43a42f source, not its failed
initial implementation. _flash, _receipt_types, _counts, _read_types and
_read_rows remain byte-identical; after-flash indices4/6/25/20, late count
classification, read-row key/type ordering and all partial-prefix behavior
must survive unchanged. Keep the accepted parser-portability oracle repair
and all original first-failure evidence.

### Private composition and compile inventory

Run and actions retain their original private loading algorithms and injected
helper/compiler/actions seams. They remain no-native-dispatch imports with
existing local source reads, not passive/no-I/O imports. Remote retains passive
definition import. Runtime action modules remain private and source-pinned;
do not register them in sys.modules or invoke historical mains.

The private legacy inert caller is obtained from the pinned historical
P7_motor_fault_raw/inert_run.py with the exact existing three injection seams,
motor-fault prefix rewrite, caller-path rewrite,11-to13 command-count literals
and adapter labels already used by D201. Only its new fixed prefix changes.
Complete operands/counts are in private_runtime_projections. The private
inert actions use their existing single fixed prefix replacement. No private
projection is written over a source or emitted to disk.


| Private projection | Bytes | SHA256 |
| --- | ---: | --- |
| inert caller | 22983 | 3bd88946372ae637acdcfce2170a385e92dc313665bc75ed268c4aaa9ba1af75 |
| inert actions | 19156 | cd3a28e82de554358e1a4855a76b5dc316f0007158bdac846fcb464e9130c3ab |


Use the unchanged accepted launcher tools/compile_motor_const.py (7557 bytes, SHA256 957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247).

It checks originals before private load_caller(root=ROOT). Only its
CompileDiagnostic.source_names/source_mapping seams are used by runtime
admission, through the existing root/base object; no compiler main, build,
claim, compiler process or transport path is called.


| Existing compile source role | Private bytes | Private SHA256 |
| --- | ---: | --- |
| tools/app_motor_fault_compile_remote.py | 6893 | 914d4d11057c8982154fbcd80fbea485977cf4952fad045625ca88271052040a |
| tools/app_motor_fault_static_policy.py | 8266 | e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d |
| tools/compile_app_motor_fault.py | 29874 | bda40e969dc48d4194f1c391c013cf0853e1fb39dee780a94f4754412d59f41a |


Current manifest is state/analysis/P7_motor_const_compile_raw/inputs_static.json (13559 bytes, SHA256 1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95).

Require its app-motor-const-static-inputs-v1 schema, current source, boot,
129 exact file pins, exact source inventory and source mapping. All129 current
working file hashes were checked during this data preparation. This is local
source evidence, not a new compile or remote source admission.

## Current field map and fixed read plan

The accepted D204 ABI independently reports all the following values. Its
23 type sizes/alignments, eleven Runner windows, separate SETTLE report and
nine reason values equal the predecessor. All16 selected complete current
SUMOX_LAYOUT blocks were compared byte-for-byte with D199 without projection.
The companion records each current block length/hash. Equality is verified
from current GDB output, not assumed from unchanged source.


| Window | Address | Bytes | Type |
| --- | ---: | ---: | --- |
| trace | 536951180 | 2128 | motor_fault::TraceReport |
| report | 537119696 | 1168 | app_motor_observe::Report |
| runtime | 537117984 | 600 | app::RuntimeReport |
| transaction | 537115448 | 504 | app::TransactionReport |
| settle | 537121768 | 28 | motors::SettleProbeReport |
| gate | 536953520 | 88 | motors::MotorGate |

Runner is at536951136,169736 bytes/alignment8. Its separate SETTLE object is
at537121768,28 bytes/alignment4, LOCAL OBJECT DEFAULT section5. The report
retains nested before_abort.previous at537120816,48 bytes; live previous at
537115952 remains omitted. Do not merge it with the pre-abort snapshot.

Prepare one new data map at
state/analysis/P7_motor_const_compile_raw/abi_static01_decode_fields.json.
Take the pinned D199 map and apply the seven exact top-level field updates
under field_map.steps in the companion; serialize json.dumps(value,indent=2,
sort_keys=True), one LF, UTF-8. Update current raw/summary/source identities,
schema, predecessor-map identity, provenance and all16 comparison rows only.
Keep all115 selected field kinds/offsets/widths,16 types, windows, enum values
and source-only masks1/2/4/7 byte-for-byte as JSON values. Those masks are pinned
source semantics, not newly queried target constants.


Required new map: 16755 bytes, SHA256 ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709. The source map is state/analysis/P7_motor_settle_compile_raw/abi_static01_decode_fields.json (16346 bytes, SHA256 0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd).

The map remains data, within65536 bytes, and needs independent review before
its use. A prospective hash is not a claim that the new map file already exists.

Exactly26 reads request727128 bytes: two flash brackets plus six windows in
each of two samples. Loader remains263680 bytes in five chunks
[65536,65536,65536,65536,1536]; packaged sketch is95368 bytes in two chunks
[65536,29832]. Windows total4516 bytes per sample. The arithmetic is
2*(263680+95368+4516)=727128. Ordered read rows and indexed filenames are in
the companion: before.loader0..4, before.sketch0..1, six first windows,
six second windows, after.sketch0..1, after.loader0..4.

Keep window indices7..18, SETTLE indices11/17 and flash terminal indices
before_loader4, before_sketch6, after_loader25, after_sketch20. No arbitrary
caller window, address, name, count, extra poll or retry is accepted.

## Preparation and unchanged eleven-role scope

Preparation retains exactly schema,run_id,source_sha256,bindings,files, with
schema app-motor-const-run-preparation-v1. Bindings remain exactly upload and
capture, with full expected-versus-prepared canonical equality before claim.
Preserve installed-tool pins, capture configuration, loader and loader_image,
directory structure and all14 upload absence paths. Only the exact source,
run/build/output paths and raw/package identities change.

The companion gives the deterministic metadata derivation from D201
preparation, current twelve provenance values and serialization. It must yield:


9988 bytes / SHA256 519a95f623e3c463842217cdb568cb1909941974b49c36453bfc8f8ea1f8449e.

This proposal writes no preparation or native scope file. An implementation
worker later prepares them under explicit ownership and hashes current files.

Scope retains exactly schema,run_id,board,source_sha256,expected_identity,files.
Its schema is app-motor-const-native-scope-v1. All eleven distinct file roles:


- state/analysis/P7_motor_const_run_raw/preparation.json

- state/analysis/P7_motor_const_run_raw/run.py

- state/analysis/P7_motor_const_run_raw/actions.py

- state/analysis/P7_motor_const_run_raw/remote.py

- tests/tooling/test_motor_const_run.py

- tests/tooling/test_motor_const_actions.py

- tests/tooling/test_motor_const_remote.py

- state/analysis/P7_motor_const_run_contract.md

- state/analysis/P7_motor_const_run_raw/run_derivation01.json

- state/reviews/P7_motor_const_caller_review.md

- state/reviews/P7_motor_const_remote_review.md


The old caller-contract role maps to this single run contract, and the old
remote-contract role maps to its companion run_derivation01.json. This avoids
duplicate policy documents while preserving the exact eleven-key validator
shape and pinning both normative inputs. Caller and remote source/host reviews
remain separate roles. There is no recursive scope/preparation self hash.
No placeholder oracle/review/hash may be admitted. Offline interpreter and
field-map acceptance remain additional coordinator gates outside these
unchanged eleven caller roles.

## Preserved native lifecycle and failure policy

Inherit the complete D201 caller and remote contracts except the fixed metadata
above. Preserve InertRun, build_command, validate_reply, run_actions, public
adapter collect/upload and every original error/closure seam. Retain
--check-only|--execute with --reviewed-head; clean committed reviewed HEAD,
Python-I/-B as required, unchanged local/ADB hashes and continuous clean-tree
checks. Check-only stays local/read-only/unclaimed.

D206 cleanup must first close through its separate authenticated result and
independent actual review. Then freshly verify /tmp/remoteocd absence, current
board/boot/UID/GID/tool/source/artifact identities, no recognized conflicts
and unused adapter/upload/capture/local owners. Do not infer protected process
clearance from D206's initial nonprivileged inventory. Runtime preparation
does not authorize a cleanup retry, root command or credential access.

Retain one exclusive adapter claim and one exact remote.py push, durable
intent before each action, verified claim before push, one upload and one
conditional capture. Complete success is exactly13 transports: four single
stage/action labels plus three dispatches each for three prerequisite groups.
Keep seven labels and every counter, set, closing prerequisite and immutable
command assertion. A consumed/uncertain owner is never reused.

Preserve upload195s/capture630s/prerequisite60s outer bounds and remote
upload180s/capture600s, command30000UTF16 units including NUL, reply65536 bytes,
decoded action payload196608 bytes, and all installed/process/storage guards.
Retain the single declared30-second pre-sample wait and2-second inter-sample
wait, injected clocks/sleepers, finite exact types excluding bool, timing order,
remaining-budget checks and partial-read evidence. No additional sleep/poll
or retry is added. Wait completion does not prove FROZEN, completed epochs,
coherence, target progress or success.

Keep all11 action-envelope keys, strict schemas, frame/sequence/hash handling,
the exact five analysis keys, returned-only success and durable_unattributed
failure fallback. An inner collected report cannot override an outer framing,
transport, source, close or postcheck error. Preserve first errors, every raw
receipt, partial child evidence and failed-owner consumption. Stop after an
attempted failure; no silent rebind, alternate transport or automatic cleanup.

## Corrected offline interpretation and observed outcome

The decoder inherits the complete pinned corrected D201 contract and source
except the exact seven metadata substitutions. Public decode, annotate_settle,
interpret and main interfaces, pure-call no-I/O behavior, defensive copies,
strict JSON/duplicates/nonfinite/type/int-vs-bool handling, canonical base64,
literal allowed paths, prefix ordering, hash/size/linkage/closure checks,
stable error priorities and field traversal remain unchanged. Keep packet
bound1048576, map bound65536, all115 fields and64 trace slots. Retain source
predicate annotations as annotations, not new format rejection.

Retrieve only saved upload/capture results and at most the twelve declared
SRAM files using a separately reviewed nonprivileged file-only retrieval
after capture. Record exact raw packet hash and closing rereads. Pass that
actual explicit hash to the offline CLI; no guessed future packet hash is
embedded. Preserve packet, raw window bytes and decoded result. Failed or
partial packets keep their original native status and first error even where
prefix decoding is possible. Retrieval/parser success does not upgrade a
failed native operation.

Report collection integrity separately from observed application behavior.
A current begin_ok=true and absence of SETUP_FAILED would show this attempt
passed initialization; require the actual observer/runtime fields and trace
available in this attempt to support that statement. Report actual polls,
epochs, phase/reason, lifetime first_failure, current sample, presence flags,
validity masks, all loss fields, runtime maxima and halt/inhibition fields.

A later CALLBACK_FAILURE, runtime/timing abort, poll limit or other terminal
condition remains a failure/limitation in its own right. Do not hide it because
setup passed. EPOCH_LIMIT/POLL_LIMIT are diagnostic stop reasons, not physical
qualification. A clean lifetime report supports only no recorded failure in
this finite attempt, not elimination of intermittent SETTLE failures. Keep
historical D195/D201 failures intact for comparison.

The native first_failure has no epoch/stage/token; its association with a
particular callback must not be invented. Two equal sample sets still have
coherence=UNPROVEN; no atomic or temporally coherent publication follows.
Compare observed150us-predicate values without changing the limit, extrapolating
cycle savings, inferring live PWM getter cost, declaring a worst-case bound
from a sampled maximum, or attributing physical electrical behavior.

## Independent tests, reviews and activation boundary

Separate oracle authors must freeze current fixtures and transitive inputs
before reading or executing new implementations; implementation authors must
not read their new oracles first. Preserve the full accepted D201 suites:
remote45, actions27, caller27=99 native methods, plus all67 corrected offline
interpreter methods. The historical Windows native suite has56 passes and43
explicit Linux-only skips; Linux executes all99. Interpreter has67 on both
platforms without skips. Preserve every assertion and former failure,
including the corrected deep-JSON portability case, not just the successful
reports. Record any new supplements and platform skips independently.

Add exact10/8/15/7 source recipes, private inert/compile caller identities,
current16-type/115-field map identity and six current windows; two correctly
sized95368 sketch chunks/26reads/727128 total; stale D201 source/package/map/
owner/ABI/entry refusals; preserve earlier D194/D195 negative provenance.
Exercise success and every existing error/partial/clock/framing/close branch
through controlled fixture seams. Keep real admission/prepare behavior where
already tested; do not replace it with success-only mocks or execute native
endpoints. No additional host test may weaken an existing assertion.

Run suites serially with fresh exclusive receipts, Linux TMPDIR=/dev/shm,
Windows dedicated TEMP/TMP/TMPDIR before startup and Python-I/-B. Root owns
execution and exact command/time bounds; account for the prior caller's
approximately285s Linux duration when selecting its outer bound. Preserve raw
streams, first errors and opening/closing pins. Source/host, field-map/
interpreter and exact final scope reviews must pass before a committed clean
HEAD/check-only and one separately admitted native execution.

No executable, test, compiler, transport, upload, reset, MCU read, authentication
or motor operation occurred in preparing these two proposal files. This proposal
does not pass a phase gate, grant motor permission, establish live RAM/stack/
WCET, prove a physical remedy or replace independent actual-result review.



## Fixed predecessor contracts and corrected evidence


- state/analysis/P7_motor_settle_caller_contract.md (15129 bytes, SHA256 4a07cd9a8d21620896446665edccf5b7ad165c11e8bd97df9784c3a6e618f3f9)

- state/analysis/P7_motor_settle_remote_contract.md (10744 bytes, SHA256 6d245a4e1f0426d5ed54b1ca47d124643ba9b2e3b6c86975294ba6efcd641dd3)

- state/analysis/P7_motor_settle_interpreter_contract.md (32296 bytes, SHA256 6007ec4e2e22cdf0e8f751790c49924b26b4adb8f9dfde5d5f6db2ed9bd7dff8)

- state/analysis/P7_motor_settle_run_raw/interpreter_repair01.json (7384 bytes, SHA256 baa0aacba7a4d8d12878db6ee9eebf532820b88ba81960e404f0ef7f2e56eb71)

- state/analysis/P7_motor_settle_run_raw/interpreter_oracle_portability01.json (5794 bytes, SHA256 883bdf33acb61412a0963417b98786374fb4010cdb65c9e6a086559322ba0006)

- state/reviews/P7_motor_settle_actual_review.md (14116 bytes, SHA256 690a41643fc06a7d5c56ab61cc89113d602d8d6dee9e436cdbb09e3f7f19a0bc)
