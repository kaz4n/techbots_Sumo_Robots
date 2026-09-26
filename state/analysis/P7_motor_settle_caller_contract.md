# D201 fixed inhibited SETTLE caller and actions

26 September 2026. Prepare only new run.py and actions.py beneath
state/analysis/P7_motor_settle_run_raw. Use the exact D195 metadata derivatives
below, preserving every existing lifecycle, guard, wait and error policy.
The companion contract is state/analysis/P7_motor_settle_remote_contract.md.
Actual D199 compile/ABI/entry file observations and semantic review are
accepted prerequisites; new source/host preparation itself authorizes no
native upload/capture. Fresh final scope and actual admission remain separate.

The fixed binding proposal is
state/analysis/P7_motor_settle_run_raw/capture_binding01.json,
24233 bytes SHA256 0a9d4a6af736ff96efa3b9213696f4369cb861e07996e594ebce00c996e39619.
It carries exact observations and ordered source derivation tables. It is not
the future preparation.json, scope, native bindings or consumed attempt owner.

## Exact source derivations and fixed identity

Originals:
- state/analysis/P7_app_motor_observe_run_raw/actions.py12515B SHA256
  6a730069e2511306459f5c3443976a84351b155fd04660a094606cfd98f2829f;
- state/analysis/P7_app_motor_observe_run_raw/run.py24944B SHA256
  95cc5cb695c8d9bbee85a2105aca46d7c371c1a3bec3c5e3a36ea8fb4dbd1471.

Apply exactly the nine action substitutions in this order:

| Old literal | New literal | Count |
|---|---|---:|
| `3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0` | `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da` | 1 |
| `app-motor-observe-3a08ddeb-run01` | `app-motor-settle-117cc0e7-run01` | 1 |
| `app-motor-observe` | `app-motor-settle` | 4 |
| `_app_motor_observe_actions_legacy` | `_app_motor_settle_actions_legacy` | 1 |
| `98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db` | `577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0` | 1 |
| `ADAPTER_BYTES = 11357` | `ADAPTER_BYTES = 11343` | 1 |
| `95360` | `95520` | 1 |
| `('previous', 537115952, 48)` | `('settle', 537121768, 28)` | 1 |
| `727152` | `727432` | 1 |

Require actions.py12507 bytes SHA256
8918231c9c2aaf1b72120539e1677db73ce9103798fa860e9fa2501ac669092a.

Apply exactly the17 caller substitutions in this order:

| Old literal | New literal | Count |
|---|---|---:|
| `3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0` | `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da` | 1 |
| `app-motor-observe-3a08ddeb-run01` | `app-motor-settle-117cc0e7-run01` | 1 |
| `P7_app_motor_observe` | `P7_motor_settle` | 7 |
| `test_app_motor_observe` | `test_motor_settle` | 3 |
| `app-motor-observe` | `app-motor-settle` | 6 |
| `native_abi_static02` | `native_abi_static01` | 8 |
| `abi02_actual_review` | `abi_actual_review` | 1 |
| `tools/compile_app_motor_observe.py` | `tools/compile_motor_settle_probe.py` | 2 |
| `70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827` | `b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62` | 1 |
| `aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e` | `aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282` | 1 |
| `len(value['files']) == 128` | `len(value['files']) == 129` | 1 |
| `D193` | `D198` | 2 |
| `ABI02` | `ABI` | 1 |
| `95344` | `95504` | 1 |
| `f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc` | `d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc` | 1 |
| `95360` | `95520` | 1 |
| `85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c` | `e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0` | 1 |

Require run.py24885 bytes SHA256
fe2b4d644edbc6096fe1956f4aa8fe801eed4d125ab19ea31eef86ca70469de4.
Counts apply after preceding replacements. They are source derivation rules,
not generic runtime transformations. Do not add predicates, native options,
reads, retries, output owners, transport branches or side effects beyond these
fixed substitutions. Historical original bytes and failures stay unchanged.

SOURCE is117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da;
RUN_ID app-motor-settle-117cc0e7-run01; BOARD2629958581. Fixed boot remains
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, with existing full identity checks.
The sketch is still app_motor_observe and the profile static/default,
MATCH0/MOTORS_ALLOWED0/probe1. No motor-capable build is introduced.

Use new RAW=state/analysis/P7_motor_settle_run_raw/:
preparation.json, inert_run01_scope.json and exclusive native_inert_run01.
Immutable stage is /home/arduino/sumox26_codex_build/RUN_ID-adapter.
Only its remote.py child is pushed, exactly11343 bytes SHA256
577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0.
The remote upload/capture owners append -upload/-capture to RUN_ID. No absence
is assumed, historical owner is reused or uncertain attempt retried.

