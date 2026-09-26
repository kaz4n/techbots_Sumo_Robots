# D240 qualified application delivery: source and host review

27 September 2026, Dubai. Separate Codex reviewer with reused project context.
Read-only source, fixture and saved-result review; no reviewer test or native
execution. This report is the only reviewer edit in this scope.

**PASS for the bounded source/host preparation. No open material finding.**
This accepts the paired commissioning delivery implementation, not an actual
application upload, physical qualification, motor permission or a phase gate.

## Exact closure

Independently rehashed all 25 pins in
`state/analysis/P7_app_identified_delivery_raw/preparation_manifest01.json`
(4379 bytes, SHA256
`690cdce5157697490bcb0c45b9171a09dc54ef6fea338c5e784ec729ddcb9da1`).

| Input | Bytes | SHA256 |
|---|---:|---|
| tools/run_app_identified_delivery.py | 11308 | `78e131b240f3b14444e3af11b9b539d3a76e71cf08847e9e6898ea34ec4e33c6` |
| tools/deploy_commissioning_app.py | 32202 | `e030c2497605fc77938c70e7cb76e8c29db65322bdb4cba87381a70d2ddcfde4` |
| tests/test_app_identified_delivery.py | 14247 | `17307649a3c853765cd97adfa63fa358cbb166d1debc811ec2f3775a7b55581c` |
| P7_app_identified_delivery_contract.md | 3905 | `792f9a5a712dd8aa26fcf425250b66e2607e4fcea54bea16529a263fba28b19c` |
| P7_app_identified_delivery_validation.md | 3230 | `b5d91a435fc6b6ef08a0d239f28e72cfbd383ddc1b515fbfe732f5b34675593a` |

## Reviewed behavior and evidence

The caller binds current delivery-tool bytes to the exact reviewed Git HEAD,
separately binds the actual compiled source/config and D222 artifact receipts,
and retains D227 physical qualification, enabled-grant evidence, profile gate
and request-specific fresh STAND OK/RING OK checks. M0 cannot acquire operational
dump grants. The standalone D227 CLI still refuses nondefault stream/session.
No firmware, default config, locked test or inherited native lifecycle changed.

The positive uint64 session must equal the run-ID prefix and the compiled
stream/session literals. Exclusive prefix-owned claim creation consumes that
image/session even after failure. Revalidation binds the unchanged full request,
scope, code and claim. Same-prefix suffix changes cannot obtain a second owner.
Receiver/upload use the same fixed ADB executable, serial and boot. The existing
two receive-only commands, 900/915/960-second bounds, closed command latch and
bounded cleanup remain inherited. Connection precedes the one qualified upload;
its outcome and five-operation closure are nested under the consumed owner.

The new final validator reparses the original complete wire with the expected
session, checks END/counts/CRC through the unchanged parser, independently
validates the CSV bundle and compares every CSV byte to the wire-derived bytes.
Source/config/target declarations are checked. Variable counts and interrupted
recordings remain visible rather than being relabeled clean. Caller-declared
origin and hardware_acceptance=false remain explicit. No reconstructed BEGIN,
observed END alone or SENT_UNCONFIRMED status can satisfy this validator.

Saved host02 command/result/stderr show nine methods, zero failures/errors/skips,
28.172 seconds unittest time, process exit zero in 28.410 seconds, with all four
execution inputs unchanged. The reviewed fixture bodies include real temporary
Git/source/compile/artifact admission, decoded upload payload construction,
missing authority/grant refusals, owner collision and changed-claim refusal,
and actual inherited uploader closure through the paired path. Real small-wire
fixtures cover variable counts, interruption, wrong session, missing envelope,
changed CSV and the actual inherited close_receiver calling the new validator.
Controlled orchestration fixtures prove connection and post-connection claim
failure prevent upload, while failed upload still closes the receiver.

## Finding and repair trace

The initial new caller wrote result.json outside error handling. A secondary
journal failure could replace an earlier upload/receiver failure before attaching
the outcome. This was reported independently and repaired: owner/journal errors
are retained as result_write secondary evidence, the original primary survives,
and its complete in-memory outcome is attached before raising. The final fixture
combines failed upload and failed final write and checks the original exception
identity and both error records. Missing capture or incomplete closing evidence
also forces FAILED.

Initial host01 failures and exact initial caller/test bytes remain pinned: one
fixture incorrectly searched compressed payload text, and another encountered
the unchanged descriptor-stability refusal. The final fixture decodes the actual
payload, and a fresh unchanged guard path passed. No guard was relaxed and no
broad inherited test suite was repeated.

## Boundary

This is a usable checked preparation/execute pipeline for the seven existing
static/default/MATCH0 commissioning profiles only. It does not implement the
separate static MATCH/Immediate/M1 production-release profile. Actual application
delivery still needs the exact qualified compiled configuration, current
request-specific authority, clean committed tool HEAD and one fresh owner.
Bare-board M0 with disabled grants cannot produce an honest operational app dump.
An ordinary reset loses RAM evidence and does not renew an already used session.
No native application action is admitted or claimed by this source/host review.
