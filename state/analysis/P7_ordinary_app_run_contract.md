# D212 proposal: one ordinary inhibited upload and finite passive observation

UNADOPTED PROPOSAL, 26 September 2026. D051 permits preparing this proposal. It does not authorize native execution. D211's separate exact upload-scratch cleanup must close before any D212 runtime admission. The accepted D208 ordinary build, D209 ABI and D210 entry observation are prerequisites, not evidence that this new attempt ran.

Only this contract, run_derivation01.json and ordinary_scalar_map01.json are authored here. No new executable or oracle is authored, imported or run. No compiler, device, authentication, upload, cleanup or MCU operation occurred during preparation. All historical sources, tests, failures and receipts remain unchanged.

## 1. Purpose and fixed evidence

Observe whether the current ordinary app starts and makes sampled progress under its existing inhibited profile. This is a continuous ordinary application, not a diagnostic Runner. Its loop continues after the host stops collecting. There is no Trace, SETTLE report, finite epoch limit, terminal freeze, before-abort snapshot or forced final halt in this build. Do not add any such mechanism or change production source/configuration for this attempt.

Fixed source: 9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.
The sketch is src/app/app.ino; static arduino:zephyr:unoq:link_mode=static, default startup, MATCH=0, MOTORS_ALLOWED=0, SUMOX_MOTOR_FAULT_PROBE=0 and every setup grant zero. Current grants, mounting axes and dump origin are derived from pinned config/configuredSetupGrants, not newly assumed hardware facts. No STAND/RING permission, pin acceptance, phase gate or measured WCET is implied.

The companion derivation is normative data: ordered old/new/count transformations, prospective source identities, exact 12 provenance pins, input pins, artifact bindings, read plan, inherited body identities and test selection boundaries. Its bytes/SHA are 117644B/237e2b54238b8f23e4fc6e00beb20b4e37d03a96e893a3146036787b962a3867. Source-to-image linkage is the accepted D208 compile; no native address is borrowed from a diagnostic image.

The accepted ordinary artifacts are:

| File | Bytes | SHA-256 |
|---|---:|---|
| build/app.ino.bin | 92928 | 6f5f531b114219d712d857b4ac89ad161ceb217211207788a27443b7d4ab6db7 |
| build/app.ino.bin-zsk.bin | 92944 | 7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad |
| build/app.ino.elf | 170376 | aaeeb64025dae2b2f8bf0458a39c110377ca8d5e4c9f833fae75444a181f6db5 |
| build/app.ino_debug.elf | 1751548 | 71e512382e764810ed02eec110e3c1c003244d41d608b145ea400e1e8235ab90 |

D208 artifact packet 275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0;
D209 ABI e224750ea11a9bd462c1708e2d797b622e9fee56e3e46e479242bff19eefdbf4;
D210 entry 8cb90c514ffc6a9e1f04c8ea601ec3f70e5c49c45017e6da88a9753026298f85.
Accepted actual reviews are respectively 8cd383e47ab78db74141c0100aedb134afaeac60195555c8eac3b529e1de9865,
585be669385e1ca85ddd188d3eeda5fdf11cfc3392eea614370d9bfabbcc4b6a,
a30c194bd8c5949455a9bbbbffdefeb0a065e0747ca0e5227ed52333237f309d.
Full raw results/local closures/reviews are in the exact 12-member provenance set. Their saved values cannot substitute for fresh identity/source/artifact admission.

## 2. Owners, roles and ordinary source mapping

Use RUN_ID ordinary-app-9044ebbb-run01. Local owners are P7_ordinary_app_run_raw/native_inert_run01 and retrieved_inert_run01. Remote owners under /home/arduino/sumox26_codex_build/ are ordinary-app-9044ebbb-run01-adapter, -upload and -capture. Build inputs remain the accepted ordinary-app-static01/build and source9044.../app. Owners must be absent when first claimed. No previous diagnostic/native owner is reused or reset.

Keep the existing 11 SCOPE_FILES roles: preparation/run/actions/remote, three native oracles, this contract, its companion derivation, caller review, remote review. The companion derivation fills the second scope-document role; no duplicate contract is needed. Keep preparation's exact schema/run/source/bindings/files keys, two fixed bindings and 12 exact provenance entries. The independent map/decoder/oracle/review/freeze and D211 closure are additional coordinator prerequisites pinned before execution, not silently omitted because the legacy native scope has 11 roles.

The caller must load accepted tools/compile_ordinary_app_static.py, SHA40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89, through its checked load_caller. Use that private CompileDiagnostic.source_names/source_mapping; do not invoke compile/main. The ordinary manifest is exactly125 pinned files, schema ordinary-app-static-inputs-v1 and SHAa5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7.