## Source/artifact/provenance binding

New COMPILED=state/analysis/P7_motor_settle_compile_raw/.
Its inputs_static.json is13432 bytes SHA256
aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282.
It has129 exact pins and app-motor-settle-static-inputs-v1 schema.
Keep every pin read and source-name check. Use the checked launcher
tools/compile_motor_settle_probe.py7570B SHA256
b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62,
then its private load_caller(root=ROOT), CompileDiagnostic.source_names and
source_mapping through the existing root/base seam. Its original sources and
projected hashes remain checked. Never call its main/build/compile/claim path
and never substitute an unprojected legacy inventory.

Build stays /home/arduino/sumox26_codex_build/app-motor-settle-static01/build.
Keep exact raw95504B SHA256
d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc and
package95520B SHA256
e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0,
using app_motor_observe.ino filenames. Preserve canonical expected-vs-prepared
upload/capture comparison before claim, original installed dependency pins,
absence lists and immutable command state.

Preparation's exact keys remain schema,run_id,source_sha256,bindings,files.
Its schema is app-motor-settle-run-preparation-v1. Bindings are exactly
upload/capture. Files maps the twelve paths below to exact bytes/sha256 records;
the accepted values are fixed by the following table and binding proposal.

| Repository-relative provenance file | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_settle_compile_raw/inputs_static.json | 13432 | aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/result.json | 1608 | 9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5 |
| state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json | 9648 | e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/result.json | 905572 | 230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/local_result.json | 275 | eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9 |
| state/analysis/P7_motor_settle_compile_raw/native_abi_static01/abi.json | 5410 | 069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941 |
| state/analysis/P7_motor_settle_compile_raw/native_entry_static01/result.json | 378557 | 10d8a184598b587ff820cb3342586a61a22106a087788a7be756486e22a824ad |
| state/analysis/P7_motor_settle_compile_raw/native_entry_static01/local_result.json | 277 | ec4c45e92b7cdb4e6191293c77777182d7a90f49e1594d3421c61f24bf171fe7 |
| state/analysis/P7_motor_settle_compile_raw/native_entry_static01/entry.json | 9919 | 8332f7974cdcb39ec5e65cd262b2c22623bb51412f07fc04ec329d5b0d685485 |
| state/reviews/P7_motor_settle_compile_actual_review.md | 8475 | f046db4709a339df345b2e2214da0a946cee4ecebe00b05d80266abe8bb2f624 |
| state/reviews/P7_motor_settle_abi_actual_review.md | 7312 | a7c3993ab5e0d008b4464bf93f89b5877447992fa8e3197d8c869812e11f874f |
| state/reviews/P7_motor_settle_entry_actual_review.md | 15336 | 20f54afaf33dbfc17c08f0406c3a00c575cf237956044be0581db1737a7109b7 |

Preserve COMPILE_CHECKED/source/boot/first_error=None and ARTIFACTS_CHECKED
predicates. ABI local and summary must be STATIC_ABI_OBSERVED, local first_error
None. Entry local and summary must be STATIC_ENTRY_OBSERVED, local first_error
None. Keep raw ABI/entry results pinned as provenance. Do not reclassify any
older failed file-tool attempt or insert its bytes in successful provenance.

Actual review hashes bind the externally accepted files; the unchanged caller
does not parse prose reviews or independently prove their semantic conclusions.
The coordinator verifies the accepted review status/scope before final scope.
No new runtime review-schema predicate is implied by metadata-only derivation.

Required scope keys remain exactly schema,run_id,board,source_sha256,
expected_identity,files. Its eleven file keys are exactly:

- state/analysis/P7_motor_settle_run_raw/preparation.json
- state/analysis/P7_motor_settle_run_raw/run.py
- state/analysis/P7_motor_settle_run_raw/actions.py
- state/analysis/P7_motor_settle_run_raw/remote.py
- tests/tooling/test_motor_settle_run.py
- tests/tooling/test_motor_settle_actions.py
- tests/tooling/test_motor_settle_remote.py
- state/analysis/P7_motor_settle_caller_contract.md
- state/analysis/P7_motor_settle_remote_contract.md
- state/reviews/P7_motor_settle_caller_review.md
- state/reviews/P7_motor_settle_remote_review.md

No scope/preparation self hash. This fixes exact future contract/review path
spellings; no draft is silently admitted in their place. Keep committed clean
reviewed HEAD, unchanged source/ADB/local checks, fresh board identity,
exclusive owners and bounded command count. Check-only performs local
admission only: no owner creation, board access, staging, upload/reset or SRAM.

## Preserved action protocol and sample timing

