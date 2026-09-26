# D221 fixed inhibited B4 upload source and host review

FINAL PASS for the fixed source/host scope below, 2026-09-26. No open material
source or focused-host finding. This independent reviewer inspected source and
saved host evidence and performed data-only parsing/hash/derivation checks; no
subject imports, subject tests, board commands, credentials or cleanup were run.
This is not native upload admission or actual firmware acceptance.

## Exact reviewed files

| File | Bytes | SHA256 |
|---|---:|---|
| tools/upload_b4_app.py | 15397 | faea6cbf06d9f79273033fc9d1d819f1b7ce5f489b814ada0ff1b93c2df3c7ec |
| state/analysis/P7_b4_app_upload_raw/remote.py | 5115 | c2f0a4423839f9b3444c2949587486248d3a0af9578ae8188fd478bb55868b57 |
| state/analysis/P7_b4_app_upload_raw/actions.py | 21419 | 7d5cd50fba630c5ca46bdc786f0959610c4c6e6b31059b7fbf13206c09faca57 |
| state/analysis/P7_b4_app_upload_raw/preparation.json | 8189 | ac6bace04fa1196c20944eea4d693dfa02f920e2bfa1efb2a55e4010aaede509 |
| state/analysis/P7_b4_app_upload_raw/derivation01.json | 100030 | d478b6bd81a4ba906839b007cd3d733dd8ce3dbc52c2b752a10a8155ffebeaf8 |
| state/analysis/P7_b4_app_upload_raw/plan01.json | 8282 | 07726511930332b17c49c02c91a1f83df2d22bcc09502fd8255fa573bedee3b8 |
| state/analysis/P7_b4_app_upload_contract.md | 8925 | f9ab9c6729fe4ac6504fe6d284086331f680a004976e0e2898fde41a41222ff8 |
| tests/tooling/test_b4_app_upload.py | 31644 | 1724d4c0f3a034dbd375f9fd45303939f4be3a3a06f9fc27dd41247484cb9da4 |
| state/analysis/P7_b4_app_upload_raw/upload_oracle01.json | 10672 | 97fb48a8a3d2958bb769d0b9d874ff85ae17f8d3412bc0e83da7c449e6be2d57 |

## Source and derivation findings

The fresh b4-app-m0-9044ebbb-load01 owner is fixed across adapter, upload,
local native_upload01 and upload01_scope.json. Existing owners are neither
repaired nor reused. The caller accepts only --check-only or --execute with a
canonical reviewed HEAD. Check-only calls local admission without claiming an
owner or entering native transport. Inherited current/committed pins, clean HEAD,
untracked-path restrictions, plain paths, fixed ADB/serial/identity, durable
exclusive records and owner/descriptor guards remain active.

The preparation binds accepted D214/D215/D217 compile, ABI and entry evidence
and their independent actual reviews. The exact 130-file manifest fc8e6fc1 and
source projection 9044ebbb are checked; the fixed project app.ino, static FQBN
and exact MATCH=0/MOTORS_ALLOWED=0/SUMOX_B4_STAND=1 profile are required. The
other commissioning/probe profiles are zero, and the pinned config retains all
17 APP_GRANT values zero. Raw B4 bytes are 82896/6fcad2f0 and package bytes are
82912/84667b0a. The ordinary D212 package cannot satisfy these selections.

Independently verified 154 unique derivation/provenance/manifest paths, all three
exact diff forward/reverse reconstructions and all 19 recorded unchanged bodies.
The D212 caller injection replaces its sole literal action import; remaining
source is exact. The remote adapter removes capture functions/plans/windows and
preserves selected upload composition; the pinned uploader remains
24710/e926b7ba with no operational body change. Its descriptor admission,
installed pins/override absences, /tmp/remoteocd absence, process checks,
exclusive output, bounded child/180-second budget, raw streams, file cap,
first-error/final-check and descriptor-close behavior remain inherited.

There is one upload command and no capture/retrieve dispatch or fabricated
predecessor. Success order is adapter-claim, adapter-push, CLI initialization,
CLI builtin files, capabilities, upload, then the same three prerequisites.
The new transport guard limits total calls to nine, stage/upload labels to one
and prerequisite labels to two. Durable staging/action intent precedes dispatch;
upload intent requires stage_ready and predecessor None. Successful closure
requires exact counters/action/stage sets and no accumulated diagnostics.
Stage or action failure preserves the first error and attempts local and
prerequisite closing independently; finish failures force FAILED and attach
the sequence result. Consumed owners/intents prevent silent replay.

The bootstrap accepts only upload; checks canonical JSON, duplicate/nonfinite
rejection, one bounded BZ2 member, canonical base64/base85, exact source pins,
fixed binding digest and exact typed adapter pin before execution. The host uses
deep exact scalar-type binding comparison. The bootstrap holds one root
descriptor and independently rechecks staged adapter bytes and closes root in
finally. Only returned origin can pass local validation. Durable fallback is
explicitly durable_unattributed; closing errors cannot produce accepted success.
The full canonical report length/hash covers the streams before compacting.

The author's preseal oversized binding-literal candidate and correction are
recorded in derivation01. Independently decoded the current wrapper and
reproduced binding digest 2faf9ab1, payload102608/ea73114e, and bootstrap
6702/2c2f7b33. Full base64 argv31227 exceeds the bound; selected base85 argv29529
fits the unchanged 30000 UTF-16-unit bound including NUL. No limit was widened.

## Focused host evidence

The independently prepared oracle covers nine methods: fixed artifacts/profile,
dependency pin refusal and unchanged upload composition; bounded framing/types;
returned-origin and independent closing behavior; strict success validation;
first-error/finish sequencing; actual B4 evidence/profile admission; scope,
one-shot intent and nine-call guards; inherited-body/caller/stage-failure
behavior; and CLI check-only/head selection. Native process/network operations
are forbidden or controlled in these fixtures. Windows resource/pwd sentinels
do not assert real platform behavior. Historical unchanged suites were not
replayed.

Reviewed both first raw stderr streams: nine Linux PASS and nine Windows PASS,
no skips, failures or repairs. Test-reported durations are13.589s and1.448s;
outer elapsed times27.9351947s and2.0639454s. Their saved returncodes are zero,
stdout is empty, and stream hashes match receipts. Linux stderr is
a3741cc9ff3f7e22402c5fd0da62b5d2c4c762246f6e87179e7370fd0ce2a485;
Windows stderr is
2f432014b9822478bb892ca2739b076c1ec671ab8f35b9eea838a2452ed8c375.

upload_host_closing01.json is4333 bytes /
1ede62bee1363d4143e1f0c0081eb0612d173bf1f96caf9fec9d009e9a1c1bf1.
Its freeze30708/02291bf3, oracle, eight saved run-file pins and oracle inputs
match current bytes. Independently rehashed all195 coordinator-frozen inputs;
none changed. Windows temporary owner is recorded empty; no independent Linux
remnant inventory is claimed. Unique evidence remains retained.

## Separate native boundary

This closes source and focused host review only. Before one native attempt,
require accepted D220 exact cleanup/fresh scratch absence, a separately reviewed
concrete ten-file scope with this sealed review, the host closure/oracle/freeze
and prerequisite evidence in its admission union, clean committed HEAD, and
successful check-only. Actual returned upload/closing receipts need a separate
review. D219 capture remains independent, with no synthetic predecessor from
this review. No recording completion/coherence, physical sensor/motor result,
RAM/WCET qualification, motor-run permission or phase gate follows.

Review sealed; no product or test files edited.