This is a substantive source-admission distinction from diagnostic129: accepted D208 selects src/app/app.ino and the source-only mapping; it preserves ancestry, extension, reserved-path, collision/case-collision, count, 4MiB and exact digest checks. Its digest ordering is sorted(mapped,key=Path). Real host admission must crosscheck the pinned ordinary source hash helper; a success-only fake mapper is not enough. The legacy variable name diagnostic may remain private, but its loaded behavior is the pinned ordinary mapper. No bench/Runner/probe source is substituted.

All14 absence paths remain exact; only the three sketch.yaml/yml/json paths move to current source9044.../app. Retain the /tmp/remoteocd absence guard, all installed helper/tool pins and exact static/default upload CLI. Do not relax this guard or clean scratch as part of the run.

## 3. Exact native composition

Derive the three new files from P7_motor_const_run_raw only by the companion's ordered counted substitutions. This is metadata adaptation of the established lifecycle, not a new generic framework:

| Subject | Steps | Prospective bytes | Prospective SHA-256 |
|---|---:|---:|---|
| remote.py | 17 | 11269 | a2c2fc9d32694a96a406b6de499bfb04a2a159710443c8b37ca56e92921a536f |
| actions.py | 11 | 12496 | 07c03a65fad73f49064abd0af77161b5ed10e2c6002bb6c442e7ab5b28ee25b1 |
| run.py | 19 | 24859 | f48a8be9fa380a2a922613d188ae7622eafffdf3dc5fec12edc1372b4f7fc2d2 |

These are prospective data identities computed without importing or executing a subject; actual materialized bytes must match before testing. The private historical inert caller projection is22977B/56b7e654537694ffb52b4557f21b369a4ad942cb507a876882bfa587c7899dd3. Retain its counted injection/prefix/counter/allowlist recipe, all other code and error handling. No arbitrary replacement fallback is permitted.

Preserve source loading, descriptor/no-follow/type/ancestry/hash checks, isolated Python -I -B, fixed transport/framing limits, claim/intent-before-dispatch, real checked admission, return attribution, original first error and separately appended closing errors. A durable_unattributed result is evidence only and cannot become a successful returned action. Preserve every original local/prerequisite/transport closing check and counters. Capture follows only successful returned upload; one upload and one capture maximum, with no retry or adaptive follow-up.

A complete native attempt has13 transports: three passes each over two baseline labels and capabilities, then one adapter claim, one adapter push, one upload and one capture. Preserve exact existing order and gating. Adapter claim requires at least1GiB free and no conflicts. Preserve upload180s plus5s reap, bounded streams, local upload195s and capture630s envelopes, 600s capture budget and30s child budgets. All other original bounds stay exact. Remote total command and Windows command-line guards stay active. The upload previously approached the30,000 UTF-16-unit ceiling; host fixtures and admission must measure the actual new upload/capture argv including NUL and enforce the unchanged ceiling. Do not widen it.

Upload flashes/resets once through the fixed existing CLI. Passive collection uses pinned OpenOCD/p0_mem_read.cfg with AP0 mem_ap, reset_config none, no Cortex target, no flash driver/events and disabled network command ports. Only fixed dump_image and shutdown commands are allowed. No halt/resume/reset/write/abort/inferior call is added. Stopping OpenOCD does not stop the MCU. Neither transport failure nor host deadline establishes what the MCU subsequently did.

## 4. Fixed geometry and timing

The seven windows come from current accepted ordinary Runtime and UnoQPort objects. Runtime begins0x20013960, size166376; UnoQPort begins0x2003c348, size40. All selected extents lie inside their independently observed allocated, startup-initialized object bounds and do not overlap.

| Order | Name | Address | Bytes | Selected scalar fields |
|---:|---|---|---:|---:|
| 0 | report | 0x2003bc98 | 600 | 10 |
| 1 | transaction | 0x2003b2b0 | 504 | 36 |
| 2 | previous | 0x2003b4a8 | 48 | 9 |
| 3 | gate | 0x20013a28 | 88 | 15 |
| 4 | grants | 0x2003bc80 | 21 | 21 |
| 5 | attempted_word | 0x2003c2a8 | 4 | 1 |
| 6 | motor_port | 0x2003c348 | 40 | 15 |

Only attempted_word byte2 is decoded as Runtime.attempted_. Bytes0,1,3 are opaque. The four-byte aligned container is wholly inside Runtime; it does not redefine the neighboring fields. Other addresses are word-aligned; a positive length need not be a multiple of4. No shared range validator is weakened. RuntimeReport has no nested transaction report; transaction and previous are separate live windows.