Retain build_command(action,sources,bindings,adapter_pin), validate_reply and
run_actions signatures, all framing/sequence/first-error/closure behavior,
the11-field action envelope and returned-only success. Reply stays65536 bytes,
decoded payload196608 bytes and command30000UTF16 units including NUL. Three
inline source identities and staged adapter before/after checks remain exact.
Durable_unattributed fallback preserves evidence and always remains failure
after an outer/close error, even if its inner report says COLLECTED.

Keep read-plan agreement with remote exactly:26 reads,727432 requested bytes,
12 SRAM snapshots, six current windows trace/report/runtime/transaction/settle/
gate, four flash comparisons and two65536-bounded sketch chunks. Only live
previous48 is replaced by observed separate settle28 at537121768; nested
Report.before_abort.previous stays. Preserve all final Runtime/Transaction/
Gate and all loss fields. The adapter/action layer does no typed decoding.

Keep analysis's exact keys schema,flash,snapshots,coherence,pre_sample_wait.
Its prefix is app-motor-settle, coherence=UNPROVEN. pre_sample_wait requires
exact requested_seconds,before,after; requested_seconds exact int30, bool
refused; times finite int/float excluding bool; capture start <= before <= after
<= wait.before; after-before>=30. Keep report.wait exact request2, elapsed>=2,
time types/order and wait.after<=capture finish. No FROZEN/epoch assertion,
extra memory poll or retry is added. Failed envelopes preserve original partial
reports, wait evidence and first errors. A successful inner result cannot
override failed outer transport, framing, pins or closure.

## Unchanged lifecycle, limits and independent host validation

Keep InertRun(reviewed_head,*,root=None), old controlled seams and exact CLI
--check-only|--execute with --reviewed-head. Existing local private composition
on import remains; do not claim actions/caller are no-I/O imports or introduce
native dispatch at import. The remote adapter alone retains passive definition
import semantics.

Complete success remains seven allowlisted labels and13 transports: two stage
operations, one upload, one capture, and three dispatches for each of the
three prerequisite groups. Each stage/action dispatches once. Durable intent
precedes claim/push and verified exclusive claim precedes push. Preserve
upload195s/capture630s/prerequisites60s, remote upload180s/capture600s and
every installed-tool/process/space guard. No automatic cleanup, retry, loader
replacement, alternate source/profile/transport/root, or additional reset/read
is admitted. /tmp/remoteocd must be freshly absent under the original guard.

Independent oracles freeze before reading new implementations. Preserve all
24 D195 action methods (13 inherited+11 additions) and25 caller methods
(20 inherited+5 additions) through declared private fixture metadata
projection; retain every safety/error/order assertion and all old failures.

| Original oracle | Bytes | SHA256 |
|---|---:|---|
| tests/tooling/test_app_motor_observe_actions.py | 13390 | 103493975bccdcab094b412a5ba26cf125a6f294a9b5efac167660f6fda8a563 |
| tests/tooling/test_app_motor_observe_run.py | 10975 | 7af304d06b85de0f835856ecbd241d957c193b7d252c2849eea474e6043fbb9c |

Add exact9/17 source derivation and old source/manifest/package/window
refusals,129-pin D198 source inventory, successful current ABI and entry
evidence/failed predecessor rejection, exact new schemas/owners/pins and
native-free check-only. Keep all wait shape/type/time/order cases and one-shot
error/closing behavior. Independently compare actual action/remote plans,
26/727432 accounting, inline payload identities and composed command bounds.
Use controlled filesystem/clock/transport fixtures, no board or actual sleep.
Test Windows and Linux serially, preserve first failures and obtain separate
source/host reviews before final scope and fresh admission.

## Separate field interpretation and evidence limits

Current field-map DATA is
state/analysis/P7_motor_settle_compile_raw/abi_static01_decode_fields.json,
16346 bytes SHA256
0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd.
It retains104 old selected fields with14 byte-identical current ptype blocks
and adds11 observed SETTLE members, yielding16 structs/115 fields. Observed
reason values are separate from source-only valid masks1/2/4/7. This map and a
new offline interpreter contract do not change remote or caller source bytes,
scope keys, successful capture predicates or native read order.

A partial/failed capture remains failed in the caller even when an offline
interpreter can decode its retained prefix. Offline annotations cannot upgrade
native status, reconstruct missing windows, replace first_error or erase trace
loss. No association of native first_failure with a specific epoch/stage can
be invented: its record has no token or stage field. Repeated bytes retain
coherence=UNPROVEN. File instruction review, source diagnostics and this
inhibited observation do not establish physical cause, a timing repair,
liveRAM/WCET, electrical acceptance, motor-capable authorization or human gates.
