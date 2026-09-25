# Additive upload file-limit correction review

25 September 2026, Asia/Dubai. Separate same-model review reusing D154-D156
context. Design review only at this checkpoint; no implementation/test/native
execution by reviewer. Reviewer owns only this review note.

Contract SHA256
`8b31b281a69fbf4c54794b99965b559d780b4138093ffcd56ee72d4aab05871d`.
**Design PASS for host implementation/testing; no material design finding.**

An explicit upload_loader entry and per-instance preexec callback isolate the
2303728B file cap from legacy upload and frozen D153. A shared small runner
avoids module copies and global rebinding. The source-specific cap admits the
largest authorized copy while both diagnostic streams still require <1048576B
for acceptance. The contract explicitly permits larger transient stream files;
it does not incorrectly retain a physical1MiB ceiling claim.

Independent companion tests must exercise all inherited cases through the new
entry, adapting only its invocation and two new-API preexec expectations while
leaving original tests unchanged. New callback/cap, both stream boundaries and
support-global stability remain necessary. Four real Linux copy tests already
establish the loader/cap boundary; they do not validate this new wrapper wiring.

Original81668c79 source and every old oracle/receipt remain historical evidence.
Changing the uploader digest must fail D155's old source pin, and the legacy
entry keeps its prior behavior. No current output/run binding changes: consumed
run01 is not revived. Residue handling, fresh ownership and any later caller/run
selection remain separate. No cleanup, native operation or retry is authorized.

Actual source and frozen test receipts are pending; design PASS is not evidence
that the uploader correction has been implemented or executed successfully.

Implementation/receipt review, commit3787649fbfda902fcb9765d063c9f8840748b9f0:
uploader SHA256
`bb6f9631d6e2283d3111e15121f8da7b94bc6d78f3bb3f3a5092d89fce050dcd`.
Reviewed the full17-added/3-changed-line diff. Instance initialization preserves
the legacy support callback by default; only upload_loader passes the new
callback. Popen uses that instance value. limit_upload_files locally imports
resource and sets both limits to2303728; common runner behavior is unchanged.
No global rebinding, import-time action, new output identity or D153 edit.

Companion test_upload_loader.py SHA256
`57fafd8462574217a2e1ec4fb00889ba28b58ddb766d12686baeebc5e06b20d7`
inherits all55 original cases, changes only new-entry invocation and two
preexec expectations, and adds four limit/stream-boundary tests. Its reported
authorship is independent and contract-derived; this reviewer inspected it
after source, and does not claim fresh-context or cross-model independence.

Verified loader_limit_freeze.json SHAa2dd763c0211d296462e605ec84e189b37101c82331f3d4ca85fa82e4052cb59,
whose timestamp precedes both runs and whose commands match both receipts.
loader_limit_legacy_first.json: **55/55 PASS**, exit_code0,3.595s.
loader_limit_first.json: **59/59 PASS**, exit_code0,3.698s.
All nine per-file pins_unchanged values are true in both; independently
rehashed all nine current inputs with exact matches. Original test01bcfbe9,
D153 source1aa602d0 and D155 source6f86e645 remain unchanged. D155 still pins
the older81668c79 uploader and therefore rejects this new source before use.

**Final scoped disposition: PASS for D157 host implementation and tests;
no open material finding.** The separate four real Linux copy-boundary tests
support the chosen limit; these114 wrapper tests use controlled child/process
seams and do not establish native CLI or MCU success. D156 remains failed and
consumed, with its original evidence intact. No later caller, residue handling,
fresh ownership, run permission, physical acceptance or phase gate is supplied.