Exact ordered plan: before loader5 chunks/263680B, before sketch2 chunks/92944B, first seven windows, second seven windows, after sketch2 chunks, after loader5 chunks. Flash chunks are at most65536B. Totals are28 reads and715858B, including14 SRAM reads/2610B. No extra read can be inferred from this permission.

Preserve the existing30-second initial wait immediately before read index7 and the two-second gap immediately before index14. Each wait records requested/before/after, verifies elapsed duration and surrounding budget; no success means the wait has actually completed. There is no claim of30 seconds continuously running firmware. Comparison completion indices are4 before_loader,6 before_sketch,22 after_sketch,27 after_loader. Snapshots are exactly reads[7:21]. A complete report requires all28 exact reads/bytes, all14 exact snapshot rows, completed waits, all four full-image comparisons true and no native/closing errors. Package raw/header extents must not be confused: capture compares92944B, upload consumes92928B.

## 5. Scalar map and evidence provenance

ordinary_scalar_map01.json is 42416B/d8f4eb7eb36430cff975e3032168fa61f2c249e55596401a67862b272bb08fb7. It contains seven window specifications,107 flat scalar fields, observed widths/offsets and exact ptype line evidence. All13 current ptype blocks have hashes; the exact raw ABI and parsed ABI pins accompany them. Nested field offsets are transcribed from current ptype and crosschecked in their actual containing layout, not assigned diagnostic coordinates.

The seven actual enum tables cover RuntimePhase, RuntimeFault, app::Phase, app::Fault, motors::Fault, core::State and edge::EscapeFault. An unknown numeric code is retained and marked; it is not repaired to NONE. The fsm::RobotFault bits and expected zero grant bytes are explicitly source-only semantics. Its known mask1023 is not a GDB observation, and zero is an empty mask, not an invented NONE enumerator. dump_origin is preserved as rawu8; its value0 expectation comes only from pinned current config.

The flat map selects scheduling/readiness/counter fields; transaction decision/timing, Robot token/state/output/faults; applied.feedback and retained previous independently; gate/halt bookkeeping; all grant bytes; attempted_; and native configured/low/settled/mask/timer/channel/pwm-index/pulse bookkeeping. It excludes pointer tables, padding, unselected peripheral reports and all diagnostic trace data. Whole window raw bytes still survive in the retained evidence and decoder output.

## 6. Decoder API, exact retained parser and ordinary semantics

New interpret_run01.py derives from the corrected D207 decoder d96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab. Do not claim a metadata-only decoder adaptation. Preserve the32 exact function bodies listed in the derivation, including strict JSON/duplicate/nonfinite/depth handling, verified base64/size/hash checks, receipt key/type/error ordering, upload admission, file set, wait record, _admission, _interpret, bounded reads and main.

Only the listed eight structural functions receive exact identity/count metadata changes; all other statements in them remain identical. Fixed changes are maximum files14→16, commands26→28, snapshots end19→21, gap13→14, flash boundaries(4,6,25,20)→(4,6,27,22), complete readcount28 and ordinary prefix/package extent. Integer receipt types continue to reject bool. Do not use this amendment to accept malformed JSON, schemas, missing files, timestamps or forged counts.

Replace exactly nine semantic functions: _layout, _scalar, _width, _decode_value, _decode, decode, _windows, _result and interpret. One bounded _ordinary_findings helper is permitted. Remove only the six listed SETTLE annotation helpers and diagnostic ALIASES/REASONS/SAMPLE_KEYS constants. Their historical source/tests remain intact. Flat decoding needs no recursive pointer/type traversal. No new transport or file discovery helper is permitted.

Public API remains decode(kind,body,*,field_map_raw), interpret(packet_raw,*,field_map_raw), main(argv). kind is exactly one of the seven window names; old short/diagnostic type aliases are refused. Argument exact-type ordering is kind str, body bytes, map bytes, then map size/hash/schema, selected kind and exact body size. Map mismatch is rejected before packet/window parsing. Pin the exact map bytes and hash; check source/schema/seven unique windows/107 unique bounded nonoverlapping fields/scalar widths/observed enums and object bounds. No dynamic address resolution or unreviewed map is accepted.

decode returns exactly {raw_hex,fields}; fields is a fresh dict keyed by the selected flat names, decoded in increasing(offset,name) order. Each scalar record is exactly {raw_hex,raw_unsigned,value,enum_name,issues}. raw_hex is lower-case little-endian bytes, raw_unsigned is the exact unsigned integer representation, and issues is an ordered list of stable strings.

