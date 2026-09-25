# D175 motor-fault upload profile review

Date: 2026-09-25 (Asia/Dubai).
Reviewer: separate fresh-context same-model Codex agent; read-only source review.
Scope: actual upload_remote.py diff and new test_motor_fault_upload.py; D175 and P7_motor_fault_upload_contract.md are the acceptance basis.
Implementation SHA256: e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1.
Test SHA256: bdc810cb1838692def32672f2777c27d9b27fa99823a331c945d7ca521fbc0fb.
Contract SHA256: be91540316277b995ebe4cce26504fdd108845d3007624f13bd8df9fedc26cfe.

BLOCKER: none.
MAJOR: none.
MINOR: none.

PASS: upload_remote.py:61 admits only exact built-in string identifiers, constructs independent profile/file/argv objects and preserves module constants.
PASS: upload_remote.py:69 matches the recorded active_verified.json source/build path, raw ELF selector, dynamic FQBN, diagnostic sketch/output and three replaced absence paths.
PASS: upload_remote.py:91 rejects cross-profile fields/paths and preserves validation plus the detached JSON copy of caller bindings.
PASS: upload_remote.py:143,276,343,393,436 consistently select result/attempt/command metadata and both admission/final file/absence checks from the same instance.
PASS: legacy default upload(), static run01/run02 arguments, schemas, shared 15 file roles and three directory selections remain unchanged.
PASS: descriptor ownership, exclusive consumed attempt, environment, one launch, 180s budget/120s child timeout, group kill/reap, first-error handling, partial streams and independent final checks are unchanged by this diff.
PASS: upload_loader retains the 2303728-byte child file cap and strict below-1MiB accepted streams; no compile, capture, retry or cleanup path is introduced.
PASS: test_motor_fault_upload.py covers public success/refusal, nested legacy profiles, caller mutation, ownership/failure receipts, controlled default-child deadlines/cleanup and stream limits; inherited fixture bodies were inspected.

Tests: not executed by this reviewer, as explicitly assigned; the safety-auditor role's general host-test instruction is superseded for this bounded review.
Limits: source review does not certify native upload, artifact origin, runtime coherence, motor authorization, physical acceptance or a human phase gate.
Verdict: PASS for the reviewed host-preparation diff; native execution still requires the separately bound caller and identified scope required by D175.
Follow-up (same reviewer context): inspected coordinator receipts upload_first.json and upload_legacy.json (SHA256 ca0a307efcfc03d0f7f02278bf44584af0c700622b86f2defb2b020742ecf0ad); no reviewer test/native execution.
Observed results: new suite 34/34 PASS; old uploader/loader/private suites 55/55, 59/59, 3/3 PASS; run02 ownership suite FAILED, 19/20 PASS and one failure at test_run02_ownership.py:223. The later upload_file_limit_current.json (SHA256 f74c486161e0e82cc252cad7298b63dcd9cc9f78e8ff2aabc440faedc86e4dce) independently records 4/4 PASS, native calls0; its separate execution does not erase the earlier failed suite.
Failure: line223 compares the historical run02 uploader pin 23661c8a18205cfb64d77c5ae81765463560cf52f451e257bb3bb339d39f2b18 with current e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1. startup_run.py:149 and native_run02/inputs.json retain that same old pin; native_run02_scope.json still binds unchanged launcher c9588835 and test84503c31.
Consumed constraints: native_run02/result.json records COMPLETED/UPLOADED/COLLECTED; D160 explicitly consumes that scope. startup_run.py:473 rejects the existing owner, and lines478-479 independently reject changed helper bytes against historical pins before dispatch. D175 expressly prohibits old consumed-manifest changes.
Disposition: expected consumed-snapshot mismatch, with no material D175 behavior regression found; source-review PASS remains, while the legacy-suite failure must remain reported as FAILED. Preserve the negative receipt, original assertion, historical pins and consumed owner; do not repin, skip, weaken or retry to obtain an all-green claim.