Scalar meanings:
- u8/u16/u32/u64 use exact integers. i8 uses signed two's-complement value while retaining unsigned raw bits.
- bool0/1 becomes false/true. Other native bytes yield value=null and INVALID_BOOL; preserve the byte, do not reject an otherwise valid packet or stop decoding later fields.
- f32 finite values decode normally, preserving negative-zero raw bits. NaN/positive or negative infinity yield value=null and NONFINITE_F32; preserve exact raw bits. Output JSON never contains nonfinite numbers.
- Known observed enum values get their exact enum_name. Unknown values keep numeric value, enum_name=null and UNKNOWN_ENUM. Non-enum fields use enum_name=null.
- All other canonical scalars have issues=[]; no guessed value is substituted. Raw bytes and scalar records remain independently owned between calls.

_result retains schema/status/retrieval_sha256/field_map_sha256/coherence/upload_result/capture_result/decode_first_error/verified_files/windows/repeated_fields_equal. Set schema ordinary-app-observed-fields-v1 and replace settle_annotations with application_findings (list). No diagnostic branch/loss/completion output remains. windows maps first.name/second.name to the decode result. repeated_fields_equal contains the seven names, null until both are decoded, then compares selected scalar raw_hex only; opaque/padding bytes cannot influence that comparison. Whole raw windows remain available separately. Equality never changes coherence=UNPROVEN.

application_findings records exactly {sample,field,code,raw_hex,value}, in read-plan order then field(offset,name) order. Scalar issue codes are emitted first; additional semantic codes apply only when issues=[] and follow fixed order:
SAMPLED_FAULT_PHASE for report.phase==3 or transaction.phase==4;
SAMPLED_FAULT_CODE for any selected typed fault field !=0;
SAMPLED_CONTRACT_BITS for nonzero transaction robot.contract_faults, followed by UNKNOWN_CONTRACT_BITS if outside1023;
UNEXPECTED_GRANT_VALUE for a grants scalar raw byte !=0;
SAMPLED_NONZERO_MOTOR_COMMAND for nonzero finite selected duty values, true selected motors_enabled, or nonzero motor_port.pulses_;
SAMPLED_NOT_ATTEMPTED for canonical attempted_==false.
Do not flag invalid scalar values a second time as guessed semantic values. pwm_indices_ and transient native low/settled masks are reported without converting them into physical pin or motor conclusions. HaltResult fresh/attempted/inhibition fields are sampled return data, not a final publication.

Status remains DECODED for structurally complete collection even with application findings; PARTIAL for an admissible failed capture prefix; REJECTED for the first structural decoding failure. Keep the untouched native first_error and postcheck_errors independently of decode_first_error. There is no automatic application PASS/FAIL, first-failure reconstruction, epoch-limit conclusion or retry recommendation from this decoder.

## 7. Prefix, retrieval and inference limits

Preserve all57 allowed (commands,reads) prefix pairs: commands0..28 and reads=commands or commands-1 where nonnegative. Requested bytes equal exactly the attempted plan prefix. Successful reads are an ordered prefix; a missing declared body differs from an unread tail. Failed captures require a native first error even when every read finished but closing failed. The existing wait/flash boundary ordering and first structural error precedence remain intact. An early failure with no complete report/schema may be raw evidence without an admissible decoded prefix; do not fabricate missing report fields.

Only after native closure, prepare one separate file-only retrieval of exact saved upload/capture reports and the successful SRAM prefix, at most16 files. Use the pinned D207 retrieval template with only EXPECTED and PINS assignments changed to actual returned/durable evidence; report hashes cannot be predicted. Keep the60s alarm, pinned descriptor helper, no-follow read/hash/length checks, second file pass and full before/after identity. Save exact argv/stdout/stderr and packet bytes under a fresh retrieved_inert_run01 owner. This retrieval opens saved files only; it does not perform additional MCU reads. Failed or mismatched retrieval is not retried automatically.

The observation provides sampled values, not atomicity. Open resets TransactionReport before acquisition. Transaction completion stores completed_us, timing_valid, finished and execution_us before a multiple-word PreviousTick copy, separate duration stores and final IDLE; Runtime then updates epochs/max/freshness. uint64 tokens can tear. Runtime::step clears freshness/service pulses before early returns. Runtime and Transaction FAULT publication precedes further cleanup; neither is a cleanup-complete fence. Gate.halt is idempotent. A default/unattempted HaltResult does not alone mean cleanup failed.

The absent grants can legitimately leave RUNNING with advancing epochs, initialization_complete=false and Robot BOOT. BOOT is not setup failure; attempted_ is not begin_ok, and app.ino discards begin's return. applied.feedback duration fields and retained previous differ by design. Increasing/equal/decreasing counters are only observed relations: equal is not proof of a stall; decreasing may reflect tearing, reset or other ambiguity; increasing does not prove uninterrupted execution. Linux boot and unchanged flash do not establish MCU reset continuity.

D210 actual instructions support selected setup/dispatch/completion, M0 native refusal,150us/4096 SETTLE bounds and fault cleanup ordering. Unselected callback, strategy, chronology, recorder, UART, sensor and peripheral interiors remain source/host-only. File-only instruction review and sampled bookkeeping are not electrical/physical qualification, continuous performance evidence or measured worst-case time. maximum_execution_us is a sampled software counter, not an800us WCET claim. No final inhibition follows from ending this passive capture.

## 8. Independent host obligations and first-failure preservation

Before any subject execution, the independent author reads this contract, fixed data and pinned historical fixtures, while the new subjects remain unread/unhashed/unimported. The implementation author must not read new oracle bodies until implementation is sealed. A metadata-only identity receipt may supply final source/semantic-body hashes; it cannot supply expected behavior. Freeze exact selected method names, assertion counts, every counted fixture projection and distinct negative stimuli before root's first run.

Native plan:47 remote,29 actions,30 caller methods. Preserve the91 ancestral behavior methods (42/24/25) through explicit counted fixture metadata projections and all applicable assertion bodies. Replace the15 D207 Current* metadata expectations with five declared ordinary cases per suite; these are new ordinary semantic expectations, not renamed proof of diagnostic geometry. The companion enumerates the obligations. Real ordinary125-file preparation must run in the fixture; keep true rejection paths for stale129 manifests, source/artifact/ABI/entry/owners and actual source mapping drift. Never replace admission with an unconditional successful stub. Mocks must still prohibit actual device/compile/subprocess operations where the historical boundary requires it.

Decoder plan:46 methods. Retain the explicitly named27 applicable PacketOracle and seven MainOracle methods, with counted fixture metadata/geometry adaptations. Four PacketOracle cases tied to SETTLE/Trace or invalid-native-byte structural rejection, all13 old nested-map cases, all16 SETTLE annotation cases and the three D207-only provenance cases are explicitly nonapplicable; their historical files are untouched. Twelve new ordinary methods cover every107 scalar, all seven observed enums, signed/unsigned endpoints,64-bit precision, every bool and float field, raw unknown/nonfinite preservation, attempted opaque neighbors, all window widths/map checks, complete/partial application findings, source/owner/image negatives, independent return containers and first-error preservation. The exact names and exclusions are in the derivation.

All57 prefixes are exercised. Preserve malformed/oversize/duplicate/deep JSON, exact bool-vs-int receipt types, incomplete/short/failed waits, each flash completion boundary, malformed raw/closing hashes, error shapes, output exclusivity and corrected first-error ordering. Adapted negatives must be explicitly unequal to the new positive values: a stale diagnostic previous/report tuple must never become the accepted ordinary tuple by a global substitution. The author must report any inapplicable inherited case before freeze rather than weakening it.

Run eight first suites serially (remote/actions/caller/interpreter, Linux then Windows for each), Python-I-B,600s outer bound per suite, exact independent/coordinator pins before and after. Linux fixtures use uniquely owned /dev/shm scratch. Windows TEMP/TMP/TMPDIR are dedicated before Python startup, outside shared Temp. Keep named platform skips explicit; Linux must run retained descriptor/credential/process cases, and ordinary portable metadata/decoder cases run on both. The prior named skip inventory is retained in the derivation: expected Windows remote29PASS/18SKIP, actions24PASS/5SKIP, caller9PASS/21SKIP and decoder46PASS/no skips; Linux has47/29/30/46 passes and no expected skips. Freeze the exact applicable skip inventory; no new generic platform skip. No oracle-specific environment is required. Tests own temporary fixture paths only; preserve every failed receipt and use guarded cleanup. Do not filter symbol/assertion output, add retries, change locked tests or edit production config.

Before native admission: separate source/host reviews, D211 actual cleanup review, accepted preparation/scope/map/decoder pins, fresh complete board identity and source/artifact/helper/process/free-space evidence, unused-owner checks and one clean reviewed Git HEAD. All writers hold through one check-only and at most one execute. Any failed admission/child/closure consumes only what it actually claimed; save the exact failure and stop. Changes or retries require new recorded scope/owner and review. Successful collection and decoded format acceptance do not close physical gates or authorize a motor-capable build.
